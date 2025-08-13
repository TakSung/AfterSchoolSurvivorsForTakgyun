import pytest

from src.core.coordinate_transformer import (
    CoordinateSpace,
    ICoordinateTransformer,
)
from src.utils.vector2 import Vector2


class MockCoordinateTransformer(ICoordinateTransformer):
    """테스트용 Mock Coordinate Transformer"""

    def __init__(self, screen_size: Vector2 = Vector2(800, 600)):
        self._camera_offset = Vector2.zero()
        self._zoom_level = 1.0
        self._screen_size = screen_size
        self._cache_dirty = False

    def world_to_screen(self, world_pos: Vector2) -> Vector2:
        # 기본적인 변환: (월드 좌표 - 카메라 오프셋) * 줌 + 스크린 중심
        relative_pos = (world_pos - self._camera_offset) * self._zoom_level
        screen_center = self._screen_size / 2
        return relative_pos + screen_center

    def screen_to_world(self, screen_pos: Vector2) -> Vector2:
        # 역변환: (스크린 좌표 - 스크린 중심) / 줌 + 카메라 오프셋
        screen_center = self._screen_size / 2
        relative_pos = (screen_pos - screen_center) / self._zoom_level
        return relative_pos + self._camera_offset

    def get_camera_offset(self) -> Vector2:
        return self._camera_offset.copy()

    def set_camera_offset(self, offset: Vector2) -> None:
        self._camera_offset = offset.copy()
        self.invalidate_cache()

    def invalidate_cache(self) -> None:
        self._cache_dirty = True

    @property
    def zoom_level(self) -> float:
        return self._zoom_level

    @zoom_level.setter
    def zoom_level(self, value: float) -> None:
        self._zoom_level = max(0.1, value)
        self.invalidate_cache()

    @property
    def screen_size(self) -> Vector2:
        return self._screen_size.copy()

    @screen_size.setter
    def screen_size(self, size: Vector2) -> None:
        self._screen_size = size.copy()
        self.invalidate_cache()


class TestCoordinateSpace:
    def test_좌표공간_열거형_값_확인_성공_시나리오(self) -> None:
        """1. 좌표 공간 열거형 값 확인 (성공 시나리오)

        목적: CoordinateSpace 열거형의 정의와 표시명 검증
        테스트할 범위: CoordinateSpace 열거형과 display_name 속성
        커버하는 함수 및 데이터: WORLD, SCREEN 상수와 한국어 표시명
        기대되는 안정성: 일관된 좌표 공간 식별 보장
        """
        # When & Then - 좌표 공간 값 검증
        assert CoordinateSpace.WORLD.value == 0, (
            'WORLD 좌표공간 값이 0이어야 함'
        )
        assert CoordinateSpace.SCREEN.value == 1, (
            'SCREEN 좌표공간 값이 1이어야 함'
        )

        # When & Then - 표시명 검증
        assert CoordinateSpace.WORLD.display_name == '월드 좌표', (
            'WORLD 표시명이 정확해야 함'
        )
        assert CoordinateSpace.SCREEN.display_name == '스크린 좌표', (
            'SCREEN 표시명이 정확해야 함'
        )


