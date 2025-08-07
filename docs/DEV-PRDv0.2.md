# 방과후생존 게임 - 개발자 중심 PRD v0.2 (Product Requirements Document)

## 📋 문서 정보

- **문서 타입**: 기술 설계 중심 PRD v0.2
- **작성일**: 2025-08-07
- **아키텍트**: 시니어 게임 아키텍트
- **기반 문서**: [기획 PRD](./PRD.md), [아키텍트 인터뷰](./interview/25-08-07-아키텍쳐_기술_인터뷰.md)
- **주요 변경사항**: 플레이어 중앙 고정 카메라 시스템 아키텍처 전면 적용
- **변경 근거**: [플레이어 이동 아키텍처 변경 인터뷰](./interview/25-08-07-플레이어_이동_아키텍처_변경_인터뷰.md)

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

- **플랫폼**: PC (Windows, macOS) → **모바일 확장 고려**
- **개발 언어**: Python 3.13+
- **게임 엔진**: Pygame 2.6.0+
- **성능 목표**: 40+ FPS (60fps/40fps 설정 선택)
- **개발 기간**: MVP 3-4개월 → **Phase 2 +2주 추가**

### 🆕 핵심 플레이 경험 설계 원칙

1. **크로스 플랫폼 일관성**: PC와 모바일에서 동일한 "시원한" 플레이 경험
2. **플레이어 중앙 고정**: 화면 중앙에서 안정감 있는 조작감
3. **무한 확장감**: 맵의 제약 없는 자유로운 탐험 느낌

---

# 2. 🆕 카메라 중심 아키텍처 설계 (Camera-Centric Architecture)

## 2.1 전체 시스템 아키텍처

### 아키텍처 패턴 선택

```
ECS (Entity-Component-System) + 좌표계 변환 레이어 + 추상화 인터페이스
├── Entity Manager (엔티티 생명주기 관리)
├── Component Registry (컴포넌트 타입 관리)
├── System Orchestrator (시스템 실행 순서 제어)
├── 🆕 Coordinate Transformation Layer (좌표계 변환)
└── Interface Abstractions (성능 최적화 교체 준비)
```

### 핵심 설계 원칙

1. **추상화 우선**: 모든 시스템을 인터페이스로 설계
2. **상태와 계산 분리**: 순수 함수 기반 계산 로직
3. **데이터 드리븐**: JSON 기반 외부 데이터 관리
4. **테스트 중심**: pytest 기반 단위/통합 테스트
5. **🆕 다형성 기반 최적화**: 좌표 변환 시스템의 교체 가능한 구현

## 2.2 🆕 좌표계 변환 시스템

### 좌표계 인터페이스 설계

```python
from abc import ABC, abstractmethod

class ICoordinateTransformer(ABC):
    """좌표 변환 시스템의 다형성 인터페이스"""
    
    @abstractmethod
    def world_to_screen(self, world_pos: Vector2) -> Vector2:
        """월드 좌표를 스크린 좌표로 변환"""
        pass
    
    @abstractmethod 
    def screen_to_world(self, screen_pos: Vector2) -> Vector2:
        """스크린 좌표를 월드 좌표로 변환"""
        pass
    
    @abstractmethod
    def get_camera_offset(self) -> Vector2:
        """현재 카메라 오프셋 반환"""
        pass

class CameraBasedTransformer(ICoordinateTransformer):
    """초기 구현: 단순한 카메라 오프셋 방식"""
    
    def __init__(self, camera_component: CameraComponent):
        self.camera = camera_component
        self._cached_offset = Vector2(0, 0)
        self._cache_dirty = True
    
    def world_to_screen(self, world_pos: Vector2) -> Vector2:
        offset = self.get_camera_offset()
        return Vector2(world_pos.x - offset.x, world_pos.y - offset.y)
    
    def screen_to_world(self, screen_pos: Vector2) -> Vector2:
        offset = self.get_camera_offset()
        return Vector2(screen_pos.x + offset.x, screen_pos.y + offset.y)
    
    def get_camera_offset(self) -> Vector2:
        if self._cache_dirty:
            self._cached_offset = self.camera.world_offset.copy()
            self._cache_dirty = False
        return self._cached_offset

class OptimizedTransformer(ICoordinateTransformer):  
    """향후 최적화: 캐싱, 배치 처리 등 적용된 버전"""
    pass

class SpatialOptimizedTransformer(ICoordinateTransformer):
    """향후 확장: 공간 분할 기반 최적화 버전"""
    pass
```

### 좌표계 통합 관리자

```python
class CoordinateManager:
    """전역 좌표 변환 관리자"""
    
    def __init__(self):
        self.transformer: ICoordinateTransformer = None
        self.observers: List[ICoordinateObserver] = []
    
    def set_transformer(self, transformer: ICoordinateTransformer):
        """좌표 변환 구현체 교체 (런타임 최적화 가능)"""
        self.transformer = transformer
        self._notify_observers()
    
    def world_to_screen(self, world_pos: Vector2) -> Vector2:
        return self.transformer.world_to_screen(world_pos)
    
    def screen_to_world(self, screen_pos: Vector2) -> Vector2:
        return self.transformer.screen_to_world(screen_pos)
```

## 2.3 🆕 핵심 시스템 재설계

### Core Systems (카메라 중심 시스템)

