"""
Unit tests for Pydantic data models.

This module tests the validation logic, field constraints, and data integrity
of all Pydantic models defined in src/data/models.py.
"""

import pytest
from pydantic import ValidationError

from src.data.models import (
    AbilityData,
    AbilityType,
    BossData,
    BossesConfig,
    BossPhaseData,
    DifficultyBalanceData,
    EnemiesConfig,
    EnemyData,
    EnemyType,
    GameBalanceData,
    GameConfig,
    ItemsConfig,
    PlayerBalanceData,
    SynergyData,
    WeaponData,
    WeaponType,
)


class TestWeaponType:
    """Test cases for WeaponType enum."""

    def test_무기_타입_값_정확성_검증_성공_시나리오(self) -> None:
        """1. 무기 타입 enum 값들의 정확성 검증 (성공 시나리오)

        목적: 무기 타입 enum이 올바른 정수 값을 가지는지 검증
        테스트할 범위: WeaponType enum의 모든 값들
        커버하는 함수 및 데이터: enum 값들과 display_name, damage_multiplier
        기대되는 안정성: 일관된 무기 타입 데이터 보장
        """
        # Given & When & Then - enum 값 검증
        assert WeaponType.SOCCER_BALL == 0
        assert WeaponType.BASKETBALL == 1
        assert WeaponType.BASEBALL_BAT == 2

    def test_무기_타입_표시명_정확성_검증_성공_시나리오(self) -> None:
        """2. 무기 타입 한글 표시명 정확성 검증 (성공 시나리오)"""
        # Given & When & Then - 표시명 검증
        assert WeaponType.SOCCER_BALL.display_name == '축구공'
        assert WeaponType.BASKETBALL.display_name == '농구공'
        assert WeaponType.BASEBALL_BAT.display_name == '야구 배트'

    def test_무기_타입_데미지_배율_정확성_검증_성공_시나리오(self) -> None:
        """3. 무기 타입별 데미지 배율 정확성 검증 (성공 시나리오)"""
        # Given & When & Then - 데미지 배율 검증
        assert WeaponType.SOCCER_BALL.damage_multiplier == 1.2
        assert WeaponType.BASKETBALL.damage_multiplier == 1.0
        assert WeaponType.BASEBALL_BAT.damage_multiplier == 1.5


class TestAbilityType:
    """Test cases for AbilityType enum."""

    def test_능력_타입_값_및_표시명_정확성_검증_성공_시나리오(self) -> None:
        """4. 능력 타입 enum 값과 표시명 정확성 검증 (성공 시나리오)"""
        # Given & When & Then - enum 값 검증
        assert AbilityType.SOCCER_SHOES == 0
        assert AbilityType.BASKETBALL_SHOES == 1
        assert AbilityType.RED_GINSENG == 2
        assert AbilityType.MILK == 3

        # 표시명 검증
        assert AbilityType.SOCCER_SHOES.display_name == '축구화'
        assert AbilityType.BASKETBALL_SHOES.display_name == '농구화'
        assert AbilityType.RED_GINSENG.display_name == '홍삼'
        assert AbilityType.MILK.display_name == '우유'


class TestEnemyType:
    """Test cases for EnemyType enum."""

    def test_적_타입_기본_속성_정확성_검증_성공_시나리오(self) -> None:
        """5. 적 타입별 기본 속성값 정확성 검증 (성공 시나리오)"""
        # Given & When & Then - 국어 선생님
        korean = EnemyType.KOREAN
        assert korean.display_name == '국어 선생님'
        assert not korean.is_boss

        # 수학 선생님
        math = EnemyType.MATH
        assert math.display_name == '수학 선생님'
        assert not math.is_boss

        # 교장 선생님 (보스)
        principal = EnemyType.PRINCIPAL
        assert principal.display_name == '교장 선생님'
        assert principal.is_boss


