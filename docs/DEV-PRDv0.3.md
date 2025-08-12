# 방과후생존 게임 - 개발자 중심 PRD v0.3 (Product Requirements Document)

## 📋 문서 정보

- **문서 타입**: 기술 설계 중심 PRD v0.3
- **작성일**: 2025-01-12
- **아키텍트**: 시니어 게임 아키텍트
- **기반 문서**: [DEV-PRDv0.2](./DEV-PRDv0.2.md), [ProjectileSystem 옵저버 패턴 리팩토링](./interview/2025-01-12-ProjectileSystem-옵저버패턴-리팩토링.md)
- **주요 변경사항**: 옵저버 패턴 기반 이벤트 시스템 도입 및 ProjectileSystem 책임 분리
- **변경 근거**: 단일 책임 원칙 준수, 시스템 결합도 감소, 확장성 증대

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
4. **🆕 이벤트 기반 반응성**: 적 처치 시 즉각적인 피드백과 보상

---

# 2. 🆕 이벤트 기반 아키텍처 설계 (Event-Driven Architecture)

## 2.1 전체 시스템 아키텍처

### 아키텍처 패턴 선택

```
ECS (Entity-Component-System) + 좌표계 변환 레이어 + 🆕 이벤트 시스템 + 추상화 인터페이스
├── Entity Manager (엔티티 생명주기 관리)
├── Component Registry (컴포넌트 타입 관리)
├── System Orchestrator (시스템 실행 순서 제어)
├── Coordinate Transformation Layer (좌표계 변환)
├── 🆕 Event Bus System (이벤트 발행/구독 메커니즘)
└── Interface Abstractions (성능 최적화 교체 준비)
```

### 핵심 설계 원칙

1. **추상화 우선**: 모든 시스템을 인터페이스로 설계
2. **상태와 계산 분리**: 순수 함수 기반 계산 로직
3. **데이터 드리븐**: JSON 기반 외부 데이터 관리
4. **테스트 중심**: pytest 기반 단위/통합 테스트
5. **다형성 기반 최적화**: 좌표 변환 시스템의 교체 가능한 구현
6. **🆕 이벤트 기반 느슨한 결합**: 시스템 간 직접 의존성 제거

## 2.2 🆕 이벤트 시스템 설계

### 이벤트 기본 구조

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import IntEnum
from typing import Any, Callable, Dict, List, Optional
import time

class EventType(IntEnum):
    ENEMY_DEATH = 0
    PLAYER_LEVEL_UP = 1
    ITEM_COLLECTED = 2
    BOSS_SPAWNED = 3
    
    @property
    def display_name(self) -> str:
        return self._display_names[self]
    
    _display_names = {
        ENEMY_DEATH: "적 사망",
        PLAYER_LEVEL_UP: "플레이어 레벨업",
        ITEM_COLLECTED: "아이템 획득",
        BOSS_SPAWNED: "보스 출현"
    }

@dataclass
class BaseEvent(ABC):
    """모든 게임 이벤트의 기본 클래스"""
    event_type: EventType
    timestamp: float = None
    
    def __post_init__(self) -> None:
        if self.timestamp is None:
            self.timestamp = time.time()

@dataclass
class EnemyDeathEvent(BaseEvent):
    """적 사망 이벤트 - 최소 데이터만 포함"""
    enemy_entity_id: str
    
    def __post_init__(self) -> None:
        super().__post_init__()
        self.event_type = EventType.ENEMY_DEATH
        assert isinstance(self.enemy_entity_id, str), "enemy_entity_id must be string"
        assert len(self.enemy_entity_id) > 0, "enemy_entity_id cannot be empty"
```

### 이벤트 버스 시스템

```python
from collections import deque
from typing import Deque, Set

class IEventSubscriber(ABC):
    """이벤트 구독자 인터페이스"""
    
    @abstractmethod
    def handle_event(self, event: BaseEvent) -> None:
        """이벤트 처리 메서드"""
        pass
    
    @abstractmethod
    def get_subscribed_events(self) -> List[EventType]:
        """구독하는 이벤트 타입 목록 반환"""
        pass

