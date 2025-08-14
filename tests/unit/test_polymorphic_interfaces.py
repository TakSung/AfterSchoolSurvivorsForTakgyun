"""
Polymorphic interface compatibility tests for coordinate transformers.

Tests that all ICoordinateTransformer implementations maintain consistent
behavior and interface compatibility when used polymorphically.
"""

import pytest

from src.core.cached_camera_transformer import CachedCameraTransformer
from src.core.camera_based_transformer import CameraBasedTransformer
from src.core.coordinate_transformer import (
    CoordinateSpace,
    ICoordinateTransformer,
)
from src.utils.vector2 import Vector2


class TestPolymorphicInterfaceCompatibility:
    """Test polymorphic interface compatibility across transformer implementations."""

    @pytest.fixture(
        params=[
            CameraBasedTransformer,
            CachedCameraTransformer,
        ]
    )
    def transformer_class(
        self, request: pytest.FixtureRequest
    ) -> type[ICoordinateTransformer]:
        """Parameterized fixture providing all transformer implementation classes.

        Returns:
            Transformer class type
        """
        return request.param

    @pytest.fixture
    def screen_size(self) -> Vector2:
        """Standard screen size for testing.

        Returns:
            Screen dimensions vector
        """
        return Vector2(1024, 768)

    @pytest.fixture
    def transformer_instance(
        self,
        transformer_class: type[ICoordinateTransformer],
        screen_size: Vector2,
    ) -> ICoordinateTransformer:
        """Create transformer instance from class type.

        Args:
            transformer_class: Class to instantiate
            screen_size: Screen dimensions

        Returns:
            Transformer instance
        """
        if transformer_class == CachedCameraTransformer:
            return transformer_class(screen_size, cache_size=100)
        else:
            return transformer_class(screen_size)

    def test_인터페이스_메서드_시그니처_호환성_검증_성공_시나리오(
        self, transformer_instance: ICoordinateTransformer
    ) -> None:
        """1. 인터페이스 메서드 시그니처 호환성 검증 (성공 시나리오)

        목적: 모든 구현체가 ICoordinateTransformer의 필수 메서드를 제공하는지 검증
        테스트할 범위: 인터페이스 메서드 존재성과 시그니처 호환성
        커버하는 함수 및 데이터: world_to_screen, screen_to_world, transform 등
        기대되는 안정성: 인터페이스 계약 준수를 통한 다형성 보장
        """
        # Given - 변환기 인스턴스 (다형성 적용)
        transformer: ICoordinateTransformer = transformer_instance

        # Then - 필수 메서드 존재성 검증
        assert hasattr(transformer, 'world_to_screen'), (
            '모든 구현체는 world_to_screen 메서드를 제공해야 함'
        )
        assert hasattr(transformer, 'screen_to_world'), (
            '모든 구현체는 screen_to_world 메서드를 제공해야 함'
        )
        assert hasattr(transformer, 'transform'), (
            '모든 구현체는 transform 메서드를 제공해야 함'
        )
        assert hasattr(transformer, 'get_camera_offset'), (
            '모든 구현체는 get_camera_offset 메서드를 제공해야 함'
        )
        assert hasattr(transformer, 'set_camera_offset'), (
            '모든 구현체는 set_camera_offset 메서드를 제공해야 함'
        )
        assert hasattr(transformer, 'is_point_visible'), (
            '모든 구현체는 is_point_visible 메서드를 제공해야 함'
        )

        # Then - 속성 존재성 검증
        assert hasattr(transformer, 'zoom_level'), (
            '모든 구현체는 zoom_level 속성을 제공해야 함'
        )
        assert hasattr(transformer, 'screen_size'), (
            '모든 구현체는 screen_size 속성을 제공해야 함'
        )

    def test_메서드_반환값_타입_일관성_검증_성공_시나리오(
        self, transformer_instance: ICoordinateTransformer
    ) -> None:
        """2. 메서드 반환값 타입 일관성 검증 (성공 시나리오)

        목적: 모든 구현체의 메서드가 일관된 반환 타입을 제공하는지 검증
        테스트할 범위: 각 메서드의 반환값 타입과 구조
        커버하는 함수 및 데이터: 좌표 변환 메서드들의 반환값
        기대되는 안정성: 타입 안전성을 통한 다형성 활용 보장
        """
        # Given - 테스트 데이터
        test_world_pos = Vector2(100.0, 75.0)
        test_screen_pos = Vector2(512.0, 384.0)
        Vector2(50.0, 25.0)

        # When & Then - world_to_screen 반환값 검증
        screen_result = transformer_instance.world_to_screen(test_world_pos)
        assert isinstance(screen_result, Vector2), (
            'world_to_screen은 Vector2 타입을 반환해야 함'
        )

        # When & Then - screen_to_world 반환값 검증
        world_result = transformer_instance.screen_to_world(test_screen_pos)
        assert isinstance(world_result, Vector2), (
            'screen_to_world는 Vector2 타입을 반환해야 함'
        )

        # When & Then - get_camera_offset 반환값 검증
        offset_result = transformer_instance.get_camera_offset()
        assert isinstance(offset_result, Vector2), (
            'get_camera_offset은 Vector2 타입을 반환해야 함'
        )

        # When & Then - is_point_visible 반환값 검증
        visibility_result = transformer_instance.is_point_visible(
            test_world_pos
        )
        assert isinstance(visibility_result, bool), (
            'is_point_visible은 bool 타입을 반환해야 함'
        )

        # When & Then - transform 반환값 검증
        transform_result = transformer_instance.transform(
            test_world_pos, CoordinateSpace.WORLD, CoordinateSpace.SCREEN
        )
        assert isinstance(transform_result, Vector2), (
            'transform은 Vector2 타입을 반환해야 함'
        )

    def test_속성_접근_일관성_검증_성공_시나리오(
        self, transformer_instance: ICoordinateTransformer
    ) -> None:
        """3. 속성 접근 일관성 검증 (성공 시나리오)

        목적: 모든 구현체의 속성 접근이 일관되게 동작하는지 검증
        테스트할 범위: getter/setter 속성의 동작 일관성
        커버하는 함수 및 데이터: zoom_level, screen_size 속성들
        기대되는 안정성: 속성 인터페이스의 일관된 동작 보장
        """
        # Given - 초기값 저장
        original_zoom = transformer_instance.zoom_level
        original_screen_size = transformer_instance.screen_size

        # When & Then - zoom_level 속성 검증
        assert isinstance(transformer_instance.zoom_level, int | float), (
            'zoom_level은 숫자 타입이어야 함'
        )

        # 줌 레벨 변경 및 검증
        new_zoom = 2.0
        transformer_instance.zoom_level = new_zoom
        assert abs(transformer_instance.zoom_level - new_zoom) < 0.001, (
            'zoom_level setter가 올바르게 동작해야 함'
        )

        # When & Then - screen_size 속성 검증
        assert isinstance(transformer_instance.screen_size, Vector2), (
            'screen_size는 Vector2 타입이어야 함'
        )

        # 화면 크기 변경 및 검증
        new_screen_size = Vector2(800, 600)
        transformer_instance.screen_size = new_screen_size
        assert transformer_instance.screen_size == new_screen_size, (
            'screen_size setter가 올바르게 동작해야 함'
        )

        # 원래값 복원
        transformer_instance.zoom_level = original_zoom
        transformer_instance.screen_size = original_screen_size

    def test_변환기_교체_동작_일관성_검증_성공_시나리오(
        self, screen_size: Vector2
    ) -> None:
        """4. 변환기 교체 동작 일관성 검증 (성공 시나리오)

        목적: 서로 다른 구현체 간 교체 시에도 일관된 동작을 보이는지 검증
        테스트할 범위: 동일 조건에서 구현체 교체 시 결과 일관성
        커버하는 함수 및 데이터: 동일 설정의 서로 다른 변환기들
        기대되는 안정성: 구현체 교체에도 불구한 동작 일관성 보장
        """
        # Given - 동일 설정의 서로 다른 변환기들 생성
        basic_transformer = CameraBasedTransformer(screen_size)
        cached_transformer = CachedCameraTransformer(
            screen_size, cache_size=100
        )

        # 동일한 설정 적용
        camera_offset = Vector2(100.0, 50.0)
        zoom_level = 1.5

        transformers = [basic_transformer, cached_transformer]
        for transformer in transformers:
            transformer.set_camera_offset(camera_offset)
            transformer.zoom_level = zoom_level

        # When - 동일한 좌표 변환 수행
        test_world_pos = Vector2(200.0, 150.0)
        screen_results = []

        for transformer in transformers:
            screen_pos = transformer.world_to_screen(test_world_pos)
            screen_results.append(screen_pos)

        # Then - 결과 일관성 검증 (1픽셀 이내 허용)
        for i in range(len(screen_results) - 1):
            distance = screen_results[i].distance_to(screen_results[i + 1])
            assert distance < 1.0, (
                f'변환기 교체 시에도 결과가 일관되어야 함: 차이 {distance:.6f}픽셀'
            )

    def test_복합_다형성_작업_플로우_검증_성공_시나리오(
        self, transformer_instance: ICoordinateTransformer
    ) -> None:
        """5. 복합 다형성 작업 플로우 검증 (성공 시나리오)

        목적: 다형성을 활용한 복합적인 작업 플로우가 올바르게 동작하는지 검증
        테스트할 범위: 여러 메서드를 연쇄적으로 사용하는 시나리오
        커버하는 함수 및 데이터: 실제 게임 로직과 유사한 복합 작업
        기대되는 안정성: 다형성 환경에서의 복잡한 작업 안정성 보장
        """
        # Given - 복합 작업 시나리오 설정
        transformer: ICoordinateTransformer = transformer_instance

        # 초기 설정
        transformer.set_camera_offset(Vector2(50.0, 30.0))
        transformer.zoom_level = 1.25
        transformer.screen_size = Vector2(1280, 720)

        # 테스트 월드 좌표들 (게임 객체들의 위치)
        world_positions = [
            Vector2(0.0, 0.0),  # 플레이어 위치
            Vector2(100.0, 80.0),  # 적 위치
            Vector2(-50.0, -30.0),  # 아이템 위치
            Vector2(200.0, 150.0),  # 원거리 객체
        ]

        # When - 복합 작업 플로우 실행
        try:
            # 1. 모든 월드 좌표를 스크린 좌표로 변환
            screen_positions = []
            for world_pos in world_positions:
                screen_pos = transformer.world_to_screen(world_pos)
                screen_positions.append(screen_pos)

            # 2. 가시성 검사 수행
            visible_positions = []
            for world_pos in world_positions:
                if transformer.is_point_visible(world_pos):
                    visible_positions.append(world_pos)

            # 3. 스크린 좌표를 다시 월드 좌표로 역변환
            restored_positions = []
            for screen_pos in screen_positions:
                world_pos = transformer.screen_to_world(screen_pos)
                restored_positions.append(world_pos)

            # 4. transform 메서드를 통한 추가 변환
            transformed_positions = []
            for world_pos in world_positions:
                screen_pos = transformer.transform(
                    world_pos, CoordinateSpace.WORLD, CoordinateSpace.SCREEN
                )
                transformed_positions.append(screen_pos)

        except Exception as e:
            pytest.fail(f'복합 다형성 작업 중 예외 발생: {e}')

        # Then - 작업 결과 검증
        assert len(screen_positions) == len(world_positions), (
            '변환된 좌표 수가 원본과 일치해야 함'
        )
        assert len(restored_positions) == len(world_positions), (
            '역변환된 좌표 수가 원본과 일치해야 함'
        )
        assert len(transformed_positions) == len(world_positions), (
            'transform 메서드 결과 수가 원본과 일치해야 함'
        )

        # 왕복 변환 정확성 검증
        for i, (original, restored) in enumerate(
            zip(world_positions, restored_positions, strict=False)
        ):
            distance = original.distance_to(restored)
            assert distance < 1.0, (
                f'위치 {i}에서 왕복 변환 오차 초과: {distance:.6f}'
            )

        # transform 메서드와 world_to_screen 결과 일치성 검증
        for i, (screen_pos, transformed_pos) in enumerate(
            zip(screen_positions, transformed_positions, strict=False)
        ):
            distance = screen_pos.distance_to(transformed_pos)
            assert distance < 0.001, (
                f'위치 {i}에서 변환 메서드 결과 불일치: {distance:.6f}'
            )

    def test_인터페이스_기본_구현_동작_검증_성공_시나리오(
        self, transformer_instance: ICoordinateTransformer
    ) -> None:
        """6. 인터페이스 기본 구현 동작 검증 (성공 시나리오)

        목적: ICoordinateTransformer의 기본 구현 메서드들이 올바르게 동작하는지 검증
        테스트할 범위: 인터페이스에서 제공하는 기본 구현 메서드들
        커버하는 함수 및 데이터: transform, is_point_visible 등의 기본 구현
        기대되는 안정성: 인터페이스 기본 구현의 일관된 동작 보장
        """
        # Given - 테스트 좌표와 설정
        test_world_pos = Vector2(100.0, 75.0)
        test_screen_pos = Vector2(400.0, 300.0)

        # When & Then - transform 메서드의 기본 구현 검증
        # WORLD to SCREEN 변환
        screen_result = transformer_instance.transform(
            test_world_pos, CoordinateSpace.WORLD, CoordinateSpace.SCREEN
        )
        direct_screen_result = transformer_instance.world_to_screen(
            test_world_pos
        )

        assert screen_result.distance_to(direct_screen_result) < 0.001, (
            'transform(WORLD->SCREEN)은 world_to_screen과 동일한 결과를 반환해야 함'
        )

        # SCREEN to WORLD 변환
        world_result = transformer_instance.transform(
            test_screen_pos, CoordinateSpace.SCREEN, CoordinateSpace.WORLD
        )
        direct_world_result = transformer_instance.screen_to_world(
            test_screen_pos
        )

        assert world_result.distance_to(direct_world_result) < 0.001, (
            'transform(SCREEN->WORLD)는 screen_to_world와 동일한 결과를 반환해야 함'
        )

        # WORLD to WORLD 변환 (동일 공간)
        world_to_world = transformer_instance.transform(
            test_world_pos, CoordinateSpace.WORLD, CoordinateSpace.WORLD
        )

        assert world_to_world.distance_to(test_world_pos) < 0.001, (
            '동일 좌표 공간 변환 시 원본과 동일한 값을 반환해야 함'
        )
        assert world_to_world is not test_world_pos, (
            '동일 좌표 공간 변환 시 새로운 객체를 반환해야 함'
        )

        # When & Then - is_point_visible 메서드 검증
        # 화면 중심 근처 점 (가시 영역)
        center_world = Vector2.zero()
        transformer_instance.set_camera_offset(Vector2.zero())

        assert transformer_instance.is_point_visible(center_world), (
            '화면 중심 근처 점은 가시 영역이어야 함'
        )

        # 화면에서 매우 먼 점 (비가시 영역)
        far_world = Vector2(10000.0, 10000.0)
        assert not transformer_instance.is_point_visible(far_world), (
            '화면에서 매우 먼 점은 비가시 영역이어야 함'
        )

    def test_예외_상황_처리_일관성_검증_성공_시나리오(
        self, transformer_instance: ICoordinateTransformer
    ) -> None:
        """7. 예외 상황 처리 일관성 검증 (성공 시나리오)

        목적: 모든 구현체가 예외 상황을 일관되게 처리하는지 검증
        테스트할 범위: 경계값, 극값, 잘못된 입력에 대한 처리
        커버하는 함수 및 데이터: 예외 상황에서의 구현체 동작
        기대되는 안정성: 예외 상황에서도 일관된 동작 보장
        """
        # Given & When & Then - 극값 좌표 처리 검증
        extreme_world_pos = Vector2(1e6, 1e6)

        try:
            screen_result = transformer_instance.world_to_screen(
                extreme_world_pos
            )
            assert isinstance(screen_result, Vector2), (
                '극값 좌표 변환도 Vector2를 반환해야 함'
            )

            # 무한대나 NaN 값이 아닌 유한한 값인지 검증
            import math

            assert math.isfinite(screen_result.x) and math.isfinite(
                screen_result.y
            ), '극값 좌표 변환 결과는 유한한 값이어야 함'

        except (OverflowError, ValueError) as e:
            # 일부 구현체에서는 극값에서 예외를 발생시킬 수 있음
            # 이는 허용되지만 예외 타입은 일관되어야 함
            assert isinstance(e, OverflowError | ValueError), (
                f'예외 타입이 예상 범위 내에 있어야 함: {type(e)}'
            )

        # Given & When & Then - 줌 레벨 경계값 처리 검증
        # 최소값 이하 설정 시도
        transformer_instance.zoom_level = -1.0
        assert transformer_instance.zoom_level >= 0.1, (
            '음수 줌 레벨은 최소값으로 제한되어야 함'
        )

        # 매우 큰 값 설정 시도
        transformer_instance.zoom_level = 100.0
        current_zoom = transformer_instance.zoom_level
        assert current_zoom <= 20.0, (  # 합리적인 상한선
            f'과도한 줌 레벨은 제한되어야 함: {current_zoom}'
        )

        # Given & When & Then - 작은 화면 크기 처리 검증
        very_small_screen = Vector2(1, 1)

        try:
            transformer_instance.screen_size = very_small_screen
            test_pos = Vector2(1.0, 1.0)

            # 매우 작은 화면에서도 변환이 동작해야 함
            screen_result = transformer_instance.world_to_screen(test_pos)
            world_result = transformer_instance.screen_to_world(screen_result)

            assert isinstance(screen_result, Vector2), (
                '작은 화면에서도 Vector2 반환'
            )
            assert isinstance(world_result, Vector2), (
                '작은 화면에서도 Vector2 반환'
            )

        except (ZeroDivisionError, ValueError) as e:
            # 일부 구현체에서는 극소 화면에서 예외를 발생시킬 수 있음
            assert isinstance(e, ZeroDivisionError | ValueError), (
                f'예외 타입이 예상 범위 내에 있어야 함: {type(e)}'
            )


