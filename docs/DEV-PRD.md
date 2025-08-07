# 방과후생존 게임 - 개발자 중심 PRD (Product Requirements Document)

## 📋 문서 정보
- **문서 타입**: 기술 설계 중심 PRD  
- **작성일**: 2025-08-07
- **아키텍트**: 시니어 게임 아키텍트
- **기반 문서**: [기획 PRD](./PRD.md), [아키텍트 인터뷰](./interview/25-08-07-아키텍쳐_기술_인터뷰.md)

---

# 1. 프로젝트 개요 (Project Overview)

## 1.1 게임 컨셉
**"10분 동안 아무 생각 없이 몰입하여 스트레스를 해소하는"** 하이퍼 캐주얼 로그라이크 생존 게임

### 핵심 플레이 루프
```
플레이어 시작 → 마우스 이동 → 자동 공격 → 적 처치 → 경험치 획득 
→ 레벨업 → 아이템 선택 → 시너지 조합 → 보스 대응 → 성장 → 반복
```

### 기술적 목표
- **플랫폼**: PC (Windows, macOS)
- **개발 언어**: Python 3.13+
- **게임 엔진**: Pygame 2.6.0+
- **성능 목표**: 40+ FPS (60fps/40fps 설정 선택)
- **개발 기간**: MVP 3-4개월

---

# 2. 기술 아키텍처 설계 (Technical Architecture)

## 2.1 전체 시스템 아키텍처

### 아키텍처 패턴 선택
```
ECS (Entity-Component-System) + 추상화 레이어
├── Entity Manager (엔티티 생명주기 관리)
├── Component Registry (컴포넌트 타입 관리)  
├── System Orchestrator (시스템 실행 순서 제어)
└── Interface Abstractions (성능 최적화 교체 준비)
```

### 핵심 설계 원칙
1. **추상화 우선**: 모든 시스템을 인터페이스로 설계
2. **상태와 계산 분리**: 순수 함수 기반 계산 로직
3. **데이터 드리븐**: JSON 기반 외부 데이터 관리
4. **테스트 중심**: pytest 기반 단위/통합 테스트

## 2.2 시스템 컴포넌트 설계

### Core Systems (핵심 시스템)
```python
# 시스템 인터페이스 정의
class ISystem(ABC):
    @abstractmethod
    def update(self, entities: List[Entity], delta_time: float) -> None: pass
    
    @abstractmethod  
    def initialize(self) -> None: pass
    
    @abstractmethod
    def cleanup(self) -> None: pass

# 주요 시스템들
class ICollisionSystem(ISystem): pass    # 충돌감지 (최우선 최적화)
class IRenderSystem(ISystem): pass       # 렌더링 (2순위 최적화)  
class ICameraSystem(ISystem): pass       # 카메라 시스템 (플레이어 추적 및 맵 오프셋)
class IMapSystem(ISystem): pass          # 맵 렌더링 시스템 (카메라 오프셋 적용)
class IAISystem(ISystem): pass           # AI 계산 (3순위 최적화)
class IPhysicsSystem(ISystem): pass      # 물리 시뮬레이션 (4순위)

# 카메라 시스템 구현 예시
class CameraSystem(ICameraSystem):
    def update(self, entities: List[Entity], delta_time: float) -> None:
        # 플레이어의 이동 방향에 따라 카메라 오프셋 업데이트
        for camera_entity in entities.with_component(CameraComponent):
            camera = camera_entity.get_component(CameraComponent)
            if camera.follow_target:
                player_movement = camera.follow_target.get_component(PlayerMovementComponent)
                
                # 플레이어 이동의 역방향으로 카메라 오프셋 적용
                camera.offset -= player_movement.direction * player_movement.speed * delta_time
                
                # 카메라 경계 처리
                camera.offset.x = max(camera.world_bounds[0], 
                                    min(camera.world_bounds[2], camera.offset.x))
                camera.offset.y = max(camera.world_bounds[1], 
                                    min(camera.world_bounds[3], camera.offset.y))
```

### Entity-Component 구조
```python
# 컴포넌트 정의
@dataclass
class HealthComponent:
    current: int
    maximum: int
    regeneration_rate: float

@dataclass  
class MovementComponent:
    velocity: Vector2
    max_speed: float
    acceleration: float

@dataclass
class PlayerMovementComponent:
    # 카메라 시스템과 연동되는 플레이어 전용 이동 컴포넌트
    direction: Vector2
    speed: float
    rotation_angle: float
    angular_velocity_limit: float = 5.0

@dataclass
class CameraComponent:
    # 카메라 오프셋 정보
    offset: Vector2
    world_bounds: tuple[int, int, int, int]  # (min_x, min_y, max_x, max_y)
    follow_target: Optional[Entity] = None

@dataclass
class WeaponComponent:
    damage: int
    attack_speed: float  # 초 단위 (FPS 독립적)
    range: float
    projectile_type: str

# 엔티티 조합 예시
PlayerEntity = Entity([
    HealthComponent(100, 100, 0.0),
    PlayerMovementComponent(Vector2(0,0), 200.0, 0.0, 5.0),
    WeaponComponent(10, 0.5, 100.0, "basic")
])

CameraEntity = Entity([
    CameraComponent(Vector2(0,0), (-1000, -1000, 1000, 1000), player_entity)
])
```