class EventBus:
    """🆕 큐잉 방식 이벤트 버스 - ECS 시스템 독립성 보장"""
    
    def __init__(self):
        self._event_queue: Deque[BaseEvent] = deque()
        self._subscribers: Dict[EventType, Set[IEventSubscriber]] = {}
        self._processing = False
    
    def subscribe(self, event_type: EventType, subscriber: IEventSubscriber) -> None:
        """이벤트 구독자 등록"""
        if event_type not in self._subscribers:
            self._subscribers[event_type] = set()
        self._subscribers[event_type].add(subscriber)
    
    def unsubscribe(self, event_type: EventType, subscriber: IEventSubscriber) -> None:
        """이벤트 구독자 해제"""
        if event_type in self._subscribers:
            self._subscribers[event_type].discard(subscriber)
    
    def publish(self, event: BaseEvent) -> None:
        """이벤트 발행 (큐에 저장)"""
        self._event_queue.append(event)
    
    def process_events(self) -> None:
        """큐의 모든 이벤트 순차 처리"""
        if self._processing:
            return  # 재진입 방지
        
        self._processing = True
        
        try:
            while self._event_queue:
                event = self._event_queue.popleft()
                self._dispatch_event(event)
        except Exception as e:
            # 이벤트 처리 중 예외 발생 시 로깅 후 계속 진행
            print(f"Event processing error: {e}")
        finally:
            self._processing = False
    
    def _dispatch_event(self, event: BaseEvent) -> None:
        """특정 이벤트를 구독자들에게 전달"""
        if event.event_type not in self._subscribers:
            return
        
        for subscriber in self._subscribers[event.event_type].copy():
            try:
                subscriber.handle_event(event)
            except Exception as e:
                # 개별 구독자 오류가 다른 구독자에게 영향주지 않도록 격리
                print(f"Subscriber error: {e}")
    
    def get_queue_size(self) -> int:
        """현재 큐에 대기 중인 이벤트 수"""
        return len(self._event_queue)
```

## 2.3 🆕 ProjectileSystem 책임 분리

### 기존 문제점과 개선 방향

**기존 ProjectileSystem 문제점:**
- 투사체 물리 처리 + 적 사망 처리 + 경험치 계산 + 엔티티 제거 (단일 책임 원칙 위반)
- 다양한 시스템과 직접적인 의존성 (높은 결합도)
- 새로운 사망 관련 로직 추가 시 ProjectileSystem 수정 필요 (확장 어려움)

**개선된 아키텍처:**

```python
class ProjectileSystem(System, IEventPublisher):
    """🆕 투사체 물리 처리 및 적 사망 이벤트 발행 전용 시스템"""
    
    def __init__(self, priority: int = 15, event_bus: EventBus = None) -> None:
        super().__init__(priority=priority)
        self.event_bus = event_bus
        self._collision_detector = BruteForceCollisionDetector()
        self._expired_projectiles: list[Entity] = []
    
    def _handle_enemy_death(self, entity_manager: 'EntityManager', enemy_entity: 'Entity') -> None:
        """🆕 적 사망 시 이벤트 발행만 담당"""
        if self.event_bus:
            death_event = EnemyDeathEvent(enemy_entity_id=enemy_entity.entity_id)
            self.event_bus.publish(death_event)
        
        # 기존의 직접 처리 로직 제거 (경험치, 엔티티 제거 등)
        # 이제 이벤트 구독자들이 각자의 책임을 처리

class ExperienceSystem(System, IEventSubscriber):
    """🆕 경험치 처리 전용 시스템"""
    
    def get_subscribed_events(self) -> List[EventType]:
        return [EventType.ENEMY_DEATH]
    
    def handle_event(self, event: BaseEvent) -> None:
        if isinstance(event, EnemyDeathEvent):
            self._handle_enemy_death(event)
    
    def _handle_enemy_death(self, event: EnemyDeathEvent) -> None:
        """적 사망 시 경험치 계산 및 적용"""
        # EntityManager를 통해 적 정보 조회
        enemy_entity = self.entity_manager.get_entity(event.enemy_entity_id)
        if enemy_entity:
            enemy_component = self.entity_manager.get_component(enemy_entity, EnemyComponent)
            if enemy_component:
                experience_reward = enemy_component.get_experience_reward()
                # 플레이어에게 경험치 적용
                self._award_experience_to_player(experience_reward)

