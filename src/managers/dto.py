"""
Manager 시스템을 위한 데이터 전송 객체들.

모든 DTO는 순수 데이터 구조로 설계되어 다른 인터페이스에 종속되지 않습니다.
변환 메서드는 각 Manager 인터페이스에서 제공합니다.
"""

from dataclasses import dataclass
from typing import Any


# ========================================
# Core Manager DTO들
# ========================================

@dataclass
class CoordinateDTO:
    """좌표 관련 데이터 전송 객체"""
    world_position: tuple[float, float]
    screen_position: tuple[float, float]
    transformer_type: str
    
    def __post_init__(self) -> None:
        """유효성 검증"""
        if not self.transformer_type:
            raise ValueError("transformer_type cannot be empty")


@dataclass
class DifficultyDTO:
    """난이도 관련 데이터 전송 객체"""
    current_level: str  # DifficultyLevel enum을 문자열로
    elapsed_time: float
    health_multiplier: float
    speed_multiplier: float
    spawn_rate_multiplier: float
    
    def __post_init__(self) -> None:
        """유효성 검증"""
        if self.elapsed_time < 0:
            raise ValueError("elapsed_time cannot be negative")
        if any(m <= 0 for m in [self.health_multiplier, self.speed_multiplier, self.spawn_rate_multiplier]):
            raise ValueError("Multipliers must be positive")


@dataclass
class GameStateDTO:
    """게임 상태 관련 데이터 전송 객체"""
    current_state: str  # GameState enum을 문자열로
    previous_state: str
    config_data: dict[str, Any]
    
    def __post_init__(self) -> None:
        """유효성 검증"""
        if not self.current_state:
            raise ValueError("current_state cannot be empty")


@dataclass
class TimeDTO:
    """시간 관리 관련 데이터 전송 객체"""
    delta_time: float
    total_time: float
    time_scale: float
    time_mode: str  # TimeMode enum을 문자열로
    
    def __post_init__(self) -> None:
        """유효성 검증"""
        if self.delta_time < 0 or self.time_scale <= 0:
            raise ValueError("Invalid time values")


# ========================================
# Domain Manager DTO들
# ========================================

@dataclass
class EntityDTO:
    """엔티티 데이터 전송 객체 (순수 데이터, 종속성 없음)"""
    entity_id: str
    active: bool
    components: dict[str, dict[str, Any]]
    
    def __post_init__(self) -> None:
        """유효성 검증"""
        if not self.entity_id:
            raise ValueError("entity_id cannot be empty")


@dataclass
class EnemyDTO:
    """적 엔티티 특화 데이터 전송 객체"""
    entity_id: str
    position: tuple[float, float]
    health: int
    max_health: int
    ai_type: str  # AIType enum을 문자열로
    movement_speed: float
    
    def __post_init__(self) -> None:
        """유효성 검증"""
        if self.health < 0 or self.max_health <= 0:
            raise ValueError("Invalid health values")
        if self.movement_speed < 0:
            raise ValueError("Movement speed cannot be negative")


@dataclass
class WeaponDTO:
    """무기 데이터 전송 객체 (다중 무기 지원)"""
    entity_id: str
    weapons: list[dict[str, Any]]  # 여러 무기 정보
    primary_weapon_index: int      # 주 무기 인덱스
    total_dps: float
    
    def __post_init__(self) -> None:
        """유효성 검증"""
        if not self.weapons:
            raise ValueError("At least one weapon required")
        if not (0 <= self.primary_weapon_index < len(self.weapons)):
            raise ValueError("Invalid primary weapon index")


@dataclass
class ProjectileDTO:
    """투사체 데이터 전송 객체"""
    entity_id: str
    owner_entity_id: str
    position: tuple[float, float]
    velocity: tuple[float, float]
    damage: int
    lifetime: float
    
    def __post_init__(self) -> None:
        """유효성 검증"""
        if not self.entity_id or not self.owner_entity_id:
            raise ValueError("entity_id and owner_entity_id cannot be empty")
        if self.damage < 0 or self.lifetime <= 0:
            raise ValueError("Invalid damage or lifetime values")