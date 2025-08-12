"""
Tests for WeaponComponent class.

무기 컴포넌트의 데이터 구조, 유효성 검사, 쿨다운 계산,
데미지 계산 등 핵심 기능을 검증하는 테스트 모음입니다.
"""

from src.components.weapon_component import (
    ProjectileType,
    WeaponComponent,
    WeaponType,
)


class TestWeaponComponent:
    """WeaponComponent에 대한 테스트 클래스"""

    def test_무기_컴포넌트_기본_초기화_검증_성공_시나리오(self) -> None:
        """1. 무기 컴포넌트 기본 값으로 초기화 검증 (성공 시나리오)

        목적: WeaponComponent가 올바른 기본값으로 초기화되는지 검증
        테스트할 범위: 기본값 설정, 타입 검증, 데이터 일관성
        커버하는 함수 및 데이터: __init__, 모든 기본 필드값
        기대되는 안정성: 기본값으로 안정적인 초기화 보장
        """
        # Given & When - 기본값으로 무기 컴포넌트 생성
        weapon = WeaponComponent()

        # Then - 기본값 확인
        assert weapon.weapon_type == WeaponType.SOCCER_BALL, (
            'weapon_type 기본값이 SOCCER_BALL이어야 함'
        )
        assert weapon.projectile_type == ProjectileType.BASIC, (
            'projectile_type 기본값이 BASIC이어야 함'
        )
        assert weapon.attack_speed == 1.0, 'attack_speed 기본값이 1.0이어야 함'
        assert weapon.range == 200.0, 'range 기본값이 200.0이어야 함'
        assert weapon.damage == 10, 'damage 기본값이 10이어야 함'
        assert weapon.last_attack_time == 0.0, (
            'last_attack_time 기본값이 0.0이어야 함'
        )
        assert weapon.current_target_id is None, (
            'current_target_id 기본값이 None이어야 함'
        )

    def test_무기_컴포넌트_커스텀_초기화_검증_성공_시나리오(self) -> None:
        """2. 무기 컴포넌트 커스텀 값으로 초기화 검증 (성공 시나리오)

        목적: WeaponComponent가 커스텀 값으로 올바르게 초기화되는지 검증
        테스트할 범위: 커스텀 값 설정, 타입 검증, 데이터 일관성
        커버하는 함수 및 데이터: __init__ with custom values
        기대되는 안정성: 커스텀 값으로 안정적인 초기화 보장
        """
        # Given - 커스텀 값 설정
        weapon_type = WeaponType.BASEBALL_BAT
        attack_speed = 2.5
        weapon_range = 150.0
        damage = 25
        target_id = 42

        # When - 커스텀 값으로 무기 컴포넌트 생성
        weapon = WeaponComponent(
            weapon_type=weapon_type,
            attack_speed=attack_speed,
            range=weapon_range,
            damage=damage,
            current_target_id=target_id,
        )

        # Then - 커스텀 값 확인
        assert weapon.weapon_type == weapon_type, (
            '설정한 weapon_type과 일치해야 함'
        )
        assert weapon.attack_speed == attack_speed, (
            '설정한 attack_speed와 일치해야 함'
        )
        assert weapon.range == weapon_range, '설정한 range와 일치해야 함'
        assert weapon.damage == damage, '설정한 damage와 일치해야 함'
        assert weapon.current_target_id == target_id, (
            '설정한 target_id와 일치해야 함'
        )

    def test_무기_컴포넌트_유효성_검사_성공_시나리오(self) -> None:
        """3. 무기 컴포넌트 유효성 검사 통과 (성공 시나리오)

        목적: 올바른 데이터로 구성된 WeaponComponent의 유효성 검사 통과 확인
        테스트할 범위: validate() 메서드의 정상 동작
        커버하는 함수 및 데이터: validate()
        기대되는 안정성: 유효한 데이터에 대해 True 반환
        """
        # Given - 유효한 무기 컴포넌트 생성
        weapon = WeaponComponent(attack_speed=1.5, range=300.0, damage=20)

        # When - 유효성 검사 수행
        is_valid = weapon.validate()

        # Then - 유효성 검사 통과 확인
        assert is_valid is True, '유효한 무기 컴포넌트는 검증을 통과해야 함'

    def test_무기_컴포넌트_유효성_검사_실패_시나리오(self) -> None:
        """4. 무기 컴포넌트 유효성 검사 실패 (실패 시나리오)

        목적: 잘못된 데이터로 구성된 WeaponComponent의 유효성 검사 실패 확인
        테스트할 범위: validate() 메서드의 예외 케이스 처리
        커버하는 함수 및 데이터: validate()
        기대되는 안정성: 잘못된 데이터에 대해 False 반환
        """
        # Test cases for invalid data
        invalid_cases = [
            # attack_speed가 0 이하인 경우
            WeaponComponent(attack_speed=0.0, range=100.0, damage=10),
            WeaponComponent(attack_speed=-1.0, range=100.0, damage=10),
            # range가 0 이하인 경우
            WeaponComponent(attack_speed=1.0, range=0.0, damage=10),
            WeaponComponent(attack_speed=1.0, range=-50.0, damage=10),
            # damage가 0 이하인 경우
            WeaponComponent(attack_speed=1.0, range=100.0, damage=0),
            WeaponComponent(attack_speed=1.0, range=100.0, damage=-5),
            # last_attack_time이 음수인 경우
            WeaponComponent(
                attack_speed=1.0, range=100.0, damage=10, last_attack_time=-1.0
            ),
        ]

        for invalid_weapon in invalid_cases:
            # When - 유효성 검사 수행
            is_valid = invalid_weapon.validate()

            # Then - 유효성 검사 실패 확인
            assert is_valid is False, (
                f'잘못된 무기 데이터는 검증에 실패해야 함: {invalid_weapon}'
            )

    def test_쿨다운_지속시간_계산_정확성_검증_성공_시나리오(self) -> None:
        """5. 쿨다운 지속시간 계산 정확성 검증 (성공 시나리오)

        목적: 공격 속도에 따른 쿨다운 지속시간 계산 정확성 확인
        테스트할 범위: get_cooldown_duration() 메서드
        커버하는 함수 및 데이터: get_cooldown_duration()
        기대되는 안정성: 공격 속도 역수로 정확한 쿨다운 계산
        """
        test_cases = [
            (1.0, 1.0),  # 1초당 1회 공격 → 1초 쿨다운
            (2.0, 0.5),  # 1초당 2회 공격 → 0.5초 쿨다운
            (0.5, 2.0),  # 1초당 0.5회 공격 → 2초 쿨다운
            (4.0, 0.25),  # 1초당 4회 공격 → 0.25초 쿨다운
        ]

        for attack_speed, expected_cooldown in test_cases:
            # Given - 공격 속도 설정된 무기 컴포넌트
            weapon = WeaponComponent(attack_speed=attack_speed)

            # When - 쿨다운 지속시간 계산
            actual_cooldown = weapon.get_cooldown_duration()

            # Then - 계산 결과 확인
            assert abs(actual_cooldown - expected_cooldown) < 0.001, (
                f'공격속도 {attack_speed}에 대한 쿨다운이 {expected_cooldown}이어야 함, '
                f'실제: {actual_cooldown}'
            )

    def test_공격_가능_여부_판단_정확성_검증_성공_시나리오(self) -> None:
        """6. 공격 가능 여부 판단 정확성 검증 (성공 시나리오)

        목적: 현재 시간과 마지막 공격 시간을 기반으로 한 공격 가능 여부 판단 정확성 확인
        테스트할 범위: can_attack() 메서드
        커버하는 함수 및 데이터: can_attack()
        기대되는 안정성: 쿨다운 시간 경과 시 공격 가능 판단
        """
        # Given - 공격속도 2.0 (0.5초 쿨다운)인 무기
        weapon = WeaponComponent(attack_speed=2.0, last_attack_time=0.0)

        # Test case 1: 쿨다운이 완료되지 않은 경우
        current_time = 0.3  # 0.3초 경과 (0.5초 쿨다운 미완료)
        # When & Then
        assert weapon.can_attack(current_time) is False, (
            '쿨다운이 완료되지 않은 상태에서는 공격할 수 없어야 함'
        )

        # Test case 2: 쿨다운이 정확히 완료된 경우
        current_time = 0.5  # 정확히 0.5초 경과
        # When & Then
        assert weapon.can_attack(current_time) is True, (
            '쿨다운이 완료된 상태에서는 공격할 수 있어야 함'
        )

        # Test case 3: 쿨다운을 초과한 경우
        current_time = 1.0  # 1.0초 경과 (쿨다운 초과)
        # When & Then
        assert weapon.can_attack(current_time) is True, (
            '쿨다운을 초과한 상태에서는 공격할 수 있어야 함'
        )

    def test_마지막_공격_시간_업데이트_정확성_검증_성공_시나리오(self) -> None:
        """7. 마지막 공격 시간 업데이트 정확성 검증 (성공 시나리오)

        목적: set_last_attack_time() 메서드의 정확한 시간 업데이트 확인
        테스트할 범위: set_last_attack_time() 메서드
        커버하는 함수 및 데이터: set_last_attack_time()
        기대되는 안정성: 지정한 시간으로 정확한 업데이트
        """
        # Given - 기본 무기 컴포넌트
        weapon = WeaponComponent()
        assert weapon.last_attack_time == 0.0, '초기 공격 시간이 0.0이어야 함'

        # When - 마지막 공격 시간 업데이트
        new_attack_time = 5.5
        weapon.set_last_attack_time(new_attack_time)

        # Then - 업데이트된 시간 확인
        assert weapon.last_attack_time == new_attack_time, (
            f'마지막 공격 시간이 {new_attack_time}으로 업데이트되어야 함'
        )

    def test_효과적_데미지_계산_정확성_검증_성공_시나리오(self) -> None:
        """8. 효과적 데미지 계산 정확성 검증 (성공 시나리오)

        목적: 무기 타입별 데미지 배율이 적용된 효과적 데미지 계산 정확성 확인
        테스트할 범위: get_effective_damage() 메서드와 무기 타입별 배율
        커버하는 함수 및 데이터: get_effective_damage(), WeaponType.damage_multiplier
        기대되는 안정성: 무기 타입별 정확한 데미지 배율 적용
        """
        base_damage = 100

        test_cases = [
            (WeaponType.SOCCER_BALL, 1.2, 120),  # 축구공: 1.2배
            (WeaponType.BASKETBALL, 1.0, 100),  # 농구공: 1.0배
            (WeaponType.BASEBALL_BAT, 1.5, 150),  # 야구 배트: 1.5배
        ]

        for weapon_type, expected_multiplier, expected_damage in test_cases:
            # Given - 특정 무기 타입과 기본 데미지를 가진 무기
            weapon = WeaponComponent(
                weapon_type=weapon_type, damage=base_damage
            )

            # When - 효과적 데미지 계산
            effective_damage = weapon.get_effective_damage()

            # Then - 계산 결과 확인
            assert effective_damage == expected_damage, (
                f'{weapon_type.display_name}의 효과적 데미지가 {expected_damage}이어야 함, '
                f'실제: {effective_damage}'
            )

            # 무기 타입의 배율도 함께 확인
            assert weapon_type.damage_multiplier == expected_multiplier, (
                f'{weapon_type.display_name}의 데미지 배율이 {expected_multiplier}이어야 함'
            )