## 2.3 성능 최적화 전략

### 단계별 최적화 계획
| 우선순위 | 시스템 | 초기 구현 | 최적화 구현 | 성능 향상 | 복잡도 증가 |
|---------|--------|-----------|-------------|-----------|-------------|
| 1 | CollisionSystem | O(n²) 브루트포스 | Spatial Partitioning | 🟢 극대 | 🔴 10배 |
| 2 | RenderSystem | 개별 draw() 호출 | Sprite Group 배치 | 🟡 중간 | 🟡 2배 |  
| 3 | AISystem | if-else 체인 | Behavior Tree | 🟢 확장성 | 🔴 6배 |
| 4 | PhysicsSystem | 기본 벡터 연산 | Pymunk 통합 | 🟢 향상 | 🔴 3배 |

### 교체 가능한 인터페이스 설계
```python
# 충돌감지 시스템 추상화 예시
class ICollisionDetector(ABC):
    @abstractmethod
    def check_collisions(self, entities: List[Entity]) -> List[CollisionPair]: pass

class BruteForceCollisionDetector(ICollisionDetector):
    def check_collisions(self, entities):
        # O(n²) 단순 구현 - MVP용
        pass

class SpatialHashCollisionDetector(ICollisionDetector): 
    def check_collisions(self, entities):
        # O(n log n) 최적화 구현 - 확장용  
        pass
```

---

# 3. 게임 시스템 상세 설계 (Detailed Game Systems)

## 3.1 게임 루프 및 타이밍 관리

### FPS 관리 시스템
```python
class GameLoop:
    def __init__(self, target_fps: int = 60):
        self.target_fps = target_fps  # 60 or 40 (설정 선택)
        self.frame_time = 1.0 / target_fps
        self.clock = pygame.time.Clock()
    
    def run(self):
        while self.running:
            # 고정 프레임 방식 (delta time 불필요)
            self.clock.tick(self.target_fps)
            self.update()
            self.render()
```

### 시간 기반 밸런싱
```json
// game_balance.json
{
  "player": {
    "base_attack_speed": 0.5,     // 0.5초마다 공격 (FPS 독립적)
    "movement_speed": 200.0       // 픽셀/초
  },
  "enemies": {
    "spawn_interval": 2.0,        // 2초마다 적 등장
    "difficulty_scaling": {
      "time_based": true,
      "hp_multiplier_per_minute": 1.1
    }
  },
  "bosses": {
    "spawn_interval": 90.0,       // 1분 30초마다 보스 등장
    "pattern_duration": {
      "alpha_stun": 1.0,          // 1초 스턴
      "beta_attack_warning": 2.0  // 2초 예고시간  
    }
  }
}
```

## 3.2 플레이어 시스템

### 플레이어 컴포넌트
```python
@dataclass
class PlayerComponent:
    # 기본 능력치
    health: HealthComponent
    movement: MovementComponent  
    inventory: ItemInventoryComponent  # 6슬롯 제한
    
    # 게임 진행 상태
    experience: int = 0
    level: int = 1
    
    # 현재 디버프 상태
    active_debuffs: List[DebuffEffect] = field(default_factory=list)

@dataclass
class PlayerMovementComponent:
    # 이동 방향과 속도 (카메라 시스템과 연동)
    direction: Vector2
    speed: float
    rotation_angle: float  # 플레이어가 바라보는 방향 (라디안)
    angular_velocity_limit: float = 5.0  # 부드러운 회전을 위한 각속도 제한

class PlayerMovementSystem(ISystem):
    def update(self, entities, delta_time):
        for entity in entities.with_component(PlayerComponent):
            # 마우스 위치 추적 및 회전 방향 계산
            mouse_pos = pygame.mouse.get_pos()
            screen_center = (pygame.display.get_surface().get_width() // 2, 
                           pygame.display.get_surface().get_height() // 2)
            
            # 플레이어는 화면 중앙에 고정, 마우스 방향을 바라봄
            direction = normalize(Vector2(mouse_pos) - Vector2(screen_center))
            target_angle = math.atan2(direction.y, direction.x)
            
            movement = entity.get_component(PlayerMovementComponent)
            
            # 부드러운 회전 전환
            angle_diff = target_angle - movement.rotation_angle
            if angle_diff > math.pi:
                angle_diff -= 2 * math.pi
            elif angle_diff < -math.pi:
                angle_diff += 2 * math.pi
            
            rotation_speed = min(movement.angular_velocity_limit * delta_time, abs(angle_diff))
            movement.rotation_angle += rotation_speed * (1 if angle_diff > 0 else -1)
            
            # 이동 방향과 속도 저장 (카메라 시스템에서 사용)
            movement.direction = direction
            movement.speed = movement.max_speed if direction.length() > 0 else 0
```

