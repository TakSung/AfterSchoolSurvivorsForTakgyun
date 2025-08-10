# 명령어 작성 Command

## 목적
사용자가 직접 편집할 수 있는 명령어를 한국어로 작성하되, 출력 포맷을 정확히 통제할 수 있는 최신 프롬프트 엔지니어링 기술을 적용합니다.

## 사용법
```
/write-command <명령어이름>
```

## 고급 프롬프트 엔지니어링: 출력 포맷 정밀 제어

### 1단계: 구조화된 출력 템플릿 (Structured Output Control)

**SOTA 기법: JSON Schema + Format Enforcement**

```json
{
  "command_template": {
    "name": "string (Korean allowed)",
    "purpose": "string (Korean description)",
    "usage": "string (exact format pattern)",
    "output_schema": {
      "type": "object",
      "properties": {
        "success": {"type": "boolean"},
        "message": {"type": "string", "language": "korean"},
        "data": {"type": "object"},
        "format": {"type": "string", "enum": ["markdown", "json", "code", "text"]}
      },
      "required": ["success", "message"]
    }
  }
}
```

### 2단계: 출력 포맷 강제 패턴 (Format Enforcement)

```python
# 필수 템플릿 - 절대 벗어나지 말 것:

COMMAND_OUTPUT_TEMPLATE = """
# 명령어: {command_name}

## 설명
{korean_description}

## 사용법
```
/{command_name} <매개변수>
```

## 실행 절차

### 입력 검증 단계
```python
def validate_input(input_params: dict) -> tuple[bool, str]:
    if not {validation_condition}:
        return False, "{korean_error_message}"
    return True, "입력이 유효합니다"
```

### 처리 단계
```python
def execute_{command_name}(params: dict) -> dict:
    try:
        # 1단계: {processing_step_1}
        result_1 = {action_1}
        
        # 2단계: {processing_step_2}  
        result_2 = {action_2}
        
        # 3단계: 결과 포맷팅
        return format_output(result_1, result_2)
        
    except Exception as e:
        return {{"error": True, "message": f"{korean_error_prefix}: {{str(e)}}"}}
```

### 출력 포맷팅
```python
def format_output(data: Any) -> dict:
    return {{
        "success": True,
        "message": "{korean_success_message}",
        "data": data,
        "timestamp": datetime.now().isoformat(),
        "format": "{output_format_type}"
    }}
```

## 출력 예시

### 성공 케이스
```json
{{
    "success": true,
    "message": "{korean_success_message}",
    "data": {{
        {expected_output_structure}
    }},
    "format": "{format_type}"
}}
```

### 실패 케이스
```json
{{
    "success": false,
    "message": "{korean_error_message}",
    "error_code": "{error_code}",
    "suggestion": "{korean_improvement_suggestion}"
}}
```

## 사용자 편집 가이드
이 명령어는 다음 부분을 사용자가 직접 수정할 수 있습니다:
- [ ] 명령어 이름 변경
- [ ] 한국어 설명 수정
- [ ] 매개변수 추가/제거
- [ ] 출력 포맷 조정
- [ ] 에러 메시지 커스터마이징
"""
```

### 3단계: 출력 형식별 특화 패턴

#### A. 마크다운 출력 명령어
```python
MARKDOWN_OUTPUT_TEMPLATE = """
## 명령어 실행 결과

### ✅ 처리 상태
{korean_status_message}

### 📊 결과 데이터
{formatted_data_in_korean}

### 🔧 추가 작업
{korean_next_steps}

---
*생성 시간: {timestamp}*
"""
```

#### B. 코드 출력 명령어  
```python
CODE_OUTPUT_TEMPLATE = """
```{language}
# {korean_code_description}
{generated_code}
```

**설명**: {korean_explanation}
**사용법**: {korean_usage_instruction}
"""
```

#### C. JSON 데이터 출력 명령어
```python
JSON_OUTPUT_TEMPLATE = """
```json
{{
    "결과": {{
        "상태": "{korean_status}",
        "데이터": {json_data},
        "메시지": "{korean_user_message}"
    }},
    "메타정보": {{
        "생성시간": "{timestamp}",
        "명령어": "{command_name}"
    }}
}}
```
"""
```

### 4단계: 동적 포맷 선택 시스템

```python
# 출력 포맷을 자동으로 선택하는 고급 시스템
class OutputFormatController:
    def __init__(self):
        self.format_patterns = {
            'code': self.format_as_code,
            'data': self.format_as_json,
            'guide': self.format_as_markdown,
            'error': self.format_as_error
        }
    
    def auto_select_format(self, content_type: str, user_preference: str = None):
        """사용자 선호도와 내용 타입에 따른 자동 포맷 선택"""
        if user_preference:
            return self.format_patterns.get(user_preference, self.format_as_markdown)
        
        # 내용 기반 자동 선택
        format_mapping = {
            'function': 'code',
            'class': 'code', 
            'data': 'data',
            'tutorial': 'guide',
            'exception': 'error'
        }
        
        return self.format_patterns.get(format_mapping.get(content_type), self.format_as_markdown)
```

