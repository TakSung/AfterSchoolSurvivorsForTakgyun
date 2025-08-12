"""
ProjectileComponent 유닛 테스트

이 테스트는 투사체 컴포넌트의 물리적 속성과 상태 관리 기능을 검증합니다.
특히 Vector2 연산의 정확성과 영벡터 문제 해결책도 함께 테스트합니다.
"""

from src.components.projectile_component import ProjectileComponent
from src.utils.vector2 import Vector2


class TestProjectileComponent:
    """ProjectileComponent에 대한 포괄적 테스트 클래스"""

    def test_기본_초기화_및_기본값_설정_검증_성공_시나리오(self) -> None:
        """1. 기본 초기화 및 기본값 설정 검증 (성공 시나리오)

        목적: 기본 파라미터로 생성 시 모든 기본값이 올바르게 설정되는지 검증
        테스트할 범위: __post_init__ 메서드의 기본값 설정 로직
        커버하는 함수 및 데이터: hit_targets, direction 초기화
        기대되는 안정성: 일관된 기본 상태로 객체 생성 보장
        """
        # Given - 기본 파라미터로 ProjectileComponent 생성
        projectile = ProjectileComponent()

        # When - 객체가 생성됨 (__post_init__ 자동 호출)

        # Then - 모든 기본값이 올바르게 설정됨
        assert projectile.hit_targets == [], (
            'hit_targets는 빈 리스트로 초기화되어야 함'
        )
        assert projectile.direction == Vector2.zero(), (
            'direction은 Vector2.zero()로 초기화되어야 함'
        )
        assert projectile.velocity == 300.0, '기본 velocity는 300.0이어야 함'
        assert projectile.lifetime == 3.0, '기본 lifetime은 3.0이어야 함'
        assert projectile.max_lifetime == 3.0, (
            '기본 max_lifetime은 3.0이어야 함'
        )
        assert projectile.damage == 10, '기본 damage는 10이어야 함'
        assert projectile.owner_id is None, '기본 owner_id는 None이어야 함'
        assert projectile.piercing is False, '기본 piercing은 False여야 함'
        assert projectile.max_velocity == 1000.0, (
            '기본 max_velocity는 1000.0이어야 함'
        )

    def test_velocity_최대값_제한_적용_검증_성공_시나리오(self) -> None:
        """2. velocity 최대값 제한 적용 검증 (성공 시나리오)

        목적: max_velocity를 초과하는 velocity가 자동으로 제한되는지 검증
        테스트할 범위: __post_init__의 velocity 제한 로직
        커버하는 함수 및 데이터: velocity, max_velocity
        기대되는 안정성: 과도한 속도값으로 인한 게임 밸런스 파괴 방지
        """
        # Given - max_velocity(1000.0)를 초과하는 velocity=1500.0으로 생성
        projectile = ProjectileComponent(velocity=1500.0, max_velocity=1000.0)

        # When - 객체가 초기화됨 (__post_init__ 실행)

        # Then - velocity가 max_velocity로 제한됨
        assert projectile.velocity == 1000.0, (
            'velocity가 max_velocity로 제한되어야 함'
        )
        assert projectile.max_velocity == 1000.0, (
            'max_velocity는 변경되지 않아야 함'
        )

    def test_lifetime_최대값_제한_적용_검증_성공_시나리오(self) -> None:
        """3. lifetime 최대값 제한 적용 검증 (성공 시나리오)

        목적: max_lifetime을 초과하는 lifetime이 자동으로 제한되는지 검증
        테스트할 범위: __post_init__의 lifetime 제한 로직
        커버하는 함수 및 데이터: lifetime, max_lifetime
        기대되는 안정성: 과도한 수명으로 인한 메모리 누수 방지
        """
        # Given - max_lifetime을 초과하는 lifetime으로 생성
        projectile = ProjectileComponent(lifetime=10.0, max_lifetime=5.0)

        # When - 객체가 초기화됨 (__post_init__ 실행)

        # Then - lifetime이 max_lifetime으로 제한됨
        assert projectile.lifetime == 5.0, (
            'lifetime이 max_lifetime으로 제한되어야 함'
        )
        assert projectile.max_lifetime == 5.0, (
            'max_lifetime은 변경되지 않아야 함'
        )

    def test_validate_정상_데이터_검증_성공_시나리오(self) -> None:
        """4. validate() 정상 데이터 검증 성공 (성공 시나리오)

        목적: 모든 속성이 유효한 상태에서 validate() 메서드가 True를 반환하는지 검증
        테스트할 범위: validate() 메서드의 유효성 검사 로직
        커버하는 함수 및 데이터: velocity, lifetime, max_lifetime, damage 검증 조건
        기대되는 안정성: 유효한 투사체 데이터에 대한 정확한 판단 보장
        """
        # Given - 모든 속성이 유효한 ProjectileComponent
        projectile = ProjectileComponent(
            velocity=200.0, lifetime=2.0, max_lifetime=3.0, damage=15
        )

        # When - validate() 호출
        result = projectile.validate()

        # Then - True 반환
        assert result is True, (
            '유효한 데이터에 대해 validate()는 True를 반환해야 함'
        )

    def test_get_velocity_vector_벡터_계산_정확성_검증_성공_시나리오(
        self,
    ) -> None:
        """5. get_velocity_vector() 벡터 계산 정확성 (성공 시나리오)

        목적: 방향과 속도를 곱한 속도 벡터가 올바르게 계산되는지 검증
        테스트할 범위: get_velocity_vector() 메서드와 Vector2 연산
        커버하는 함수 및 데이터: direction, velocity, Vector2 곱셈 연산
        기대되는 안정성: 물리 엔진에서 사용할 정확한 속도 벡터 제공
        """
        # Given - direction=(1,0), velocity=100인 투사체
        direction = Vector2(1.0, 0.0)
        projectile = ProjectileComponent(direction=direction, velocity=100.0)

        # When - get_velocity_vector() 호출
        velocity_vector = projectile.get_velocity_vector()

        # Then - Vector2(100, 0) 반환, magnitude=100 확인
        assert velocity_vector.x == 100.0, 'velocity_vector.x는 100.0이어야 함'
        assert velocity_vector.y == 0.0, 'velocity_vector.y는 0.0이어야 함'
        assert abs(velocity_vector.magnitude - 100.0) < 1e-10, (
            'magnitude는 100.0이어야 함'
        )

    def test_update_lifetime_수명_감소_정상_동작_검증_성공_시나리오(
        self,
    ) -> None:
        """6. update_lifetime() 수명 감소 정상 동작 (성공 시나리오)

        목적: delta_time만큼 lifetime이 정확히 감소하는지 검증
        테스트할 범위: update_lifetime() 메서드의 시간 업데이트 로직
        커버하는 함수 및 데이터: lifetime 상태 변경
        기대되는 안정성: 정확한 시간 기반 수명 관리 보장
        """
        # Given - lifetime=3.0인 투사체
        projectile = ProjectileComponent(lifetime=3.0)
        original_lifetime = projectile.lifetime

        # When - update_lifetime(1.5) 호출
        delta_time = 1.5
        projectile.update_lifetime(delta_time)

        # Then - lifetime이 1.5로 감소
        expected_lifetime = original_lifetime - delta_time
        assert projectile.lifetime == expected_lifetime, (
            f'lifetime이 {expected_lifetime}로 감소해야 함'
        )
        assert projectile.lifetime == 1.5, 'lifetime이 정확히 1.5여야 함'

    def test_get_lifetime_ratio_비율_계산_정확성_검증_성공_시나리오(
        self,
    ) -> None:
        """7. get_lifetime_ratio() 비율 계산 정확성 (성공 시나리오)

        목적: 남은 수명의 비율이 올바르게 계산되는지 검증
        테스트할 범위: get_lifetime_ratio() 메서드의 비율 계산 로직
        커버하는 함수 및 데이터: lifetime, max_lifetime 비율 계산
        기대되는 안정성: UI나 시각 효과에서 사용할 정확한 수명 비율 제공
        """
        # Given - lifetime=2.0, max_lifetime=5.0인 투사체
        projectile = ProjectileComponent(lifetime=2.0, max_lifetime=5.0)

        # When - get_lifetime_ratio() 호출
        ratio = projectile.get_lifetime_ratio()

        # Then - 0.4 반환
        expected_ratio = 2.0 / 5.0
        assert abs(ratio - expected_ratio) < 1e-10, (
            f'비율은 {expected_ratio}여야 함'
        )
        assert abs(ratio - 0.4) < 1e-10, '비율은 정확히 0.4여야 함'

    def test_add_hit_target_타겟_추가_및_중복_방지_검증_성공_시나리오(
        self,
    ) -> None:
        """8. add_hit_target() 타겟 추가 및 중복 방지 (성공 시나리오)

        목적: 타겟이 올바르게 추가되고 중복이 방지되는지 검증
        테스트할 범위: add_hit_target() 메서드의 타겟 관리 로직
        커버하는 함수 및 데이터: hit_targets 리스트 변경, 중복 검사
        기대되는 안정성: 관통 투사체의 정확한 타겟 추적 보장
        """
        # Given - 빈 hit_targets를 가진 투사체
        projectile = ProjectileComponent()
        assert projectile.hit_targets == [], (
            '초기 hit_targets는 빈 리스트여야 함'
        )

        # When - add_hit_target("enemy1") 두 번 호출
        projectile.add_hit_target('enemy1')
        projectile.add_hit_target('enemy1')  # 중복 추가 시도

        # Then - hit_targets에 "enemy1"이 한 번만 추가됨
        assert len(projectile.hit_targets) == 1, (
            'hit_targets 길이는 1이어야 함'
        )
        assert 'enemy1' in projectile.hit_targets, (
            'enemy1이 hit_targets에 있어야 함'
        )
        assert projectile.hit_targets.count('enemy1') == 1, (
            'enemy1은 한 번만 있어야 함'
        )

    def test_create_towards_target_정상적인_방향_계산_검증_성공_시나리오(
        self,
    ) -> None:
        """9. create_towards_target() 정상적인 방향 계산 (성공 시나리오)

        목적: 시작점에서 목표점으로의 정규화된 방향벡터가 올바르게 계산되는지 검증
        테스트할 범위: create_towards_target() 클래스 메서드와 Vector2 연산
        커버하는 함수 및 데이터: Vector2.from_tuple(), normalize() 연산
        기대되는 안정성: 타겟 지향 투사체 생성 시 정확한 방향 설정 보장
        """
        # Given - start_pos=(0,0), target_pos=(3,4)
        start_pos = (0.0, 0.0)
        target_pos = (3.0, 4.0)

        # When - create_towards_target() 호출
        projectile = ProjectileComponent.create_towards_target(
            start_pos=start_pos,
            target_pos=target_pos,
            velocity=200.0,
            damage=15,
        )

        # Then - direction의 magnitude=1.0, 올바른 정규화된 방향벡터 반환
        assert abs(projectile.direction.magnitude - 1.0) < 1e-10, (
            'direction의 크기는 1.0이어야 함'
        )

        # 방향벡터 검증: (3,4)를 정규화하면 (0.6, 0.8)
        expected_x = 3.0 / 5.0  # 0.6
        expected_y = 4.0 / 5.0  # 0.8
        assert abs(projectile.direction.x - expected_x) < 1e-10, (
            f'direction.x는 {expected_x}여야 함'
        )
        assert abs(projectile.direction.y - expected_y) < 1e-10, (
            f'direction.y는 {expected_y}여야 함'
        )

        # 기타 속성 확인
        assert projectile.velocity == 200.0, 'velocity는 설정값과 같아야 함'
        assert projectile.damage == 15, 'damage는 설정값과 같아야 함'

    def test_velocity_0_경계값_처리_검증_실패_시나리오(self) -> None:
        """10. velocity=0.0 경계값 처리 (실패 시나리오)

        목적: velocity가 0일 때 validate()가 False를 반환하는지 검증
        테스트할 범위: validate() 메서드의 velocity > 0 조건 검사
        커버하는 함수 및 데이터: velocity 유효성 검증
        기대되는 안정성: 무효한 속도값에 대한 정확한 검증 제공
        """
        # Given - velocity=0.0으로 설정
        projectile = ProjectileComponent(velocity=0.0)

        # When - validate() 호출
        result = projectile.validate()

        # Then - False 반환 (velocity > 0 조건 위반)
        assert result is False, (
            'velocity=0.0일 때 validate()는 False를 반환해야 함'
        )

    def test_lifetime_0_만료_상태_검증_성공_시나리오(self) -> None:
        """11. lifetime=0.0 만료 상태 검증 (성공 시나리오)

        목적: lifetime이 0일 때 is_expired()가 True를 반환하는지 검증
        테스트할 범위: is_expired() 메서드의 만료 조건 검사
        커버하는 함수 및 데이터: lifetime <= 0 조건
        기대되는 안정성: 만료된 투사체에 대한 정확한 상태 판단 보장
        """
        # Given - lifetime=0.0인 투사체
        projectile = ProjectileComponent(lifetime=0.0)

        # When - is_expired() 호출
        result = projectile.is_expired()

        # Then - True 반환
        assert result is True, (
            'lifetime=0.0일 때 is_expired()는 True를 반환해야 함'
        )

    def test_max_lifetime_0인_경우_get_lifetime_ratio_처리_검증_성공_시나리오(
        self,
    ) -> None:
        """12. max_lifetime=0인 경우 get_lifetime_ratio() 처리 (성공 시나리오)

        목적: max_lifetime이 0일 때 0으로 나누기 오류 없이 0.0을 반환하는지 검증
        테스트할 범위: get_lifetime_ratio() 메서드의 0 나누기 방지 로직
        커버하는 함수 및 데이터: max_lifetime <= 0 조건 처리
        기대되는 안정성: 잘못된 설정에서도 안전한 동작 보장
        """
        # Given - max_lifetime=0인 투사체
        projectile = ProjectileComponent(max_lifetime=0.0, lifetime=1.0)

        # When - get_lifetime_ratio() 호출
        ratio = projectile.get_lifetime_ratio()

        # Then - 0.0 반환 (의도된 설계)
        assert ratio == 0.0, (
            'max_lifetime=0일 때 get_lifetime_ratio()는 0.0을 반환해야 함'
        )

    def test_create_towards_target_동일_좌표_영벡터_처리_검증_성공_시나리오(
        self,
    ) -> None:
        """13. create_towards_target() 동일 좌표 영벡터 처리 (성공 시나리오)

        목적: 시작점과 목표점이 동일할 때 기본 방향으로 처리되는지 검증
        테스트할 범위: create_towards_target()의 영벡터 문제 해결 로직
        커버하는 함수 및 데이터: 영벡터 검사, 기본 방향 설정
        기대되는 안정성: 예외적 상황에서도 안정적인 투사체 생성 보장
        """
        # Given - start_pos=(100,100), target_pos=(100,100) (정확히 동일)
        start_pos = (100.0, 100.0)
        target_pos = (100.0, 100.0)

        # When - create_towards_target() 호출
        projectile = ProjectileComponent.create_towards_target(
            start_pos=start_pos, target_pos=target_pos
        )

        # Then - direction=Vector2(1.0, 0.0) (기본 우측 방향) 반환
        assert projectile.direction.x == 1.0, (
            '영벡터 상황에서 direction.x는 1.0이어야 함'
        )
        assert projectile.direction.y == 0.0, (
            '영벡터 상황에서 direction.y는 0.0이어야 함'
        )
        assert abs(projectile.direction.magnitude - 1.0) < 1e-10, (
            'direction의 크기는 1.0이어야 함'
        )

    def test_create_towards_target_부동소수점_오차_범위_영벡터_처리_검증_성공_시나리오(
        self,
    ) -> None:
        """14. create_towards_target() 부동소수점 오차 범위 영벡터 처리 (성공 시나리오)

        목적: 부동소수점 오차 범위 내 좌표에서 영벡터로 처리되는지 검증
        테스트할 범위: 영벡터 판단 임계값(1e-6) 로직
        커버하는 함수 및 데이터: magnitude() < 1e-6 조건, 기본 방향 설정
        기대되는 안정성: 부동소수점 연산 오차에 강건한 처리 보장
        """
        # Given - start_pos=(0,0), target_pos=(1e-7, 1e-7) (오차 범위 내)
        start_pos = (0.0, 0.0)
        target_pos = (1e-7, 1e-7)

        # When - create_towards_target() 호출
        projectile = ProjectileComponent.create_towards_target(
            start_pos=start_pos, target_pos=target_pos
        )

        # Then - direction=Vector2(1.0, 0.0) (기본 우측 방향) 반환
        assert projectile.direction.x == 1.0, (
            '오차 범위 영벡터에서 direction.x는 1.0이어야 함'
        )
        assert projectile.direction.y == 0.0, (
            '오차 범위 영벡터에서 direction.y는 0.0이어야 함'
        )
        assert abs(projectile.direction.magnitude - 1.0) < 1e-10, (
            'direction의 크기는 1.0이어야 함'
        )

    def test_update_lifetime_매우_큰_delta_time_처리_검증_성공_시나리오(
        self,
    ) -> None:
        """15. update_lifetime() 매우 큰 delta_time 처리 (성공 시나리오)

        목적: 매우 큰 delta_time에 대해서도 올바르게 계산되는지 검증
        테스트할 범위: update_lifetime() 메서드의 극값 처리
        커버하는 함수 및 데이터: lifetime 음수 허용, is_expired() 연동
        기대되는 안정성: 극단적 시간 변화에도 안정적인 수명 관리 보장
        """
        # Given - lifetime=2.0인 투사체
        projectile = ProjectileComponent(lifetime=2.0)

        # When - update_lifetime(100.0) 호출
        projectile.update_lifetime(100.0)

        # Then - lifetime이 -98.0이 됨 (음수 허용, is_expired()=True)
        assert projectile.lifetime == -98.0, 'lifetime이 정확히 -98.0이어야 함'
        assert projectile.is_expired() is True, (
            '매우 큰 delta_time 후 is_expired()는 True여야 함'
        )

    def test_has_hit_target_존재하지_않는_타겟_확인_검증_성공_시나리오(
        self,
    ) -> None:
        """16. has_hit_target() 존재하지 않는 타겟 확인 (성공 시나리오)

        목적: 충돌하지 않은 타겟에 대해 False를 반환하는지 검증
        테스트할 범위: has_hit_target() 메서드의 타겟 검색 로직
        커버하는 함수 및 데이터: hit_targets 리스트 검색
        기대되는 안정성: 타겟 충돌 이력의 정확한 조회 보장
        """
        # Given - hit_targets=["enemy1"]인 투사체
        projectile = ProjectileComponent()
        projectile.add_hit_target('enemy1')

        # When - has_hit_target("enemy2") 호출
        result = projectile.has_hit_target('enemy2')

        # Then - False 반환
        assert result is False, (
            '충돌하지 않은 타겟에 대해 has_hit_target()은 False를 반환해야 함'
        )

        # 기존 타겟은 여전히 존재하는지 확인
        assert projectile.has_hit_target('enemy1') is True, (
            '기존 타겟 enemy1은 여전히 존재해야 함'
        )

    def test_validate_무효한_데이터_다중_조건_검증_실패_시나리오(self) -> None:
        """17. validate() 무효한 데이터 다중 조건 검증 (실패 시나리오)

        목적: 여러 조건이 동시에 위반될 때 validate()가 False를 반환하는지 검증
        테스트할 범위: validate() 메서드의 모든 검증 조건
        커버하는 함수 및 데이터: velocity, lifetime, max_lifetime, damage 조건들
        기대되는 안정성: 복합적으로 무효한 데이터에 대한 정확한 판단 보장
        """
        # Given - 여러 조건이 위반된 ProjectileComponent (assert를 우회하여 생성 후 직접 수정)
        projectile = ProjectileComponent()

        # 개발자 가정 우회하여 무효한 값들 직접 설정
        projectile.velocity = 0.0  # velocity > 0 위반
        projectile.max_lifetime = 0.0  # max_lifetime > 0 위반
        projectile.damage = -5  # damage >= 0 위반
        # lifetime은 음수 설정이 어려우므로 다른 조건들만 위반

        # When - validate() 호출
        result = projectile.validate()

        # Then - False 반환
        assert result is False, (
            '여러 조건 위반 시 validate()는 False를 반환해야 함'
        )

    def test_Vector2_연산_통합_검증_성공_시나리오(self) -> None:
        """18. Vector2 연산 통합 검증 (성공 시나리오)

        목적: ProjectileComponent에서 사용하는 Vector2 연산들이 정확한지 통합 검증
        테스트할 범위: Vector2의 zero(), from_tuple(), magnitude(), normalize() 연산
        커버하는 함수 및 데이터: Vector2 클래스의 모든 사용 메서드
        기대되는 안정성: 직접 작성한 Vector2 클래스의 정확성 보장
        """
        # Given - 다양한 Vector2 연산이 필요한 상황들

        # Vector2.zero() 검증
        zero_vector = Vector2.zero()
        assert zero_vector.x == 0.0, 'Vector2.zero().x는 0.0이어야 함'
        assert zero_vector.y == 0.0, 'Vector2.zero().y는 0.0이어야 함'

        # Vector2.from_tuple() 검증
        tuple_vector = Vector2.from_tuple((3.0, 4.0))
        assert tuple_vector.x == 3.0, (
            'from_tuple로 생성한 벡터의 x는 3.0이어야 함'
        )
        assert tuple_vector.y == 4.0, (
            'from_tuple로 생성한 벡터의 y는 4.0이어야 함'
        )

        # magnitude 검증
        magnitude = tuple_vector.magnitude
        expected_magnitude = 5.0  # sqrt(3^2 + 4^2) = 5
        assert abs(magnitude - expected_magnitude) < 1e-10, (
            f'magnitude는 {expected_magnitude}여야 함'
        )

        # normalize() 검증
        normalized = tuple_vector.normalize()
        assert abs(normalized.magnitude - 1.0) < 1e-10, (
            '정규화된 벡터의 크기는 1.0이어야 함'
        )
        assert abs(normalized.x - 0.6) < 1e-10, (
            '정규화된 벡터의 x는 0.6이어야 함'
        )
        assert abs(normalized.y - 0.8) < 1e-10, (
            '정규화된 벡터의 y는 0.8이어야 함'
        )

    def test_복합_시나리오_수명과_타겟_관리_통합_검증_성공_시나리오(
        self,
    ) -> None:
        """19. 복합 시나리오 - 수명과 타겟 관리 통합 검증 (성공 시나리오)

        목적: 수명 관리와 타겟 관리 기능이 함께 동작할 때의 정확성 검증
        테스트할 범위: update_lifetime(), add_hit_target(), is_expired() 연동
        커버하는 함수 및 데이터: 복합적인 상태 변화 시나리오
        기대되는 안정성: 실제 게임에서의 복합 상황에 대한 안정적 동작 보장
        """
        # Given - 관통 투사체 생성
        projectile = ProjectileComponent(
            lifetime=3.0, piercing=True, velocity=400.0
        )

        # When - 시간이 지나면서 여러 타겟을 충돌
        projectile.add_hit_target('enemy1')
        projectile.update_lifetime(1.0)  # lifetime: 3.0 -> 2.0

        projectile.add_hit_target('enemy2')
        projectile.update_lifetime(1.5)  # lifetime: 2.0 -> 0.5

        projectile.add_hit_target('enemy3')
        projectile.update_lifetime(1.0)  # lifetime: 0.5 -> -0.5

        # Then - 모든 상태가 올바르게 관리됨
        assert len(projectile.hit_targets) == 3, (
            '3개의 타겟이 충돌 기록에 있어야 함'
        )
        assert 'enemy1' in projectile.hit_targets, (
            'enemy1이 충돌 기록에 있어야 함'
        )
        assert 'enemy2' in projectile.hit_targets, (
            'enemy2가 충돌 기록에 있어야 함'
        )
        assert 'enemy3' in projectile.hit_targets, (
            'enemy3이 충돌 기록에 있어야 함'
        )

        assert projectile.lifetime == -0.5, '최종 lifetime은 -0.5여야 함'
        assert projectile.is_expired() is True, '투사체가 만료 상태여야 함'

        # 수명 비율도 올바르게 계산되는지 확인
        ratio = projectile.get_lifetime_ratio()
        assert ratio == 0.0, '만료된 투사체의 lifetime_ratio는 0.0이어야 함'

    def test_불변_조건_확인_검증_성공_시나리오(self) -> None:
        """20. 불변 조건 확인 검증 (성공 시나리오)

        목적: 객체 생성 후 변경되지 않아야 할 속성들이 보존되는지 검증
        테스트할 범위: max_lifetime, max_velocity, owner_id, damage, piercing 불변성
        커버하는 함수 및 데이터: 불변 조건으로 정의된 속성들
        기대되는 안정성: 의도하지 않은 속성 변경으로 인한 오류 방지
        """
        # Given - 초기 설정으로 투사체 생성
        initial_max_lifetime = 5.0
        initial_max_velocity = 800.0
        initial_owner_id = 'player1'
        initial_damage = 25
        initial_piercing = True

        projectile = ProjectileComponent(
            max_lifetime=initial_max_lifetime,
            max_velocity=initial_max_velocity,
            owner_id=initial_owner_id,
            damage=initial_damage,
            piercing=initial_piercing,
        )

        # When - 다양한 메서드 실행 (상태를 변경하는 작업들)
        projectile.update_lifetime(1.0)
        projectile.add_hit_target('enemy1')
        projectile.add_hit_target('enemy2')

        # Then - 불변 조건들이 유지됨
        assert projectile.max_lifetime == initial_max_lifetime, (
            'max_lifetime은 변경되지 않아야 함'
        )
        assert projectile.max_velocity == initial_max_velocity, (
            'max_velocity는 변경되지 않아야 함'
        )
        assert projectile.owner_id == initial_owner_id, (
            'owner_id는 변경되지 않아야 함'
        )
        assert projectile.damage == initial_damage, (
            'damage는 변경되지 않아야 함'
        )
        assert projectile.piercing == initial_piercing, (
            'piercing은 변경되지 않아야 함'
        )

        # hit_targets 리스트의 참조는 유지되지만 내용은 변경 가능
        assert isinstance(projectile.hit_targets, list), (
            'hit_targets는 여전히 리스트여야 함'
        )
        assert len(projectile.hit_targets) == 2, (
            'hit_targets에 2개 항목이 있어야 함'
        )