class ItemDropSystem(System, IEventSubscriber):
    """🆕 아이템 드롭 처리 시스템"""
    
    def get_subscribed_events(self) -> List[EventType]:
        return [EventType.ENEMY_DEATH]
    
    def handle_event(self, event: BaseEvent) -> None:
        if isinstance(event, EnemyDeathEvent):
            self._handle_enemy_death(event)
    
    def _handle_enemy_death(self, event: EnemyDeathEvent) -> None:
        """적 사망 시 아이템 드롭 확률 계산 및 생성"""
        enemy_entity = self.entity_manager.get_entity(event.enemy_entity_id)
        if enemy_entity:
            enemy_pos = self.entity_manager.get_component(enemy_entity, PositionComponent)
            if enemy_pos and self._should_drop_item():
                self._create_item_at_position(enemy_pos.world_position)

class EntityCleanupSystem(System, IEventSubscriber):
    """🆕 엔티티 정리 전용 시스템"""
    
    def get_subscribed_events(self) -> List[EventType]:
        return [EventType.ENEMY_DEATH]
    
    def handle_event(self, event: BaseEvent) -> None:
        if isinstance(event, EnemyDeathEvent):
            self._handle_enemy_death(event)
    
    def _handle_enemy_death(self, event: EnemyDeathEvent) -> None:
        """적 엔티티 제거 처리"""
        self.entity_manager.remove_entity(event.enemy_entity_id)
```

## 2.4 🆕 시스템 통합 및 초기화

### 게임 루프 통합

```python
class GameLoop:
    """🆕 이벤트 시스템이 통합된 게임 루프"""
    
    def __init__(self):
        self.entity_manager = EntityManager()
        self.system_orchestrator = SystemOrchestrator()
        self.event_bus = EventBus()
        
        # 이벤트 발행 시스템들
        self.projectile_system = ProjectileSystem(priority=15, event_bus=self.event_bus)
        
        # 이벤트 구독 시스템들
        self.experience_system = ExperienceSystem(priority=20)
        self.item_drop_system = ItemDropSystem(priority=21)
        self.entity_cleanup_system = EntityCleanupSystem(priority=22)
        
        # 구독 관계 설정
        self._setup_event_subscriptions()
        
        # 시스템 등록
        self.system_orchestrator.add_system(self.projectile_system)
        self.system_orchestrator.add_system(self.experience_system)
        self.system_orchestrator.add_system(self.item_drop_system)
        self.system_orchestrator.add_system(self.entity_cleanup_system)
    
    def _setup_event_subscriptions(self):
        """이벤트 구독 관계 설정"""
        for system in [self.experience_system, self.item_drop_system, self.entity_cleanup_system]:
            for event_type in system.get_subscribed_events():
                self.event_bus.subscribe(event_type, system)
    
    def update(self, delta_time: float):
        """게임 루프 업데이트"""
        # 시스템 업데이트
        self.system_orchestrator.update(self.entity_manager, delta_time)
        
        # 🆕 이벤트 처리 (모든 시스템 업데이트 후)
        self.event_bus.process_events()
```

---

# 3. 좌표계 변환 시스템 (기존 유지)

## 3.1 좌표계 인터페이스 설계

[DEV-PRDv0.2의 섹션 2.2와 동일하게 유지]

## 3.2 핵심 시스템 재설계

[DEV-PRDv0.2의 섹션 2.3과 동일하게 유지]

---

# 4. 🆕 게임 시스템 상세 설계 (Event-Aware Game Systems)

## 4.1 플레이어 시스템 재설계

[DEV-PRDv0.2의 섹션 3.1과 동일하게 유지]

## 4.2 🆕 무기 및 투사체 시스템

### 무기 시스템 (이벤트 연동)

```python
class WeaponSystem(System):
    """🆕 이벤트 기반 자동 공격 시스템"""
    
    def __init__(self, coordinate_manager: CoordinateManager, event_bus: EventBus):
        self.coordinate_manager = coordinate_manager
        self.event_bus = event_bus
    
    def _create_projectile_towards_target(self, player_pos: Vector2, target_pos: Vector2, weapon: WeaponComponent) -> None:
        """투사체 생성 (이벤트 발행 포함)"""
        projectile_entity = self._create_projectile_entity(player_pos, target_pos, weapon)
        
        # 투사체 생성 이벤트 발행 (향후 사운드, 이펙트 시스템에서 활용)
        if self.event_bus:
            projectile_event = ProjectileCreatedEvent(
                projectile_entity_id=projectile_entity.entity_id,
                weapon_type=weapon.weapon_type
            )
            self.event_bus.publish(projectile_event)