### 자동 공격 시스템
```python
class AutoAttackSystem(ISystem):
    def update(self, entities, delta_time):
        for entity in entities.with_component(PlayerComponent):
            weapon = entity.get_component(WeaponComponent)
            
            # 시간 기반 공격 쿨다운 (FPS 독립적)
            weapon.last_attack_time += delta_time
            if weapon.last_attack_time >= weapon.attack_speed:
                self._perform_attack(entity)
                weapon.last_attack_time = 0.0
    
    def _perform_attack(self, player_entity):
        # 가장 가까운 적을 향해 투사체 발사
        target = self._find_nearest_enemy(player_entity)
        if target:
            self._create_projectile(player_entity, target)
```

## 3.3 아이템 및 시너지 시스템

### 룰 엔진 기반 아이템 시스템
```json
// items.json
{
  "items": [
    {
      "id": "soccer_ball",
      "name": "축구공",
      "type": "weapon",
      "base_effects": {
        "damage": 15,
        "attack_speed": 0.8,
        "projectile_bounces": 1
      },
      "level_scaling": {
        "damage": 3,
        "projectile_bounces": 1
      }
    }
  ],
  "synergies": [
    {
      "id": "soccer_combo",
      "conditions": ["soccer_ball", "soccer_shoes"], 
      "effects": {
        "damage_multiplier": 1.15
      },
      "description": "축구화 + 축구공 시너지"
    }
  ]
}
```

### 아이템 효과 계산 시스템
```python
class ItemEffectCalculator:
    """순수 함수 기반 아이템 효과 계산 (테스트 용이)"""
    
    @staticmethod
    def calculate_total_effects(items: List[Item], synergies: List[Synergy]) -> ItemEffects:
        base_effects = ItemEffectCalculator._sum_base_effects(items)
        synergy_effects = ItemEffectCalculator._calculate_synergy_effects(items, synergies)
        
        # 가산 방식 적용 (디버프와의 일관성)
        return ItemEffectCalculator._combine_effects_additive(base_effects, synergy_effects)
    
    @staticmethod
    def apply_debuff_effects(base_effects: ItemEffects, debuffs: List[DebuffEffect]) -> ItemEffects:
        # 가산 방식: 기본 효과 × (1 + 시너지 보너스 - 디버프 페널티)
        total_multiplier = 1.0
        for debuff in debuffs:
            total_multiplier -= debuff.penalty_ratio
        
        return base_effects * max(0.1, total_multiplier)  # 최소 10% 보장

# 단위 테스트 예시
def test_soccer_synergy():
    items = [Item("soccer_ball"), Item("soccer_shoes")]  
    synergies = [SynergyRule("soccer_combo", ["soccer_ball", "soccer_shoes"], 0.15)]
    
    effects = ItemEffectCalculator.calculate_total_effects(items, synergies)
    assert effects.damage_multiplier == 1.15
```

### 아이템 선택 UI 시스템
```python
class ItemSelectionSystem:
    def show_levelup_options(self, player_level: int) -> Tuple[Item, Item]:
        # 레벨업 시 2개 아이템 무작위 제시
        available_items = self._get_available_items(player_level)
        return random.sample(available_items, 2)
    
    def apply_item_choice(self, player: Entity, chosen_item: Item):
        inventory = player.get_component(ItemInventoryComponent)
        
        if chosen_item.id in inventory.items:
            # 기존 아이템 강화
            inventory.items[chosen_item.id].level += 1
        else:
            # 새 아이템 획득 (6슬롯 제한 확인)
            if len(inventory.items) < 6:
                inventory.items[chosen_item.id] = chosen_item
            else:
                # 슬롯 가득참 - 교체 선택 UI 표시
                self._show_replacement_ui(player, chosen_item)
        
        # 효과 재계산 (캐싱 방식)
        self._recalculate_player_effects(player)
```

## 3.4 적 및 AI 시스템

