import time
import pytest
from unittest.mock import Mock, patch

from src.core.time_manager import TimeManager, TimeMode


class TestTimeManager:
    def test_시간_관리자_초기화_상태_확인_성공_시나리오(self) -> None:
        """1. 시간 관리자 초기화 상태 확인 (성공 시나리오)
        
        목적: TimeManager 생성자와 초기 상태 설정 검증
        테스트할 범위: __init__, 초기 속성값
        커버하는 함수 및 데이터: time_mode, fixed_timestep, time_scale 등
        기대되는 안정성: 올바른 초기 상태 설정 보장
        """
        # Given & When - 기본 설정으로 TimeManager 생성
        time_manager = TimeManager()
        
        # Then - 초기 상태 확인
        assert time_manager.time_mode == TimeMode.VARIABLE_TIMESTEP, "기본 시간 모드는 가변 시간 간격이어야 함"
        assert time_manager.fixed_timestep == 1.0 / 60.0, "기본 고정 시간 간격은 60 FPS여야 함"
        assert time_manager.time_scale == 1.0, "초기 시간 스케일은 1.0이어야 함"
        assert time_manager.delta_time == 0.0, "초기 델타 시간은 0.0이어야 함"
        assert time_manager.total_game_time == 0.0, "초기 총 게임 시간은 0.0이어야 함"
        assert not time_manager.is_paused, "초기에는 일시정지 상태가 아니어야 함"

    def test_시간_모드_전환_기능_검증_성공_시나리오(self) -> None:
        """2. 시간 모드 전환 기능 검증 (성공 시나리오)
        
        목적: 고정/가변 시간 간격 모드 전환 동작 검증
        테스트할 범위: time_mode 프로퍼티 setter
        커버하는 함수 및 데이터: TimeMode 열거형, 모드 전환 로직
        기대되는 안정성: 모드 전환 시 상태 초기화 보장
        """
        # Given - 가변 시간 간격 모드로 시작
        time_manager = TimeManager(TimeMode.VARIABLE_TIMESTEP)
        time_manager._accumulated_time = 0.5  # 임의 값 설정
        
        # When - 고정 시간 간격 모드로 전환
        time_manager.time_mode = TimeMode.FIXED_TIMESTEP
        
        # Then - 모드 전환 확인
        assert time_manager.time_mode == TimeMode.FIXED_TIMESTEP, "고정 시간 간격 모드로 전환되어야 함"
        assert time_manager._accumulated_time == 0.0, "모드 전환 시 누적 시간이 초기화되어야 함"
        
        # When - 다시 가변 시간 간격 모드로 전환
        time_manager.time_mode = TimeMode.VARIABLE_TIMESTEP
        
        # Then - 모드 전환 확인
        assert time_manager.time_mode == TimeMode.VARIABLE_TIMESTEP, "가변 시간 간격 모드로 전환되어야 함"

    def test_시간_스케일링_기능_검증_성공_시나리오(self) -> None:
        """3. 시간 스케일링 기능 검증 (성공 시나리오)
        
        목적: 일시정지, 슬로우모션, 시간 스케일 조정 기능 검증
        테스트할 범위: pause, resume, set_slow_motion, reset_time_scale
        커버하는 함수 및 데이터: time_scale 프로퍼티, 시간 스케일링 메서드들
        기대되는 안정성: 시간 스케일 조정의 정확한 동작 보장
        """
        # Given - TimeManager 생성
        time_manager = TimeManager()
        
        # When & Then - 일시정지
        time_manager.pause()
        assert time_manager.time_scale == 0.0, "일시정지 시 time_scale은 0.0이어야 함"
        assert time_manager.is_paused, "일시정지 상태여야 함"
        
        # When & Then - 재개
        time_manager.resume()
        assert time_manager.time_scale == 1.0, "재개 시 time_scale은 1.0이어야 함"
        assert not time_manager.is_paused, "재개 후 일시정지 상태가 아니어야 함"
        
        # When & Then - 슬로우모션
        time_manager.set_slow_motion(0.5)
        assert time_manager.time_scale == 0.5, "슬로우모션 시 time_scale은 0.5여야 함"
        
        # When & Then - 시간 스케일 리셋
        time_manager.reset_time_scale()
        assert time_manager.time_scale == 1.0, "리셋 후 time_scale은 1.0이어야 함"

    def test_고정_시간_간격_모드_업데이트_검증_성공_시나리오(self) -> None:
        """4. 고정 시간 간격 모드 업데이트 검증 (성공 시나리오)
        
        목적: 고정 timestep 모드에서의 업데이트 로직 검증
        테스트할 범위: _update_fixed_timestep, update 메서드
        커버하는 함수 및 데이터: 누적 시간 관리, 다중 업데이트 처리
        기대되는 안정성: 일정한 시간 간격으로 업데이트 호출 보장
        """
        # Given - 고정 시간 간격 모드 TimeManager
        fixed_timestep = 1.0 / 30.0  # 30 FPS
        time_manager = TimeManager(
            time_mode=TimeMode.FIXED_TIMESTEP,
            fixed_timestep=fixed_timestep
        )
        
        update_callback = Mock()
        time_manager.add_update_callback(update_callback)
        
        # When - 고정 timestep보다 작은 시간으로 업데이트
        small_delta = fixed_timestep * 0.5
        update_count = time_manager.update(small_delta)
        
        # Then - 업데이트가 호출되지 않음
        assert update_count == 0, "고정 timestep 미만 시간에서는 업데이트가 호출되지 않아야 함"
        update_callback.assert_not_called()
        
        # When - 고정 timestep과 같은 시간으로 업데이트
        update_count = time_manager.update(fixed_timestep)
        
        # Then - 한 번 업데이트 호출
        assert update_count == 1, "고정 timestep 시간에서는 한 번 업데이트가 호출되어야 함"
        update_callback.assert_called_once_with(fixed_timestep)
        
        # When - 고정 timestep의 2.5배 시간으로 업데이트
        update_callback.reset_mock()
        large_delta = fixed_timestep * 2.5
        update_count = time_manager.update(large_delta)
        
        # Then - 두 번 업데이트 호출
        assert update_count == 2, "2.5배 시간에서는 두 번 업데이트가 호출되어야 함"
        assert update_callback.call_count == 2, "콜백이 두 번 호출되어야 함"

    def test_가변_시간_간격_모드_업데이트_검증_성공_시나리오(self) -> None:
        """5. 가변 시간 간격 모드 업데이트 검증 (성공 시나리오)
        
        목적: 가변 timestep 모드에서의 업데이트 로직 검증
        테스트할 범위: _update_variable_timestep, update 메서드
        커버하는 함수 및 데이터: 실시간 델타 시간 처리
        기대되는 안정성: 실제 프레임 시간을 그대로 사용하는 업데이트 보장
        """
        # Given - 가변 시간 간격 모드 TimeManager
        time_manager = TimeManager(time_mode=TimeMode.VARIABLE_TIMESTEP)
        
        update_callback = Mock()
        time_manager.add_update_callback(update_callback)
        
        # When - 다양한 델타 시간으로 업데이트
        test_deltas = [0.016, 0.033, 0.008, 0.041]  # 다양한 프레임 시간
        
        for delta in test_deltas:
            time_manager.update(delta)
        
        # Then - 각 델타 시간으로 콜백 호출 확인
        assert update_callback.call_count == len(test_deltas), "각 업데이트마다 콜백이 호출되어야 함"
        
        # 마지막 델타 시간이 현재 델타 시간과 일치
        assert time_manager.delta_time == test_deltas[-1], "마지막 델타 시간이 저장되어야 함"

    def test_시간_스케일_적용_업데이트_검증_성공_시나리오(self) -> None:
        """6. 시간 스케일 적용 업데이트 검증 (성공 시나리오)
        
        목적: 시간 스케일이 적용된 상태에서의 업데이트 동작 검증
        테스트할 범위: 스케일된 시간을 사용한 업데이트
        커버하는 함수 및 데이터: time_scale 적용된 델타 시간 계산
        기대되는 안정성: 시간 스케일에 따른 정확한 시간 계산 보장
        """
        # Given - 가변 시간 간격 모드 TimeManager (max_frame_time을 크게 설정)
        time_manager = TimeManager(max_frame_time=1.0)
        
        update_callback = Mock()
        time_manager.add_update_callback(update_callback)
        
        raw_delta = 0.1
        
        # When - 정상 속도 (1.0x)
        time_manager.time_scale = 1.0
        time_manager.update(raw_delta)
        
        # Then - 원본 델타 시간으로 호출
        update_callback.assert_called_with(raw_delta * 1.0)
        assert time_manager.delta_time == raw_delta * 1.0, "정상 속도에서 델타 시간이 정확해야 함"
        
        # When - 슬로우모션 (0.5x)
        update_callback.reset_mock()
        time_manager.time_scale = 0.5
        time_manager.update(raw_delta)
        
        # Then - 절반 속도로 호출
        update_callback.assert_called_with(raw_delta * 0.5)
        assert time_manager.delta_time == raw_delta * 0.5, "슬로우모션에서 델타 시간이 절반이어야 함"
        
        # When - 일시정지 (0.0x)
        update_callback.reset_mock()
        time_manager.pause()
        time_manager.update(raw_delta)
        
        # Then - 0으로 호출
        update_callback.assert_called_with(0.0)
        assert time_manager.delta_time == 0.0, "일시정지에서 델타 시간이 0이어야 함"

    def test_콜백_관리_기능_검증_성공_시나리오(self) -> None:
        """7. 콜백 관리 기능 검증 (성공 시나리오)
        
        목적: 업데이트 콜백 추가/제거/클리어 기능 검증
        테스트할 범위: add_update_callback, remove_update_callback, clear_update_callbacks
        커버하는 함수 및 데이터: 콜백 리스트 관리
        기대되는 안정성: 콜백 등록/해제의 정확한 동작 보장
        """
        # Given - TimeManager와 콜백 함수들 (max_frame_time을 크게 설정)
        time_manager = TimeManager(max_frame_time=1.0)
        
        callback1 = Mock()
        callback2 = Mock()
        callback3 = Mock()
        
        # When - 콜백 추가
        time_manager.add_update_callback(callback1)
        time_manager.add_update_callback(callback2)
        time_manager.add_update_callback(callback3)
        
        # Then - 콜백 개수 확인
        stats = time_manager.get_time_stats()
        assert stats['update_callbacks_count'] == 3, "3개의 콜백이 등록되어야 함"
        
        # When - 업데이트 호출
        time_manager.update(0.1)
        
        # Then - 모든 콜백 호출 확인
        callback1.assert_called_once_with(0.1)
        callback2.assert_called_once_with(0.1)
        callback3.assert_called_once_with(0.1)
        
        # When - 특정 콜백 제거
        time_manager.remove_update_callback(callback2)
        
        # Then - 콜백 개수 변경 확인
        stats = time_manager.get_time_stats()
        assert stats['update_callbacks_count'] == 2, "콜백 제거 후 2개여야 함"
        
        # When - 모든 콜백 클리어
        time_manager.clear_update_callbacks()
        
        # Then - 콜백 개수 0 확인
        stats = time_manager.get_time_stats()
        assert stats['update_callbacks_count'] == 0, "모든 콜백이 클리어되어야 함"

    def test_보간_인자_계산_기능_검증_성공_시나리오(self) -> None:
        """8. 보간 인자 계산 기능 검증 (성공 시나리오)
        
        목적: 고정 timestep 모드에서의 보간 인자 계산 검증
        테스트할 범위: get_interpolation_factor 메서드
        커버하는 함수 및 데이터: 누적 시간 기반 보간값 계산
        기대되는 안정성: 렌더링 보간을 위한 정확한 인자 제공 보장
        """
        # Given - 고정 시간 간격 모드 TimeManager
        fixed_timestep = 1.0 / 30.0
        time_manager = TimeManager(
            time_mode=TimeMode.FIXED_TIMESTEP,
            fixed_timestep=fixed_timestep
        )
        
        # When - timestep의 절반만큼 업데이트
        half_step = fixed_timestep * 0.5
        time_manager.update(half_step)
        
        # Then - 보간 인자 0.5
        interpolation_factor = time_manager.get_interpolation_factor()
        assert abs(interpolation_factor - 0.5) < 0.001, "보간 인자가 0.5여야 함"
        
        # When - 추가로 timestep의 1/4만큼 업데이트
        quarter_step = fixed_timestep * 0.25
        time_manager.update(quarter_step)
        
        # Then - 보간 인자 0.75
        interpolation_factor = time_manager.get_interpolation_factor()
        assert abs(interpolation_factor - 0.75) < 0.001, "보간 인자가 0.75여야 함"
        
        # When - 가변 시간 간격 모드로 전환
        time_manager.time_mode = TimeMode.VARIABLE_TIMESTEP
        
        # Then - 보간 인자 0.0
        interpolation_factor = time_manager.get_interpolation_factor()
        assert interpolation_factor == 0.0, "가변 모드에서 보간 인자는 0.0이어야 함"

    def test_최대_프레임_시간_제한_검증_성공_시나리오(self) -> None:
        """9. 최대 프레임 시간 제한 검증 (성공 시나리오)
        
        목적: 과도하게 긴 프레임 시간 제한 기능 검증
        테스트할 범위: max_frame_time 제한 로직
        커버하는 함수 및 데이터: 프레임 시간 클램핑
        기대되는 안정성: 프레임 드롭 시에도 안정적인 시간 처리 보장
        """
        # Given - 최대 프레임 시간 0.05초로 제한
        max_frame_time = 0.05  # 20 FPS 제한
        time_manager = TimeManager(max_frame_time=max_frame_time)
        
        update_callback = Mock()
        time_manager.add_update_callback(update_callback)
        
        # When - 매우 긴 프레임 시간으로 업데이트
        very_long_delta = 0.5  # 500ms (2 FPS)
        time_manager.update(very_long_delta)
        
        # Then - 최대 프레임 시간으로 제한됨
        update_callback.assert_called_with(max_frame_time)
        assert time_manager.delta_time == max_frame_time, "델타 시간이 최대값으로 제한되어야 함"

    def test_시간_통계_정보_제공_정확성_검증_성공_시나리오(self) -> None:
        """10. 시간 통계 정보 제공 정확성 검증 (성공 시나리오)
        
        목적: get_time_stats 메서드의 정확한 통계 정보 제공 검증
        테스트할 범위: get_time_stats 메서드
        커버하는 함수 및 데이터: 모든 시간 관련 통계
        기대되는 안정성: 완전하고 정확한 시간 통계 데이터 제공 보장
        """
        # Given - 설정된 TimeManager
        time_manager = TimeManager(
            time_mode=TimeMode.FIXED_TIMESTEP,
            fixed_timestep=1.0 / 40.0
        )
        time_manager.time_scale = 0.8
        time_manager._total_game_time = 5.0
        time_manager._delta_time = 0.02
        time_manager._accumulated_time = 0.01
        
        callback1 = Mock()
        callback2 = Mock()
        time_manager.add_update_callback(callback1)
        time_manager.add_update_callback(callback2)
        
        # When - 시간 통계 조회
        stats = time_manager.get_time_stats()
        
        # Then - 통계 정보 확인
        assert stats['time_mode'] == "고정 시간 간격", "시간 모드 표시명이 정확해야 함"
        assert stats['time_scale'] == 0.8, "시간 스케일이 정확해야 함"
        assert stats['delta_time'] == 0.02, "델타 시간이 정확해야 함"
        assert stats['total_game_time'] == 5.0, "총 게임 시간이 정확해야 함"
        assert stats['fixed_timestep'] == 1.0 / 40.0, "고정 timestep이 정확해야 함"
        assert stats['accumulated_time'] == 0.01, "누적 시간이 정확해야 함"
        assert stats['update_callbacks_count'] == 2, "콜백 개수가 정확해야 함"
        assert not stats['is_paused'], "일시정지 상태가 정확해야 함"
        
        # unscaled_delta_time 계산 확인
        expected_unscaled = 0.02 / 0.8
        assert abs(stats['unscaled_delta_time'] - expected_unscaled) < 0.001, "스케일되지 않은 델타 시간이 정확해야 함"

    def test_시간_열거형_표시명_정확성_검증_성공_시나리오(self) -> None:
        """11. 시간 열거형 표시명 정확성 검증 (성공 시나리오)
        
        목적: TimeMode 열거형의 표시명 기능 검증
        테스트할 범위: TimeMode.display_name 프로퍼티
        커버하는 함수 및 데이터: 한국어 모드 표시명
        기대되는 안정성: 일관된 모드 표시명 제공 보장
        """
        # When & Then - 각 모드별 표시명 확인
        assert TimeMode.FIXED_TIMESTEP.display_name == "고정 시간 간격", "고정 timestep 표시명이 정확해야 함"
        assert TimeMode.VARIABLE_TIMESTEP.display_name == "가변 시간 간격", "가변 timestep 표시명이 정확해야 함"

    def test_시간_관리자_리셋_기능_검증_성공_시나리오(self) -> None:
        """12. 시간 관리자 리셋 기능 검증 (성공 시나리오)
        
        목적: reset 메서드의 상태 초기화 기능 검증
        테스트할 범위: reset 메서드
        커버하는 함수 및 데이터: 모든 시간 관련 상태 초기화
        기대되는 안정성: 완전한 상태 초기화 보장
        """
        # Given - 상태가 변경된 TimeManager
        time_manager = TimeManager()
        time_manager._delta_time = 0.5
        time_manager._accumulated_time = 0.3
        time_manager._total_game_time = 10.0
        time_manager.time_scale = 0.6
        
        # When - 리셋 수행
        time_manager.reset()
        
        # Then - 상태 초기화 확인
        assert time_manager.delta_time == 0.0, "델타 시간이 초기화되어야 함"
        assert time_manager._accumulated_time == 0.0, "누적 시간이 초기화되어야 함"
        assert time_manager.total_game_time == 0.0, "총 게임 시간이 초기화되어야 함"
        assert time_manager.time_scale == 1.0, "시간 스케일이 초기화되어야 함"