class ProjectileSystem(System):
    """🆕 투사체 물리 및 충돌 처리 시스템 (이벤트 발행)"""
    
    def _handle_projectile_enemy_collision(self, entity_manager, projectile_entity, enemy_entity):
        """투사체-적 충돌 처리 (이벤트 기반)"""
        # 데미지 적용
        projectile = entity_manager.get_component(projectile_entity, ProjectileComponent)
        enemy_health = entity_manager.get_component(enemy_entity, HealthComponent)
        
        if projectile and enemy_health:
            # 충돌 기록 및 데미지 적용
            if not projectile.has_hit_target(enemy_entity.entity_id):
                current_time = time.time()
                enemy_health.take_damage(projectile.damage, current_time)
                projectile.add_hit_target(enemy_entity.entity_id)
                
                # 🆕 적 사망 확인 및 이벤트 발행
                if enemy_health.is_dead():
                    if self.event_bus:
                        death_event = EnemyDeathEvent(enemy_entity_id=enemy_entity.entity_id)
                        self.event_bus.publish(death_event)
                
                # 관통하지 않는 투사체 제거
                if not projectile.piercing:
                    self._expired_projectiles.append(projectile_entity)
```

## 4.3 맵 시스템 구현

[DEV-PRDv0.2의 섹션 3.2와 동일하게 유지]

## 4.4 AI 시스템 월드 좌표 적용

[DEV-PRDv0.2의 섹션 3.3과 동일하게 유지]

## 4.5 렌더링 시스템 업데이트

[DEV-PRDv0.2의 섹션 3.4와 동일하게 유지]

---

# 5. 데이터 관리 및 설정 시스템 (기존 유지)

[DEV-PRDv0.2의 섹션 4와 동일하게 유지]

---

# 6. 🆕 테스트 전략 및 품질 보장 (Testing Strategy) - 이벤트 시스템 테스트 추가

## 6.1 pytest 기반 테스트 아키텍처

### 테스트 구조 및 분류

```
tests/
├── unit/                 # 단위 테스트
│   ├── test_items.py     # pytest -m items
│   ├── test_collision.py # pytest -m collision  
│   ├── test_ai.py        # pytest -m ai
│   ├── test_balance.py   # pytest -m balance
│   ├── test_coordinates.py # pytest -m coordinates (좌표계 테스트)
│   └── 🆕 test_events.py    # pytest -m events (이벤트 시스템 테스트)
├── integration/          # 통합 테스트
│   ├── test_gameplay.py  # 전체 게임플레이 플로우
│   ├── test_systems.py   # 시스템 간 상호작용
│   ├── test_camera_systems.py # 카메라 시스템 통합 테스트
│   └── 🆕 test_event_flow.py   # 이벤트 플로우 통합 테스트
└── performance/          # 성능 테스트
    ├── test_fps.py       # FPS 성능 벤치마크
    ├── test_memory.py    # 메모리 사용량 테스트
    ├── test_coordinate_performance.py # 좌표 변환 성능 테스트
    └── 🆕 test_event_performance.py   # 이벤트 시스템 성능 테스트
```

### 🆕 이벤트 시스템 테스트

```python
# tests/unit/test_events.py
import pytest
from unittest.mock import Mock
from src.events.event_bus import EventBus, EnemyDeathEvent, EventType
from src.events.base_event import BaseEvent

