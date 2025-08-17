"""
모든 Manager 인터페이스 정의.

Core Manager와 Domain Manager 인터페이스를 통합 관리하여
일관된 아키텍처 패턴을 제공합니다.
"""

from abc import ABC, abstractmethod
from typing import TypeVar, TYPE_CHECKING, Any, Callable

if TYPE_CHECKING:
    from .core.entity import Entity
    from .core.component import Component
    from .utils.vector2 import Vector2
    from .core.coordinate_transformer import ICoordinateTransformer
    from .dto.spawn_result import SpawnResult
    from .managers.dto import EnemyDTO, WeaponDTO, ProjectileDTO

T = TypeVar('T', bound='Component')


# ========================================
# Core Manager 인터페이스들 (시스템 레벨)
# ========================================

class ICoordinateManager(ABC):
    """좌표 변환 시스템 관리 인터페이스"""
    
    @classmethod
    @abstractmethod
    def create(cls) -> 'ICoordinateManager':
        """CoordinateManager 구현체를 생성하는 스테틱 생성자"""
        pass
    
    @classmethod
    @abstractmethod
    def get_instance(cls) -> 'ICoordinateManager':
        """싱글톤 인스턴스 반환"""
        pass
    
    @abstractmethod
    def world_to_screen(self, world_pos: 'Vector2') -> 'Vector2': ...
    
    @abstractmethod
    def screen_to_world(self, screen_pos: 'Vector2') -> 'Vector2': ...
    
    @abstractmethod
    def set_transformer(self, transformer: 'ICoordinateTransformer') -> None: ...
    
    @abstractmethod
    def get_transformer(self) -> 'ICoordinateTransformer | None': ...
    
    @abstractmethod
    def add_observer(self, observer: Any) -> None: ...
    
    @abstractmethod
    def remove_observer(self, observer: Any) -> None: ...


class IDifficultyManager(ABC):
    """게임 난이도 관리 인터페이스"""
    
    @classmethod
    @abstractmethod
    def create(cls) -> 'IDifficultyManager':
        """DifficultyManager 구현체를 생성하는 스테틱 생성자"""
        pass
    
    @classmethod
    @abstractmethod
    def get_instance(cls) -> 'IDifficultyManager':
        """싱글톤 인스턴스 반환"""
        pass
    
    @abstractmethod
    def update(self, delta_time: float) -> None: ...
    
    @abstractmethod
    def get_health_multiplier(self) -> float: ...
    
    @abstractmethod
    def get_speed_multiplier(self) -> float: ...
    
    @abstractmethod
    def get_spawn_rate_multiplier(self) -> float: ...
    
    @abstractmethod
    def get_current_level(self) -> Any: ...  # DifficultyLevel
    
    @abstractmethod
    def reset(self) -> None: ...


class IGameStateManager(ABC):
    """게임 상태 관리 인터페이스"""
    
    @classmethod
    @abstractmethod
    def create(cls, config_path: str = 'config.json', auto_save: bool = True) -> 'IGameStateManager':
        """GameStateManager 구현체를 생성하는 스테틱 생성자"""
        pass
    
    @abstractmethod
    def get_current_state(self) -> Any: ...  # GameState
    
    @abstractmethod
    def set_state(self, new_state: Any) -> None: ...  # GameState
    
    @abstractmethod
    def add_state_callback(self, state: Any, callback: Callable[[], None]) -> None: ...
    
    @abstractmethod
    def add_transition_callback(self, callback: Callable[[Any, Any], None]) -> None: ...
    
    @abstractmethod
    def get_config(self, key: str, default: Any = None) -> Any: ...
    
    @abstractmethod
    def set_config(self, key: str, value: Any) -> None: ...
    
    @abstractmethod
    def save_config(self) -> bool: ...


class ITimeManager(ABC):
    """시간 관리 인터페이스"""
    
    @classmethod
    @abstractmethod
    def create(cls, time_mode: Any = None, fixed_timestep: float = 1.0/60.0) -> 'ITimeManager':
        """TimeManager 구현체를 생성하는 스테틱 생성자"""
        pass
    
    @abstractmethod
    def update(self) -> None: ...
    
    @abstractmethod
    def get_delta_time(self) -> float: ...
    
    @abstractmethod
    def get_total_time(self) -> float: ...
    
    @abstractmethod
    def get_time_scale(self) -> float: ...
    
    @abstractmethod
    def set_time_scale(self, scale: float) -> None: ...
    
    @abstractmethod
    def add_update_callback(self, callback: Callable[[float], None]) -> None: ...
    
    @abstractmethod
    def reset(self) -> None: ...


# ========================================
# Domain Manager 인터페이스들 (게임 로직)
# ========================================

