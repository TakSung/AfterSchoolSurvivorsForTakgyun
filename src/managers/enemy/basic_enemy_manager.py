"""
EnemyManager 구현체 - 적 엔티티 특화 관리.

인터페이스 기반으로 설계되어 의존성 주입과 테스트 격리를 지원합니다.
"""

import random
import math
from typing import TYPE_CHECKING

from ...interfaces import IEnemyManager, IEntityManager, ICoordinateManager, IDifficultyManager
from ...components.collision_component import CollisionComponent, CollisionLayer
from ...components.enemy_ai_component import AIType, EnemyAIComponent
from ...components.enemy_component import EnemyComponent
from ...components.health_component import HealthComponent
from ...components.position_component import PositionComponent
from ...components.render_component import RenderComponent
from ...components.velocity_component import VelocityComponent
from ...utils.vector2 import Vector2
from ...managers.dto import EnemyDTO

if TYPE_CHECKING:
    from ...core.entity import Entity
    from ...dto.spawn_result import SpawnResult


class EnemyManagerImpl(IEnemyManager):
    """
    적 엔티티 생성 및 관리 특화 구현체.
    
    완전한 의존성 주입을 통해 테스트 용이성과 유연성을 제공합니다.
    """
    
    def __init__(
        self,
        entity_manager: IEntityManager,
        coordinate_manager: ICoordinateManager | None = None,
        difficulty_manager: IDifficultyManager | None = None,
    ) -> None:
        """
        EnemyManager 구현체 초기화.
        
        Args:
            entity_manager: 엔티티 CRUD 작업을 위한 EntityManager
            coordinate_manager: 좌표 변환을 위한 CoordinateManager (선택사항)
            difficulty_manager: 난이도 배율을 위한 DifficultyManager (선택사항)
        """
        # AI-NOTE : 2025-01-16 완전 의존성 주입을 통한 테스트 용이성 확보
        # - 이유: 모든 외부 의존성을 주입받아 Mock 객체로 테스트 가능
        # - 요구사항: 단위 테스트에서 각 매니저를 독립적으로 검증
        # - 비즈니스 가치: 안정적인 적 생성 로직 보장
        
        self._entity_manager = entity_manager
        self._coordinate_manager = coordinate_manager
        self._difficulty_manager = difficulty_manager
    
    @classmethod
    def create(
        cls,
        entity_manager: IEntityManager,
        coordinate_manager: ICoordinateManager | None = None,
        difficulty_manager: IDifficultyManager | None = None,
    ) -> 'IEnemyManager':
        """EnemyManager 구현체를 생성하는 스테틱 생성자"""
        return cls(entity_manager, coordinate_manager, difficulty_manager)
    
    def create_enemy_entity(self, spawn_result: 'SpawnResult') -> 'Entity':
        """
        SpawnResult 데이터를 기반으로 적 엔티티를 생성합니다.
        
        Args:
            spawn_result: 스폰 위치와 설정 정보
            
        Returns:
            생성된 적 엔티티
        """
        # AI-NOTE : 2025-01-16 SpawnResult 기반 적 컴포넌트 조립
        # - 이유: 스포너와 매니저 간 데이터 전달을 DTO로 표준화
        # - 요구사항: 스폰 위치, 난이도 정보를 바탕으로 적 생성
        # - 비즈니스 가치: 일관된 적 생성 프로세스 제공
        
        # 1. 기본 엔티티 생성
        entity = self._entity_manager.create_entity()
        
        # 2. 적 특화 컴포넌트들 추가
        self._add_basic_components(entity, spawn_result)
        self._add_ai_component(entity, spawn_result)
        self._add_physics_components(entity, spawn_result)
        
        return entity
    
    def get_enemy_count(self) -> int:
        """
        현재 활성 적 엔티티 수를 반환합니다.
        
        Returns:
            활성 적 엔티티 수
        """
        enemy_count = 0
        for entity, _ in self._entity_manager.get_entities_with_component(EnemyComponent):
            if entity.active:
                enemy_count += 1
        return enemy_count
    
    def get_enemies_in_range(self, center: Vector2, radius: float) -> list['Entity']:
        """
        지정된 범위 내의 모든 적 엔티티를 반환합니다.
        
        Args:
            center: 중심 좌표
            radius: 검색 반경
            
        Returns:
            범위 내의 적 엔티티 리스트
        """
        enemies_in_range = []
        
        for entity, _ in self._entity_manager.get_entities_with_component(EnemyComponent):
            if not entity.active:
                continue
                
            # 위치 컴포넌트 확인
            position_components = self._entity_manager.get_components(entity, PositionComponent)
            if not position_components:
                continue
                
            position = position_components[0]
            enemy_pos = Vector2(position.x, position.y)
            
            # 거리 계산
            distance = (enemy_pos - center).magnitude()
            if distance <= radius:
                enemies_in_range.append(entity)
        
        return enemies_in_range
    
    def get_closest_enemy(self, position: Vector2) -> 'Entity | None':
        """
        지정된 위치에서 가장 가까운 적 엔티티를 반환합니다.
        
        Args:
            position: 기준 위치
            
        Returns:
            가장 가까운 적 엔티티, 없으면 None
        """
        closest_enemy = None
        closest_distance = float('inf')
        
        for entity, _ in self._entity_manager.get_entities_with_component(EnemyComponent):
            if not entity.active:
                continue
                
            # 위치 컴포넌트 확인
            position_components = self._entity_manager.get_components(entity, PositionComponent)
            if not position_components:
                continue
                
            enemy_position = position_components[0]
            enemy_pos = Vector2(enemy_position.x, enemy_position.y)
            
            # 거리 계산
            distance = (enemy_pos - position).magnitude()
            if distance < closest_distance:
                closest_distance = distance
                closest_enemy = entity
        
        return closest_enemy
    
    def entity_to_enemy_dto(self, entity: 'Entity') -> EnemyDTO:
        """
        적 엔티티를 EnemyDTO로 변환합니다.
        
        Args:
            entity: 변환할 적 엔티티
            
        Returns:
            변환된 EnemyDTO
            
        Raises:
            ValueError: 적 엔티티가 아니거나 필수 컴포넌트가 없는 경우
        """
        # 적 컴포넌트 확인
        if not self._entity_manager.has_component(entity, EnemyComponent):
            raise ValueError(f"Entity {entity.entity_id} is not an enemy")
        
        # 필수 컴포넌트들 가져오기
        position_components = self._entity_manager.get_components(entity, PositionComponent)
        health_components = self._entity_manager.get_components(entity, HealthComponent)
        ai_components = self._entity_manager.get_components(entity, EnemyAIComponent)
        
        if not position_components or not health_components or not ai_components:
            raise ValueError(f"Enemy entity {entity.entity_id} missing required components")
        
        position = position_components[0]
        health = health_components[0]
        ai = ai_components[0]
        
        return EnemyDTO(
            entity_id=entity.entity_id,
            position=(position.x, position.y),
            health=health.current_health,
            max_health=health.max_health,
            ai_type=ai.ai_type.name,
            movement_speed=ai.movement_speed
        )
    
    def enemy_dto_to_entity(self, dto: EnemyDTO) -> 'Entity':
        """
        EnemyDTO를 기반으로 적 엔티티를 생성합니다.
        
        Args:
            dto: 생성할 적 정보
            
        Returns:
            생성된 적 엔티티
        """
        entity = self._entity_manager.create_entity()
        
        # 위치 컴포넌트
        self._entity_manager.add_component(
            entity, PositionComponent(x=dto.position[0], y=dto.position[1])
        )
        
        # 적 컴포넌트
        self._entity_manager.add_component(entity, EnemyComponent())
        
        # 체력 컴포넌트
        self._entity_manager.add_component(
            entity, HealthComponent(current_health=dto.health, max_health=dto.max_health)
        )
        
        # AI 컴포넌트
        ai_type = getattr(AIType, dto.ai_type)
        self._entity_manager.add_component(
            entity,
            EnemyAIComponent(
                ai_type=ai_type,
                chase_range=150.0,
                attack_range=50.0,
                movement_speed=dto.movement_speed,
            ),
        )
        
        # 기본 렌더링 컴포넌트
        self._entity_manager.add_component(
            entity,
            RenderComponent(color=(255, 100, 100), size=(20, 20)),
        )
        
        # 기본 물리 컴포넌트들
        self._entity_manager.add_component(entity, VelocityComponent(vx=0.0, vy=0.0))
        self._entity_manager.add_component(
            entity,
            CollisionComponent(
                width=20,
                height=20,
                layer=CollisionLayer.ENEMY,
                collision_mask={CollisionLayer.PLAYER, CollisionLayer.PROJECTILE},
            ),
        )
        
        return entity
    
    def _add_basic_components(self, entity: 'Entity', spawn_result: 'SpawnResult') -> None:
        """
        기본 적 컴포넌트들을 추가합니다.
        
        Args:
            entity: 컴포넌트를 추가할 엔티티
            spawn_result: 스폰 설정 정보
        """
        # 위치 컴포넌트
        self._entity_manager.add_component(
            entity, PositionComponent(x=spawn_result.x, y=spawn_result.y)
        )
        
        # 적 식별 컴포넌트
        self._entity_manager.add_component(entity, EnemyComponent())
        
        # 체력 컴포넌트 (난이도 배율 적용)
        base_health = spawn_result.get_additional_data('base_health', 100)
        scaled_health = int(base_health * spawn_result.difficulty_scale)
        
        # 난이도 매니저 배율 적용
        if self._difficulty_manager:
            health_multiplier = self._difficulty_manager.get_health_multiplier()
            scaled_health = int(scaled_health * health_multiplier)
        
        self._entity_manager.add_component(
            entity,
            HealthComponent(current_health=scaled_health, max_health=scaled_health),
        )
        
        # 렌더링 컴포넌트
        self._entity_manager.add_component(
            entity,
            RenderComponent(color=(255, 100, 100), size=(20, 20)),
        )
    
    def _add_ai_component(self, entity: 'Entity', spawn_result: 'SpawnResult') -> None:
        """
        AI 컴포넌트를 추가합니다.
        
        Args:
            entity: 컴포넌트를 추가할 엔티티
            spawn_result: 스폰 설정 정보
        """
        # AI-NOTE : 2025-01-16 랜덤 AI 타입 배정으로 적 다양성 구현
        # - 이유: 다양한 AI 행동 패턴으로 게임 재미 증대
        # - 요구사항: AGGRESSIVE, DEFENSIVE, PATROL 중 랜덤 선택
        # - 비즈니스 가치: 예측 불가능한 적 행동으로 전략적 게임플레이 제공
        
        # AI 타입 옵션 가져오기
        ai_type_options = spawn_result.get_additional_data(
            'ai_type_options', ['AGGRESSIVE', 'DEFENSIVE', 'PATROL']
        )
        
        # 문자열 옵션을 AIType enum으로 변환
        ai_types = []
        for option in ai_type_options:
            if hasattr(AIType, option):
                ai_types.append(getattr(AIType, option))
        
        if not ai_types:  # 기본값 사용
            ai_types = [AIType.AGGRESSIVE, AIType.DEFENSIVE, AIType.PATROL]
        
        selected_ai_type = random.choice(ai_types)
        
        # 기본 속도 및 난이도 배율 적용
        base_speed = spawn_result.get_additional_data('base_speed', 80.0)
        scaled_speed = base_speed * spawn_result.difficulty_scale
        
        if self._difficulty_manager:
            speed_multiplier = self._difficulty_manager.get_speed_multiplier()
            scaled_speed *= speed_multiplier
        
        self._entity_manager.add_component(
            entity,
            EnemyAIComponent(
                ai_type=selected_ai_type,
                chase_range=150.0,
                attack_range=50.0,
                movement_speed=scaled_speed,
            ),
        )
    
    def _add_physics_components(self, entity: 'Entity', spawn_result: 'SpawnResult') -> None:
        """
        물리 및 충돌 컴포넌트들을 추가합니다.
        
        Args:
            entity: 컴포넌트를 추가할 엔티티
            spawn_result: 스폰 설정 정보
        """
        # 속도 컴포넌트
        self._entity_manager.add_component(entity, VelocityComponent(vx=0.0, vy=0.0))
        
        # 충돌 컴포넌트
        self._entity_manager.add_component(
            entity,
            CollisionComponent(
                width=20,
                height=20,
                layer=CollisionLayer.ENEMY,
                collision_mask={
                    CollisionLayer.PLAYER,
                    CollisionLayer.PROJECTILE,
                },
            ),
        )