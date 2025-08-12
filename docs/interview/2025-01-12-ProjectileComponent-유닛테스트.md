# ProjectileComponent 유닛테스트 설계 인터뷰

## 인터뷰 정보
- **날짜**: 2025-01-12
- **대상**: ProjectileComponent
- **인터뷰어**: 유닛 테스트 설계 전문가
- **목적**: ProjectileComponent에 대한 포괄적 유닛테스트 시나리오 설계

---

## 1. 핵심 책임 및 비즈니스 로직 분석

### 핵심 책임 (Core Responsibility)
- **투사체 엔티티의 물리적 속성과 상태를 관리하는 데이터 컨테이너**

### 비즈니스 로직 (Business Logic)
1. **투사체 수명 관리**: `lifetime` 감소와 만료 검사를 통한 자동 소멸 메커니즘
2. **물리 기반 이동**: `direction`과 `velocity`를 조합한 벡터 기반 이동 계산 
3. **투사체 특성 관리 시스템**: `piercing` 플래그와 `hit_targets` 리스트를 통한 다중 적 타격 관리 (관통, 튕기는 특성 등 확장 가능)
4. **타겟 지향 생성**: 시작점과 목표점을 받아 정규화된 방향벡터를 계산하는 팩토리 메서드
5. **데이터 유효성 검증**: 투사체 속성값들의 논리적 일관성 검사

---

## 2. 입력 파라미터 분석

### 초기화 파라미터들
- **`direction`**:
    - **추정 타입 및 형식**: `Vector2 | None`, 기본값 `None` (자동으로 `Vector2.zero()`로 초기화)
    - **주요 경계값**: `Vector2.zero()`, 정규화된 벡터, 정규화되지 않은 벡터
    - **개발자 가정**: 잘못된 타입은 assert로 방지 (테스트하지 않음)

- **`velocity`**:
    - **추정 타입 및 형식**: `float`, 양수 (기본값 300.0)
    - **주요 경계값**: `0.0`, `0.1`, `max_velocity`(1000.0)
    - **개발자 가정**: 음수, None은 assert로 방지 (테스트하지 않음)
    - **비즈니스 로직**: max_velocity를 넘으면 자동으로 max_velocity로 제한

- **`lifetime`**:
    - **추정 타입 및 형식**: `float`, 0 이상 (기본값 3.0)
    - **주요 경계값**: `0.0`, `0.1`, `max_lifetime`과 같은 값
    - **개발자 가정**: 음수는 assert로 방지 (테스트하지 않음)
    - **비즈니스 로직**: max_lifetime보다 크면 자동으로 max_lifetime으로 제한

- **`max_lifetime`**:
    - **추정 타입 및 형식**: `float`, 양수 (기본값 3.0)
    - **주요 경계값**: `0.1`, `10.0`, 매우 큰 값

### 메서드 파라미터들
- **`update_lifetime(delta_time)`**:
    - **추정 타입 및 형식**: `float`, 0 이상
    - **주요 경계값**: `0.0`, `lifetime과 같은 값`, 매우 큰 값
    - **개발자 가정**: 음수, None은 assert로 방지 (테스트하지 않음)

- **`create_towards_target()` 클래스 메서드**:
    - **`start_pos, target_pos`**: `tuple[float, float]`
    - **주요 경계값**: 같은 위치, 매우 먼 거리, 대각선 방향
    - **개발자 가정**: None, 잘못된 길이의 튜플은 assert로 방지 (테스트하지 않음)
    - **`velocity, lifetime`**: 위와 동일한 검증 로직 적용

---

## 3. 출력 분석 및 예외 상황

### 각 메서드의 반환값들
- **`validate()`**: `bool` - 컴포넌트 데이터의 유효성 상태
- **`get_velocity_vector()`**: `Vector2` - 방향과 속도를 곱한 물리 벡터 
- **`is_expired()`**: `bool` - 수명 만료 여부
- **`get_lifetime_ratio()`**: `float` - 0.0~1.0 범위의 수명 비율
- **`has_hit_target(target_id)`**: `bool` - 특정 타겟 충돌 이력 여부
- **`create_towards_target()`**: `ProjectileComponent` - 목표 지향 투사체 인스턴스

