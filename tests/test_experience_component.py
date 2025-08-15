"""
Tests for ExperienceComponent and related strategies.

This module tests experience management, leveling mechanics,
and strategy pattern implementation.
"""

from src.components.experience_component import (
    DefaultExperiencePolicy,
    DefaultExperienceStrategy,
    ExperienceComponent,
    ExperienceType,
    ExponentialExperienceStrategy,
    LinearExperienceStrategy,
)


class TestExperienceType:
    def test_경험치_타입_enum_값_및_표시명_정확성_검증_성공_시나리오(
        self,
    ) -> None:
        """1. 경험치 타입 enum 값 및 표시명 정확성 검증 (성공 시나리오)

        목적: ExperienceType enum의 값과 표시명이 정확한지 검증
        테스트할 범위: ExperienceType의 모든 enum 값과 display_name 속성
        커버하는 함수 및 데이터: enum 값들과 _display_names 매핑
        기대되는 안정성: 일관된 enum 값과 표시명 제공 보장
        """
        # Given & When & Then - 각 경험치 타입 값 및 표시명 확인
        assert ExperienceType.DEFAULT.value == 0
        assert ExperienceType.DEFAULT.display_name == '기본 경험치'

        assert ExperienceType.LINEAR.value == 1
        assert ExperienceType.LINEAR.display_name == '선형 경험치'

        assert ExperienceType.EXPONENTIAL.value == 2
        assert ExperienceType.EXPONENTIAL.display_name == '지수 경험치'


class TestDefaultExperienceStrategy:
    def test_기본_전략_경험치_계산_정확성_검증_성공_시나리오(self) -> None:
        """2. 기본 전략 경험치 계산 정확성 검증 (성공 시나리오)

        목적: DefaultExperienceStrategy의 경험치 계산이 정확한지 검증
        테스트할 범위: 다음 레벨 필요 경험치와 누적 경험치 계산
        커버하는 함수 및 데이터: calculate_exp_to_next_level, calculate_total_exp_for_level
        기대되는 안정성: 수학적으로 정확한 경험치 계산 보장
        """
        # Given - 기본 전략 생성 (base_exp=100, multiplier=1.5)
        strategy = DefaultExperienceStrategy(base_exp=100, multiplier=1.5)

        # When & Then - 레벨별 경험치 계산 확인
        assert strategy.calculate_exp_to_next_level(0) == 100  # 특수 케이스
        assert strategy.calculate_exp_to_next_level(1) == 100  # 1->2레벨
        assert (
            strategy.calculate_exp_to_next_level(2) == 150
        )  # 2->3레벨 (100 * 1.5^1)
        assert (
            strategy.calculate_exp_to_next_level(3) == 225
        )  # 3->4레벨 (100 * 1.5^2)

        # 누적 경험치 계산 확인
        assert strategy.calculate_total_exp_for_level(1) == 0  # 1레벨까지는 0
        assert (
            strategy.calculate_total_exp_for_level(2) == 100
        )  # 2레벨까지는 100
        assert (
            strategy.calculate_total_exp_for_level(3) == 250
        )  # 3레벨까지는 100+150
        assert (
            strategy.calculate_total_exp_for_level(4) == 475
        )  # 4레벨까지는 100+150+225

    def test_사용자_정의_매개변수_기본_전략_동작_검증_성공_시나리오(
        self,
    ) -> None:
        """3. 사용자 정의 매개변수 기본 전략 동작 검증 (성공 시나리오)

        목적: 커스텀 매개변수로 생성된 기본 전략이 올바르게 동작하는지 검증
        테스트할 범위: 커스텀 base_exp와 multiplier 적용 확인
        커버하는 함수 및 데이터: DefaultExperienceStrategy 초기화 및 계산 메서드
        기대되는 안정성: 다양한 매개변수에도 정확한 계산 보장
        """
        # Given - 커스텀 매개변수로 전략 생성
        strategy = DefaultExperienceStrategy(base_exp=200, multiplier=2.0)

        # When & Then - 커스텀 매개변수 적용 확인
        assert strategy.calculate_exp_to_next_level(1) == 200  # base_exp=200
        assert strategy.calculate_exp_to_next_level(2) == 400  # 200 * 2.0^1
        assert strategy.calculate_exp_to_next_level(3) == 800  # 200 * 2.0^2