```python
# 시스템 인터페이스 정의
class ISystem(ABC):
    @abstractmethod
    def update(self, entities: List[Entity], delta_time: float) -> None: pass
    
    @abstractmethod  
    def initialize(self, coordinate_manager: CoordinateManager) -> None: pass
    
    @abstractmethod
    def cleanup(self) -> None: pass

# 🆕 카메라 시스템 - 핵심 시스템으로 승격
class ICameraSystem(ISystem): 
    """플레이어 중앙 고정 및 월드 오프셋 관리"""
    pass

class CameraSystem(ICameraSystem):
    def __init__(self, coordinate_manager: CoordinateManager):
        self.coordinate_manager = coordinate_manager
        self.screen_center = Vector2(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
    
    def update(self, entities: List[Entity], delta_time: float) -> None:
        for camera_entity in entities.with_component(CameraComponent):
            camera = camera_entity.get_component(CameraComponent)
            
            if camera.follow_target:
                player_movement = camera.follow_target.get_component(PlayerMovementComponent)
                
                # 🆕 핵심: 플레이어 이동의 역방향으로 월드 이동
                if player_movement.direction.length() > 0.1:  # 데드존
                    movement_delta = player_movement.direction * player_movement.speed * delta_time
                    camera.world_offset -= movement_delta
                
                # 월드 경계 처리
                camera.world_offset.x = max(camera.world_bounds[0], 
                                          min(camera.world_bounds[2], camera.world_offset.x))
                camera.world_offset.y = max(camera.world_bounds[1], 
                                          min(camera.world_bounds[3], camera.world_offset.y))
                
                # 좌표 변환기 업데이트
                self.coordinate_manager.transformer._cache_dirty = True

# 주요 시스템들 (우선순위 재조정)
class ICollisionSystem(ISystem): pass    # 충돌감지 (최우선 최적화)
class IRenderSystem(ISystem): pass       # 렌더링 (좌표변환 적용, 2순위 최적화)  
class IMapSystem(ISystem): pass          # 🆕 맵 렌더링 시스템 (무한 스크롤)
class IAISystem(ISystem): pass           # AI 계산 (월드좌표 기반, 3순위 최적화)
class IPhysicsSystem(ISystem): pass      # 물리 시뮬레이션 (4순위)
```

### 🆕 Entity-Component 구조 업데이트

```python
# 🆕 플레이어 컴포넌트 재설계
@dataclass
class PlayerMovementComponent:
    """플레이어는 스크린 중앙 고정, 논리적 월드 위치만 추적"""
    world_position: Vector2       # 월드 상의 논리적 위치
    direction: Vector2            # 현재 이동/바라보는 방향
    speed: float                  # 이동 속도
    rotation_angle: float         # 플레이어 스프라이트 회전각 (라디안)
    angular_velocity_limit: float = 5.0  # 부드러운 회전을 위한 각속도 제한

@dataclass
class CameraComponent:
    """🆕 월드 전체를 이동시키는 카메라 오프셋 관리"""
    world_offset: Vector2         # 월드 전체 오프셋 (핵심!)
    screen_center: Vector2        # 화면 중앙 좌표 (플레이어 고정 위치)
    world_bounds: tuple[float, float, float, float]  # 월드 경계 (min_x, min_y, max_x, max_y)
    follow_target: Optional[Entity] = None

@dataclass
class MapRenderComponent:
    """🆕 무한 스크롤링 타일 배경"""
    tile_size: int = 64
    tile_texture_id: str = "grid_pattern"
    visible_range: int = 2  # 화면 밖 추가 렌더링 범위

# 기존 컴포넌트들
@dataclass
class HealthComponent:
    current: int
    maximum: int
    regeneration_rate: float

@dataclass  
class MovementComponent:
    """일반 엔티티용 이동 (월드 좌표 기반)"""
    velocity: Vector2
    max_speed: float
    acceleration: float

@dataclass
class PositionComponent:
    """🆕 모든 엔티티의 월드 위치 (렌더링 시 좌표 변환 적용)"""
    world_x: float
    world_y: float
    
    @property
    def world_position(self) -> Vector2:
        return Vector2(self.world_x, self.world_y)

@dataclass
class WeaponComponent:
    damage: int
    attack_speed: float  # 초 단위 (FPS 독립적)
    range: float
    projectile_type: str

# 엔티티 조합 예시
PlayerEntity = Entity([
    HealthComponent(100, 100, 0.0),
    PlayerMovementComponent(Vector2(0,0), Vector2(0,0), 200.0, 0.0, 5.0),
    WeaponComponent(10, 0.5, 100.0, "basic"),
    # 🆕 플레이어는 PositionComponent 없음 (스크린 중앙 고정)
])

CameraEntity = Entity([
    CameraComponent(Vector2(0,0), Vector2(SCREEN_WIDTH//2, SCREEN_HEIGHT//2), 
                    (-2000, -2000, 2000, 2000), player_entity)
])
```

## 2.4 성능 최적화 전략 업데이트

### 단계별 최적화 계획