### 적 타입별 컴포넌트 설계
```python
@dataclass
class EnemyAIComponent:
    ai_type: str  # "basic", "boss", "special"
    state_machine: Optional[StateMachine] = None
    target_entity: Optional[Entity] = None
    
@dataclass  
class BasicEnemyAI(EnemyAIComponent):
    chase_range: float = 200.0
    attack_range: float = 50.0
    movement_speed: float = 100.0

class EnemyAISystem(ISystem):
    def update(self, entities, delta_time):
        for entity in entities.with_component(EnemyAIComponent):
            ai = entity.get_component(EnemyAIComponent)
            
            if ai.ai_type == "basic":
                self._update_basic_ai(entity, delta_time)
            elif ai.ai_type == "boss": 
                self._update_boss_ai(entity, delta_time)
    
    def _update_basic_ai(self, enemy: Entity, delta_time: float):
        # 단순 상태 기반 AI
        player = self._find_player()
        distance = self._calculate_distance(enemy, player)
        
        if distance <= enemy.ai.attack_range:
            self._attack_player(enemy)
        elif distance <= enemy.ai.chase_range:
            self._move_towards_player(enemy, player)
        else:
            self._patrol_behavior(enemy)
```

## 3.5 보스 및 디버프 시스템

### 보스 패턴 시스템
```json  
// bosses.json
{
  "principal_boss": {
    "id": "principal",
    "name": "교장선생님", 
    "spawn_interval": 90.0,
    "patterns": [
      {
        "sequence_id": "basic_pattern",
        "difficulty_weight": 1.0,
        "actions": [
          {
            "type": "speech_alpha",
            "duration": 1.0,
            "effects": ["stun_player", "apply_random_debuff"]
          },
          {
            "type": "speech_beta", 
            "warning_time": 2.0,
            "damage_area": "random_circle",
            "area_size": "medium"
          }
        ]
      },
      {
        "sequence_id": "hard_pattern",
        "difficulty_weight": 2.0,
        "actions": [
          {
            "type": "speech_alpha",
            "duration": 1.0,
            "effects": ["stun_player", "apply_hard_debuff"]
          },
          {
            "type": "special_attack",
            "warning_time": 1.5,
            "damage_area": "large_circle"  
          },
          {
            "type": "speech_beta",
            "warning_time": 1.0,
            "damage_area": "small_circle",
            "repeat_count": 3
          }
        ]
      }
    ]
  }
}
```

### 디버프 및 미션 시스템
```python
@dataclass
class DebuffEffect:
    debuff_type: str  # "speed_down", "attack_down", "damage_up_taken"
    penalty_ratio: float  # 0.3 = 30% 감소
    duration: float  # 초 단위
    mission_condition: Optional[MissionCondition] = None

@dataclass
class MissionCondition:
    mission_type: str  # "run_distance", "survive_time", "avoid_attacks"
    target_value: float
    current_progress: float = 0.0

class DebuffSystem(ISystem):
    def apply_boss_debuff(self, player: Entity, boss_pattern: BossPattern):
        # 보스 패턴에 따른 디버프 적용
        debuff = self._select_counter_debuff(player)
        player.get_component(PlayerComponent).active_debuffs.append(debuff)
        
        # 미션 조건 생성
        mission = self._create_counter_mission(debuff)
        self.ui_system.show_mission_popup(mission)
    
    def _select_counter_debuff(self, player: Entity) -> DebuffEffect:
        # 플레이어의 강력한 아이템 조합을 카운터하는 디버프 선택
        dominant_weapon = self._analyze_player_build(player)
        
        if dominant_weapon == "projectile_heavy":
            return DebuffEffect("attack_speed_down", 0.5, 30.0, 
                              MissionCondition("avoid_attacks", 10))
        elif dominant_weapon == "melee_heavy": 
            return DebuffEffect("movement_speed_down", 0.4, 25.0,
                              MissionCondition("run_distance", 500.0))
        else:
            return DebuffEffect("damage_taken_up", 0.3, 20.0, 
                              MissionCondition("survive_time", 15.0))
```

---

# 4. 데이터 관리 및 설정 시스템 (Data Management)

## 4.1 외부 데이터 파일 구조

### 데이터 파일 아키텍처
```
data/
├── items.json          # 아이템 정보 + 시너지 규칙
├── enemies.json        # 적 AI 패턴 + 능력치  
├── bosses.json         # 보스 패턴 + 디버프 규칙
├── game_balance.json   # 시간 기반 밸런싱 값들
└── game_settings.json  # 사용자 설정값
```

### 데이터 로딩 시스템
```python
class DataManager:
    """게임 시작 시 모든 데이터 로딩 (핫 리로딩 없음)"""
    
    def __init__(self):
        self.items_data: Dict = {}
        self.enemies_data: Dict = {}
        self.bosses_data: Dict = {}
        self.balance_data: Dict = {}
        
    def load_all_data(self):
        """게임 시작 시 한 번만 실행"""
        self.items_data = self._load_json("data/items.json")
        self.enemies_data = self._load_json("data/enemies.json") 
        self.bosses_data = self._load_json("data/bosses.json")
        self.balance_data = self._load_json("data/game_balance.json")
        
        # 데이터 유효성 검증
        self._validate_data_integrity()
    
    def _validate_data_integrity(self):
        """데이터 무결성 검증"""
        # 시너지 조건의 아이템 ID가 실제 존재하는지 확인
        for synergy in self.items_data["synergies"]:
            for item_id in synergy["conditions"]:
                if not self._item_exists(item_id):
                    raise DataIntegrityError(f"시너지 {synergy['id']}에서 존재하지 않는 아이템 {item_id} 참조")
```