### 5단계: 사용자 커스터마이징 지원

```python
# 사용자가 쉽게 수정할 수 있는 설정 부분
USER_CUSTOMIZABLE_SETTINGS = {
    "언어설정": {
        "기본언어": "한국어",
        "코드주석": "한국어", 
        "에러메시지": "한국어",
        "사용자메시지": "한국어"
    },
    "출력형식": {
        "기본포맷": "markdown",
        "코드포맷": "syntax_highlighted",
        "데이터포맷": "json_pretty",
        "에러포맷": "user_friendly"
    },
    "동작설정": {
        "자동검증": True,
        "상세로그": False,
        "타임스탬프": True,
        "진행표시": True
    }
}

def apply_user_customization(settings: dict, output: dict) -> dict:
    """사용자 설정을 적용하여 출력 조정"""
    if settings["언어설정"]["사용자메시지"] == "한국어":
        output["message"] = translate_to_korean(output["message"])
    
    if settings["출력형식"]["기본포맷"] == "markdown":
        return format_as_markdown(output)
    
    return output
```

### 6단계: 검증 및 품질 보증

```python
def validate_command_output(output: dict, expected_schema: dict) -> tuple[bool, str]:
    """명령어 출력이 예상 스키마를 따르는지 검증"""
    required_fields = ['success', 'message']
    
    for field in required_fields:
        if field not in output:
            return False, f"필수 필드 '{field}'가 누락되었습니다"
    
    if not isinstance(output['success'], bool):
        return False, "'success' 필드는 불린 타입이어야 합니다"
    
    if not isinstance(output['message'], str) or not contains_korean(output['message']):
        return False, "'message' 필드는 한국어 문자열이어야 합니다"
    
    return True, "출력 형식이 올바릅니다"

def contains_korean(text: str) -> bool:
    """텍스트에 한국어가 포함되어 있는지 확인"""
    korean_pattern = r'[가-힣]'
    return bool(re.search(korean_pattern, text))
```

## 명령어 카테고리별 특화 패턴

### 개발 도구 명령어
```python
DEVELOPMENT_COMMAND_TEMPLATE = """
# 개발 명령어: {command_name}

## 목적
{korean_purpose}

## 코드 생성 포맷
```python
# {korean_code_description}
{generated_python_code}
```

## 실행 결과
**상태**: {korean_status}
**생성된 파일**: {file_list}
**다음 단계**: {korean_next_steps}
"""
```

### 분석 도구 명령어
```python
ANALYSIS_COMMAND_TEMPLATE = """
# 분석 명령어: {command_name}

## 분석 결과

### 📈 주요 지표
{korean_metrics_summary}

### 📋 상세 분석
{detailed_analysis_in_korean}

### 💡 개선 제안
{korean_improvement_suggestions}
"""
```

### 설정 관리 명령어
```python
CONFIG_COMMAND_TEMPLATE = """
# 설정 명령어: {command_name}

## 현재 설정
```json
{current_config_json}
```

## 변경된 설정
{korean_change_summary}

## 적용 결과
**성공**: {success_status}
**메시지**: {korean_result_message}
"""
```

## 고급 기술 적용

1. **구조화된 출력**: JSON Schema를 통한 정확한 포맷 제어
2. **동적 포맷 선택**: 내용과 사용자 선호에 따른 자동 포맷팅
3. **사용자 커스터마이징**: 쉬운 설정 변경 지원
4. **검증 시스템**: 출력 품질 자동 검사
5. **한국어 우선**: 사용자 대상 메시지는 모두 한국어
6. **포맷 강제**: 템플릿 벗어남 방지 시스템

## 메타 명령어: 명령어 생성 검증

```python
def validate_new_command(command_spec: dict) -> dict:
    """새로 생성된 명령어의 품질 검증"""
    checks = {
        "한국어_설명": contains_korean(command_spec.get('description', '')),
        "출력_스키마": 'output_schema' in command_spec,
        "에러_처리": 'error_handling' in command_spec,
        "사용자_편집성": 'customizable_parts' in command_spec
    }
    
    passed = sum(checks.values())
    total = len(checks)
    
    return {
        "success": passed == total,
        "message": f"검증 결과: {passed}/{total} 항목 통과",
        "details": {k: "✅" if v else "❌" for k, v in checks.items()},
        "score": f"{(passed/total)*100:.0f}점"
    }
```