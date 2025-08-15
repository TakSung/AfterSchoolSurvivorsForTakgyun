"""
Tests for ExperienceUISystem and experience UI rendering system.

This module tests UI rendering functionality, font management,
player experience panel rendering, and system lifecycle management.
"""

import pygame

from src.components.experience_component import ExperienceComponent
from src.components.experience_ui_component import ExperienceUIComponent
from src.components.player_component import PlayerComponent
from src.core.entity_manager import EntityManager
from src.systems.experience_ui_system import ExperienceUISystem


class TestExperienceUISystem:
    def setup_method(self) -> None:
        """각 테스트 메서드 실행 전 설정"""
        # pygame 초기화 (테스트용)
        pygame.init()
        self.test_surface = pygame.Surface((800, 600))
        self.ui_system = ExperienceUISystem(surface=self.test_surface, priority=60)
        self.entity_manager = EntityManager()
        
    def teardown_method(self) -> None:
        """각 테스트 메서드 실행 후 정리"""
        pygame.quit()

    def test_경험치_UI_시스템_초기화_및_설정_검증_성공_시나리오(self) -> None:
        """1. 경험치 UI 시스템 초기화 및 설정 검증 (성공 시나리오)

        목적: ExperienceUISystem의 초기화와 기본 설정이 올바른지 확인
        테스트할 범위: 시스템 초기화, 기본 속성 설정
        커버하는 함수 및 데이터: __init__, initialize, 기본 설정들
        기대되는 안정성: UI 렌더링 시스템의 안정적 초기화 보장
        """
        # Given & When - UI 시스템 초기화
        self.ui_system.initialize()

        # Then - 초기화 상태 확인
        assert self.ui_system.enabled is True
        assert self.ui_system.priority == 60
        assert self.ui_system.get_system_name() == "ExperienceUISystem"
        assert self.ui_system.surface is self.test_surface
        assert isinstance(self.ui_system._fonts, dict)
        assert len(self.ui_system._fonts) == 0  # 초기에는 폰트 없음
        assert self.ui_system._font_cache_limit == 10

    def test_폰트_캐싱_시스템_생성_및_관리_성공_시나리오(self) -> None:
        """2. 폰트 캐싱 시스템 생성 및 관리 (성공 시나리오)

        목적: 폰트 캐싱이 올바르게 동작하고 메모리 효율적인지 확인
        테스트할 범위: _get_font, 폰트 캐시 관리, 캐시 제한
        커버하는 함수 및 데이터: 폰트 생성, 캐시 저장, 제한 처리
        기대되는 안정성: 메모리 효율적인 폰트 관리 보장
        """
        # Given - UI 시스템 초기화
        self.ui_system.initialize()

        # When - 다양한 크기의 폰트 요청
        font_24 = self.ui_system._get_font(24)
        font_16 = self.ui_system._get_font(16)
        font_32 = self.ui_system._get_font(32)

        # Then - 폰트 생성 및 캐시 확인
        assert isinstance(font_24, pygame.font.Font)
        assert isinstance(font_16, pygame.font.Font)
        assert isinstance(font_32, pygame.font.Font)
        assert len(self.ui_system._fonts) == 3

        # When - 같은 크기 폰트 재요청
        font_24_again = self.ui_system._get_font(24)

        # Then - 캐시된 폰트 반환 확인
        assert font_24 is font_24_again
        assert len(self.ui_system._fonts) == 3  # 개수 변화 없음

    def test_폰트_캐시_제한_및_정리_동작_성공_시나리오(self) -> None:
        """3. 폰트 캐시 제한 및 정리 동작 (성공 시나리오)

        목적: 폰트 캐시 제한이 올바르게 작동하는지 확인
        테스트할 범위: 캐시 제한 도달 시 정리 로직
        커버하는 함수 및 데이터: _font_cache_limit 처리, 캐시 정리
        기대되는 안정성: 메모리 누수 방지와 캐시 관리 보장
        """
        # Given - 캐시 제한을 3으로 설정한 UI 시스템
        ui_system = ExperienceUISystem(self.test_surface, priority=50)
        ui_system._font_cache_limit = 3
        ui_system.initialize()

        # When - 제한을 초과하는 폰트 생성
        sizes = [12, 14, 16, 18, 20]  # 5개 (제한 3개 초과)
        for size in sizes:
            ui_system._get_font(size)

        # Then - 캐시 크기 제한 확인
        assert len(ui_system._fonts) <= 3

        # 마지막에 요청한 폰트들이 캐시에 있는지 확인
        assert 20 in ui_system._fonts  # 마지막 요청
        assert 18 in ui_system._fonts
        assert 16 in ui_system._fonts

    def test_경험치_UI_컴포넌트_렌더링_처리_성공_시나리오(self) -> None:
        """4. 경험치 UI 컴포넌트 렌더링 처리 (성공 시나리오)

        목적: ExperienceUIComponent가 있는 엔티티의 렌더링이 올바른지 확인
        테스트할 범위: update 메서드, UI 컴포넌트 찾기, 렌더링 호출
        커버하는 함수 및 데이터: 컴포넌트 검색, 렌더링 파이프라인
        기대되는 안정성: UI 컴포넌트의 정확한 렌더링 처리 보장
        """
        # Given - 경험치와 UI 컴포넌트를 가진 엔티티
        entity = self.entity_manager.create_entity()
        exp_comp = ExperienceComponent(current_exp=150, level=3)
        ui_comp = ExperienceUIComponent(
            ui_position=(100, 100),
            show_level=True,
            show_experience_bar=True
        )

        self.entity_manager.add_component(entity, exp_comp)
        self.entity_manager.add_component(entity, ui_comp)
        self.ui_system.initialize()

        # When - 시스템 업데이트 (렌더링 수행)
        self.ui_system.update(self.entity_manager, 0.016)

        # Then - 시스템이 예외 없이 실행되고 엔티티 매니저가 설정됨
        assert self.ui_system._entity_manager is self.entity_manager

    def test_경험치_컴포넌트_없는_엔티티_안전_처리_성공_시나리오(self) -> None:
        """5. 경험치 컴포넌트 없는 엔티티 안전 처리 (성공 시나리오)

        목적: UI 컴포넌트만 있고 경험치 컴포넌트가 없는 경우의 안전 처리 확인
        테스트할 범위: 컴포넌트 누락 시 예외 처리
        커버하는 함수 및 데이터: None 체크, 안전한 스킵 처리
        기대되는 안정성: 불완전한 엔티티에 대한 안정적 동작 보장
        """
        # Given - UI 컴포넌트만 있는 엔티티 (경험치 컴포넌트 없음)
        entity = self.entity_manager.create_entity()
        ui_comp = ExperienceUIComponent()
        self.entity_manager.add_component(entity, ui_comp)
        self.ui_system.initialize()

        # When - 시스템 업데이트 시도
        # Then - 예외 없이 안전하게 처리되어야 함
        self.ui_system.update(self.entity_manager, 0.016)

    def test_레벨업_애니메이션_트리거_및_업데이트_성공_시나리오(self) -> None:
        """6. 레벨업 애니메이션 트리거 및 업데이트 (성공 시나리오)

        목적: 레벨업 시 애니메이션이 올바르게 트리거되고 업데이트되는지 확인
        테스트할 범위: 레벨 변화 감지, 애니메이션 트리거, 타이머 업데이트
        커버하는 함수 및 데이터: 레벨 비교, 애니메이션 호출
        기대되는 안정성: 레벨업 시각 효과의 정확한 동작 보장
        """
        # Given - 경험치와 UI 컴포넌트를 가진 엔티티
        entity = self.entity_manager.create_entity()
        exp_comp = ExperienceComponent(current_exp=100, level=2)
        ui_comp = ExperienceUIComponent(animate_level_up=True)
        ui_comp.previous_level = 1  # 이전 레벨 설정

        self.entity_manager.add_component(entity, exp_comp)
        self.entity_manager.add_component(entity, ui_comp)
        self.ui_system.initialize()

        # When - 시스템 업데이트 (레벨업 감지)
        self.ui_system.update(self.entity_manager, 0.016)

        # Then - 애니메이션 트리거 확인
        assert ui_comp.is_flashing is True
        assert ui_comp.previous_level == 2  # 새 레벨로 업데이트

        # When - 시간 경과 시뮬레이션
        self.ui_system.update(self.entity_manager, 0.5)

        # Then - 애니메이션 타이머 감소 확인
        assert ui_comp.level_up_flash_timer < 1.0

    def test_플레이어_경험치_패널_렌더링_성공_시나리오(self) -> None:
        """7. 플레이어 경험치 패널 렌더링 (성공 시나리오)

        목적: 플레이어 전용 경험치 패널이 올바르게 렌더링되는지 확인
        테스트할 범위: render_player_experience_panel, 플레이어 찾기
        커버하는 함수 및 데이터: 플레이어 검색, 패널 렌더링
        기대되는 안정성: 플레이어 UI 패널의 안정적 렌더링 보장
        """
        # Given - 플레이어 엔티티 생성
        player_entity = self.entity_manager.create_entity()
        player_comp = PlayerComponent()
        exp_comp = ExperienceComponent(current_exp=250, level=4)

        self.entity_manager.add_component(player_entity, player_comp)
        self.entity_manager.add_component(player_entity, exp_comp)
        self.ui_system.initialize()

        # When - 플레이어 경험치 패널 렌더링
        # Then - 예외 없이 실행되어야 함
        self.ui_system.render_player_experience_panel(
            self.entity_manager,
            position=(50, 50),
            panel_width=400,
            panel_height=150
        )

    def test_플레이어_없는_경우_패널_렌더링_안전_처리_성공_시나리오(self) -> None:
        """8. 플레이어 없는 경우 패널 렌더링 안전 처리 (성공 시나리오)

        목적: 플레이어가 없는 경우 패널 렌더링이 안전하게 처리되는지 확인
        테스트할 범위: 빈 엔티티 매니저에서의 패널 렌더링
        커버하는 함수 및 데이터: 플레이어 검색 실패 시 처리
        기대되는 안정성: 플레이어 부재 시 안전한 동작 보장
        """
        # Given - 플레이어가 없는 엔티티 매니저
        self.ui_system.initialize()

        # When - 플레이어 경험치 패널 렌더링 시도
        # Then - 예외 없이 안전하게 처리되어야 함
        self.ui_system.render_player_experience_panel(self.entity_manager)

    def test_시스템_활성화_비활성화_동작_검증_성공_시나리오(self) -> None:
        """9. 시스템 활성화/비활성화 동작 검증 (성공 시나리오)

        목적: 시스템이 비활성화되었을 때 렌더링이 수행되지 않는지 확인
        테스트할 범위: enabled 플래그, 조건부 실행
        커버하는 함수 및 데이터: enabled 체크, early return
        기대되는 안정성: 시스템 상태에 따른 정확한 동작 제어 보장
        """
        # Given - UI 컴포넌트가 있는 엔티티
        entity = self.entity_manager.create_entity()
        exp_comp = ExperienceComponent()
        ui_comp = ExperienceUIComponent()
        self.entity_manager.add_component(entity, exp_comp)
        self.entity_manager.add_component(entity, ui_comp)

        # When - 시스템 비활성화 후 업데이트
        self.ui_system.disable()
        self.ui_system.update(self.entity_manager, 0.016)

        # Then - 엔티티 매니저가 설정되지 않음 (렌더링 스킵됨)
        assert not hasattr(self.ui_system, '_entity_manager') or \
               self.ui_system._entity_manager is None

        # When - 시스템 활성화 후 업데이트
        self.ui_system.enable()
        self.ui_system.update(self.entity_manager, 0.016)

        # Then - 정상적으로 처리됨
        assert self.ui_system._entity_manager is self.entity_manager

    def test_시스템_정리_및_리소스_해제_성공_시나리오(self) -> None:
        """10. 시스템 정리 및 리소스 해제 (성공 시나리오)

        목적: 시스템 종료 시 리소스가 올바르게 해제되는지 확인
        테스트할 범위: cleanup 메서드, 폰트 캐시 정리
        커버하는 함수 및 데이터: 캐시 클리어, 리소스 해제
        기대되는 안정성: 메모리 누수 방지 및 안전한 종료 보장
        """
        # Given - 폰트가 캐시된 UI 시스템
        self.ui_system.initialize()
        self.ui_system._get_font(24)
        self.ui_system._get_font(16)
        assert len(self.ui_system._fonts) == 2

        # When - 시스템 정리
        self.ui_system.cleanup()

        # Then - 폰트 캐시 정리 확인
        assert len(self.ui_system._fonts) == 0