"""
EnemyManager for specialized enemy entity management.

This manager handles enemy-specific entity creation and component assembly,
with all dependencies injected from the outside for testability.
"""

import random
from typing import TYPE_CHECKING

from ..components.collision_component import CollisionComponent, CollisionLayer
from ..components.enemy_ai_component import AIType, EnemyAIComponent
from ..components.enemy_component import EnemyComponent
from ..components.health_component import HealthComponent
from ..components.position_component import PositionComponent
from ..components.render_component import RenderComponent
from ..components.velocity_component import VelocityComponent

if TYPE_CHECKING:
    from ..core.coordinate_manager import CoordinateManager
    from ..core.difficulty_manager import DifficultyManager
    from ..core.entity import Entity
    from ..core.interfaces.i_component_registry import IComponentRegistry
    from ..dto.spawn_result import SpawnResult


class EnemyManager:
    """
    Specialized manager for enemy entity creation and management.

    Handles enemy-specific component assembly and lifecycle management
    with complete dependency injection for testability and flexibility.
    """

    def __init__(
        self,
        component_registry: 'IComponentRegistry',
        coordinate_manager: 'CoordinateManager',
        difficulty_manager: 'DifficultyManager',
    ) -> None:
        """
        Initialize EnemyManager with injected dependencies.

        Args:
            component_registry: Component registry for entity operations
            coordinate_manager: Coordinate transformation manager
            difficulty_manager: Difficulty scaling manager
        """
        # AI-NOTE : 2025-01-16 완전 의존성 주입을 통한 테스트 용이성 확보
        # - 이유: 모든 외부 의존성을 주입받아 Mock 객체로 테스트 가능
        # - 요구사항: 단위 테스트에서 각 매니저를 독립적으로 검증
        # - 비즈니스 가치: 안정적인 적 생성 로직 보장
        self._component_registry = component_registry
        self._coordinate_manager = coordinate_manager
        self._difficulty_manager = difficulty_manager

    def create_enemy_from_spawn_result(
        self, entity: 'Entity', spawn_result: 'SpawnResult'
    ) -> None:
        """
        Create enemy entity from spawn result data.

        Takes an existing entity and adds enemy-specific components
        based on the provided spawn result information.

        Args:
            entity: Existing entity to configure as enemy
            spawn_result: Spawn data containing position and configuration
        """
        # AI-NOTE : 2025-01-16 SpawnResult 기반 적 컴포넌트 조립
        # - 이유: 스포너와 매니저 간 데이터 전달을 DTO로 표준화
        # - 요구사항: 스폰 위치, 난이도 정보를 바탕으로 적 생성
        # - 비즈니스 가치: 일관된 적 생성 프로세스 제공

        self._add_basic_components(entity, spawn_result)
        self._add_ai_component(entity, spawn_result)
        self._add_physics_components(entity, spawn_result)

    def get_enemy_count(self) -> int:
        """
        Get current number of enemy entities.

        Returns:
            Number of active enemy entities in the game.
        """
        enemy_count = 0
        for entity, _ in self._component_registry.get_entities_with_components(
            EnemyComponent, PositionComponent
        ):
            if entity.active:
                enemy_count += 1
        return enemy_count

    def _add_basic_components(
        self, entity: 'Entity', spawn_result: 'SpawnResult'
    ) -> None:
        """
        Add basic enemy components.

        Args:
            entity: Entity to configure
            spawn_result: Spawn configuration data
        """
        # Position component from spawn result
        self._component_registry.add_component(
            entity, PositionComponent(x=spawn_result.x, y=spawn_result.y)
        )

        # Enemy identification component
        self._component_registry.add_component(entity, EnemyComponent())

        # Health component with difficulty scaling
        base_health = spawn_result.get_additional_data('base_health', 100)
        scaled_health = int(base_health * spawn_result.difficulty_scale)

        # Apply difficulty manager scaling if available
        health_multiplier = self._difficulty_manager.get_health_multiplier()
        final_health = int(scaled_health * health_multiplier)

        self._component_registry.add_component(
            entity,
            HealthComponent(
                current_health=final_health, max_health=final_health
            ),
        )

        # Render component (basic enemy appearance)
        self._component_registry.add_component(
            entity,
            RenderComponent(
                color=(255, 100, 100),  # Light red color
                size=(20, 20),
            ),
        )

    def _add_ai_component(
        self, entity: 'Entity', spawn_result: 'SpawnResult'
    ) -> None:
        """
        Add AI component with random AI type.

        Args:
            entity: Entity to configure
            spawn_result: Spawn configuration data
        """
        # AI-NOTE : 2025-01-16 랜덤 AI 타입 배정으로 적 다양성 구현
        # - 이유: 다양한 AI 행동 패턴으로 게임 재미 증대
        # - 요구사항: AGGRESSIVE, DEFENSIVE, PATROL 중 랜덤 선택
        # - 비즈니스 가치: 예측 불가능한 적 행동으로 전략적 게임플레이 제공

        # Get AI type options from spawn result or use defaults
        ai_type_options = spawn_result.get_additional_data(
            'ai_type_options', ['AGGRESSIVE', 'DEFENSIVE', 'PATROL']
        )

        # Convert string options to AIType enum
        ai_types = []
        for option in ai_type_options:
            if hasattr(AIType, option):
                ai_types.append(getattr(AIType, option))

        if not ai_types:  # Fallback to all types
            ai_types = [AIType.AGGRESSIVE, AIType.DEFENSIVE, AIType.PATROL]

        selected_ai_type = random.choice(ai_types)

        # Base speed with difficulty scaling
        base_speed = spawn_result.get_additional_data('base_speed', 80.0)
        speed_multiplier = self._difficulty_manager.get_speed_multiplier()
        scaled_speed = (
            base_speed * speed_multiplier * spawn_result.difficulty_scale
        )

        self._component_registry.add_component(
            entity,
            EnemyAIComponent(
                ai_type=selected_ai_type,
                chase_range=150.0,
                attack_range=50.0,
                movement_speed=scaled_speed,
            ),
        )

    def _add_physics_components(
        self, entity: 'Entity', spawn_result: 'SpawnResult'
    ) -> None:
        """
        Add physics and collision components.

        Args:
            entity: Entity to configure
            spawn_result: Spawn configuration data
        """
        # Velocity component (used by AI system)
        self._component_registry.add_component(
            entity, VelocityComponent(vx=0.0, vy=0.0)
        )

        # Collision component (basic collision box)
        self._component_registry.add_component(
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