class IEntityManager(ABC):
    """순수 엔티티 CRUD 작업만 담당하는 기본 인터페이스"""
    
    @classmethod
    @abstractmethod
    def create(cls, component_registry: Any = None) -> 'IEntityManager':
        """EntityManager 구현체를 생성하는 스테틱 생성자"""
        pass
    
    @abstractmethod
    def create_entity(self) -> 'Entity': ...
    
    @abstractmethod
    def destroy_entity(self, entity: 'Entity') -> None: ...
    
    @abstractmethod
    def get_entity(self, entity_id: str) -> 'Entity | None': ...
    
    @abstractmethod
    def get_all_entities(self) -> list['Entity']: ...
    
    @abstractmethod
    def get_active_entities(self) -> list['Entity']: ...
    
    # 제네릭 타입 안전성 + 다중 컴포넌트 지원
    @abstractmethod
    def add_component(self, entity: 'Entity', component: 'Component') -> None: ...
    
    @abstractmethod
    def remove_component(self, entity: 'Entity', component_type: type['Component']) -> None: ...
    
    @abstractmethod
    def get_components(self, entity: 'Entity', component_type: type[T]) -> list[T]:
        """같은 타입의 컴포넌트들을 리스트로 반환 (다중 컴포넌트 지원)"""
        pass
    
    @abstractmethod
    def has_component(self, entity: 'Entity', component_type: type['Component']) -> bool: ...
    
    @abstractmethod
    def get_entities_with_component(self, component_type: type[T]) -> list[tuple['Entity', list[T]]]:
        """컴포넌트와 함께 엔티티들을 반환 (다중 컴포넌트 지원)"""
        pass
    
    @abstractmethod
    def get_entities_with_components(self, *component_types: type['Component']) -> list['Entity']: ...


class IEnemyManager(ABC):
    """적 엔티티 생성 및 관리 특화 인터페이스"""
    
    @classmethod
    @abstractmethod
    def create(cls, entity_manager: IEntityManager, 
              coordinate_manager: ICoordinateManager | None = None, 
              difficulty_manager: IDifficultyManager | None = None) -> 'IEnemyManager':
        """EnemyManager 구현체를 생성하는 스테틱 생성자"""
        pass
    
    @abstractmethod
    def create_enemy_entity(self, spawn_result: 'SpawnResult') -> 'Entity': ...
    
    @abstractmethod
    def get_enemy_count(self) -> int: ...
    
    @abstractmethod
    def get_enemies_in_range(self, center: 'Vector2', radius: float) -> list['Entity']: ...
    
    @abstractmethod
    def get_closest_enemy(self, position: 'Vector2') -> 'Entity | None': ...
    
    # DTO 변환 메서드들
    @abstractmethod
    def entity_to_enemy_dto(self, entity: 'Entity') -> 'EnemyDTO': ...
    
    @abstractmethod
    def enemy_dto_to_entity(self, dto: 'EnemyDTO') -> 'Entity': ...


class IWeaponManager(ABC):
    """무기 관리 및 스탯 계산 특화 인터페이스"""
    
    @classmethod
    @abstractmethod
    def create(cls, entity_manager: IEntityManager) -> 'IWeaponManager':
        """WeaponManager 구현체를 생성하는 스테틱 생성자"""
        pass
    
    # 다중 무기 지원
    @abstractmethod
    def get_weapon_components(self, entity: 'Entity') -> list[Any]:  # list[WeaponComponent]
        """엔티티의 모든 무기 컴포넌트들을 반환 (다중 무기 지원)"""
        pass
    
    @abstractmethod
    def get_primary_weapon(self, entity: 'Entity') -> Any:  # WeaponComponent | None
        """주 무기 컴포넌트 반환"""
        pass
    
    @abstractmethod
    def get_effective_attack_speed(self, entity: 'Entity', weapon_index: int = 0) -> float: ...
    
    @abstractmethod
    def get_effective_damage(self, entity: 'Entity', weapon_index: int = 0) -> int: ...
    
    @abstractmethod
    def get_total_dps(self, entity: 'Entity') -> float:
        """모든 무기의 합계 DPS 계산"""
        pass
    
    @abstractmethod
    def update_weapon_stats(self, entity: 'Entity') -> None: ...
    
    # DTO 변환 메서드들
    @abstractmethod
    def entity_to_weapon_dto(self, entity: 'Entity') -> 'WeaponDTO': ...
    
    @abstractmethod
    def weapon_dto_to_entity(self, dto: 'WeaponDTO') -> 'Entity': ...


class IProjectileManager(ABC):
    """투사체 추적 및 관리 특화 인터페이스"""
    
    @classmethod
    @abstractmethod
    def create(cls) -> 'IProjectileManager':
        """ProjectileManager 구현체를 생성하는 스테틱 생성자"""
        pass
    
    @abstractmethod
    def register_projectile_entity(self, entity: 'Entity') -> None: ...
    
    @abstractmethod
    def unregister_projectile(self, projectile_entity_id: str) -> bool: ...
    
    @abstractmethod
    def get_active_projectiles(self) -> list[str]: ...
    
    @abstractmethod
    def get_projectile_count(self) -> int: ...
    
    @abstractmethod
    def cleanup_inactive_projectiles(self, entity_manager: IEntityManager) -> int: ...
    
    # DTO 변환 메서드들
    @abstractmethod
    def entity_to_projectile_dto(self, entity: 'Entity') -> 'ProjectileDTO': ...
    
    @abstractmethod
    def projectile_dto_to_entity(self, dto: 'ProjectileDTO') -> 'Entity': ...