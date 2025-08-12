# HealthComponent 유닛 테스트 인터뷰 기록

**날짜**: 2025-01-12  
**인터뷰 대상**: HealthComponent  
**인터뷰어**: 유닛 테스트 설계 전문가  
**목적**: HealthComponent에 대한 포괄적인 유닛 테스트 시나리오 설계

---

## 1. 핵심 책임 및 비즈니스 로직 분석

### 핵심 책임 (Core Responsibility)
- 엔티티의 생명력 관리 및 데미지/힐링 처리

### 비즈니스 로직
1. **체력 상태 관리**: 현재/최대 체력 추적, 생존/사망 판정
2. **데미지 처리**: 무적 상태 및 데미지 면역 시간 고려한 데미지 적용
3. **힐링 처리**: 최대 체력 한도 내에서 체력 회복
4. **체력 재생**: 시간 경과에 따른 자동 체력 회복
5. **체력 관련 상태 계산**: 체력 비율, 중상 판정 등

**사용자 확인**: ✅ 맞음, 추가 사항 없음

---

## 2. 입력 파라미터 분석

### `damage` (take_damage 메서드)
- **타입 및 형식**: `int`, `0 이상의 정수`
- **주요 경계값**: `0`, `1`, `current_health와 같은 값`, `current_health보다 큰 값`
- **개발자 가정 (assert 처리)**: `음수 불가`, `None 불가`
- **허용 타입**: `float` 타입도 허용 (int로 자동 변환)

### `current_time` (take_damage 메서드)
- **타입 및 형식**: `float`, `0.0 이상의 시간값 (초 단위)`
- **주요 경계값**: `0.0`, `last_damage_time과 같은 값`, `last_damage_time + damage_immunity_time`
- **개발자 가정 (assert 처리)**: `음수 불가`, `None 불가`, `str 타입 불가`

### `amount` (heal 메서드)
- **타입 및 형식**: `int`, `0 이상의 정수`
- **주요 경계값**: `0`, `1`, `max_health - current_health`, `max_health보다 큰 값`
- **개발자 가정 (assert 처리)**: `음수 불가`, `None 불가`
- **허용 타입**: `float` 타입도 허용 (int로 자동 변환)

### `new_max_health` (set_max_health 메서드)
- **타입 및 형식**: `int`, `1 이상의 정수`
- **주요 경계값**: `0`, `1`, `current_health와 같은 값`
- **개발자 가정 (assert 처리)**: `0 이하 불가`, `None 불가`
- **허용 타입**: `float` 타입도 허용 (int로 자동 변환)

### `delta_time` (update_regeneration 메서드)
- **타입 및 형식**: `float`, `0.0 이상의 시간 간격 (초 단위)`
- **주요 경계값**: `0.0`, `매우 작은 값`, `매우 큰 값`
- **개발자 가정 (assert 처리)**: `음수 불가`, `None 불가`, `str 타입 불가`

### `threshold` (is_critically_wounded 메서드)
- **타입 및 형식**: `float`, `0.0~1.0 사이의 비율값`
- **주요 경계값**: `0.0`, `0.25 (기본값)`, `1.0`
- **개발자 가정 (assert 처리)**: `음수 불가`, `None 불가`, `str 타입 불가`

**사용자 확인**: ✅ AssertionError는 개발자 가정이므로 테스트에서 점검하지 않음

---

## 3. 반환값 및 예외 상황 분석

### 반환값 타입
- `take_damage()`: `int` (실제 적용된 데미지량, 0 이상)
- `heal()`: `int` (실제 회복된 체력량, 0 이상)  
- `is_alive()`, `is_dead()`: `bool` (생존/사망 상태)
- `validate()`: `bool` (유효성 검사 결과)
- `get_health_ratio()`: `float` (0.0~1.0 사이의 체력 비율)
- `is_critically_wounded()`: `bool` (중상 여부)
- `update_regeneration()`: `int` (재생된 체력량, 0 이상)
- `set_max_health()`, `set_invulnerable()`, `full_heal()`: `None` (void 메서드)

### 예외 처리
- 개발자 가정 위반 시: `AssertionError` (테스트 대상 아님)
- 정상 동작 범위: 모든 메서드가 예상 범위 내에서 정상 동작

---

## 4. 상태 변화 및 부수 효과 분석

### 사전 조건 (Pre-conditions)
- 컴포넌트가 유효한 상태로 초기화되어 있어야 함 (`0 <= current_health <= max_health`)
- 시간 관련 메서드는 이전 호출 시점의 시간값이 설정되어 있어야 함

### 사후 조건 (Post-conditions)
- `take_damage()` 실행 후: `current_health` 감소, `last_damage_time` 업데이트
- `heal()` 실행 후: `current_health` 증가 (max_health 한도 내)
- `set_max_health()` 실행 후: `max_health` 변경, 필요시 `current_health` 조정
- `update_regeneration()` 실행 후: `current_health` 증가 (재생량만큼)
- `set_invulnerable()` 실행 후: `is_invulnerable` 상태 변경
- `full_heal()` 실행 후: `current_health`가 `max_health`와 같아짐

