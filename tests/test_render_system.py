from unittest.mock import Mock, patch

import pygame

from src.systems.render_system import (
    LayeredSpriteGroup,
    RenderableSprite,
    RenderLayer,
    RenderSystem,
)
from src.utils.vector2 import Vector2


class TestRenderLayer:
    def test_렌더링_레이어_열거형_표시명_정확성_검증_성공_시나리오(
        self,
    ) -> None:
        """1. 렌더링 레이어 열거형 표시명 정확성 검증 (성공 시나리오)

        목적: RenderLayer 열거형의 표시명 기능 검증
        테스트할 범위: RenderLayer.display_name 프로퍼티
        커버하는 함수 및 데이터: 한국어 레이어 표시명
        기대되는 안정성: 일관된 레이어 표시명 제공 보장
        """
        # When & Then - 각 레이어별 표시명 확인
        assert RenderLayer.BACKGROUND.display_name == '배경', (
            'BACKGROUND 표시명이 정확해야 함'
        )
        assert RenderLayer.GROUND.display_name == '지면', (
            'GROUND 표시명이 정확해야 함'
        )
        assert RenderLayer.ENTITIES.display_name == '엔티티', (
            'ENTITIES 표시명이 정확해야 함'
        )
        assert RenderLayer.PROJECTILES.display_name == '발사체', (
            'PROJECTILES 표시명이 정확해야 함'
        )
        assert RenderLayer.EFFECTS.display_name == '이펙트', (
            'EFFECTS 표시명이 정확해야 함'
        )
        assert RenderLayer.UI.display_name == 'UI', 'UI 표시명이 정확해야 함'


class TestRenderableSprite:
    def setUp(self) -> None:
        pygame.init()

    def test_렌더링_가능_스프라이트_초기화_상태_확인_성공_시나리오(
        self,
    ) -> None:
        """2. 렌더링 가능 스프라이트 초기화 상태 확인 (성공 시나리오)

        목적: RenderableSprite 생성자와 초기 상태 설정 검증
        테스트할 범위: __init__, 초기 속성값
        커버하는 함수 및 데이터: layer, world_position 등
        기대되는 안정성: 올바른 초기 상태 설정 보장
        """
        pygame.init()

        # Given & When - 기본 설정으로 RenderableSprite 생성
        sprite = RenderableSprite()

        # Then - 초기 상태 확인
        assert sprite.layer == RenderLayer.ENTITIES, (
            '기본 레이어는 ENTITIES여야 함'
        )
        assert sprite.world_position == Vector2(), (
            '초기 월드 위치는 (0,0)이어야 함'
        )
        assert sprite.image is not None, '이미지가 설정되어야 함'
        assert sprite.rect is not None, '렉트가 설정되어야 함'

        # Given & When - 특정 레이어로 스프라이트 생성
        ui_sprite = RenderableSprite(RenderLayer.UI)

        # Then - 레이어 확인
        assert ui_sprite.layer == RenderLayer.UI, (
            '지정한 레이어로 설정되어야 함'
        )

    def test_스프라이트_레이어_속성_설정_검증_성공_시나리오(self) -> None:
        """3. 스프라이트 레이어 속성 설정 검증 (성공 시나리오)

        목적: 스프라이트 레이어 변경 기능 검증
        테스트할 범위: layer 프로퍼티 setter
        커버하는 함수 및 데이터: 레이어 변경 로직
        기대되는 안정성: 올바른 레이어 변경 보장
        """
        pygame.init()

        # Given - 스프라이트 생성
        sprite = RenderableSprite(RenderLayer.ENTITIES)

        # When - 레이어 변경
        sprite.layer = RenderLayer.BACKGROUND

        # Then - 레이어 변경 확인
        assert sprite.layer == RenderLayer.BACKGROUND, '레이어가 변경되어야 함'

    def test_스프라이트_월드_위치_설정_검증_성공_시나리오(self) -> None:
        """4. 스프라이트 월드 위치 설정 검증 (성공 시나리오)

        목적: 스프라이트 월드 위치 변경 기능 검증
        테스트할 범위: world_position 프로퍼티
        커버하는 함수 및 데이터: 위치 설정 로직
        기대되는 안정성: 올바른 위치 설정 보장
        """
        pygame.init()

        # Given - 스프라이트 생성
        sprite = RenderableSprite()

        # When - 월드 위치 설정
        new_position = Vector2(100, 200)
        sprite.world_position = new_position

        # Then - 위치 설정 확인
        assert sprite.world_position == new_position, (
            '월드 위치가 설정되어야 함'
        )

    def test_스프라이트_화면_위치_업데이트_검증_성공_시나리오(self) -> None:
        """5. 스프라이트 화면 위치 업데이트 검증 (성공 시나리오)

        목적: 화면 좌표 업데이트 기능 검증
        테스트할 범위: update_screen_position 메서드
        커버하는 함수 및 데이터: 화면 위치 업데이트 로직
        기대되는 안정성: 올바른 화면 위치 설정 보장
        """
        pygame.init()

        # Given - 스프라이트 생성
        sprite = RenderableSprite()

        # When - 화면 위치 업데이트
        screen_position = Vector2(150, 250)
        sprite.update_screen_position(screen_position)

        # Then - 화면 위치 확인
        assert sprite.rect.centerx == 150, 'rect의 x 중심이 업데이트되어야 함'
        assert sprite.rect.centery == 250, 'rect의 y 중심이 업데이트되어야 함'