class TestWeaponData:
    """Test cases for WeaponData model."""

    def test_무기_데이터_정상_생성_검증_성공_시나리오(self) -> None:
        """6. 무기 데이터 모델 정상 생성 검증 (성공 시나리오)"""
        # Given & When
        weapon = WeaponData(
            weapon_type=WeaponType.SOCCER_BALL,
            name='축구공',
            description='축구에 사용하는 공',
            base_damage=15,
            attack_speed=1.5,
            attack_range=200.0,
            projectile_speed=350.0,
            max_level=5,
        )

        # Then
        assert weapon.weapon_type == WeaponType.SOCCER_BALL
        assert weapon.name == '축구공'
        assert weapon.base_damage == 15
        assert weapon.attack_speed == 1.5

    def test_무기_이름_유효성_검증_실패_시나리오(self) -> None:
        """7. 무기 이름 유효성 검증 실패 시나리오"""
        # Given & When & Then - 빈 이름
        with pytest.raises(ValidationError) as exc_info:
            WeaponData(
                weapon_type=WeaponType.SOCCER_BALL,
                name='',
                base_damage=15,
                attack_speed=1.5,
                attack_range=200.0,
            )
        assert 'String should have at least 1 character' in str(exc_info.value)

        # 공백만 있는 이름
        with pytest.raises(ValidationError) as exc_info:
            WeaponData(
                weapon_type=WeaponType.SOCCER_BALL,
                name='   ',
                base_damage=15,
                attack_speed=1.5,
                attack_range=200.0,
            )
        assert '무기 이름은 비워둘 수 없습니다' in str(exc_info.value)

    def test_무기_데미지_범위_검증_실패_시나리오(self) -> None:
        """8. 무기 데미지 범위 검증 실패 시나리오"""
        # Given & When & Then - 음수 데미지
        with pytest.raises(ValidationError) as exc_info:
            WeaponData(
                weapon_type=WeaponType.SOCCER_BALL,
                name='축구공',
                base_damage=-5,
                attack_speed=1.5,
                attack_range=200.0,
            )
        assert 'Input should be greater than or equal to 1' in str(
            exc_info.value
        )

        # 0 데미지
        with pytest.raises(ValidationError) as exc_info:
            WeaponData(
                weapon_type=WeaponType.SOCCER_BALL,
                name='축구공',
                base_damage=0,
                attack_speed=1.5,
                attack_range=200.0,
            )
        assert 'Input should be greater than or equal to 1' in str(
            exc_info.value
        )


class TestAbilityData:
    """Test cases for AbilityData model."""

    def test_능력_데이터_정상_생성_검증_성공_시나리오(self) -> None:
        """9. 능력 데이터 모델 정상 생성 검증 (성공 시나리오)"""
        # Given & When
        ability = AbilityData(
            ability_type=AbilityType.SOCCER_SHOES,
            name='축구화',
            description='이동 속도를 증가시킨다',
            effect_type='speed_boost',
            effect_value=0.2,
            max_level=3,
        )

        # Then
        assert ability.ability_type == AbilityType.SOCCER_SHOES
        assert ability.name == '축구화'
        assert ability.effect_type == 'speed_boost'
        assert ability.effect_value == 0.2

    def test_능력_효과_타입_유효성_검증_실패_시나리오(self) -> None:
        """10. 능력 효과 타입 유효성 검증 실패 시나리오"""
        # Given & When & Then - 유효하지 않은 효과 타입
        with pytest.raises(ValidationError) as exc_info:
            AbilityData(
                ability_type=AbilityType.SOCCER_SHOES,
                name='축구화',
                effect_type='invalid_boost',
                effect_value=0.2,
            )
        assert '유효하지 않은 효과 타입: invalid_boost' in str(exc_info.value)

    def test_능력_이름_공백_제거_검증_성공_시나리오(self) -> None:
        """11. 능력 이름 공백 제거 검증 (성공 시나리오)"""
        # Given & When
        ability = AbilityData(
            ability_type=AbilityType.SOCCER_SHOES,
            name='  축구화  ',
            effect_type='speed_boost',
            effect_value=0.2,
        )

        # Then
        assert ability.name == '축구화'


