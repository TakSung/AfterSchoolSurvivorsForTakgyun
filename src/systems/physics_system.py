"""
Physics system for ECS architecture.

Handles basic physics calculations including velocity, acceleration,
and position updates using 2D vector operations.
"""

from typing import TYPE_CHECKING
import numpy as np
import logging

from ..core.system import System

if TYPE_CHECKING:
    from ..core.entity import Entity
    from ..core.entity_manager import EntityManager
    from ..components.position_component import PositionComponent

logger = logging.getLogger(__name__)


class PhysicsSystem(System):
    """
    System that handles basic physics calculations for entities.
    
    Processes entities with position and velocity components to update
    their positions based on physics calculations.
    """

    def __init__(self, priority: int = 10) -> None:
        """
        Initialize the physics system.
        
        Args:
            priority: System execution priority (lower number = earlier execution).
        """
        super().__init__(priority)
        self._gravity = np.array([0.0, 0.0])  # 2D gravity vector

    def initialize(self) -> None:
        """Initialize the physics system."""
        super().initialize()
        logger.info("PhysicsSystem initialized")

    def get_required_components(self) -> list[type]:
        """
        Get required component types for physics calculations.
        
        Returns:
            List containing PositionComponent and VelocityComponent types.
        """
        from ..components.position_component import PositionComponent
        from ..components.velocity_component import VelocityComponent
        
        return [PositionComponent, VelocityComponent]

    def update(self, entity_manager: 'EntityManager', delta_time: float) -> None:
        """
        Update physics calculations for all entities.
        
        Args:
            entity_manager: Manager to access entities and components.
            delta_time: Time elapsed since last update in seconds.
        """
        if not self.enabled:
            return

        entities = self.filter_entities(entity_manager)
        
        for entity in entities:
            self._update_entity_physics(entity_manager, entity, delta_time)

    def _update_entity_physics(
        self, 
        entity_manager: 'EntityManager', 
        entity: 'Entity', 
        delta_time: float
    ) -> None:
        """
        Update physics for a single entity.
        
        Args:
            entity_manager: Manager to access entity components.
            entity: Entity to update physics for.
            delta_time: Time elapsed since last update in seconds.
        """
        position = entity_manager.get_component(entity, 'PositionComponent')
        velocity = entity_manager.get_component(entity, 'VelocityComponent')

        if not position or not velocity:
            return

        # AI-NOTE : 2025-01-11 프레임 독립적인 물리 계산 구현
        # - 이유: 게임이 다양한 프레임레이트에서 일관되게 동작해야 함
        # - 요구사항: 델타 타임 기반으로 위치와 속도 업데이트
        # - 히스토리: numpy 기반 벡터 연산으로 성능 최적화
        
        # 현재 위치와 속도를 numpy 벡터로 변환
        current_pos = np.array([position.x, position.y])
        current_vel = np.array([velocity.vx, velocity.vy])
        
        # 중력 적용 (가속도)
        if hasattr(velocity, 'apply_gravity') and velocity.apply_gravity:
            current_vel += self._gravity * delta_time
            velocity.vx = float(current_vel[0])
            velocity.vy = float(current_vel[1])
        
        # 마찰력 적용
        if hasattr(velocity, 'friction') and velocity.friction > 0:
            friction_force = self.calculate_friction(current_vel, velocity.friction)
            current_vel += friction_force * delta_time
            velocity.vx = float(current_vel[0])
            velocity.vy = float(current_vel[1])
        
        # 위치 업데이트 (속도 * 시간)
        new_position = current_pos + current_vel * delta_time
        position.x = float(new_position[0])
        position.y = float(new_position[1])

    def calculate_velocity_from_acceleration(
        self, 
        current_velocity: tuple[float, float], 
        acceleration: tuple[float, float], 
        delta_time: float
    ) -> tuple[float, float]:
        """
        Calculate new velocity from current velocity and acceleration.
        
        Args:
            current_velocity: Current velocity as (vx, vy) tuple.
            acceleration: Acceleration as (ax, ay) tuple.
            delta_time: Time step for integration.
            
        Returns:
            New velocity as (vx, vy) tuple.
        """
        vel = np.array(current_velocity)
        acc = np.array(acceleration)
        
        new_vel = vel + acc * delta_time
        return (float(new_vel[0]), float(new_vel[1]))

    def calculate_position_from_velocity(
        self, 
        current_position: tuple[float, float], 
        velocity: tuple[float, float], 
        delta_time: float
    ) -> tuple[float, float]:
        """
        Calculate new position from current position and velocity.
        
        Args:
            current_position: Current position as (x, y) tuple.
            velocity: Velocity as (vx, vy) tuple.
            delta_time: Time step for integration.
            
        Returns:
            New position as (x, y) tuple.
        """
        pos = np.array(current_position)
        vel = np.array(velocity)
        
        new_pos = pos + vel * delta_time
        return (float(new_pos[0]), float(new_pos[1]))

    def calculate_friction(
        self, 
        velocity: np.ndarray, 
        friction_coefficient: float
    ) -> np.ndarray:
        """
        Calculate friction force opposing velocity.
        
        Args:
            velocity: Current velocity vector.
            friction_coefficient: Friction coefficient (0.0 = no friction, 1.0 = full stop).
            
        Returns:
            Friction force vector.
        """
        # AI-DEV : 속도 방향 반대로 작용하는 마찰력 계산
        # - 문제: 속도가 0에 가까울 때 방향 계산 오류 발생 가능
        # - 해결책: 속도 크기가 임계값 이하면 0으로 설정
        # - 주의사항: 마찰 계수가 너무 크면 진동 현상 발생 가능
        
        velocity_magnitude = np.linalg.norm(velocity)
        
        if velocity_magnitude < 1e-6:  # 매우 작은 속도는 0으로 처리
            return np.array([0.0, 0.0])
        
        # 속도 방향의 반대로 마찰력 적용
        friction_direction = -velocity / velocity_magnitude
        friction_force = friction_direction * friction_coefficient * velocity_magnitude
        
        return friction_force

    def normalize_vector(self, vector: tuple[float, float]) -> tuple[float, float]:
        """
        Normalize a 2D vector to unit length.
        
        Args:
            vector: Vector to normalize as (x, y) tuple.
            
        Returns:
            Normalized vector as (x, y) tuple.
        """
        vec = np.array(vector)
        magnitude = np.linalg.norm(vec)
        
        if magnitude < 1e-6:  # 영벡터는 그대로 반환
            return (0.0, 0.0)
        
        normalized = vec / magnitude
        return (float(normalized[0]), float(normalized[1]))

    def vector_add(
        self, 
        vector1: tuple[float, float], 
        vector2: tuple[float, float]
    ) -> tuple[float, float]:
        """
        Add two 2D vectors.
        
        Args:
            vector1: First vector as (x, y) tuple.
            vector2: Second vector as (x, y) tuple.
            
        Returns:
            Sum vector as (x, y) tuple.
        """
        result = np.array(vector1) + np.array(vector2)
        return (float(result[0]), float(result[1]))

    def vector_multiply(
        self, 
        vector: tuple[float, float], 
        scalar: float
    ) -> tuple[float, float]:
        """
        Multiply a vector by a scalar.
        
        Args:
            vector: Vector to multiply as (x, y) tuple.
            scalar: Scalar multiplier.
            
        Returns:
            Scaled vector as (x, y) tuple.
        """
        result = np.array(vector) * scalar
        return (float(result[0]), float(result[1]))

    def vector_magnitude(self, vector: tuple[float, float]) -> float:
        """
        Calculate the magnitude of a 2D vector.
        
        Args:
            vector: Vector as (x, y) tuple.
            
        Returns:
            Magnitude of the vector.
        """
        return float(np.linalg.norm(np.array(vector)))

    def vector_distance(
        self, 
        point1: tuple[float, float], 
        point2: tuple[float, float]
    ) -> float:
        """
        Calculate distance between two points.
        
        Args:
            point1: First point as (x, y) tuple.
            point2: Second point as (x, y) tuple.
            
        Returns:
            Distance between the points.
        """
        diff = np.array(point2) - np.array(point1)
        return float(np.linalg.norm(diff))

    def set_gravity(self, gravity_x: float, gravity_y: float) -> None:
        """
        Set gravity vector for the physics system.
        
        Args:
            gravity_x: X component of gravity.
            gravity_y: Y component of gravity (positive = downward).
        """
        self._gravity = np.array([gravity_x, gravity_y])

    def get_gravity(self) -> tuple[float, float]:
        """
        Get current gravity vector.
        
        Returns:
            Gravity vector as (x, y) tuple.
        """
        return (float(self._gravity[0]), float(self._gravity[1]))

    def cleanup(self) -> None:
        """Clean up physics system resources."""
        super().cleanup()
        logger.info("PhysicsSystem cleanup completed")