class TestLayeredSpriteGroup:
    def setUp(self) -> None:
        pygame.init()

    def test_레이어드_스프라이트_그룹_초기화_상태_확인_성공_시나리오(
        self,
    ) -> None:
        """6. 레이어드 스프라이트 그룹 초기화 상태 확인 (성공 시나리오)

        목적: LayeredSpriteGroup 생성자와 초기 상태 설정 검증
        테스트할 범위: __init__, 레이어별 그룹 초기화
        커버하는 함수 및 데이터: 레이어별 pygame.sprite.Group 생성
        기대되는 안정성: 모든 레이어에 대한 그룹 생성 보장
        """
        pygame.init()

        # Given & When - LayeredSpriteGroup 생성
        sprite_group = LayeredSpriteGroup()

        # Then - 초기 상태 확인
        assert sprite_group.get_total_sprite_count() == 0, (
            '초기 스프라이트 개수는 0이어야 함'
        )

        for layer in RenderLayer:
            assert sprite_group.get_layer_sprite_count(layer) == 0, (
                f'{layer.display_name} 레이어가 비어있어야 함'
            )

    def test_스프라이트_추가_제거_기능_검증_성공_시나리오(self) -> None:
        """7. 스프라이트 추가 제거 기능 검증 (성공 시나리오)

        목적: 스프라이트 추가/제거 동작 검증
        테스트할 범위: add_sprite, remove_sprite 메서드
        커버하는 함수 및 데이터: 스프라이트 그룹 관리
        기대되는 안정성: 정확한 스프라이트 추가/제거 보장
        """
        pygame.init()

        # Given - LayeredSpriteGroup과 스프라이트들
        sprite_group = LayeredSpriteGroup()
        entity_sprite = RenderableSprite(RenderLayer.ENTITIES)
        ui_sprite = RenderableSprite(RenderLayer.UI)

        # When - 스프라이트 추가
        sprite_group.add_sprite(entity_sprite)
        sprite_group.add_sprite(ui_sprite)

        # Then - 추가 확인
        assert sprite_group.get_total_sprite_count() == 2, (
            '총 스프라이트 개수가 2개여야 함'
        )
        assert (
            sprite_group.get_layer_sprite_count(RenderLayer.ENTITIES) == 1
        ), '엔티티 레이어에 1개 스프라이트가 있어야 함'
        assert sprite_group.get_layer_sprite_count(RenderLayer.UI) == 1, (
            'UI 레이어에 1개 스프라이트가 있어야 함'
        )

        # When - 스프라이트 제거
        sprite_group.remove_sprite(entity_sprite)

        # Then - 제거 확인
        assert sprite_group.get_total_sprite_count() == 1, (
            '총 스프라이트 개수가 1개여야 함'
        )
        assert (
            sprite_group.get_layer_sprite_count(RenderLayer.ENTITIES) == 0
        ), '엔티티 레이어가 비어있어야 함'
        assert sprite_group.get_layer_sprite_count(RenderLayer.UI) == 1, (
            'UI 레이어에 1개 스프라이트가 남아있어야 함'
        )

    def test_스프라이트_레이어_이동_기능_검증_성공_시나리오(self) -> None:
        """8. 스프라이트 레이어 이동 기능 검증 (성공 시나리오)

        목적: 스프라이트를 다른 레이어로 이동하는 기능 검증
        테스트할 범위: move_sprite_to_layer 메서드
        커버하는 함수 및 데이터: 레이어 간 스프라이트 이동
        기대되는 안정성: 올바른 레이어 이동 보장
        """
        pygame.init()

        # Given - LayeredSpriteGroup과 스프라이트
        sprite_group = LayeredSpriteGroup()
        sprite = RenderableSprite(RenderLayer.ENTITIES)
        sprite_group.add_sprite(sprite)

        # When - 레이어 이동
        sprite_group.move_sprite_to_layer(sprite, RenderLayer.EFFECTS)

        # Then - 이동 확인
        assert sprite.layer == RenderLayer.EFFECTS, (
            '스프라이트의 레이어가 변경되어야 함'
        )
        assert (
            sprite_group.get_layer_sprite_count(RenderLayer.ENTITIES) == 0
        ), '기존 레이어가 비어있어야 함'
        assert sprite_group.get_layer_sprite_count(RenderLayer.EFFECTS) == 1, (
            '새 레이어에 스프라이트가 있어야 함'
        )

    def test_레이어별_클리어_기능_검증_성공_시나리오(self) -> None:
        """9. 레이어별 클리어 기능 검증 (성공 시나리오)

        목적: 특정 레이어의 모든 스프라이트 제거 기능 검증
        테스트할 범위: clear_layer, clear_all 메서드
        커버하는 함수 및 데이터: 레이어별/전체 스프라이트 제거
        기대되는 안정성: 완전한 스프라이트 제거 보장
        """
        pygame.init()

        # Given - 여러 레이어에 스프라이트 추가
        sprite_group = LayeredSpriteGroup()
        entity1 = RenderableSprite(RenderLayer.ENTITIES)
        entity2 = RenderableSprite(RenderLayer.ENTITIES)
        ui_sprite = RenderableSprite(RenderLayer.UI)

        sprite_group.add_sprite(entity1)
        sprite_group.add_sprite(entity2)
        sprite_group.add_sprite(ui_sprite)

        # When - 특정 레이어 클리어
        sprite_group.clear_layer(RenderLayer.ENTITIES)

        # Then - 특정 레이어만 클리어 확인
        assert (
            sprite_group.get_layer_sprite_count(RenderLayer.ENTITIES) == 0
        ), '엔티티 레이어가 비어있어야 함'
        assert sprite_group.get_layer_sprite_count(RenderLayer.UI) == 1, (
            'UI 레이어는 남아있어야 함'
        )
        assert sprite_group.get_total_sprite_count() == 1, (
            '총 1개 스프라이트가 남아있어야 함'
        )

        # When - 전체 클리어
        sprite_group.clear_all()

        # Then - 전체 클리어 확인
        assert sprite_group.get_total_sprite_count() == 0, (
            '모든 스프라이트가 제거되어야 함'
        )
        for layer in RenderLayer:
            assert sprite_group.get_layer_sprite_count(layer) == 0, (
                f'{layer.display_name} 레이어가 비어있어야 함'
            )


