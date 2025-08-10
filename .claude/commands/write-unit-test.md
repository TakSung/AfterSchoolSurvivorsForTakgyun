# 단위 테스트 작성 명령어

## 설명
AfterSchoolSurvivors 게임 프로젝트에서 pytest 경고 없는 안전한 단위 테스트 코드를 한국어 명명법으로 생성

## 사용법
```
/write-unit-test-for-py <클래스이름>
```

## 실행 절차

### 입력 검증 단계
```python
def validate_input(class_name: str) -> tuple[bool, str]:
    if not class_name:
        return False, "클래스 이름이 필요합니다"
    if not class_name[0].isupper():
        return False, "클래스 이름은 PascalCase여야 합니다"
    return True, "입력이 유효합니다"
```

### 처리 단계
```python
def execute_write_unit_test(class_name: str) -> dict:
    try:
        # 1단계: 규칙 참조 및 적용
        rules = load_rules("@/.claude/rules/unit-test-rule.md")
        
        # 2단계: 클래스 분석 및 테스트 생성
        test_code = generate_korean_test_code(class_name, rules)
        
        # 3단계: pytest 경고 방지 검증
        validate_pytest_safety(test_code)
        
        return format_test_output(test_code)
        
    except Exception as e:
        return {"error": True, "message": f"테스트 생성 실패: {str(e)}"}
```

### 출력 포맷팅
```python
def format_test_output(test_code: str) -> dict:
    return {
        "success": True,
        "message": "단위 테스트가 성공적으로 생성되었습니다",
        "data": {
            "test_file": test_code,
            "helper_classes": "Mock* 접두사로 생성됨",
            "naming_convention": "한국어 테스트 메서드명 적용"
        },
        "format": "python"
    }
```

## 규칙 참조
**핵심 규칙**: @/.claude/rules/unit-test-rule.md 참조

### 필수 적용 사항
1. **pytest 경고 방지**: Helper 클래스는 Mock* 접두사 사용
2. **한국어 테스트명**: `test_{대상}_{상황}_{결과}_시나리오` 패턴
3. **5단계 Docstring**: 목적, 테스트 범위, 커버 함수, 기대 안정성
4. **Given-When-Then**: 테스트 구조 명확화
5. **ECS 패턴**: AfterSchoolSurvivors 아키텍처 특화

## 출력 예시

### 성공 케이스
```json
{
    "success": true,
    "message": "단위 테스트가 성공적으로 생성되었습니다",
    "data": {
        "test_class": "TestEntityManager",
        "test_methods": [
            "test_엔티티_생성_고유ID_할당_성공_시나리오",
            "test_컴포넌트_추가_정상_등록_성공_시나리오"
        ],
        "helper_classes": ["MockPositionComponent", "MockHealthComponent"],
        "ai_dev_comments": "pytest 경고 방지 주석 포함"
    },
    "format": "python"
}
```

### 실패 케이스
```json
{
    "success": false,
    "message": "클래스 분석 실패: 해당 클래스를 찾을 수 없습니다",
    "error_code": "CLASS_NOT_FOUND",
    "suggestion": "클래스 경로와 이름을 확인하세요"
}
```

## 사용자 편집 가이드
이 명령어는 다음 부분을 사용자가 직접 수정할 수 있습니다:
- [ ] 테스트 시나리오 추가/제거
- [ ] Helper 클래스 접두사 변경 (Mock, Fake, Dummy, Stub 등)
- [ ] 한국어 메시지 커스터마이징
- [ ] ECS 패턴 테스트 추가
- [ ] AI-DEV 주석 형식 조정

**규칙 참조 파일**: @/.claude/rules/unit-test-rule.md