| 우선순위 | 시스템 | 초기 구현 | 최적화 구현 | 성능 향상 | 복잡도 증가 |
|---------|--------|-----------|-------------|-----------|-------------|
| 1 | 🆕 CoordinateTransformer | 단순 오프셋 계산 | 캐싱 + 배치 처리 | 🟢 중간 | 🟡 2배 |
| 2 | CollisionSystem | O(n²) 브루트포스 | Spatial Partitioning | 🟢 극대 | 🔴 10배 |
| 3 | RenderSystem | 개별 draw() + 좌표변환 | Sprite Group + 컬링 | 🟡 중간 | 🟡 3배 |  
| 4 | 🆕 MapSystem | 전체 타일 렌더링 | 가시영역만 렌더링 | 🟢 높음 | 🟡 2배 |
| 5 | AISystem | if-else 체인 | Behavior Tree | 🟢 확장성 | 🔴 6배 |
| 6 | PhysicsSystem | 기본 벡터 연산 | Pymunk 통합 | 🟢 향상 | 🔴 3배 |

### 🆕 좌표 변환 최적화

```python
class OptimizedCoordinateTransformer(ICoordinateTransformer):
    """성능 최적화된 좌표 변환 시스템"""
    
    def __init__(self, camera_component: CameraComponent):
        self.camera = camera_component
        self._cached_offset = Vector2(0, 0)
        self._cache_frame = -1
        self._current_frame = 0
        
        # 배치 처리용 버퍼
        self._batch_world_positions = []
        self._batch_screen_positions = []
    
    def world_to_screen(self, world_pos: Vector2) -> Vector2:
        """개별 좌표 변환 (캐싱 적용)"""
        self._update_cache_if_needed()
        return Vector2(world_pos.x - self._cached_offset.x, 
                      world_pos.y - self._cached_offset.y)
    
    def batch_world_to_screen(self, world_positions: List[Vector2]) -> List[Vector2]:
        """배치 좌표 변환 (성능 최적화)"""
        self._update_cache_if_needed()
        offset = self._cached_offset
        
        return [Vector2(pos.x - offset.x, pos.y - offset.y) 
                for pos in world_positions]
    
    def _update_cache_if_needed(self):
        if self._cache_frame != self._current_frame:
            self._cached_offset = self.camera.world_offset.copy()
            self._cache_frame = self._current_frame
    
    def advance_frame(self):
        """프레임 진행 (매 게임 루프마다 호출)"""
        self._current_frame += 1
```

---

# 3. 🆕 게임 시스템 상세 설계 (Camera-Aware Game Systems)

## 3.1 플레이어 시스템 재설계

### 🆕 플레이어 이동 시스템

```python
class PlayerMovementSystem(ISystem):
    """플레이어 중앙 고정 + 마우스 추적 시스템"""
    
    def __init__(self, coordinate_manager: CoordinateManager):
        self.coordinate_manager = coordinate_manager
        self.screen_center = Vector2(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
    
    def update(self, entities: List[Entity], delta_time: float) -> None:
        for player_entity in entities.with_component(PlayerMovementComponent):
            movement = player_entity.get_component(PlayerMovementComponent)
            
            # 마우스 위치 추적
            mouse_pos = pygame.mouse.get_pos()
            mouse_direction = (Vector2(mouse_pos) - self.screen_center)
            
            # 데드존 처리
            if mouse_direction.length() > 10.0:  # 10픽셀 데드존
                mouse_direction = mouse_direction.normalize()
                target_angle = math.atan2(mouse_direction.y, mouse_direction.x)
                
                # 부드러운 회전
                self._smooth_rotation(movement, target_angle, delta_time)
                
                # 이동 방향과 속도 설정 (카메라 시스템에서 사용)
                movement.direction = mouse_direction
                movement.speed = movement.max_speed
                
                # 논리적 월드 위치 업데이트
                movement.world_position += mouse_direction * movement.speed * delta_time
            else:
                # 정지 상태
                movement.direction = Vector2(0, 0)
                movement.speed = 0
    
    def _smooth_rotation(self, movement: PlayerMovementComponent, 
                        target_angle: float, delta_time: float):
        """부드러운 회전 처리"""
        angle_diff = target_angle - movement.rotation_angle
        
        # 각도 차이 정규화 (-π ~ π)
        while angle_diff > math.pi:
            angle_diff -= 2 * math.pi
        while angle_diff < -math.pi:
            angle_diff += 2 * math.pi
        
        # 각속도 제한 적용
        rotation_speed = min(movement.angular_velocity_limit * delta_time, 
                           abs(angle_diff))
        movement.rotation_angle += rotation_speed * (1 if angle_diff > 0 else -1)
```

### 자동 공격 시스템 (월드 좌표 기반)

