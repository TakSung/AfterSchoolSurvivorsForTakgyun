"""
Tests for CameraComponent class.

카메라 컴포넌트의 데이터 구조, 유효성 검사, 오프셋 업데이트 등
핵심 기능을 검증하는 테스트 모음입니다.
"""

from src.components.camera_component import CameraComponent
from src.core.entity import Entity


class TestCameraComponent:
    """CameraComponent에 대한 테스트 클래스"""

    def test_카메라_컴포넌트_기본_초기화_검증_성공_시나리오(self) -> None:
        """1. 카메라 컴포넌트 기본 값으로 초기화 검증 (성공 시나리오)

        목적: CameraComponent가 올바른 기본값으로 초기화되는지 검증
        테스트할 범위: 기본값 설정, 타입 검증
        커버하는 함수 및 데이터: __init__, world_offset, screen_center, world_bounds, follow_target, dead_zone_radius
        기대되는 안정성: 기본값으로 안정적인 초기화 보장
        """
        # Given & When - 기본값으로 카메라 컴포넌트 생성
        camera = CameraComponent()

        # Then - 기본값 확인
        assert camera.world_offset == (0.0, 0.0), (
            'world_offset 기본값이 (0.0, 0.0)이어야 함'
        )
        assert camera.screen_center == (400, 300), (
            'screen_center 기본값이 (400, 300)이어야 함'
        )
        assert camera.follow_target is None, (
            'follow_target 기본값이 None이어야 함'
        )
        assert camera.dead_zone_radius == 10.0, (
            'dead_zone_radius 기본값이 10.0이어야 함'
        )

        # 기본 월드 경계 확인
        expected_bounds = {
            'min_x': -1000.0,
            'max_x': 1000.0,
            'min_y': -1000.0,
            'max_y': 1000.0,
        }
        assert camera.world_bounds == expected_bounds, (
            'world_bounds 기본값이 올바르게 설정되어야 함'
        )

    def test_카메라_컴포넌트_커스텀_초기화_검증_성공_시나리오(self) -> None:
        """2. 카메라 컴포넌트 커스텀 값으로 초기화 검증 (성공 시나리오)

        목적: 커스텀 값으로 CameraComponent 초기화가 정상 작동하는지 검증
        테스트할 범위: 커스텀 값 설정, 타입 유지
        커버하는 함수 및 데이터: __init__ with parameters
        기대되는 안정성: 커스텀 값으로 정확한 초기화
        """
        # Given - 커스텀 값들 준비
        custom_offset = (50.0, -25.0)
        custom_center = (600, 450)
        custom_bounds = {
            'min_x': -500.0,
            'max_x': 500.0,
            'min_y': -300.0,
            'max_y': 300.0,
        }
        target_entity = Entity.create()
        custom_dead_zone = 15.0

        # When - 커스텀 값으로 카메라 컴포넌트 생성
        camera = CameraComponent(
            world_offset=custom_offset,
            screen_center=custom_center,
            world_bounds=custom_bounds,
            follow_target=target_entity,
            dead_zone_radius=custom_dead_zone,
        )

        # Then - 커스텀 값 확인
        assert camera.world_offset == custom_offset, (
            '커스텀 world_offset이 올바르게 설정되어야 함'
        )
        assert camera.screen_center == custom_center, (
            '커스텀 screen_center가 올바르게 설정되어야 함'
        )
        assert camera.world_bounds == custom_bounds, (
            '커스텀 world_bounds가 올바르게 설정되어야 함'
        )
        assert camera.follow_target == target_entity, (
            '커스텀 follow_target이 올바르게 설정되어야 함'
        )
        assert camera.dead_zone_radius == custom_dead_zone, (
            '커스텀 dead_zone_radius가 올바르게 설정되어야 함'
        )

    def test_월드_오프셋_업데이트_정상_동작_검증_성공_시나리오(self) -> None:
        """3. 월드 오프셋 업데이트 정상 동작 검증 (성공 시나리오)

        목적: update_world_offset 메서드의 정상 동작 검증
        테스트할 범위: 오프셋 업데이트, 경계 제한 없는 케이스
        커버하는 함수 및 데이터: update_world_offset
        기대되는 안정성: 경계 내 오프셋 업데이트 성공
        """
        # Given - 기본 카메라 컴포넌트 생성
        camera = CameraComponent()
        new_offset = (100.0, -50.0)

        # When - 오프셋 업데이트
        result = camera.update_world_offset(new_offset)

        # Then - 업데이트 결과 확인
        assert result is True, '경계 내 오프셋 업데이트는 True를 반환해야 함'
        assert camera.world_offset == new_offset, (
            'world_offset이 새로운 값으로 업데이트되어야 함'
        )

    def test_월드_오프셋_경계_제한_적용_검증_성공_시나리오(self) -> None:
        """4. 월드 오프셋 경계 제한 적용 검증 (성공 시나리오)

        목적: world_bounds를 넘는 오프셋이 올바르게 제한되는지 검증
        테스트할 범위: 경계 제한 로직, 제한된 값 반환
        커버하는 함수 및 데이터: update_world_offset with boundary constraints
        기대되는 안정성: 경계를 넘는 값이 안전하게 제한됨
        """
        # Given - 작은 경계를 가진 카메라 컴포넌트
        small_bounds = {
            'min_x': -50.0,
            'max_x': 50.0,
            'min_y': -30.0,
            'max_y': 30.0,
        }
        camera = CameraComponent(world_bounds=small_bounds)

        # When - 경계를 넘는 오프셋 업데이트 시도
        excessive_offset = (100.0, -100.0)  # 경계 넘는 값
        result = camera.update_world_offset(excessive_offset)

        # Then - 제한된 값으로 설정 확인
        assert result is True, '경계 제한이 적용되어도 업데이트는 성공해야 함'
        assert camera.world_offset == (50.0, -30.0), (
            '오프셋이 경계값으로 제한되어야 함'
        )

    def test_월드_오프셋_중복_업데이트_최적화_검증_성공_시나리오(self) -> None:
        """5. 월드 오프셋 중복 업데이트 최적화 검증 (성공 시나리오)

        목적: 동일한 오프셋으로 업데이트 시 최적화가 작동하는지 검증
        테스트할 범위: 중복 업데이트 감지, False 반환
        커버하는 함수 및 데이터: update_world_offset duplicate handling
        기대되는 안정성: 불필요한 업데이트 방지로 성능 최적화
        """
        # Given - 특정 오프셋을 가진 카메라 컴포넌트
        initial_offset = (25.0, -15.0)
        camera = CameraComponent(world_offset=initial_offset)

        # When - 동일한 오프셋으로 업데이트 시도
        result = camera.update_world_offset(initial_offset)

        # Then - 중복 업데이트 감지 확인
        assert result is False, '동일한 오프셋 업데이트는 False를 반환해야 함'
        assert camera.world_offset == initial_offset, (
            '오프셋은 변경되지 않아야 함'
        )

    def test_월드_경계_설정_기능_검증_성공_시나리오(self) -> None:
        """6. 월드 경계 설정 기능 검증 (성공 시나리오)

        목적: set_world_bounds 메서드의 정상 동작 검증
        테스트할 범위: 경계값 설정, 딕셔너리 업데이트
        커버하는 함수 및 데이터: set_world_bounds
        기대되는 안정성: 경계값이 올바르게 설정됨
        """
        # Given - 기본 카메라 컴포넌트
        camera = CameraComponent()

        # When - 새로운 경계값 설정
        camera.set_world_bounds(-200.0, 300.0, -150.0, 250.0)

        # Then - 경계값 설정 확인
        expected_bounds = {
            'min_x': -200.0,
            'max_x': 300.0,
            'min_y': -150.0,
            'max_y': 250.0,
        }
        assert camera.world_bounds == expected_bounds, (
            '새로운 경계값이 올바르게 설정되어야 함'
        )

    def test_카메라_컴포넌트_유효성_검사_성공_시나리오(self) -> None:
        """7. 카메라 컴포넌트 유효성 검사 성공 (성공 시나리오)

        목적: validate 메서드가 올바른 데이터에 대해 True를 반환하는지 검증
        테스트할 범위: 모든 필드의 유효성 검증
        커버하는 함수 및 데이터: validate
        기대되는 안정성: 유효한 데이터에 대한 정확한 검증
        """
        # Given - 유효한 데이터를 가진 카메라 컴포넌트
        camera = CameraComponent(
            world_offset=(10.0, -5.0),
            screen_center=(400, 300),
            world_bounds={
                'min_x': -100.0,
                'max_x': 100.0,
                'min_y': -80.0,
                'max_y': 80.0,
            },
            dead_zone_radius=5.0,
        )

        # When - 유효성 검사 실행
        result = camera.validate()

        # Then - 유효성 검사 통과 확인
        assert result is True, (
            '유효한 데이터에 대해 validate()는 True를 반환해야 함'
        )

    def test_카메라_컴포넌트_유효성_검사_실패_시나리오들(self) -> None:
        """8. 카메라 컴포넌트 유효성 검사 실패 시나리오들 (실패 시나리오)

        목적: validate 메서드가 잘못된 데이터에 대해 False를 반환하는지 검증
        테스트할 범위: 다양한 무효 데이터 케이스
        커버하는 함수 및 데이터: validate with invalid data
        기대되는 안정성: 무효한 데이터 감지 및 거부
        """
        # 잘못된 world_offset 타입
        camera_invalid_offset = CameraComponent()
        camera_invalid_offset.world_offset = 'invalid'
        assert not camera_invalid_offset.validate(), (
            '잘못된 world_offset 타입에 대해 False를 반환해야 함'
        )

        # 잘못된 screen_center 타입
        camera_invalid_center = CameraComponent()
        camera_invalid_center.screen_center = (1.5, 2.5)
        assert not camera_invalid_center.validate(), (
            '잘못된 screen_center 타입에 대해 False를 반환해야 함'
        )

        # 불완전한 world_bounds
        camera_incomplete_bounds = CameraComponent()
        camera_incomplete_bounds.world_bounds = {
            'min_x': -10.0
        }  # 불완전한 딕셔너리
        assert not camera_incomplete_bounds.validate(), (
            '불완전한 world_bounds에 대해 False를 반환해야 함'
        )

        # 논리적으로 잘못된 world_bounds (min > max)
        camera_invalid_bounds_logic = CameraComponent()
        camera_invalid_bounds_logic.world_bounds = {
            'min_x': 100.0,
            'max_x': 50.0,  # min_x > max_x
            'min_y': -10.0,
            'max_y': 10.0,
        }
        assert not camera_invalid_bounds_logic.validate(), (
            '잘못된 경계 논리에 대해 False를 반환해야 함'
        )

        # 음수 dead_zone_radius
        camera_negative_dead_zone = CameraComponent()
        camera_negative_dead_zone.dead_zone_radius = -5.0
        assert not camera_negative_dead_zone.validate(), (
            '음수 dead_zone_radius에 대해 False를 반환해야 함'
        )

    def test_카메라_컴포넌트_상속_및_인터페이스_검증_성공_시나리오(
        self,
    ) -> None:
        """9. 카메라 컴포넌트 상속 및 인터페이스 검증 (성공 시나리오)

        목적: CameraComponent가 Component를 올바르게 상속하는지 검증
        테스트할 범위: 상속 관계, 기본 메서드 구현
        커버하는 함수 및 데이터: Component interface methods
        기대되는 안정성: 기본 컴포넌트 인터페이스 준수
        """
        # Given - 카메라 컴포넌트 생성
        camera = CameraComponent()

        # When & Then - 상속 관계 및 메서드 존재 확인
        from src.core.component import Component

        assert isinstance(camera, Component), (
            'CameraComponent는 Component를 상속해야 함'
        )

        # 기본 Component 메서드들이 사용 가능한지 확인
        assert hasattr(camera, 'copy'), 'copy 메서드가 존재해야 함'
        assert hasattr(camera, 'serialize'), 'serialize 메서드가 존재해야 함'
        assert hasattr(camera, 'deserialize'), (
            'deserialize 메서드가 존재해야 함'
        )
        assert hasattr(camera, 'validate'), 'validate 메서드가 존재해야 함'

        # copy 메서드 동작 확인
        camera_copy = camera.copy()
        assert camera_copy is not camera, (
            'copy()는 새로운 인스턴스를 반환해야 함'
        )
        assert camera_copy.world_offset == camera.world_offset, (
            '복사본의 데이터가 일치해야 함'
        )

    def test_카메라_컴포넌트_시리얼라이제이션_검증_성공_시나리오(self) -> None:
        """10. 카메라 컴포넌트 직렬화/역직렬화 검증 (성공 시나리오)

        목적: serialize/deserialize 메서드의 정상 동작 검증
        테스트할 범위: 데이터 직렬화, 역직렬화, 데이터 일관성
        커버하는 함수 및 데이터: serialize, deserialize
        기대되는 안정성: 데이터 손실 없는 직렬화/역직렬화
        """
        # Given - 커스텀 데이터를 가진 카메라 컴포넌트
        original_camera = CameraComponent(
            world_offset=(75.0, -25.0),
            screen_center=(640, 480),
            world_bounds={
                'min_x': -200.0,
                'max_x': 200.0,
                'min_y': -150.0,
                'max_y': 150.0,
            },
            dead_zone_radius=12.5,
        )

        # When - 직렬화 후 역직렬화
        serialized_data = original_camera.serialize()
        deserialized_camera = CameraComponent.deserialize(serialized_data)

        # Then - 데이터 일관성 확인
        assert (
            deserialized_camera.world_offset == original_camera.world_offset
        ), 'world_offset이 동일해야 함'
        assert (
            deserialized_camera.screen_center == original_camera.screen_center
        ), 'screen_center가 동일해야 함'
        assert (
            deserialized_camera.world_bounds == original_camera.world_bounds
        ), 'world_bounds가 동일해야 함'
        assert (
            deserialized_camera.dead_zone_radius
            == original_camera.dead_zone_radius
        ), 'dead_zone_radius가 동일해야 함'
        assert (
            deserialized_camera.follow_target == original_camera.follow_target
        ), 'follow_target이 동일해야 함'
