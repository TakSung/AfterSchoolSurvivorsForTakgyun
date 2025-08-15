"""
DifficultyManager 테스트 모듈

DifficultyManager의 시간 기반 난이도 조정, 능력치 스케일링,
난이도 단계 전환을 검증합니다.
"""

from src.core.difficulty_manager import (
    DifficultyLevel,
    DifficultyManager,
    DifficultySettings,
)


class TestDifficultySettings:
    """DifficultySettings 테스트 클래스"""

    def test_기본_설정값_유효성_검증_성공_시나리오(self) -> None:
        """1. 기본 설정값 유효성 검증 (성공 시나리오)

        목적: DifficultySettings의 기본값이 올바르게 설정되는지 검증
        테스트할 범위: DifficultySettings 초기화 및 유효성 검증
        커버하는 함수 및 데이터: __init__, validate()
        기대되는 안정성: 안전한 기본 설정값으로 시스템 안정성 보장
        """
        # Given & When - 기본 설정 생성
        settings = DifficultySettings()

        # Then - 기본값 검증
        assert settings.easy_duration == 60.0, (
            '쉬움 단계 지속시간이 60초여야 함'
        )
        assert settings.normal_duration == 120.0, (
            '보통 단계 지속시간이 120초여야 함'
        )
        assert settings.hard_duration == 180.0, (
            '어려움 단계 지속시간이 180초여야 함'
        )

        assert settings.health_scale_rate == 0.02, (
            '체력 스케일링 비율이 2%여야 함'
        )
        assert settings.speed_scale_rate == 0.015, (
            '속도 스케일링 비율이 1.5%여야 함'
        )
        assert settings.spawn_scale_rate == 0.05, (
            '스폰 스케일링 비율이 5%여야 함'
        )

        assert settings.max_health_multiplier == 3.0, (
            '최대 체력 배수가 3배여야 함'
        )
        assert settings.max_speed_multiplier == 2.5, (
            '최대 속도 배수가 2.5배여야 함'
        )
        assert settings.min_spawn_multiplier == 0.25, (
            '최소 스폰 배수가 0.25여야 함'
        )

        # 유효성 검증
        assert settings.validate() is True, '기본 설정이 유효해야 함'

    def test_커스텀_설정값_생성_및_검증_성공_시나리오(self) -> None:
        """2. 커스텀 설정값 생성 및 검증 (성공 시나리오)

        목적: 사용자 정의 설정값이 올바르게 적용되는지 검증
        테스트할 범위: 커스텀 설정 생성 및 유효성 검증
        커버하는 함수 및 데이터: 설정값 커스터마이징 및 검증 로직
        기대되는 안정성: 사용자 정의 설정으로 유연한 게임 조정
        """
        # Given - 커스텀 설정값
        custom_settings = DifficultySettings(
            easy_duration=90.0,
            normal_duration=150.0,
            hard_duration=240.0,
            health_scale_rate=0.03,
            speed_scale_rate=0.02,
            spawn_scale_rate=0.04,
            max_health_multiplier=4.0,
            max_speed_multiplier=3.0,
            min_spawn_multiplier=0.2,
        )

        # When & Then - 커스텀 값 확인
        assert custom_settings.easy_duration == 90.0, (
            '커스텀 쉬움 지속시간 적용'
        )
        assert custom_settings.health_scale_rate == 0.03, (
            '커스텀 체력 스케일링 적용'
        )
        assert custom_settings.max_health_multiplier == 4.0, (
            '커스텀 최대 체력 배수 적용'
        )

        # 유효성 검증
        assert custom_settings.validate() is True, '커스텀 설정이 유효해야 함'

    def test_잘못된_설정값_검증_실패_시나리오(self) -> None:
        """3. 잘못된 설정값 검증 실패 (실패 시나리오)

        목적: 잘못된 설정값에 대한 유효성 검증 실패 확인
        테스트할 범위: validate() 메서드의 오류 감지 능력
        커버하는 함수 및 데이터: 설정값 유효성 검증 로직
        기대되는 안정성: 잘못된 설정으로 인한 시스템 오류 방지
        """
        # Given - 잘못된 설정값들
        invalid_settings_list = [
            # 음수 지속시간
            DifficultySettings(easy_duration=-10.0),
            # 음수 스케일링 비율
            DifficultySettings(health_scale_rate=-0.01),
            # 1보다 작은 최대 배수
            DifficultySettings(max_health_multiplier=0.5),
            # 1보다 큰 최소 스폰 배수
            DifficultySettings(min_spawn_multiplier=1.5),
            # 0 또는 음수 최소 스폰 배수
            DifficultySettings(min_spawn_multiplier=0.0),
        ]

        # When & Then - 각 잘못된 설정에 대해 검증 실패 확인
        for i, invalid_settings in enumerate(invalid_settings_list):
            assert invalid_settings.validate() is False, (
                f'잘못된 설정 {i + 1}이 유효성 검증을 통과하지 않아야 함'
            )