```python
class AutoAttackSystem(ISystem):
    """🆕 월드 좌표 기반 자동 공격 시스템"""
    
    def __init__(self, coordinate_manager: CoordinateManager):
        self.coordinate_manager = coordinate_manager
    
    def update(self, entities: List[Entity], delta_time: float) -> None:
        for player_entity in entities.with_component(PlayerComponent):
            weapon = player_entity.get_component(WeaponComponent)
            
            # 시간 기반 공격 쿨다운 (FPS 독립적)
            weapon.last_attack_time += delta_time
            if weapon.last_attack_time >= weapon.attack_speed:
                self._perform_attack(player_entity, entities)
                weapon.last_attack_time = 0.0
    
    def _perform_attack(self, player_entity: Entity, all_entities: List[Entity]):
        player_movement = player_entity.get_component(PlayerMovementComponent)
        weapon = player_entity.get_component(WeaponComponent)
        
        # 🆕 월드 좌표에서 가장 가까운 적 탐색
        target = self._find_nearest_enemy_in_world(player_movement.world_position, 
                                                  all_entities, weapon.range)
        if target:
            self._create_projectile_in_world(player_movement.world_position, 
                                           target.get_component(PositionComponent).world_position,
                                           weapon)
    
    def _find_nearest_enemy_in_world(self, player_world_pos: Vector2, 
                                    entities: List[Entity], weapon_range: float) -> Optional[Entity]:
        """월드 좌표 기반 적 탐색"""
        nearest_enemy = None
        min_distance = weapon_range
        
        for entity in entities.with_component(EnemyAIComponent, PositionComponent):
            enemy_pos = entity.get_component(PositionComponent).world_position
            distance = (enemy_pos - player_world_pos).length()
            
            if distance < min_distance:
                min_distance = distance
                nearest_enemy = entity
        
        return nearest_enemy
```

## 3.2 🆕 맵 시스템 구현

### 무한 스크롤 타일 시스템

```python
class MapRenderSystem(ISystem):
    """무한 스크롤링 타일 기반 배경 시스템"""
    
    def __init__(self, coordinate_manager: CoordinateManager):
        self.coordinate_manager = coordinate_manager
        self.tile_size = 64
        self.tile_cache = {}  # 타일 스프라이트 캐싱
        self.visible_tiles = set()  # 현재 화면에 보이는 타일들
    
    def update(self, entities: List[Entity], delta_time: float) -> None:
        """가시 타일 영역 업데이트"""
        camera_offset = self.coordinate_manager.transformer.get_camera_offset()
        self._update_visible_tiles(camera_offset)
    
    def render(self, screen: pygame.Surface, entities: List[Entity]) -> None:
        """가시 타일들만 렌더링"""
        camera_offset = self.coordinate_manager.transformer.get_camera_offset()
        
        for tile_x, tile_y in self.visible_tiles:
            # 타일의 월드 좌표 계산
            tile_world_x = tile_x * self.tile_size
            tile_world_y = tile_y * self.tile_size
            
            # 스크린 좌표로 변환
            screen_pos = self.coordinate_manager.world_to_screen(
                Vector2(tile_world_x, tile_world_y))
            
            # 화면 경계 확인 후 렌더링
            if self._is_on_screen(screen_pos):
                self._draw_tile(screen, screen_pos, tile_x, tile_y)
    
    def _update_visible_tiles(self, camera_offset: Vector2):
        """화면에 보이는 타일 범위 계산"""
        self.visible_tiles.clear()
        
        # 화면 좌상단 월드 좌표
        top_left_world = self.coordinate_manager.screen_to_world(Vector2(0, 0))
        # 화면 우하단 월드 좌표  
        bottom_right_world = self.coordinate_manager.screen_to_world(
            Vector2(SCREEN_WIDTH, SCREEN_HEIGHT))
        
        # 타일 인덱스 범위 계산 (여유분 포함)
        start_tile_x = int(top_left_world.x // self.tile_size) - 1
        end_tile_x = int(bottom_right_world.x // self.tile_size) + 2
        start_tile_y = int(top_left_world.y // self.tile_size) - 1
        end_tile_y = int(bottom_right_world.y // self.tile_size) + 2
        
        # 가시 타일 목록 생성
        for tile_y in range(start_tile_y, end_tile_y):
            for tile_x in range(start_tile_x, end_tile_x):
                self.visible_tiles.add((tile_x, tile_y))
    
    def _draw_tile(self, screen: pygame.Surface, screen_pos: Vector2, 
                   tile_x: int, tile_y: int):
        """개별 타일 렌더링 (패턴 기반)"""
        # 타일 패턴 결정 (그리드 시각화)
        if (tile_x + tile_y) % 2 == 0:
            color = (240, 240, 240)  # 밝은 회색
        else:
            color = (220, 220, 220)  # 어두운 회색
        
        # 격자 선 그리기
        pygame.draw.rect(screen, color, 
                        (screen_pos.x, screen_pos.y, self.tile_size, self.tile_size))
        pygame.draw.rect(screen, (200, 200, 200), 
                        (screen_pos.x, screen_pos.y, self.tile_size, self.tile_size), 1)
```

## 3.3 🆕 AI 시스템 월드 좌표 적용

### 적 AI 시스템 재설계

