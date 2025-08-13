# Rule: Repository Pattern Implementation

## Meta-Principle
외부 종속성(파일 시스템, 데이터베이스, 네트워크 등)을 추상화 인터페이스로 분리하여 테스트 가능하고 유지보수가 용이한 코드를 작성한다.

## Constitutional Constraints
1. MUST: 외부 종속성은 반드시 ABC 인터페이스로 추상화
2. MUST NOT: 비즈니스 로직에서 직접적인 파일/DB/네트워크 호출 금지
3. IF-THEN: 외부 종속성 발견 시 → Repository 패턴 적용 필수

## Execution Procedure
```python
def implement_repository_pattern():
    # Step 1: 외부 종속성 식별
    if has_external_dependency():
        return "외부 종속성을 Repository로 분리해야 합니다"
    
    # Step 2: 인터페이스 정의
    create_abc_interface()
    
    # Step 3: 구현체 분리
    assert interface_implemented(), "인터페이스 구현이 완료되지 않았습니다"
```

## Few-Shot Examples

### Example 1: Success Case (File System Repository)
**Input**: DataLoader가 직접 파일 시스템에 접근
```python
# 잘못된 구현
class DataLoader:
    def load_json(self, filename):
        with open(self.data_path / filename) as f:  # 직접 파일 접근
            return json.load(f)
```

**Output**: Repository 패턴 적용
```python
# 올바른 구현
class IFileRepository(ABC):
    @abstractmethod
    def read_json(self, file_path: Path) -> dict[str, Any]: pass

class DataLoader:
    def __init__(self, file_repository: IFileRepository):
        self._file_repository = file_repository
    
    def load_json(self, filename):
        return self._file_repository.read_json(self.data_path / filename)
```

**Reasoning**: 파일 시스템을 추상화하여 테스트 시 Mock Repository 주입 가능

### Example 2: Failure Prevention (Database Access)
**Input**: Entity Manager가 직접 데이터베이스 접근
```python
# 잘못된 구현
class EntityManager:
    def save_entity(self, entity):
        cursor.execute("INSERT INTO entities...", entity.data)  # 직접 DB 접근
```

**Output**: "데이터베이스 접근을 Repository로 분리해야 합니다"

**Reasoning**: 직접 DB 접근은 테스트 어려움과 결합도 증가 초래

## Implementation Guidelines

### 1. Repository Interface 정의 패턴
```python
class I{Domain}Repository(ABC):
    """
    {Domain} 데이터 접근을 위한 추상 인터페이스.
    
    외부 종속성을 격리하여 테스트 가능성과 유지보수성을 향상시킵니다.
    """
    
    @abstractmethod
    def {action}(self, {params}) -> {return_type}:
        """
        {Action description in Korean}.
        
        Args:
            {params}: 매개변수 설명
            
        Returns:
            반환값 설명
            
        Raises:
            구체적인 예외 상황 명시
        """
        pass
```

### 2. 구현체 패턴
```python
class {ConcreteImplementation}Repository(I{Domain}Repository):
    """
    {Domain} Repository의 {Storage Type} 구현체.
    
    실제 {external dependency} 접근을 담당합니다.
    """
    
    def {action}(self, {params}) -> {return_type}:
        # 타입 검증
        if not isinstance({param}, {expected_type}):
            raise TypeError(f"Expected {expected_type}, got {type({param})}")
        
        try:
            # 실제 외부 종속성 호출
            return {external_call}
        except {SpecificException} as e:
            raise {SpecificException}(f"Korean error message: {e}") from e
```

### 3. 의존성 주입 패턴
```python
class {BusinessLogicClass}:
    def __init__(self, {repository_name}: I{Domain}Repository | None = None):
        self._{repository_name} = {repository_name} or {DefaultRepository}()
    
    def {business_method}(self):
        # Repository를 통한 데이터 접근
        data = self._{repository_name}.{repository_method}()
        # 비즈니스 로직 처리
        return processed_data
```

## Common Repository Types

### FileRepository (파일 시스템)
```python
class IFileRepository(ABC):
    @abstractmethod
    def exists(self, path: Path) -> bool: pass
    
    @abstractmethod
    def read_text(self, path: Path) -> str: pass
    
    @abstractmethod
    def write_text(self, path: Path, content: str) -> None: pass
```

### ConfigRepository (설정 관리)
```python
class IConfigRepository(ABC):
    @abstractmethod
    def load_config(self, key: str) -> Any: pass
    
    @abstractmethod
    def save_config(self, key: str, value: Any) -> None: pass
```

### AssetRepository (게임 리소스)
```python
class IAssetRepository(ABC):
    @abstractmethod
    def load_texture(self, name: str) -> Texture: pass
    
    @abstractmethod
    def load_sound(self, name: str) -> Sound: pass
```

## Testing Support

### Mock Repository 패턴
```python
class Mock{Domain}Repository(I{Domain}Repository):
    def __init__(self):
        self.{method}_calls = []
        self.{method}_return_value = {default_value}
    
    def {method}(self, {params}):
        self.{method}_calls.append({params})
        return self.{method}_return_value
```

### Test Fixture 패턴
```python
@pytest.fixture
def mock_{repository_name}():
    return Mock{Domain}Repository()

@pytest.fixture  
def {business_class}(mock_{repository_name}):
    return {BusinessClass}(mock_{repository_name})
```

## Validation Metrics
- **Abstraction Rate**: 100% 외부 종속성이 인터페이스로 추상화
- **Test Coverage**: Repository 주입으로 100% 단위 테스트 가능
- **Korean Messages**: 모든 에러 메시지는 한국어로 제공

## Anti-Patterns to Avoid

### ❌ 직접 외부 접근
```python
# 금지: 비즈니스 로직에서 직접 파일 접근
def process_data():
    with open("data.json") as f:  # 직접 접근 금지
        data = json.load(f)
```

### ❌ 구체 클래스 의존
```python
# 금지: 구체 클래스에 직접 의존
def __init__(self):
    self.repo = FileSystemRepository()  # 구체 클래스 의존 금지
```

### ❌ Repository 없는 외부 호출
```python
# 금지: Repository 없이 네트워크 호출
def fetch_data():
    response = requests.get("http://api.example.com")  # 직접 호출 금지
```

## Korean Output Validation
- 모든 에러 메시지: "~을/를 Repository로 분리해야 합니다"
- 성공 메시지: "Repository 패턴이 올바르게 적용되었습니다"
- 가이드 메시지: "의존성 주입을 통해 테스트 가능성이 향상되었습니다"