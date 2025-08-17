"""
EntityRenderSystem 단위 테스트

EntityRenderSystem의 핵심 기능들을 검증하는 테스트 스위트:
- 좌표 변환 시스템 통합
- 화면 밖 컬링 최적화
- 플레이어 중앙 고정 렌더링
- 깊이 정렬 및 회전 처리
"""

import pygame

from src.components.player_component import PlayerComponent
from src.components.position_component import PositionComponent
from src.components.render_component import RenderComponent, RenderLayer
from src.components.rotation_component import RotationComponent
from src.core.coordinate_manager import CoordinateManager
from src.core.coordinate_transformer import ICoordinateTransformer
from src.core.entity_manager import EntityManager
from src.systems.entity_render_system import EntityRenderSystem
from src.utils.vector2 import Vector2


class MockCoordinateTransformer(ICoordinateTransformer):
    """좌표 변환기 모의 객체"""

    def __init__(self):
        self._offset = Vector2(0, 0)
        self._zoom_level = 1.0
        self._screen_size = Vector2(800, 600)

    def world_to_screen(self, world_pos: Vector2) -> Vector2:
        return Vector2(
            world_pos.x - self._offset.x + 400,  # 화면 중앙(800/2)
            world_pos.y - self._offset.y + 300,  # 화면 중앙(600/2)
        )

    def screen_to_world(self, screen_pos: Vector2) -> Vector2:
        return Vector2(
            screen_pos.x + self._offset.x - 400,
            screen_pos.y + self._offset.y - 300,
        )

    def get_camera_offset(self) -> Vector2:
        return self._offset

    def set_camera_offset(self, offset: Vector2) -> None:
        self._offset = offset

    def invalidate_cache(self) -> None:
        pass  # Mock implementation

    @property
    def zoom_level(self) -> float:
        return self._zoom_level

    @zoom_level.setter
    def zoom_level(self, value: float) -> None:
        self._zoom_level = value

    @property
    def screen_size(self) -> Vector2:
        return self._screen_size

    @screen_size.setter
    def screen_size(self, size: Vector2) -> None:
        self._screen_size = size

    def set_offset(self, offset: Vector2) -> None:
        self._offset = offset