```python
class EnemyAISystem(ISystem):
    """🆕 월드 좌표 기반 AI 시스템"""
    
    def __init__(self, coordinate_manager: CoordinateManager):
        self.coordinate_manager = coordinate_manager
    
    def update(self, entities: List[Entity], delta_time: float) -> None:
        # 플레이어 월드 위치 획득
        player_world_pos = self._get_player_world_position(entities)
        if not player_world_pos:
            return
        
        for enemy_entity in entities.with_component(EnemyAIComponent, PositionComponent):
            ai = enemy_entity.get_component(EnemyAIComponent)
            
            if ai.ai_type == "basic":
                self._update_basic_ai(enemy_entity, player_world_pos, delta_time)
            elif ai.ai_type == "boss": 
                self._update_boss_ai(enemy_entity, player_world_pos, delta_time)
    
    def _get_player_world_position(self, entities: List[Entity]) -> Optional[Vector2]:
        """플레이어의 월드 위치 획득"""
        for entity in entities.with_component(PlayerMovementComponent):
            return entity.get_component(PlayerMovementComponent).world_position
        return None
    
    def _update_basic_ai(self, enemy_entity: Entity, player_world_pos: Vector2, 
                        delta_time: float):
        """기본 적 AI - 월드 좌표 기반"""
        ai = enemy_entity.get_component(EnemyAIComponent)
        enemy_pos = enemy_entity.get_component(PositionComponent)
        enemy_movement = enemy_entity.get_component(MovementComponent)
        
        # 플레이어와의 월드 좌표 거리 계산
        distance = (player_world_pos - enemy_pos.world_position).length()
        
        if distance <= ai.attack_range:
            # 공격 상태
            self._attack_player(enemy_entity, player_world_pos)
        elif distance <= ai.chase_range:
            # 추적 상태 - 월드 좌표에서 방향 계산
            direction = (player_world_pos - enemy_pos.world_position).normalize()
            enemy_movement.velocity = direction * ai.movement_speed
            
            # 월드 위치 업데이트
            enemy_pos.world_x += enemy_movement.velocity.x * delta_time
            enemy_pos.world_y += enemy_movement.velocity.y * delta_time
        else:
            # 대기/순찰 상태
            enemy_movement.velocity = Vector2(0, 0)
```

## 3.4 🆕 렌더링 시스템 업데이트

### 좌표 변환 적용 렌더링

```python
class EntityRenderSystem(ISystem):
    """🆕 좌표 변환이 적용된 엔티티 렌더링 시스템"""
    
    def __init__(self, coordinate_manager: CoordinateManager):
        self.coordinate_manager = coordinate_manager
        self.screen_center = Vector2(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
    
    def render(self, screen: pygame.Surface, entities: List[Entity]) -> None:
        # 🆕 일반 엔티티들: 월드 좌표 → 스크린 좌표 변환하여 렌더링
        self._render_world_entities(screen, entities)
        
        # 🆕 플레이어: 항상 화면 중앙에 렌더링 (좌표 변환 없음)
        self._render_player_at_center(screen, entities)
        
        # UI 요소들: 스크린 좌표 고정 렌더링
        self._render_ui_elements(screen, entities)
    
    def _render_world_entities(self, screen: pygame.Surface, entities: List[Entity]):
        """월드 엔티티들 렌더링 (좌표 변환 적용)"""
        renderable_entities = []
        
        # 렌더링 대상 엔티티 수집 및 좌표 변환
        for entity in entities.with_component(PositionComponent, RenderComponent):
            pos = entity.get_component(PositionComponent)
            render = entity.get_component(RenderComponent)
            
            # 월드 좌표 → 스크린 좌표 변환
            screen_pos = self.coordinate_manager.world_to_screen(pos.world_position)
            
            # 화면 밖 컬링 (성능 최적화)
            if self._is_on_screen(screen_pos, render.width, render.height):
                renderable_entities.append((entity, screen_pos, render))
        
        # 깊이 정렬 후 렌더링
        renderable_entities.sort(key=lambda item: item[1].y)  # Y좌표 기준 정렬
        
        for entity, screen_pos, render in renderable_entities:
            screen.blit(render.sprite, (screen_pos.x, screen_pos.y))
    
    def _render_player_at_center(self, screen: pygame.Surface, entities: List[Entity]):
        """플레이어를 화면 중앙에 고정 렌더링"""
        for player_entity in entities.with_component(PlayerMovementComponent, RenderComponent):
            movement = player_entity.get_component(PlayerMovementComponent)
            render = player_entity.get_component(RenderComponent)
            
            # 회전 적용된 스프라이트 생성
            rotated_sprite = pygame.transform.rotate(render.sprite, 
                                                   math.degrees(-movement.rotation_angle))
            
            # 화면 중앙에 렌더링
            sprite_rect = rotated_sprite.get_rect()
            sprite_rect.center = (self.screen_center.x, self.screen_center.y)
            screen.blit(rotated_sprite, sprite_rect)
    
    def _is_on_screen(self, screen_pos: Vector2, width: int, height: int) -> bool:
        """화면 밖 컬링 판정"""
        margin = 50  # 여유분
        return (screen_pos.x + width >= -margin and 
                screen_pos.x <= SCREEN_WIDTH + margin and
                screen_pos.y + height >= -margin and 
                screen_pos.y <= SCREEN_HEIGHT + margin)
```

---

# 4. 데이터 관리 및 설정 시스템 (Data Management) - 기존 유지

[기존 DEV-PRD.md의 섹션 4와 동일하게 유지]

---

# 5. 테스트 전략 및 품질 보장 (Testing Strategy) - 기존 유지 + 좌표계 테스트 추가

## 5.1 pytest 기반 테스트 아키텍처

### 테스트 구조 및 분류