class TestSynergyData:
    """Test cases for SynergyData model."""

    def test_시너지_데이터_정상_생성_검증_성공_시나리오(self) -> None:
        """12. 시너지 데이터 모델 정상 생성 검증 (성공 시나리오)"""
        # Given & When
        synergy = SynergyData(
            name='축구 시너지',
            description='축구공과 축구화의 시너지',
            required_items=['축구공', '축구화'],
            effect_type='damage_boost',
            effect_value=0.15,
        )

        # Then
        assert synergy.name == '축구 시너지'
        assert len(synergy.required_items) == 2
        assert '축구공' in synergy.required_items
        assert '축구화' in synergy.required_items

    def test_시너지_필수_아이템_개수_검증_실패_시나리오(self) -> None:
        """13. 시너지 필수 아이템 개수 검증 실패 시나리오"""
        # Given & When & Then - 1개 아이템만으로 시너지 시도
        with pytest.raises(ValidationError) as exc_info:
            SynergyData(
                name='무효한 시너지',
                required_items=['축구공'],
                effect_type='damage_boost',
                effect_value=0.15,
            )
        assert 'List should have at least 2 items' in str(exc_info.value)

    def test_시너지_아이템_중복_검증_실패_시나리오(self) -> None:
        """14. 시너지 아이템 중복 검증 실패 시나리오"""
        # Given & When & Then - 중복 아이템으로 시너지 시도
        with pytest.raises(ValidationError) as exc_info:
            SynergyData(
                name='중복 시너지',
                required_items=['축구공', '축구공'],
                effect_type='damage_boost',
                effect_value=0.15,
            )
        assert '시너지 아이템 목록에 중복이 있습니다' in str(exc_info.value)


class TestEnemyData:
    """Test cases for EnemyData model."""

    def test_적_데이터_정상_생성_검증_성공_시나리오(self) -> None:
        """15. 적 데이터 모델 정상 생성 검증 (성공 시나리오)"""
        # Given & When
        enemy = EnemyData(
            enemy_type=EnemyType.KOREAN,
            name='국어 선생님',
            description='국어 과목을 가르치는 선생님',
            base_health=50,
            base_speed=30.0,
            base_attack_power=25,
            experience_reward=15,
            spawn_weight=1.0,
        )

        # Then
        assert enemy.enemy_type == EnemyType.KOREAN
        assert enemy.name == '국어 선생님'
        assert enemy.base_health == 50
        assert enemy.experience_reward == 15

    def test_적_이름_공백_제거_검증_성공_시나리오(self) -> None:
        """16. 적 이름 공백 제거 검증 (성공 시나리오)"""
        # Given & When
        enemy = EnemyData(
            enemy_type=EnemyType.MATH,
            name='  수학 선생님  ',
            base_health=30,
            base_speed=80.0,
            base_attack_power=15,
        )

        # Then
        assert enemy.name == '수학 선생님'


class TestBossPhaseData:
    """Test cases for BossPhaseData model."""

    def test_보스_페이즈_정상_생성_검증_성공_시나리오(self) -> None:
        """17. 보스 페이즈 데이터 정상 생성 검증 (성공 시나리오)"""
        # Given & When
        phase = BossPhaseData(
            phase_number=1,
            health_threshold=0.8,
            attack_pattern='훈화 말씀',
            attack_power_multiplier=1.2,
            speed_multiplier=1.1,
            special_abilities=['스턴', '디버프'],
        )

        # Then
        assert phase.phase_number == 1
        assert phase.health_threshold == 0.8
        assert phase.attack_pattern == '훈화 말씀'
        assert '스턴' in phase.special_abilities

    def test_보스_체력_임계값_범위_검증_실패_시나리오(self) -> None:
        """18. 보스 체력 임계값 범위 검증 실패 시나리오"""
        # Given & When & Then - 1.0 초과
        with pytest.raises(ValidationError) as exc_info:
            BossPhaseData(
                phase_number=1,
                health_threshold=1.5,
                attack_pattern='훈화 말씀',
            )
        assert 'Input should be less than or equal to 1' in str(exc_info.value)

        # 0.0 미만
        with pytest.raises(ValidationError) as exc_info:
            BossPhaseData(
                phase_number=1,
                health_threshold=-0.1,
                attack_pattern='훈화 말씀',
            )
        assert 'Input should be greater than or equal to 0' in str(
            exc_info.value
        )


