# ECS 아키텍처 리팩토링 PRD - 방과 후 생존 게임

## Overview

현재 방과 후 생존 게임의 ECS 아키텍처를 **책임 분리**와 **다형성** 원칙에 따라 리팩토링하는 프로젝트입니다. 

### 해결할 문제점
- **인터페이스 부재**: 통일된 API 없어 디버깅 소요 증가
- **EntityManager 단일책임 위반**: 각 객체별 다른 조합을 하나의 클래스에서 관리
- **기능별 응집도 저하**: 객체별 특성이 분산되어 응집성 부족  
- **이벤트/매니저 개념 혼재**: 계층 경계 불분명으로 코드 이해도 저하

### 목표 달성 효과
- **개발 생산성 향상**: 통일된 인터페이스로 디버깅 시간 단축
- **유지보수성 개선**: 명확한 책임 분리로 코드 이해도 향상
- **확장성 확보**: Strategy 패턴과 Manager 인터페이스로 런타임 변경 가능
- **테스트 용이성**: Mock 객체 주입으로 단위 테스트 격리

## Core Features

### 1. 영향도 기반 리팩토링 순서
**Entity → Component → System → Manager/Event/Strategy** 순서로 진행하여 연쇄 변경 최소화

### 2. SharedEventQueue 기반 Producer-Consumer 시스템
- 기존 EventBus 대신 타입 안전한 직접 연결 방식
- Producer와 Consumer가 SharedEventQueue를 공유
- 중간 등록/전송 단계 제거로 성능 향상

### 3. Manager 인터페이스 추상화
- IEnemyManager, IWeaponManager 등 특화된 관리자 인터페이스
- DTO 기반 타입 안전한 데이터 전송
- 정적 팩토리 메서드로 구현체 숨김

### 4. Strategy 패턴 적용 System
- IAttackStrategy, ISpawnStrategy 등 런타임 교체 가능한 전략
- System이 EntityManager 직접 접근 제거
- Manager + Strategy + EventProducer 조합으로 동작

### 5. 순수 EntityManager CRUD
- 특수 생성/관리 로직 제거
- 순수 CRUD 기능만 제공
- 다른 Manager는 EntityManager를 활용

## User Experience

### 개발자 경험 (Developer Experience)
- **통일된 API**: 모든 Manager가 동일한 인터페이스 패턴 제공
- **명확한 책임 분리**: 각 계층의 역할이 명확하여 코드 이해 용이
- **TDD 지원**: 인터페이스 기반으로 테스트 우선 개발 가능

### 핵심 개발 플로우
1. **Interface First**: 인터페이스 정의로 시작
2. **DTO 기반 통신**: 타입 안전한 데이터 전송
3. **Strategy 교체**: 런타임에 행동 변경 가능
4. **Event 기반 통신**: 시스템 간 느슨한 결합

## Technical Architecture

### 폴더 구조 재편성
```
src/
├── ecs/                          # ECS Framework (최하위 계층)
│   ├── entity.py, component.py, system.py
│   └── component_registry.py
├── managers/                     # 특화된 도메인 관리자들
│   ├── i_entity_manager.py       # 인터페이스들
│   ├── entity/                   # EntityManager 구현체들
│   ├── enemy/                    # EnemyManager 구현체들
│   └── weapon/                   # WeaponManager 구현체들
├── systems/                      # 게임 로직 + 전략 패턴
│   ├── strategies/               # 전략 패턴 구현체들
│   │   ├── attack/, spawn/, movement/
│   │   └── coordinate_transform/
│   └── events/                   # 이벤트 처리 시스템들
├── events/                       # Producer-Consumer 이벤트 시스템
│   ├── core/                     # EventProducer, EventConsumer, EventTunnelManager
│   ├── types/                    # 구체적인 이벤트 타입들
│   └── consumers/                # 순수 EventConsumer
├── components/                   # 게임 컴포넌트들
│   ├── core/, gameplay/, systems/
├── dto/                          # 데이터 전송 객체들
│   ├── creation/, update/, query/
└── utils/, factories/, orchestration/, config/
```

### 핵심 아키텍처 패턴
- **Producer-Consumer**: SharedEventQueue 기반 이벤트 시스템
- **Strategy Pattern**: 런타임 행동 변경 가능한 시스템
- **Interface Segregation**: 각 Manager별 특화된 인터페이스
- **Dependency Injection**: Mock 객체 주입으로 테스트 격리