### 예외 상황 처리 방식
- **개발자 가정 위반 시**: AssertionError 발생 (유닛테스트에서 검증하지 않음)
- **`get_lifetime_ratio()` 메서드**: `max_lifetime <= 0`인 경우 0.0을 반환 (의도된 설계)
- **`create_towards_target()` 영벡터 문제**: 
  - **문제**: start_pos와 target_pos가 동일할 때 normalize() 실패 가능
  - **해결책**: 게임 개발 트렌드 기반 처리 - 부동소수점 오차를 고려한 영벡터 검사 후 기본 방향(우측) 제공
  - **심도있는 테스트 케이스 필요**: 정확히 같은 좌표, 부동소수점 오차 범위 내 좌표, 매우 작은 거리 등

---

## 4. 상태 변화 및 부수 효과 분석

### 사전 조건 (Pre-conditions)
- 초기화 시: 모든 파라미터는 적절한 타입이어야 함 (assert로 보장)
- `update_lifetime()`: `delta_time`은 0 이상이어야 함
- `create_towards_target()`: 위치 튜플들은 유효한 형식이어야 함

### 사후 조건 (Post-conditions)
- **초기화 후**: `hit_targets`는 빈 리스트로, `direction`은 Vector2로 초기화됨
- **`update_lifetime()` 실행 후**: `lifetime`이 `delta_time`만큼 감소함
- **`add_hit_target()` 실행 후**: `hit_targets` 리스트에 새로운 타겟이 추가됨 (중복 방지)
- **velocity/lifetime 제한 적용 후**: `max_velocity`, `max_lifetime` 범위 내로 제한됨

### 부수 효과 (Side Effects)
- **`update_lifetime()`**: `self.lifetime` 값을 직접 변경함
- **`add_hit_target()`**: `self.hit_targets` 리스트를 변경함
- **`__post_init__()`**: 여러 속성들을 동시에 초기화/제한함

### 외부 의존성
- Vector2 클래스의 메서드들(`zero()`, `from_tuple()`, `normalize()`, `magnitude()`)을 사용함

---

## 5. 모킹 대상 확인

### 모킹하지 않는 대상 (실제 객체 사용)
- **Vector2 클래스**: 안정적인 수학적 유틸리티 클래스로 간주하여 실제 객체 사용
  - 이유: Vector2를 더 실제적인 상황에서 검증할 기회로 활용
  - 메서드: `zero()`, `from_tuple()`, `normalize()`, `magnitude()` 등

### 모킹이 필요한 대상
- 없음 (ProjectileComponent는 순수한 데이터 컴포넌트로 외부 시스템과의 상호작용이 없음)

---

## 6. 가정 및 불변 조건

### 가정 (Assumptions - 테스트하지 않음)
- Python의 내장 라이브러리와 dataclass는 정상 동작한다
- 부동소수점 연산의 기본적인 정밀도는 보장된다
- 메모리 할당과 객체 생성은 성공한다

### 검증 대상 (Vector2 클래스)
- **Vector2 클래스의 수학적 연산들**: 직접 작성한 클래스이므로 정확성을 검증해야 함
  - `zero()`: (0, 0) 벡터 생성 확인
  - `from_tuple()`: 튜플에서 Vector2 변환 확인  
  - `normalize()`: 정규화 결과 확인 (magnitude = 1.0)
  - `magnitude()`: 크기 계산 정확성 확인

### 불변 조건 (Invariants)
- 입력된 객체들의 ID는 변경되지 않는다
- `max_lifetime`, `max_velocity` 값은 초기화 후 변경되지 않는다
- `hit_targets` 리스트의 참조는 유지된다 (내용은 변경 가능)
- `owner_id`, `damage`, `piercing` 값은 생성 후 외부에서 변경되지 않는다

---

## 7. 검증 조건 정리

### 입력 검증 조건
- `velocity`: 0.0, 경계값, max_velocity 초과 시 제한
- `lifetime`: 0.0, 경계값, max_lifetime 초과 시 제한  
- `direction`: None 처리, Vector2 객체 처리
- `delta_time`: 0.0, 정상값, 매우 큰 값
- 위치 튜플들: 동일 좌표, 일반적 거리, 매우 먼 거리

### 출력 검증 조건
- 각 메서드의 반환 타입과 값 범위
- Vector2 연산 결과의 정확성 (normalize, magnitude 등)
- 영벡터 처리 시 기본 방향(우측) 반환

