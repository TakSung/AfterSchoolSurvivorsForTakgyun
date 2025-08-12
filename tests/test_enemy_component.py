"""
Unit tests for EnemyComponent.

Tests the enemy identification and property management system
following the game design document specifications.
"""

from src.components.enemy_component import EnemyComponent, EnemyType


class TestEnemyType:
    """Test cases for EnemyType enumeration."""

    def test_적_타입_표시명_정확성_검증_성공_시나리오(self) -> None:
        """1. 적 타입 표시명 정확성 검증 (성공 시나리오)

        목적: EnemyType 열거형의 한국어 표시명 정확성 검증
        테스트할 범위: display_name 속성
        커버하는 함수 및 데이터: display_name property
        기대되는 안정성: 기획서에 명시된 적 이름과 일치
        """
        # Given - 각 적 타입
        korean_teacher = EnemyType.KOREAN
        math_teacher = EnemyType.MATH
        principal = EnemyType.PRINCIPAL

        # When - 표시명 조회
        korean_name = korean_teacher.display_name
        math_name = math_teacher.display_name
        principal_name = principal.display_name

        # Then - 기획서에 따른 정확한 이름 반환 확인
        assert korean_name == '국어 선생님', '국어 선생님 표시명이 정확해야 함'
        assert math_name == '수학 선생님', '수학 선생님 표시명이 정확해야 함'
        assert principal_name == '교장 선생님', (
            '교장 선생님 표시명이 정확해야 함'
        )

    def test_적_타입_기본_체력_정확성_검증_성공_시나리오(self) -> None:
        """2. 적 타입 기본 체력 정확성 검증 (성공 시나리오)

        목적: EnemyType별 기본 체력값 정확성 검증
        테스트할 범위: base_health 속성
        커버하는 함수 및 데이터: base_health property
        기대되는 안정성: 각 적 타입별 설정된 기본 체력값 반환
        """
        # Given - 각 적 타입
        korean_teacher = EnemyType.KOREAN
        math_teacher = EnemyType.MATH
        principal = EnemyType.PRINCIPAL

        # When - 기본 체력 조회
        korean_health = korean_teacher.base_health
        math_health = math_teacher.base_health
        principal_health = principal.base_health

        # Then - 설정된 기본 체력값 반환 확인
        assert korean_health == 50, '국어 선생님 기본 체력이 50이어야 함'
        assert math_health == 30, '수학 선생님 기본 체력이 30이어야 함'
        assert principal_health == 200, '교장 선생님 기본 체력이 200이어야 함'

    def test_적_타입_기본_속도_정확성_검증_성공_시나리오(self) -> None:
        """3. 적 타입 기본 속도 정확성 검증 (성공 시나리오)

        목적: EnemyType별 기본 이동 속도값 정확성 검증
        테스트할 범위: base_speed 속성
        커버하는 함수 및 데이터: base_speed property
        기대되는 안정성: 각 적 타입별 설정된 기본 속도값 반환
        """
        # Given - 각 적 타입
        korean_teacher = EnemyType.KOREAN
        math_teacher = EnemyType.MATH
        principal = EnemyType.PRINCIPAL

        # When - 기본 속도 조회
        korean_speed = korean_teacher.base_speed
        math_speed = math_teacher.base_speed
        principal_speed = principal.base_speed

        # Then - 설정된 기본 속도값 반환 확인
        assert korean_speed == 30.0, '국어 선생님 기본 속도가 30.0이어야 함'
        assert math_speed == 80.0, '수학 선생님 기본 속도가 80.0이어야 함'
        assert principal_speed == 50.0, '교장 선생님 기본 속도가 50.0이어야 함'

    def test_적_타입_기본_공격력_정확성_검증_성공_시나리오(self) -> None:
        """4. 적 타입 기본 공격력 정확성 검증 (성공 시나리오)

        목적: EnemyType별 기본 공격력값 정확성 검증
        테스트할 범위: base_attack_power 속성
        커버하는 함수 및 데이터: base_attack_power property
        기대되는 안정성: 각 적 타입별 설정된 기본 공격력값 반환
        """
        # Given - 각 적 타입
        korean_teacher = EnemyType.KOREAN
        math_teacher = EnemyType.MATH
        principal = EnemyType.PRINCIPAL

        # When - 기본 공격력 조회
        korean_attack = korean_teacher.base_attack_power
        math_attack = math_teacher.base_attack_power
        principal_attack = principal.base_attack_power

        # Then - 설정된 기본 공격력값 반환 확인
        assert korean_attack == 25, '국어 선생님 기본 공격력이 25여야 함'
        assert math_attack == 15, '수학 선생님 기본 공격력이 15여야 함'
        assert principal_attack == 50, '교장 선생님 기본 공격력이 50이어야 함'