## 4.2 설정 관리 시스템

### 사용자 설정
```json
// game_settings.json
{
  "display": {
    "target_fps": 60,        // 60 or 40
    "resolution": [1280, 720],
    "fullscreen": false
  },
  "audio": {
    "master_volume": 0.8,
    "sfx_volume": 0.7,
    "music_volume": 0.5
  },
  "gameplay": {
    "auto_pause_on_levelup": true,
    "show_damage_numbers": true,
    "camera_shake": true
  }
}
```

### 설정 적용 시스템
```python
class SettingsManager:
    def __init__(self):
        self.current_settings = self._load_default_settings()
        self.observers: List[ISettingsObserver] = []
    
    def change_fps_setting(self, new_fps: int):
        if new_fps not in [40, 60]:
            raise ValueError("FPS는 40 또는 60만 지원됩니다")
            
        self.current_settings["display"]["target_fps"] = new_fps
        self._notify_observers("fps_changed", new_fps)
        self._save_settings()
    
    def register_observer(self, observer: ISettingsObserver):
        """설정 변경 시 알림받을 시스템 등록"""
        self.observers.append(observer)
```

---

# 5. 테스트 전략 및 품질 보장 (Testing Strategy)

## 5.1 pytest 기반 테스트 아키텍처

### 테스트 구조 및 분류
```
tests/
├── unit/                 # 단위 테스트
│   ├── test_items.py     # pytest -m items
│   ├── test_collision.py # pytest -m collision  
│   ├── test_ai.py        # pytest -m ai
│   └── test_balance.py   # pytest -m balance
├── integration/          # 통합 테스트
│   ├── test_gameplay.py  # 전체 게임플레이 플로우
│   └── test_systems.py   # 시스템 간 상호작용
└── performance/          # 성능 테스트
    ├── test_fps.py       # FPS 성능 벤치마크
    └── test_memory.py    # 메모리 사용량 테스트
```

### 단위 테스트 예시
```python
# tests/unit/test_items.py
import pytest
from src.systems.item_system import ItemEffectCalculator
from src.data.items import Item, SynergyRule

@pytest.mark.items
class TestItemSynergies:
    
    def test_soccer_synergy_calculation(self):
        """축구화 + 축구공 시너지 테스트"""
        # Given
        items = [
            Item("soccer_ball", {"damage": 15}),
            Item("soccer_shoes", {"movement_speed": 1.1})
        ]
        synergies = [
            SynergyRule("soccer_combo", ["soccer_ball", "soccer_shoes"], {"damage_multiplier": 1.15})
        ]
        
        # When  
        effects = ItemEffectCalculator.calculate_total_effects(items, synergies)
        
        # Then
        assert effects.damage == 15 * 1.15  # 시너지 적용
        assert effects.movement_speed == 1.1
    
    @pytest.mark.parametrize("debuff_penalty,expected_damage", [
        (0.3, 15 * 1.15 * 0.7),  # 30% 디버프
        (0.5, 15 * 1.15 * 0.5),  # 50% 디버프
        (0.8, 15 * 1.15 * 0.2),  # 80% 디버프 (최소 20%)
    ])
    def test_debuff_interaction_with_synergy(self, debuff_penalty, expected_damage):
        """디버프와 시너지 상호작용 테스트"""
        # Given
        base_effects = ItemEffects(damage=15 * 1.15)  # 시너지 적용된 상태
        debuffs = [DebuffEffect("damage_down", debuff_penalty, 10.0)]
        
        # When
        final_effects = ItemEffectCalculator.apply_debuff_effects(base_effects, debuffs)
        
        # Then
        assert abs(final_effects.damage - expected_damage) < 0.01

# tests/unit/test_collision.py
@pytest.mark.collision
class TestCollisionSystems:
    
    def test_brute_force_collision_accuracy(self):
        """브루트포스 충돌감지 정확성 테스트"""
        detector = BruteForceCollisionDetector()
        entities = self._create_test_entities([(0,0), (5,5), (100,100)])
        
        collisions = detector.check_collisions(entities)
        
        assert len(collisions) == 1  # (0,0)과 (5,5)만 충돌
        assert collisions[0].entity_a.position == Vector2(0,0)
        assert collisions[0].entity_b.position == Vector2(5,5)
    
    def test_collision_system_interface_compatibility(self):
        """충돌감지 시스템 인터페이스 호환성 테스트"""
        systems = [
            BruteForceCollisionDetector(),
            SpatialHashCollisionDetector()  # 최적화 버전
        ]
        test_entities = self._create_test_entities([(0,0), (5,5)])
        
        # 두 구현체가 동일한 결과를 반환하는지 확인
        results = [system.check_collisions(test_entities) for system in systems]
        assert all(len(result) == 1 for result in results)  # 모두 1개 충돌 감지
```