### 상태 변화 검증 조건
- `update_lifetime()` 후 lifetime 감소
- `add_hit_target()` 후 hit_targets 변경
- 초기화 시 max 값 제한 적용
- `__post_init__()` 시 기본값 설정

### 불변 조건
- 객체 ID 유지, 최대값 상수 유지, 리스트 참조 유지

### 특별 검증 조건 (영벡터 문제)
- 정확히 같은 좌표에서 기본 방향 반환
- 부동소수점 오차 범위 내 좌표 처리
- 매우 작은 거리에서의 동작

---

## 8. 최종 유닛 테스트 시나리오

### 1. 핵심 기능
- **책임**: 투사체 엔티티의 물리적 속성과 상태를 관리하는 데이터 컨테이너
- **비즈니스 로직**: 수명 관리, 물리 기반 이동, 투사체 특성 관리, 타겟 지향 생성, 데이터 유효성 검증

### 2. 함수 시그니처
```python
@dataclass
class ProjectileComponent(Component):
    def __post_init__(self) -> None
    def validate(self) -> bool
    def get_velocity_vector(self) -> Vector2
    def is_expired(self) -> bool
    def update_lifetime(self, delta_time: float) -> None
    def get_lifetime_ratio(self) -> float
    def has_hit_target(self, target_id: str) -> bool
    def add_hit_target(self, target_id: str) -> None
    
    @classmethod
    def create_towards_target(cls, start_pos: tuple[float, float], target_pos: tuple[float, float], ...) -> 'ProjectileComponent'
```

### 3. 사전 조건 및 가정
- **사전 조건**: 
  - 모든 파라미터는 적절한 타입이어야 함 (assert로 보장)
  - delta_time, 위치 튜플들은 유효한 형식이어야 함
- **가정 (테스트하지 않음)**:
  - Python 내장 라이브러리와 dataclass는 정상 동작
  - 부동소수점 연산의 기본 정밀도 보장
  - 메모리 할당과 객체 생성 성공

### 4. 사후 조건 및 불변 조건
- **사후 조건**:
  - 초기화 후: hit_targets는 빈 리스트, direction은 Vector2로 설정
  - update_lifetime 후: lifetime이 delta_time만큼 감소
  - add_hit_target 후: hit_targets에 새 타겟 추가 (중복 방지)
- **불변 조건**:
  - 객체 ID, max_값들, 리스트 참조 유지

### 5. 모킹 대상
- **모킹하지 않음**: Vector2 클래스 (실제 객체로 검증하여 Vector2 정확성도 확인)

### 6. 테스트 시나리오 (Given-When-Then)

#### A. 성공 시나리오

**Test 1.1**: 기본 초기화 및 기본값 설정 검증 *(검증 조건: 초기화, 기본값 설정)*
- **Given**: 기본 파라미터로 ProjectileComponent 생성
- **When**: 객체가 생성됨
- **Then**: hit_targets=[], direction=Vector2.zero(), 모든 기본값이 올바르게 설정됨

**Test 1.2**: velocity 최대값 제한 적용 검증 *(검증 조건: max_velocity 제한)*
- **Given**: max_velocity(1000.0)를 초과하는 velocity=1500.0으로 생성
- **When**: 객체가 초기화됨
- **Then**: velocity가 1000.0으로 제한됨

**Test 1.3**: lifetime 최대값 제한 적용 검증 *(검증 조건: max_lifetime 제한)*
- **Given**: max_lifetime을 초과하는 lifetime으로 생성
- **When**: 객체가 초기화됨
- **Then**: lifetime이 max_lifetime으로 제한됨

**Test 1.4**: validate() 정상 데이터 검증 성공 *(검증 조건: 데이터 유효성)*
- **Given**: 모든 속성이 유효한 ProjectileComponent
- **When**: validate() 호출
- **Then**: True 반환

**Test 1.5**: get_velocity_vector() 벡터 계산 정확성 *(검증 조건: Vector2 연산 정확성)*
- **Given**: direction=(1,0), velocity=100인 투사체
- **When**: get_velocity_vector() 호출
- **Then**: Vector2(100, 0) 반환, magnitude=100 확인

