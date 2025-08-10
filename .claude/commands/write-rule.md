# Write Rule Command (Optimized)

## Purpose
Create optimized behavioral rules using advanced prompt engineering for consistent AI behavior with minimal token usage.

## Usage
```
/write-rule <rule_topic>
```

## Advanced Prompt Engineering: Constitutional AI + Few-Shot Pattern

### Step 1: Rule Architecture Framework

**SOTA Pattern: Hierarchical Rule Structure**
```yaml
rule_structure:
  meta_rule:     # High-level principle (1 line)
  constraints:   # Hard boundaries (2-3 items)
  procedures:    # Step-by-step actions (3-5 steps)
  examples:      # Few-shot learning (2 examples)
  validation:    # Success criteria (1-2 metrics)
```

### Step 2: Constitutional AI Template (English for Optimization)

```python
# MANDATORY TEMPLATE - DO NOT DEVIATE:

RULE_TEMPLATE = """
## Rule: {rule_name}

### Meta-Principle
{single_governing_principle}

### Constitutional Constraints
1. MUST: {hard_requirement_1}
2. MUST NOT: {prohibition_1}
3. IF-THEN: {conditional_rule}

### Execution Procedure
```python
def execute_{rule_name}():
    # Step 1: {validation_step}
    if not {condition}:
        return {korean_error_message}
    
    # Step 2: {action_step}
    {specific_action}
    
    # Step 3: {verification_step}
    assert {success_condition}, "{korean_validation_message}"
```

### Few-Shot Examples
#### Example 1: Success Case
**Input**: {example_input_1}
**Output**: {korean_success_output_1}
**Reasoning**: {why_this_works}

#### Example 2: Failure Prevention
**Input**: {example_input_2}
**Output**: {korean_error_output_2}  
**Reasoning**: {why_this_fails}

### Validation Metrics
- **Compliance Rate**: {target_percentage}%
- **Token Efficiency**: < {max_tokens} tokens per invocation
- **Korean Output**: All user-facing messages in Korean
"""
```

### Step 3: Self-Improving Rule Pattern (Meta-Learning)

```python
# Advanced: Rules that learn from violations
SELF_IMPROVING_TEMPLATE = """
### Violation Tracking
```python
rule_violations = {
    'pattern_1': {
        'frequency': 0,
        'last_violation': None,
        'mitigation': '{specific_fix}'
    }
}

def track_violation(pattern: str, context: str):
    rule_violations[pattern]['frequency'] += 1
    rule_violations[pattern]['last_violation'] = context
    
    if rule_violations[pattern]['frequency'] > 3:
        escalate_rule_enforcement(pattern)
```

### Anti-Pattern Detection
**Common Failures**:
- English user messages (Target: 0 instances)
- Missing validation steps (Target: 100% coverage)
- Verbose explanations (Target: <50 tokens overhead)
```

### Step 4: Domain-Specific Rule Categories

#### Category A: Code Quality Rules
```python
# Optimized for Python/ECS patterns
TEMPLATE_CODE_QUALITY = """
## Rule: {code_rule_name}

### Meta-Principle
Ensure {quality_aspect} without compromising {performance_aspect}

### Constraints
1. MUST: Use Python 3.13+ type hints
2. MUST NOT: Create functions without Korean docstrings
3. IF-THEN: If ECS component → Use @dataclass pattern

### Procedure
1. Validate input types: `isinstance(input, expected_type)`
2. Apply quality check: {specific_validation}
3. Return Korean feedback: "{korean_success_message}"

### Examples
#### Success: Clean ECS Component
**Input**: `@dataclass class HealthComponent: hp: int`
**Output**: "컴포넌트가 올바르게 정의되었습니다"

#### Failure: Missing Type Hints
**Input**: `def calculate_damage(damage):`
**Output**: "타입 힌트가 누락되었습니다"
"""
```

#### Category B: Communication Rules
```python
# Optimized for Korean user interaction
TEMPLATE_COMMUNICATION = """
## Rule: {communication_rule_name}

### Meta-Principle
Provide {information_type} in Korean with {tone_requirement}

### Constraints
1. MUST: Respond in Korean for user-facing messages
2. MUST NOT: Use technical jargon without explanation
3. IF-THEN: If error → Provide specific solution in Korean

### Procedure
1. Detect user context: Korean/English/Technical level
2. Format response: Use Korean for solutions, English for code
3. Validate clarity: Ensure actionable guidance provided

### Examples
#### Success: Clear Error Guidance
**Input**: Test failure
**Output**: "테스트가 실패했습니다. test_entity_creation() 메서드에서 assert 문을 확인하세요."

#### Failure: Vague Response
**Input**: Test failure  
**Output**: "Something went wrong"
"""
```

### Step 5: Performance Optimization Patterns

```python
# Token-efficient rule encoding
OPTIMIZATION_PATTERNS = {
    'reference_compression': '@/.claude/rules/{topic}.md',
    'example_limiting': 'max_2_examples_per_rule',
    'conditional_loading': 'load_rule_only_when_triggered',
    'hierarchical_inheritance': 'inherit_from_parent_rule'
}

# Rule inheritance for token savings
PARENT_RULE_TEMPLATE = """
## Parent Rule: {parent_name}
### Base Constraints
{shared_constraints}

## Child Rule: {child_name}  
### Inherits: @parent_rule
### Additional Constraints
{specific_constraints}
"""
```

### Step 6: Validation Framework

```python
def validate_rule_effectiveness(rule_name: str) -> dict:
    """Rule quality metrics (Korean output for user)"""
    return {
        'compliance_rate': f'{percentage}% 준수율',
        'token_efficiency': f'{tokens} 토큰 사용',
        'korean_coverage': f'{percentage}% 한국어 응답',
        'violation_patterns': [
            '가장 흔한 위반: {pattern}',
            '개선 방안: {solution}'
        ]
    }
```

## Rule Categories for AfterSchoolSurvivors Project

### Game Development Rules
- **ECS Pattern Enforcement**: Component/System/Entity strict typing
- **Performance Constraints**: 40+ FPS maintenance rules
- **Korean UI Standards**: All game text in Korean

### Code Quality Rules  
- **Type Safety**: Python 3.13+ enforcement
- **Test Coverage**: Korean test naming conventions
- **Documentation**: Korean comments for game logic

### Communication Rules
- **Error Messages**: Korean explanations with English code
- **Success Feedback**: Korean confirmation messages
- **Progress Updates**: Korean status with technical details

## Meta-Rule for Rule Creation

```python
# Self-referential rule for creating better rules
def create_optimized_rule(topic: str) -> str:
    """
    Meta-rule: Every rule must be:
    1. Constitutional (hard constraints)
    2. Few-shot (2 examples max)
    3. Validated (measurable success)
    4. Korean-output (user messages)
    5. Token-efficient (<200 tokens)
    """
    
    if not follows_template(topic):
        return "규칙 템플릿을 따르지 않았습니다"
    
    if token_count(topic) > 200:
        return "토큰 사용량이 초과되었습니다. 최적화가 필요합니다"
    
    return f"{topic} 규칙이 성공적으로 생성되었습니다"
```

## Advanced Techniques Applied

1. **Constitutional AI**: Hard constraints prevent rule violations
2. **Few-Shot Learning**: Minimal examples for maximum learning
3. **Meta-Learning**: Rules that improve from violations  
4. **Token Optimization**: Hierarchical inheritance reduces duplication
5. **Korean Output**: User-facing messages always in Korean
6. **Chain-of-Thought**: Structured reasoning in rule execution