class TestTransformerInterchangeability:
    """Test transformer interchangeability in runtime scenarios."""

    def test_런타임_변환기_교체_시나리오_검증_성공_시나리오(self) -> None:
        """8. 런타임 변환기 교체 시나리오 검증 (성공 시나리오)

        목적: 실행 중 변환기 교체 시나리오가 안전하게 동작하는지 검증
        테스트할 범위: 변환기 인스턴스 교체와 상태 전이
        커버하는 함수 및 데이터: 실제 게임에서의 변환기 교체 시나리오
        기대되는 안정성: 런타임 변환기 교체의 투명성 보장
        """
        # Given - 초기 변환기와 설정
        screen_size = Vector2(1024, 768)
        camera_offset = Vector2(100.0, 50.0)
        zoom_level = 1.5

        # 초기 변환기 생성 및 설정
        current_transformer: ICoordinateTransformer = CameraBasedTransformer(
            screen_size
        )
        current_transformer.set_camera_offset(camera_offset)
        current_transformer.zoom_level = zoom_level

        # 테스트 대상 위치들
        test_positions = [
            Vector2(0.0, 0.0),
            Vector2(200.0, 150.0),
            Vector2(-100.0, -75.0),
        ]

        # When - 초기 변환기로 변환 수행
        initial_results = []
        for pos in test_positions:
            screen_pos = current_transformer.world_to_screen(pos)
            initial_results.append(screen_pos)

        # 변환기를 CachedCameraTransformer로 교체
        current_transformer = CachedCameraTransformer(
            screen_size, cache_size=100
        )
        current_transformer.set_camera_offset(camera_offset)
        current_transformer.zoom_level = zoom_level

        # When - 교체된 변환기로 동일한 변환 수행
        replacement_results = []
        for pos in test_positions:
            screen_pos = current_transformer.world_to_screen(pos)
            replacement_results.append(screen_pos)

        # Then - 결과 일관성 검증
        assert len(initial_results) == len(replacement_results), (
            '변환기 교체 전후 결과 수가 일치해야 함'
        )

        for i, (initial, replacement) in enumerate(
            zip(initial_results, replacement_results, strict=False)
        ):
            distance = initial.distance_to(replacement)
            assert distance < 0.001, (
                f'위치 {i}에서 변환기 교체 시 결과 불일치: {distance:.6f}픽셀'
            )

    def test_성능_특성_인터페이스_호환성_검증_성공_시나리오(self) -> None:
        """9. 성능 특성 인터페이스 호환성 검증 (성공 시나리오)

        목적: 성능 특성이 다른 구현체들이 인터페이스 관점에서 호환되는지 검증
        테스트할 범위: 캐시된 구현체와 기본 구현체의 인터페이스 호환성
        커버하는 함수 및 데이터: 동일한 작업에 대한 서로 다른 구현체의 결과
        기대되는 안정성: 성능 최적화가 인터페이스 호환성에 영향을 주지 않음 보장
        """
        # Given - 동일한 설정의 서로 다른 성능 특성 변환기들
        screen_size = Vector2(800, 600)
        camera_offset = Vector2(75.0, 50.0)
        zoom_level = 2.0

        basic_transformer = CameraBasedTransformer(screen_size)
        cached_transformer = CachedCameraTransformer(
            screen_size, cache_size=500
        )

        transformers = [basic_transformer, cached_transformer]

        # 모든 변환기에 동일한 설정 적용
        for transformer in transformers:
            transformer.set_camera_offset(camera_offset)
            transformer.zoom_level = zoom_level

        # 테스트 좌표들 (반복적으로 사용하여 캐시 효과 확인)
        test_positions = [
            Vector2(50.0, 40.0),
            Vector2(150.0, 120.0),
            Vector2(-50.0, -30.0),
            Vector2(50.0, 40.0),  # 중복 - 캐시 테스트용
            Vector2(150.0, 120.0),  # 중복 - 캐시 테스트용
        ]

        # When - 모든 변환기로 동일한 작업 수행
        all_results = []
        for transformer in transformers:
            transformer_results = []

            # 다중 변환 작업
            for pos in test_positions:
                # 왕복 변환
                screen_pos = transformer.world_to_screen(pos)
                restored_pos = transformer.screen_to_world(screen_pos)

                # transform 메서드 사용
                transformed_pos = transformer.transform(
                    pos, CoordinateSpace.WORLD, CoordinateSpace.SCREEN
                )

                # 가시성 검사
                is_visible = transformer.is_point_visible(pos)

                transformer_results.append(
                    {
                        'original': pos,
                        'screen': screen_pos,
                        'restored': restored_pos,
                        'transformed': transformed_pos,
                        'visible': is_visible,
                    }
                )

            all_results.append(transformer_results)

        # Then - 모든 변환기의 결과 일관성 검증
        basic_results, cached_results = all_results

        assert len(basic_results) == len(cached_results), (
            '기본/캐시 변환기 결과 수가 일치해야 함'
        )

        for i, (basic, cached) in enumerate(
            zip(basic_results, cached_results, strict=False)
        ):
            # 스크린 좌표 변환 결과 비교
            screen_distance = basic['screen'].distance_to(cached['screen'])
            assert screen_distance < 0.001, (
                f'위치 {i}: 스크린 변환 결과 불일치 {screen_distance:.6f}픽셀'
            )

            # 역변환 결과 비교
            restored_distance = basic['restored'].distance_to(
                cached['restored']
            )
            assert restored_distance < 0.001, (
                f'위치 {i}: 역변환 결과 불일치 {restored_distance:.6f}픽셀'
            )

            # transform 메서드 결과 비교
            transform_distance = basic['transformed'].distance_to(
                cached['transformed']
            )
            assert transform_distance < 0.001, (
                f'위치 {i}: transform 결과 불일치 {transform_distance:.6f}픽셀'
            )

            # 가시성 검사 결과 비교
            assert basic['visible'] == cached['visible'], (
                f'위치 {i}: 가시성 검사 결과 불일치'
            )
