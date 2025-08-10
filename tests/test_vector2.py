import math
import pytest

from src.utils.vector2 import Vector2


class TestVector2:
    def test_벡터_생성_및_기본_속성_확인_성공_시나리오(self) -> None:
        """1. Vector2 객체 생성 및 기본 속성 확인 (성공 시나리오)
        
        목적: Vector2 클래스의 생성자와 기본 속성 검증
        테스트할 범위: __init__, x, y 속성
        커버하는 함수 및 데이터: 기본 생성자, 매개변수 생성자
        기대되는 안정성: 정확한 좌표 값 저장 보장
        """
        # Given & When - 기본 생성자로 벡터 생성
        default_vector = Vector2()
        
        # Then - 기본값 확인
        assert default_vector.x == 0.0, "기본 x 좌표는 0.0이어야 함"
        assert default_vector.y == 0.0, "기본 y 좌표는 0.0이어야 함"
        
        # Given & When - 매개변수로 벡터 생성
        custom_vector = Vector2(3.5, -2.1)
        
        # Then - 설정된 값 확인
        assert custom_vector.x == 3.5, "x 좌표가 정확히 설정되어야 함"
        assert custom_vector.y == -2.1, "y 좌표가 정확히 설정되어야 함"

    def test_벡터_연산_정확성_검증_성공_시나리오(self) -> None:
        """2. 벡터 사칙연산 정확성 검증 (성공 시나리오)
        
        목적: Vector2의 덧셈, 뺄셈, 곱셈, 나눗셈 연산 검증
        테스트할 범위: __add__, __sub__, __mul__, __truediv__
        커버하는 함수 및 데이터: 벡터 간 연산, 스칼라 연산
        기대되는 안정성: 수학적으로 정확한 연산 결과 보장
        """
        # Given - 테스트용 벡터들 생성
        v1 = Vector2(4.0, 3.0)
        v2 = Vector2(2.0, 1.0)
        
        # When & Then - 벡터 덧셈 검증
        result_add = v1 + v2
        assert result_add.x == 6.0, "벡터 덧셈 x 좌표가 정확해야 함"
        assert result_add.y == 4.0, "벡터 덧셈 y 좌표가 정확해야 함"
        
        # When & Then - 벡터 뺄셈 검증
        result_sub = v1 - v2
        assert result_sub.x == 2.0, "벡터 뺄셈 x 좌표가 정확해야 함"
        assert result_sub.y == 2.0, "벡터 뺄셈 y 좌표가 정확해야 함"
        
        # When & Then - 스칼라 곱셈 검증
        result_mul = v1 * 2.5
        assert result_mul.x == 10.0, "스칼라 곱셈 x 좌표가 정확해야 함"
        assert result_mul.y == 7.5, "스칼라 곱셈 y 좌표가 정확해야 함"
        
        # When & Then - 스칼라 나눗셈 검증
        result_div = v1 / 2.0
        assert result_div.x == 2.0, "스칼라 나눗셈 x 좌표가 정확해야 함"
        assert result_div.y == 1.5, "스칼라 나눗셈 y 좌표가 정확해야 함"

    def test_벡터_크기_계산_정확성_검증_성공_시나리오(self) -> None:
        """3. 벡터 크기 계산 정확성 검증 (성공 시나리오)
        
        목적: magnitude, magnitude_squared 속성의 정확성 검증
        테스트할 범위: magnitude, magnitude_squared 프로퍼티
        커버하는 함수 및 데이터: 피타고라스 정리 기반 크기 계산
        기대되는 안정성: 수학적으로 정확한 벡터 크기 계산 보장
        """
        # Given - 3-4-5 직각삼각형 벡터 생성 (크기 5)
        vector = Vector2(3.0, 4.0)
        
        # When & Then - 벡터 크기 검증
        expected_magnitude = 5.0
        assert math.isclose(vector.magnitude, expected_magnitude), "벡터 크기가 정확해야 함"
        assert math.isclose(vector.magnitude_squared, 25.0), "벡터 크기 제곱이 정확해야 함"
        
        # Given - 영벡터 테스트
        zero_vector = Vector2.zero()
        
        # When & Then - 영벡터 크기 검증
        assert zero_vector.magnitude == 0.0, "영벡터의 크기는 0이어야 함"
        assert zero_vector.magnitude_squared == 0.0, "영벡터의 크기 제곱은 0이어야 함"

    def test_벡터_거리_계산_정확성_검증_성공_시나리오(self) -> None:
        """4. 벡터 간 거리 계산 정확성 검증 (성공 시나리오)
        
        목적: distance_to, distance_squared_to 메서드의 정확성 검증
        테스트할 범위: distance_to, distance_squared_to 메서드
        커버하는 함수 및 데이터: 두 점 간 거리 계산
        기대되는 안정성: 정확한 유클리드 거리 계산 보장
        """
        # Given - 두 점 생성 (거리 5인 점들)
        point1 = Vector2(0.0, 0.0)
        point2 = Vector2(3.0, 4.0)
        
        # When & Then - 거리 계산 검증
        distance = point1.distance_to(point2)
        distance_squared = point1.distance_squared_to(point2)
        
        assert math.isclose(distance, 5.0), "두 점 간 거리가 정확해야 함"
        assert math.isclose(distance_squared, 25.0), "두 점 간 거리 제곱이 정확해야 함"
        
        # Given - 동일한 점들
        same_point1 = Vector2(2.5, -1.5)
        same_point2 = Vector2(2.5, -1.5)
        
        # When & Then - 동일 점 거리 검증
        assert same_point1.distance_to(same_point2) == 0.0, "동일한 점들 간 거리는 0이어야 함"

    def test_벡터_정규화_정확성_검증_성공_시나리오(self) -> None:
        """5. 벡터 정규화 정확성 검증 (성공 시나리오)
        
        목적: normalize, normalized 메서드의 정확성 검증
        테스트할 범위: normalize, normalized 메서드
        커버하는 함수 및 데이터: 단위 벡터 변환
        기대되는 안정성: 크기 1인 벡터로 정확한 정규화 보장
        """
        # Given - 임의 크기 벡터 생성
        vector = Vector2(6.0, 8.0)
        
        # When - 정규화 수행
        normalized = vector.normalized()
        
        # Then - 정규화 결과 검증
        assert math.isclose(normalized.magnitude, 1.0), "정규화된 벡터의 크기는 1이어야 함"
        assert math.isclose(normalized.x, 0.6), "정규화된 x 좌표가 정확해야 함"
        assert math.isclose(normalized.y, 0.8), "정규화된 y 좌표가 정확해야 함"
        
        # Given - 영벡터 정규화 테스트
        zero_vector = Vector2.zero()
        
        # When & Then - 영벡터 정규화 검증
        normalized_zero = zero_vector.normalized()
        assert normalized_zero.x == 0.0, "영벡터 정규화 시 x는 0이어야 함"
        assert normalized_zero.y == 0.0, "영벡터 정규화 시 y는 0이어야 함"

    def test_벡터_내적_외적_계산_정확성_검증_성공_시나리오(self) -> None:
        """6. 벡터 내적, 외적 계산 정확성 검증 (성공 시나리오)
        
        목적: dot, cross 메서드의 정확성 검증
        테스트할 범위: dot, cross 메서드
        커버하는 함수 및 데이터: 벡터 내적, 외적 연산
        기대되는 안정성: 수학적으로 정확한 내적, 외적 계산 보장
        """
        # Given - 테스트용 벡터들 생성
        v1 = Vector2(2.0, 3.0)
        v2 = Vector2(4.0, -1.0)
        
        # When & Then - 내적 계산 검증
        dot_product = v1.dot(v2)
        expected_dot = 2.0 * 4.0 + 3.0 * (-1.0)  # 8 - 3 = 5
        assert math.isclose(dot_product, expected_dot), "내적 계산이 정확해야 함"
        
        # When & Then - 외적 계산 검증 (2D에서는 스칼라)
        cross_product = v1.cross(v2)
        expected_cross = 2.0 * (-1.0) - 3.0 * 4.0  # -2 - 12 = -14
        assert math.isclose(cross_product, expected_cross), "외적 계산이 정확해야 함"

    def test_벡터_클래스_메서드_정확성_검증_성공_시나리오(self) -> None:
        """7. Vector2 클래스 메서드 정확성 검증 (성공 시나리오)
        
        목적: 미리 정의된 벡터 상수와 생성 메서드 검증
        테스트할 범위: zero, one, up, down, left, right, from_angle 메서드
        커버하는 함수 및 데이터: 클래스 메서드로 생성되는 특수 벡터들
        기대되는 안정성: 일관된 방향 벡터 제공 보장
        """
        # When & Then - 상수 벡터들 검증
        assert Vector2.zero() == Vector2(0, 0), "영벡터가 정확해야 함"
        assert Vector2.one() == Vector2(1, 1), "단위벡터가 정확해야 함"
        assert Vector2.up() == Vector2(0, -1), "상향 벡터가 정확해야 함"
        assert Vector2.down() == Vector2(0, 1), "하향 벡터가 정확해야 함"
        assert Vector2.left() == Vector2(-1, 0), "좌향 벡터가 정확해야 함"
        assert Vector2.right() == Vector2(1, 0), "우향 벡터가 정확해야 함"
        
        # When & Then - 각도로부터 벡터 생성 검증
        angle_vector = Vector2.from_angle(math.pi / 2, 2.0)  # 90도, 크기 2
        assert math.isclose(angle_vector.x, 0.0, abs_tol=1e-10), "90도 벡터 x가 0이어야 함"
        assert math.isclose(angle_vector.y, 2.0), "90도 벡터 y가 2이어야 함"

    def test_영으로_나누기_예외_처리_실패_시나리오(self) -> None:
        """8. 영으로 나누기 예외 처리 검증 (실패 시나리오)
        
        목적: 0으로 나누기 시 적절한 예외 발생 검증
        테스트할 범위: __truediv__ 메서드
        커버하는 함수 및 데이터: 0으로 나누기 예외 상황
        기대되는 안정성: 수학적 오류에 대한 명확한 예외 처리
        """
        # Given - 임의 벡터 생성
        vector = Vector2(5.0, 3.0)
        
        # When & Then - 0으로 나누기 시 예외 발생 검증
        with pytest.raises(ValueError, match="Cannot divide vector by zero"):
            vector / 0