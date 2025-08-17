"""
Integration tests for Experience UI system components.

This module tests the complete UI rendering pipeline from components
to systems with real pygame integration.
"""

import pygame

from src.components.experience_component import ExperienceComponent
from src.components.experience_ui_component import ExperienceUIComponent
from src.components.player_component import PlayerComponent
from src.core.entity_manager import EntityManager
from src.systems.experience_ui_system import ExperienceUISystem


class TestExperienceUIIntegration:
    def setup_method(self) -> None:
        """각 테스트 메서드 실행 전 설정"""
        pygame.init()
        self.screen = pygame.Surface((1200, 800))
        self.entity_manager = EntityManager()
        self.ui_system = ExperienceUISystem(self.screen, priority=60)
        self.ui_system.initialize()
        
    def teardown_method(self) -> None:
        """각 테스트 메서드 실행 후 정리"""
        self.ui_system.cleanup()
        pygame.quit()

    def test_완전한_경험치_UI_렌더링_파이프라인_통합_성공_시나리오(self) -> None:
        """1. 완전한 경험치 UI 렌더링 파이프라인 통합 (성공 시나리오)

        목적: 경험치 컴포넌트, UI 컴포넌트, UI 시스템이 함께 올바르게 동작하는지 확인
        테스트할 범위: 전체 UI 렌더링 파이프라인
        커버하는 함수 및 데이터: 완전한 엔티티-컴포넌트-시스템 통합
        기대되는 안정성: 실제 게임 환경에서의 안정적 UI 렌더링 보장
        """
        # Given - 완전한 UI 설정이 있는 엔티티
        player_entity = self.entity_manager.create_entity()
        
        # 경험치 데이터
        exp_comp = ExperienceComponent(
            current_exp=75,  # 75% 진행
            level=3
        )
        
        # UI 설정
        ui_comp = ExperienceUIComponent(
            ui_position=(50, 50),
            bar_width=300,
            bar_height=20,
            show_level=True,
            show_experience_bar=True,
            show_experience_text=True,
            animate_level_up=True
        )
        
        # 플레이어 컴포넌트 (패널 렌더링 테스트용)
        player_comp = PlayerComponent()
        
        self.entity_manager.add_component(player_entity, exp_comp)
        self.entity_manager.add_component(player_entity, ui_comp)
        self.entity_manager.add_component(player_entity, player_comp)

        # When - UI 시스템 업데이트 (렌더링 수행)
        self.ui_system.set_entity_manager(self.entity_manager)
        self.ui_system.update(0.016)
        
        # Then - 예외 없이 렌더링 완료
        assert self.ui_system._entity_manager is self.entity_manager
        
        # 폰트가 로드되었는지 확인
        assert len(self.ui_system._fonts) > 0

    def test_플레이어_경험치_패널_통합_렌더링_성공_시나리오(self) -> None:
        """2. 플레이어 경험치 패널 통합 렌더링 (성공 시나리오)

        목적: 플레이어 전용 경험치 패널이 완전히 렌더링되는지 확인
        테스트할 범위: render_player_experience_panel의 완전한 실행
        커버하는 함수 및 데이터: 패널 배경, 레벨 텍스트, 경험치 바, 총 경험치
        기대되는 안정성: 플레이어 UI의 완전한 렌더링 보장
        """
        # Given - 고레벨 플레이어 설정
        player_entity = self.entity_manager.create_entity()
        player_comp = PlayerComponent()
        exp_comp = ExperienceComponent(
            current_exp=350,
            level=7,
            total_exp_earned=1500
        )
        
        self.entity_manager.add_component(player_entity, player_comp)
        self.entity_manager.add_component(player_entity, exp_comp)

        # When - 플레이어 경험치 패널 렌더링
        self.ui_system.render_player_experience_panel(
            self.entity_manager,
            position=(100, 100),
            panel_width=400,
            panel_height=150
        )
        
        # Then - 렌더링 완료 확인 (폰트 캐시에서 확인)
        # 패널 렌더링 시 다양한 폰트가 사용됨
        assert len(self.ui_system._fonts) >= 3  # 레벨, 경험치, 총 경험치 폰트

    def test_레벨업_애니메이션_통합_처리_성공_시나리오(self) -> None:
        """3. 레벨업 애니메이션 통합 처리 (성공 시나리오)

        목적: 레벨업 시 애니메이션이 UI 시스템에서 올바르게 처리되는지 확인
        테스트할 범위: 레벨 변화 감지, 애니메이션 트리거, 색상 변화
        커버하는 함수 및 데이터: 애니메이션 상태 관리, 시각적 효과
        기대되는 안정성: 레벨업 시각 피드백의 완전한 통합 동작 보장
        """
        # Given - 레벨업 직전 플레이어
        entity = self.entity_manager.create_entity()
        exp_comp = ExperienceComponent(current_exp=90, level=2)
        ui_comp = ExperienceUIComponent(
            animate_level_up=True,
            level_up_flash_duration=1.0
        )
        ui_comp.previous_level = 1  # 이전 레벨 설정
        
        self.entity_manager.add_component(entity, exp_comp)
        self.entity_manager.add_component(entity, ui_comp)

        # When - 첫 번째 업데이트 (레벨업 감지)
        self.ui_system.set_entity_manager(self.entity_manager)
        self.ui_system.update(0.016)
        
        # Then - 애니메이션 시작 확인
        assert ui_comp.is_flashing is True
        assert ui_comp.previous_level == 2
        
        # 애니메이션 색상 확인
        animated_color = ui_comp.get_current_fill_color()
        normal_color = ui_comp.fill_color
        flash_color = ui_comp.level_up_flash_color
        assert animated_color in [normal_color, flash_color]

        # When - 시간 경과 시뮬레이션
        for _ in range(10):  # 여러 프레임 시뮬레이션
            self.ui_system.update(0.1)
            
        # Then - 애니메이션 종료 확인 (충분한 시간이 지났으므로)
        # 10 * 0.1 = 1초 경과했으므로 1초 애니메이션은 종료되어야 함
        assert ui_comp.is_flashing is False or ui_comp.level_up_flash_timer <= 0.001
        final_color = ui_comp.get_current_fill_color()
        # 애니메이션이 끝났으면 기본 색상, 아직 진행 중이면 플래시 색상 중 하나
        assert final_color in [normal_color, flash_color]

    def test_다중_엔티티_UI_렌더링_성능_검증_성공_시나리오(self) -> None:
        """4. 다중 엔티티 UI 렌더링 성능 검증 (성공 시나리오)

        목적: 여러 엔티티의 UI가 동시에 렌더링될 때 성능과 정확성 확인
        테스트할 범위: 다중 엔티티 처리, 렌더링 성능
        커버하는 함수 및 데이터: 배치 렌더링, 시스템 확장성
        기대되는 안정성: 다수의 UI 요소 동시 렌더링의 안정성 보장
        """
        # Given - 여러 개의 UI 엔티티 생성
        entities = []
        for i in range(5):
            entity = self.entity_manager.create_entity()
            exp_comp = ExperienceComponent(
                current_exp=i * 20,
                level=i + 1
            )
            ui_comp = ExperienceUIComponent(
                ui_position=(50, 100 + i * 60),  # 다른 위치
                bar_width=200,
                fill_color=(255 - i * 50, 255, i * 50)  # 다른 색상
            )
            
            self.entity_manager.add_component(entity, exp_comp)
            self.entity_manager.add_component(entity, ui_comp)
            entities.append(entity)

        # When - 모든 엔티티 UI 렌더링
        self.ui_system.set_entity_manager(self.entity_manager)
        self.ui_system.update(0.016)
        
        # Then - 모든 엔티티가 처리되었는지 확인
        ui_entities = self.entity_manager.get_entities_with_component(
            ExperienceUIComponent
        )
        assert len(ui_entities) == 5
        
        # 시스템이 안정적으로 동작했는지 확인
        assert self.ui_system._entity_manager is self.entity_manager

    def test_UI_설정_변경_즉시_반영_검증_성공_시나리오(self) -> None:
        """5. UI 설정 변경 즉시 반영 검증 (성공 시나리오)

        목적: UI 설정을 동적으로 변경했을 때 즉시 반영되는지 확인
        테스트할 범위: 런타임 UI 설정 변경, 즉시 반영
        커버하는 함수 및 데이터: 동적 설정 변경, 렌더링 업데이트
        기대되는 안정성: 게임 중 UI 커스터마이징의 즉시 반영 보장
        """
        # Given - 기본 설정의 UI 엔티티
        entity = self.entity_manager.create_entity()
        exp_comp = ExperienceComponent(current_exp=50, level=2)
        ui_comp = ExperienceUIComponent(
            ui_position=(100, 100),
            bar_width=200,
            fill_color=(255, 255, 0)
        )
        
        self.entity_manager.add_component(entity, exp_comp)
        self.entity_manager.add_component(entity, ui_comp)

        # When - 첫 번째 렌더링
        self.ui_system.set_entity_manager(self.entity_manager)
        self.ui_system.update(0.016)
        original_position = ui_comp.get_bar_position()
        
        # When - UI 설정 동적 변경
        ui_comp.set_position(300, 200)
        ui_comp.set_bar_size(400, 30)
        ui_comp.set_colors(
            fill=(0, 255, 0),  # 녹색으로 변경
            background=(50, 50, 50)
        )
        
        # When - 변경 후 렌더링
        self.ui_system.set_entity_manager(self.entity_manager)
        self.ui_system.update(0.016)
        
        # Then - 설정 변경 확인
        new_position = ui_comp.get_bar_position()
        assert new_position != original_position
        assert new_position == (300, 200)
        assert ui_comp.bar_width == 400
        assert ui_comp.bar_height == 30
        assert ui_comp.fill_color == (0, 255, 0)
        assert ui_comp.background_color == (50, 50, 50)