class TestLinearExperienceStrategy:
    def test_선형_전략_경험치_계산_정확성_검증_성공_시나리오(self) -> None:
        """4. 선형 전략 경험치 계산 정확성 검증 (성공 시나리오)

        목적: LinearExperienceStrategy의 선형 증가 계산이 정확한지 검증
        테스트할 범위: 선형 증가 방식의 경험치 계산
        커버하는 함수 및 데이터: 선형 증가 공식 적용
        기대되는 안정성: 예측 가능한 선형 경험치 증가 보장
        """
        # Given - 선형 전략 생성 (base_exp=100, increment=50)
        strategy = LinearExperienceStrategy(base_exp=100, increment=50)

        # When & Then - 선형 증가 확인
        assert strategy.calculate_exp_to_next_level(1) == 100  # base_exp
        assert strategy.calculate_exp_to_next_level(2) == 150  # 100 + 50*1
        assert strategy.calculate_exp_to_next_level(3) == 200  # 100 + 50*2
        assert strategy.calculate_exp_to_next_level(4) == 250  # 100 + 50*3

        # 누적 경험치 확인
        assert strategy.calculate_total_exp_for_level(3) == 250  # 100+150


class TestExponentialExperienceStrategy:
    def test_지수_전략_경험치_계산_정확성_검증_성공_시나리오(self) -> None:
        """5. 지수 전략 경험치 계산 정확성 검증 (성공 시나리오)

        목적: ExponentialExperienceStrategy의 지수 증가 계산이 정확한지 검증
        테스트할 범위: 지수 증가 방식의 경험치 계산
        커버하는 함수 및 데이터: 지수 증가 공식 적용
        기대되는 안정성: 빠르게 증가하는 지수 경험치 계산 보장
        """
        # Given - 지수 전략 생성 (base_exp=100, exponent=2.0)
        strategy = ExponentialExperienceStrategy(base_exp=100, exponent=2.0)

        # When & Then - 지수 증가 확인
        assert strategy.calculate_exp_to_next_level(1) == 100  # base_exp
        assert strategy.calculate_exp_to_next_level(2) == 400  # 100 * 2^2
        assert strategy.calculate_exp_to_next_level(3) == 900  # 100 * 3^2
        assert strategy.calculate_exp_to_next_level(4) == 1600  # 100 * 4^2


