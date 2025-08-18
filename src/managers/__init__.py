"""
Manager 모듈 편의 함수들 - Core/Domain 통합

새로운 Manager 패턴을 위한 편의 함수들을 제공합니다.
인터페이스 기반 설계로 구현체를 숨기고 의존성 주입을 지원합니다.
"""

from ..interfaces import (
    # Core Managers
    ICoordinateManager, IDifficultyManager, IGameStateManager, ITimeManager,
    # Domain Managers  
    IEntityManager, IEnemyManager, IWeaponManager, IProjectileManager
)

from .enemy_manager import EnemyManager, create_enemy_manager  # 기존 호환성 + 새로운 패턴

# Import implementations
from .entity.crud_entity_manager import EntityManager as CrudEntityManager
from .weapon.basic_weapon_manager import WeaponManager as BasicWeaponManager
from .projectile.physics_projectile_manager import ProjectileManager as PhysicsProjectileManager
from .enemy.basic_enemy_manager import EnemyManagerImpl as BasicEnemyManager


# ========================================
# Domain Manager 생성 함수들
# ========================================

def create_entity_manager() -> IEntityManager:
    """EntityManager 생성 편의 함수"""
    return CrudEntityManager.create()


def create_weapon_manager(entity_manager: IEntityManager) -> IWeaponManager:
    """WeaponManager 생성 편의 함수"""
    return BasicWeaponManager.create(entity_manager)


def create_projectile_manager() -> IProjectileManager:
    """ProjectileManager 생성 편의 함수"""
    return PhysicsProjectileManager.create()


# ========================================
# Core Manager 생성 함수들 (향후 추가될 예정)
# ========================================

def create_coordinate_manager() -> ICoordinateManager:
    """CoordinateManager 생성 편의 함수"""
    return ICoordinateManager.create()


def create_difficulty_manager() -> IDifficultyManager:
    """DifficultyManager 생성 편의 함수"""
    return IDifficultyManager.create()


def create_game_state_manager(config_path: str = 'config.json', auto_save: bool = True) -> IGameStateManager:
    """GameStateManager 생성 편의 함수"""
    return IGameStateManager.create(config_path, auto_save)


def create_time_manager() -> ITimeManager:
    """TimeManager 생성 편의 함수"""
    return ITimeManager.create()


# ========================================
# 통합 생성 함수들
# ========================================

def create_core_managers() -> tuple[ICoordinateManager, IDifficultyManager, IGameStateManager, ITimeManager]:
    """모든 Core Manager들을 한 번에 생성하는 편의 함수"""
    coordinate_manager = create_coordinate_manager()
    difficulty_manager = create_difficulty_manager()
    game_state_manager = create_game_state_manager()
    time_manager = create_time_manager()
    
    return coordinate_manager, difficulty_manager, game_state_manager, time_manager


def create_domain_managers(
    coordinate_manager: ICoordinateManager | None = None,
    difficulty_manager: IDifficultyManager | None = None
) -> tuple[IEntityManager, IEnemyManager, IWeaponManager, IProjectileManager]:
    """모든 Domain Manager들을 한 번에 생성하는 편의 함수"""
    entity_manager = create_entity_manager()
    enemy_manager = create_enemy_manager(entity_manager, coordinate_manager, difficulty_manager)
    weapon_manager = create_weapon_manager(entity_manager)
    projectile_manager = create_projectile_manager()
    
    return entity_manager, enemy_manager, weapon_manager, projectile_manager


def create_all_managers() -> dict[str, any]:
    """모든 Manager들을 한 번에 생성하는 편의 함수"""
    # Core Managers 생성
    coordinate_manager, difficulty_manager, game_state_manager, time_manager = create_core_managers()
    
    # Domain Managers 생성 (Core Managers 주입)
    entity_manager, enemy_manager, weapon_manager, projectile_manager = create_domain_managers(
        coordinate_manager, difficulty_manager
    )
    
    return {
        # Core
        'coordinate': coordinate_manager,
        'difficulty': difficulty_manager,
        'game_state': game_state_manager,
        'time': time_manager,
        # Domain
        'entity': entity_manager,
        'enemy': enemy_manager,
        'weapon': weapon_manager,
        'projectile': projectile_manager
    }


__all__ = [
    # 기존 호환성
    'EnemyManager',
    # 새로운 패턴 Domain Manager 생성 함수들
    'create_entity_manager',
    'create_enemy_manager', 
    'create_weapon_manager',
    'create_projectile_manager',
    # Core Manager 생성 함수들
    'create_coordinate_manager',
    'create_difficulty_manager', 
    'create_game_state_manager',
    'create_time_manager',
    # 통합 생성 함수들
    'create_core_managers',
    'create_domain_managers',
    'create_all_managers'
]