### 통합 테스트
```python
# tests/integration/test_gameplay.py
@pytest.mark.integration
class TestGameplayFlow:
    
    def test_complete_levelup_flow(self):
        """레벨업 → 아이템 선택 → 시너지 적용 전체 플로우 테스트"""
        # Given
        game = TestGameInstance()
        player = game.create_player()
        
        # When: 경험치를 충분히 획득하여 레벨업
        game.add_experience(player, 100)
        
        # Then: 레벨업 이벤트 발생 확인
        assert player.level == 2
        assert game.ui.is_item_selection_visible()
        
        # When: 아이템 선택
        available_items = game.ui.get_available_items()
        game.ui.select_item(available_items[0])
        
        # Then: 아이템 효과 적용 확인
        assert len(player.inventory.items) == 1
        assert player.combat_stats.damage > 0  # 기본값보다 증가
    
    def test_boss_fight_scenario(self):
        """보스전 시나리오 테스트"""
        game = TestGameInstance()
        player = game.create_player()
        
        # 1분 30초 경과 시뮬레이션
        game.advance_time(90.0)
        
        # 보스 등장 확인
        boss = game.find_entity_by_type("boss")
        assert boss is not None
        assert boss.get_component(EnemyAIComponent).ai_type == "boss"
        
        # 디버프 적용 확인  
        game.simulate_boss_attack(boss, player)
        assert len(player.active_debuffs) > 0
        
        # 미션 시스템 활성화 확인
        assert game.mission_system.has_active_mission()
```

### 성능 테스트
```python
# tests/performance/test_fps.py
@pytest.mark.performance
class TestPerformanceBenchmarks:
    
    def test_collision_system_performance(self):
        """충돌감지 시스템 성능 벤치마크"""
        entities_counts = [50, 100, 200, 500]
        
        for count in entities_counts:
            entities = self._create_random_entities(count)
            
            # 브루트포스 방식 측정
            start_time = time.time()
            brute_detector = BruteForceCollisionDetector()  
            brute_detector.check_collisions(entities)
            brute_time = time.time() - start_time
            
            # 최적화 방식이 구현된 경우 비교
            if count <= 100:  # 소규모에서는 브루트포스도 허용
                assert brute_time < 0.016  # 60 FPS 기준 (16ms)
            else:  # 대규모에서는 최적화 필요
                pytest.skip("최적화된 충돌감지 시스템 구현 필요")
```

## 5.2 테스트 실행 환경

### pytest 설정
```ini
# pytest.ini
[tool:pytest]
markers =
    items: 아이템 시스템 테스트
    collision: 충돌감지 시스템 테스트  
    ai: AI 시스템 테스트
    balance: 게임 밸런스 테스트
    integration: 통합 테스트
    performance: 성능 테스트
    slow: 실행 시간이 긴 테스트

testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*

# 테스트 실행 예시
# pytest -m items                    # 아이템 시스템만 테스트
# pytest -m "not slow"               # 빠른 테스트만 실행
# pytest tests/unit/                 # 단위 테스트만 실행
# pytest -v --tb=short              # 자세한 출력 + 간단한 traceback
```

---

# 6. 개발 로드맵 및 우선순위 (Development Roadmap)

## 6.1 MVP 개발 단계

### Phase 1: 핵심 인프라 구축 (2-3주)
**목표**: ECS 프레임워크 + 테스트 환경 + 기본 게임 루프

**🔧 개발 항목**:
- [ ] ECS 프레임워크 구현 (인터페이스 우선)
- [ ] 게임 루프 시스템 (60fps/40fps 선택)
- [ ] 기본 렌더링 시스템 (단순 구현)
- [ ] 충돌감지 시스템 (브루트포스 + 인터페이스)
- [ ] pytest 테스트 환경 구축
- [ ] 데이터 로딩 시스템 (JSON 기반)

**✅ 완료 조건**:
- 빈 게임 월드에서 40+ FPS 달성
- 모든 시스템 인터페이스 정의 완료  
- 기본 단위 테스트 프레임워크 동작

### Phase 2: 기본 게임플레이 구현 (3-4주)  
**목표**: 플레이어 조작 + 적 AI + 경험치 시스템

