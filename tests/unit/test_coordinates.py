"""
Comprehensive coordinate transformation accuracy tests.

Tests mathematical accuracy of world-screen transformations,
round-trip consistency, edge cases, and various transformer implementations.
"""

import math

import pytest

from src.core.cached_camera_transformer import CachedCameraTransformer
from src.core.camera_based_transformer import CameraBasedTransformer
from src.core.coordinate_transformer import ICoordinateTransformer
from src.utils.vector2 import Vector2


class TestCoordinateTransformationAccuracy:
    """Test coordinate transformation mathematical accuracy."""

    @pytest.fixture
    def screen_size(self) -> Vector2:
        """Return standard screen size for testing."""
        return Vector2(1024, 768)

    @pytest.fixture
    def transformer_basic(
        self, screen_size: Vector2
    ) -> CameraBasedTransformer:
        """Create basic camera-based transformer."""
        return CameraBasedTransformer(screen_size)

    @pytest.fixture
    def transformer_cached(
        self, screen_size: Vector2
    ) -> CachedCameraTransformer:
        """Create cached camera-based transformer."""
        return CachedCameraTransformer(screen_size, cache_size=100)

    @pytest.fixture(params=['basic', 'cached'])
    def transformer(
        self,
        request: pytest.FixtureRequest,
        transformer_basic: CameraBasedTransformer,
        transformer_cached: CachedCameraTransformer,
    ) -> ICoordinateTransformer:
        """Return parameterized transformer fixture for all implementations."""
        if request.param == 'basic':
            return transformer_basic
        elif request.param == 'cached':
            return transformer_cached
        else:
            raise ValueError(f'Unknown transformer type: {request.param}')

    @pytest.mark.parametrize(
        'world_x,world_y',
        [
            (0.0, 0.0),  # Origin
            (100.0, 50.0),  # Positive integers
            (-100.0, -50.0),  # Negative integers
            (123.456, 789.123),  # Positive floats
            (-123.456, -789.123),  # Negative floats
            (1000000.0, 500000.0),  # Large positive values
            (-1000000.0, -500000.0),  # Large negative values
            (0.001, 0.001),  # Small positive values
            (-0.001, -0.001),  # Small negative values
        ],
    )
    def test_월드_스크린_왕복_변환_정확성_검증_성공_시나리오(
        self,
        transformer: ICoordinateTransformer,
        world_x: float,
        world_y: float,
    ) -> None:
        """1. 월드-스크린 왕복 변환 정확성 검증 (성공 시나리오)

        목적: world → screen → world 변환 후 원래 좌표 복원 검증
        테스트할 범위: world_to_screen, screen_to_world의 수학적 정확성
        커버하는 함수 및 데이터: 다양한 좌표값의 변환 정확성
        기대되는 안정성: 왕복 변환 후 1픽셀 이내 오차 보장
        """
        # Given - 테스트 월드 좌표
        original_world = Vector2(world_x, world_y)

        # When - 월드 → 스크린 → 월드 변환
        screen_pos = transformer.world_to_screen(original_world)
        restored_world = transformer.screen_to_world(screen_pos)

        # Then - 왕복 변환 정확성 검증 (1픽셀 이내 허용)
        distance = original_world.distance_to(restored_world)
        assert distance < 1.0, (
            f'왕복 변환 오차가 1픽셀을 초과: {distance:.6f} '
            f'(원본: {original_world}, 복원: {restored_world})'
        )

    @pytest.mark.parametrize(
        'screen_x,screen_y',
        [
            (0.0, 0.0),  # Top-left corner
            (1024.0, 768.0),  # Bottom-right corner
            (512.0, 384.0),  # Screen center
            (256.0, 192.0),  # Quarter screen
            (768.0, 576.0),  # Three-quarters screen
            (-100.0, -50.0),  # Outside screen (negative)
            (1200.0, 900.0),  # Outside screen (positive)
        ],
    )
    def test_스크린_월드_왕복_변환_정확성_검증_성공_시나리오(
        self,
        transformer: ICoordinateTransformer,
        screen_x: float,
        screen_y: float,
    ) -> None:
        """2. 스크린-월드 왕복 변환 정확성 검증 (성공 시나리오)

        목적: screen → world → screen 변환 후 원래 좌표 복원 검증
        테스트할 범위: screen_to_world, world_to_screen의 수학적 정확성
        커버하는 함수 및 데이터: 화면 내외 다양한 스크린 좌표
        기대되는 안정성: 왕복 변환 후 1픽셀 이내 오차 보장
        """
        # Given - 테스트 스크린 좌표
        original_screen = Vector2(screen_x, screen_y)

        # When - 스크린 → 월드 → 스크린 변환
        world_pos = transformer.screen_to_world(original_screen)
        restored_screen = transformer.world_to_screen(world_pos)

        # Then - 왕복 변환 정확성 검증 (1픽셀 이내 허용)
        distance = original_screen.distance_to(restored_screen)
        assert distance < 1.0, (
            f'왕복 변환 오차가 1픽셀을 초과: {distance:.6f} '
            f'(원본: {original_screen}, 복원: {restored_screen})'
        )

    @pytest.mark.parametrize(
        'camera_x,camera_y',
        [
            (0.0, 0.0),  # No offset
            (100.0, 50.0),  # Positive offset
            (-100.0, -50.0),  # Negative offset
            (1000.0, 500.0),  # Large offset
            (-1000.0, -500.0),  # Large negative offset
            (0.1, 0.1),  # Small offset
            (-0.1, -0.1),  # Small negative offset
        ],
    )
    def test_카메라_오프셋_변경_시_변환_정확성_검증_성공_시나리오(
        self,
        transformer: ICoordinateTransformer,
        camera_x: float,
        camera_y: float,
    ) -> None:
        """3. 카메라 오프셋 변경 시 변환 정확성 검증 (성공 시나리오)

        목적: 카메라 오프셋 적용 시 좌표 변환의 수학적 정확성 검증
        테스트할 범위: set_camera_offset과 변환 함수들의 연동
        커버하는 함수 및 데이터: 다양한 카메라 오프셋 값
        기대되는 안정성: 카메라 이동 시에도 변환 정확성 유지
        """
        # Given - 카메라 오프셋 설정
        camera_offset = Vector2(camera_x, camera_y)
        transformer.set_camera_offset(camera_offset)

        # Test world coordinates
        test_world = Vector2(200.0, 150.0)

        # When - 왕복 변환 수행
        screen_pos = transformer.world_to_screen(test_world)
        restored_world = transformer.screen_to_world(screen_pos)

        # Then - 정확성 검증
        distance = test_world.distance_to(restored_world)
        assert distance < 1.0, (
            f'카메라 오프셋 {camera_offset}에서 왕복 변환 오차 초과: '
            f'{distance:.6f}'
        )

        # 카메라 오프셋이 올바르게 적용되었는지 확인
        assert transformer.get_camera_offset() == camera_offset, (
            '카메라 오프셋이 정확히 설정되어야 함'
        )

    @pytest.mark.parametrize(
        'zoom_level',
        [
            0.1,  # Minimum zoom
            0.5,  # Half zoom
            1.0,  # Normal zoom
            1.5,  # 1.5x zoom
            2.0,  # 2x zoom
            5.0,  # 5x zoom
            10.0,  # Maximum zoom (typically)
        ],
    )
    def test_줌_레벨_변경_시_변환_정확성_검증_성공_시나리오(
        self, transformer: ICoordinateTransformer, zoom_level: float
    ) -> None:
        """4. 줌 레벨 변경 시 변환 정확성 검증 (성공 시나리오)

        목적: 줌 레벨 변화 시 좌표 변환의 수학적 정확성 검증
        테스트할 범위: zoom_level 속성과 변환 함수들의 연동
        커버하는 함수 및 데이터: 최소/최대/일반적인 줌 레벨
        기대되는 안정성: 줌 레벨 변화 시에도 변환 정확성 유지
        """
        # Given - 줌 레벨 설정
        transformer.zoom_level = zoom_level

        # Test coordinates
        test_world = Vector2(100.0, 75.0)

        # When - 왕복 변환 수행
        screen_pos = transformer.world_to_screen(test_world)
        restored_world = transformer.screen_to_world(screen_pos)

        # Then - 정확성 검증
        distance = test_world.distance_to(restored_world)
        assert distance < 1.0, (
            f'줌 레벨 {zoom_level}에서 왕복 변환 오차 초과: {distance:.6f}'
        )

        # 줌 레벨이 올바르게 설정되었는지 확인
        expected_zoom = max(
            0.1, min(10.0, zoom_level)
        )  # CameraBasedTransformer 제약
        assert abs(transformer.zoom_level - expected_zoom) < 0.001, (
            f'줌 레벨이 정확히 설정되어야 함: 예상 {expected_zoom}, '
            f'실제 {transformer.zoom_level}'
        )

    def test_화면_크기_변경_시_변환_정확성_검증_성공_시나리오(
        self, transformer: ICoordinateTransformer
    ) -> None:
        """5. 화면 크기 변경 시 변환 정확성 검증 (성공 시나리오)

        목적: 화면 크기 변화 시 좌표 변환의 수학적 정확성 검증
        테스트할 범위: screen_size 속성과 변환 함수들의 연동
        커버하는 함수 및 데이터: 일반적인 화면 해상도들
        기대되는 안정성: 화면 크기 변화 시에도 변환 정확성 유지
        """
        # Test different screen sizes
        screen_sizes = [
            Vector2(800, 600),  # 4:3 ratio
            Vector2(1280, 720),  # 16:9 HD
            Vector2(1920, 1080),  # 16:9 Full HD
            Vector2(2560, 1440),  # 16:9 QHD
            Vector2(1024, 1024),  # Square
            Vector2(400, 300),  # Small screen
        ]

        test_world = Vector2(50.0, 25.0)

        for screen_size in screen_sizes:
            # Given - 화면 크기 설정
            transformer.screen_size = screen_size

            # When - 왕복 변환 수행
            screen_pos = transformer.world_to_screen(test_world)
            restored_world = transformer.screen_to_world(screen_pos)

            # Then - 정확성 검증
            distance = test_world.distance_to(restored_world)
            assert distance < 1.0, (
                f'화면 크기 {screen_size}에서 왕복 변환 오차 초과: '
                f'{distance:.6f}'
            )

            # 화면 크기가 올바르게 설정되었는지 확인
            assert transformer.screen_size == screen_size, (
                f'화면 크기가 정확히 설정되어야 함: {screen_size}'
            )

    def test_복합_변환_상황_정확성_검증_성공_시나리오(
        self, transformer: ICoordinateTransformer
    ) -> None:
        """6. 복합 변환 상황 정확성 검증 (성공 시나리오)

        목적: 카메라 오프셋, 줌, 화면 크기가 모두 적용된 복합 상황 검증
        테스트할 범위: 모든 변환 파라미터가 동시 적용된 상황
        커버하는 함수 및 데이터: 실제 게임 상황과 유사한 복합 설정
        기대되는 안정성: 복합 변환 시에도 정확성 보장
        """
        # Given - 복합 설정 적용
        transformer.screen_size = Vector2(1920, 1080)
        transformer.set_camera_offset(Vector2(150.0, 75.0))
        transformer.zoom_level = 1.5

        # 다양한 월드 좌표에 대해 테스트
        test_coordinates = [
            Vector2(0.0, 0.0),
            Vector2(100.0, 50.0),
            Vector2(-100.0, -50.0),
            Vector2(500.0, 250.0),
            Vector2(-500.0, -250.0),
        ]

        for world_pos in test_coordinates:
            # When - 왕복 변환 수행
            screen_pos = transformer.world_to_screen(world_pos)
            restored_world = transformer.screen_to_world(screen_pos)

            # Then - 정확성 검증
            distance = world_pos.distance_to(restored_world)
            assert distance < 1.0, (
                f'복합 변환에서 {world_pos} 왕복 변환 오차 초과: '
                f'{distance:.6f} (스크린: {screen_pos}, '
                f'복원: {restored_world})'
            )

    def test_극값_좌표_변환_안정성_검증_성공_시나리오(
        self, transformer: ICoordinateTransformer
    ) -> None:
        """7. 극값 좌표 변환 안정성 검증 (성공 시나리오)

        목적: 매우 큰 값이나 작은 값의 좌표 변환 시 안정성 검증
        테스트할 범위: float의 극값에 가까운 좌표들의 변환
        커버하는 함수 및 데이터: 극값 좌표, 무한대, NaN 경계
        기대되는 안정성: 극값에서도 계산 오류 없음
        """
        # Test extreme but valid coordinates
        extreme_coordinates = [
            Vector2(1e6, 1e6),  # Very large positive
            Vector2(-1e6, -1e6),  # Very large negative
            Vector2(1e-6, 1e-6),  # Very small positive
            Vector2(-1e-6, -1e-6),  # Very small negative
            Vector2(1e6, -1e6),  # Mixed large values
            Vector2(-1e6, 1e6),  # Mixed large values
        ]

        for world_pos in extreme_coordinates:
            # When - 변환 수행 (예외 없이 완료되어야 함)
            try:
                screen_pos = transformer.world_to_screen(world_pos)
                restored_world = transformer.screen_to_world(screen_pos)

                # Then - 유한한 값인지 확인
                assert math.isfinite(screen_pos.x) and math.isfinite(
                    screen_pos.y
                ), f'스크린 좌표가 유한하지 않음: {screen_pos}'
                assert math.isfinite(restored_world.x) and math.isfinite(
                    restored_world.y
                ), f'복원된 월드 좌표가 유한하지 않음: {restored_world}'

                # 왕복 변환 정확성 확인 (극값에서는 관대한 허용치)
                distance = world_pos.distance_to(restored_world)
                relative_error = distance / max(
                    abs(world_pos.x), abs(world_pos.y), 1.0
                )
                # 매우 작은 좌표값에서는 부동소수점 정밀도로 큰 오차 허용
                max_relative_error = (
                    1e-3
                    if max(abs(world_pos.x), abs(world_pos.y)) < 1e-3
                    else 1e-6
                )
                assert relative_error < max_relative_error, (
                    f'극값 {world_pos}에서 상대 오차 초과: {relative_error} '
                    f'(허용치: {max_relative_error})'
                )

            except (OverflowError, ZeroDivisionError) as e:
                pytest.fail(f'극값 좌표 {world_pos} 변환 중 예외 발생: {e}')

    def test_연속_변환_누적_오차_검증_성공_시나리오(
        self, transformer: ICoordinateTransformer
    ) -> None:
        """8. 연속 변환 누적 오차 검증 (성공 시나리오)

        목적: 다수 변환 시 오차 누적이 허용 범위 내인지 검증
        테스트할 범위: 반복적인 왕복 변환에서의 오차 누적
        커버하는 함수 및 데이터: 100회 연속 왕복 변환
        기대되는 안정성: 연속 변환에서도 누적 오차 제한
        """
        # Given - 초기 월드 좌표
        original_world = Vector2(100.0, 75.0)
        current_world = original_world.copy()

        # When - 100회 왕복 변환 수행
        for _i in range(100):
            screen_pos = transformer.world_to_screen(current_world)
            current_world = transformer.screen_to_world(screen_pos)

        # Then - 누적 오차 검증
        accumulated_error = original_world.distance_to(current_world)
        assert accumulated_error < 10.0, (  # 100회 변환 후 10픽셀 이내 허용
            f'100회 연속 변환 후 누적 오차 초과: {accumulated_error:.6f}'
        )

    @pytest.mark.parametrize(
        'angle_degrees', [0, 45, 90, 135, 180, 225, 270, 315]
    )
    def test_방향별_변환_일관성_검증_성공_시나리오(
        self, transformer: ICoordinateTransformer, angle_degrees: int
    ) -> None:
        """9. 방향별 변환 일관성 검증 (성공 시나리오)

        목적: 모든 방향에서 변환 정확성이 일관되게 유지되는지 검증
        테스트할 범위: 8방향 단위 벡터들의 변환 정확성
        커버하는 함수 및 데이터: 0~315도 방향의 단위 벡터들
        기대되는 안정성: 방향에 관계없이 일관된 변환 정확성
        """
        # Given - 특정 방향의 단위 벡터 생성
        angle_radians = math.radians(angle_degrees)
        distance = 100.0

        world_pos = Vector2(
            distance * math.cos(angle_radians),
            distance * math.sin(angle_radians),
        )

        # When - 왕복 변환 수행
        screen_pos = transformer.world_to_screen(world_pos)
        restored_world = transformer.screen_to_world(screen_pos)

        # Then - 정확성 검증
        error_distance = world_pos.distance_to(restored_world)
        assert error_distance < 1.0, (
            f'{angle_degrees}도 방향에서 변환 오차 초과: {error_distance:.6f} '
            f'(원본: {world_pos}, 복원: {restored_world})'
        )

        # 방향 보존 검증 - 원점에서의 방향각이 유지되는지 확인
        original_angle = math.atan2(world_pos.y, world_pos.x)
        restored_angle = math.atan2(restored_world.y, restored_world.x)

        angle_difference = abs(original_angle - restored_angle)
        # 각도 차이가 ±π를 넘으면 2π를 빼서 정규화
        if angle_difference > math.pi:
            angle_difference = 2 * math.pi - angle_difference

        assert angle_difference < 0.01, (  # 약 0.57도 이내 허용
            f'{angle_degrees}도 방향에서 각도 변화 초과: '
            f'{math.degrees(angle_difference):.3f}도'
        )