```
tests/
├── unit/                 # 단위 테스트
│   ├── test_items.py     # pytest -m items
│   ├── test_collision.py # pytest -m collision  
│   ├── test_ai.py        # pytest -m ai
│   ├── test_balance.py   # pytest -m balance
│   └── 🆕 test_coordinates.py # pytest -m coordinates (좌표계 테스트)
├── integration/          # 통합 테스트
│   ├── test_gameplay.py  # 전체 게임플레이 플로우
│   ├── test_systems.py   # 시스템 간 상호작용
│   └── 🆕 test_camera_systems.py # 카메라 시스템 통합 테스트
└── performance/          # 성능 테스트
    ├── test_fps.py       # FPS 성능 벤치마크
    ├── test_memory.py    # 메모리 사용량 테스트
    └── 🆕 test_coordinate_performance.py # 좌표 변환 성능 테스트
```

### 🆕 좌표계 테스트

```python
# tests/unit/test_coordinates.py
import pytest
from src.systems.coordinate_system import CameraBasedTransformer, OptimizedTransformer
from src.components.camera import CameraComponent
from src.utils.vector import Vector2

@pytest.mark.coordinates
class TestCoordinateTransformations:
    
    def test_world_to_screen_basic(self):
        """기본 월드→스크린 좌표 변환 테스트"""
        # Given
        camera = CameraComponent(Vector2(100, 50), Vector2(400, 300), (-1000, -1000, 1000, 1000))
        transformer = CameraBasedTransformer(camera)
        world_pos = Vector2(200, 150)
        
        # When
        screen_pos = transformer.world_to_screen(world_pos)
        
        # Then
        assert screen_pos.x == 100  # 200 - 100 = 100
        assert screen_pos.y == 100  # 150 - 50 = 100
    
    def test_screen_to_world_basic(self):
        """기본 스크린→월드 좌표 변환 테스트"""
        # Given
        camera = CameraComponent(Vector2(100, 50), Vector2(400, 300), (-1000, -1000, 1000, 1000))
        transformer = CameraBasedTransformer(camera)
        screen_pos = Vector2(100, 100)
        
        # When
        world_pos = transformer.screen_to_world(screen_pos)
        
        # Then
        assert world_pos.x == 200  # 100 + 100 = 200
        assert world_pos.y == 150  # 100 + 50 = 150
    
    def test_coordinate_transformation_consistency(self):
        """좌표 변환 일관성 테스트 (왕복 변환)"""
        # Given
        camera = CameraComponent(Vector2(75, 25), Vector2(400, 300), (-1000, -1000, 1000, 1000))
        transformer = CameraBasedTransformer(camera)
        original_world_pos = Vector2(300, 250)
        
        # When: 월드 → 스크린 → 월드 변환
        screen_pos = transformer.world_to_screen(original_world_pos)
        converted_world_pos = transformer.screen_to_world(screen_pos)
        
        # Then: 원래 좌표와 일치해야 함
        assert abs(converted_world_pos.x - original_world_pos.x) < 0.01
        assert abs(converted_world_pos.y - original_world_pos.y) < 0.01
    
    @pytest.mark.parametrize("transformer_class", [
        CameraBasedTransformer,
        OptimizedTransformer
    ])
    def test_transformer_interface_compatibility(self, transformer_class):
        """다형성 인터페이스 호환성 테스트"""
        # Given
        camera = CameraComponent(Vector2(50, 50), Vector2(400, 300), (-1000, -1000, 1000, 1000))
        transformer = transformer_class(camera)
        test_positions = [Vector2(0, 0), Vector2(100, 200), Vector2(-50, -75)]
        
        # When & Then: 모든 구현체가 동일한 인터페이스로 작동
        for world_pos in test_positions:
            screen_pos = transformer.world_to_screen(world_pos)
            back_to_world = transformer.screen_to_world(screen_pos)
            
            assert abs(back_to_world.x - world_pos.x) < 0.01
            assert abs(back_to_world.y - world_pos.y) < 0.01

# tests/performance/test_coordinate_performance.py
@pytest.mark.performance
class TestCoordinatePerformance:
    
    def test_coordinate_transformation_performance(self):
        """좌표 변환 시스템 성능 벤치마크"""
        # Given
        camera = CameraComponent(Vector2(0, 0), Vector2(400, 300), (-1000, -1000, 1000, 1000))
        basic_transformer = CameraBasedTransformer(camera)
        optimized_transformer = OptimizedTransformer(camera)
        
        test_positions = [Vector2(i, i*2) for i in range(1000)]
        
        # When: 기본 구현체 성능 측정
        start_time = time.time()
        for pos in test_positions:
            basic_transformer.world_to_screen(pos)
        basic_time = time.time() - start_time
        
        # When: 최적화 구현체 성능 측정
        start_time = time.time()
        for pos in test_positions:
            optimized_transformer.world_to_screen(pos)
        optimized_time = time.time() - start_time
        
        # Then: 최적화 버전이 더 빠르거나 비슷해야 함
        assert optimized_time <= basic_time * 1.1  # 10% 오차 허용
        assert basic_time < 0.1  # 1000개 변환이 100ms 이내
```

---

# 6. 🆕 개발 로드맵 및 우선순위 (Updated Development Roadmap)

## 6.1 MVP 개발 단계 (일정 수정)

### Phase 1: 핵심 인프라 구축 (2-3주) - 변경 없음

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

### 🆕 Phase 2: 카메라 중심 게임플레이 구현 (5-6주, +2주 추가)

**목표**: 플레이어 중앙 고정 + 월드 좌표 기반 게임플레이 + 적 AI + 경험치 시스템

**🎮 개발 항목**:

**Week 1-2: 좌표계 인프라 구축**

- [ ] 🆕 ICoordinateTransformer 인터페이스 설계 및 기본 구현
- [ ] 🆕 CameraSystem 구현 (플레이어 중앙 고정, 월드 오프셋 관리)
- [ ] 🆕 CoordinateManager 전역 관리자 구현
- [ ] 🆕 좌표계 단위 테스트 작성

**Week 3-4: 플레이어 및 맵 시스템**

- [ ] 🆕 PlayerMovementSystem 재구현 (마우스 추적, 중앙 고정)
- [ ] 🆕 MapRenderSystem 구현 (무한 스크롤 타일 배경)
- [ ] 🆕 EntityRenderSystem 업데이트 (좌표 변환 적용)
- [ ] 맵 경계 처리 및 시각적 그리드 패턴 구현

**Week 5-6: 게임플레이 로직**

- [ ] 🆕 AutoAttackSystem 재구현 (월드 좌표 기반 타겟팅)
- [ ] 🆕 EnemyAISystem 재구현 (월드 좌표 기반 추적/공격)
- [ ] 기본 적 1종 + 간단 AI (추격 + 공격)
- [ ] 투사체 시스템 (월드 좌표 기반)
- [ ] 경험치/레벨업 시스템
- [ ] 기본 UI (체력, 경험치 바)

**✅ 완료 조건**:

- ✅ **플레이어가 마우스 방향을 바라보며 화면 중앙에 고정**
- ✅ **맵이 플레이어 이동의 역방향으로 자연스럽게 움직임**  
- ✅ **카메라 경계 처리로 맵 밖으로 나가지 않음**
- ✅ **적을 자동으로 공격하여 처치 가능 (월드 좌표 기준)**
- ✅ **경험치 획득으로 레벨업 가능**
- ✅ **적 20마리 동시 존재 시 40+ FPS 유지**
- 🆕 **좌표 변환 시스템이 모든 게임플레이에 올바르게 적용**

### Phase 3: 아이템 시스템 구현 (2-3주) - 변경 없음

**목표**: JSON 기반 아이템 + 룰 엔진 + 시너지

### Phase 4: 보스 시스템 구현 (3-4주) - 변경 없음  

**목표**: 교장선생님 보스 + 디버프 시스템

## 6.2 🆕 확장 단계 (MVP 이후)

### Phase 5: 성능 최적화 (2-3주) - 우선순위 재조정

- 🆕 좌표 변환 시스템 최적화 (배치 처리, 고급 캐싱)
- 충돌감지 시스템 → Spatial Partitioning 교체
- 렌더링 시스템 → Sprite Group 최적화 + 컬링
- 🆕 맵 렌더링 최적화 (가시 영역만 처리)
- 메모리 풀링 패턴 적용
- 성능 프로파일링 및 병목 지점 해결

### Phase 6: 모바일 이식 준비 (3-4주) - 🆕 추가

- 🆕 터치 입력 시스템 (마우스 입력과 통합)
- 🆕 다양한 해상도/화면비 지원
- 🆕 모바일 성능 최적화 (배터리, 발열 고려)
- 🆕 플랫폼별 빌드 시스템

### Phase 7: 콘텐츠 확장 (4-6주) - 변경 없음

### Phase 8: 품질 향상 (2-3주) - 변경 없음

---

# 7. 🆕 기술적 제약사항 및 위험 요소 (Updated Technical Constraints & Risks)

## 7.1 기술적 제약사항

### Python + Pygame 성능 한계

| 제약사항 | 영향도 | 대응 방안 | 🆕 좌표계 영향 |
|----------|--------|-----------| -------------|
| GIL(Global Interpreter Lock) | 🔴 높음 | 게임 로직을 단일 스레드로 설계 | 영향 없음 |
| Pygame 렌더링 성능 | 🟡 중간 | Sprite Group + 더티 렌더링 활용 | 🟡 좌표 변환 추가 연산 |
| 메모리 관리 자동화 | 🟡 중간 | Object Pooling 패턴으로 GC 압박 감소 | 🟡 변환 결과 캐싱 |
| 실행 파일 크기 | 🟢 낮음 | PyInstaller 최적화 옵션 활용 | 영향 없음 |

### 🆕 좌표 변환 시스템 제약사항

| 제약사항 | 영향도 | 대응 방안 |
|----------|--------| ----------|
| 모든 렌더링마다 좌표 변환 | 🟡 중간 | 배치 처리 + 캐싱 |
| 월드-스크린 좌표 일관성 유지 | 🔴 높음 | 인터페이스 기반 추상화 |
| 개발자 학습 곡선 | 🟡 중간 | 헬퍼 함수 + 문서화 |

## 7.2 🆕 위험 요소 및 완화 방안

### 좌표계 변환 위험 요소

```python
# 위험: 좌표 변환 성능 병목
class CoordinateOptimizationManager:
    """좌표 변환 성능 모니터링 및 최적화"""
    
    def __init__(self):
        self.transform_count = 0
        self.frame_start_time = 0
        self.performance_threshold = 0.005  # 5ms
    
    def monitor_performance(self):
        """성능 모니터링 및 최적화 구현체 자동 전환"""
        frame_time = time.time() - self.frame_start_time
        
        if frame_time > self.performance_threshold:
            # 성능 이슈 감지 시 최적화 버전으로 전환
            coordinate_manager.set_transformer(OptimizedTransformer())
            
    def start_frame(self):
        self.frame_start_time = time.time()
        self.transform_count = 0
```