class TestBossData:
    """Test cases for BossData model."""

    def test_보스_데이터_정상_생성_검증_성공_시나리오(self) -> None:
        """19. 보스 데이터 정상 생성 검증 (성공 시나리오)"""
        # Given & When
        boss = BossData(
            enemy_type=EnemyType.PRINCIPAL,
            name='교장 선생님',
            description='학교의 최고 권력자',
            base_health=500,
            base_speed=50.0,
            base_attack_power=100,
            spawn_interval=90.0,
        )

        # Then
        assert boss.enemy_type == EnemyType.PRINCIPAL
        assert boss.name == '교장 선생님'
        assert boss.base_health == 500
        assert boss.spawn_interval == 90.0

    def test_보스_타입_유효성_검증_실패_시나리오(self) -> None:
        """20. 보스 타입 유효성 검증 실패 시나리오"""
        # Given & When & Then - 보스가 아닌 타입으로 보스 데이터 생성 시도
        with pytest.raises(ValidationError) as exc_info:
            BossData(
                enemy_type=EnemyType.KOREAN,  # 보스가 아님
                name='가짜 보스',
                base_health=500,
                base_speed=50.0,
                base_attack_power=100,
            )
        assert '보스 데이터에는 보스 타입만 사용할 수 있습니다' in str(
            exc_info.value
        )


class TestGameBalanceData:
    """Test cases for game balance data models."""

    def test_플레이어_밸런스_기본값_검증_성공_시나리오(self) -> None:
        """21. 플레이어 밸런스 기본값 검증 (성공 시나리오)"""
        # Given & When
        player_balance = PlayerBalanceData()

        # Then
        assert player_balance.base_health == 100
        assert player_balance.base_speed == 200.0
        assert player_balance.base_attack_power == 10
        assert player_balance.level_up_experience == 100
        assert player_balance.experience_scaling == 1.2

    def test_난이도_밸런스_기본값_검증_성공_시나리오(self) -> None:
        """22. 난이도 밸런스 기본값 검증 (성공 시나리오)"""
        # Given & When
        difficulty_balance = DifficultyBalanceData()

        # Then
        assert difficulty_balance.scaling_factor == 1.1
        assert difficulty_balance.boss_interval == 90.0
        assert difficulty_balance.enemy_spawn_rate_increase == 0.1
        assert difficulty_balance.max_enemies_on_screen == 50

    def test_게임_밸런스_통합_검증_성공_시나리오(self) -> None:
        """23. 게임 밸런스 통합 검증 (성공 시나리오)"""
        # Given & When
        game_balance = GameBalanceData()

        # Then
        assert isinstance(game_balance.player, PlayerBalanceData)
        assert isinstance(game_balance.difficulty, DifficultyBalanceData)
        assert game_balance.player.base_health == 100
        assert game_balance.difficulty.boss_interval == 90.0