class TestRenderSystem:
    def setUp(self) -> None:
        pygame.init()

    @patch('pygame.display.set_mode')
    def test_렌더링_시스템_초기화_상태_확인_성공_시나리오(
        self, mock_set_mode
    ) -> None:
        """10. 렌더링 시스템 초기화 상태 확인 (성공 시나리오)

        목적: RenderSystem 생성자와 초기 상태 설정 검증
        테스트할 범위: __init__, 초기 속성값
        커버하는 함수 및 데이터: surface, screen_size, background_color 등
        기대되는 안정성: 올바른 초기 상태 설정 보장
        """
        pygame.init()

        # Given - Mock surface 생성
        mock_surface = Mock()
        mock_surface.get_width.return_value = 800
        mock_surface.get_height.return_value = 600

        # When - RenderSystem 생성
        render_system = RenderSystem(mock_surface)

        # Then - 초기 상태 확인
        assert render_system.surface == mock_surface, 'surface가 설정되어야 함'
        assert render_system.screen_size == Vector2(800, 600), (
            '화면 크기가 정확해야 함'
        )
        assert render_system.background_color == (0, 0, 0), (
            '기본 배경색이 검은색이어야 함'
        )
        assert render_system.camera_transformer is None, (
            '초기에는 카메라 변환기가 없어야 함'
        )

    @patch('pygame.display.set_mode')
    def test_렌더링_시스템_스프라이트_관리_기능_검증_성공_시나리오(
        self, mock_set_mode
    ) -> None:
        """11. 렌더링 시스템 스프라이트 관리 기능 검증 (성공 시나리오)

        목적: RenderSystem의 스프라이트 추가/제거/관리 기능 검증
        테스트할 범위: add_sprite, remove_sprite, get_all_sprites 등
        커버하는 함수 및 데이터: 스프라이트 관리 메서드들
        기대되는 안정성: 정확한 스프라이트 관리 보장
        """
        pygame.init()

        # Given - RenderSystem과 스프라이트들
        mock_surface = Mock()
        mock_surface.get_width.return_value = 800
        mock_surface.get_height.return_value = 600

        render_system = RenderSystem(mock_surface)
        sprite1 = RenderableSprite(RenderLayer.ENTITIES)
        sprite2 = RenderableSprite(RenderLayer.UI)

        # When - 스프라이트 추가
        render_system.add_sprite(sprite1)
        render_system.add_sprite(sprite2)

        # Then - 추가 확인
        stats = render_system.get_render_stats()
        assert stats['total_sprites'] == 2, '총 스프라이트 개수가 2개여야 함'
        assert stats['layer_counts']['엔티티'] == 1, (
            '엔티티 레이어에 1개 스프라이트가 있어야 함'
        )
        assert stats['layer_counts']['UI'] == 1, (
            'UI 레이어에 1개 스프라이트가 있어야 함'
        )

        # When - 스프라이트 제거
        render_system.remove_sprite(sprite1)

        # Then - 제거 확인
        stats = render_system.get_render_stats()
        assert stats['total_sprites'] == 1, '총 스프라이트 개수가 1개여야 함'
        assert stats['layer_counts']['엔티티'] == 0, (
            '엔티티 레이어가 비어있어야 함'
        )

    @patch('pygame.display.set_mode')
    def test_렌더링_시스템_콜백_관리_기능_검증_성공_시나리오(
        self, mock_set_mode
    ) -> None:
        """12. 렌더링 시스템 콜백 관리 기능 검증 (성공 시나리오)

        목적: RenderSystem의 콜백 등록/해제 기능 검증
        테스트할 범위: add_*_callback, remove_*_callback 메서드들
        커버하는 함수 및 데이터: 콜백 관리 메서드들
        기대되는 안정성: 정확한 콜백 등록/해제 보장
        """
        pygame.init()

        # Given - RenderSystem과 콜백 함수들
        mock_surface = Mock()
        mock_surface.get_width.return_value = 800
        mock_surface.get_height.return_value = 600

        render_system = RenderSystem(mock_surface)
        update_callback = Mock()
        pre_render_callback = Mock()
        post_render_callback = Mock()

        # When - 콜백 추가
        render_system.add_update_callback(update_callback)
        render_system.add_pre_render_callback(pre_render_callback)
        render_system.add_post_render_callback(post_render_callback)

        # Then - 콜백 개수 확인
        stats = render_system.get_render_stats()
        assert stats['update_callbacks_count'] == 1, (
            '업데이트 콜백이 1개 등록되어야 함'
        )
        assert stats['pre_render_callbacks_count'] == 1, (
            'pre-render 콜백이 1개 등록되어야 함'
        )
        assert stats['post_render_callbacks_count'] == 1, (
            'post-render 콜백이 1개 등록되어야 함'
        )

        # When - 콜백 제거
        render_system.remove_update_callback(update_callback)

        # Then - 콜백 제거 확인
        stats = render_system.get_render_stats()
        assert stats['update_callbacks_count'] == 0, (
            '업데이트 콜백이 제거되어야 함'
        )

    @patch('pygame.display.set_mode')
    def test_렌더링_시스템_업데이트_기능_검증_성공_시나리오(
        self, mock_set_mode
    ) -> None:
        """13. 렌더링 시스템 업데이트 기능 검증 (성공 시나리오)

        목적: RenderSystem의 업데이트 로직 검증
        테스트할 범위: update, update_sprite_positions 메서드
        커버하는 함수 및 데이터: 업데이트 콜백 호출, 스프라이트 위치 업데이트
        기대되는 안정성: 올바른 업데이트 순서와 동작 보장
        """
        pygame.init()

        # Given - RenderSystem과 업데이트 콜백
        mock_surface = Mock()
        mock_surface.get_width.return_value = 800
        mock_surface.get_height.return_value = 600

        render_system = RenderSystem(mock_surface)
        update_callback = Mock()
        render_system.add_update_callback(update_callback)

        # When - 업데이트 수행
        render_system.update(0.016)

        # Then - 콜백 호출 확인
        update_callback.assert_called_once()

    @patch('pygame.display.set_mode')
    def test_렌더링_시스템_화면_클리어_기능_검증_성공_시나리오(
        self, mock_set_mode
    ) -> None:
        """14. 렌더링 시스템 화면 클리어 기능 검증 (성공 시나리오)

        목적: 화면 클리어 기능의 정상 동작 검증
        테스트할 범위: clear_screen 메서드
        커버하는 함수 및 데이터: 배경색으로 화면 클리어
        기대되는 안정성: 올바른 화면 클리어 보장
        """
        pygame.init()

        # Given - RenderSystem
        mock_surface = Mock()
        mock_surface.get_width.return_value = 800
        mock_surface.get_height.return_value = 600

        render_system = RenderSystem(
            mock_surface, background_color=(255, 0, 0)
        )

        # When - 화면 클리어
        render_system.clear_screen()

        # Then - surface.fill 호출 확인
        mock_surface.fill.assert_called_with((255, 0, 0))

    @patch('pygame.display.set_mode')
    def test_렌더링_시스템_렌더링_기능_검증_성공_시나리오(
        self, mock_set_mode
    ) -> None:
        """15. 렌더링 시스템 렌더링 기능 검증 (성공 시나리오)

        목적: 전체 렌더링 파이프라인 동작 검증
        테스트할 범위: render 메서드
        커버하는 함수 및 데이터: 화면 클리어, 콜백 호출, 스프라이트 렌더링
        기대되는 안정성: 올바른 렌더링 순서와 동작 보장
        """
        pygame.init()

        # Given - RenderSystem과 콜백들
        mock_surface = Mock()
        mock_surface.get_width.return_value = 800
        mock_surface.get_height.return_value = 600
        # pygame sprite.Group.draw가 호출하는 blits 메서드 mock 설정
        mock_surface.blits.return_value = []

        render_system = RenderSystem(mock_surface)
        pre_callback = Mock()
        post_callback = Mock()

        render_system.add_pre_render_callback(pre_callback)
        render_system.add_post_render_callback(post_callback)

        # When - 렌더링 수행
        render_system.render()

        # Then - 렌더링 파이프라인 확인
        mock_surface.fill.assert_called_once_with((0, 0, 0))  # 화면 클리어
        pre_callback.assert_called_once_with(mock_surface)  # pre-render 콜백
        post_callback.assert_called_once_with(mock_surface)  # post-render 콜백

    @patch('pygame.display.set_mode')
    def test_렌더링_시스템_통계_정보_제공_정확성_검증_성공_시나리오(
        self, mock_set_mode
    ) -> None:
        """16. 렌더링 시스템 통계 정보 제공 정확성 검증 (성공 시나리오)

        목적: get_render_stats 메서드의 정확한 통계 정보 제공 검증
        테스트할 범위: get_render_stats 메서드
        커버하는 함수 및 데이터: 렌더링 관련 모든 통계
        기대되는 안정성: 완전하고 정확한 렌더링 통계 데이터 제공 보장
        """
        pygame.init()

        # Given - 설정된 RenderSystem
        mock_surface = Mock()
        mock_surface.get_width.return_value = 1024
        mock_surface.get_height.return_value = 768

        render_system = RenderSystem(
            mock_surface,
            background_color=(128, 128, 128),
            track_dirty_rects=True,
        )

        # 스프라이트와 콜백 추가
        sprite1 = RenderableSprite(RenderLayer.ENTITIES)
        sprite2 = RenderableSprite(RenderLayer.UI)
        render_system.add_sprite(sprite1)
        render_system.add_sprite(sprite2)

        update_callback = Mock()
        render_system.add_update_callback(update_callback)

        # When - 통계 조회
        stats = render_system.get_render_stats()

        # Then - 통계 정보 확인
        assert stats['total_sprites'] == 2, '총 스프라이트 개수가 정확해야 함'
        assert stats['screen_size'] == (1024, 768), '화면 크기가 정확해야 함'
        assert stats['background_color'] == (128, 128, 128), (
            '배경색이 정확해야 함'
        )
        assert stats['dirty_rects_tracking'], (
            'dirty rect 추적이 활성화되어야 함'
        )
        assert stats['update_callbacks_count'] == 1, (
            '업데이트 콜백 개수가 정확해야 함'
        )
        assert stats['has_camera_transformer'] is False, (
            '카메라 변환기가 없어야 함'
        )

        # 레이어별 통계 확인
        assert stats['layer_counts']['엔티티'] == 1, (
            '엔티티 레이어 개수가 정확해야 함'
        )
        assert stats['layer_counts']['UI'] == 1, 'UI 레이어 개수가 정확해야 함'
        assert stats['layer_counts']['배경'] == 0, (
            '배경 레이어가 비어있어야 함'
        )

    @patch('pygame.display.set_mode')
    def test_렌더링_시스템_더티_렉트_추적_기능_검증_성공_시나리오(
        self, mock_set_mode
    ) -> None:
        """17. 렌더링 시스템 더티 렉트 추적 기능 검증 (성공 시나리오)

        목적: 더티 렉트 추적 기능의 정상 동작 검증
        테스트할 범위: enable_dirty_rect_tracking, clear_screen 메서드
        커버하는 함수 및 데이터: 더티 렉트 관리
        기대되는 안정성: 효율적인 화면 업데이트 보장
        """
        pygame.init()

        # Given - 더티 렉트 추적이 활성화된 RenderSystem
        mock_surface = Mock()
        mock_surface.get_width.return_value = 800
        mock_surface.get_height.return_value = 600

        render_system = RenderSystem(mock_surface, track_dirty_rects=True)

        # Then - 초기 상태 확인
        stats = render_system.get_render_stats()
        assert stats['dirty_rects_tracking'], (
            '더티 렉트 추적이 활성화되어야 함'
        )
        assert stats['dirty_rects_count'] == 0, (
            '초기 더티 렉트 개수는 0이어야 함'
        )

        # When - 더티 렉트 추적 비활성화
        render_system.enable_dirty_rect_tracking(False)

        # Then - 비활성화 확인
        stats = render_system.get_render_stats()
        assert not stats['dirty_rects_tracking'], (
            '더티 렉트 추적이 비활성화되어야 함'
        )
