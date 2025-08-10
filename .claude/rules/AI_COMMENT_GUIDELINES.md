# AI 주석 시스템 가이드라인

## Meta-Principle
AI가 코드를 작성할 때 비즈니스 로직과 기술적 구현을 명확히 구분하여 향후 유지보수성을 극대화

## Constitutional Constraints
1. MUST: 모든 비즈니스 로직 변경에는 AI-NOTE 주석 필수
2. MUST NOT: 기술적 구현과 비즈니스 로직을 혼재하여 설명
3. IF-THEN: 기술적 문제 해결 시 AI-DEV 주석으로 해결책과 이유 명시

## Execution Procedure

### Step 1: 주석 유형 판단
```python
def determine_comment_type(change_type: str) -> str:
    if change_type in ['business_logic', 'user_requirement', 'game_balance']:
        return "AI-NOTE"
    elif change_type in ['technical_fix', 'performance', 'bug_fix', 'dev_env']:
        return "AI-DEV"
    else:
        return "판단 불가 - 컨텍스트를 다시 확인하세요"
```

### Step 2: 주석 작성
```python
def write_ai_comment(comment_type: str, context: dict) -> str:
    if comment_type == "AI-NOTE":
        return f"""# AI-NOTE : {context['date']} {context['description']}
# - 이유: {context['reason']}
# - 요구사항: {context['requirement']}
# - 히스토리: {context['history']}"""
    
    elif comment_type == "AI-DEV":
        return f"""# AI-DEV : {context['technical_reason']} {context['description']}
# - 문제: {context['problem']}
# - 해결책: {context['solution']}
# - 주의사항: {context['caution']}"""
```

### Step 3: 검증
```python
def validate_comment(comment: str) -> tuple[bool, str]:
    if not comment.startswith(("# AI-NOTE :", "# AI-DEV :")):
        return False, "올바른 AI 주석 형식이 아닙니다"
    
    required_fields = ["이유:", "문제:"] if "AI-DEV" in comment else ["이유:", "요구사항:"]
    for field in required_fields:
        if field not in comment:
            return False, f"필수 필드 '{field}'가 누락되었습니다"
    
    return True, "주석이 올바르게 작성되었습니다"
```

## Few-Shot Examples

### Example 1: 비즈니스 로직 주석 (AI-NOTE)
**Input**: 게임 밸런스 조정을 위한 무기 데미지 배율 시스템 구현
**Output**: 
```python
# AI-NOTE : 2025-01-10 무기별 데미지 배율 시스템 도입
# - 이유: 게임 밸런스 조정을 위한 요구사항 반영
# - 요구사항: 축구공(1.2배), 농구공(1.0배), 야구방망이(1.5배)
# - 히스토리: 기존 고정 데미지에서 무기별 차별화로 변경
def calculate_damage(self, base_damage: int, weapon_type: WeaponType) -> int:
    multiplier = weapon_type.damage_multiplier
    return int(base_damage * multiplier)
```
**Reasoning**: 게임 밸런스라는 비즈니스 요구사항을 반영한 변경이므로 AI-NOTE가 적절함

### Example 2: 기술적 구현 주석 (AI-DEV)
**Input**: 레이스 컨디션 해결을 위한 동기화 메커니즘 추가
**Output**:
```python
# AI-DEV : 레이스 컨디션 방지를 위한 비동기 저장 완료 대기
# - 문제: async 저장과 sync 저장이 동시 실행되어 파일 충돌 발생
# - 해결책: threading.Event로 비동기 작업 완료 신호 대기
# - 주의사항: timeout 설정으로 무한 대기 방지 (100ms)
def save_config(self) -> bool:
    if not self._async_save_event.is_set():
        self._async_save_event.wait(timeout=0.1)
```
**Reasoning**: 기술적 문제 해결이므로 AI-DEV로 문제와 해결책을 명확히 기록

## 상세 작성 규칙

### AI-NOTE : 비즈니스 로직 & 요구사항

**사용 시점**:
- 사용자 요구사항 구현
- 게임 밸런스 조정  
- 도메인 규칙 적용
- UI/UX 개선사항
- 기획 변경사항

**필수 구성요소**:
1. **변경일자**: YYYY-MM-DD 형식
2. **이유**: 왜 이 변경이 필요했는지
3. **요구사항**: 구체적인 요구사항 내용
4. **히스토리**: 이전 버전과의 차이점

**작성 예시**:
```python
# AI-NOTE : 2025-01-15 보스전 특수 디버프 시스템 도입
# - 이유: 게임 난이도 조정 및 보스전 긴장감 증대 요구사항
# - 요구사항: 보스전 시 플레이어 이동속도 30% 감소, 공격력 20% 감소
# - 히스토리: 기존 보스전은 일반 몬스터와 동일한 조건이었음
def apply_boss_debuff(self, player_stats: PlayerStats) -> PlayerStats:
    return PlayerStats(
        speed=player_stats.speed * 0.7,
        attack_power=player_stats.attack_power * 0.8
    )
```

