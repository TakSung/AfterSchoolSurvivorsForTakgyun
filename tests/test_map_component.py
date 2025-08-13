"""
Unit tests for MapComponent.

This module tests the MapComponent functionality including tile calculations,
boundary checking, and visual properties management.
"""


from src.components.map_component import MapComponent


class TestMapComponent:
    """Unit tests for MapComponent."""

    def test_맵_컴포넌트_기본_초기화_검증_성공_시나리오(self) -> None:
        """1. 맵 컴포넌트 기본 초기화 검증 (성공 시나리오)

        목적: MapComponent의 기본값들이 올바르게 초기화되는지 검증
        테스트할 범위: 기본값 설정, 타입 확인
        커버하는 함수 및 데이터: __init__, 기본 필드값들
        기대되는 안정성: 일관된 기본값으로 초기화
        """
        # Given & When - 기본 초기화
        map_comp = MapComponent()

        # Then - 기본값 확인 (객체의 설정 변수 사용)
        assert map_comp.tile_size == 64, f"기본 타일 크기는 {map_comp.tile_size}이어야 함"
        assert map_comp.world_width == 2000.0, "기본 월드 너비는 2000.0이어야 함"
        assert map_comp.world_height == 2000.0, "기본 월드 높이는 2000.0이어야 함"
        assert map_comp.light_tile_color == (240, 240, 240), "기본 밝은 타일 색상 확인"
        assert map_comp.dark_tile_color == (220, 220, 220), "기본 어두운 타일 색상 확인"
        assert map_comp.grid_color == (0, 0, 0), "기본 격자 색상 확인"
        assert map_comp.enable_infinite_scroll is True, "무한 스크롤 기본값은 True"
        assert map_comp.tile_pattern_size == 4, "기본 타일 패턴 크기는 4"

    def test_맵_컴포넌트_커스텀_초기화_검증_성공_시나리오(self) -> None:
        """2. 맵 컴포넌트 커스텀 초기화 검증 (성공 시나리오)

        목적: MapComponent의 커스텀 값들이 올바르게 설정되는지 검증
        테스트할 범위: 커스텀 초기화, 값 설정
        커버하는 함수 및 데이터: __init__ with custom values
        기대되는 안정성: 커스텀 값들의 정확한 설정
        """
        # Given & When - 커스텀 초기화 (새로운 필드명 사용)
        map_comp = MapComponent(
            tile_size=32,
            world_width=1024.0,
            world_height=768.0,
            light_tile_color=(200, 200, 200),
            dark_tile_color=(100, 100, 100),
            grid_color=(50, 50, 50),
            enable_infinite_scroll=False,
            tile_pattern_size=8
        )

        # Then - 커스텀 값 확인
        assert map_comp.tile_size == 32, "커스텀 타일 크기 확인"
        assert map_comp.world_width == 1024.0, "커스텀 월드 너비 확인"
        assert map_comp.world_height == 768.0, "커스텀 월드 높이 확인"
        assert map_comp.light_tile_color == (200, 200, 200), "커스텀 밝은 타일 색상 확인"
        assert map_comp.dark_tile_color == (100, 100, 100), "커스텀 어두운 타일 색상 확인"
        assert map_comp.grid_color == (50, 50, 50), "커스텀 격자 색상 확인"
        assert map_comp.enable_infinite_scroll is False, "무한 스크롤 비활성화 확인"
        assert map_comp.tile_pattern_size == 8, "커스텀 타일 패턴 크기 확인"

    def test_타일_위치_계산_기능_검증_성공_시나리오(self) -> None:
        """3. 타일 위치 계산 기능 검증 (성공 시나리오)

        목적: 월드 좌표를 타일 좌표로 변환하는 기능이 정확한지 검증
        테스트할 범위: get_tile_at_position, 좌표 변환 로직
        커버하는 함수 및 데이터: get_tile_at_position 메서드
        기대되는 안정성: 정확한 타일 좌표 계산
        """
        # Given - 기본 맵 컴포넌트 (객체의 tile_size 사용)
        map_comp = MapComponent()
        tile_size = map_comp.tile_size  # 객체 설정 변수 사용

        # When & Then - 다양한 월드 좌표에 대한 타일 좌표 계산
        assert map_comp.get_tile_at_position(0.0, 0.0) == (0, 0)
        assert map_comp.get_tile_at_position(tile_size/2, tile_size/2) == (0, 0)
        assert map_comp.get_tile_at_position(tile_size, tile_size) == (1, 1)
        assert map_comp.get_tile_at_position(tile_size*2, tile_size) == (2, 1)
        assert map_comp.get_tile_at_position(-tile_size/2, -tile_size/2) == (-1, -1)
        assert map_comp.get_tile_at_position(-tile_size, -tile_size) == (-1, -1)

    def test_타일_월드_위치_계산_기능_검증_성공_시나리오(self) -> None:
        """4. 타일 월드 위치 계산 기능 검증 (성공 시나리오)

        목적: 타일 좌표를 월드 좌표로 변환하는 기능이 정확한지 검증
        테스트할 범위: get_tile_world_position, 역변환 로직
        커버하는 함수 및 데이터: get_tile_world_position 메서드
        기대되는 안정성: 정확한 월드 좌표 계산
        """
        # Given - 기본 맵 컴포넌트 (객체의 tile_size 사용)
        map_comp = MapComponent()
        tile_size = map_comp.tile_size  # 객체 설정 변수 사용

        # When & Then - 다양한 타일 좌표에 대한 월드 위치 계산
        assert map_comp.get_tile_world_position(0, 0) == (0.0, 0.0)
        assert map_comp.get_tile_world_position(1, 1) == (float(tile_size), float(tile_size))
        assert map_comp.get_tile_world_position(2, 3) == (float(tile_size*2), float(tile_size*3))
        assert map_comp.get_tile_world_position(-1, -1) == (float(-tile_size), float(-tile_size))
        assert map_comp.get_tile_world_position(-2, -3) == (float(-tile_size*2), float(-tile_size*3))

    def test_가시_타일_범위_계산_기능_검증_성공_시나리오(self) -> None:
        """5. 가시 타일 범위 계산 기능 검증 (성공 시나리오)

        목적: 화면에 보이는 타일 범위를 정확하게 계산하는지 검증
        테스트할 범위: get_visible_tile_range, 뷰포트 컬링
        커버하는 함수 및 데이터: get_visible_tile_range 메서드
        기대되는 안정성: 정확한 가시 타일 범위 계산
        """
        # Given - 기본 맵 컴포넌트 (객체의 tile_size 사용)
        map_comp = MapComponent()
        tile_size = map_comp.tile_size  # 객체 설정 변수 사용
        screen_width = 800
        screen_height = 600

        # When - 카메라 오프셋 (0, 0)에서의 가시 타일 범위
        camera_offset = (0.0, 0.0)
        (min_tile, max_tile) = map_comp.get_visible_tile_range(
            camera_offset, screen_width, screen_height
        )

        # Then - 타일 범위 확인 (여유분 1타일 포함, 객체 설정 변수 기준)
        min_tile_x, min_tile_y = min_tile
        max_tile_x, max_tile_y = max_tile

        expected_max_x = int(screen_width // tile_size) + 1
        expected_max_y = int(screen_height // tile_size) + 1

        assert min_tile_x == -1, "최소 X 타일은 -1이어야 함"
        assert min_tile_y == -1, "최소 Y 타일은 -1이어야 함"
        assert max_tile_x == expected_max_x, f"최대 X 타일은 {expected_max_x}이어야 함 ({screen_width}/{tile_size} + 1)"
        assert max_tile_y == expected_max_y, f"최대 Y 타일은 {expected_max_y}이어야 함 ({screen_height}/{tile_size} + 1)"

    def test_가시_타일_범위_카메라_오프셋_적용_검증_성공_시나리오(self) -> None:
        """6. 가시 타일 범위 카메라 오프셋 적용 검증 (성공 시나리오)

        목적: 카메라 오프셋이 가시 타일 범위 계산에 정확히 반영되는지 검증
        테스트할 범위: get_visible_tile_range with offset, 오프셋 계산
        커버하는 함수 및 데이터: 카메라 오프셋이 적용된 타일 범위 계산
        기대되는 안정성: 오프셋에 따른 정확한 타일 범위 변화
        """
        # Given - 기본 맵 컴포넌트 (객체의 tile_size 사용)
        map_comp = MapComponent()
        tile_size = map_comp.tile_size  # 객체 설정 변수 사용
        screen_width = 800
        screen_height = 600

        # When - 카메라 오프셋 (-100, -100)에서의 가시 타일 범위
        camera_offset = (-100.0, -100.0)
        (min_tile, max_tile) = map_comp.get_visible_tile_range(
            camera_offset, screen_width, screen_height
        )

        # Then - 오프셋이 반영된 타일 범위 확인 (객체 설정 변수 기준)
        min_tile_x, min_tile_y = min_tile
        max_tile_x, max_tile_y = max_tile

        # 실제 계산 방식에 맞춘 기댓값 계산
        # camera_offset = (-100, -100)이므로
        # top_left_world = (100, 100), bottom_right_world = (900, 700)
        top_left_world_x = -camera_offset[0]  # 100
        top_left_world_y = -camera_offset[1]  # 100
        bottom_right_world_x = top_left_world_x + screen_width  # 900
        bottom_right_world_y = top_left_world_y + screen_height  # 700

        expected_min_x = int(top_left_world_x // tile_size) - 1
        expected_min_y = int(top_left_world_y // tile_size) - 1
        expected_max_x = int(bottom_right_world_x // tile_size) + 1
        expected_max_y = int(bottom_right_world_y // tile_size) + 1

        assert min_tile_x == expected_min_x, f"오프셋 적용된 최소 X 타일은 {expected_min_x}이어야 함"
        assert min_tile_y == expected_min_y, f"오프셋 적용된 최소 Y 타일은 {expected_min_y}이어야 함"
        assert max_tile_x == expected_max_x, f"오프셋 적용된 최대 X 타일은 {expected_max_x}이어야 함"
        assert max_tile_y == expected_max_y, f"오프셋 적용된 최대 Y 타일은 {expected_max_y}이어야 함"

    def test_타일_패턴_타입_계산_기능_검증_성공_시나리오(self) -> None:
        """7. 타일 패턴 타입 계산 기능 검증 (성공 시나리오)

        목적: 체스보드 패턴을 위한 타일 패턴 타입 계산이 정확한지 검증
        테스트할 범위: get_tile_pattern_type, 패턴 계산 로직
        커버하는 함수 및 데이터: get_tile_pattern_type 메서드
        기대되는 안정성: 일관된 체스보드 패턴 생성
        """
        # Given - 무한 스크롤 활성화된 맵 컴포넌트
        map_comp = MapComponent(enable_infinite_scroll=True, tile_pattern_size=4)

        # When & Then - 체스보드 패턴 확인
        assert map_comp.get_tile_pattern_type(0, 0) == 0  # (0+0) % 2 = 0
        assert map_comp.get_tile_pattern_type(0, 1) == 1  # (0+1) % 2 = 1
        assert map_comp.get_tile_pattern_type(1, 0) == 1  # (1+0) % 2 = 1
        assert map_comp.get_tile_pattern_type(1, 1) == 0  # (1+1) % 2 = 0
        assert map_comp.get_tile_pattern_type(2, 2) == 0  # (2+2) % 2 = 0
        assert map_comp.get_tile_pattern_type(3, 1) == 0  # (3+1) % 2 = 0

    def test_타일_패턴_타입_음수_좌표_처리_검증_성공_시나리오(self) -> None:
        """8. 타일 패턴 타입 음수 좌표 처리 검증 (성공 시나리오)

        목적: 음수 타일 좌표에서도 패턴이 올바르게 계산되는지 검증
        테스트할 범위: get_tile_pattern_type with negative coordinates
        커버하는 함수 및 데이터: 음수 처리 로직, abs() 함수 활용
        기대되는 안정성: 음수 좌표에서도 일관된 패턴 유지
        """
        # Given - 패턴 크기 4인 맵 컴포넌트
        map_comp = MapComponent(tile_pattern_size=4)

        # When & Then - 음수 좌표에서의 패턴 확인
        assert map_comp.get_tile_pattern_type(-1, -1) == 0  # abs(-1)+abs(-1)=2, 2%2=0
        assert map_comp.get_tile_pattern_type(-1, 0) == 1   # abs(-1)+abs(0)=1, 1%2=1
        assert map_comp.get_tile_pattern_type(0, -1) == 1   # abs(0)+abs(-1)=1, 1%2=1
        assert map_comp.get_tile_pattern_type(-2, -3) == 1  # abs(-2)+abs(-3)=5, 5%2=1

    def test_월드_경계_내부_확인_기능_검증_성공_시나리오(self) -> None:
        """9. 월드 경계 내부 확인 기능 검증 (성공 시나리오)

        목적: 주어진 좌표가 월드 경계 내부에 있는지 정확하게 판단하는지 검증
        테스트할 범위: is_within_world_bounds, 경계 검사 로직
        커버하는 함수 및 데이터: is_within_world_bounds 메서드
        기대되는 안정성: 정확한 경계 내부/외부 판단
        """
        # Given - 2000x2000 크기의 맵 컴포넌트
        map_comp = MapComponent(world_width=2000.0, world_height=2000.0)

        # When & Then - 경계 내부 좌표 확인
        assert map_comp.is_within_world_bounds(0.0, 0.0) is True
        assert map_comp.is_within_world_bounds(1000.0, 1000.0) is True
        assert map_comp.is_within_world_bounds(2000.0, 2000.0) is True

        # 경계 외부 좌표 확인
        assert map_comp.is_within_world_bounds(-1.0, 0.0) is False
        assert map_comp.is_within_world_bounds(0.0, -1.0) is False
        assert map_comp.is_within_world_bounds(2001.0, 1000.0) is False
        assert map_comp.is_within_world_bounds(1000.0, 2001.0) is False

    def test_월드_경계_클램핑_기능_검증_성공_시나리오(self) -> None:
        """10. 월드 경계 클램핑 기능 검증 (성공 시나리오)

        목적: 좌표를 월드 경계 내로 제한하는 기능이 정확한지 검증
        테스트할 범위: clamp_to_world_bounds, 클램핑 로직
        커버하는 함수 및 데이터: clamp_to_world_bounds 메서드
        기대되는 안정성: 경계 밖 좌표의 정확한 클램핑
        """
        # Given - 1000x800 크기의 맵 컴포넌트
        map_comp = MapComponent(world_width=1000.0, world_height=800.0)

        # When & Then - 경계 내부 좌표는 그대로
        assert map_comp.clamp_to_world_bounds(500.0, 400.0) == (500.0, 400.0)

        # 경계 외부 좌표는 클램핑
        assert map_comp.clamp_to_world_bounds(-100.0, 400.0) == (0.0, 400.0)
        assert map_comp.clamp_to_world_bounds(500.0, -50.0) == (500.0, 0.0)
        assert map_comp.clamp_to_world_bounds(1200.0, 400.0) == (1000.0, 400.0)
        assert map_comp.clamp_to_world_bounds(500.0, 900.0) == (500.0, 800.0)

        # 양쪽 모두 클램핑
        assert map_comp.clamp_to_world_bounds(-50.0, 1000.0) == (0.0, 800.0)
        assert map_comp.clamp_to_world_bounds(1500.0, -100.0) == (1000.0, 0.0)

    def test_맵_컴포넌트_유효성_검사_성공_시나리오(self) -> None:
        """11. 맵 컴포넌트 유효성 검사 성공 시나리오

        목적: 올바른 데이터를 가진 맵 컴포넌트가 유효성 검사를 통과하는지 검증
        테스트할 범위: validate 메서드, 전체 데이터 검증
        커버하는 함수 및 데이터: validate 메서드의 모든 검증 로직
        기대되는 안정성: 유효한 데이터에 대한 정확한 검증
        """
        # Given - 올바른 데이터를 가진 맵 컴포넌트 (새로운 필드명 사용)
        map_comp = MapComponent(
            tile_size=32,
            world_width=1024.0,
            world_height=768.0,
            light_tile_color=(255, 255, 255),
            dark_tile_color=(200, 200, 200),
            grid_color=(0, 0, 0),
            enable_infinite_scroll=True,
            tile_pattern_size=2
        )

        # When - 유효성 검사
        result = map_comp.validate()

        # Then - 유효성 검사 통과
        assert result is True, "유효한 맵 컴포넌트는 검증을 통과해야 함"

    def test_맵_컴포넌트_유효성_검사_실패_시나리오들(self) -> None:
        """12. 맵 컴포넌트 유효성 검사 실패 시나리오들

        목적: 잘못된 데이터를 가진 맵 컴포넌트가 유효성 검사에서 실패하는지 검증
        테스트할 범위: validate 메서드, 에러 케이스들
        커버하는 함수 및 데이터: 각종 유효하지 않은 데이터 패턴
        기대되는 안정성: 잘못된 데이터에 대한 정확한 검증 실패
        """
        # Given & When & Then - 잘못된 타일 크기
        invalid_comp = MapComponent(tile_size=0)
        assert invalid_comp.validate() is False

        # 잘못된 월드 크기
        invalid_comp = MapComponent(world_width=-100.0)
        assert invalid_comp.validate() is False

        invalid_comp = MapComponent(world_height=0.0)
        assert invalid_comp.validate() is False

        # 잘못된 색상 (새로운 필드명 사용)
        invalid_comp = MapComponent(light_tile_color=(256, 100, 100))  # 256 > 255
        assert invalid_comp.validate() is False

        invalid_comp = MapComponent(dark_tile_color=(-1, 50, 50))  # -1 < 0
        assert invalid_comp.validate() is False

        invalid_comp = MapComponent(grid_color=(256, 100, 100))  # 256 > 255
        assert invalid_comp.validate() is False

        # 잘못된 패턴 크기
        invalid_comp = MapComponent(tile_pattern_size=0)
        assert invalid_comp.validate() is False

    def test_타일_색상_반환_기능_검증_성공_시나리오(self) -> None:
        """13. 타일 색상 반환 기능 검증 (성공 시나리오).

        목적: 체스판 패턴에 따른 타일 색상이 정확하게 반환되는지 검증
        테스트할 범위: get_tile_color, 패턴 기반 색상 선택
        커버하는 함수 및 데이터: get_tile_color 메서드
        기대되는 안정성: 패턴에 따른 일관된 색상 반환
        """
        # Given - 기본 맵 컴포넌트
        map_comp = MapComponent()

        # When & Then - 체스판 패턴에 따른 색상 확인
        # 패턴 0 (밝은 색상): (x+y) % 2 == 0
        assert map_comp.get_tile_color(0, 0) == map_comp.light_tile_color
        assert map_comp.get_tile_color(1, 1) == map_comp.light_tile_color
        assert map_comp.get_tile_color(2, 2) == map_comp.light_tile_color

        # 패턴 1 (어두운 색상): (x+y) % 2 == 1
        assert map_comp.get_tile_color(0, 1) == map_comp.dark_tile_color
        assert map_comp.get_tile_color(1, 0) == map_comp.dark_tile_color
        assert map_comp.get_tile_color(1, 2) == map_comp.dark_tile_color

        # 음수 좌표에서도 동일한 패턴 유지
        # (-2) + (-2) = -4, -4 % 2 = 0
        assert map_comp.get_tile_color(-2, -2) == map_comp.light_tile_color
        # (-1) + (-2) = -3, -3 % 2 = 1
        assert map_comp.get_tile_color(-1, -2) == map_comp.dark_tile_color
