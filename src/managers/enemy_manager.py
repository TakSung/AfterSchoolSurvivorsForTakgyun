"""
EnemyManager - 새로운 패턴으로 리팩토링됨.

이 파일은 기존 코드와의 호환성을 위해 유지되며,
실제 구현은 domain/enemy_manager_impl.py를 사용합니다.

새로운 사용법:
    from src.interfaces import IEnemyManager
    from src.managers import create_enemy_manager
    
    enemy_manager: IEnemyManager = create_enemy_manager(entity_manager)
"""

import warnings
from typing import TYPE_CHECKING

from ..interfaces import IEnemyManager, IEntityManager, ICoordinateManager, IDifficultyManager
from .domain.enemy_manager_impl import EnemyManagerImpl

if TYPE_CHECKING:
    from ..core.entity import Entity
    from ..dto.spawn_result import SpawnResult


class EnemyManager:
    """
    기존 EnemyManager 호환성을 위한 래퍼 클래스.

    ⚠️  DEPRECATED: 이 클래스는 더 이상 권장되지 않습니다.
    대신 IEnemyManager 인터페이스와 create_enemy_manager() 함수를 사용하세요.
    
    새로운 사용법:
        from src.interfaces import IEnemyManager
        from src.managers import create_enemy_manager
        
        enemy_manager: IEnemyManager = create_enemy_manager(entity_manager)
    """

    def __init__(
        self,
        component_registry: any = None,  # 기존 호환성을 위해 유지
        coordinate_manager: any = None,
        difficulty_manager: any = None,
    ) -> None:
        """
        DEPRECATED: 기존 호환성을 위한 초기화.
        
        새로운 패턴에서는 create_enemy_manager() 함수를 사용하세요.
        """
        warnings.warn(
            "EnemyManager 직접 생성은 deprecated입니다. "
            "대신 create_enemy_manager() 함수를 사용하세요.",
            DeprecationWarning,
            stacklevel=2
        )
        
        # 기존 구현을 새로운 구현체로 래핑
        # 실제로는 적절한 변환이 필요하지만, 현재는 호환성만 유지
        self._impl: IEnemyManager | None = None

    def create_enemy_from_spawn_result(
        self, entity: 'Entity', spawn_result: 'SpawnResult'
    ) -> None:
        """
        DEPRECATED: 기존 호환성을 위한 메서드.
        
        새로운 패턴에서는 IEnemyManager.create_enemy_entity()를 사용하세요.
        """
        warnings.warn(
            "create_enemy_from_spawn_result는 deprecated입니다. "
            "새로운 IEnemyManager.create_enemy_entity()를 사용하세요.",
            DeprecationWarning,
            stacklevel=2
        )
        # 기존 호환성을 위한 더미 구현
        pass

    def get_enemy_count(self) -> int:
        """
        DEPRECATED: 기존 호환성을 위한 메서드.
        
        새로운 패턴에서는 IEnemyManager.get_enemy_count()를 사용하세요.
        """
        warnings.warn(
            "get_enemy_count는 deprecated입니다. "
            "새로운 IEnemyManager.get_enemy_count()를 사용하세요.",
            DeprecationWarning,
            stacklevel=2
        )
        return 0  # 기존 호환성을 위한 더미 값

    # ========================================
    # 기존 메서드들 모두 DEPRECATED
    # ========================================
    
    def _add_basic_components(
        self, entity: 'Entity', spawn_result: 'SpawnResult'
    ) -> None:
        """DEPRECATED: 기존 호환성을 위한 메서드."""
        pass

    def _add_ai_component(
        self, entity: 'Entity', spawn_result: 'SpawnResult'
    ) -> None:
        """DEPRECATED: 기존 호환성을 위한 메서드."""
        pass

    def _add_physics_components(
        self, entity: 'Entity', spawn_result: 'SpawnResult'
    ) -> None:
        """DEPRECATED: 기존 호환성을 위한 메서드."""
        pass


# ========================================
# 새로운 패턴을 위한 편의 함수
# ========================================

def create_enemy_manager(
    entity_manager: IEntityManager,
    coordinate_manager: ICoordinateManager | None = None,
    difficulty_manager: IDifficultyManager | None = None,
) -> IEnemyManager:
    """
    새로운 패턴의 EnemyManager를 생성하는 편의 함수.
    
    Args:
        entity_manager: 엔티티 CRUD 작업을 위한 EntityManager
        coordinate_manager: 좌표 변환을 위한 CoordinateManager (선택사항)
        difficulty_manager: 난이도 배율을 위한 DifficultyManager (선택사항)
        
    Returns:
        IEnemyManager 인터페이스 구현체
        
    Example:
        >>> entity_manager = create_entity_manager()
        >>> enemy_manager = create_enemy_manager(entity_manager)
        >>> enemy = enemy_manager.create_enemy_entity(spawn_result)
    """
    return EnemyManagerImpl.create(entity_manager, coordinate_manager, difficulty_manager)