### 부수 효과 (Side Effects)
- 모든 메서드는 객체 내부 상태만 변경하며, 외부 시스템에 대한 부수 효과는 없음
- 파일 I/O, 데이터베이스 접근, 네트워크 통신 등의 외부 의존성 없음
- 순수한 메모리 내 상태 변경만 수행

**사용자 확인**: ✅ 내용 정확함

---

## 5. 모킹 대상 확인

### 모킹 필요성
- 외부 의존성 없음 (파일 I/O, 데이터베이스, 네트워크 등)
- 순수한 메모리 내 상태 변경만 수행
- **모킹 대상 없음**

**사용자 확인**: ✅ 모킹 없음

---

## 6. 가정 및 불변 조건

### 가정 (Assumptions - 테스트하지 않음)
- Python 내장 타입 및 연산자는 정상 동작한다
- 메서드 파라미터는 올바른 타입으로 전달된다 (assert로 보장)
- 시스템 시간은 단조증가한다

### 불변 조건 (Invariants)
- 실행 전후 객체의 ID는 변경되지 않는다
- `0 <= current_health <= max_health` 항상 유지
- `max_health > 0` 항상 유지
- 시간 관련 필드는 음수가 되지 않는다

---

## 7. 검증 조건 목록 확정

### 입력 검증 조건
- 경계값 테스트: 0, 최소값, 최대값, current_health와의 관계
- 정상 범위 값들의 올바른 처리
- float 타입 입력의 int 변환 처리

### 출력 검증 조건
- 각 메서드의 올바른 반환값 타입 및 범위
- 상태에 따른 조건부 반환값 (무적, 면역, 사망 등)

### 상태 변화 검증 조건
- 각 메서드 실행 후 내부 상태의 정확한 변경
- 상태 변경의 부작용 (예: max_health 변경 시 current_health 조정)
- 시간 관련 상태 업데이트

### 불변 조건
- 체력 범위 유지 (`0 <= current_health <= max_health`)
- 객체 ID 불변성
- 시간 필드의 음수 방지

**사용자 확인**: ✅ 누락 조건 없음

---

## 8. 최종 유닛 테스트 시나리오

### A. 기본 초기화 및 상태 테스트

**Test 1.1**: 기본 초기화 검증 *(검증 조건: 기본값 설정, 불변 조건)*
- **Given**: 기본 파라미터로 HealthComponent 생성
- **When**: 컴포넌트 속성 조회
- **Then**: 기본값들이 올바르게 설정됨 (current_health=100, max_health=100 등)

**Test 1.2**: 커스텀 초기화 검증 *(검증 조건: 사용자 정의값 설정)*
- **Given**: 사용자 정의 파라미터로 HealthComponent 생성
- **When**: 컴포넌트 속성 조회
- **Then**: 설정한 값들이 정확히 저장됨

**Test 1.3**: __post_init__ 체력 조정 검증 *(검증 조건: 불변 조건 유지)*
- **Given**: current_health > max_health인 상황
- **When**: HealthComponent 초기화
- **Then**: current_health가 max_health로 자동 조정됨

### B. 데미지 처리 테스트

**Test 2.1**: 정상 데미지 적용 검증 *(검증 조건: 상태 변화, 반환값)*
- **Given**: 정상 상태의 HealthComponent
- **When**: take_damage(30, 1.0) 호출
- **Then**: current_health 감소, last_damage_time 업데이트, 실제 데미지량 반환

**Test 2.2**: 과도한 데미지 처리 검증 *(검증 조건: 경계값, 상태 변화)*
- **Given**: current_health=50인 컴포넌트
- **When**: take_damage(100, 1.0) 호출
- **Then**: current_health=0, 실제 데미지는 50만 반환

**Test 2.3**: 무적 상태 데미지 무시 검증 *(검증 조건: 조건부 반환값)*
- **Given**: is_invulnerable=True인 컴포넌트
- **When**: take_damage(50, 1.0) 호출
- **Then**: 체력 변화 없음, 0 반환

**Test 2.4**: 데미지 면역 시간 검증 *(검증 조건: 시간 관련 상태)*
- **Given**: damage_immunity_time=2.0, 최근 데미지 받은 컴포넌트
- **When**: 면역 시간 내에 take_damage 호출
- **Then**: 데미지 무시, 0 반환

**Test 2.5**: float 타입 데미지 처리 검증 *(검증 조건: 타입 변환)*
- **Given**: 정상 상태의 컴포넌트
- **When**: take_damage(25.7, 1.0) 호출
- **Then**: int(25)로 변환되어 처리됨

### C. 힐링 처리 테스트

**Test 3.1**: 정상 힐링 적용 검증 *(검증 조건: 상태 변화, 반환값)*
- **Given**: current_health=50인 컴포넌트
- **When**: heal(30) 호출
- **Then**: current_health=80, 30 반환

**Test 3.2**: 최대 체력 한도 힐링 검증 *(검증 조건: 경계값, 불변 조건)*
- **Given**: current_health=80, max_health=100인 컴포넌트
- **When**: heal(50) 호출
- **Then**: current_health=100, 20 반환