class TestConfigModels:
    """Test cases for configuration models."""

    def test_아이템_설정_무기_유효성_검증_실패_시나리오(self) -> None:
        """24. 아이템 설정 무기 유효성 검증 실패 시나리오"""
        # Given & When & Then - 빈 무기 딕셔너리
        with pytest.raises(ValidationError) as exc_info:
            ItemsConfig(weapons={})
        assert '최소 하나의 무기가 정의되어야 합니다' in str(exc_info.value)

    def test_적_설정_기본적_유효성_검증_실패_시나리오(self) -> None:
        """25. 적 설정 기본적 유효성 검증 실패 시나리오"""
        # Given & When & Then - 빈 기본 적 딕셔너리
        with pytest.raises(ValidationError) as exc_info:
            EnemiesConfig(basic_enemies={})
        assert '최소 하나의 기본 적이 정의되어야 합니다' in str(exc_info.value)

    def test_보스_설정_유효성_검증_실패_시나리오(self) -> None:
        """26. 보스 설정 유효성 검증 실패 시나리오"""
        # Given & When & Then - 빈 보스 딕셔너리
        with pytest.raises(ValidationError) as exc_info:
            BossesConfig(bosses={})
        assert '최소 하나의 보스가 정의되어야 합니다' in str(exc_info.value)

    def test_게임_설정_통합_기본값_검증_성공_시나리오(self) -> None:
        """27. 게임 설정 통합 기본값 검증 (성공 시나리오)"""
        # Given & When
        game_config = GameConfig()

        # Then
        assert isinstance(game_config.items, ItemsConfig)
        assert isinstance(game_config.enemies, EnemiesConfig)
        assert isinstance(game_config.bosses, BossesConfig)
        assert isinstance(game_config.game_balance, GameBalanceData)

    def test_게임_설정_추가_필드_금지_검증_실패_시나리오(self) -> None:
        """28. 게임 설정 추가 필드 금지 검증 실패 시나리오"""
        # Given & When & Then - 정의되지 않은 필드 추가 시도
        with pytest.raises(ValidationError):
            GameConfig(unknown_field='value')


class TestDataIntegration:
    """Integration tests for data models."""

    def test_무기_데이터_완전한_설정_생성_검증_성공_시나리오(self) -> None:
        """29. 무기 데이터 완전한 설정 생성 검증 (성공 시나리오)"""
        # Given & When
        soccer_ball = WeaponData(
            weapon_type=WeaponType.SOCCER_BALL,
            name='축구공',
            description='가장 기본적인 무기',
            base_damage=10,
            attack_speed=1.2,
            attack_range=180.0,
            projectile_speed=320.0,
            max_level=5,
        )

        basketball = WeaponData(
            weapon_type=WeaponType.BASKETBALL,
            name='농구공',
            description='균형잡힌 무기',
            base_damage=12,
            attack_speed=1.0,
            attack_range=200.0,
            projectile_speed=300.0,
            max_level=5,
        )

        items_config = ItemsConfig(
            weapons={'soccer_ball': soccer_ball, 'basketball': basketball},
            abilities={},
            synergies={},
        )

        # Then
        assert len(items_config.weapons) == 2
        assert 'soccer_ball' in items_config.weapons
        assert (
            items_config.weapons['soccer_ball'].weapon_type
            == WeaponType.SOCCER_BALL
        )

    def test_전체_게임_데이터_통합_검증_성공_시나리오(self) -> None:
        """30. 전체 게임 데이터 통합 검증 (성공 시나리오)"""
        # Given
        weapon = WeaponData(
            weapon_type=WeaponType.SOCCER_BALL,
            name='축구공',
            base_damage=10,
            attack_speed=1.2,
            attack_range=180.0,
        )

        enemy = EnemyData(
            enemy_type=EnemyType.KOREAN,
            name='국어 선생님',
            base_health=50,
            base_speed=30.0,
            base_attack_power=25,
        )

        boss = BossData(
            enemy_type=EnemyType.PRINCIPAL,
            name='교장 선생님',
            base_health=500,
            base_speed=50.0,
            base_attack_power=100,
        )

        # When
        game_config = GameConfig(
            items=ItemsConfig(weapons={'soccer_ball': weapon}),
            enemies=EnemiesConfig(basic_enemies={'korean_teacher': enemy}),
            bosses=BossesConfig(bosses={'principal': boss}),
        )

        # Then
        assert len(game_config.items.weapons) == 1
        assert len(game_config.enemies.basic_enemies) == 1
        assert len(game_config.bosses.bosses) == 1
        assert game_config.items.weapons['soccer_ball'].name == '축구공'
        assert (
            game_config.enemies.basic_enemies['korean_teacher'].name
            == '국어 선생님'
        )
        assert game_config.bosses.bosses['principal'].name == '교장 선생님'