### AI-DEV : 개발 기술적 사항

**사용 시점**:
- 성능 최적화
- 버그 수정
- 라이브러리 사용법
- 알고리즘 구현
- 메모리 관리
- 스레드 안전성
- 예외 처리

**필수 구성요소**:
1. **기술적 이유**: 어떤 기술적 문제를 해결하는지
2. **문제**: 구체적인 기술적 문제 설명
3. **해결책**: 적용한 기술적 해결책
4. **주의사항**: 향후 유지보수 시 알아야 할 점

**작성 예시**:
```python
# AI-DEV : 좌표 변환 성능 최적화를 위한 LRU 캐시 적용
# - 문제: 매 프레임마다 동일한 좌표 변환 연산이 반복되어 CPU 사용률 증가
# - 해결책: 최대 1000개 항목의 LRU 캐시로 변환 결과 재사용
# - 주의사항: 캐시 크기는 메모리 사용량과 성능의 트레이드오프 고려 필요
@lru_cache(maxsize=1000)
def transform_world_to_screen(self, world_pos: Vector2) -> Vector2:
    return self._apply_camera_transform(world_pos)
```

## 히스토리 관리 패턴

### 누적 히스토리 방식
```python
# AI-NOTE : [변경 히스토리]
# - 2025-01-20: 아이템 시너지 효과 15% → 20%로 상향 (밸런스 피드백 반영)
# - 2025-01-15: 보스전 디버프 추가 (난이도 조정 요구사항)
# - 2025-01-10: 무기별 데미지 배율 시스템 도입 (초기 밸런스 요구사항)
# - 2025-01-05: 기본 데미지 계산 로직 구현 (MVP 요구사항)
```

### 단일 변경 방식 (최신 변경만 유지)
```python
# AI-DEV : pytest 경고 해결을 위한 Helper 클래스명 변경 (2025-01-10)
# - 문제: Test*로 시작하는 Helper 클래스가 pytest 수집 대상으로 오인됨
# - 해결책: Mock* 접두사로 변경하여 명확한 구분
# - 결과: 9개 PytestCollectionWarning 제거
```

## 중첩 사용 패턴

```python
# AI-NOTE : 사용자 요구사항 - 실시간 아이템 시너지 계산 시스템
class ItemSynergyCalculator:
    def __init__(self):
        # AI-DEV : 성능 최적화를 위한 시너지 테이블 사전 계산
        # - 문제: 런타임 시너지 계산으로 인한 프레임 드롭 (60fps → 30fps)
        # - 해결책: 모든 가능한 시너지 조합을 사전 계산하여 O(1) 조회
        # - 주의사항: 새 아이템 추가 시 테이블 재계산 필요
        self._precomputed_synergies = self._build_synergy_table()
    
    def calculate_bonus(self, items: list[ItemType]) -> float:
        # AI-DEV : 정렬된 튜플을 키로 사용하여 조합 순서 무관하게 조회
        key = tuple(sorted(item.value for item in items))
        return self._precomputed_synergies.get(key, 1.0)
```

## 업데이트 및 관리 규칙

### 코드 변경 시
1. **기존 AI 주석 검토**: 변경 사항이 기존 주석에 영향을 주는지 확인
2. **주석 업데이트**: 필요시 히스토리에 새로운 변경사항 추가
3. **불필요한 주석 정리**: 더 이상 관련없는 주석은 제거

### 주석 생명주기 관리
- **활성**: 현재 코드와 직접적으로 관련된 주석
- **히스토리**: 과거 변경사항이지만 맥락 이해에 중요한 주석  
- **삭제 대상**: 완전히 관련없어진 주석

## Validation Metrics
- **적용률**: 비즈니스/기술적 변경사항의 95% 이상에 적절한 AI 주석 적용
- **일관성**: 동일한 유형의 변경에 대해 일관된 주석 패턴 사용
- **유용성**: 6개월 후에도 주석을 통해 변경 이유를 명확히 이해 가능

## Anti-Pattern Detection

**자주하는 실수들**:
- AI-NOTE와 AI-DEV를 혼재하여 사용
- 단순한 코드 설명을 AI 주석으로 작성 
- 변경 이유 없이 "구현함"과 같은 무의미한 설명
- 주석 없이 비즈니스 로직 변경

**개선 방안**:
- 변경 전 30초 동안 "이것이 비즈니스 요구사항인가? 기술적 문제 해결인가?" 자문
- 6개월 후 다른 개발자가 이해할 수 있는 수준으로 상세히 작성
- 히스토리 정보를 통해 변경의 맥락 제공