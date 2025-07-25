# 제품 요구사항 정의서 (PRD): 방과 후 생존
> **문서 버전**: 1.0
> **작성일**: 2025-07-18
> **작성자**: 게임 PM

## 1. 개요 (Overview)

### 1.1. 프로젝트 비전
본 프로젝트는 "10분 동안 아무 생각 없이 몰입하여 스트레스를 해소하는" 하이퍼 캐주얼 로그라이크 게임을 제작하는 것을 목표로 한다. 플레이어는 자동 공격의 쾌감과 매번 달라지는 아이템 조합의 재미를 통해 짧지만 강렬한 성취감을 경험한다.

### 1.2. 핵심 목표
- **플레이어 경험**: "쉬운 조작과 빠른 적응"을 통해 즉각적인 재미를 제공하고, "운과 실력이 결합된 전략적 선택"을 통해 반복 플레이의 가치를 높인다.
- **성공 지표 (MVP)**:
    - **플레이 타임**: 평균 플레이 시간이 8분 이상 도달
    - **리텐션**: D1 리텐션 20% 달성
- **기술 목표**: Python/Pygame 기반으로 안정적인 40 FPS 이상을 유지하는 프로토타입 완성

### 1.3. 타겟 플레이어
- 간단한 조작으로 짧은 시간 동안 즐길 수 있는 스낵 컬처 게임을 선호하는 사용자
- 로그라이크 장르의 "성장"과 "운빨" 요소에 재미를 느끼는 사용자

## 2. 기능 요구사항 (Functional Requirements)

### 2.1. 게임 흐름 (Game Flow)
1.  **시작**: 플레이어는 운동장 맵 중앙에서 시작한다. 캐릭터는 멈추지 않고 마우스 커서를 따라 자동 이동한다.
2.  **전투**: 캐릭터는 바라보는 방향으로 자동 공격한다.
3.  **적 등장**: 시간이 지남에 따라 다양한 종류의 적들이 화면 사방에서 등장한다.
4.  **성장**: 적을 처치하여 경험치를 획득하고 레벨업한다.
5.  **아이템 선택**: 레벨업 시, 2개의 아이템이 무작위로 제시되며 플레이어는 하나를 선택하여 획득 또는 강화한다.
6.  **보스전**: 1분 30초마다 보스가 등장하며, 특수 패턴과 디버프 미션을 동반한다.
7.  **종료**: 플레이어 캐릭터의 체력이 0이 되면 게임이 종료되고, 생존 시간이 기록된다.

### 2.2. 플레이어 캐릭터
- **조작**: 마우스 커서 위치에 따라 이동 방향 결정. 공격은 자동.
- **아이템 슬롯**: 총 6개. 한 번 획득한 아이템은 버릴 수 없다.

### 2.3. 아이템 시스템

#### 2.3.1. 아이템 목록
| 구분 | 아이템명 | 설명 | 강화 효과 |
| :--- | :--- | :--- | :--- |
| **무기** | 축구공 | 주변 적에게 튕기는 투사체 발사 | 데미지, 튕기는 횟수, 투사체 크기 증가 |
| | 농구공 | 적을 관통하는 빠른 투사체 발사 | 데미지, 관통 횟수, 투사체 속도 증가 |
| | 야구 배트 | 캐릭터 주변을 휘둘러 근접 피해 | 데미지, 공격 범위, 공격 속도 증가 |
| **능력** | 축구화 | 이동 속도 증가 | 이동 속도 증가량 상승, 최대 체력 상승 |
| | 농구화 | 짧은 시간 점프하여 무적 및 적 통과 | 무적 시간 증가, 쿨타임 감소 |
| | 홍삼 | 체력 대량 회복 (획득 시 1회) | 회복량 증가 |
| | 우유 | 체력 소량 회복 (획득 시 1회) | 회복량 증가 |

#### 2.3.2. 아이템 시너지 (Synergy)
- 특정 아이템 조합 시 추가 효과가 발동된다. 이는 플레이어의 아이템 선택에 전략적 깊이를 더한다.
- **(예시) 시너지 리스트:**
    - **축구화 + 축구공**: 축구공의 데미지 15% 증가
    - **야구 배트 + 농구화**: 점프 후 착지 시, 주변에 충격파를 발생시켜 적을 밀어냄
    - *(추가 시너지 조합은 밸런스 테스트를 거쳐 확정)*

### 2.4. 난이도 및 적 설계

#### 2.4.1. 점진적 난이도 상승
- 시간 경과에 따라 모든 적의 등장 빈도, 이동 속도, 체력이 점진적으로 증가한다.