class TestDefaultExperiencePolicy:
    def test_기본_정책_적_경험치_보상_계산_정확성_검증_성공_시나리오(
        self,
    ) -> None:
        """6. 기본 정책 적 경험치 보상 계산 정확성 검증 (성공 시나리오)

        목적: DefaultExperiencePolicy의 적별 경험치 보상이 정확한지 검증
        테스트할 범위: 적 타입과 레벨에 따른 경험치 보상 계산
        커버하는 함수 및 데이터: get_enemy_exp_reward 메서드
        기대되는 안정성: 적 타입별 차등 경험치 제공 보장
        """
        # Given - 기본 정책 생성
        policy = DefaultExperiencePolicy()

        # When & Then - 적 타입별 기본 경험치 확인
        assert policy.get_enemy_exp_reward('basic', 1) == 10
        assert policy.get_enemy_exp_reward('enhanced', 1) == 25
        assert policy.get_enemy_exp_reward('boss', 1) == 100
        assert policy.get_enemy_exp_reward('mini_boss', 1) == 50
        assert policy.get_enemy_exp_reward('unknown', 1) == 10  # 기본값

        # 레벨별 보너스 확인 (레벨당 20% 증가)
        assert policy.get_enemy_exp_reward('basic', 2) == 12  # 10 * 1.2
        assert policy.get_enemy_exp_reward('basic', 3) == 14  # 10 * 1.4
        assert policy.get_enemy_exp_reward('boss', 2) == 120  # 100 * 1.2

    def test_플레이어_레벨별_경험치_배율_정확성_검증_성공_시나리오(
        self,
    ) -> None:
        """7. 플레이어 레벨별 경험치 배율 정확성 검증 (성공 시나리오)

        목적: 플레이어 레벨에 따른 경험치 획득 배율이 정확한지 검증
        테스트할 범위: 레벨 구간별 경험치 배율 적용
        커버하는 함수 및 데이터: get_exp_multiplier 메서드
        기대되는 안정성: 레벨 진행에 따른 적절한 난이도 조절 보장
        """
        # Given - 기본 정책 생성
        policy = DefaultExperiencePolicy()

        # When & Then - 레벨별 배율 확인
        assert policy.get_exp_multiplier(5) == 1.0  # 1-10레벨: 100%
        assert policy.get_exp_multiplier(10) == 1.0  # 1-10레벨: 100%
        assert policy.get_exp_multiplier(15) == 0.9  # 11-20레벨: 90%
        assert policy.get_exp_multiplier(20) == 0.9  # 11-20레벨: 90%
        assert policy.get_exp_multiplier(25) == 0.8  # 21+레벨: 80%

    def test_레벨업_조건_확인_정확성_검증_성공_시나리오(self) -> None:
        """8. 레벨업 조건 확인 정확성 검증 (성공 시나리오)

        목적: 레벨업 조건 판단이 정확한지 검증
        테스트할 범위: 현재 경험치와 필요 경험치 비교 로직
        커버하는 함수 및 데이터: should_level_up 메서드
        기대되는 안정성: 정확한 레벨업 시점 판단 보장
        """
        # Given - 기본 정책 생성
        policy = DefaultExperiencePolicy()

        # When & Then - 레벨업 조건 확인
        assert policy.should_level_up(100, 100) is True  # 정확히 도달
        assert policy.should_level_up(150, 100) is True  # 초과 달성
        assert policy.should_level_up(99, 100) is False  # 아직 부족
        assert policy.should_level_up(0, 100) is False  # 시작 상태