## Development Roadmap

### Phase 1: Entity 리팩토링 (2일)
- Entity 클래스 인터페이스 정리
- 기존 테스트 케이스 수정
- demo-*.py 동작 확인

### Phase 2: Component 리팩토링 (3일)  
- Component ABC 인터페이스 표준화
- 컴포넌트별 검증 로직 추가
- 기존 테스트 케이스 수정

### Phase 3: System 기본 리팩토링 (3일)
- System ABC 인터페이스 정의
- 기본적인 System 구조 정리
- 기존 테스트 케이스 수정

### Phase 4A: System 인터페이스 변경 (3일)
- System.update(delta_time) 인터페이스 변경 (entity_manager 파라미터 제거)
- TDD 6단계 프로세스 적용
- 좌표변환시스템 최우선 처리

### Phase 4B: Event 시스템 (5일)
- SharedEventQueue 기반 Producer-Consumer 구현
- EventTunnelManager 구현
- 기존 EventBus 시스템 대체

### Phase 4C: Strategy 패턴 (4일)
- IAttackStrategy, ISpawnStrategy 등 인터페이스 정의
- 각 System에 Strategy 패턴 적용
- 런타임 전략 교체 기능 구현

## Logical Dependency Chain

### 영향도 기반 의존성 순서
1. **Entity** (65개 참조) - 최우선: 모든 객체의 기반
2. **Component** (109개 참조) - 두 번째: Entity에 의존 
3. **System** (26개 참조) - 세 번째: Component와 Entity 사용
4. **EntityManager** (20개 참조) - 네 번째: 상위 객체들 관리

### 시스템별 영향도 순서
1. **CoordinateManager/좌표변환시스템** (58개 참조) - 최고 영향도
2. **RenderSystem** (2개 참조) - 낮은 영향도  
3. **CollisionSystem** (2개 참조) - 낮은 영향도
4. **CameraSystem, PlayerMovementSystem** (1개 참조) - 낮은 영향도

### 단계별 검증 방법
- **Phase 1-3**: 각 단계 완료 시 demo-*.py 수정하며 동작 확인
- **Phase 4**: 각 시스템 단위테스트 완료 시마다 검증

## Risks and Mitigations

### 기술적 위험요소
- **복잡한 이벤트 시스템**: SharedEventQueue 구현 복잡성
  - *완화책*: 단계별 TDD 적용으로 점진적 구현
  
- **Strategy 패턴 과다 적용**: 불필요한 추상화로 복잡성 증가
  - *완화책*: 실제 필요한 부분만 선별적 적용

### 개발 프로세스 위험
- **테스트 케이스 불일치**: 리팩토링 중 기능 동작 변경
  - *완화책*: AI는 테스트 수정 금지, 반드시 사용자 승인 필요
  
- **종속성 분석 누락**: 통폐합 대상 식별 실패  
  - *완화책*: 매 리팩토링 시점마다 종속성 재분석

### TDD 6단계 프로세스 (Phase 4)
1. **인터페이스 구현**
2. **기존 테스트 케이스 분석** (구현체 스펙 도출)
3. **사용자 인터뷰** (시나리오/스펙 확정)
4. **테스트 구현** (인터페이스만 사용)
5. **리팩토링 진행** (테스트 기반)
6. **품질 검증** (ruff, mypy, pytest all)

## Appendix

### 인터뷰 기반 요구사항 수집
- **인터뷰 일시**: 2025-08-16
- **참여자**: 프로젝트 오너, 시니어 게임 아키텍트 (AI)
- **상세 인터뷰 기록**: docs/interview/2025-08-16-리팩토링-계획.md

### 설계 문서 참조
- **목표 아키텍처**: docs/design2.md
- **기존 아키텍처 분석**: docs/history/2025-08-17.md

### 테스트 전략
- **Phase 1-3**: 기존 테스트 케이스 수정, 단위테스트 우선
- **Phase 4**: TDD 방식, 새로운 테스트 작성
- **AI 제약**: 테스트 케이스 수정 금지, 반드시 사용자 승인 필요

### 성공 지표
- **아키텍처 품질**: 모든 System이 EntityManager 직접 접근 제거
- **코드 품질**: 타입 힌트 100% 적용, 순환 의존성 0개
- **성능 목표**: 게임 실행 시 40+ FPS 유지, Event 처리 지연시간 1ms 이하

### 총 작업 기간
**20일** (약 4주) - 영향도 기반 단계별 진행