class TestWeaponType:
    """WeaponType 열거형에 대한 테스트 클래스"""

    def test_무기_타입_표시명_정확성_검증_성공_시나리오(self) -> None:
        """9. 무기 타입 표시명 정확성 검증 (성공 시나리오)

        목적: 각 무기 타입의 한국어 표시명이 올바르게 설정되어 있는지 확인
        테스트할 범위: WeaponType.display_name 속성
        커버하는 함수 및 데이터: WeaponType.display_name
        기대되는 안정성: 정확한 한국어 표시명 제공
        """
        expected_names = {
            WeaponType.SOCCER_BALL: '축구공',
            WeaponType.BASKETBALL: '농구공',
            WeaponType.BASEBALL_BAT: '야구 배트',
        }

        for weapon_type, expected_name in expected_names.items():
            # When & Then - 표시명 확인
            assert weapon_type.display_name == expected_name, (
                f'{weapon_type}의 표시명이 "{expected_name}"이어야 함, '
                f'실제: "{weapon_type.display_name}"'
            )

    def test_무기_타입_데미지_배율_정확성_검증_성공_시나리오(self) -> None:
        """10. 무기 타입 데미지 배율 정확성 검증 (성공 시나리오)

        목적: 각 무기 타입의 데미지 배율이 게임 기획에 맞게 설정되어 있는지 확인
        테스트할 범위: WeaponType.damage_multiplier 속성
        커버하는 함수 및 데이터: WeaponType.damage_multiplier
        기대되는 안정성: 게임 밸런스에 맞는 정확한 배율 제공
        """
        expected_multipliers = {
            WeaponType.SOCCER_BALL: 1.2,
            WeaponType.BASKETBALL: 1.0,
            WeaponType.BASEBALL_BAT: 1.5,
        }

        for weapon_type, expected_multiplier in expected_multipliers.items():
            # When & Then - 데미지 배율 확인
            assert weapon_type.damage_multiplier == expected_multiplier, (
                f'{weapon_type.display_name}의 데미지 배율이 {expected_multiplier}이어야 함, '
                f'실제: {weapon_type.damage_multiplier}'
            )


class TestProjectileType:
    """ProjectileType 열거형에 대한 테스트 클래스"""

    def test_투사체_타입_표시명_정확성_검증_성공_시나리오(self) -> None:
        """11. 투사체 타입 표시명 정확성 검증 (성공 시나리오)

        목적: 각 투사체 타입의 한국어 표시명이 올바르게 설정되어 있는지 확인
        테스트할 범위: ProjectileType.display_name 속성
        커버하는 함수 및 데이터: ProjectileType.display_name
        기대되는 안정성: 정확한 한국어 표시명 제공
        """
        expected_names = {ProjectileType.BASIC: '기본'}

        for projectile_type, expected_name in expected_names.items():
            # When & Then - 표시명 확인
            assert projectile_type.display_name == expected_name, (
                f'{projectile_type}의 표시명이 "{expected_name}"이어야 함, '
                f'실제: "{projectile_type.display_name}"'
            )
