"""
Unit tests for collision system components.

Tests the collision detection algorithms and collision system functionality
including AABB collision detection, collision components, and system integration.
"""

import time

import pytest

from src.components.collision_component import (
    CollisionComponent,
)
from src.components.position_component import PositionComponent
from src.core.entity_manager import EntityManager
from src.systems.collision_system import (
    BruteForceCollisionDetector,
    CollisionSystem,
)


class TestBruteForceCollisionDetector:
    """Test cases for BruteForceCollisionDetector._check_aabb_collision method."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.detector = BruteForceCollisionDetector()

    # Success Scenarios - 충돌 케이스
    def test_완전히_겹치는_사각형_충돌_검증_성공_시나리오(self):
        """1.1. 완전히 겹치는 사각형 충돌 검증 (성공 시나리오)

        목적: 한 사각형이 다른 사각형에 완전히 포함될 때 충돌 감지
        테스트할 범위: AABB 기본 충돌 검사 로직
        커버하는 함수 및 데이터: _check_aabb_collision 메서드
        기대되는 안정성: 완전 포함 관계에서 True 반환 보장
        """
        # Given - 큰 사각형과 내부의 작은 사각형
        result = self.detector._check_aabb_collision(0, 0, 4, 4, 0, 0, 2, 2)

        # Then - 충돌로 판정
        assert result is True, '완전히 겹치는 사각형들은 충돌로 판정되어야 함'

    def test_부분적으로_겹치는_사각형_충돌_검증_성공_시나리오(self):
        """1.2. 부분적으로 겹치는 사각형 충돌 검증 (성공 시나리오)

        목적: 두 사각형이 부분적으로 겹칠 때 충돌 감지
        테스트할 범위: 부분 겹침 상황에서의 충돌 검사
        커버하는 함수 및 데이터: _check_aabb_collision의 겹침 계산
        기대되는 안정성: 부분 겹침에서 True 반환 보장
        """
        # Given - 부분적으로 겹치는 두 사각형
        result = self.detector._check_aabb_collision(0, 0, 4, 4, 1, 1, 4, 4)

        # Then - 충돌로 판정
        assert result is True, (
            '부분적으로 겹치는 사각형들은 충돌로 판정되어야 함'
        )

    def test_우측_모서리_접촉_충돌_검증_성공_시나리오(self):
        """1.3. 우측 모서리 접촉 충돌 검증 (성공 시나리오)

        목적: 사각형들이 우측 모서리에서 정확히 접촉할 때 충돌 감지
        테스트할 범위: 경계값에서의 충돌 판정 로직
        커버하는 함수 및 데이터: right1 == left2 조건 처리
        기대되는 안정성: 모서리 접촉에서 True 반환 보장
        """
        # Given - 우측 모서리가 접촉하는 두 사각형 (right1 == left2)
        result = self.detector._check_aabb_collision(0, 0, 2, 2, 2, 0, 2, 2)

        # Then - 충돌로 판정 (모서리 접촉도 충돌)
        assert result is True, (
            '모서리가 접촉하는 사각형들은 충돌로 판정되어야 함'
        )

    def test_하단_모서리_접촉_충돌_검증_성공_시나리오(self):
        """1.4. 하단 모서리 접촉 충돌 검증 (성공 시나리오)

        목적: 사각형들이 하단 모서리에서 정확히 접촉할 때 충돌 감지
        테스트할 범위: Y축 경계값에서의 충돌 판정
        커버하는 함수 및 데이터: bottom1 == top2 조건 처리
        기대되는 안정성: Y축 모서리 접촉에서 True 반환 보장
        """
        # Given - 하단 모서리가 접촉하는 두 사각형 (bottom1 == top2)
        result = self.detector._check_aabb_collision(0, 0, 2, 2, 0, 2, 2, 2)

        # Then - 충돌로 판정
        assert result is True, (
            'Y축 모서리가 접촉하는 사각형들은 충돌로 판정되어야 함'
        )

    def test_점과_사각형_내부_충돌_검증_성공_시나리오(self):
        """1.5. 점과 사각형 내부 충돌 검증 (성공 시나리오)

        목적: 크기가 0인 점이 사각형 내부에 위치할 때 충돌 감지
        테스트할 범위: 점 충돌 케이스 처리 (탄막 시나리오)
        커버하는 함수 및 데이터: width=0, height=0 케이스 처리
        기대되는 안정성: 점-사각형 내부 충돌에서 True 반환 보장
        """
        # Given - 점(크기 0)과 사각형
        result = self.detector._check_aabb_collision(0, 0, 0, 0, 0, 0, 4, 4)

        # Then - 충돌로 판정 (점이 사각형 내부)
        assert result is True, '사각형 내부의 점은 충돌로 판정되어야 함'

    def test_점과_점_동일_위치_충돌_검증_성공_시나리오(self):
        """1.6. 점과 점 동일 위치 충돌 검증 (성공 시나리오)

        목적: 두 점이 동일한 위치에 있을 때만 충돌 감지
        테스트할 범위: 점-점 충돌의 특수 케이스
        커버하는 함수 및 데이터: 모든 크기가 0인 케이스
        기대되는 안정성: 동일 위치 점들에서 True 반환 보장
        """
        # Given - 같은 위치의 두 점
        result = self.detector._check_aabb_collision(5, 5, 0, 0, 5, 5, 0, 0)

        # Then - 충돌로 판정 (동일 위치)
        assert result is True, '같은 위치의 두 점은 충돌로 판정되어야 함'

    def test_점과_사각형_모서리_충돌_검증_성공_시나리오(self):
        """1.7. 점과 사각형 모서리 충돌 검증 (성공 시나리오)

        목적: 점이 사각형의 모서리 위에 위치할 때 충돌 감지
        테스트할 범위: 점과 모서리의 경계 케이스
        커버하는 함수 및 데이터: 점이 경계선상에 위치하는 경우
        기대되는 안정성: 모서리 위 점에서 True 반환 보장
        """
        # Given - 사각형의 우측 모서리에 위치한 점
        result = self.detector._check_aabb_collision(2, 0, 0, 0, 0, 0, 4, 2)

        # Then - 충돌로 판정 (모서리 위 점)
        assert result is True, '사각형 모서리 위의 점은 충돌로 판정되어야 함'

    # Success Scenarios - 비충돌 케이스
    def test_완전히_분리된_사각형_비충돌_검증_성공_시나리오(self):
        """2.1. 완전히 분리된 사각형 비충돌 검증 (성공 시나리오)

        목적: 서로 떨어진 사각형들이 비충돌로 판정되는지 검증
        테스트할 범위: 기본적인 비충돌 케이스
        커버하는 함수 및 데이터: 분리된 사각형 처리
        기대되는 안정성: 분리된 사각형들에서 False 반환 보장
        """
        # Given - 완전히 분리된 두 사각형
        result = self.detector._check_aabb_collision(0, 0, 2, 2, 10, 10, 2, 2)

        # Then - 비충돌로 판정
        assert result is False, '분리된 사각형들은 비충돌로 판정되어야 함'

    def test_X축_분리_모서리_근접_비충돌_검증_성공_시나리오(self):
        """2.2. X축 분리 모서리 근접 비충돌 검증 (성공 시나리오)

        목적: X축에서 아주 작은 간격으로 분리된 사각형들의 비충돌 검증
        테스트할 범위: X축 경계값 근처에서의 비충돌 판정
        커버하는 함수 및 데이터: left2 > right1 조건
        기대되는 안정성: 미세한 간격에서도 False 반환 보장
        """
        # Given - X축에서 아주 작은 간격으로 분리된 사각형들
        result = self.detector._check_aabb_collision(0, 0, 2, 2, 2.1, 0, 2, 2)

        # Then - 비충돌로 판정
        assert result is False, (
            'X축에서 분리된 사각형들은 비충돌로 판정되어야 함'
        )

    def test_Y축_분리_모서리_근접_비충돌_검증_성공_시나리오(self):
        """2.3. Y축 분리 모서리 근접 비충돌 검증 (성공 시나리오)

        목적: Y축에서 아주 작은 간격으로 분리된 사각형들의 비충돌 검증
        테스트할 범위: Y축 경계값 근처에서의 비충돌 판정
        커버하는 함수 및 데이터: top2 > bottom1 조건
        기대되는 안정성: 미세한 Y축 간격에서도 False 반환 보장
        """
        # Given - Y축에서 아주 작은 간격으로 분리된 사각형들
        result = self.detector._check_aabb_collision(0, 0, 2, 2, 0, 2.1, 2, 2)

        # Then - 비충돌로 판정
        assert result is False, (
            'Y축에서 분리된 사각형들은 비충돌로 판정되어야 함'
        )

    def test_점과_사각형_외부_비충돌_검증_성공_시나리오(self):
        """2.4. 점과 사각형 외부 비충돌 검증 (성공 시나리오)

        목적: 점이 사각형 외부에 위치할 때 비충돌 검증
        테스트할 범위: 점-사각형 외부 케이스
        커버하는 함수 및 데이터: 점이 사각형 범위 밖에 있는 경우
        기대되는 안정성: 외부 점에서 False 반환 보장
        """
        # Given - 사각형 외부에 위치한 점
        result = self.detector._check_aabb_collision(0, 0, 0, 0, 5, 5, 2, 2)

        # Then - 비충돌로 판정
        assert result is False, '사각형 외부의 점은 비충돌로 판정되어야 함'

    def test_점과_점_다른_위치_비충돌_검증_성공_시나리오(self):
        """2.5. 점과 점 다른 위치 비충돌 검증 (성공 시나리오)

        목적: 서로 다른 위치의 두 점이 비충돌로 판정되는지 검증
        테스트할 범위: 점-점 비충돌 케이스
        커버하는 함수 및 데이터: 위치가 다른 점들
        기대되는 안정성: 다른 위치 점들에서 False 반환 보장
        """
        # Given - 서로 다른 위치의 두 점
        result = self.detector._check_aabb_collision(0, 0, 0, 0, 1, 1, 0, 0)

        # Then - 비충돌로 판정
        assert result is False, '다른 위치의 두 점은 비충돌로 판정되어야 함'

    # Enhanced Edge Case Scenarios
    def test_매우_큰_좌표값_충돌_검증_성공_시나리오(self):
        """3.1. 매우 큰 좌표값 충돌 검증 (성공 시나리오)

        목적: 매우 큰 좌표값에서도 정상적인 충돌 검사 수행
        테스트할 범위: 큰 숫자에서의 연산 정확성
        커버하는 함수 및 데이터: 대용량 좌표값 처리
        기대되는 안정성: 큰 좌표값에서도 정확한 결과 보장
        """
        # Given - 매우 큰 좌표값의 겹치는 사각형들
        result = self.detector._check_aabb_collision(
            1e6, 1e6, 10, 10, 1e6 + 5, 1e6 + 5, 10, 10
        )

        # Then - 정상적으로 충돌 감지
        assert result is True, '큰 좌표값에서도 충돌이 정확히 감지되어야 함'

    def test_매우_작은_크기_동일_위치_검증_성공_시나리오(self):
        """3.2. 매우 작은 크기 동일 위치 검증 (성공 시나리오)

        목적: 매우 작은 크기의 사각형들도 정확히 충돌 검사
        테스트할 범위: 부동소수점 정밀도 한계 근처
        커버하는 함수 및 데이터: 미세한 크기 처리
        기대되는 안정성: 작은 크기에서도 정확한 결과 보장
        """
        # Given - 매우 작은 크기의 같은 위치 사각형들
        result = self.detector._check_aabb_collision(
            0, 0, 1e-6, 1e-6, 0, 0, 1e-6, 1e-6
        )

        # Then - 정상적으로 충돌 감지
        assert result is True, (
            '매우 작은 크기의 사각형들도 충돌이 감지되어야 함'
        )

    def test_정확히_모서리_겹침_부동소수점_정밀도_검증_성공_시나리오(self):
        """3.3. 정확히 모서리 겹침 부동소수점 정밀도 검증 (성공 시나리오)

        목적: 부동소수점 정밀도에서 정확한 모서리 접촉 감지
        테스트할 범위: right1 == left2 정확한 경우
        커버하는 함수 및 데이터: 부동소수점 equality 처리
        기대되는 안정성: 정확한 접촉에서 True 반환 보장
        """
        # Given - 정확히 모서리가 접촉하는 사각형들
        result = self.detector._check_aabb_collision(0, 0, 2, 2, 2.0, 0, 2, 2)

        # Then - 충돌로 정확히 감지
        assert result is True, '정확한 모서리 접촉은 충돌로 감지되어야 함'

    def test_미세하게_모자라서_비충돌_검증_성공_시나리오(self):
        """3.4. 미세하게 모자라서 비충돌 검증 (성공 시나리오)

        목적: 매우 작은 간격으로도 정확한 비충돌 판정
        테스트할 범위: 부동소수점 정밀도 한계에서 비충돌
        커버하는 함수 및 데이터: 미세한 간격 처리
        기대되는 안정성: 작은 간격에서도 False 반환 보장
        """
        # Given - 아주 작은 간격으로 분리된 사각형들
        result = self.detector._check_aabb_collision(
            0, 0, 2, 2, 2.0000001, 0, 2, 2
        )

        # Then - 비충돌로 정확히 판정
        assert result is False, (
            '아주 작은 간격도 비충돌로 정확히 판정되어야 함'
        )

    def test_매우_미세하게_겹침_검증_성공_시나리오(self):
        """3.5. 매우 미세하게 겹침 검증 (성공 시나리오)

        목적: 매우 작은 겹침도 정확한 충돌로 감지
        테스트할 범위: 부동소수점 정밀도 한계에서 충돌
        커버하는 함수 및 데이터: 미세한 겹침 처리
        기대되는 안정성: 작은 겹침에서도 True 반환 보장
        """
        # Given - 아주 작게 겹치는 사각형들
        result = self.detector._check_aabb_collision(
            0, 0, 2, 2, 1.9999999, 0, 2, 2
        )

        # Then - 충돌로 정확히 감지
        assert result is True, '아주 작은 겹침도 충돌로 정확히 감지되어야 함'

    def test_매우_큰_사각형_내부에_매우_작은_점_검증_성공_시나리오(self):
        """3.6. 매우 큰 사각형 내부에 매우 작은 점 검증 (성공 시나리오)

        목적: 크기 극한값에서도 정확한 포함 관계 검사
        테스트할 범위: 극한적 크기 차이에서의 충돌 검사
        커버하는 함수 및 데이터: 거대한 범위에서 점 검사
        기대되는 안정성: 극한값에서도 정확한 결과 보장
        """
        # Given - 거대한 사각형 내부의 미세한 점
        result = self.detector._check_aabb_collision(
            1e-10, 1e-10, 0, 0, 0, 0, 1e6, 1e6
        )

        # Then - 정상적으로 충돌 감지
        assert result is True, '거대한 사각형 내부의 점은 충돌로 감지되어야 함'

    def test_매우_큰_사각형_외부에_매우_작은_점_검증_성공_시나리오(self):
        """3.7. 매우 큰 사각형 외부에 매우 작은 점 검증 (성공 시나리오)

        목적: 크기 극한값에서 정확한 외부 판정
        테스트할 범위: 극한적 크기에서의 비충돌 검사
        커버하는 함수 및 데이터: 거대한 범위 밖 점 검사
        기대되는 안정성: 극한값에서도 정확한 비충돌 판정 보장
        """
        # Given - 거대한 사각형 밖의 점
        result = self.detector._check_aabb_collision(
            1e6 + 1, 1e6 + 1, 0, 0, 0, 0, 1e6, 1e6
        )

        # Then - 정확히 비충돌 판정
        assert result is False, (
            '거대한 사각형 밖의 점은 비충돌로 판정되어야 함'
        )

    def test_음의_좌표에서_모서리_접촉_검증_성공_시나리오(self):
        """3.8. 음의 좌표에서 모서리 접촉 검증 (성공 시나리오)

        목적: 음수 영역에서도 정확한 모서리 접촉 감지
        테스트할 범위: 음수 좌표에서의 충돌 검사
        커버하는 함수 및 데이터: 음수 영역 처리
        기대되는 안정성: 음수 좌표에서도 정확한 결과 보장
        """
        # Given - 음수 영역에서 모서리 접촉하는 사각형들
        result = self.detector._check_aabb_collision(
            -5, -5, 2, 2, -3, -5, 2, 2
        )

        # Then - 정상적으로 충돌 감지
        assert result is True, '음수 영역에서도 모서리 접촉이 감지되어야 함'

    def test_0크기_선분들의_교차_검증_성공_시나리오(self):
        """3.9. 0크기 선분들의 교차 검증 (성공 시나리오)

        목적: 특수한 점 케이스(선분)에서의 교차 감지
        테스트할 범위: width=0 또는 height=0 케이스
        커버하는 함수 및 데이터: 선분과 선분의 교차점
        기대되는 안정성: 선분 교차에서 True 반환 보장
        """
        # Given - 한 점에서 교차하는 두 선분 (수직, 수평)
        result = self.detector._check_aabb_collision(0, 0, 4, 0, 0, 0, 0, 4)

        # Then - 교차점에서 충돌 감지
        assert result is True, '교차하는 선분들은 충돌로 감지되어야 함'

    def test_0크기_선분들의_평행_비접촉_검증_성공_시나리오(self):
        """3.10. 0크기 선분들의 평행 비접촉 검증 (성공 시나리오)

        목적: 평행한 선분들의 비충돌 정확한 판정
        테스트할 범위: 평행 선분들의 비교
        커버하는 함수 및 데이터: 동일한 크기 0 선분들
        기대되는 안정성: 평행 선분에서 False 반환 보장
        """
        # Given - 평행하지만 접촉하지 않는 두 수평 선분
        result = self.detector._check_aabb_collision(0, 0, 4, 0, 0, 1, 4, 0)

        # Then - 비충돌로 정확히 판정
        assert result is False, '평행한 선분들은 비충돌로 판정되어야 함'

    def test_대각선_방향_최소_겹침_검증_성공_시나리오(self):
        """3.11. 대각선 방향 최소 겹침 검증 (성공 시나리오)

        목적: 대각선으로 아주 작게 겹치는 경우의 충돌 감지
        테스트할 범위: 복합 경계 조건에서의 충돌
        커버하는 함수 및 데이터: X, Y축 모두 미세 겹침
        기대되는 안정성: 대각선 미세 겹침에서 True 반환 보장
        """
        # Given - 대각선으로 아주 작게 겹치는 사각형들
        result = self.detector._check_aabb_collision(
            0, 0, 2, 2, 1.9999, 1.9999, 2, 2
        )

        # Then - 충돌로 정확히 감지
        assert result is True, '대각선 미세 겹침도 충돌로 감지되어야 함'

    def test_한축_완전겹침_다른축_모서리접촉_검증_성공_시나리오(self):
        """3.12. 한축 완전겹침 다른축 모서리접촉 검증 (성공 시나리오)

        목적: 축별로 다른 겹침 상태에서의 충돌 감지
        테스트할 범위: X축 완전 겹침, Y축 모서리 접촉
        커버하는 함수 및 데이터: 축별 개별 조건 조합
        기대되는 안정성: 복합 조건에서 True 반환 보장
        """
        # Given - Y축 모서리 접촉, X축 완전 겹침
        result = self.detector._check_aabb_collision(0, 0, 4, 2, 0, 2, 4, 2)

        # Then - 충돌로 정확히 감지
        assert result is True, '축별 겹침 조합에서도 충돌이 감지되어야 함'

    def test_매우_큰_사각형들의_모서리_정확_접촉_성능_검증_성공_시나리오(self):
        """3.13. 매우 큰 사각형들의 모서리 정확 접촉 + 성능 검증 (성공 시나리오)

        목적: 대용량 데이터에서도 빠른 연산 성능 보장
        테스트할 범위: 거대한 사각형들의 모서리 접촉과 성능
        커버하는 함수 및 데이터: 1e8 좌표, 1e6 크기 처리
        기대되는 안정성: 대용량에서도 < 1ms 성능과 정확한 결과 보장
        """
        # Given - 거대한 사각형들의 모서리 접촉
        start_time = time.time()
        result = self.detector._check_aabb_collision(
            1e8, 1e8, 1e6, 1e6, 1e8 + 1e6, 1e8, 1e6, 1e6
        )
        execution_time = (time.time() - start_time) * 1000  # ms로 변환

        # Then - 충돌 감지 및 성능 검증
        assert result is True, '거대한 사각형들의 모서리 접촉이 감지되어야 함'
        assert execution_time < 1.0, (
            f'실행 시간이 1ms를 초과했습니다: {execution_time}ms'
        )

    def test_매우_큰_사각형들의_미세_겹침_성능_검증_성공_시나리오(self):
        """3.14. 매우 큰 사각형들의 미세 겹침 + 성능 검증 (성공 시나리오)

        목적: 대용량 미세 겹침에서의 성능과 정확성 검증
        테스트할 범위: 거대한 사각형들의 0.1 단위 겹침
        커버하는 함수 및 데이터: 대용량 데이터에서 미세 겹침
        기대되는 안정성: < 1ms 성능과 정확한 충돌 감지 보장
        """
        # Given - 거대한 사각형들의 미세 겹침
        start_time = time.time()
        result = self.detector._check_aabb_collision(
            1e8, 1e8, 1e6, 1e6, 1e8 + 1e6 - 0.1, 1e8, 1e6, 1e6
        )
        execution_time = (time.time() - start_time) * 1000

        # Then - 미세 겹침 감지 및 성능 검증
        assert result is True, '거대한 사각형들의 미세 겹침이 감지되어야 함'
        assert execution_time < 1.0, (
            f'실행 시간이 1ms를 초과했습니다: {execution_time}ms'
        )

    def test_매우_큰_사각형들의_미세_비접촉_성능_검증_성공_시나리오(self):
        """3.15. 매우 큰 사각형들의 미세 비접촉 + 성능 검증 (성공 시나리오)

        목적: 대용량 미세 간격에서의 성능과 정확성 검증
        테스트할 범위: 거대한 사각형들의 0.1 단위 간격
        커버하는 함수 및 데이터: 대용량 데이터에서 미세 간격
        기대되는 안정성: < 1ms 성능과 정확한 비충돌 판정 보장
        """
        # Given - 거대한 사각형들의 미세 간격
        start_time = time.time()
        result = self.detector._check_aabb_collision(
            1e8, 1e8, 1e6, 1e6, 1e8 + 1e6 + 0.1, 1e8, 1e6, 1e6
        )
        execution_time = (time.time() - start_time) * 1000

        # Then - 미세 비접촉 판정 및 성능 검증
        assert result is False, (
            '거대한 사각형들의 미세 간격이 비충돌로 판정되어야 함'
        )
        assert execution_time < 1.0, (
            f'실행 시간이 1ms를 초과했습니다: {execution_time}ms'
        )

    # Assert 조건 검증 테스트들
    def test_음수_너비_입력_시_AssertionError_발생_검증(self):
        """입력 검증: 음수 너비 입력 시 AssertionError 발생 검증

        목적: 개발자 가정 위반 시 즉시 오류 발견
        테스트할 범위: w1 < 0 조건 검증
        기대되는 안정성: 개발 단계에서 잘못된 입력 즉시 차단
        """
        # Given & When & Then - 음수 너비로 AssertionError 발생
        with pytest.raises(
            AssertionError, match='Width w1 must be non-negative'
        ):
            self.detector._check_aabb_collision(0, 0, -1, 2, 0, 0, 2, 2)

    def test_잘못된_타입_입력_시_AssertionError_발생_검증(self):
        """입력 검증: 잘못된 타입 입력 시 AssertionError 발생 검증

        목적: 개발자 가정 위반 시 타입 오류 즉시 발견
        테스트할 범위: 문자열 타입 입력
        기대되는 안정성: 개발 단계에서 타입 오류 즉시 차단
        """
        # Given & When & Then - 문자열 타입으로 AssertionError 발생
        with pytest.raises(AssertionError, match='x1 must be numeric'):
            self.detector._check_aabb_collision('invalid', 0, 2, 2, 0, 0, 2, 2)


class TestCollisionSystem:
    """Test cases for CollisionSystem functionality."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.collision_system = CollisionSystem()
        self.entity_manager = EntityManager()

    def test_collision_detector_교체_기능_검증_성공_시나리오(self):
        """CollisionSystem의 collision detector 교체 기능 검증 (성공 시나리오)

        목적: Strategy 패턴으로 충돌 감지 알고리즘 교체 가능성 검증
        테스트할 범위: set_collision_detector 메서드
        커버하는 함수 및 데이터: detector 교체와 상태 변경
        기대되는 안정성: 런타임 알고리즘 교체 정상 동작 보장
        """
        # Given - 새로운 collision detector
        new_detector = BruteForceCollisionDetector()

        # When - detector 교체
        self.collision_system.set_collision_detector(new_detector)

        # Then - detector가 정상적으로 교체됨
        assert self.collision_system.get_collision_detector() is new_detector
        assert isinstance(
            self.collision_system.get_collision_detector(),
            BruteForceCollisionDetector,
        )

    def test_point_collision_검사_기능_검증_성공_시나리오(self):
        """CollisionSystem의 point collision 검사 기능 검증 (성공 시나리오)

        목적: 특정 점과 엔티티의 충돌 검사 기능 검증
        테스트할 범위: check_point_collision 메서드
        커버하는 함수 및 데이터: 점-엔티티 충돌 검사
        기대되는 안정성: 점 충돌 검사 정확성 보장
        """
        # Given - 엔티티 생성 및 컴포넌트 추가
        entity = self.entity_manager.create_entity()
        self.entity_manager.add_component(entity, PositionComponent(5, 5))
        self.entity_manager.add_component(entity, CollisionComponent(4, 4))

        # When - 점 충돌 검사 (엔티티 내부 점)
        result_inside = self.collision_system.check_point_collision(
            5, 5, self.entity_manager, entity
        )
        result_outside = self.collision_system.check_point_collision(
            10, 10, self.entity_manager, entity
        )

        # Then - 내부는 충돌, 외부는 비충돌
        assert result_inside is True, '엔티티 내부 점은 충돌로 감지되어야 함'
        assert result_outside is False, (
            '엔티티 외부 점은 비충돌로 판정되어야 함'
        )
