"""
ProjectileFactory for creating projectile entities.

This factory handles the creation of projectile entities with all necessary components,
separating the creation logic from the attack system and delegating management
to the ProjectileManager.
"""

import logging
from typing import TYPE_CHECKING, Optional

import pygame

if TYPE_CHECKING:
    from ..components.position_component import PositionComponent
    from ..components.weapon_component import WeaponComponent
    from ..core.entity import Entity
    from ..core.entity_manager import EntityManager
    from ..utils.vector2 import Vector2

logger = logging.getLogger(__name__)


class ProjectileFactory:
    """투사체 생성 전담 팩토리"""
    
    @staticmethod
    def create_projectile(
        weapon: 'WeaponComponent',
        start_pos: 'PositionComponent',
        direction: 'Vector2',
        entity_manager: 'EntityManager',
        owner_entity: Optional['Entity'] = None,
    ) -> Optional['Entity']:
        """
        투사체 엔티티 생성
        
        Args:
            weapon: 무기 컴포넌트
            start_pos: 시작 위치
            direction: 정규화된 방향 벡터
            entity_manager: 엔티티 매니저
            owner_entity: 소유자 엔티티 (선택사항)
        
        Returns:
            생성된 투사체 엔티티 또는 None (실패 시)
        """
        try:
            # AI-NOTE : 2025-08-16 투사체 팩토리 패턴 도입
            # - 이유: 투사체 생성 로직을 AutoAttackSystem에서 분리
            # - 요구사항: 단일 책임 원칙 적용, 재사용 가능한 팩토리
            # - 히스토리: 기존 _execute_direction_attack 로직을 팩토리로 이동
            
            from ..components.collision_component import (
                CollisionComponent,
                CollisionLayer,
            )
            from ..components.projectile_component import ProjectileComponent
            from ..components.render_component import RenderComponent, RenderLayer
            from ..components.position_component import PositionComponent
            
            # 1. 투사체 엔티티 생성
            projectile_entity = entity_manager.create_entity()
            logger.debug(f"Created projectile entity: {projectile_entity.entity_id}")
            
            # 2. ProjectileComponent 추가
            projectile_comp = ProjectileComponent(
                direction=direction,
                velocity=400.0,  # 기본 투사체 속도
                damage=weapon.get_effective_damage(),
                lifetime=2.5,  # 기본 수명 2.5초
                owner_id=owner_entity.entity_id if owner_entity else None,
            )
            entity_manager.add_component(projectile_entity, projectile_comp)
            
            # 3. PositionComponent 추가 (월드 좌표 시작 위치)
            position_comp = PositionComponent(x=start_pos.x, y=start_pos.y)
            entity_manager.add_component(projectile_entity, position_comp)
            
            # 4. RenderComponent 추가 (투사체 시각화)
            projectile_surface = ProjectileFactory._create_projectile_sprite()
            render_comp = RenderComponent(
                sprite=projectile_surface,
                size=(6, 6),  # 6x6 픽셀 크기
                layer=RenderLayer.PROJECTILES,
                visible=True,
            )
            entity_manager.add_component(projectile_entity, render_comp)
            
            # 5. CollisionComponent 추가 (충돌 감지용)
            collision_comp = CollisionComponent(
                width=6.0,
                height=6.0,
                layer=CollisionLayer.PROJECTILE,
                collision_mask={CollisionLayer.ENEMY},  # 적과만 충돌
                is_trigger=True,  # 트리거 충돌 (관통 가능)
                is_solid=False,  # 비고체 (다른 객체를 밀어내지 않음)
            )
            entity_manager.add_component(projectile_entity, collision_comp)
            
            # AI-DEV : 투사체 컴포넌트 검증 로직
            # - 문제: 컴포넌트 추가 실패 시 엔티티가 남아있을 수 있음
            # - 해결책: 생성 후 필수 컴포넌트 존재 확인
            # - 주의사항: 실패 시 엔티티 정리 필요
            
            # 투사체 생성 완료 확인
            required_components = [
                (ProjectileComponent, "ProjectileComponent"),
                (PositionComponent, "PositionComponent"),
                (RenderComponent, "RenderComponent"),
                (CollisionComponent, "CollisionComponent"),
            ]
            
            for comp_type, comp_name in required_components:
                if not entity_manager.has_component(projectile_entity, comp_type):
                    logger.error(f"Failed to add {comp_name} to projectile {projectile_entity.entity_id}")
                    entity_manager.destroy_entity(projectile_entity)
                    return None
            
            logger.info(f"Successfully created projectile {projectile_entity.entity_id} with all components")
            return projectile_entity
            
        except Exception as e:
            logger.error(f'Failed to create projectile: {e}')
            import traceback
            logger.error(f'Traceback: {traceback.format_exc()}')
            
            # 실패 시 엔티티 정리 (생성되었다면)
            try:
                if 'projectile_entity' in locals():
                    entity_manager.destroy_entity(projectile_entity)
            except:
                pass  # 이미 정리되었거나 생성되지 않음
            
            return None
    
    @staticmethod
    def _create_projectile_sprite() -> pygame.Surface:
        """
        투사체 스프라이트 생성
        
        Returns:
            투사체 pygame.Surface
        """
        # AI-NOTE : 2025-08-16 투사체 스프라이트 표준화
        # - 이유: 일관된 투사체 외형 제공
        # - 요구사항: 6x6 픽셀 노란색 원형 투사체
        # - 히스토리: 기존 AutoAttackSystem의 스프라이트 생성 로직 추출
        
        projectile_surface = pygame.Surface((6, 6), pygame.SRCALPHA)
        projectile_surface.fill((255, 255, 0))  # 노란색 투사체
        pygame.draw.circle(
            projectile_surface, (255, 255, 255), (3, 3), 2, 1
        )  # 흰색 테두리
        
        return projectile_surface