class TestEnemyComponent:
    """Test cases for EnemyComponent class."""

    def test_적_컴포넌트_기본_초기화_검증_성공_시나리오(self) -> None:
        """5. 적 컴포넌트 기본 초기화 검증 (성공 시나리오)

        목적: 기본값으로 EnemyComponent 생성 및 속성 확인
        테스트할 범위: 기본 초기화
        커버하는 함수 및 데이터: 기본 dataclass 필드값
        기대되는 안정성: 기본값들이 정확히 설정됨
        """
        # Given & When - 기본값으로 적 컴포넌트 생성
        enemy = EnemyComponent()

        # Then - 기본값 확인
        assert enemy.enemy_type == EnemyType.KOREAN, (
            '기본 적 타입이 국어 선생님이어야 함'
        )
        assert enemy.difficulty_level == 1, '기본 난이도 레벨이 1이어야 함'
        assert enemy.experience_reward == 10, '기본 경험치 보상이 10이어야 함'
        assert enemy.is_boss is False, '기본 보스 여부가 False여야 함'

    def test_적_컴포넌트_커스텀_초기화_검증_성공_시나리오(self) -> None:
        """6. 적 컴포넌트 커스텀 초기화 검증 (성공 시나리오)

        목적: 사용자 정의값으로 EnemyComponent 생성 및 속성 확인
        테스트할 범위: 커스텀 초기화
        커버하는 함수 및 데이터: dataclass 필드 설정
        기대되는 안정성: 설정한 값들이 정확히 저장됨
        """
        # Given - 커스텀 설정값
        custom_type = EnemyType.PRINCIPAL
        custom_level = 5
        custom_reward = 50
        custom_boss = True

        # When - 커스텀값으로 적 컴포넌트 생성
        enemy = EnemyComponent(
            enemy_type=custom_type,
            difficulty_level=custom_level,
            experience_reward=custom_reward,
            is_boss=custom_boss,
        )

        # Then - 설정값 확인
        assert enemy.enemy_type == custom_type, (
            '설정한 적 타입이 저장되어야 함'
        )
        assert enemy.difficulty_level == custom_level, (
            '설정한 난이도가 저장되어야 함'
        )
        assert enemy.experience_reward == custom_reward, (
            '설정한 경험치가 저장되어야 함'
        )
        assert enemy.is_boss == custom_boss, '설정한 보스 여부가 저장되어야 함'

    def test_적_컴포넌트_유효성_검사_성공_시나리오(self) -> None:
        """7. 적 컴포넌트 유효성 검사 성공 시나리오

        목적: 유효한 설정값에 대한 validate() 메서드 성공 동작 확인
        테스트할 범위: validate() 메서드
        커버하는 함수 및 데이터: validate() 반환값
        기대되는 안정성: 유효한 데이터에 대해 True 반환
        """
        # Given - 유효한 설정값들
        valid_configs = [
            (EnemyType.KOREAN, 1, 0, False),  # 최소 경계값
            (EnemyType.MATH, 5, 25, True),  # 중간값
            (EnemyType.PRINCIPAL, 10, 100, False),  # 최대 경계값
        ]

        for enemy_type, level, reward, is_boss in valid_configs:
            # When - 유효한 설정으로 적 컴포넌트 생성 및 검증
            enemy = EnemyComponent(
                enemy_type=enemy_type,
                difficulty_level=level,
                experience_reward=reward,
                is_boss=is_boss,
            )
            result = enemy.validate()

            # Then - 유효성 검사 성공 확인
            assert result is True, (
                f'유효한 설정 {enemy_type}, {level}, {reward}, {is_boss}에 대해 True를 반환해야 함'
            )

    def test_적_컴포넌트_유효성_검사_실패_시나리오(self) -> None:
        """8. 적 컴포넌트 유효성 검사 실패 시나리오

        목적: 무효한 설정값에 대한 validate() 메서드 실패 동작 확인
        테스트할 범위: validate() 메서드
        커버하는 함수 및 데이터: validate() 반환값
        기대되는 안정성: 무효한 데이터에 대해 False 반환
        """
        # Given - 무효한 설정값들
        invalid_configs = [
            (EnemyType.KOREAN, 0, 10, False),  # 난이도 레벨 너무 낮음
            (EnemyType.MATH, 11, 10, False),  # 난이도 레벨 너무 높음
            (EnemyType.PRINCIPAL, 5, -5, True),  # 음수 경험치
        ]

        for enemy_type, level, reward, is_boss in invalid_configs:
            # When - 무효한 설정으로 적 컴포넌트 생성 및 검증
            enemy = EnemyComponent(
                enemy_type=enemy_type,
                difficulty_level=level,
                experience_reward=reward,
                is_boss=is_boss,
            )
            result = enemy.validate()

            # Then - 유효성 검사 실패 확인
            assert result is False, (
                f'무효한 설정 {enemy_type}, {level}, {reward}, {is_boss}에 대해 False를 반환해야 함'
            )

    def test_적_체력_스케일링_계산_정확성_검증_성공_시나리오(self) -> None:
        """9. 적 체력 스케일링 계산 정확성 검증 (성공 시나리오)

        목적: 난이도에 따른 체력 스케일링 계산 정확성 검증
        테스트할 범위: get_scaled_health() 메서드
        커버하는 함수 및 데이터: 난이도별 체력 배율 계산
        기대되는 안정성: 올바른 배율로 체력 계산
        """
        # Given - 각 적 타입별 테스트 케이스
        test_cases = [
            (EnemyType.KOREAN, 1, 50),  # 기본 체력 50, 난이도 1: 50 * 1.0 = 50
            (EnemyType.KOREAN, 5, 90),  # 기본 체력 50, 난이도 5: 50 * 1.8 = 90
            (EnemyType.MATH, 1, 30),  # 기본 체력 30, 난이도 1: 30 * 1.0 = 30
            (
                EnemyType.MATH,
                10,
                84,
            ),  # 기본 체력 30, 난이도 10: 30 * 2.8 = 84
            (
                EnemyType.PRINCIPAL,
                3,
                280,
            ),  # 기본 체력 200, 난이도 3: 200 * 1.4 = 280
        ]

        for enemy_type, level, expected_health in test_cases:
            # When - 적 컴포넌트 생성 및 스케일된 체력 조회
            enemy = EnemyComponent(
                enemy_type=enemy_type, difficulty_level=level
            )
            scaled_health = enemy.get_scaled_health()

            # Then - 올바른 체력 계산 확인
            assert scaled_health == expected_health, (
                f'{enemy_type} 난이도 {level}에서 체력이 {expected_health}여야 함 (실제: {scaled_health})'
            )

    def test_속도_스케일링_기획서_규칙_검증_성공_시나리오(self) -> None:
        """10. 속도 스케일링 기획서 규칙 검증 (성공 시나리오)

        목적: 기획서에 따른 적별 속도 스케일링 규칙 준수 확인
        테스트할 범위: get_scaled_speed() 메서드
        커버하는 함수 및 데이터: 적 타입별 속도 스케일링 로직
        기대되는 안정성: 수학, 교장만 속도 증가, 국어는 고정
        """
        # Given - 각 적 타입과 난이도 레벨
        difficulty_level = 5

        korean_enemy = EnemyComponent(
            enemy_type=EnemyType.KOREAN, difficulty_level=difficulty_level
        )
        math_enemy = EnemyComponent(
            enemy_type=EnemyType.MATH, difficulty_level=difficulty_level
        )
        principal_enemy = EnemyComponent(
            enemy_type=EnemyType.PRINCIPAL, difficulty_level=difficulty_level
        )

        # When - 스케일된 속도 조회
        korean_speed = korean_enemy.get_scaled_speed()
        math_speed = math_enemy.get_scaled_speed()
        principal_speed = principal_enemy.get_scaled_speed()

        # Then - 기획서에 따른 스케일링 규칙 확인
        assert korean_speed == 30.0, (
            '국어 선생님은 속도 스케일링이 적용되지 않아야 함'
        )
        assert math_speed == 112.0, (
            '수학 선생님은 속도 스케일링이 적용되어야 함 (80.0 * 1.4 = 112.0)'
        )
        assert principal_speed == 70.0, (
            '교장 선생님은 속도 스케일링이 적용되어야 함 (50.0 * 1.4 = 70.0)'
        )

    def test_공격력_스케일링_기획서_규칙_검증_성공_시나리오(self) -> None:
        """11. 공격력 스케일링 기획서 규칙 검증 (성공 시나리오)

        목적: 기획서에 따른 적별 공격력 스케일링 규칙 준수 확인
        테스트할 범위: get_scaled_attack_power() 메서드
        커버하는 함수 및 데이터: 적 타입별 공격력 스케일링 로직
        기대되는 안정성: 국어, 교장만 공격력 증가, 수학은 고정
        """
        # Given - 각 적 타입과 난이도 레벨
        difficulty_level = 6

        korean_enemy = EnemyComponent(
            enemy_type=EnemyType.KOREAN, difficulty_level=difficulty_level
        )
        math_enemy = EnemyComponent(
            enemy_type=EnemyType.MATH, difficulty_level=difficulty_level
        )
        principal_enemy = EnemyComponent(
            enemy_type=EnemyType.PRINCIPAL, difficulty_level=difficulty_level
        )

        # When - 스케일된 공격력 조회
        korean_attack = korean_enemy.get_scaled_attack_power()
        math_attack = math_enemy.get_scaled_attack_power()
        principal_attack = principal_enemy.get_scaled_attack_power()

        # Then - 기획서에 따른 스케일링 규칙 확인
        assert korean_attack == 50, (
            '국어 선생님은 공격력 스케일링이 적용되어야 함 (25 * 2.0 = 50)'
        )
        assert math_attack == 15, (
            '수학 선생님은 공격력 스케일링이 적용되지 않아야 함'
        )
        assert principal_attack == 100, (
            '교장 선생님은 공격력 스케일링이 적용되어야 함 (50 * 2.0 = 100)'
        )

    def test_경험치_보상_스케일링_계산_정확성_검증_성공_시나리오(self) -> None:
        """12. 경험치 보상 스케일링 계산 정확성 검증 (성공 시나리오)

        목적: 난이도에 따른 경험치 보상 스케일링 계산 정확성 검증
        테스트할 범위: get_experience_reward() 메서드
        커버하는 함수 및 데이터: 난이도별 경험치 배율 계산
        기대되는 안정성: 올바른 배율로 경험치 계산
        """
        # Given - 경험치 스케일링 테스트 케이스
        test_cases = [
            (10, 1, 10),  # 기본 경험치 10, 난이도 1: 10 * 1.0 = 10
            (20, 3, 40),  # 기본 경험치 20, 난이도 3: 20 * 2.0 = 40
            (30, 10, 165),  # 기본 경험치 30, 난이도 10: 30 * 5.5 = 165
        ]

        for base_reward, level, expected_reward in test_cases:
            # When - 적 컴포넌트 생성 및 스케일된 경험치 조회
            enemy = EnemyComponent(
                experience_reward=base_reward, difficulty_level=level
            )
            scaled_reward = enemy.get_experience_reward()

            # Then - 올바른 경험치 계산 확인
            assert scaled_reward == expected_reward, (
                f'기본 경험치 {base_reward}, 난이도 {level}에서 경험치가 {expected_reward}여야 함 (실제: {scaled_reward})'
            )

    def test_타겟팅_유효성_확인_성공_시나리오(self) -> None:
        """13. 타겟팅 유효성 확인 (성공 시나리오)

        목적: 적이 공격 대상으로서 유효한지 확인
        테스트할 범위: is_valid_target() 메서드
        커버하는 함수 및 데이터: 타겟팅 가능 여부 판단
        기대되는 안정성: 현재는 항상 유효한 타겟으로 반환
        """
        # Given - 다양한 설정의 적 컴포넌트들
        enemies = [
            EnemyComponent(enemy_type=EnemyType.KOREAN),
            EnemyComponent(enemy_type=EnemyType.MATH, difficulty_level=10),
            EnemyComponent(enemy_type=EnemyType.PRINCIPAL, is_boss=True),
        ]

        for enemy in enemies:
            # When - 타겟팅 유효성 검사
            is_valid = enemy.is_valid_target()

            # Then - 모든 적이 유효한 타겟으로 확인
            assert is_valid is True, (
                f'모든 적은 유효한 타겟이어야 함: {enemy.enemy_type}'
            )

    def test_컴포넌트_속성_불변성_확인_성공_시나리오(self) -> None:
        """14. 컴포넌트 속성 불변성 확인 (성공 시나리오)

        목적: 메서드 실행 후 컴포넌트 속성이 변경되지 않는지 확인
        테스트할 범위: 모든 메서드 실행 후 속성 불변성
        커버하는 함수 및 데이터: 순수 함수로서의 동작 보장
        기대되는 안정성: 속성값들이 메서드 실행 전후 동일
        """
        # Given - 적 컴포넌트 생성
        original_enemy = EnemyComponent(
            enemy_type=EnemyType.PRINCIPAL,
            difficulty_level=7,
            experience_reward=50,
            is_boss=True,
        )

        # 원본 속성값 저장
        original_type = original_enemy.enemy_type
        original_level = original_enemy.difficulty_level
        original_reward = original_enemy.experience_reward
        original_boss = original_enemy.is_boss

        # When - 모든 메서드 실행
        original_enemy.validate()
        original_enemy.get_scaled_health()
        original_enemy.get_scaled_speed()
        original_enemy.get_scaled_attack_power()
        original_enemy.get_experience_reward()
        original_enemy.is_valid_target()

        # Then - 속성값 불변 확인
        assert original_enemy.enemy_type == original_type, (
            '적 타입이 변경되지 않아야 함'
        )
        assert original_enemy.difficulty_level == original_level, (
            '난이도가 변경되지 않아야 함'
        )
        assert original_enemy.experience_reward == original_reward, (
            '경험치가 변경되지 않아야 함'
        )
        assert original_enemy.is_boss == original_boss, (
            '보스 여부가 변경되지 않아야 함'
        )