### 🆕 개발 복잡성 위험 요소

**위험**: 좌표계 혼동으로 인한 버그 발생

**완화 방안**:

1. **명확한 명명 규칙**: `world_pos`, `screen_pos`로 구분
2. **타입 안전성**: `WorldPosition`, `ScreenPosition` 타입 클래스 도입
3. **테스트 커버리지**: 좌표 변환 관련 95% 이상 테스트 커버리지
4. **개발 도구**: 좌표 디버깅용 시각적 도구 제공

```python
# 타입 안전성 강화
@dataclass
class WorldPosition:
    x: float
    y: float
    
    def to_vector2(self) -> Vector2:
        return Vector2(self.x, self.y)

@dataclass  
class ScreenPosition:
    x: float
    y: float
    
    def to_vector2(self) -> Vector2:
        return Vector2(self.x, self.y)
```

---

# 8. 성공 지표 및 검증 방법 (Success Metrics) - 기존 유지 + 좌표계 지표 추가

## 8.1 기술적 성공 지표

### 성능 지표

- **FPS 안정성**: 적 50마리 + 투사체 100개 상황에서 40+ FPS 유지율 95% 이상
- **메모리 사용량**: 게임 실행 30분 후 메모리 증가량 50MB 이하
- **로딩 시간**: 게임 시작부터 플레이 가능까지 3초 이내
- 🆕 **좌표 변환 성능**: 1000개 엔티티 좌표 변환을 16ms 이내 처리

### 품질 지표  

- **테스트 커버리지**: 핵심 게임 로직 90% 이상
- **버그 밀도**: 플레이 10분당 크래시 0건, 심각한 버그 1건 이하
- **크로스 플랫폼**: Windows, macOS에서 동일한 게임플레이 경험
- 🆕 **좌표 정확성**: 좌표 변환 오차 0.1픽셀 이내

### 🆕 플레이어 경험 지표

- **조작 반응성**: 마우스 이동 → 화면 반응 지연 50ms 이내
- **카메라 부드러움**: 카메라 이동 시 끊김 현상 0%
- **시각적 일관성**: 모든 엔티티가 올바른 상대 위치에 렌더링

---

# 9. 부록 (Appendix)

## 9.1 참고 문서

- [기획 PRD](./PRD.md) - 게임 컨셉 및 기획 요구사항
- [게임 의존성](./game-dependency.md) - Python 라이브러리 스택  
- [아키텍트 인터뷰](./interview/25-08-07-아키텍쳐_기술_인터뷰.md) - 설계 결정 과정
- 🆕 [플레이어 이동 아키텍처 변경 인터뷰](./interview/25-08-07-플레이어_이동_아키텍처_변경_인터뷰.md) - 좌표계 변경 근거

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

### 🆕 프로젝트 구조 업데이트

```
AfterSchoolSurvivors/
├── src/
│   ├── core/          # ECS 프레임워크
│   ├── systems/       # 게임 시스템들
│   │   ├── camera.py      # 🆕 카메라 시스템
│   │   ├── coordinate.py  # 🆕 좌표 변환 시스템
│   │   └── map.py         # 🆕 맵 렌더링 시스템
│   ├── components/    # ECS 컴포넌트들
│   ├── data/          # 데이터 관리
│   └── ui/            # 사용자 인터페이스
├── data/              # JSON 데이터 파일들
├── tests/             # 테스트 코드
│   └── unit/
│       └── test_coordinates.py  # 🆕 좌표계 테스트
├── assets/            # 이미지, 사운드 리소스
└── docs/              # 문서화
    └── interview/     # 🆕 인터뷰 기록들
```

## 9.3 🆕 좌표계 개발 가이드라인

### 개발자 가이드라인

1. **좌표 명명 규칙**:
   - `world_pos`, `world_x`, `world_y`: 월드 좌표
   - `screen_pos`, `screen_x`, `screen_y`: 스크린 좌표
   - 절대 혼용 금지

2. **좌표 변환 원칙**:
   - 모든 게임 로직은 월드 좌표에서 수행
   - 렌더링만 스크린 좌표로 변환
   - `CoordinateManager`를 통한 일관된 변환

3. **성능 고려사항**:
   - 좌표 변환은 렌더링 시점에만 수행
   - 배치 변환 함수 적극 활용
   - 불필요한 중복 변환 방지

### 코딩 컨벤션 추가

```python
# 🆕 좌표 관련 명명 규칙
class PlayerMovementSystem:
    def update_player_world_position(self, world_delta: Vector2): pass

def render_entity_at_screen_position(screen_pos: Vector2): pass

# 🆕 인터페이스: I 접두사
class ICoordinateTransformer(ABC): pass

# 🆕 좌표 변환 컴포넌트
class CameraComponent: pass
class MapRenderComponent: pass
```

---

**문서 버전**: 0.2  
**최종 수정일**: 2025-08-07  
**주요 변경사항**: 플레이어 중앙 고정 카메라 시스템 아키텍처 전면 적용  
**다음 검토일**: Phase 2 카메라 시스템 구현 완료 시점