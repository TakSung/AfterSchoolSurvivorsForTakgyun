from src.core.camera_based_transformer import CameraBasedTransformer
from src.utils.vector2 import Vector2


class TestCameraBasedTransformer:
    def test_카메라_변환기_초기화_정확성_검증_성공_시나리오(self) -> None:
        """1. CameraBasedTransformer 초기화 정확성 검증 (성공 시나리오)

        목적: CameraBasedTransformer 생성자와 초기 상태 검증
        테스트할 범위: __init__, 초기 속성 설정
        커버하는 함수 및 데이터: 화면 크기, 카메라 오프셋, 줌 레벨 초기화
        기대되는 안정성: 정확한 초기 상태 설정 보장
        """
        # Given & When - 기본 매개변수로 변환기 생성
        screen_size = Vector2(1024, 768)
        transformer = CameraBasedTransformer(screen_size)

        # Then - 초기 상태 확인
        assert transformer.screen_size == screen_size, (
            '화면 크기가 정확히 설정되어야 함'
        )
        assert transformer.get_camera_offset() == Vector2.zero(), (
            '기본 카메라 오프셋은 영벡터여야 함'
        )
        assert transformer.zoom_level == 1.0, '기본 줌 레벨은 1.0이어야 함'

        # Given & When - 모든 매개변수로 변환기 생성
        camera_offset = Vector2(100, 50)
        zoom_level = 2.0
        transformer_full = CameraBasedTransformer(
            screen_size, camera_offset, zoom_level
        )

        # Then - 설정된 값 확인
        assert transformer_full.get_camera_offset() == camera_offset, (
            '카메라 오프셋이 정확히 설정되어야 함'
        )
        assert transformer_full.zoom_level == zoom_level, (
            '줌 레벨이 정확히 설정되어야 함'
        )

    def test_기본_좌표_변환_정확성_검증_성공_시나리오(self) -> None:
        """2. 기본 좌표 변환 정확성 검증 (성공 시나리오)

        목적: world_to_screen과 screen_to_world 메서드의 기본 동작 검증
        테스트할 범위: world_to_screen, screen_to_world 메서드
        커버하는 함수 및 데이터: 기본 변환 수학적 계산
        기대되는 안정성: 왕복 변환 시 좌표 일관성 보장
        """
        # Given - 변환기 설정 (800x600 화면, 오프셋 없음, 줌 1배)
        transformer = CameraBasedTransformer(Vector2(800, 600))

        # When & Then - 월드 원점이 화면 중심으로 변환되는지 확인
        world_origin = Vector2.zero()
        screen_pos = transformer.world_to_screen(world_origin)
        expected_center = Vector2(400, 300)  # 800/2, 600/2

        assert screen_pos == expected_center, (
            '월드 원점이 화면 중심으로 변환되어야 함'
        )

        # When & Then - 왕복 변환 정확성 검증
        back_to_world = transformer.screen_to_world(screen_pos)
        assert world_origin.distance_to(back_to_world) < 0.001, (
            '왕복 변환 시 좌표가 일치해야 함'
        )

    def test_카메라_오프셋_적용_변환_검증_성공_시나리오(self) -> None:
        """3. 카메라 오프셋 적용 변환 검증 (성공 시나리오)

        목적: 카메라 오프셋 변경이 좌표 변환에 올바르게 반영되는지 검증
        테스트할 범위: set_camera_offset과 변환 결과
        커버하는 함수 및 데이터: 카메라 이동에 따른 좌표 변환 변화
        기대되는 안정성: 카메라 위치 변화에 따른 일관된 변환 보장
        """
        # Given - 변환기 설정
        transformer = CameraBasedTransformer(Vector2(800, 600))
        world_pos = Vector2(100, 100)

        # When - 카메라 오프셋 없이 변환
        screen_pos_no_offset = transformer.world_to_screen(world_pos)

        # When - 카메라 오프셋 설정 후 변환
        camera_offset = Vector2(50, 30)
        transformer.set_camera_offset(camera_offset)
        screen_pos_with_offset = transformer.world_to_screen(world_pos)

        # Then - 오프셋 적용 확인
        # 카메라 오프셋(50, 30)만큼 화면에서 객체가 이동해야 함
        offset_difference = screen_pos_no_offset - screen_pos_with_offset
        assert offset_difference.distance_to(Vector2(50, 30)) < 0.001, (
            '카메라 오프셋이 올바르게 적용되어야 함'
        )

    def test_줌_레벨_적용_변환_검증_성공_시나리오(self) -> None:
        """4. 줌 레벨 적용 변환 검증 (성공 시나리오)

        목적: 줌 레벨 변화가 좌표 변환에 올바르게 반영되는지 검증
        테스트할 범위: zoom_level 속성과 변환 결과
        커버하는 함수 및 데이터: 줌 배율에 따른 좌표 스케일링
        기대되는 안정성: 줌 레벨 변화에 따른 비례적 좌표 변환 보장
        """
        # Given - 변환기 설정
        transformer = CameraBasedTransformer(Vector2(800, 600))
        world_pos = Vector2(100, 100)

        # When - 줌 레벨 1배에서 변환
        transformer.zoom_level = 1.0
        screen_pos_zoom_1 = transformer.world_to_screen(world_pos)

        # When - 줌 레벨 2배로 설정 후 변환
        transformer.zoom_level = 2.0
        screen_pos_zoom_2 = transformer.world_to_screen(world_pos)

        # Then - 줌 레벨 적용 확인
        screen_center = Vector2(400, 300)
        offset_1 = screen_pos_zoom_1 - screen_center
        offset_2 = screen_pos_zoom_2 - screen_center

        # 줌 2배 시 화면 중심에서의 거리가 2배가 되어야 함
        expected_offset_2 = offset_1 * 2
        assert expected_offset_2.distance_to(offset_2) < 0.001, (
            '줌 레벨에 따른 스케일링이 정확해야 함'
        )

    def test_화면_크기_변경_변환_검증_성공_시나리오(self) -> None:
        """5. 화면 크기 변경 변환 검증 (성공 시나리오)

        목적: 화면 크기 변화가 좌표 변환에 올바르게 반영되는지 검증
        테스트할 범위: screen_size 속성과 변환 결과
        커버하는 함수 및 데이터: 화면 해상도 변화에 따른 중심점 계산
        기대되는 안정성: 화면 크기 변화에 따른 올바른 중심점 계산 보장
        """
        # Given - 변환기 설정
        transformer = CameraBasedTransformer(Vector2(800, 600))
        world_origin = Vector2.zero()

        # When - 기본 화면 크기에서 변환
        screen_pos_800x600 = transformer.world_to_screen(world_origin)

        # When - 화면 크기 변경 후 변환
        new_screen_size = Vector2(1024, 768)
        transformer.screen_size = new_screen_size
        screen_pos_1024x768 = transformer.world_to_screen(world_origin)

        # Then - 새로운 화면 중심으로 변환 확인
        expected_new_center = new_screen_size / 2
        assert screen_pos_1024x768.distance_to(expected_new_center) < 0.001, (
            '새로운 화면 중심으로 변환되어야 함'
        )

    def test_변환_매트릭스_캐싱_동작_검증_성공_시나리오(self) -> None:
        """6. 변환 매트릭스 캐싱 동작 검증 (성공 시나리오)

        목적: 변환 매트릭스 캐싱 메커니즘의 정확한 동작 검증
        테스트할 범위: get_transformation_matrix, 캐시 무효화
        커버하는 함수 및 데이터: 매트릭스 캐시 생성과 무효화
        기대되는 안정성: 효율적인 매트릭스 캐싱을 통한 성능 최적화 보장
        """
        # Given - 변환기 설정
        transformer = CameraBasedTransformer(Vector2(800, 600))

        # When - 첫 번째 매트릭스 조회
        matrix1 = transformer.get_transformation_matrix()
        cache_stats1 = transformer.get_cache_stats()

        # When - 두 번째 매트릭스 조회 (캐시 사용)
        matrix2 = transformer.get_transformation_matrix()
        cache_stats2 = transformer.get_cache_stats()

        # Then - 캐시 동작 확인
        assert matrix1 == matrix2, (
            '동일한 설정에서 같은 매트릭스가 반환되어야 함'
        )
        assert cache_stats1['has_transform_matrix'], (
            '첫 조회 후 매트릭스 캐시가 존재해야 함'
        )
        assert cache_stats2['has_transform_matrix'], (
            '두 번째 조회에서도 캐시가 유지되어야 함'
        )

        # When - 카메라 오프셋 변경으로 캐시 무효화
        transformer.set_camera_offset(Vector2(10, 10))
        cache_stats3 = transformer.get_cache_stats()

        # Then - 캐시 무효화 확인
        assert cache_stats3['cache_dirty'], (
            '설정 변경 시 캐시가 무효화되어야 함'
        )

    def test_다중_좌표_변환_성능_최적화_검증_성공_시나리오(self) -> None:
        """7. 다중 좌표 변환 성능 최적화 검증 (성공 시나리오)

        목적: transform_multiple_points 메서드의 성능 최적화 검증
        테스트할 범위: transform_multiple_points 메서드
        커버하는 함수 및 데이터: 매트릭스 기반 일괄 변환
        기대되는 안정성: 다수 좌표의 효율적 일괄 변환 보장
        """
        # Given - 변환기와 테스트 좌표들 설정
        transformer = CameraBasedTransformer(
            Vector2(800, 600), Vector2(50, 30), 1.5
        )
        world_positions = [
            Vector2(0, 0),
            Vector2(100, 50),
            Vector2(-50, -30),
            Vector2(200, 150),
        ]

        # When - 일괄 변환
        screen_positions = transformer.transform_multiple_points(
            world_positions
        )

        # When - 개별 변환
        individual_positions = [
            transformer.world_to_screen(pos) for pos in world_positions
        ]

        # Then - 결과 일치 확인
        assert len(screen_positions) == len(world_positions), (
            '변환된 좌표 개수가 일치해야 함'
        )

        for batch_pos, individual_pos in zip(
            screen_positions, individual_positions, strict=False
        ):
            assert batch_pos.distance_to(individual_pos) < 0.001, (
                '일괄 변환과 개별 변환 결과가 일치해야 함'
            )

    def test_월드_사각형_가시성_검사_정확성_검증_성공_시나리오(self) -> None:
        """8. 월드 사각형 가시성 검사 정확성 검증 (성공 시나리오)

        목적: is_world_rect_visible 메서드의 사각형 가시성 판단 정확성 검증
        테스트할 범위: is_world_rect_visible 메서드
        커버하는 함수 및 데이터: 사각형 영역의 화면 내 가시성 판단
        기대되는 안정성: 정확한 사각형 가시성 판단을 통한 렌더링 최적화 지원
        """
        # Given - 변환기 설정
        transformer = CameraBasedTransformer(Vector2(800, 600))

        # When & Then - 화면 중심의 작은 사각형 (가시)
        center_rect_visible = transformer.is_world_rect_visible(
            Vector2.zero(), Vector2(100, 100)
        )
        assert center_rect_visible, '화면 중심의 사각형은 가시 영역이어야 함'

        # When & Then - 화면 밖의 사각형 (비가시)
        far_rect_visible = transformer.is_world_rect_visible(
            Vector2(1000, 1000), Vector2(50, 50)
        )
        assert not far_rect_visible, '화면 밖 사각형은 비가시 영역이어야 함'

        # When & Then - 화면을 완전히 덮는 큰 사각형 (가시)
        large_rect_visible = transformer.is_world_rect_visible(
            Vector2.zero(), Vector2(2000, 2000)
        )
        assert large_rect_visible, '화면을 덮는 큰 사각형은 가시 영역이어야 함'

    def test_가시_월드_영역_경계_계산_정확성_검증_성공_시나리오(self) -> None:
        """9. 가시 월드 영역 경계 계산 정확성 검증 (성공 시나리오)

        목적: get_visible_world_bounds 메서드의 가시 영역 경계 계산 정확성 검증
        테스트할 범위: get_visible_world_bounds 메서드
        커버하는 함수 및 데이터: 현재 카메라 설정에서 보이는 월드 영역 계산
        기대되는 안정성: 정확한 가시 영역 경계를 통한 컬링 최적화 지원
        """
        # Given - 변환기 설정 (카메라 중심, 줌 2배)
        transformer = CameraBasedTransformer(
            Vector2(800, 600), Vector2(100, 100), 2.0
        )

        # When - 가시 월드 영역 경계 계산
        top_left, bottom_right = transformer.get_visible_world_bounds()

        # Then - 경계 계산 정확성 검증
        # 줌 2배이므로 실제 보이는 월드 영역은 화면 크기의 절반
        expected_width = 800 / 2.0  # 400
        expected_height = 600 / 2.0  # 300

        actual_width = bottom_right.x - top_left.x
        actual_height = bottom_right.y - top_left.y

        assert abs(actual_width - expected_width) < 0.001, (
            '가시 영역 너비가 정확해야 함'
        )
        assert abs(actual_height - expected_height) < 0.001, (
            '가시 영역 높이가 정확해야 함'
        )

        # 카메라 오프셋 중심으로 영역이 계산되어야 함
        center_x = (top_left.x + bottom_right.x) / 2
        center_y = (top_left.y + bottom_right.y) / 2
        expected_center = Vector2(100, 100)  # 카메라 오프셋

        assert abs(center_x - expected_center.x) < 0.001, (
            '가시 영역 중심 X가 카메라 오프셋과 일치해야 함'
        )
        assert abs(center_y - expected_center.y) < 0.001, (
            '가시 영역 중심 Y가 카메라 오프셋과 일치해야 함'
        )

    def test_줌_레벨_범위_제한_검증_성공_시나리오(self) -> None:
        """10. 줌 레벨 범위 제한 검증 (성공 시나리오)

        목적: 줌 레벨의 최소/최대값 제한이 올바르게 동작하는지 검증
        테스트할 범위: zoom_level 세터의 범위 제한
        커버하는 함수 및 데이터: 줌 레벨 경계값 처리
        기대되는 안정성: 안전한 줌 레벨 범위 내에서만 동작 보장
        """
        # Given - 변환기 설정
        transformer = CameraBasedTransformer(Vector2(800, 600))

        # When & Then - 최소값 제한 테스트
        transformer.zoom_level = 0.05  # 0.1 미만
        assert transformer.zoom_level == 0.1, (
            '줌 레벨 최소값이 0.1로 제한되어야 함'
        )

        # When & Then - 최대값 제한 테스트
        transformer.zoom_level = 15.0  # 10.0 초과
        assert transformer.zoom_level == 10.0, (
            '줌 레벨 최대값이 10.0으로 제한되어야 함'
        )

        # When & Then - 정상 범위 테스트
        transformer.zoom_level = 2.5
        assert transformer.zoom_level == 2.5, (
            '정상 범위의 줌 레벨은 그대로 설정되어야 함'
        )