@pytest.mark.events
class TestEventBus:
    
    def test_event_publishing_and_queue(self):
        """이벤트 발행 및 큐 저장 테스트"""
        # Given
        event_bus = EventBus()
        event = EnemyDeathEvent(enemy_entity_id="enemy_001")
        
        # When
        event_bus.publish(event)
        
        # Then
        assert event_bus.get_queue_size() == 1
    
    def test_subscriber_registration_and_event_handling(self):
        """구독자 등록 및 이벤트 처리 테스트"""
        # Given
        event_bus = EventBus()
        mock_subscriber = Mock()
        mock_subscriber.handle_event = Mock()
        
        # When
        event_bus.subscribe(EventType.ENEMY_DEATH, mock_subscriber)
        event = EnemyDeathEvent(enemy_entity_id="enemy_001")
        event_bus.publish(event)
        event_bus.process_events()
        
        # Then
        mock_subscriber.handle_event.assert_called_once_with(event)
        assert event_bus.get_queue_size() == 0
    
    def test_multiple_subscribers_handling(self):
        """다중 구독자 이벤트 처리 테스트"""
        # Given
        event_bus = EventBus()
        subscriber1 = Mock()
        subscriber2 = Mock()
        subscriber1.handle_event = Mock()
        subscriber2.handle_event = Mock()
        
        # When
        event_bus.subscribe(EventType.ENEMY_DEATH, subscriber1)
        event_bus.subscribe(EventType.ENEMY_DEATH, subscriber2)
        event = EnemyDeathEvent(enemy_entity_id="enemy_001")
        event_bus.publish(event)
        event_bus.process_events()
        
        # Then
        subscriber1.handle_event.assert_called_once_with(event)
        subscriber2.handle_event.assert_called_once_with(event)
    
    def test_subscriber_exception_isolation(self):
        """구독자 예외 격리 테스트"""
        # Given
        event_bus = EventBus()
        failing_subscriber = Mock()
        working_subscriber = Mock()
        
        failing_subscriber.handle_event = Mock(side_effect=Exception("Test error"))
        working_subscriber.handle_event = Mock()
        
        # When
        event_bus.subscribe(EventType.ENEMY_DEATH, failing_subscriber)
        event_bus.subscribe(EventType.ENEMY_DEATH, working_subscriber)
        event = EnemyDeathEvent(enemy_entity_id="enemy_001")
        event_bus.publish(event)
        event_bus.process_events()  # 예외가 발생해도 처리 계속
        
        # Then
        failing_subscriber.handle_event.assert_called_once()
        working_subscriber.handle_event.assert_called_once()  # 다른 구독자는 정상 작동

@pytest.mark.events  
class TestEnemyDeathEvent:
    
    def test_enemy_death_event_creation(self):
        """적 사망 이벤트 생성 테스트"""
        # Given
        enemy_id = "enemy_123"
        
        # When
        event = EnemyDeathEvent(enemy_entity_id=enemy_id)
        
        # Then
        assert event.enemy_entity_id == enemy_id
        assert event.event_type == EventType.ENEMY_DEATH
        assert event.timestamp is not None
    
    def test_enemy_death_event_validation(self):
        """적 사망 이벤트 데이터 검증 테스트"""
        # Given & When & Then
        with pytest.raises(AssertionError):
            EnemyDeathEvent(enemy_entity_id="")  # 빈 문자열
        
        with pytest.raises(AssertionError):  
            EnemyDeathEvent(enemy_entity_id=None)  # None 값

# tests/integration/test_event_flow.py
@pytest.mark.integration
class TestEventFlow:
    
    def test_projectile_enemy_death_event_flow(self):
        """투사체-적 사망 이벤트 플로우 통합 테스트"""
        # Given: 통합 환경 설정
        entity_manager = EntityManager()
        event_bus = EventBus()
        
        projectile_system = ProjectileSystem(event_bus=event_bus)
        experience_system = ExperienceSystem()
        cleanup_system = EntityCleanupSystem()
        
        # 이벤트 구독 설정
        event_bus.subscribe(EventType.ENEMY_DEATH, experience_system)
        event_bus.subscribe(EventType.ENEMY_DEATH, cleanup_system)
        
        # 테스트 엔티티 생성
        enemy_entity = self._create_test_enemy(entity_manager)
        
        # When: 적 사망 이벤트 발생
        death_event = EnemyDeathEvent(enemy_entity_id=enemy_entity.entity_id)
        event_bus.publish(death_event)
        event_bus.process_events()
        
        # Then: 모든 구독자가 올바르게 처리
        assert experience_system.total_experience > 0  # 경험치 증가
        assert not entity_manager.has_entity(enemy_entity.entity_id)  # 엔티티 제거