class TestCoordinateTransformationEdgeCases:
    """Test coordinate transformation edge cases and boundary conditions."""

    @pytest.fixture
    def transformer(self) -> CameraBasedTransformer:
        """Create transformer for edge case testing."""
        return CameraBasedTransformer(Vector2(800, 600))

    def test_제로_벡터_변환_안전성_검증_성공_시나리오(
        self, transformer: CameraBasedTransformer
    ) -> None:
        """10. 제로 벡터 변환 안전성 검증 (성공 시나리오)

        목적: 영점 좌표의 변환이 안전하게 처리되는지 검증
        테스트할 범위: Vector2.zero() 좌표의 변환
        커버하는 함수 및 데이터: 원점 좌표의 변환 결과
        기대되는 안정성: 영점에서도 정확한 변환 수행
        """
        # Given - 제로 벡터
        zero_world = Vector2.zero()
        zero_screen = Vector2.zero()

        # When & Then - 월드 제로 벡터 변환
        screen_result = transformer.world_to_screen(zero_world)
        assert math.isfinite(screen_result.x) and math.isfinite(
            screen_result.y
        ), '제로 월드 좌표 변환 결과가 유한해야 함'

        # When & Then - 스크린 제로 벡터 변환
        world_result = transformer.screen_to_world(zero_screen)
        assert math.isfinite(world_result.x) and math.isfinite(
            world_result.y
        ), '제로 스크린 좌표 변환 결과가 유한해야 함'

    def test_줌_레벨_경계값_처리_검증_성공_시나리오(
        self, transformer: CameraBasedTransformer
    ) -> None:
        """11. 줌 레벨 경계값 처리 검증 (성공 시나리오)

        목적: 줌 레벨의 최소/최대 경계값에서 안전한 처리 검증
        테스트할 범위: zoom_level의 제약 조건 적용
        커버하는 함수 및 데이터: 0.1 ~ 10.0 범위의 줌 레벨 제약
        기대되는 안정성: 경계값에서도 안전한 줌 레벨 적용
        """
        test_world = Vector2(100.0, 50.0)

        # Test minimum zoom boundary
        transformer.zoom_level = 0.05  # Below minimum
        assert transformer.zoom_level >= 0.1, '최소 줌 레벨이 적용되어야 함'

        screen_pos = transformer.world_to_screen(test_world)
        restored_world = transformer.screen_to_world(screen_pos)
        assert test_world.distance_to(restored_world) < 1.0, (
            '최소 줌 레벨에서도 변환 정확성 유지'
        )

        # Test maximum zoom boundary
        transformer.zoom_level = 15.0  # Above maximum
        assert transformer.zoom_level <= 10.0, '최대 줌 레벨이 적용되어야 함'

        screen_pos = transformer.world_to_screen(test_world)
        restored_world = transformer.screen_to_world(screen_pos)
        assert test_world.distance_to(restored_world) < 1.0, (
            '최대 줌 레벨에서도 변환 정확성 유지'
        )

    def test_매우_작은_화면_크기_처리_검증_성공_시나리오(
        self, transformer: CameraBasedTransformer
    ) -> None:
        """12. 매우 작은 화면 크기 처리 검증 (성공 시나리오)

        목적: 극소 화면 크기에서도 변환이 안전하게 처리되는지 검증
        테스트할 범위: 1x1 ~ 10x10 픽셀 화면에서의 변환
        커버하는 함수 및 데이터: 극소 화면 크기의 변환 안정성
        기대되는 안정성: 작은 화면에서도 계산 오류 없음
        """
        small_screen_sizes = [
            Vector2(1, 1),
            Vector2(2, 2),
            Vector2(5, 5),
            Vector2(10, 10),
        ]

        test_world = Vector2(1.0, 1.0)

        for screen_size in small_screen_sizes:
            transformer.screen_size = screen_size

            # Should not crash or produce invalid results
            try:
                screen_pos = transformer.world_to_screen(test_world)
                restored_world = transformer.screen_to_world(screen_pos)

                # Verify finite results
                assert math.isfinite(screen_pos.x) and math.isfinite(
                    screen_pos.y
                ), (
                    f'화면 크기 {screen_size}에서 유한한 스크린 좌표 '
                    '생성되어야 함'
                )
                assert math.isfinite(restored_world.x) and math.isfinite(
                    restored_world.y
                ), (
                    f'화면 크기 {screen_size}에서 유한한 월드 좌표 '
                    '복원되어야 함'
                )

                # Allow larger error tolerance for very small screens
                distance = test_world.distance_to(restored_world)
                max_allowed_error = max(
                    10.0, 100.0 / min(screen_size.x, screen_size.y)
                )
                assert distance < max_allowed_error, (
                    f'화면 크기 {screen_size}에서 허용 오차 '
                    f'{max_allowed_error} 초과: {distance}'
                )

            except (ZeroDivisionError, OverflowError) as e:
                pytest.fail(f'작은 화면 크기 {screen_size}에서 예외 발생: {e}')