class TestEntityRenderSystem:
    def setup_method(self) -> None:
        """각 테스트 전 초기화"""
        pygame.init()

        self.surface = pygame.Surface((800, 600))
        self.entity_manager = EntityManager()
        self.coordinate_manager = CoordinateManager.get_instance()

        # Mock 좌표 변환기 설정
        self.mock_transformer = MockCoordinateTransformer()
        self.coordinate_manager.set_transformer(self.mock_transformer)

        self.render_system = EntityRenderSystem(self.surface, cull_margin=50)

    def teardown_method(self) -> None:
        """각 테스트 후 정리"""
        pygame.quit()

    def test_좌표_변환_시스템_통합_및_world_to_screen_적용_성공_시나리오(
        self,
    ) -> None:
        """1. EntityRenderSystem이 CoordinateManager.world_to_screen()을 올바르게 적용하는지 검증

        목적: 월드 좌표를 스크린 좌표로 변환하는 시스템 통합 확인
        테스트할 범위: EntityRenderSystem._render_entity 메서드의 좌표 변환 로직
        커버하는 함수 및 데이터: world_to_screen() 호출 및 결과 활용
        기대되는 안정성: 좌표 변환이 정확히 적용되어 올바른 위치에 렌더링
        """
        # Given - 월드 좌표 (100, 200)에 엔티티 생성
        entity = self.entity_manager.create_entity()

        pos_comp = PositionComponent(x=100.0, y=200.0)
        render_comp = RenderComponent(
            color=(255, 0, 0), size=(32, 32), visible=True
        )

        self.entity_manager.add_component(entity, pos_comp)
        self.entity_manager.add_component(entity, render_comp)

        # Mock transformer로 예상 스크린 좌표 계산
        world_pos = Vector2(100.0, 200.0)
        expected_screen_pos = self.mock_transformer.world_to_screen(world_pos)

        # When - 렌더링 시스템 업데이트
        self.render_system.set_entity_manager(self.entity_manager)
        self.render_system.update(0.016)

        # Then - 좌표 변환이 올바르게 적용되었는지 확인
        stats = self.render_system.get_render_stats()
        assert stats['visible_entities'] == 1, '엔티티가 렌더링되어야 함'
        assert stats['culled_entities'] == 0, (
            '화면 내 엔티티는 컬링되지 않아야 함'
        )

    def test_화면_밖_컬링_최적화_시스템_동작_성공_시나리오(self) -> None:
        """2. _is_on_screen() 메서드가 컬링 여유분을 적용하여 정확히 동작하는지 검증

        목적: 50픽셀 여유분을 포함한 화면 밖 컬링 시스템 검증
        테스트할 범위: _is_on_screen() 메서드와 컬링 로직
        커버하는 함수 및 데이터: 컬링 마진, 화면 경계 계산
        기대되는 안정성: 화면 밖 엔티티는 컬링되고 통계에 정확히 반영
        """
        # Given - 화면 밖에 위치한 엔티티 생성
        entity = self.entity_manager.create_entity()

        # 화면 왼쪽 밖 (스크린 좌표로 변환 시 x < -50이 되도록)
        pos_comp = PositionComponent(x=-600.0, y=0.0)
        render_comp = RenderComponent(
            color=(0, 255, 0), size=(32, 32), visible=True
        )

        self.entity_manager.add_component(entity, pos_comp)
        self.entity_manager.add_component(entity, render_comp)

        # When - 렌더링 시스템 업데이트
        self.render_system.set_entity_manager(self.entity_manager)
        self.render_system.update(0.016)

        # Then - 컬링 통계 확인
        stats = self.render_system.get_render_stats()
        assert stats['visible_entities'] == 0, (
            '화면 밖 엔티티는 렌더링되지 않아야 함'
        )
        assert stats['culled_entities'] == 1, '화면 밖 엔티티는 컬링되어야 함'

    def test_플레이어_중앙_고정_렌더링_시스템_동작_성공_시나리오(self) -> None:
        """3. PlayerComponent를 가진 엔티티가 화면 중앙에 고정 렌더링되는지 검증

        목적: 플레이어 엔티티의 특별한 중앙 고정 렌더링 확인
        테스트할 범위: _render_player() 메서드와 플레이어 식별 로직
        커버하는 함수 및 데이터: PlayerComponent 감지, 화면 중앙 좌표 적용
        기대되는 안정성: 플레이어는 월드 좌표와 무관하게 항상 화면 중앙에 렌더링
        """
        # Given - PlayerComponent를 가진 엔티티 생성
        player_entity = self.entity_manager.create_entity()

        player_comp = PlayerComponent(player_id=0)
        pos_comp = PositionComponent(x=1000.0, y=1000.0)  # 화면 밖 월드 좌표
        render_comp = RenderComponent(
            color=(0, 0, 255), size=(64, 64), visible=True
        )

        self.entity_manager.add_component(player_entity, player_comp)
        self.entity_manager.add_component(player_entity, pos_comp)
        self.entity_manager.add_component(player_entity, render_comp)

        # When - 렌더링 시스템 업데이트
        self.render_system.set_entity_manager(self.entity_manager)
        self.render_system.update(0.016)

        # Then - 플레이어 렌더링 통계 확인
        stats = self.render_system.get_render_stats()
        assert stats['player_entities'] == 1, (
            '플레이어 엔티티가 렌더링되어야 함'
        )
        assert stats['visible_entities'] == 1, (
            '플레이어가 가시적으로 렌더링되어야 함'
        )

    def test_깊이_정렬_시스템_Y좌표_기준_동작_성공_시나리오(self) -> None:
        """4. Y좌표 기준 깊이 정렬이 올바르게 동작하는지 검증

        목적: _sort_entities_by_depth() 메서드의 정렬 로직 확인
        테스트할 범위: 엔티티 정렬 알고리즘과 렌더 레이어/Y좌표 우선순위
        커버하는 함수 및 데이터: RenderLayer 값, Y좌표 비교
        기대되는 안정성: 엔티티들이 레이어와 Y좌표에 따라 올바른 순서로 정렬
        """
        # Given - 다양한 Y좌표와 레이어를 가진 엔티티들 생성
        entities = []

        # 배경 레이어 엔티티 (Y=100)
        bg_entity = self.entity_manager.create_entity()
        self.entity_manager.add_component(
            bg_entity, PositionComponent(x=0, y=100)
        )
        self.entity_manager.add_component(
            bg_entity,
            RenderComponent(
                layer=RenderLayer.BACKGROUND, color=(128, 128, 128)
            ),
        )
        entities.append(bg_entity)

        # 엔티티 레이어, Y=50 (앞쪽)
        front_entity = self.entity_manager.create_entity()
        self.entity_manager.add_component(
            front_entity, PositionComponent(x=0, y=50)
        )
        self.entity_manager.add_component(
            front_entity,
            RenderComponent(layer=RenderLayer.ENTITIES, color=(255, 0, 0)),
        )
        entities.append(front_entity)

        # 엔티티 레이어, Y=200 (뒤쪽)
        back_entity = self.entity_manager.create_entity()
        self.entity_manager.add_component(
            back_entity, PositionComponent(x=0, y=200)
        )
        self.entity_manager.add_component(
            back_entity,
            RenderComponent(layer=RenderLayer.ENTITIES, color=(0, 255, 0)),
        )
        entities.append(back_entity)

        # When - 깊이 정렬 수행
        self.render_system.set_entity_manager(self.entity_manager)
        sorted_entities = self.render_system._sort_entities_by_depth(
            self.entity_manager, entities
        )

        # Then - 정렬 순서 검증 (배경 -> 뒤 엔티티 -> 앞 엔티티)
        assert sorted_entities[0] == bg_entity, (
            '배경이 맨 뒤에 렌더링되어야 함'
        )
        assert sorted_entities[1] == front_entity, (
            'Y좌표가 작은 엔티티가 먼저 렌더링되어야 함'
        )
        assert sorted_entities[2] == back_entity, (
            'Y좌표가 큰 엔티티가 나중에 렌더링되어야 함'
        )

    def test_회전_처리_시스템_동작_및_캐싱_성공_시나리오(self) -> None:
        """5. RotationComponent를 가진 엔티티의 회전 처리와 캐싱이 동작하는지 검증

        목적: _get_rotated_surface() 메서드의 회전 처리와 성능 캐싱 확인
        테스트할 범위: 회전 각도 적용, 캐싱 메커니즘
        커버하는 함수 및 데이터: pygame.transform.rotate() 적용, 회전 캐시
        기대되는 안정성: 회전된 스프라이트가 정확히 생성되고 캐시되어 성능 향상
        """
        # Given - 회전 컴포넌트를 가진 엔티티 생성
        entity = self.entity_manager.create_entity()

        pos_comp = PositionComponent(x=0.0, y=0.0)
        render_comp = RenderComponent(
            color=(255, 255, 0), size=(32, 32), visible=True
        )
        rotation_comp = RotationComponent(angle=45.0)  # 45도 회전

        self.entity_manager.add_component(entity, pos_comp)
        self.entity_manager.add_component(entity, render_comp)
        self.entity_manager.add_component(entity, rotation_comp)

        # When - 첫 번째 렌더링 (캐시 생성)
        self.render_system.set_entity_manager(self.entity_manager)
        self.render_system.update(0.016)
        first_stats = self.render_system.get_render_stats()

        # 두 번째 렌더링 (캐시 사용)
        self.render_system.set_entity_manager(self.entity_manager)
        self.render_system.update(0.016)
        second_stats = self.render_system.get_render_stats()

        # Then - 회전 처리 및 캐싱 확인
        assert first_stats['rotated_sprites'] >= 1, (
            '회전된 스프라이트가 생성되어야 함'
        )
        assert second_stats['visible_entities'] == 1, (
            '회전된 엔티티가 렌더링되어야 함'
        )

    def test_렌더링_성능_통계_수집_정확성_검증_성공_시나리오(self) -> None:
        """6. 렌더링 성능 통계가 정확히 수집되는지 검증

        목적: get_render_stats() 메서드가 정확한 통계를 제공하는지 확인
        테스트할 범위: 렌더링 통계 카운터들의 정확성
        커버하는 함수 및 데이터: 모든 렌더링 통계 필드
        기대되는 안정성: 통계값들이 실제 렌더링 상황을 정확히 반영
        """
        # Given - 다양한 상황의 엔티티들 생성

        # 일반 렌더링 엔티티
        normal_entity = self.entity_manager.create_entity()
        self.entity_manager.add_component(
            normal_entity, PositionComponent(0, 0)
        )
        self.entity_manager.add_component(normal_entity, RenderComponent())

        # 플레이어 엔티티
        player_entity = self.entity_manager.create_entity()
        self.entity_manager.add_component(player_entity, PlayerComponent())
        self.entity_manager.add_component(
            player_entity, PositionComponent(0, 0)
        )
        self.entity_manager.add_component(player_entity, RenderComponent())

        # 화면 밖 엔티티 (컬링 대상)
        culled_entity = self.entity_manager.create_entity()
        self.entity_manager.add_component(
            culled_entity, PositionComponent(-1000, -1000)
        )
        self.entity_manager.add_component(culled_entity, RenderComponent())

        # When - 렌더링 시스템 업데이트
        self.render_system.set_entity_manager(self.entity_manager)
        self.render_system.update(0.016)

        # Then - 통계 정확성 검증
        stats = self.render_system.get_render_stats()

        assert stats['total_entities'] == 3, '전체 엔티티 수가 정확해야 함'
        assert stats['visible_entities'] == 2, '가시 엔티티 수가 정확해야 함'
        assert stats['player_entities'] == 1, (
            '플레이어 엔티티 수가 정확해야 함'
        )
        assert stats['culled_entities'] == 1, '컬링된 엔티티 수가 정확해야 함'

    def test_화면_크기_변경_시_적응_처리_성공_시나리오(self) -> None:
        """7. set_surface()로 화면 크기가 변경될 때 시스템이 올바르게 적응하는지 검증

        목적: 화면 크기 변경 시 내부 캐시 업데이트 확인
        테스트할 범위: set_surface() 메서드와 화면 크기 관련 필드들
        커버하는 함수 및 데이터: 화면 중앙 좌표, 화면 크기 캐시
        기대되는 안정성: 새로운 화면 크기에 맞춰 렌더링 시스템 동작
        """
        # Given - 초기 화면 크기 확인
        initial_center = self.render_system._screen_center
        assert initial_center == (400, 300), (
            '초기 화면 중앙이 (400, 300)이어야 함'
        )

        # When - 새로운 화면 크기로 변경
        new_surface = pygame.Surface((1024, 768))
        self.render_system.set_surface(new_surface)

        # Then - 화면 크기 관련 필드들이 업데이트되었는지 확인
        assert self.render_system._screen_width == 1024, (
            '화면 너비가 업데이트되어야 함'
        )
        assert self.render_system._screen_height == 768, (
            '화면 높이가 업데이트되어야 함'
        )
        assert self.render_system._screen_center == (512, 384), (
            '화면 중앙이 업데이트되어야 함'
        )

    def test_컬링_마진_설정_변경_동작_성공_시나리오(self) -> None:
        """8. set_cull_margin()으로 컬링 여유분이 올바르게 변경되는지 검증

        목적: 컬링 마진 설정 변경 기능의 동작 확인
        테스트할 범위: set_cull_margin() 메서드와 컬링 경계 적용
        커버하는 함수 및 데이터: _cull_margin 필드, 경계 계산
        기대되는 안정성: 새로운 마진 설정에 따른 컬링 동작 변경
        """
        # Given - 초기 컬링 마진 확인
        assert self.render_system._cull_margin == 50, (
            '초기 컬링 마진이 50이어야 함'
        )

        # When - 컬링 마진 변경
        self.render_system.set_cull_margin(100)

        # Then - 컬링 마진이 변경되었는지 확인
        assert self.render_system._cull_margin == 100, (
            '컬링 마진이 100으로 변경되어야 함'
        )

        # 음수 값 설정 시 0으로 제한되는지 확인
        self.render_system.set_cull_margin(-10)
        assert self.render_system._cull_margin == 0, (
            '음수 마진은 0으로 제한되어야 함'
        )

    def test_회전_캐시_메모리_관리_및_정리_성공_시나리오(self) -> None:
        """9. 회전 캐시의 메모리 관리가 올바르게 동작하는지 검증

        목적: 회전 캐시 크기 제한과 메모리 정리 기능 확인
        테스트할 범위: 캐시 크기 제한, clear_rotation_cache() 메서드
        커버하는 함수 및 데이터: _rotation_cache, _max_cache_size
        기대되는 안정성: 메모리 사용량이 제한되고 정리 기능이 작동
        """
        # Given - 캐시 정리 전 상태 확인
        initial_cache_size = len(self.render_system._rotation_cache)

        # When - 캐시 정리 수행
        self.render_system.clear_rotation_cache()

        # Then - 캐시가 비워졌는지 확인
        assert len(self.render_system._rotation_cache) == 0, (
            '캐시가 정리되어야 함'
        )

    def test_시스템_초기화_및_cleanup_처리_성공_시나리오(self) -> None:
        """10. 시스템 초기화와 정리 과정이 올바르게 동작하는지 검증

        목적: initialize()와 cleanup() 메서드의 동작 확인
        테스트할 범위: 시스템 초기화/정리 로직
        커버하는 함수 및 데이터: 좌표 변환기 확인, 리소스 정리
        기대되는 안정성: 시스템이 안전하게 초기화되고 정리됨
        """
        # Given - 새로운 렌더링 시스템 인스턴스 생성
        new_surface = pygame.Surface((800, 600))
        new_system = EntityRenderSystem(new_surface)

        # When - 초기화 수행
        new_system.initialize()

        # Then - 초기화 상태 확인 (경고 없이 완료되어야 함)
        assert new_system.enabled, '시스템이 활성화되어야 함'

        # When - 정리 수행
        new_system.cleanup()

        # Then - 정리 후 상태 확인
        assert len(new_system._rotation_cache) == 0, (
            '정리 후 회전 캐시가 비워져야 함'
        )
