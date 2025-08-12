"""
Unit tests for HealthComponent.

Tests the health management system including damage application,
healing, regeneration, and state management.
"""

from src.components.health_component import HealthComponent


class TestHealthComponent:
    """Test cases for HealthComponent class."""

    def test_체력_컴포넌트_기본_초기화_검증_성공_시나리오(self) -> None:
        """1. 체력 컴포넌트 기본 초기화 검증 (성공 시나리오).

        목적: 기본값으로 HealthComponent 생성 및 속성 확인
        테스트할 범위: 기본 초기화
        커버하는 함수 및 데이터: 기본 dataclass 필드값
        기대되는 안정성: 기본값들이 정확히 설정됨
        """
        # Given & When - 기본값으로 체력 컴포넌트 생성
        health = HealthComponent()

        # Then - 기본값 확인
        assert health.current_health == 100, '기본 현재 체력이 100이어야 함'
        assert health.max_health == 100, '기본 최대 체력이 100이어야 함'
        assert health.damage_immunity_time == 0.0, (
            '기본 데미지 면역 시간이 0.0이어야 함'
        )
        assert health.last_damage_time == 0.0, (
            '기본 마지막 데미지 시간이 0.0이어야 함'
        )
        assert health.is_invulnerable is False, '기본 무적 상태가 False여야 함'
        assert health.regeneration_rate == 0.0, '기본 재생율이 0.0이어야 함'

    def test_체력_컴포넌트_커스텀_초기화_검증_성공_시나리오(self) -> None:
        """2. 체력 컴포넌트 커스텀 초기화 검증 (성공 시나리오).

        목적: 사용자 정의값으로 HealthComponent 생성 및 속성 확인
        테스트할 범위: 커스텀 초기화
        커버하는 함수 및 데이터: dataclass 필드 설정
        기대되는 안정성: 설정한 값들이 정확히 저장됨
        """
        # Given - 커스텀 설정값
        custom_current = 80
        custom_max = 150
        custom_immunity = 2.5
        custom_regen = 5.0

        # When - 커스텀값으로 체력 컴포넌트 생성
        health = HealthComponent(
            current_health=custom_current,
            max_health=custom_max,
            damage_immunity_time=custom_immunity,
            regeneration_rate=custom_regen,
            is_invulnerable=True,
        )

        # Then - 설정값 확인
        assert health.current_health == custom_current, (
            '설정한 현재 체력이 저장되어야 함'
        )
        assert health.max_health == custom_max, (
            '설정한 최대 체력이 저장되어야 함'
        )
        assert health.damage_immunity_time == custom_immunity, (
            '설정한 데미지 면역 시간이 저장되어야 함'
        )
        assert health.regeneration_rate == custom_regen, (
            '설정한 재생율이 저장되어야 함'
        )
        assert health.is_invulnerable is True, (
            '설정한 무적 상태가 저장되어야 함'
        )

    def test_post_init_체력_조정_검증_성공_시나리오(self) -> None:
        """3. __post_init__ 체력 조정 검증 (성공 시나리오).

        목적: current_health > max_health인 경우 자동 조정 확인
        테스트할 범위: __post_init__ 메서드
        커버하는 함수 및 데이터: 체력 범위 조정 로직
        기대되는 안정성: 불변 조건 유지
        """
        # Given & When - 현재 체력이 최대 체력을 초과하는 설정
        health = HealthComponent(current_health=150, max_health=100)

        # Then - 현재 체력이 최대 체력으로 조정됨
        assert health.current_health == 100, (
            '현재 체력이 최대 체력으로 조정되어야 함'
        )
        assert health.max_health == 100, '최대 체력은 설정값 유지'

    def test_정상_데미지_적용_검증_성공_시나리오(self) -> None:
        """4. 정상 데미지 적용 검증 (성공 시나리오).

        목적: 일반적인 데미지 처리 동작 확인
        테스트할 범위: take_damage 메서드
        커버하는 함수 및 데이터: 데미지 적용 로직
        기대되는 안정성: 올바른 상태 변화 및 반환값
        """
        # Given - 정상 상태의 체력 컴포넌트
        health = HealthComponent(current_health=100, max_health=100)

        # When - 30 데미지 적용
        damage_dealt = health.take_damage(30, 1.0)

        # Then - 체력 감소 및 상태 업데이트 확인
        assert health.current_health == 70, '현재 체력이 30 감소해야 함'
        assert health.last_damage_time == 1.0, (
            '마지막 데미지 시간이 업데이트되어야 함'
        )
        assert damage_dealt == 30, '실제 적용된 데미지량이 반환되어야 함'

    def test_과도한_데미지_처리_검증_성공_시나리오(self) -> None:
        """5. 과도한 데미지 처리 검증 (성공 시나리오).

        목적: 현재 체력보다 큰 데미지 처리 확인
        테스트할 범위: take_damage 메서드 경계값
        커버하는 함수 및 데이터: 데미지 상한 제한 로직
        기대되는 안정성: 체력이 음수가 되지 않음
        """
        # Given - 체력 50인 컴포넌트
        health = HealthComponent(current_health=50, max_health=100)

        # When - 100 데미지 적용 (현재 체력보다 큼)
        damage_dealt = health.take_damage(100, 1.0)

        # Then - 현재 체력만큼만 데미지 적용
        assert health.current_health == 0, '현재 체력이 0이 되어야 함'
        assert damage_dealt == 50, '실제 적용된 데미지는 50이어야 함'

    def test_무적_상태_데미지_무시_검증_성공_시나리오(self) -> None:
        """6. 무적 상태 데미지 무시 검증 (성공 시나리오).

        목적: 무적 상태에서 데미지 무시 동작 확인
        테스트할 범위: take_damage 메서드 무적 처리
        커버하는 함수 및 데이터: is_invulnerable 조건부 로직
        기대되는 안정성: 무적 시 체력 변화 없음
        """
        # Given - 무적 상태인 컴포넌트
        health = HealthComponent(current_health=100, is_invulnerable=True)

        # When - 50 데미지 적용
        damage_dealt = health.take_damage(50, 1.0)

        # Then - 데미지 무시됨
        assert health.current_health == 100, (
            '무적 상태에서 체력 변화 없어야 함'
        )
        assert damage_dealt == 0, '무적 상태에서 데미지 적용량 0이어야 함'

    def test_데미지_면역_시간_검증_성공_시나리오(self) -> None:
        """7. 데미지 면역 시간 검증 (성공 시나리오).

        목적: 데미지 면역 시간 내 추가 데미지 무시 확인
        테스트할 범위: take_damage 메서드 면역 시간 처리
        커버하는 함수 및 데이터: damage_immunity_time 조건부 로직
        기대되는 안정성: 면역 시간 내 데미지 무시
        """
        # Given - 데미지 면역 시간이 있는 컴포넌트 (충분히 이전 시간 설정)
        health = HealthComponent(
            current_health=100, damage_immunity_time=2.0, last_damage_time=-5.0
        )

        # When - 첫 번째 데미지 적용 (면역 시간 밖에서 시작)
        first_damage = health.take_damage(30, 1.0)

        # When - 면역 시간 내에 두 번째 데미지 적용
        second_damage = health.take_damage(20, 2.5)  # 1.5초 후 (면역 시간 내)

        # Then - 첫 번째 데미지만 적용됨
        assert health.current_health == 70, '첫 번째 데미지만 적용되어야 함'
        assert first_damage == 30, '첫 번째 데미지는 정상 적용'
        assert second_damage == 0, '면역 시간 내 두 번째 데미지는 무시'

    def test_float_타입_데미지_처리_검증_성공_시나리오(self) -> None:
        """8. float 타입 데미지 처리 검증 (성공 시나리오).

        목적: float 타입 데미지의 int 변환 처리 확인
        테스트할 범위: take_damage 메서드 타입 변환
        커버하는 함수 및 데이터: int() 변환 로직
        기대되는 안정성: float 값의 올바른 변환
        """
        # Given - 정상 상태의 컴포넌트
        health = HealthComponent(current_health=100)

        # When - float 타입 데미지 적용
        damage_dealt = health.take_damage(25.7, 1.0)

        # Then - int로 변환되어 처리됨
        assert health.current_health == 75, '25.7 -> 25로 변환되어 적용'
        assert damage_dealt == 25, '반환값도 int로 변환됨'

    def test_정상_힐링_적용_검증_성공_시나리오(self) -> None:
        """9. 정상 힐링 적용 검증 (성공 시나리오).

        목적: 일반적인 힐링 처리 동작 확인
        테스트할 범위: heal 메서드
        커버하는 함수 및 데이터: 힐링 적용 로직
        기대되는 안정성: 올바른 체력 회복
        """
        # Given - 체력이 감소한 컴포넌트
        health = HealthComponent(current_health=50, max_health=100)

        # When - 30 힐링 적용
        healed_amount = health.heal(30)

        # Then - 체력 회복 확인
        assert health.current_health == 80, '현재 체력이 30 증가해야 함'
        assert healed_amount == 30, '실제 회복된 체력량이 반환되어야 함'

    def test_최대_체력_한도_힐링_검증_성공_시나리오(self) -> None:
        """10. 최대 체력 한도 힐링 검증 (성공 시나리오).

        목적: 최대 체력을 초과하는 힐링 제한 확인
        테스트할 범위: heal 메서드 상한 제한
        커버하는 함수 및 데이터: max_health 경계값 처리
        기대되는 안정성: 체력이 최대치를 초과하지 않음
        """
        # Given - 체력 80인 컴포넌트 (max_health=100)
        health = HealthComponent(current_health=80, max_health=100)

        # When - 50 힐링 적용 (최대 체력 초과)
        healed_amount = health.heal(50)

        # Then - 최대 체력까지만 회복
        assert health.current_health == 100, (
            '현재 체력이 최대 체력이 되어야 함'
        )
        assert healed_amount == 20, '실제 회복량은 20이어야 함'

    def test_0_이하_힐링_무시_검증_성공_시나리오(self) -> None:
        """11. 0 이하 힐링 무시 검증 (성공 시나리오).

        목적: 0 이하 힐링값 무시 동작 확인
        테스트할 범위: heal 메서드 경계값
        커버하는 함수 및 데이터: amount <= 0 조건 처리
        기대되는 안정성: 무효한 힐링값 무시
        """
        # Given - 정상 상태의 컴포넌트
        health = HealthComponent(current_health=50, max_health=100)
        initial_health = health.current_health

        # When - 0 힐링 적용
        healed_amount = health.heal(0)

        # Then - 체력 변화 없음
        assert health.current_health == initial_health, '체력 변화가 없어야 함'
        assert healed_amount == 0, '회복량이 0이어야 함'

    def test_float_타입_힐링_처리_검증_성공_시나리오(self) -> None:
        """12. float 타입 힐링 처리 검증 (성공 시나리오).

        목적: float 타입 힐링값의 int 변환 처리 확인
        테스트할 범위: heal 메서드 타입 변환
        커버하는 함수 및 데이터: int() 변환 로직
        기대되는 안정성: float 값의 올바른 변환
        """
        # Given - 체력이 감소한 컴포넌트
        health = HealthComponent(current_health=50, max_health=100)

        # When - float 타입 힐링 적용
        healed_amount = health.heal(25.9)

        # Then - int로 변환되어 처리됨
        assert health.current_health == 75, '25.9 -> 25로 변환되어 적용'
        assert healed_amount == 25, '반환값도 int로 변환됨'

    def test_정상_최대_체력_설정_검증_성공_시나리오(self) -> None:
        """13. 정상 최대 체력 설정 검증 (성공 시나리오).

        목적: 최대 체력 설정 동작 확인
        테스트할 범위: set_max_health 메서드
        커버하는 함수 및 데이터: max_health 설정 로직
        기대되는 안정성: 올바른 최대 체력 변경
        """
        # Given - 기본 컴포넌트
        health = HealthComponent()

        # When - 최대 체력을 150으로 설정
        health.set_max_health(150)

        # Then - 최대 체력 변경 확인
        assert health.max_health == 150, '최대 체력이 150으로 변경되어야 함'

    def test_최대_체력_감소_시_현재_체력_조정_검증_성공_시나리오(self) -> None:
        """14. 최대 체력 감소 시 현재 체력 조정 검증 (성공 시나리오).

        목적: 최대 체력 감소 시 현재 체력 자동 조정 확인
        테스트할 범위: set_max_health 메서드 부작용
        커버하는 함수 및 데이터: 체력 조정 로직
        기대되는 안정성: 불변 조건 유지
        """
        # Given - 현재 체력이 최대인 컴포넌트
        health = HealthComponent(current_health=100, max_health=100)

        # When - 최대 체력을 80으로 감소
        health.set_max_health(80)

        # Then - 현재 체력도 조정됨
        assert health.max_health == 80, '최대 체력이 80으로 변경되어야 함'
        assert health.current_health == 80, '현재 체력이 80으로 조정되어야 함'

    def test_float_타입_최대_체력_처리_검증_성공_시나리오(self) -> None:
        """15. float 타입 최대 체력 처리 검증 (성공 시나리오).

        목적: float 타입 최대 체력의 int 변환 처리 확인
        테스트할 범위: set_max_health 메서드 타입 변환
        커버하는 함수 및 데이터: int() 변환 로직
        기대되는 안정성: float 값의 올바른 변환
        """
        # Given - 기본 컴포넌트
        health = HealthComponent()

        # When - float 타입 최대 체력 설정
        health.set_max_health(120.7)

        # Then - int로 변환되어 설정됨
        assert health.max_health == 120, '120.7 -> 120으로 변환되어 설정'

    def test_생존_상태_확인_검증_성공_시나리오(self) -> None:
        """16. 생존 상태 확인 검증 (성공 시나리오).

        목적: 생존 상태 판정 동작 확인
        테스트할 범위: is_alive 메서드
        커버하는 함수 및 데이터: 체력 > 0 조건 판정
        기대되는 안정성: 올바른 생존 상태 반환
        """
        # Given - 체력이 있는 컴포넌트
        health = HealthComponent(current_health=50)

        # When - 생존 상태 확인
        is_alive = health.is_alive()

        # Then - True 반환
        assert is_alive is True, '체력이 있으면 생존 상태여야 함'

    def test_사망_상태_확인_검증_성공_시나리오(self) -> None:
        """17. 사망 상태 확인 검증 (성공 시나리오).

        목적: 사망 상태 판정 동작 확인
        테스트할 범위: is_dead 메서드
        커버하는 함수 및 데이터: 체력 <= 0 조건 판정
        기대되는 안정성: 올바른 사망 상태 반환
        """
        # Given - 체력이 0인 컴포넌트
        health = HealthComponent(current_health=0)

        # When - 사망 상태 확인
        is_dead = health.is_dead()

        # Then - True 반환
        assert is_dead is True, '체력이 0이면 사망 상태여야 함'

    def test_체력_비율_계산_검증_성공_시나리오(self) -> None:
        """18. 체력 비율 계산 검증 (성공 시나리오).

        목적: 체력 비율 계산 동작 확인
        테스트할 범위: get_health_ratio 메서드
        커버하는 함수 및 데이터: 체력 비율 계산 로직
        기대되는 안정성: 올바른 비율 반환
        """
        # Given - 체력 75인 컴포넌트 (max_health=100)
        health = HealthComponent(current_health=75, max_health=100)

        # When - 체력 비율 계산
        ratio = health.get_health_ratio()

        # Then - 0.75 반환
        assert ratio == 0.75, '체력 비율이 0.75여야 함'

    def test_중상_판정_검증_성공_시나리오(self) -> None:
        """19. 중상 판정 검증 (성공 시나리오).

        목적: 중상 상태 판정 동작 확인
        테스트할 범위: is_critically_wounded 메서드
        커버하는 함수 및 데이터: threshold 비교 로직
        기대되는 안정성: 올바른 중상 판정
        """
        # Given - 체력 20인 컴포넌트 (max_health=100)
        health = HealthComponent(current_health=20, max_health=100)

        # When - 중상 판정 (threshold=0.25)
        is_critical = health.is_critically_wounded(0.25)

        # Then - True 반환 (20/100 = 0.2 <= 0.25)
        assert is_critical is True, (
            '체력 비율이 임계값 이하면 중상 상태여야 함'
        )

    def test_정상_재생_처리_검증_성공_시나리오(self) -> None:
        """20. 정상 재생 처리 검증 (성공 시나리오).

        목적: 체력 재생 시스템 동작 확인
        테스트할 범위: update_regeneration 메서드
        커버하는 함수 및 데이터: 재생 계산 및 힐링 연동
        기대되는 안정성: 올바른 재생 처리
        """
        # Given - 재생율이 있는 컴포넌트
        health = HealthComponent(
            current_health=50, max_health=100, regeneration_rate=10.0
        )

        # When - 2초 후 재생 업데이트
        regenerated = health.update_regeneration(2.0)

        # Then - 20 체력 재생 (10.0 * 2.0 = 20)
        assert health.current_health == 70, '체력이 20 재생되어야 함'
        assert regenerated == 20, '재생된 체력량이 반환되어야 함'

    def test_사망_상태_재생_무시_검증_성공_시나리오(self) -> None:
        """21. 사망 상태 재생 무시 검증 (성공 시나리오).

        목적: 사망 상태에서 재생 무시 동작 확인
        테스트할 범위: update_regeneration 메서드 조건 처리
        커버하는 함수 및 데이터: is_dead() 조건부 로직
        기대되는 안정성: 사망 시 재생 없음
        """
        # Given - 사망 상태이지만 재생율이 있는 컴포넌트
        health = HealthComponent(
            current_health=0, max_health=100, regeneration_rate=10.0
        )

        # When - 재생 업데이트 시도
        regenerated = health.update_regeneration(1.0)

        # Then - 재생 없음
        assert health.current_health == 0, '사망 상태에서 체력 변화 없어야 함'
        assert regenerated == 0, '사망 상태에서 재생량 0이어야 함'

    def test_유효성_검사_성공_시나리오(self) -> None:
        """22. 유효성 검사 성공 시나리오.

        목적: 유효한 컴포넌트의 validate 메서드 동작 확인
        테스트할 범위: validate 메서드
        커버하는 함수 및 데이터: 모든 유효성 조건 검사
        기대되는 안정성: 유효한 상태에서 True 반환
        """
        # Given - 모든 값이 유효한 컴포넌트
        health = HealthComponent(
            current_health=80,
            max_health=100,
            damage_immunity_time=1.5,
            last_damage_time=2.0,
            regeneration_rate=5.0,
        )

        # When - 유효성 검사
        is_valid = health.validate()

        # Then - True 반환
        assert is_valid is True, '유효한 상태에서 True를 반환해야 함'

    def test_유효성_검사_실패_시나리오(self) -> None:
        """23. 유효성 검사 실패 시나리오.

        목적: 무효한 컴포넌트의 validate 메서드 동작 확인
        테스트할 범위: validate 메서드 실패 조건
        커버하는 함수 및 데이터: 유효성 조건 위반 검사
        기대되는 안정성: 무효한 상태에서 False 반환
        """
        # Given - 무효한 값을 가진 컴포넌트 (현재 체력이 최대 체력 초과)
        health = HealthComponent(max_health=100)
        health.current_health = 150  # 직접 설정으로 무효 상태 생성

        # When - 유효성 검사
        is_valid = health.validate()

        # Then - False 반환
        assert is_valid is False, '무효한 상태에서 False를 반환해야 함'

    def test_무적_상태_설정_검증_성공_시나리오(self) -> None:
        """24. 무적 상태 설정 검증 (성공 시나리오).

        목적: 무적 상태 설정 동작 확인
        테스트할 범위: set_invulnerable 메서드
        커버하는 함수 및 데이터: is_invulnerable 상태 변경
        기대되는 안정성: 올바른 무적 상태 설정
        """
        # Given - 기본 컴포넌트
        health = HealthComponent()

        # When - 무적 상태 설정
        health.set_invulnerable(True)

        # Then - 무적 상태 변경 확인
        assert health.is_invulnerable is True, (
            '무적 상태가 True로 설정되어야 함'
        )

    def test_완전_회복_검증_성공_시나리오(self) -> None:
        """25. 완전 회복 검증 (성공 시나리오).

        목적: 완전 회복 동작 확인
        테스트할 범위: full_heal 메서드
        커버하는 함수 및 데이터: 체력 최대치 설정
        기대되는 안정성: 체력이 최대치가 됨
        """
        # Given - 체력이 감소한 컴포넌트
        health = HealthComponent(current_health=50, max_health=100)

        # When - 완전 회복
        health.full_heal()

        # Then - 체력이 최대치가 됨
        assert health.current_health == health.max_health, (
            '체력이 최대치와 같아져야 함'
        )

    def test_체력_범위_불변_조건_검증_성공_시나리오(self) -> None:
        """26. 체력 범위 불변 조건 검증 (성공 시나리오).

        목적: 모든 메서드 실행 후 체력 범위 불변 조건 유지 확인
        테스트할 범위: 모든 메서드의 불변 조건 유지
        커버하는 함수 및 데이터: 체력 범위 검증
        기대되는 안정성: 항상 0 <= current_health <= max_health
        """
        # Given - 다양한 상태의 컴포넌트들
        test_cases = [
            HealthComponent(current_health=0, max_health=100),
            HealthComponent(current_health=50, max_health=100),
            HealthComponent(current_health=100, max_health=100),
        ]

        for health in test_cases:
            # When - 다양한 메서드 실행
            health.take_damage(10, 1.0)
            health.heal(5)
            health.set_max_health(120)
            health.update_regeneration(1.0)
            health.full_heal()

            # Then - 불변 조건 유지 확인
            assert 0 <= health.current_health <= health.max_health, (
                f'체력 범위 조건 위반: current={health.current_health}, '
                f'max={health.max_health}'
            )

    def test_객체_ID_불변_조건_검증_성공_시나리오(self) -> None:
        """27. 객체 ID 불변 조건 검증 (성공 시나리오).

        목적: 모든 메서드 실행 후 객체 ID 불변 확인
        테스트할 범위: 모든 메서드의 객체 ID 불변성
        커버하는 함수 및 데이터: 객체 동일성 검증
        기대되는 안정성: 객체 ID 변경되지 않음
        """
        # Given - 컴포넌트 생성
        health = HealthComponent(current_health=50, max_health=100)
        original_id = id(health)

        # When - 모든 메서드 실행
        health.validate()
        health.take_damage(20, 1.0)
        health.heal(10)
        health.set_max_health(120)
        health.get_health_ratio()
        health.is_critically_wounded()
        health.update_regeneration(1.0)
        health.set_invulnerable(True)
        health.full_heal()
        health.is_alive()
        health.is_dead()

        # Then - 객체 ID 불변 확인
        assert id(health) == original_id, '객체 ID가 변경되지 않아야 함'