class TestDifficultyLevel:
    """DifficultyLevel 열거형 테스트 클래스"""

    def test_난이도_레벨_속성_및_표시명_검증_성공_시나리오(self) -> None:
        """4. 난이도 레벨 속성 및 표시명 검증 (성공 시나리오)

        목적: DifficultyLevel 열거형의 속성과 표시명이 올바른지 검증
        테스트할 범위: DifficultyLevel 열거형 값과 속성
        커버하는 함수 및 데이터: display_name, base_multiplier 속성
        기대되는 안정성: 일관된 난이도 레벨 정보 제공
        """
        # Given & When & Then - 각 난이도 레벨 검증
        assert DifficultyLevel.EASY.display_name == '쉬움', '쉬움 레벨 표시명'
        assert DifficultyLevel.NORMAL.display_name == '보통', (
            '보통 레벨 표시명'
        )
        assert DifficultyLevel.HARD.display_name == '어려움', (
            '어려움 레벨 표시명'
        )
        assert DifficultyLevel.EXTREME.display_name == '극한', (
            '극한 레벨 표시명'
        )

        # 기본 배수 확인
        assert DifficultyLevel.EASY.base_multiplier == 1.0, '쉬움 기본 배수'
        assert DifficultyLevel.NORMAL.base_multiplier == 1.2, '보통 기본 배수'
        assert DifficultyLevel.HARD.base_multiplier == 1.5, '어려움 기본 배수'
        assert DifficultyLevel.EXTREME.base_multiplier == 2.0, '극한 기본 배수'