class TestICoordinateTransformer:
    def test_좌표_변환_인터페이스_기본_동작_확인_성공_시나리오(self) -> None:
        """2. 좌표 변환 인터페이스 기본 동작 확인 (성공 시나리오)

        목적: ICoordinateTransformer 인터페이스의 기본 메서드 검증
        테스트할 범위: transform 메서드와 기본 구현
        커버하는 함수 및 데이터: 좌표 공간 간 변환 로직
        기대되는 안정성: 일관된 좌표 변환 인터페이스 제공 보장
        """
        # Given - Mock 변환기 생성
        transformer = MockCoordinateTransformer()
        test_position = Vector2(100, 50)

        # When & Then - 동일 좌표 공간 변환 검증
        same_space_result = transformer.transform(
            test_position, CoordinateSpace.WORLD, CoordinateSpace.WORLD
        )
        assert same_space_result == test_position, (
            '동일 좌표 공간 변환 시 같은 값이어야 함'
        )
        assert same_space_result is not test_position, (
            '동일 좌표 공간 변환 시 새로운 객체여야 함'
        )

    def test_월드_스크린_좌표_변환_정확성_검증_성공_시나리오(self) -> None:
        """3. 월드-스크린 좌표 변환 정확성 검증 (성공 시나리오)

        목적: 월드 좌표와 스크린 좌표 간 변환의 정확성 검증
        테스트할 범위: world_to_screen, screen_to_world 메서드
        커버하는 함수 및 데이터: 좌표 변환 수학적 계산
        기대되는 안정성: 왕복 변환 시 좌표 일관성 보장
        """
        # Given - Mock 변환기와 테스트 좌표 설정
        transformer = MockCoordinateTransformer(Vector2(800, 600))
        world_pos = Vector2(200, 150)

        # When - 월드 → 스크린 → 월드 변환
        screen_pos = transformer.world_to_screen(world_pos)
        back_to_world = transformer.screen_to_world(screen_pos)

        # Then - 왕복 변환 정확성 검증
        assert world_pos.distance_to(back_to_world) < 0.001, (
            '왕복 변환 시 좌표가 일치해야 함'
        )

    def test_카메라_오프셋_적용_좌표_변환_검증_성공_시나리오(self) -> None:
        """4. 카메라 오프셋 적용 좌표 변환 검증 (성공 시나리오)

        목적: 카메라 오프셋이 좌표 변환에 올바르게 반영되는지 검증
        테스트할 범위: set_camera_offset, get_camera_offset 메서드
        커버하는 함수 및 데이터: 카메라 이동에 따른 좌표 변환 변화
        기대되는 안정성: 카메라 위치 변화 시 일관된 변환 보장
        """
        # Given - Mock 변환기와 초기 설정
        transformer = MockCoordinateTransformer(Vector2(800, 600))
        world_pos = Vector2(0, 0)  # 월드 원점

        # When - 카메라 오프셋 없이 변환
        screen_pos_no_offset = transformer.world_to_screen(world_pos)

        # When - 카메라 오프셋 설정 후 변환
        camera_offset = Vector2(100, 50)
        transformer.set_camera_offset(camera_offset)
        screen_pos_with_offset = transformer.world_to_screen(world_pos)

        # Then - 오프셋 적용 확인
        assert transformer.get_camera_offset() == camera_offset, (
            '카메라 오프셋이 정확히 설정되어야 함'
        )
        expected_difference = screen_pos_no_offset - screen_pos_with_offset
        assert expected_difference.distance_to(Vector2(100, 50)) < 0.001, (
            '카메라 오프셋이 올바르게 적용되어야 함'
        )

    def test_줌_레벨_적용_좌표_변환_검증_성공_시나리오(self) -> None:
        """5. 줌 레벨 적용 좌표 변환 검증 (성공 시나리오)

        목적: 줌 레벨 변화가 좌표 변환에 올바르게 반영되는지 검증
        테스트할 범위: zoom_level 속성 설정과 변환 결과
        커버하는 함수 및 데이터: 줌 배율에 따른 좌표 스케일링
        기대되는 안정성: 줌 레벨 변화 시 비례적 좌표 변환 보장
        """
        # Given - Mock 변환기와 테스트 좌표
        transformer = MockCoordinateTransformer(Vector2(800, 600))
        world_pos = Vector2(100, 100)

        # When - 기본 줌 레벨(1.0)에서 변환
        transformer.zoom_level = 1.0
        screen_pos_zoom_1 = transformer.world_to_screen(world_pos)

        # When - 줌 레벨 2배로 설정 후 변환
        transformer.zoom_level = 2.0
        screen_pos_zoom_2 = transformer.world_to_screen(world_pos)

        # Then - 줌 레벨 적용 확인
        assert transformer.zoom_level == 2.0, '줌 레벨이 정확히 설정되어야 함'
        # 줌 2배 시 월드 좌표가 스크린에서 2배 크게 나타나야 함
        screen_center = Vector2(400, 300)
        offset_1 = screen_pos_zoom_1 - screen_center
        offset_2 = screen_pos_zoom_2 - screen_center
        expected_offset_2 = offset_1 * 2
        assert expected_offset_2.distance_to(offset_2) < 0.001, (
            '줌 레벨에 따른 스케일링이 정확해야 함'
        )

    def test_화면_크기_변경_좌표_변환_검증_성공_시나리오(self) -> None:
        """6. 화면 크기 변경 좌표 변환 검증 (성공 시나리오)

        목적: 화면 크기 변화가 좌표 변환에 올바르게 반영되는지 검증
        테스트할 범위: screen_size 속성 설정과 변환 결과
        커버하는 함수 및 데이터: 화면 해상도 변화에 따른 중심점 이동
        기대되는 안정성: 화면 크기 변화 시 올바른 중심점 계산 보장
        """
        # Given - Mock 변환기와 테스트 좌표
        transformer = MockCoordinateTransformer(Vector2(800, 600))
        world_origin = Vector2.zero()

        # When - 기본 화면 크기에서 변환
        screen_pos_800x600 = transformer.world_to_screen(world_origin)

        # When - 화면 크기 변경 후 변환
        new_screen_size = Vector2(1024, 768)
        transformer.screen_size = new_screen_size
        screen_pos_1024x768 = transformer.world_to_screen(world_origin)

        # Then - 화면 크기 변경 확인
        assert transformer.screen_size == new_screen_size, (
            '화면 크기가 정확히 설정되어야 함'
        )
        # 월드 원점이 새로운 화면 중심에 매핑되어야 함
        expected_center = new_screen_size / 2
        assert screen_pos_1024x768.distance_to(expected_center) < 0.001, (
            '새로운 화면 중심으로 변환되어야 함'
        )

    def test_화면_가시성_검사_정확성_검증_성공_시나리오(self) -> None:
        """7. 화면 가시성 검사 정확성 검증 (성공 시나리오)

        목적: is_point_visible 메서드의 가시성 판단 정확성 검증
        테스트할 범위: is_point_visible 메서드
        커버하는 함수 및 데이터: 월드 좌표의 화면 내 위치 판단
        기대되는 안정성: 정확한 가시성 판단을 통한 렌더링 최적화 지원
        """
        # Given - Mock 변환기 설정 (800x600 화면)
        transformer = MockCoordinateTransformer(Vector2(800, 600))

        # When & Then - 화면 중심점 가시성 검증 (가시)
        center_world = Vector2.zero()  # 카메라 오프셋이 0이므로 화면 중심
        assert transformer.is_point_visible(center_world), (
            '화면 중심은 가시 영역이어야 함'
        )

        # When & Then - 화면 밖 점 가시성 검증 (비가시)
        far_world = Vector2(1000, 1000)  # 화면 밖
        assert not transformer.is_point_visible(far_world), (
            '화면 밖 점은 비가시 영역이어야 함'
        )

        # When & Then - 마진 포함 가시성 검증
        edge_world = Vector2(450, 350)  # 화면 경계 근처
        assert transformer.is_point_visible(edge_world, margin=100), (
            '마진 포함 시 경계 근처 점은 가시여야 함'
        )

    def test_지원하지_않는_좌표_변환_예외_처리_실패_시나리오(self) -> None:
        """8. 지원하지 않는 좌표 변환 예외 처리 검증 (실패 시나리오)

        목적: 잘못된 좌표 공간 조합 시 적절한 예외 발생 검증
        테스트할 범위: transform 메서드의 예외 처리
        커버하는 함수 및 데이터: 유효하지 않은 좌표 공간 조합
        기대되는 안정성: 명확한 예외 메시지를 통한 개발 편의성 제공
        """
        # Given - Mock 변환기와 테스트 좌표
        transformer = MockCoordinateTransformer()
        test_position = Vector2(100, 50)

        # When & Then - 현재는 WORLD-SCREEN만 지원하므로 모든 조합이 유효함
        # 미래 확장을 위한 테스트 구조 준비
        try:
            result = transformer.transform(
                test_position, CoordinateSpace.WORLD, CoordinateSpace.SCREEN
            )
            assert result is not None, '유효한 변환은 성공해야 함'
        except ValueError:
            pytest.fail('유효한 좌표 변환에서 예외가 발생하지 않아야 함')

    def test_캐시_무효화_동작_확인_성공_시나리오(self) -> None:
        """9. 캐시 무효화 동작 확인 (성공 시나리오)

        목적: 카메라나 줌 레벨 변경 시 캐시 무효화 동작 검증
        테스트할 범위: invalidate_cache 메서드 호출
        커버하는 함수 및 데이터: 상태 변경 시 캐시 플래그 업데이트
        기대되는 안정성: 상태 변경 시 자동 캐시 무효화 보장
        """
        # Given - Mock 변환기 생성
        transformer = MockCoordinateTransformer()

        # When - 카메라 오프셋 변경
        transformer.set_camera_offset(Vector2(50, 50))

        # Then - 캐시 무효화 플래그 확인
        assert transformer._cache_dirty, (
            '카메라 오프셋 변경 시 캐시가 무효화되어야 함'
        )

        # Given - 캐시 플래그 초기화
        transformer._cache_dirty = False

        # When - 줌 레벨 변경
        transformer.zoom_level = 2.0

        # Then - 캐시 무효화 플래그 확인
        assert transformer._cache_dirty, (
            '줌 레벨 변경 시 캐시가 무효화되어야 함'
        )