#### 2.4.2. 디버프 & 미션 시스템
- **목표**: 화면의 오브젝트 수를 과도하게 늘리지 않으면서 난이도를 조절하고, 플레이어에게 새로운 도전 과제를 제시한다.
- **발동 시점**: 보스 등장과 함께 발동된다.
- **개념**:
    - 디버프는 특정 무기 빌드에 대한 카운터로 작용한다. (가위-바위-보 상성)
    - 디버프를 해제하려면 보스를 처치하는 것과 별개로, 주어진 **미션**을 완료해야 한다.
    - 미션이 성공 할 때까지 보스를 처치해도 디버프는 지속된다. (시점과 상관없이 성공할 수 있는 미션만 존재한다.)
- **(예시) 디버프 & 미션 리스트:**

| 디버프 | 카운터 대상 | 미션 내용 |
| :--- | :--- | :--- |
| **과중력** (이동 속도 50% 감소) | 기동성 빌드 | 맵 끝에서 끝까지 왕복 |
| **무기력** (공격 속도 50% 감소) | 빠른 공속 빌드 | 10초 동안 적을 한 대도 공격하지 않기 |
| **유리몸** (받는 데미지 2배 증가) | 근접/탱커 빌드 | 20초 동안 피격 당하지 않기 |

### 2.5. 보스전: 교장 선생님

#### 2.5.1. 등장 조건
- 게임 시간 기준, 1분 30초마다 주기적으로 등장한다.

#### 2.5.2. 핵심 패턴 (MVP 버전)
1.  **등장 패턴: 훈화 말씀 (알파)**
    - **효과**: 등장과 즉시 발동. 화면 전체에 영향을 미치는 피할 수 없는 공격.
    - **피해**: 데미지 없음.
    - **부과 효과**: 플레이어에게 1초간 짧은 스턴 및 상기 기술된 디버프+미션 중 하나를 무작위로 부여한다.

2.  **주요 공격: 훈화 말씀 (베타)**
    - **효과**: 교장 선생님 주변에 강력한 범위(AoE) 공격을 가한다.
    - **특징**: 공격 범위, 데미지, 예고 시간, 지속 시간이 무작위로 결정된다.
        - **(규칙)**: 범위가 넓을수록 <-> 예고 시간 길고, 데미지 낮고, 지속 시간 짧음
        - **(규칙)**: 범위가 좁을수록 <-> 예고 시간 짧고, 데미지 높고, 지속 시간 길음
    - **시각적 신호 (Telegraphing)**:
        - 공격 발동 전, 바닥에 공격 범위를 명확히 표시한다.
        - 범위와 위험도에 따라 시각적 표현이 달라야 한다.
            - **(예시)** 넓고 약한 공격: 크고 옅은 붉은색 원
            - **(예시)** 좁고 강한 공격: 작고 진한 붉은색 원

## 3. 기술 요구사항 (Technical Requirements)

### 3.1. 개발 환경
- **언어**: Python 3.13+
- **라이브러리**: Pygame
- **플랫폼**: PC (Windows, Mac)

### 3.2. 성능 목표
- **최소 FPS**: 40 프레임.
- **최적화**: 화면에 동시 출력되는 적, 투사체의 최대 개수를 제한하여 성능 저하를 방지한다. (구체적인 수치는 테스트 후 결정)

### 3.3. 그래픽 및 사운드
- **그래픽 스타일**: 단순하고 명확한 2D 도트 또는 벡터(SVG) 이미지.
- **사운드**: MVP 버전에서는 사운드를 포함하지 않는다.

## 4. 리스크 및 대응 방안 (Risks & Mitigation)

| 리스크 | 심각도 | 내용 | 대응 방안 |
| :--- | :--- | :--- | :--- |
| **성능 문제** | 높음 | 다수의 적/투사체로 인해 FPS가 40 이하로 저하될 가능성 | - 동시 생성 객체 수 제한<br>- 디버프 시스템을 통한 난이도 조절 |
| **밸런싱 실패** | 중간 | 특정 아이템 조합이 지나치게 강력하여 게임의 재미를 해칠 가능성 | - MVP 단계에서 시너지 조합 최소화<br>- 데이터 기반의 지속적인 밸런스 조정 |
| **개발 지연** | 낮음 | 초보 개발자의 숙련도 이슈로 인한 개발 속도 저하 | - MVP 범위 명확화<br>- 복잡한 기능(다양한 보스, 사운드)은 후속 버전으로 계획 |

## 5. 향후 계획 (Out of Scope for MVP)
- 신규 캐릭터 (운동부 종목별) 및 전용 능력 추가
- 신규 적 (과목별 선생님) 및 보스 추가
- 아이템 및 시너지 조합 확장
- 점수판 및 랭킹 시스템
- 사운드 이펙트 및 배경음악 추가
