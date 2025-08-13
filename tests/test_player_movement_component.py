"""
Tests for PlayerMovementComponent class.

플레이어 이동 컴포넌트의 데이터 구조, 유효성 검사, 방향 계산,
위치 업데이트 등 핵심 기능을 검증하는 테스트 모음입니다.
"""

import math

from src.components.player_movement_component import PlayerMovementComponent


class TestPlayerMovementComponent:
    """PlayerMovementComponent에 대한 테스트 클래스"""

    def test_플레이어_이동_컴포넌트_기본_초기화_검증_성공_시나리오(
        self,
    ) -> None:
        """1. 플레이어 이동 컴포넌트 기본 값으로 초기화 검증 (성공 시나리오)

        목적: PlayerMovementComponent가 올바른 기본값으로 초기화되는지 검증
        테스트할 범위: 기본값 설정, 타입 검증, 데이터 일관성
        커버하는 함수 및 데이터: __init__, 모든 기본 필드값
        기대되는 안정성: 기본값으로 안정적인 초기화 보장
        """
        # Given & When - 기본값으로 플레이어 이동 컴포넌트 생성
        movement = PlayerMovementComponent()

        # Then - 기본값 확인
        assert movement.world_position == (0.0, 0.0), (
            'world_position 기본값이 (0.0, 0.0)이어야 함'
        )
        assert movement.direction == (1.0, 0.0), (
            'direction 기본값이 (1.0, 0.0)이어야 함'
        )
        assert movement.speed == 200.0, 'speed 기본값이 200.0이어야 함'
        assert movement.rotation_angle == 0.0, (
            'rotation_angle 기본값이 0.0이어야 함'
        )
        assert movement.angular_velocity_limit == math.pi * 2.0, (
            'angular_velocity_limit 기본값이 2π여야 함'
        )
        assert movement.previous_position == (0.0, 0.0), (
            'previous_position 기본값이 (0.0, 0.0)이어야 함'
        )
        assert movement.dead_zone_radius == 10.0, (
            'dead_zone_radius 기본값이 10.0이어야 함'
        )

    def test_플레이어_이동_컴포넌트_커스텀_초기화_검증_성공_시나리오(
        self,
    ) -> None:
        """2. 플레이어 이동 컴포넌트 커스텀 값으로 초기화 검증 (성공 시나리오)

        목적: 커스텀 값으로 PlayerMovementComponent 초기화가 정상 작동하는지 검증
        테스트할 범위: 커스텀 값 설정, 타입 유지, 데이터 보존
        커버하는 함수 및 데이터: __init__ with custom parameters
        기대되는 안정성: 커스텀 값으로 정확한 초기화
        """
        # Given - 커스텀 값들 준비
        custom_position = (100.0, -50.0)
        custom_direction = (0.707, 0.707)  # 45도 방향 (정규화됨)
        custom_speed = 150.0
        custom_rotation = math.pi / 4  # 45도
        custom_angular_limit = math.pi  # 180도/초
        custom_prev_position = (90.0, -45.0)
        custom_dead_zone = 15.0

        # When - 커스텀 값으로 컴포넌트 생성
        movement = PlayerMovementComponent(
            world_position=custom_position,
            direction=custom_direction,
            speed=custom_speed,
            rotation_angle=custom_rotation,
            angular_velocity_limit=custom_angular_limit,
            previous_position=custom_prev_position,
            dead_zone_radius=custom_dead_zone,
        )

        # Then - 커스텀 값 확인
        assert movement.world_position == custom_position, (
            '커스텀 world_position이 올바르게 설정되어야 함'
        )
        assert movement.direction == custom_direction, (
            '커스텀 direction이 올바르게 설정되어야 함'
        )
        assert movement.speed == custom_speed, (
            '커스텀 speed가 올바르게 설정되어야 함'
        )
        assert movement.rotation_angle == custom_rotation, (
            '커스텀 rotation_angle이 올바르게 설정되어야 함'
        )
        assert movement.angular_velocity_limit == custom_angular_limit, (
            '커스텀 angular_velocity_limit이 올바르게 설정되어야 함'
        )
        assert movement.previous_position == custom_prev_position, (
            '커스텀 previous_position이 올바르게 설정되어야 함'
        )
        assert movement.dead_zone_radius == custom_dead_zone, (
            '커스텀 dead_zone_radius가 올바르게 설정되어야 함'
        )

    def test_방향_벡터_정규화_기능_검증_성공_시나리오(self) -> None:
        """3. 방향 벡터 정규화 기능 검증 (성공 시나리오)

        목적: normalize_direction 메서드가 올바르게 방향 벡터를 정규화하는지 검증
        테스트할 범위: 벡터 정규화 연산, 단위 벡터 확인
        커버하는 함수 및 데이터: normalize_direction
        기대되는 안정성: 정확한 단위 벡터 생성
        """
        # Given - 정규화되지 않은 방향 벡터를 가진 컴포넌트
        movement = PlayerMovementComponent()
        movement.direction = (3.0, 4.0)  # 크기 5인 벡터

        # When - 방향 벡터 정규화
        movement.normalize_direction()

        # Then - 정규화 결과 확인
        dx, dy = movement.direction
        magnitude = math.sqrt(dx * dx + dy * dy)
        assert abs(magnitude - 1.0) < 0.0001, (
            '정규화된 벡터의 크기가 1이어야 함'
        )
        assert abs(dx - 0.6) < 0.0001, '정규화된 X 성분이 0.6이어야 함'
        assert abs(dy - 0.8) < 0.0001, '정규화된 Y 성분이 0.8이어야 함'

    def test_방향_벡터_정규화_영벡터_처리_검증_성공_시나리오(self) -> None:
        """4. 방향 벡터 정규화 시 영벡터 처리 검증 (성공 시나리오)

        목적: normalize_direction이 영벡터나 매우 작은 벡터를 안전하게 처리하는지 검증
        테스트할 범위: 예외 상황 처리, 기본값 설정
        커버하는 함수 및 데이터: normalize_direction with edge cases
        기대되는 안정성: 영벡터 상황에서도 안전한 동작
        """
        # Given - 영벡터를 가진 컴포넌트
        movement = PlayerMovementComponent()
        movement.direction = (0.0, 0.0)

        # When - 영벡터 정규화
        movement.normalize_direction()

        # Then - 기본 방향으로 설정 확인
        assert movement.direction == (1.0, 0.0), (
            '영벡터는 기본 방향 (1.0, 0.0)으로 설정되어야 함'
        )

    def test_각도를_통한_방향_설정_검증_성공_시나리오(self) -> None:
        """5. 각도를 통한 방향 설정 검증 (성공 시나리오)

        목적: set_direction_from_angle 메서드가 올바르게 각도에서 방향을 계산하는지 검증
        테스트할 범위: 각도-벡터 변환, 회전각 정규화
        커버하는 함수 및 데이터: set_direction_from_angle
        기대되는 안정성: 정확한 각도-벡터 변환
        """
        # Given - 기본 이동 컴포넌트
        movement = PlayerMovementComponent()

        # When - 90도 각도로 방향 설정
        movement.set_direction_from_angle(math.pi / 2)

        # Then - 방향과 회전각 확인
        assert abs(movement.direction[0] - 0.0) < 0.0001, (
            '90도일 때 X 성분이 0이어야 함'
        )
        assert abs(movement.direction[1] - 1.0) < 0.0001, (
            '90도일 때 Y 성분이 1이어야 함'
        )
        assert abs(movement.rotation_angle - math.pi / 2) < 0.0001, (
            '회전각이 π/2로 설정되어야 함'
        )

    def test_이동_벡터_계산_검증_성공_시나리오(self) -> None:
        """6. 이동 벡터 계산 검증 (성공 시나리오)

        목적: get_movement_vector 메서드가 올바른 이동 벡터를 계산하는지 검증
        테스트할 범위: 속도와 시간 기반 이동 거리 계산
        커버하는 함수 및 데이터: get_movement_vector
        기대되는 안정성: 정확한 물리 기반 이동 계산
        """
        # Given - 특정 방향과 속도를 가진 컴포넌트
        movement = PlayerMovementComponent()
        movement.direction = (1.0, 0.0)  # 우측 방향
        movement.speed = 100.0  # 100 픽셀/초

        # When - 0.5초 동안의 이동 벡터 계산
        delta_time = 0.5
        movement_vector = movement.get_movement_vector(delta_time)

        # Then - 이동 벡터 확인
        expected_distance = movement.speed * delta_time  # 50 픽셀
        assert movement_vector == (50.0, 0.0), (
            f'이동 벡터가 (50.0, 0.0)이어야 함, 실제: {movement_vector}'
        )

    def test_위치_업데이트_및_이전_위치_추적_검증_성공_시나리오(self) -> None:
        """7. 위치 업데이트 및 이전 위치 추적 검증 (성공 시나리오)

        목적: update_position 메서드가 위치를 업데이트하고 이전 위치를 추적하는지 검증
        테스트할 범위: 위치 업데이트, 이전 위치 저장
        커버하는 함수 및 데이터: update_position
        기대되는 안정성: 정확한 위치 이력 관리
        """
        # Given - 초기 위치를 가진 컴포넌트
        movement = PlayerMovementComponent()
        initial_position = (10.0, 20.0)
        movement.world_position = initial_position

        # When - 새로운 위치로 업데이트
        new_position = (30.0, 40.0)
        movement.update_position(new_position)

        # Then - 위치 업데이트와 이전 위치 추적 확인
        assert movement.world_position == new_position, (
            '새로운 위치로 업데이트되어야 함'
        )
        assert movement.previous_position == initial_position, (
            '이전 위치가 올바르게 저장되어야 함'
        )

    def test_속도_벡터_계산_검증_성공_시나리오(self) -> None:
        """8. 속도 벡터 계산 검증 (성공 시나리오)

        목적: get_velocity 메서드가 올바른 속도 벡터를 반환하는지 검증
        테스트할 범위: 방향과 속도 기반 속도 벡터 계산
        커버하는 함수 및 데이터: get_velocity
        기대되는 안정성: 정확한 속도 벡터 계산
        """
        # Given - 특정 방향과 속도를 가진 컴포넌트
        movement = PlayerMovementComponent()
        movement.direction = (0.6, 0.8)  # 정규화된 벡터
        movement.speed = 50.0

        # When - 속도 벡터 계산
        velocity = movement.get_velocity()

        # Then - 속도 벡터 확인
        expected_vx = 0.6 * 50.0  # 30.0
        expected_vy = 0.8 * 50.0  # 40.0
        assert abs(velocity[0] - expected_vx) < 0.0001, (
            f'X 속도가 {expected_vx}이어야 함'
        )
        assert abs(velocity[1] - expected_vy) < 0.0001, (
            f'Y 속도가 {expected_vy}이어야 함'
        )

    def test_각도_정규화_기능_검증_성공_시나리오(self) -> None:
        """9. 각도 정규화 기능 검증 (성공 시나리오)

        목적: _normalize_angle 메서드가 각도를 -π ~ π 범위로 정규화하는지 검증
        테스트할 범위: 각도 정규화 연산, 범위 제한
        커버하는 함수 및 데이터: _normalize_angle
        기대되는 안정성: 정확한 각도 범위 유지
        """
        # Given - 이동 컴포넌트
        movement = PlayerMovementComponent()

        # When & Then - 다양한 각도 정규화 테스트

        # 정상 범위 각도
        assert (
            abs(movement._normalize_angle(math.pi / 2) - math.pi / 2) < 0.0001
        ), 'π/2는 그대로 유지되어야 함'

        # 범위를 넘는 양수 각도
        large_angle = 3 * math.pi
        normalized = movement._normalize_angle(large_angle)
        assert abs(normalized - math.pi) < 0.0001, '3π는 π로 정규화되어야 함'

        # 범위를 넘는 음수 각도
        small_angle = -3 * math.pi
        normalized = movement._normalize_angle(small_angle)
        assert abs(normalized - (-math.pi)) < 0.0001, (
            '-3π는 -π로 정규화되어야 함'
        )

    def test_각도_차이_계산_검증_성공_시나리오(self) -> None:
        """10. 각도 차이 계산 검증 (성공 시나리오)

        목적: calculate_angular_difference가 최단 각도 차이를 올바르게 계산하는지 검증
        테스트할 범위: 각도 차이 계산, 최단 경로 선택
        커버하는 함수 및 데이터: calculate_angular_difference
        기대되는 안정성: 정확한 최단 회전 각도 계산
        """
        # Given - 특정 회전각을 가진 컴포넌트
        movement = PlayerMovementComponent()
        movement.rotation_angle = 0.0  # 0도

        # When & Then - 다양한 목표 각도에 대한 차이 계산

        # 단순한 양수 차이
        diff = movement.calculate_angular_difference(math.pi / 2)  # 90도
        assert abs(diff - math.pi / 2) < 0.0001, (
            '0도에서 90도로의 차이가 π/2여야 함'
        )

        # 경계를 넘는 경우 (최단 경로)
        movement.rotation_angle = math.pi * 0.9  # 162도
        target = -math.pi * 0.9  # -162도
        diff = movement.calculate_angular_difference(target)
        # -162도 - 162도 = -324도 = -1.8π, 정규화하면 0.2π (36도)
        expected = math.pi * 0.2  # 36도 (최단 경로는 시계방향으로 36도)
        assert abs(diff - expected) < 0.0001, (
            '162도에서 -162도로의 최단 차이가 36도여야 함'
        )

    def test_플레이어_이동_컴포넌트_유효성_검사_성공_시나리오(self) -> None:
        """11. 플레이어 이동 컴포넌트 유효성 검사 성공 (성공 시나리오)

        목적: validate 메서드가 올바른 데이터에 대해 True를 반환하는지 검증
        테스트할 범위: 모든 필드의 유효성 검증
        커버하는 함수 및 데이터: validate
        기대되는 안정성: 유효한 데이터에 대한 정확한 검증
        """
        # Given - 유효한 데이터를 가진 컴포넌트
        movement = PlayerMovementComponent(
            world_position=(100.0, -50.0),
            direction=(0.707, 0.707),  # 정규화된 벡터
            speed=150.0,
            rotation_angle=math.pi / 4,
            angular_velocity_limit=math.pi,
            previous_position=(90.0, -45.0),
            dead_zone_radius=15.0,
        )

        # When - 유효성 검사 실행
        result = movement.validate()

        # Then - 유효성 검사 통과 확인
        assert result is True, (
            '유효한 데이터에 대해 validate()는 True를 반환해야 함'
        )

    def test_플레이어_이동_컴포넌트_유효성_검사_실패_시나리오들(self) -> None:
        """12. 플레이어 이동 컴포넌트 유효성 검사 실패 시나리오들 (실패 시나리오)

        목적: validate 메서드가 잘못된 데이터에 대해 False를 반환하는지 검증
        테스트할 범위: 다양한 무효 데이터 케이스
        커버하는 함수 및 데이터: validate with invalid data
        기대되는 안정성: 무효한 데이터 감지 및 거부
        """
        # 잘못된 world_position 타입
        movement_invalid_position = PlayerMovementComponent()
        movement_invalid_position.world_position = 'invalid'
        assert not movement_invalid_position.validate(), (
            '잘못된 world_position 타입에 대해 False를 반환해야 함'
        )

        # 정규화되지 않은 direction
        movement_unnormalized = PlayerMovementComponent()
        movement_unnormalized.direction = (3.0, 4.0)  # 크기 5
        assert not movement_unnormalized.validate(), (
            '정규화되지 않은 direction에 대해 False를 반환해야 함'
        )

        # 음수 speed
        movement_negative_speed = PlayerMovementComponent()
        movement_negative_speed.speed = -10.0
        assert not movement_negative_speed.validate(), (
            '음수 speed에 대해 False를 반환해야 함'
        )

        # 범위를 벗어난 rotation_angle
        movement_invalid_angle = PlayerMovementComponent()
        movement_invalid_angle.rotation_angle = 4.0 * math.pi  # 범위 초과
        assert not movement_invalid_angle.validate(), (
            '범위를 벗어난 rotation_angle에 대해 False를 반환해야 함'
        )

        # 음수 또는 0인 angular_velocity_limit
        movement_invalid_angular_limit = PlayerMovementComponent()
        movement_invalid_angular_limit.angular_velocity_limit = 0.0
        assert not movement_invalid_angular_limit.validate(), (
            '0인 angular_velocity_limit에 대해 False를 반환해야 함'
        )