**🎮 개발 항목**:
- [ ] 플레이어 마우스 이동 시스템 (카메라 중심 고정 + 맵 역방향 이동)
- [ ] 카메라 시스템 (플레이어 중앙 고정, 맵 오프셋 렌더링)
- [ ] 시각적 맵 시스템 (타일/그리드 배경, 경계 처리)
- [ ] 자동 공격 시스템 (시간 기반)
- [ ] 기본 적 1종 + 간단 AI (추격 + 공격)
- [ ] 투사체 시스템 
- [ ] 경험치/레벨업 시스템
- [ ] 기본 UI (체력, 경험치 바)

**✅ 완료 조건**:
- 플레이어가 마우스 방향을 바라보며 화면 중앙에 고정
- 맵이 플레이어 이동의 역방향으로 자연스럽게 움직임
- 카메라 경계 처리로 맵 밖으로 나가지 않음
- 적을 자동으로 공격하여 처치 가능
- 경험치 획득으로 레벨업 가능
- 적 20마리 동시 존재 시 40+ FPS 유지

### Phase 3: 아이템 시스템 구현 (2-3주)
**목표**: JSON 기반 아이템 + 룰 엔진 + 시너지

**⚡ 개발 항목**:
- [ ] JSON 기반 아이템 데이터 구조
- [ ] 룰 엔진 기반 시너지 계산
- [ ] 아이템 선택 UI (레벨업 시)
- [ ] 아이템 인벤토리 시스템 (6슬롯)
- [ ] 가산 방식 효과 계산 시스템
- [ ] 아이템 시스템 단위 테스트

**✅ 완료 조건**:
- 7개 기본 아이템 구현
- 축구화+축구공 등 기본 시너지 동작
- 아이템 효과가 실시간 플레이에 반영
- 시너지 계산 로직 100% 테스트 커버리지

### Phase 4: 보스 시스템 구현 (3-4주)
**목표**: 교장선생님 보스 + 디버프 시스템

**👑 개발 항목**:
- [ ] 보스 등장 시스템 (1분 30초 주기)
- [ ] 교장선생님 AI 패턴 (훈화 말씀 알파/베타)
- [ ] 디버프 적용 시스템
- [ ] 미션 조건 시스템 
- [ ] 보스 공격 시각적 예고 시스템
- [ ] 보스전 통합 테스트

**✅ 완료 조건**:
- 1분 30초마다 보스가 등장
- 보스 패턴이 예측 가능하게 동작
- 디버프와 미션이 올바르게 연동
- 보스 + 적 50마리 동시 존재 시 40+ FPS 유지

## 6.2 확장 단계 (MVP 이후)

### Phase 5: 성능 최적화 (2-3주)
- 충돌감지 시스템 → Spatial Partitioning 교체
- 렌더링 시스템 → Sprite Group 최적화
- 메모리 풀링 패턴 적용
- 성능 프로파일링 및 병목 지점 해결

### Phase 6: 콘텐츠 확장 (4-6주)
- 추가 적 타입 (수학선생님, 국어선생님)
- 아이템 확장 (20+ 종류)
- 추가 시너지 조합
- 새로운 보스 패턴

### Phase 7: 품질 향상 (2-3주)
- 사운드 이펙트 + 배경음악
- 시각 효과 개선 (파티클, 화면 흔들림)
- 게임 설정 메뉴
- 최종 밸런스 조정

---

# 7. 기술적 제약사항 및 위험 요소 (Technical Constraints & Risks)

## 7.1 기술적 제약사항

### Python + Pygame 성능 한계
| 제약사항 | 영향도 | 대응 방안 |
|----------|--------|-----------|
| GIL(Global Interpreter Lock) | 🔴 높음 | 게임 로직을 단일 스레드로 설계 |
| Pygame 렌더링 성능 | 🟡 중간 | Sprite Group + 더티 렌더링 활용 |
| 메모리 관리 자동화 | 🟡 중간 | Object Pooling 패턴으로 GC 압박 감소 |
| 실행 파일 크기 | 🟢 낮음 | PyInstaller 최적화 옵션 활용 |

### 개발팀 역량 제약
- **초보 개발자 고려**: 복잡한 최적화 기법은 인터페이스로 추상화
- **1인 개발**: 과도한 확장성보다는 단순하고 안정적인 구조 우선
- **시간 제약**: MVP 범위를 엄격히 제한하여 핵심 재미에 집중

## 7.2 위험 요소 및 완화 방안

### 성능 위험 요소
```python
# 위험: 객체 수 급증으로 인한 프레임 드롭
class ObjectLimitManager:
    MAX_ENEMIES = 50        # 동시 적 최대 수
    MAX_PROJECTILES = 100   # 동시 투사체 최대 수
    
    def spawn_enemy(self):
        if len(self.enemies) >= self.MAX_ENEMIES:
            # 가장 오래된 적 제거
            self._remove_oldest_enemy()
        self._create_new_enemy()
```