class TestExperienceComponent:
    def test_경험치_컴포넌트_초기화_및_기본값_검증_성공_시나리오(self) -> None:
        """9. 경험치 컴포넌트 초기화 및 기본값 검증 (성공 시나리오)

        목적: ExperienceComponent의 초기화와 기본값이 올바른지 검증
        테스트할 범위: 컴포넌트 생성과 기본 속성값
        커버하는 함수 및 데이터: __init__, __post_init__ 메서드
        기대되는 안정성: 일관된 초기 상태 보장
        """
        # Given & When - 기본 경험치 컴포넌트 생성
        exp_comp = ExperienceComponent()

        # Then - 기본값 확인
        assert exp_comp.current_exp == 0
        assert exp_comp.level == 1
        assert exp_comp.total_exp_earned == 0
        assert isinstance(exp_comp.strategy, DefaultExperienceStrategy)
        assert isinstance(exp_comp.policy, DefaultExperiencePolicy)
        assert exp_comp.validate() is True

    def test_잘못된_초기값_자동_보정_검증_성공_시나리오(self) -> None:
        """10. 잘못된 초기값 자동 보정 검증 (성공 시나리오)

        목적: 잘못된 초기값이 자동으로 보정되는지 검증
        테스트할 범위: __post_init__의 값 보정 로직
        커버하는 함수 및 데이터: 레벨, 경험치 보정 로직
        기대되는 안정성: 잘못된 입력에 대한 자동 복구 보장
        """
        # Given & When - 잘못된 값으로 컴포넌트 생성
        exp_comp = ExperienceComponent(
            current_exp=-10,  # 음수 경험치
            level=0,  # 0 레벨
            total_exp_earned=-5,  # 음수 총 경험치
        )

        # Then - 자동 보정 확인
        assert exp_comp.current_exp == 0  # 0으로 보정
        assert exp_comp.level == 1  # 1로 보정
        assert exp_comp.total_exp_earned == 0  # current_exp로 보정

    def test_경험치_추가_및_레벨업_동작_검증_성공_시나리오(self) -> None:
        """11. 경험치 추가 및 레벨업 동작 검증 (성공 시나리오)

        목적: 경험치 추가와 레벨업 메커니즘이 올바르게 동작하는지 검증
        테스트할 범위: add_experience 메서드의 경험치 추가와 레벨업 처리
        커버하는 함수 및 데이터: 경험치 계산, 레벨업 조건 확인, 여러 레벨업 처리
        기대되는 안정성: 정확한 경험치 누적과 레벨업 처리 보장
        """
        # Given - 경험치 컴포넌트 생성
        exp_comp = ExperienceComponent()

        # When - 충분한 경험치 추가 (기본 적 처치)
        actual_exp, level_up = exp_comp.add_experience(50, 'basic', 1)

        # Then - 경험치 계산 확인 (50 + 10(basic enemy) * 1.0(multiplier) = 60)
        assert actual_exp == 60
        assert level_up is False  # 아직 레벨업 안함 (필요: 100)
        assert exp_comp.current_exp == 60
        assert exp_comp.level == 1
        assert exp_comp.total_exp_earned == 60

        # When - 레벨업을 위한 추가 경험치
        actual_exp, level_up = exp_comp.add_experience(30, 'basic', 1)

        # Then - 레벨업 확인 (60 + 40 = 100, 레벨업!)
        assert actual_exp == 40  # 30 + 10
        assert level_up is True
        assert exp_comp.level == 2
        assert exp_comp.current_exp == 0  # 레벨업 후 남은 경험치
        assert exp_comp.total_exp_earned == 100

    def test_다중_레벨업_처리_검증_성공_시나리오(self) -> None:
        """12. 다중 레벨업 처리 검증 (성공 시나리오)

        목적: 한 번에 여러 레벨이 올라가는 상황을 올바르게 처리하는지 검증
        테스트할 범위: 대량 경험치 획득 시 연속 레벨업 처리
        커버하는 함수 및 데이터: while 루프를 통한 연속 레벨업 로직
        기대되는 안정성: 어떤 양의 경험치든 정확한 레벨업 처리 보장
        """
        # Given - 경험치 컴포넌트 생성
        exp_comp = ExperienceComponent()

        # When - 보스 처치로 대량 경험치 획득
        actual_exp, level_up = exp_comp.add_experience(500, 'boss', 3)

        # Then - 다중 레벨업 확인
        # 500 + 140(boss lv3 reward) = 640 경험치
        # 1->2레벨: 100 필요, 남은 경험치: 540
        # 2->3레벨: 150 필요, 남은 경험치: 390
        # 3->4레벨: 225 필요, 남은 경험치: 165
        assert level_up is True
        assert exp_comp.level == 4
        assert exp_comp.current_exp == 165
        assert exp_comp.total_exp_earned == 640

    def test_경험치_진행률_계산_정확성_검증_성공_시나리오(self) -> None:
        """13. 경험치 진행률 계산 정확성 검증 (성공 시나리오)

        목적: 현재 레벨에서의 경험치 진행률이 정확하게 계산되는지 검증
        테스트할 범위: get_exp_progress_ratio 메서드
        커버하는 함수 및 데이터: 진행률 비율 계산 로직
        기대되는 안정성: UI 표시를 위한 정확한 진행률 제공 보장
        """
        # Given - 경험치 컴포넌트 생성 후 일부 경험치 추가
        exp_comp = ExperienceComponent()
        exp_comp.current_exp = 50  # 다음 레벨까지 100 필요

        # When & Then - 진행률 확인
        progress = exp_comp.get_exp_progress_ratio()
        assert progress == 0.5  # 50/100 = 50%

        # 경계값 테스트
        exp_comp.current_exp = 0
        assert exp_comp.get_exp_progress_ratio() == 0.0

        exp_comp.current_exp = 100
        assert exp_comp.get_exp_progress_ratio() == 1.0

    def test_전략_교체_동작_검증_성공_시나리오(self) -> None:
        """14. 전략 교체 동작 검증 (성공 시나리오)

        목적: 런타임에 경험치 계산 전략을 교체할 수 있는지 검증
        테스트할 범위: set_strategy 메서드와 전략 교체 후 동작
        커버하는 함수 및 데이터: Strategy 패턴의 런타임 교체
        기대되는 안정성: 게임 중 전략 변경 시에도 안정적 동작 보장
        """
        # Given - 기본 전략으로 시작
        exp_comp = ExperienceComponent()
        original_exp_to_next = exp_comp.get_exp_to_next_level()  # 100

        # When - 선형 전략으로 교체
        linear_strategy = LinearExperienceStrategy(base_exp=200, increment=100)
        exp_comp.set_strategy(linear_strategy)

        # Then - 새로운 전략 적용 확인
        new_exp_to_next = exp_comp.get_exp_to_next_level()  # 200
        assert new_exp_to_next != original_exp_to_next
        assert new_exp_to_next == 200
        assert exp_comp.strategy is linear_strategy

    def test_레벨_정보_조회_완전성_검증_성공_시나리오(self) -> None:
        """15. 레벨 정보 조회 완전성 검증 (성공 시나리오)

        목적: get_level_info가 모든 필요한 정보를 제공하는지 검증
        테스트할 범위: 레벨 정보 딕셔너리의 완전성과 정확성
        커버하는 함수 및 데이터: 종합적인 레벨 정보 제공
        기대되는 안정성: UI와 시스템이 필요로 하는 모든 정보 제공 보장
        """
        # Given - 일부 경험치가 있는 컴포넌트
        exp_comp = ExperienceComponent()
        exp_comp.current_exp = 75
        exp_comp.total_exp_earned = 200
        exp_comp.level = 2

        # When - 레벨 정보 조회
        level_info = exp_comp.get_level_info()

        # Then - 모든 정보 포함 확인
        assert 'level' in level_info
        assert 'current_exp' in level_info
        assert 'exp_to_next' in level_info
        assert 'total_exp_earned' in level_info
        assert 'progress_ratio' in level_info

        assert level_info['level'] == 2
        assert level_info['current_exp'] == 75
        assert level_info['exp_to_next'] == 150  # 2레벨에서 3레벨까지
        assert level_info['total_exp_earned'] == 200
        assert level_info['progress_ratio'] == 0.5  # 75/150

    def test_강제_레벨업_기능_검증_성공_시나리오(self) -> None:
        """16. 강제 레벨업 기능 검증 (성공 시나리오)

        목적: 디버깅이나 치트를 위한 강제 레벨업이 올바르게 동작하는지 검증
        테스트할 범위: force_level_up 메서드
        커버하는 함수 및 데이터: 강제 레벨 증가 로직
        기대되는 안정성: 개발/테스트 목적의 레벨 조작 기능 보장
        """
        # Given - 경험치 컴포넌트 생성
        exp_comp = ExperienceComponent()
        exp_comp.current_exp = 50

        # When - 강제 레벨업 실행
        exp_comp.force_level_up(3)

        # Then - 레벨업 결과 확인
        assert exp_comp.level == 4  # 1 + 3
        assert exp_comp.current_exp == 0  # 경험치 초기화

    def test_경험치_초기화_기능_검증_성공_시나리오(self) -> None:
        """17. 경험치 초기화 기능 검증 (성공 시나리오)

        목적: 경험치 시스템 리셋 기능이 올바르게 동작하는지 검증
        테스트할 범위: reset_experience 메서드
        커버하는 함수 및 데이터: 모든 경험치 관련 값 초기화
        기대되는 안정성: 게임 재시작 시 완전한 상태 초기화 보장
        """
        # Given - 진행된 경험치 컴포넌트
        exp_comp = ExperienceComponent()
        exp_comp.current_exp = 150
        exp_comp.level = 5
        exp_comp.total_exp_earned = 500

        # When - 경험치 초기화
        exp_comp.reset_experience()

        # Then - 초기 상태로 복원 확인
        assert exp_comp.current_exp == 0
        assert exp_comp.level == 1
        assert exp_comp.total_exp_earned == 0
        assert exp_comp.validate() is True
