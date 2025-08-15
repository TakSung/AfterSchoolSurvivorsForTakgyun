"""
Tests for ExperienceUIComponent and experience UI rendering functionality.

This module tests UI configuration, animation effects, layout management,
and visual customization for experience display components.
"""

import pytest

from src.components.experience_ui_component import ExperienceUIComponent


class TestExperienceUIComponent:
    def test_경험치_UI_컴포넌트_초기화_기본_설정_검증_성공_시나리오(self) -> None:
        """1. 경험치 UI 컴포넌트 초기화 및 기본 설정 검증 (성공 시나리오)

        목적: ExperienceUIComponent의 초기화와 기본 설정이 올바른지 확인
        테스트할 범위: 컴포넌트 초기 상태, 기본 설정값들
        커버하는 함수 및 데이터: __init__, 기본 속성값들
        기대되는 안정성: UI 컴포넌트의 일관된 기본 설정 보장
        """
        # Given & When - UI 컴포넌트 기본 생성
        ui_comp = ExperienceUIComponent()

        # Then - 기본 설정 확인
        # 표시 옵션
        assert ui_comp.show_level is True
        assert ui_comp.show_experience_bar is True
        assert ui_comp.show_experience_text is True
        assert ui_comp.show_progress_percentage is False

        # 레이아웃 설정
        assert ui_comp.ui_position == (20, 20)
        assert ui_comp.bar_width == 280
        assert ui_comp.bar_height == 16
        assert ui_comp.level_text_offset == (0, -30)
        assert ui_comp.exp_text_offset == (2, 2)

        # 색상 설정
        assert ui_comp.background_color == (80, 80, 80)
        assert ui_comp.fill_color == (255, 255, 0)  # Yellow
        assert ui_comp.border_color == (255, 255, 255)  # White
        assert ui_comp.text_color == (255, 255, 255)  # White

        # 폰트 설정
        assert ui_comp.level_font_size == 24
        assert ui_comp.exp_text_font_size == 16

        # 애니메이션 설정
        assert ui_comp.animate_level_up is True
        assert ui_comp.level_up_flash_duration == 1.0

    def test_사용자_정의_설정_초기화_및_설정_적용_성공_시나리오(self) -> None:
        """2. 사용자 정의 설정 초기화 및 설정 적용 (성공 시나리오)

        목적: 커스텀 설정으로 UI 컴포넌트를 생성할 수 있는지 확인
        테스트할 범위: 사용자 정의 초기화 매개변수 처리
        커버하는 함수 및 데이터: __init__ 커스텀 매개변수들
        기대되는 안정성: 다양한 UI 스타일 설정의 유연성 보장
        """
        # Given & When - 커스텀 설정으로 UI 컴포넌트 생성
        ui_comp = ExperienceUIComponent(
            show_progress_percentage=True,
            ui_position=(50, 100),
            bar_width=400,
            bar_height=24,
            fill_color=(0, 255, 0),  # Green
            level_font_size=32,
            animate_level_up=False
        )

        # Then - 커스텀 설정 적용 확인
        assert ui_comp.show_progress_percentage is True
        assert ui_comp.ui_position == (50, 100)
        assert ui_comp.bar_width == 400
        assert ui_comp.bar_height == 24
        assert ui_comp.fill_color == (0, 255, 0)
        assert ui_comp.level_font_size == 32
        assert ui_comp.animate_level_up is False

    def test_레벨업_애니메이션_트리거_및_상태_관리_성공_시나리오(self) -> None:
        """3. 레벨업 애니메이션 트리거 및 상태 관리 (성공 시나리오)

        목적: 레벨업 애니메이션이 올바르게 트리거되고 관리되는지 확인
        테스트할 범위: trigger_level_up_animation, 애니메이션 상태 변화
        커버하는 함수 및 데이터: 애니메이션 트리거, 상태 플래그, 타이머
        기대되는 안정성: 레벨업 시 시각적 피드백의 정확한 동작 보장
        """
        # Given - 애니메이션이 활성화된 UI 컴포넌트
        ui_comp = ExperienceUIComponent(
            animate_level_up=True,
            level_up_flash_duration=2.0
        )
        
        # 초기 상태 확인
        assert ui_comp.is_flashing is False
        assert ui_comp.level_up_flash_timer == 0.0
        assert ui_comp.previous_level == 1

        # When - 레벨업 애니메이션 트리거 (2레벨로)
        ui_comp.trigger_level_up_animation(2)

        # Then - 애니메이션 상태 확인
        assert ui_comp.is_flashing is True
        assert ui_comp.level_up_flash_timer == 2.0
        assert ui_comp.previous_level == 2

        # When - 같은 레벨로 다시 트리거 시도 (효과 없어야 함)
        ui_comp.level_up_flash_timer = 1.0  # 시간 경과 시뮬레이션
        ui_comp.trigger_level_up_animation(2)

        # Then - 상태 변화 없음 확인
        assert ui_comp.level_up_flash_timer == 1.0  # 변경되지 않음

    def test_애니메이션_업데이트_및_타이머_관리_성공_시나리오(self) -> None:
        """4. 애니메이션 업데이트 및 타이머 관리 (성공 시나리오)

        목적: 애니메이션 타이머가 올바르게 업데이트되고 종료되는지 확인
        테스트할 범위: update_animation, 타이머 감소, 애니메이션 종료
        커버하는 함수 및 데이터: 델타 타임 처리, 플래시 종료 조건
        기대되는 안정성: 애니메이션의 정확한 시간 관리와 종료 보장
        """
        # Given - 활성 애니메이션이 있는 UI 컴포넌트
        ui_comp = ExperienceUIComponent(level_up_flash_duration=1.0)
        ui_comp.trigger_level_up_animation(3)
        
        assert ui_comp.is_flashing is True
        assert ui_comp.level_up_flash_timer == 1.0

        # When - 시간 경과 시뮬레이션 (0.3초)
        ui_comp.update_animation(0.3)

        # Then - 타이머 감소 확인
        assert ui_comp.is_flashing is True
        assert ui_comp.level_up_flash_timer == pytest.approx(0.7, abs=0.01)

        # When - 애니메이션 완료 시뮬레이션
        ui_comp.update_animation(0.8)  # 총 1.1초 경과

        # Then - 애니메이션 종료 확인
        assert ui_comp.is_flashing is False
        assert ui_comp.level_up_flash_timer == 0.0

    def test_현재_채우기_색상_애니메이션_효과_반영_성공_시나리오(self) -> None:
        """5. 현재 채우기 색상 애니메이션 효과 반영 (성공 시나리오)

        목적: 애니메이션 상태에 따른 색상 변화가 올바른지 확인
        테스트할 범위: get_current_fill_color, 플래시 효과 색상 변경
        커버하는 함수 및 데이터: 플래시 색상 전환, 기본 색상 복구
        기대되는 안정성: 애니메이션 효과의 시각적 일관성 보장
        """
        # Given - 특정 색상 설정이 있는 UI 컴포넌트
        ui_comp = ExperienceUIComponent(
            fill_color=(255, 255, 0),  # Yellow
            level_up_flash_color=(255, 100, 100)  # Red
        )

        # When - 일반 상태에서 색상 확인
        normal_color = ui_comp.get_current_fill_color()

        # Then - 기본 색상 반환 확인
        assert normal_color == (255, 255, 0)

        # When - 애니메이션 활성화 후 색상 확인
        ui_comp.trigger_level_up_animation(5)
        flash_color = ui_comp.get_current_fill_color()

        # Then - 플래시 색상 또는 기본 색상 반환 (플래시 패턴에 따라)
        assert flash_color in [(255, 255, 0), (255, 100, 100)]

        # When - 애니메이션 종료 후 색상 확인
        ui_comp.update_animation(1.5)  # 애니메이션 완료
        final_color = ui_comp.get_current_fill_color()

        # Then - 기본 색상으로 복구 확인
        assert final_color == (255, 255, 0)

    def test_위치_계산_및_레이아웃_좌표_정확성_성공_시나리오(self) -> None:
        """6. 위치 계산 및 레이아웃 좌표 정확성 (성공 시나리오)

        목적: UI 요소들의 위치 계산이 올바르게 수행되는지 확인
        테스트할 범위: get_*_position 메서드들, 상대 위치 계산
        커버하는 함수 및 데이터: 텍스트 위치, 바 위치, 오프셋 계산
        기대되는 안정성: UI 레이아웃의 정확한 위치 배치 보장
        """
        # Given - 특정 위치와 오프셋을 가진 UI 컴포넌트
        ui_comp = ExperienceUIComponent(
            ui_position=(100, 200),
            level_text_offset=(10, -40),
            exp_text_offset=(5, 3)
        )

        # When - 각 요소의 위치 계산
        level_pos = ui_comp.get_level_text_position()
        bar_pos = ui_comp.get_bar_position()
        exp_text_pos = ui_comp.get_exp_text_position()

        # Then - 정확한 위치 계산 확인
        assert level_pos == (110, 160)  # (100+10, 200-40)
        assert bar_pos == (100, 200)    # ui_position 그대로
        assert exp_text_pos == (105, 203)  # (100+5, 200+3)

    def test_UI_설정_메서드_동적_변경_기능_성공_시나리오(self) -> None:
        """7. UI 설정 메서드 동적 변경 기능 (성공 시나리오)

        목적: 런타임에서 UI 설정을 동적으로 변경할 수 있는지 확인
        테스트할 범위: set_position, set_bar_size, set_colors
        커버하는 함수 및 데이터: 동적 설정 변경, 즉시 반영
        기대되는 안정성: 게임 중 UI 설정 변경의 유연성 보장
        """
        # Given - 기본 설정의 UI 컴포넌트
        ui_comp = ExperienceUIComponent()

        # When - 위치 변경
        ui_comp.set_position(300, 400)

        # Then - 위치 변경 확인
        assert ui_comp.ui_position == (300, 400)
        assert ui_comp.get_bar_position() == (300, 400)

        # When - 바 크기 변경
        ui_comp.set_bar_size(500, 30)

        # Then - 크기 변경 확인
        assert ui_comp.bar_width == 500
        assert ui_comp.bar_height == 30

        # When - 색상 설정 변경 (일부만)
        ui_comp.set_colors(
            background=(100, 100, 100),
            fill=(0, 255, 255)  # Cyan
        )

        # Then - 색상 변경 확인
        assert ui_comp.background_color == (100, 100, 100)
        assert ui_comp.fill_color == (0, 255, 255)
        # 변경하지 않은 색상은 기본값 유지
        assert ui_comp.border_color == (255, 255, 255)
        assert ui_comp.text_color == (255, 255, 255)

    def test_색상_설정_부분_업데이트_및_None_처리_성공_시나리오(self) -> None:
        """8. 색상 설정 부분 업데이트 및 None 처리 (성공 시나리오)

        목적: set_colors 메서드가 None 값을 올바르게 처리하는지 확인
        테스트할 범위: set_colors의 옵션 매개변수 처리
        커버하는 함수 및 데이터: None 체크, 부분 업데이트
        기대되는 안정성: 안전한 색상 설정 업데이트 보장
        """
        # Given - 초기 색상을 가진 UI 컴포넌트
        ui_comp = ExperienceUIComponent(
            background_color=(50, 50, 50),
            fill_color=(255, 0, 0),
            border_color=(0, 255, 0),
            text_color=(0, 0, 255)
        )

        original_background = ui_comp.background_color
        original_border = ui_comp.border_color

        # When - 일부 색상만 업데이트 (None 포함)
        ui_comp.set_colors(
            background=None,  # 변경하지 않음
            fill=(255, 255, 255),  # 흰색으로 변경
            border=None,  # 변경하지 않음
            text=(128, 128, 128)  # 회색으로 변경
        )

        # Then - 부분 업데이트 확인
        assert ui_comp.background_color == original_background  # 변경 안됨
        assert ui_comp.fill_color == (255, 255, 255)  # 변경됨
        assert ui_comp.border_color == original_border  # 변경 안됨
        assert ui_comp.text_color == (128, 128, 128)  # 변경됨

    def test_애니메이션_비활성화_모드_동작_검증_성공_시나리오(self) -> None:
        """9. 애니메이션 비활성화 모드 동작 검증 (성공 시나리오)

        목적: 애니메이션이 비활성화된 상태에서 올바르게 동작하는지 확인
        테스트할 범위: animate_level_up=False일 때의 동작
        커버하는 함수 및 데이터: 애니메이션 비활성화 처리
        기대되는 안정성: 애니메이션 없는 UI 모드의 안정적 동작 보장
        """
        # Given - 애니메이션이 비활성화된 UI 컴포넌트
        ui_comp = ExperienceUIComponent(animate_level_up=False)

        # When - 레벨업 트리거 시도
        ui_comp.trigger_level_up_animation(10)

        # Then - 애니메이션이 활성화되지 않음 확인
        assert ui_comp.is_flashing is False
        assert ui_comp.level_up_flash_timer == 0.0

        # When - 색상 확인
        color = ui_comp.get_current_fill_color()

        # Then - 기본 색상만 반환됨 확인
        assert color == ui_comp.fill_color  # 플래시 효과 없음