```

---

# 7. 🆕 개발 로드맵 및 우선순위 (Updated Development Roadmap)

## 7.1 MVP 개발 단계 (일정 수정)

### Phase 1: 핵심 인프라 구축 (2-3주) - 변경 없음

[DEV-PRDv0.2와 동일]

### 🆕 Phase 2: 이벤트 기반 게임플레이 구현 (6-7주, +3주 추가)

**목표**: 플레이어 중앙 고정 + 월드 좌표 기반 게임플레이 + 적 AI + **이벤트 시스템** + 경험치 시스템

**🎮 개발 항목**:

**Week 1-2: 좌표계 인프라 구축 (기존과 동일)**

- [ ] ICoordinateTransformer 인터페이스 설계 및 기본 구현
- [ ] CameraSystem 구현 (플레이어 중앙 고정, 월드 오프셋 관리)
- [ ] CoordinateManager 전역 관리자 구현
- [ ] 좌표계 단위 테스트 작성

**🆕 Week 3: 이벤트 시스템 구축**

- [ ] BaseEvent 추상 클래스 및 EnemyDeathEvent 구현
- [ ] EventBus 클래스 구현 (큐잉 방식)
- [ ] IEventSubscriber 인터페이스 설계
- [ ] 이벤트 시스템 단위 테스트 작성

**🆕 Week 4: ProjectileSystem 리팩토링**

- [ ] ProjectileSystem의 책임 분리 (이벤트 발행자로 역할 변경)
- [ ] 기존 직접 처리 로직 제거 (경험치, 엔티티 제거)
- [ ] 수정된 ProjectileSystem 단위 테스트
- [ ] 이벤트 발행 기능 통합 테스트

**🆕 Week 5: 옵저버 시스템들 구현**

- [ ] ExperienceSystem 구현 (EnemyDeathEvent 구독)
- [ ] ItemDropSystem 구현 (아이템 드롭 처리)
- [ ] EntityCleanupSystem 구현 (엔티티 정리)
- [ ] 각 시스템별 단위 테스트

**Week 6-7: 게임플레이 로직 및 통합**

- [ ] PlayerMovementSystem 재구현 (마우스 추적, 중앙 고정)
- [ ] MapRenderSystem 구현 (무한 스크롤 타일 배경)
- [ ] EntityRenderSystem 업데이트 (좌표 변환 적용)
- [ ] AutoAttackSystem 재구현 (월드 좌표 기반 타겟팅)
- [ ] EnemyAISystem 재구현 (월드 좌표 기반 추적/공격)
- [ ] 이벤트 플로우 통합 테스트
- [ ] 기본 UI (체력, 경험치 바)

**✅ 완료 조건**:

- ✅ **플레이어가 마우스 방향을 바라보며 화면 중앙에 고정**
- ✅ **맵이 플레이어 이동의 역방향으로 자연스럽게 움직임**  
- ✅ **카메라 경계 처리로 맵 밖으로 나가지 않음**
- ✅ **적을 자동으로 공격하여 처치 가능 (월드 좌표 기준)**
- ✅ **경험치 획득으로 레벨업 가능**
- ✅ **적 20마리 동시 존재 시 40+ FPS 유지**
- ✅ **좌표 변환 시스템이 모든 게임플레이에 올바르게 적용**
- **🆕 적 처치 시 이벤트 기반으로 경험치 획득 및 아이템 드롭 처리**
- **🆕 이벤트 시스템의 안정성 및 성능 요구사항 충족**

### Phase 3: 아이템 시스템 구현 (2-3주) - 변경 없음

**목표**: JSON 기반 아이템 + 룰 엔진 + 시너지

### Phase 4: 보스 시스템 구현 (3-4주) - 변경 없음  

**목표**: 교장선생님 보스 + 디버프 시스템

## 7.2 🆕 확장 단계 (MVP 이후)

### Phase 5: 성능 최적화 (2-3주) - 우선순위 재조정

- 좌표 변환 시스템 최적화 (배치 처리, 고급 캐싱)
- **🆕 이벤트 시스템 성능 최적화 (배치 처리, 우선순위 큐)**
- 충돌감지 시스템 → Spatial Partitioning 교체
- 렌더링 시스템 → Sprite Group 최적화 + 컬링
- 맵 렌더링 최적화 (가시 영역만 처리)
- 메모리 풀링 패턴 적용
- 성능 프로파일링 및 병목 지점 해결

[이후 Phase 6~8은 DEV-PRDv0.2와 동일]

---

# 8. 🆕 기술적 제약사항 및 위험 요소 (Updated Technical Constraints & Risks)

## 8.1 기술적 제약사항

[DEV-PRDv0.2의 섹션 7.1과 동일하게 유지]

### 🆕 이벤트 시스템 제약사항

| 제약사항 | 영향도 | 대응 방안 |
|----------|--------|-----------|
| 이벤트 처리 지연 (큐잉 방식) | 🟡 중간 | 게임 로직 특성상 1프레임 지연 허용 |
| 구독자 등록/해제 복잡성 | 🟡 중간 | 자동 등록 헬퍼 함수 제공 |
| 이벤트 처리 순서 보장 어려움 | 🟢 낮음 | 시스템 독립성 설계로 순서 의존성 제거 |

## 8.2 🆕 위험 요소 및 완화 방안

### 이벤트 시스템 위험 요소

```python
# 위험: 이벤트 루프 성능 병목
class EventPerformanceMonitor:
    """이벤트 시스템 성능 모니터링"""
    
    def __init__(self):
        self.max_events_per_frame = 100
        self.performance_threshold = 0.002  # 2ms
    
    def monitor_event_processing(self, event_bus: EventBus):
        """이벤트 처리 성능 모니터링 및 경고"""
        start_time = time.time()
        event_count = event_bus.get_queue_size()
        
        if event_count > self.max_events_per_frame:
            print(f"Warning: High event load - {event_count} events queued")
        
        # 처리 시간 측정 (process_events 호출 후)
        processing_time = time.time() - start_time
        if processing_time > self.performance_threshold:
            print(f"Warning: Event processing took {processing_time:.3f}s")