class TestCoordinateTransformerPolymorphism:
    """Test polymorphic interface compatibility for all coordinate transformers."""

    @pytest.fixture
    def screen_size(self) -> Vector2:
        """Return standard screen size for testing."""
        return Vector2(1024, 768)

    @pytest.fixture
    def transformer_implementations(
        self, screen_size: Vector2
    ) -> list[ICoordinateTransformer]:
        """Return all transformer implementations for polymorphism testing."""
        return [
            CameraBasedTransformer(screen_size),
            CachedCameraTransformer(screen_size, cache_size=50),
        ]

    def test_인터페이스_메서드_시그니처_호환성_검증_성공_시나리오(
        self, transformer_implementations: list[ICoordinateTransformer]
    ) -> None:
        """1. 인터페이스 메서드 시그니처 호환성 검증 (성공 시나리오)

        목적: 모든 구현체가 ICoordinateTransformer 인터페이스를 올바르게 구현하는지 검증
        테스트할 범위: 모든 추상 메서드와 속성의 시그니처 호환성
        커버하는 함수 및 데이터: ICoordinateTransformer의 모든 메서드
        기대되는 안정성: 모든 구현체가 동일한 인터페이스 제공
        """
        required_methods = [
            'world_to_screen',
            'screen_to_world',
            'get_camera_offset',
            'set_camera_offset',
            'invalidate_cache',
            'transform',
            'is_point_visible',
        ]

        required_properties = ['zoom_level', 'screen_size']

        for transformer in transformer_implementations:
            # Given - 각 변환기 구현체
            transformer_type = type(transformer).__name__

            # When & Then - 필수 메서드 존재 확인
            for method_name in required_methods:
                assert hasattr(transformer, method_name), (
                    f'{transformer_type}에 {method_name} 메서드가 없음'
                )
                method = getattr(transformer, method_name)
                assert callable(method), (
                    f'{transformer_type}.{method_name}이 호출 가능하지 않음'
                )

            # When & Then - 필수 속성 존재 확인
            for property_name in required_properties:
                assert hasattr(transformer, property_name), (
                    f'{transformer_type}에 {property_name} 속성이 없음'
                )

    def test_모든_구현체_기본_변환_동작_일관성_검증_성공_시나리오(
        self, transformer_implementations: list[ICoordinateTransformer]
    ) -> None:
        """2. 모든 구현체 기본 변환 동작 일관성 검증 (성공 시나리오)

        목적: 모든 구현체가 동일한 입력에 대해 일관된 변환 결과를 제공하는지 검증
        테스트할 범위: 기본 world_to_screen, screen_to_world 변환 일관성
        커버하는 함수 및 데이터: 표준 좌표값들의 변환 결과 비교
        기대되는 안정성: 구현체별로 동일한 변환 결과 보장
        """
        test_coordinates = [
            Vector2(0.0, 0.0),
            Vector2(100.0, 50.0),
            Vector2(-100.0, -50.0),
            Vector2(500.0, 250.0),
        ]

        # Given - 모든 구현체를 동일한 초기 상태로 설정
        for transformer in transformer_implementations:
            transformer.set_camera_offset(Vector2.zero())
            transformer.zoom_level = 1.0
            transformer.screen_size = Vector2(1024, 768)

        for world_pos in test_coordinates:
            # When - 각 구현체에서 변환 수행
            screen_results = []
            for transformer in transformer_implementations:
                screen_pos = transformer.world_to_screen(world_pos)
                screen_results.append(screen_pos)

            # Then - 모든 구현체의 결과가 일관되는지 검증
            reference_result = screen_results[0]
            for i, screen_result in enumerate(screen_results[1:], 1):
                distance = reference_result.distance_to(screen_result)
                assert distance < 0.001, (
                    f'월드 좌표 {world_pos}에서 구현체 간 변환 결과 불일치: '
                    f'{type(transformer_implementations[0]).__name__}={reference_result}, '
                    f'{type(transformer_implementations[i]).__name__}={screen_result}, '
                    f'차이={distance}'
                )

    def test_속성_설정_동작_일관성_검증_성공_시나리오(
        self, transformer_implementations: list[ICoordinateTransformer]
    ) -> None:
        """3. 속성 설정 동작 일관성 검증 (성공 시나리오)

        목적: 모든 구현체가 속성 설정 시 동일한 동작을 보이는지 검증
        테스트할 범위: zoom_level, screen_size, camera_offset 속성 설정
        커버하는 함수 및 데이터: 다양한 속성값 설정과 조회
        기대되는 안정성: 속성 설정/조회 동작 일관성
        """
        test_cases = [
            {
                'zoom_level': 2.0,
                'screen_size': Vector2(1920, 1080),
                'camera_offset': Vector2(100.0, 50.0),
            },
            {
                'zoom_level': 0.5,
                'screen_size': Vector2(800, 600),
                'camera_offset': Vector2(-50.0, -25.0),
            },
        ]

        for test_case in test_cases:
            for transformer in transformer_implementations:
                transformer_type = type(transformer).__name__

                # When - 속성 설정
                transformer.zoom_level = test_case['zoom_level']
                transformer.screen_size = test_case['screen_size']
                transformer.set_camera_offset(test_case['camera_offset'])

                # Then - 속성 조회 결과 확인
                assert (
                    abs(transformer.zoom_level - test_case['zoom_level'])
                    < 0.001
                ), f'{transformer_type}: 줌 레벨 설정 불일치'
                assert transformer.screen_size == test_case['screen_size'], (
                    f'{transformer_type}: 화면 크기 설정 불일치'
                )
                assert (
                    transformer.get_camera_offset()
                    == test_case['camera_offset']
                ), f'{transformer_type}: 카메라 오프셋 설정 불일치'

    def test_변환기_교체_시_동작_일관성_검증_성공_시나리오(
        self, transformer_implementations: list[ICoordinateTransformer]
    ) -> None:
        """4. 변환기 교체 시 동작 일관성 검증 (성공 시나리오)

        목적: 런타임에 변환기를 교체해도 동일한 결과를 얻을 수 있는지 검증
        테스트할 범위: 변환기 교체 후 동일 상태에서의 변환 결과 일관성
        커버하는 함수 및 데이터: 상태 복사 및 교체 시나리오
        기대되는 안정성: 변환기 교체 시에도 결과 일관성 보장
        """
        # Given - 기준 변환기 설정
        reference_transformer = transformer_implementations[0]
        reference_transformer.zoom_level = 1.5
        reference_transformer.screen_size = Vector2(1280, 720)
        reference_transformer.set_camera_offset(Vector2(200.0, 100.0))

        test_world = Vector2(150.0, 75.0)
        reference_screen = reference_transformer.world_to_screen(test_world)

        # When & Then - 다른 변환기들을 동일 상태로 설정하여 결과 비교
        for other_transformer in transformer_implementations[1:]:
            # 동일한 상태로 설정
            other_transformer.zoom_level = reference_transformer.zoom_level
            other_transformer.screen_size = reference_transformer.screen_size
            other_transformer.set_camera_offset(
                reference_transformer.get_camera_offset()
            )

            # 변환 결과 비교
            other_screen = other_transformer.world_to_screen(test_world)
            distance = reference_screen.distance_to(other_screen)

            assert distance < 0.001, (
                f'변환기 교체 시 결과 불일치: '
                f'{type(reference_transformer).__name__}={reference_screen}, '
                f'{type(other_transformer).__name__}={other_screen}, '
                f'차이={distance}'
            )

    def test_transform_메서드_다형성_호환성_검증_성공_시나리오(
        self, transformer_implementations: list[ICoordinateTransformer]
    ) -> None:
        """5. transform 메서드 다형성 호환성 검증 (성공 시나리오)

        목적: ICoordinateTransformer의 transform 메서드가 모든 구현체에서 올바르게 작동하는지 검증
        테스트할 범위: CoordinateSpace enum을 사용한 transform 메서드
        커버하는 함수 및 데이터: WORLD-SCREEN 양방향 변환
        기대되는 안정성: 통합 transform 메서드의 다형성 지원
        """
        from src.core.coordinate_transformer import CoordinateSpace

        test_position = Vector2(100.0, 50.0)

        for transformer in transformer_implementations:
            transformer_type = type(transformer).__name__

            # When - transform 메서드로 양방향 변환
            screen_via_transform = transformer.transform(
                test_position, CoordinateSpace.WORLD, CoordinateSpace.SCREEN
            )

            world_via_transform = transformer.transform(
                test_position, CoordinateSpace.SCREEN, CoordinateSpace.WORLD
            )

            # Then - 직접 메서드 호출 결과와 비교
            screen_via_direct = transformer.world_to_screen(test_position)
            world_via_direct = transformer.screen_to_world(test_position)

            assert screen_via_transform == screen_via_direct, (
                f'{transformer_type}: transform 메서드와 직접 호출 결과 불일치 (world_to_screen)'
            )
            assert world_via_transform == world_via_direct, (
                f'{transformer_type}: transform 메서드와 직접 호출 결과 불일치 (screen_to_world)'
            )

            # 동일 공간 변환 테스트
            same_space_result = transformer.transform(
                test_position, CoordinateSpace.WORLD, CoordinateSpace.WORLD
            )
            assert same_space_result == test_position, (
                f'{transformer_type}: 동일 공간 변환 시 원본 반환해야 함'
            )

    def test_is_point_visible_메서드_호환성_검증_성공_시나리오(
        self, transformer_implementations: list[ICoordinateTransformer]
    ) -> None:
        """6. is_point_visible 메서드 호환성 검증 (성공 시나리오)

        목적: 모든 구현체의 is_point_visible 메서드가 일관된 결과를 제공하는지 검증
        테스트할 범위: 화면 내외부 좌표에 대한 가시성 판단
        커버하는 함수 및 데이터: 화면 중앙, 경계, 외부 좌표
        기대되는 안정성: 가시성 판단 결과 일관성
        """
        # Given - 모든 구현체를 동일한 상태로 설정
        for transformer in transformer_implementations:
            transformer.screen_size = Vector2(800, 600)
            transformer.set_camera_offset(Vector2.zero())
            transformer.zoom_level = 1.0

        test_cases = [
            (Vector2(0.0, 0.0), True),  # 화면 중앙 (가시)
            (Vector2(-500.0, 0.0), False),  # 화면 왼쪽 외부 (불가시)
            (Vector2(500.0, 0.0), False),  # 화면 오른쪽 외부 (불가시)
            (Vector2(0.0, -400.0), False),  # 화면 위쪽 외부 (불가시)
            (Vector2(0.0, 400.0), False),  # 화면 아래쪽 외부 (불가시)
        ]

        for world_pos, expected_visible in test_cases:
            visibility_results = []

            # When - 각 구현체에서 가시성 판단
            for transformer in transformer_implementations:
                is_visible = transformer.is_point_visible(world_pos)
                visibility_results.append(is_visible)

            # Then - 모든 구현체의 결과가 일관되는지 검증
            for i, is_visible in enumerate(visibility_results):
                transformer_type = type(
                    transformer_implementations[i]
                ).__name__
                assert is_visible == expected_visible, (
                    f'{transformer_type}: {world_pos}의 가시성 판단 오류 '
                    f'(예상: {expected_visible}, 실제: {is_visible})'
                )

            # 모든 구현체 간 결과 일치 확인
            reference_result = visibility_results[0]
            for i, result in enumerate(visibility_results[1:], 1):
                assert result == reference_result, (
                    f'{world_pos}에서 구현체 간 가시성 판단 불일치: '
                    f'{type(transformer_implementations[0]).__name__}={reference_result}, '
                    f'{type(transformer_implementations[i]).__name__}={result}'
                )

    def test_캐시_무효화_동작_일관성_검증_성공_시나리오(
        self, transformer_implementations: list[ICoordinateTransformer]
    ) -> None:
        """7. 캐시 무효화 동작 일관성 검증 (성공 시나리오)

        목적: invalidate_cache 메서드가 모든 구현체에서 올바르게 작동하는지 검증
        테스트할 범위: 캐시 무효화 후 변환 결과 일관성
        커버하는 함수 및 데이터: 캐시 무효화 전후 변환 결과 비교
        기대되는 안정성: 캐시 상태와 관계없이 일관된 변환 결과
        """
        test_world = Vector2(100.0, 50.0)

        for transformer in transformer_implementations:
            transformer_type = type(transformer).__name__

            # Given - 초기 변환 수행
            initial_screen = transformer.world_to_screen(test_world)

            # When - 캐시 무효화
            transformer.invalidate_cache()

            # Then - 캐시 무효화 후에도 동일한 결과
            after_invalidation_screen = transformer.world_to_screen(test_world)

            distance = initial_screen.distance_to(after_invalidation_screen)
            assert distance < 0.001, (
                f'{transformer_type}: 캐시 무효화 후 변환 결과 변경됨 '
                f'(이전: {initial_screen}, 이후: {after_invalidation_screen}, 차이: {distance})'
            )

    def test_여러_구현체_동시_사용_독립성_검증_성공_시나리오(
        self, transformer_implementations: list[ICoordinateTransformer]
    ) -> None:
        """8. 여러 구현체 동시 사용 독립성 검증 (성공 시나리오)

        목적: 여러 변환기 인스턴스가 서로 영향을 주지 않고 독립적으로 작동하는지 검증
        테스트할 범위: 다른 설정의 여러 변환기 동시 운용
        커버하는 함수 및 데이터: 독립적인 상태 관리
        기대되는 안정성: 변환기 간 상태 격리 보장
        """
        # Given - 각 구현체를 서로 다른 설정으로 구성
        configs = [
            {'zoom': 1.0, 'offset': Vector2(0.0, 0.0)},
            {'zoom': 2.0, 'offset': Vector2(100.0, 50.0)},
        ]

        configured_transformers = []
        for i, transformer in enumerate(transformer_implementations):
            config = configs[i % len(configs)]
            transformer.zoom_level = config['zoom']
            transformer.set_camera_offset(config['offset'])
            configured_transformers.append((transformer, config))

        test_world = Vector2(50.0, 25.0)

        # When & Then - 각 변환기가 독립적인 결과 생성
        results = []
        for transformer, expected_config in configured_transformers:
            # 설정이 유지되는지 확인
            assert (
                abs(transformer.zoom_level - expected_config['zoom']) < 0.001
            ), '변환기 설정이 다른 인스턴스에 의해 영향받음'
            assert (
                transformer.get_camera_offset() == expected_config['offset']
            ), '변환기 오프셋이 다른 인스턴스에 의해 영향받음'

            screen_result = transformer.world_to_screen(test_world)
            results.append(screen_result)

        # 서로 다른 설정으로 인해 다른 결과가 나와야 함
        if len(results) > 1:
            distance = results[0].distance_to(results[1])
            assert distance > 1.0, (
                '서로 다른 설정의 변환기들이 동일한 결과를 생성함 (독립성 문제 의심)'
            )