class TestDifficultyManager:
    """DifficultyManager 테스트 클래스"""

    def setup_method(self) -> None:
        """각 테스트 메서드 전에 실행되는 설정"""
        # 싱글톤 인스턴스 리셋
        DifficultyManager.reset_instance()

    def test_싱글톤_패턴_동일_인스턴스_반환_검증_성공_시나리오(self) -> None:
        """5. 싱글톤 패턴 동일 인스턴스 반환 검증 (성공 시나리오)

        목적: DifficultyManager가 싱글톤 패턴을 올바르게 구현하는지 검증
        테스트할 범위: 싱글톤 인스턴스 생성 및 관리
        커버하는 함수 및 데이터: get_instance(), reset_instance()
        기대되는 안정성: 전역적으로 일관된 난이도 관리
        """
        # Given & When - 두 번의 인스턴스 요청
        manager1 = DifficultyManager.get_instance()
        manager2 = DifficultyManager.get_instance()

        # Then - 동일한 인스턴스 반환 확인
        assert manager1 is manager2, '동일한 인스턴스가 반환되어야 함'
        assert id(manager1) == id(manager2), '메모리 주소가 같아야 함'

    def test_초기_상태_및_기본_설정_검증_성공_시나리오(self) -> None:
        """6. 초기 상태 및 기본 설정 검증 (성공 시나리오)

        목적: DifficultyManager의 초기 상태가 올바르게 설정되는지 검증
        테스트할 범위: 초기화 상태 및 기본값
        커버하는 함수 및 데이터: 초기화 상태, get_game_time(), get_current_level()
        기대되는 안정성: 일관된 초기 상태로 예측 가능한 동작
        """
        # Given & When - 난이도 관리자 생성
        manager = DifficultyManager.get_instance()

        # Then - 초기 상태 확인
        assert manager.get_game_time() == 0.0, (
            '게임 시간이 0으로 초기화되어야 함'
        )
        assert manager.get_current_level() == DifficultyLevel.EASY, (
            '초기 난이도가 쉬움으로 설정되어야 함'
        )

        # 초기 배율 확인
        assert manager.get_health_multiplier() == 1.0, (
            '초기 체력 배율이 1.0이어야 함'
        )
        assert manager.get_speed_multiplier() == 1.0, (
            '초기 속도 배율이 1.0이어야 함'
        )
        assert manager.get_spawn_interval_multiplier() == 1.0, (
            '초기 스폰 간격 배율이 1.0이어야 함'
        )

    def test_시간_기반_난이도_레벨_전환_검증_성공_시나리오(self) -> None:
        """7. 시간 기반 난이도 레벨 전환 검증 (성공 시나리오)

        목적: 게임 시간에 따른 난이도 레벨 자동 전환이 올바른지 검증
        테스트할 범위: 시간 기반 난이도 레벨 변경
        커버하는 함수 및 데이터: update(), _update_difficulty_level()
        기대되는 안정성: 정확한 타이밍의 난이도 전환
        """
        # Given - 난이도 관리자
        manager = DifficultyManager.get_instance()

        # When & Then - 쉬움 단계 (0-60초)
        manager.update(30.0)  # 30초
        assert manager.get_current_level() == DifficultyLevel.EASY, (
            '30초에서는 쉬움 단계여야 함'
        )

        # When & Then - 보통 단계 (60-180초)
        manager.update(50.0)  # 총 80초
        assert manager.get_current_level() == DifficultyLevel.NORMAL, (
            '80초에서는 보통 단계여야 함'
        )

        # When & Then - 어려움 단계 (180-360초)
        manager.update(120.0)  # 총 200초
        assert manager.get_current_level() == DifficultyLevel.HARD, (
            '200초에서는 어려움 단계여야 함'
        )

        # When & Then - 극한 단계 (360초+)
        manager.update(200.0)  # 총 400초
        assert manager.get_current_level() == DifficultyLevel.EXTREME, (
            '400초에서는 극한 단계여야 함'
        )

    def test_체력_배율_시간_기반_증가_검증_성공_시나리오(self) -> None:
        """8. 체력 배율 시간 기반 증가 검증 (성공 시나리오)

        목적: 게임 시간에 따른 체력 배율 증가가 올바른지 검증
        테스트할 범위: get_health_multiplier() 메서드
        커버하는 함수 및 데이터: 체력 스케일링 공식 및 최대값 제한
        기대되는 안정성: 점진적 체력 증가로 적절한 도전감 제공
        """
        # Given - 난이도 관리자
        manager = DifficultyManager.get_instance()

        # When - 50초 경과 (2% * 50 = 100% 증가, 총 200%)
        manager.update(50.0)
        health_multiplier_50s = manager.get_health_multiplier()

        # When - 100초 경과 (레벨 변경 + 시간 배율)
        manager.update(50.0)  # 총 100초
        health_multiplier_100s = manager.get_health_multiplier()

        # When - 매우 긴 시간 경과 (최대값 테스트)
        manager.set_game_time(1000.0)  # 1000초로 직접 설정
        health_multiplier_max = manager.get_health_multiplier()

        # Then - 체력 배율 증가 확인
        assert health_multiplier_50s > 1.0, '50초 후 체력 배율이 증가해야 함'
        assert health_multiplier_100s > health_multiplier_50s, (
            '100초 후 체력 배율이 더 증가해야 함'
        )
        assert health_multiplier_max <= 3.0, (
            '최대 체력 배율이 3.0을 초과하지 않아야 함'
        )

        # 정확한 계산 검증 (50초: 기본 1.0 + 시간 배율 1.0 + 50*0.02 = 2.0)
        expected_50s = 1.0 * 2.0  # 쉬움 기본 배수 * (1.0 + 50*0.02)
        assert abs(health_multiplier_50s - expected_50s) < 0.01, (
            f'50초 후 체력 배율이 {expected_50s} 근처여야 함'
        )

    def test_속도_배율_시간_기반_증가_검증_성공_시나리오(self) -> None:
        """9. 속도 배율 시간 기반 증가 검증 (성공 시나리오)

        목적: 게임 시간에 따른 속도 배율 증가가 올바른지 검증
        테스트할 범위: get_speed_multiplier() 메서드
        커버하는 함수 및 데이터: 속도 스케일링 공식 및 최대값 제한
        기대되는 안정성: 점진적 속도 증가로 적절한 도전감 제공
        """
        # Given - 난이도 관리자
        manager = DifficultyManager.get_instance()

        # When - 67초 경과 (1.5% * 67 ≈ 100% 증가)
        manager.update(67.0)
        speed_multiplier_67s = manager.get_speed_multiplier()

        # When - 매우 긴 시간 경과 (최대값 테스트)
        manager.set_game_time(2000.0)  # 2000초로 직접 설정
        speed_multiplier_max = manager.get_speed_multiplier()

        # Then - 속도 배율 증가 확인
        assert speed_multiplier_67s > 1.0, '67초 후 속도 배율이 증가해야 함'
        assert speed_multiplier_max <= 2.5, (
            '최대 속도 배율이 2.5를 초과하지 않아야 함'
        )

        # 정확한 계산 검증 (67초: 기본 1.2 + 시간 배율)
        # 67초는 보통 단계이므로 기본 배수 1.2
        expected_67s = 1.2 * (1.0 + 67 * 0.015)
        assert abs(speed_multiplier_67s - expected_67s) < 0.01, (
            f'67초 후 속도 배율이 {expected_67s} 근처여야 함'
        )

    def test_스폰_간격_배율_시간_기반_감소_검증_성공_시나리오(self) -> None:
        """10. 스폰 간격 배율 시간 기반 감소 검증 (성공 시나리오)

        목적: 게임 시간에 따른 스폰 간격 배율 감소가 올바른지 검증
        테스트할 범위: get_spawn_interval_multiplier() 메서드
        커버하는 함수 및 데이터: 스폰 간격 역배율 계산 및 최소값 제한
        기대되는 안정성: 점진적 스폰 속도 증가로 적절한 도전감 제공
        """
        # Given - 난이도 관리자
        manager = DifficultyManager.get_instance()

        # When - 초기 상태
        initial_multiplier = manager.get_spawn_interval_multiplier()

        # When - 20초 경과
        manager.update(20.0)
        multiplier_20s = manager.get_spawn_interval_multiplier()

        # When - 매우 긴 시간 경과 (최소값 테스트)
        manager.set_game_time(1000.0)
        multiplier_max = manager.get_spawn_interval_multiplier()

        # Then - 스폰 간격 배율 감소 확인 (낮은 값 = 빠른 스폰)
        assert initial_multiplier == 1.0, '초기 스폰 간격 배율이 1.0이어야 함'
        assert multiplier_20s < initial_multiplier, (
            '20초 후 스폰 간격이 단축되어야 함'
        )
        assert multiplier_max >= 0.25, (
            '최소 스폰 간격 배율이 0.25 이상 유지되어야 함'
        )

    def test_난이도_정보_조회_정확성_검증_성공_시나리오(self) -> None:
        """11. 난이도 정보 조회 정확성 검증 (성공 시나리오)

        목적: get_difficulty_info()가 정확한 난이도 정보를 반환하는지 검증
        테스트할 범위: get_difficulty_info() 메서드
        커버하는 함수 및 데이터: 종합 난이도 정보 제공
        기대되는 안정성: UI 및 디버깅을 위한 정확한 정보 제공
        """
        # Given - 난이도 관리자
        manager = DifficultyManager.get_instance()

        # When - 150초 경과 (보통 단계)
        manager.update(150.0)
        difficulty_info = manager.get_difficulty_info()

        # Then - 난이도 정보 검증
        assert 'game_time' in difficulty_info, '게임 시간 정보 포함'
        assert 'difficulty_level' in difficulty_info, '난이도 레벨 정보 포함'
        assert 'health_multiplier' in difficulty_info, '체력 배율 정보 포함'
        assert 'speed_multiplier' in difficulty_info, '속도 배율 정보 포함'
        assert 'spawn_interval_multiplier' in difficulty_info, (
            '스폰 간격 배율 정보 포함'
        )

        assert difficulty_info['game_time'] == 150.0, '정확한 게임 시간'
        assert difficulty_info['difficulty_level'] == '보통', (
            '정확한 난이도 레벨'
        )
        assert isinstance(difficulty_info['health_multiplier'], float), (
            '체력 배율은 float'
        )
        assert isinstance(difficulty_info['speed_multiplier'], float), (
            '속도 배율은 float'
        )

    def test_게임_시간_직접_설정_및_리셋_검증_성공_시나리오(self) -> None:
        """12. 게임 시간 직접 설정 및 리셋 검증 (성공 시나리오)

        목적: 게임 시간 직접 설정과 리셋 기능이 올바르게 동작하는지 검증
        테스트할 범위: set_game_time(), reset() 메서드
        커버하는 함수 및 데이터: 시간 설정 및 초기화 기능
        기대되는 안정성: 테스트 및 디버깅을 위한 유연한 시간 제어
        """
        # Given - 난이도 관리자
        manager = DifficultyManager.get_instance()

        # When - 게임 시간 직접 설정
        manager.set_game_time(300.0)

        # Then - 설정된 시간 확인
        assert manager.get_game_time() == 300.0, (
            '게임 시간이 300초로 설정되어야 함'
        )
        assert manager.get_current_level() == DifficultyLevel.HARD, (
            '300초에서는 어려움 단계여야 함'
        )

        # When - 음수 시간 설정 시도
        manager.set_game_time(-50.0)

        # Then - 음수 시간이 0으로 조정되는지 확인
        assert manager.get_game_time() == 0.0, (
            '음수 시간은 0으로 조정되어야 함'
        )

        # When - 리셋 실행
        manager.update(100.0)  # 시간 진행
        manager.reset()

        # Then - 초기 상태로 복원 확인
        assert manager.get_game_time() == 0.0, '리셋 후 게임 시간이 0이어야 함'
        assert manager.get_current_level() == DifficultyLevel.EASY, (
            '리셋 후 난이도가 쉬움으로 되어야 함'
        )

    def test_커스텀_설정으로_난이도_관리자_생성_검증_성공_시나리오(
        self,
    ) -> None:
        """13. 커스텀 설정으로 난이도 관리자 생성 검증 (성공 시나리오)

        목적: 사용자 정의 설정으로 난이도 관리자가 올바르게 생성되는지 검증
        테스트할 범위: 커스텀 DifficultySettings를 사용한 초기화
        커버하는 함수 및 데이터: __init__() with custom settings
        기대되는 안정성: 사용자 정의 설정으로 유연한 난이도 조정
        """
        # Given - 커스텀 설정
        custom_settings = DifficultySettings(
            easy_duration=30.0,  # 쉬움 30초
            normal_duration=60.0,  # 보통 60초
            hard_duration=90.0,  # 어려움 90초
            health_scale_rate=0.05,  # 5% 증가율
        )

        # When - 커스텀 설정으로 새 인스턴스 생성
        DifficultyManager.reset_instance()
        manager = DifficultyManager(custom_settings)

        # Then - 커스텀 설정 적용 확인
        # 40초에서 보통 단계여야 함 (커스텀 설정에서 쉬움은 30초까지)
        manager.update(40.0)
        assert manager.get_current_level() == DifficultyLevel.NORMAL, (
            '40초에서는 보통 단계여야 함 (커스텀 설정)'
        )

        # 20초에서 더 높은 체력 배율 (5% 증가율)
        manager.set_game_time(20.0)
        health_multiplier = manager.get_health_multiplier()
        expected_multiplier = 1.0 * (1.0 + 20 * 0.05)  # 쉬움 * (1 + 20*5%)
        assert abs(health_multiplier - expected_multiplier) < 0.01, (
            '커스텀 체력 스케일링 비율이 적용되어야 함'
        )