```

**위험**: 시스템 간 이벤트 의존성 복잡화

**완화 방안**:
1. **이벤트 타입 최소화**: 꼭 필요한 이벤트만 정의
2. **구독자 독립성**: 다른 구독자의 존재를 가정하지 않는 설계
3. **이벤트 데이터 최소화**: entity_id만 전달하고 상세 데이터는 조회
4. **테스트 커버리지**: 이벤트 플로우 통합 테스트 90% 이상

### 개발 복잡성 위험 요소

[DEV-PRDv0.2의 섹션 7.2와 동일하게 유지, 이벤트 관련 내용 추가]

**위험**: 이벤트 기반 디버깅 어려움

**완화 방안**:
1. **이벤트 로깅**: 모든 이벤트 발행/처리를 로그로 기록
2. **디버그 모드**: 실시간 이벤트 플로우 시각화
3. **단위 테스트**: 이벤트별 단위 테스트로 격리된 검증
4. **통합 테스트**: 전체 이벤트 플로우 검증

---

# 9. 성공 지표 및 검증 방법 (Success Metrics) - 이벤트 시스템 지표 추가

## 9.1 기술적 성공 지표

### 성능 지표

- **FPS 안정성**: 적 50마리 + 투사체 100개 상황에서 40+ FPS 유지율 95% 이상
- **메모리 사용량**: 게임 실행 30분 후 메모리 증가량 50MB 이하
- **로딩 시간**: 게임 시작부터 플레이 가능까지 3초 이내
- **좌표 변환 성능**: 1000개 엔티티 좌표 변환을 16ms 이내 처리
- **🆕 이벤트 처리 성능**: 100개 이벤트 처리를 2ms 이내 완료

### 품질 지표  

- **테스트 커버리지**: 핵심 게임 로직 90% 이상
- **버그 밀도**: 플레이 10분당 크래시 0건, 심각한 버그 1건 이하
- **크로스 플랫폼**: Windows, macOS에서 동일한 게임플레이 경험
- **좌표 정확성**: 좌표 변환 오차 0.1픽셀 이내
- **🆕 이벤트 일관성**: 이벤트 처리 누락 0%, 중복 처리 0%

### 🆕 시스템 아키텍처 지표

- **결합도 감소**: ProjectileSystem과 다른 시스템 간 직접 의존성 0개
- **확장성**: 새로운 적 사망 관련 기능 추가 시 기존 시스템 수정 불필요
- **이벤트 처리 안정성**: 구독자 예외 발생 시에도 다른 구독자 정상 동작

---

# 10. 부록 (Appendix)

## 10.1 참고 문서

- [기획 PRD](./PRD.md) - 게임 컨셉 및 기획 요구사항
- [DEV-PRDv0.2](./DEV-PRDv0.2.md) - 이전 기술 설계 문서
- [게임 의존성](./game-dependency.md) - Python 라이브러리 스택  
- [아키텍트 인터뷰](./interview/25-08-07-아키텍쳐_기술_인터뷰.md) - 설계 결정 과정
- [플레이어 이동 아키텍처 변경 인터뷰](./interview/25-08-07-플레이어_이동_아키텍처_변경_인터뷰.md) - 좌표계 변경 근거
- **🆕 [ProjectileSystem 옵저버 패턴 리팩토링](./interview/2025-01-12-ProjectileSystem-옵저버패턴-리팩토링.md)** - 이벤트 시스템 도입 근거

## 10.2 개발 환경 설정

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
│   │   ├── camera.py      # 카메라 시스템
│   │   ├── coordinate.py  # 좌표 변환 시스템
│   │   ├── map.py         # 맵 렌더링 시스템
│   │   ├── projectile.py  # 🆕 리팩토링된 투사체 시스템
│   │   ├── experience.py  # 🆕 경험치 시스템
│   │   ├── item_drop.py   # 🆕 아이템 드롭 시스템
│   │   └── entity_cleanup.py # 🆕 엔티티 정리 시스템
│   ├── components/    # ECS 컴포넌트들
│   ├── 🆕 events/          # 이벤트 시스템
│   │   ├── base_event.py      # 기본 이벤트 클래스
│   │   ├── event_bus.py       # 이벤트 버스 시스템
│   │   └── game_events.py     # 게임 이벤트 정의들
│   ├── data/          # 데이터 관리
│   └── ui/            # 사용자 인터페이스
├── data/              # JSON 데이터 파일들
├── tests/             # 테스트 코드
│   ├── unit/
│   │   ├── test_coordinates.py  # 좌표계 테스트
│   │   └── 🆕 test_events.py         # 이벤트 시스템 테스트
│   └── integration/
│       └── 🆕 test_event_flow.py     # 이벤트 플로우 통합 테스트
├── assets/            # 이미지, 사운드 리소스
└── docs/              # 문서화
    └── interview/     # 인터뷰 기록들
```

