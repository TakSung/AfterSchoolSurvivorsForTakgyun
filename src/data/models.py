"""
Pydantic data models for game configuration and data validation.

This module defines the data models for items, enemies, bosses, and game
balance configuration using Pydantic for type safety and validation.
"""

from enum import IntEnum

from pydantic import BaseModel, ConfigDict, Field, field_validator


class WeaponType(IntEnum):
    """Types of weapons available in the game."""

    SOCCER_BALL = 0
    BASKETBALL = 1
    BASEBALL_BAT = 2

    @property
    def display_name(self) -> str:
        """Get the Korean display name for the weapon type."""
        display_names = {
            WeaponType.SOCCER_BALL: '축구공',
            WeaponType.BASKETBALL: '농구공',
            WeaponType.BASEBALL_BAT: '야구 배트',
        }
        return display_names[self]

    @property
    def damage_multiplier(self) -> float:
        """Get the damage multiplier for this weapon type."""
        damage_multipliers = [1.2, 1.0, 1.5]  # Index-based fast lookup
        return damage_multipliers[self.value]


class AbilityType(IntEnum):
    """Types of ability items available in the game."""

    SOCCER_SHOES = 0
    BASKETBALL_SHOES = 1
    RED_GINSENG = 2
    MILK = 3

    @property
    def display_name(self) -> str:
        """Get the Korean display name for the ability type."""
        display_names = {
            AbilityType.SOCCER_SHOES: '축구화',
            AbilityType.BASKETBALL_SHOES: '농구화',
            AbilityType.RED_GINSENG: '홍삼',
            AbilityType.MILK: '우유',
        }
        return display_names[self]


class EnemyType(IntEnum):
    """Types of enemies in the game."""

    KOREAN = 0  # 국어 선생님
    MATH = 1  # 수학 선생님
    PRINCIPAL = 2  # 교장 선생님 (보스)

    @property
    def display_name(self) -> str:
        """Get the Korean display name for the enemy type."""
        display_names = {
            EnemyType.KOREAN: '국어 선생님',
            EnemyType.MATH: '수학 선생님',
            EnemyType.PRINCIPAL: '교장 선생님',
        }
        return display_names[self]

    @property
    def is_boss(self) -> bool:
        """Check if this enemy type is a boss."""
        return self == EnemyType.PRINCIPAL


class WeaponData(BaseModel):
    """Data model for weapon items."""

    weapon_type: WeaponType
    name: str = Field(..., min_length=1, max_length=50)
    description: str = Field(default='', max_length=200)
    base_damage: int = Field(..., ge=1, le=1000)
    attack_speed: float = Field(..., gt=0.0, le=10.0)
    attack_range: float = Field(..., gt=0.0, le=500.0)
    projectile_speed: float = Field(default=300.0, gt=0.0, le=1000.0)
    max_level: int = Field(default=5, ge=1, le=10)

    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate weapon name."""
        if not v.strip():
            raise ValueError('무기 이름은 비워둘 수 없습니다')
        return v.strip()

    @field_validator('base_damage')
    @classmethod
    def validate_damage(cls, v: int) -> int:
        """Validate base damage value."""
        if v <= 0:
            raise ValueError('기본 데미지는 0보다 커야 합니다')
        return v


class AbilityData(BaseModel):
    """Data model for ability items."""

    ability_type: AbilityType
    name: str = Field(..., min_length=1, max_length=50)
    description: str = Field(default='', max_length=200)
    effect_type: str = Field(
        ..., min_length=1
    )  # e.g., 'speed_boost', 'health_boost'
    effect_value: float = Field(..., ge=0.0)
    max_level: int = Field(default=5, ge=1, le=10)

    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate ability name."""
        if not v.strip():
            raise ValueError('능력 이름은 비워둘 수 없습니다')
        return v.strip()

    @field_validator('effect_type')
    @classmethod
    def validate_effect_type(cls, v: str) -> str:
        """Validate effect type."""
        valid_effects = {
            'speed_boost',
            'health_boost',
            'damage_boost',
            'attack_speed_boost',
            'range_boost',
        }
        if v not in valid_effects:
            raise ValueError(f'유효하지 않은 효과 타입: {v}')
        return v


class SynergyData(BaseModel):
    """Data model for item synergy effects."""

    name: str = Field(..., min_length=1, max_length=50)
    description: str = Field(default='', max_length=200)
    required_items: list[str] = Field(..., min_length=2)
    effect_type: str = Field(..., min_length=1)
    effect_value: float = Field(..., ge=0.0)

    @field_validator('required_items')
    @classmethod
    def validate_required_items(cls, v: list[str]) -> list[str]:
        """Validate required items for synergy."""
        if len(v) < 2:
            raise ValueError('시너지에는 최소 2개의 아이템이 필요합니다')
        if len(set(v)) != len(v):
            raise ValueError('시너지 아이템 목록에 중복이 있습니다')
        return v