### 밸런싱 위험 요소
```json
// 위험: 아이템 조합이 지나치게 강력해짐
{
  "synergy_limits": {
    "max_damage_multiplier": 3.0,    // 최대 300% 데미지
    "max_attack_speed_bonus": 2.0,   // 최대 200% 공격속도
    "max_movement_speed_bonus": 1.5  // 최대 150% 이동속도
  },
  "difficulty_scaling": {
    "compensation_enabled": true,     // 강력한 조합일수록 더 어려운 적 등장
    "dynamic_enemy_stats": true
  }
}
```

### 개발 일정 위험 요소
**완화 방안**:
1. **매주 플레이 가능한 빌드 생성**: 진행도 가시화
2. **기능별 우선순위 명확화**: 핵심 재미 → 시각적 품질 → 추가 기능  
3. **테스트 자동화**: 회귀 버그 조기 발견으로 디버깅 시간 단축

---

# 8. 성공 지표 및 검증 방법 (Success Metrics)

## 8.1 기술적 성공 지표

### 성능 지표
- **FPS 안정성**: 적 50마리 + 투사체 100개 상황에서 40+ FPS 유지율 95% 이상
- **메모리 사용량**: 게임 실행 30분 후 메모리 증가량 50MB 이하
- **로딩 시간**: 게임 시작부터 플레이 가능까지 3초 이내

### 품질 지표  
- **테스트 커버리지**: 핵심 게임 로직 90% 이상
- **버그 밀도**: 플레이 10분당 크래시 0건, 심각한 버그 1건 이하
- **크로스 플랫폼**: Windows, macOS에서 동일한 게임플레이 경험

## 8.2 게임플레이 검증 방법

### 핵심 재미 요소 검증
```python
# 자동화된 게임플레이 시뮬레이션
class GameplayValidator:
    def test_10_minute_session(self):
        """10분 플레이 세션 시뮬레이션"""
        game = AutoPlayGame()
        
        # 10분 자동 플레이
        game.run_simulation(600.0)  # 600초
        
        # 핵심 지표 검증
        assert game.player.level >= 5         # 최소 성장
        assert len(game.defeated_bosses) >= 6 # 보스 6회 이상 처치
        assert game.player.max_combo >= 10    # 연속 처치 쾌감
        assert game.fps_drops < 5             # 프레임 드롭 최소화
```

### 사용자 경험 검증
1. **학습 곡선**: 신규 플레이어가 조작법을 익히는데 걸리는 시간 ≤ 30초
2. **재시도 의욕**: 게임 오버 후 즉시 재시작율 ≥ 80%  
3. **몰입도**: 플레이어가 10분 세션을 중간에 그만두지 않는 비율 ≥ 90%

---

# 9. 부록 (Appendix)

## 9.1 참고 문서
- [기획 PRD](./PRD.md) - 게임 컨셉 및 기획 요구사항
- [게임 의존성](./game-dependency.md) - Python 라이브러리 스택  
- [아키텍트 인터뷰](./interview/25-08-07-아키텍쳐_기술_인터뷰.md) - 설계 결정 과정

## 9.2 개발 환경 설정

### 필수 요구사항
```bash
# Python 환경
Python 3.13+
pygame >= 2.6.0
numpy >= 2.2.4
pytest >= 8.0.0

# 개발 도구
ruff >= 0.6.0          # 린팅 + 포맷팅
memory-profiler        # 성능 분석
```

### 프로젝트 구조
```
AfterSchoolSurvivors/
├── src/
│   ├── core/          # ECS 프레임워크
│   ├── systems/       # 게임 시스템들
│   ├── components/    # ECS 컴포넌트들
│   ├── data/          # 데이터 관리
│   └── ui/            # 사용자 인터페이스
├── data/              # JSON 데이터 파일들
├── tests/             # 테스트 코드
├── assets/            # 이미지, 사운드 리소스
└── docs/              # 문서화
```

## 9.3 코딩 컨벤션

### 핵심 원칙
1. **타입 힌트 필수**: 모든 함수와 메서드에 타입 힌트 적용
2. **순수 함수 우선**: 상태 변경과 계산 로직 분리
3. **인터페이스 기반 설계**: ABC 클래스로 계약 정의
4. **테스트 가능한 코드**: 의존성 주입으로 테스트 용이성 확보

### 명명 규칙
```python
# 클래스: PascalCase
class PlayerMovementSystem: pass

# 함수/변수: snake_case  
def calculate_damage_with_synergy(): pass
max_health = 100

# 상수: UPPER_SNAKE_CASE
MAX_ENEMIES_COUNT = 50

# 인터페이스: I 접두사
class ICollisionDetector(ABC): pass

# 컴포넌트: Component 접미사
class HealthComponent: pass
```

---

**문서 버전**: 1.0  
**최종 수정일**: 2025-08-07  
**다음 검토일**: MVP Phase 1 완료 시점