## 10.3 🆕 이벤트 시스템 개발 가이드라인

### 개발자 가이드라인

1. **이벤트 설계 원칙**:
   - 최소 데이터만 포함 (entity_id 위주)
   - 이벤트 타입은 IntEnum으로 정의
   - 구독자가 필요한 데이터는 EntityManager를 통해 조회

2. **구독자 구현 원칙**:
   - IEventSubscriber 인터페이스 준수
   - 다른 구독자의 존재를 가정하지 않는 독립적 설계
   - 예외 처리를 통한 안정성 보장

3. **성능 고려사항**:
   - 이벤트 처리는 게임 루프 마지막에 일괄 실행
   - 복잡한 로직은 이벤트 핸들러에서 분리
   - 이벤트 큐 크기 모니터링

### 🆕 이벤트 관련 코딩 컨벤션

```python
# 이벤트 타입: EventType enum 사용
class EventType(IntEnum):
    ENEMY_DEATH = 0

# 이벤트 클래스: 명확한 명명 + Event 접미사
class EnemyDeathEvent(BaseEvent):
    enemy_entity_id: str

# 구독자 메서드: handle_event 통일
def handle_event(self, event: BaseEvent) -> None:
    pass

# 이벤트 발행: 명시적 event 변수명
death_event = EnemyDeathEvent(enemy_entity_id=enemy_id)
self.event_bus.publish(death_event)
```

---

**문서 버전**: 0.3  
**최종 수정일**: 2025-01-12  
**주요 변경사항**: 옵저버 패턴 기반 이벤트 시스템 도입 및 ProjectileSystem 책임 분리  
**다음 검토일**: Phase 2 이벤트 시스템 구현 완료 시점