class EnemyData(BaseModel):
    """Data model for enemy configuration."""

    enemy_type: EnemyType
    name: str = Field(..., min_length=1, max_length=50)
    description: str = Field(default='', max_length=200)
    base_health: int = Field(..., ge=1, le=10000)
    base_speed: float = Field(..., gt=0.0, le=200.0)
    base_attack_power: int = Field(..., ge=0, le=1000)
    experience_reward: int = Field(default=10, ge=1, le=1000)
    spawn_weight: float = Field(default=1.0, gt=0.0, le=10.0)

    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate enemy name."""
        if not v.strip():
            raise ValueError('적 이름은 비워둘 수 없습니다')
        return v.strip()


class BossPhaseData(BaseModel):
    """Data model for boss phase configuration."""

    phase_number: int = Field(..., ge=1, le=10)
    health_threshold: float = Field(
        ..., ge=0.0, le=1.0
    )  # Percentage of health
    attack_pattern: str = Field(..., min_length=1)
    attack_power_multiplier: float = Field(default=1.0, gt=0.0, le=5.0)
    speed_multiplier: float = Field(default=1.0, gt=0.0, le=3.0)
    special_abilities: list[str] = Field(default_factory=list)

    @field_validator('health_threshold')
    @classmethod
    def validate_health_threshold(cls, v: float) -> float:
        """Validate health threshold percentage."""
        if not 0.0 <= v <= 1.0:
            raise ValueError('체력 임계값은 0.0과 1.0 사이여야 합니다')
        return v


class BossData(BaseModel):
    """Data model for boss configuration."""

    enemy_type: EnemyType
    name: str = Field(..., min_length=1, max_length=50)
    description: str = Field(default='', max_length=200)
    base_health: int = Field(..., ge=100, le=50000)
    base_speed: float = Field(..., gt=0.0, le=100.0)
    base_attack_power: int = Field(..., ge=10, le=5000)
    spawn_interval: float = Field(default=90.0, gt=0.0, le=600.0)  # seconds
    phases: list[BossPhaseData] = Field(default_factory=list)

    @field_validator('enemy_type')
    @classmethod
    def validate_boss_type(cls, v: EnemyType) -> EnemyType:
        """Validate that enemy type is actually a boss."""
        if not v.is_boss:
            raise ValueError('보스 데이터에는 보스 타입만 사용할 수 있습니다')
        return v

    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate boss name."""
        if not v.strip():
            raise ValueError('보스 이름은 비워둘 수 없습니다')
        return v.strip()


class PlayerBalanceData(BaseModel):
    """Data model for player balance configuration."""

    base_health: int = Field(default=100, ge=1, le=1000)
    base_speed: float = Field(default=200.0, gt=0.0, le=500.0)
    base_attack_power: int = Field(default=10, ge=1, le=100)
    level_up_experience: int = Field(default=100, ge=1, le=10000)
    experience_scaling: float = Field(default=1.2, gt=1.0, le=3.0)


class DifficultyBalanceData(BaseModel):
    """Data model for difficulty scaling configuration."""

    scaling_factor: float = Field(default=1.1, gt=1.0, le=2.0)
    boss_interval: float = Field(default=90.0, gt=10.0, le=600.0)  # seconds
    enemy_spawn_rate_increase: float = Field(default=0.1, ge=0.0, le=1.0)
    enemy_health_scaling: float = Field(default=1.05, gt=1.0, le=2.0)
    enemy_speed_scaling: float = Field(default=1.02, gt=1.0, le=2.0)
    max_enemies_on_screen: int = Field(default=50, ge=1, le=200)


class GameBalanceData(BaseModel):
    """Data model for overall game balance configuration."""

    player: PlayerBalanceData = Field(default_factory=PlayerBalanceData)
    difficulty: DifficultyBalanceData = Field(
        default_factory=DifficultyBalanceData
    )


class ItemsConfig(BaseModel):
    """Configuration model for all items data."""

    weapons: dict[str, WeaponData] = Field(default_factory=dict)
    abilities: dict[str, AbilityData] = Field(default_factory=dict)
    synergies: dict[str, SynergyData] = Field(default_factory=dict)

    @field_validator('weapons')
    @classmethod
    def validate_weapons(
        cls, v: dict[str, WeaponData]
    ) -> dict[str, WeaponData]:
        """Validate weapons dictionary."""
        if not v:
            raise ValueError('최소 하나의 무기가 정의되어야 합니다')
        return v


class EnemiesConfig(BaseModel):
    """Configuration model for enemies data."""

    basic_enemies: dict[str, EnemyData] = Field(default_factory=dict)
    elite_enemies: dict[str, EnemyData] = Field(default_factory=dict)

    @field_validator('basic_enemies')
    @classmethod
    def validate_basic_enemies(
        cls, v: dict[str, EnemyData]
    ) -> dict[str, EnemyData]:
        """Validate basic enemies dictionary."""
        if not v:
            raise ValueError('최소 하나의 기본 적이 정의되어야 합니다')
        return v


class BossesConfig(BaseModel):
    """Configuration model for bosses data."""

    bosses: dict[str, BossData] = Field(default_factory=dict)
    boss_phases: dict[str, list[BossPhaseData]] = Field(default_factory=dict)

    @field_validator('bosses')
    @classmethod
    def validate_bosses(cls, v: dict[str, BossData]) -> dict[str, BossData]:
        """Validate bosses dictionary."""
        if not v:
            raise ValueError('최소 하나의 보스가 정의되어야 합니다')
        return v


class GameConfig(BaseModel):
    """Root configuration model for all game data."""

    items: ItemsConfig = Field(default_factory=ItemsConfig)
    enemies: EnemiesConfig = Field(default_factory=EnemiesConfig)
    bosses: BossesConfig = Field(default_factory=BossesConfig)
    game_balance: GameBalanceData = Field(default_factory=GameBalanceData)

    model_config = ConfigDict(
        use_enum_values=True,
        validate_assignment=True,
        extra='forbid'  # 정의되지 않은 필드 금지
    )