**Test 1.6**: update_lifetime() 수명 감소 정상 동작 *(검증 조건: 상태 변화)*
- **Given**: lifetime=3.0인 투사체
- **When**: update_lifetime(1.5) 호출
- **Then**: lifetime이 1.5로 감소

**Test 1.7**: get_lifetime_ratio() 비율 계산 정확성 *(검증 조건: 출력 정확성)*
- **Given**: lifetime=2.0, max_lifetime=5.0인 투사체
- **When**: get_lifetime_ratio() 호출
- **Then**: 0.4 반환

**Test 1.8**: add_hit_target() 타겟 추가 및 중복 방지 *(검증 조건: 상태 변화, 중복 처리)*
- **Given**: 빈 hit_targets를 가진 투사체
- **When**: add_hit_target("enemy1") 두 번 호출
- **Then**: hit_targets에 "enemy1"이 한 번만 추가됨

**Test 1.9**: create_towards_target() 정상적인 방향 계산 *(검증 조건: Vector2 연산, 팩토리 메서드)*
- **Given**: start_pos=(0,0), target_pos=(3,4)
- **When**: create_towards_target() 호출
- **Then**: direction의 magnitude=1.0, 올바른 정규화된 방향벡터 반환

#### B. 경계값 및 특수 케이스 시나리오

**Test 2.1**: velocity=0.0 경계값 처리 *(검증 조건: 경계값)*
- **Given**: velocity=0.0으로 설정
- **When**: validate() 호출
- **Then**: False 반환 (velocity > 0 조건 위반)

**Test 2.2**: lifetime=0.0 만료 상태 검증 *(검증 조건: 만료 처리)*
- **Given**: lifetime=0.0인 투사체
- **When**: is_expired() 호출
- **Then**: True 반환

**Test 2.3**: max_lifetime=0인 경우 get_lifetime_ratio() 처리 *(검증 조건: 0 나누기 방지)*
- **Given**: max_lifetime=0인 투사체
- **When**: get_lifetime_ratio() 호출
- **Then**: 0.0 반환 (의도된 설계)

**Test 2.4**: create_towards_target() 동일 좌표 영벡터 처리 *(검증 조건: 영벡터 문제)*
- **Given**: start_pos=(100,100), target_pos=(100,100) (정확히 동일)
- **When**: create_towards_target() 호출
- **Then**: direction=Vector2(1.0, 0.0) (기본 우측 방향) 반환

**Test 2.5**: create_towards_target() 부동소수점 오차 범위 영벡터 처리 *(검증 조건: 부동소수점 오차 처리)*
- **Given**: start_pos=(0,0), target_pos=(1e-7, 1e-7) (오차 범위 내)
- **When**: create_towards_target() 호출
- **Then**: direction=Vector2(1.0, 0.0) (기본 우측 방향) 반환

**Test 2.6**: update_lifetime() 매우 큰 delta_time 처리 *(검증 조건: 큰 값 처리)*
- **Given**: lifetime=2.0인 투사체
- **When**: update_lifetime(100.0) 호출
- **Then**: lifetime이 -98.0이 됨 (음수 허용, is_expired()=True)

**Test 2.7**: has_hit_target() 존재하지 않는 타겟 확인 *(검증 조건: 타겟 검색)*
- **Given**: hit_targets=["enemy1"]인 투사체
- **When**: has_hit_target("enemy2") 호출
- **Then**: False 반환

### 7. 검증 조건 커버리지 매트릭스

- **초기화 및 기본값**: Test 1.1에서 검증
- **max_velocity 제한**: Test 1.2에서 검증  
- **max_lifetime 제한**: Test 1.3에서 검증
- **데이터 유효성**: Test 1.4, Test 2.1에서 검증
- **Vector2 연산 정확성**: Test 1.5, Test 1.9에서 검증
- **상태 변화**: Test 1.6, Test 1.8에서 검증
- **출력 정확성**: Test 1.7에서 검증
- **경계값 처리**: Test 2.1, Test 2.2, Test 2.3에서 검증
- **영벡터 문제**: Test 2.4, Test 2.5에서 검증
- **극값 처리**: Test 2.6에서 검증
- **타겟 관리**: Test 1.8, Test 2.7에서 검증

**최종 검증**: 위 시나리오들이 성공하면 7단계에서 정리한 모든 검증 조건이 커버됩니다.

---

## 9. 최종 사용자 검증