**Test 3.3**: 0 이하 힐링 무시 검증 *(검증 조건: 경계값)*
- **Given**: 정상 상태의 컴포넌트
- **When**: heal(0) 호출
- **Then**: 체력 변화 없음, 0 반환

**Test 3.4**: float 타입 힐링 처리 검증 *(검증 조건: 타입 변환)*
- **Given**: current_health=50인 컴포넌트
- **When**: heal(25.9) 호출
- **Then**: int(25)로 변환되어 처리됨

### D. 최대 체력 설정 테스트

**Test 4.1**: 정상 최대 체력 설정 검증 *(검증 조건: 상태 변화)*
- **Given**: 기본 컴포넌트
- **When**: set_max_health(150) 호출
- **Then**: max_health=150으로 변경

**Test 4.2**: 최대 체력 감소 시 현재 체력 조정 검증 *(검증 조건: 부작용, 불변 조건)*
- **Given**: current_health=100, max_health=100인 컴포넌트
- **When**: set_max_health(80) 호출
- **Then**: max_health=80, current_health=80으로 조정

**Test 4.3**: float 타입 최대 체력 처리 검증 *(검증 조건: 타입 변환)*
- **Given**: 기본 컴포넌트
- **When**: set_max_health(120.7) 호출
- **Then**: int(120)으로 변환되어 설정됨

### E. 상태 확인 메서드 테스트

**Test 5.1**: 생존 상태 확인 검증 *(검증 조건: 출력 검증)*
- **Given**: current_health > 0인 컴포넌트
- **When**: is_alive() 호출
- **Then**: True 반환

**Test 5.2**: 사망 상태 확인 검증 *(검증 조건: 출력 검증)*
- **Given**: current_health = 0인 컴포넌트
- **When**: is_dead() 호출
- **Then**: True 반환

**Test 5.3**: 체력 비율 계산 검증 *(검증 조건: 출력 검증)*
- **Given**: current_health=75, max_health=100인 컴포넌트
- **When**: get_health_ratio() 호출
- **Then**: 0.75 반환

**Test 5.4**: 중상 판정 검증 *(검증 조건: 출력 검증, 경계값)*
- **Given**: current_health=20, max_health=100인 컴포넌트
- **When**: is_critically_wounded(0.25) 호출
- **Then**: True 반환

### F. 재생 시스템 테스트

**Test 6.1**: 정상 재생 처리 검증 *(검증 조건: 상태 변화, 시간 관련)*
- **Given**: regeneration_rate=10.0, current_health=50인 컴포넌트
- **When**: update_regeneration(2.0) 호출
- **Then**: 20 체력 재생, 실제 재생량 반환

**Test 6.2**: 사망 상태 재생 무시 검증 *(검증 조건: 조건부 반환값)*
- **Given**: current_health=0, regeneration_rate=10.0인 컴포넌트
- **When**: update_regeneration(1.0) 호출
- **Then**: 재생 없음, 0 반환

### G. 유효성 검사 및 기타 테스트

**Test 7.1**: 유효성 검사 성공 시나리오 *(검증 조건: 출력 검증)*
- **Given**: 모든 값이 유효한 컴포넌트
- **When**: validate() 호출
- **Then**: True 반환

**Test 7.2**: 유효성 검사 실패 시나리오 *(검증 조건: 출력 검증)*
- **Given**: 무효한 값을 가진 컴포넌트 (음수 체력 등)
- **When**: validate() 호출
- **Then**: False 반환

**Test 7.3**: 무적 상태 설정 검증 *(검증 조건: 상태 변화)*
- **Given**: 기본 컴포넌트
- **When**: set_invulnerable(True) 호출
- **Then**: is_invulnerable=True로 변경

**Test 7.4**: 완전 회복 검증 *(검증 조건: 상태 변화)*
- **Given**: current_health=50인 컴포넌트
- **When**: full_heal() 호출
- **Then**: current_health=max_health가 됨

### H. 불변 조건 검증 테스트

**Test 8.1**: 체력 범위 불변 조건 검증 *(검증 조건: 불변 조건)*
- **Given**: 다양한 상태의 컴포넌트
- **When**: 모든 메서드 실행
- **Then**: `0 <= current_health <= max_health` 항상 유지

**Test 8.2**: 객체 ID 불변 조건 검증 *(검증 조건: 불변 조건)*
- **Given**: 컴포넌트 생성
- **When**: 모든 메서드 실행
- **Then**: 객체 ID 변경되지 않음

---

## 9. 검증 조건 커버리지 매트릭스

- **입력 검증 조건**: Test 2.5, 3.4, 4.3에서 검증됨
- **출력 검증 조건**: Test 5.1~5.4, 7.1~7.2에서 검증됨  
- **상태 변화 검증 조건**: Test 1.1~1.3, 2.1~2.2, 3.1~3.2, 4.1~4.2, 6.1, 7.3~7.4에서 검증됨
- **불변 조건**: Test 8.1~8.2에서 검증됨

**최종 검증**: 위 시나리오들이 성공하면 모든 검증 조건이 커버됩니다.
