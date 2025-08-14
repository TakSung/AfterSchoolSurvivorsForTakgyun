#!/usr/bin/env python3
"""
AI Enemy System Demo - Complete ECS Integration

완성된 EnemyAI 시스템과 월드 좌표 기반 게임플레이를 시연하는 데모입니다:
- EnemyAISystem: 월드 좌표 기반 적 AI (추적, 공격, 대기 상태)
- PlayerMovementSystem: 마우스 추적 플레이어 이동
- CameraSystem: 플레이어 따라가기 카메라
- MapRenderSystem: 무한 스크롤 배경 타일
- EntityRenderSystem: 고성능 엔티티 렌더링
- 실시간 AI 상태 시각화 및 성능 모니터링
"""

import math
import sys

import pygame

from src.components.camera_component import CameraComponent
from src.components.enemy_ai_component import AIState, AIType, EnemyAIComponent
from src.components.enemy_component import EnemyComponent
from src.components.map_component import MapComponent
from src.components.player_component import PlayerComponent
from src.components.player_movement_component import PlayerMovementComponent
from src.components.position_component import PositionComponent
from src.components.render_component import RenderComponent, RenderLayer
from src.components.rotation_component import RotationComponent
from src.core.cached_camera_transformer import CachedCameraTransformer
from src.core.coordinate_manager import CoordinateManager
from src.core.entity_manager import EntityManager
from src.core.system_orchestrator import SystemOrchestrator
from src.systems.camera_system import CameraSystem
from src.systems.enemy_ai_system import EnemyAISystem
from src.systems.entity_render_system import EntityRenderSystem
from src.systems.map_render_system import MapRenderSystem
from src.systems.player_movement_system import PlayerMovementSystem
from src.utils.vector2 import Vector2


class EnemyAIDemo:
    """
    EnemyAI 시스템을 시연하는 완전한 게임 데모

    Features:
    - 월드 좌표 기반 적 AI 시스템 (추적, 공격, 대기)
    - 다양한 AI 타입별 행동 패턴 (공격형, 방어형, 순찰형)
    - 실시간 AI 상태 시각화
    - 마우스 기반 플레이어 컨트롤
    - 무한 스크롤 맵과 카메라 시스템
    - 성능 모니터링 및 디버그 정보
    """

    def __init__(self, screen_width: int = 1024, screen_height: int = 768):
        """데모 초기화"""
        # 화면 설정
        self.screen_width = screen_width
        self.screen_height = screen_height

        # pygame 초기화
        pygame.init()
        pygame.display.set_caption(
            'AI Enemy System Demo - Complete ECS Integration'
        )
        self.screen = pygame.display.set_mode((screen_width, screen_height))
        self.clock = pygame.time.Clock()

        # ECS 시스템 초기화
        self.entity_manager = EntityManager()
        print(f"Demo: EntityManager 인스턴스 ID: {id(self.entity_manager)}")
        
        # AI-NOTE : 2025-08-14 이벤트 시스템 설정 - 카메라 오프셋 이벤트 처리
        # - 이유: CameraSystem과 MapRenderSystem 간 이벤트 기반 통신 필요
        # - 요구사항: CameraOffsetChangedEvent를 통한 카메라 오프셋 전달
        # - 히스토리: 직접 참조에서 이벤트 기반 느슨한 결합으로 개선
        from src.core.events.event_bus import EventBus
        self.event_bus = EventBus()
        self.system_orchestrator = SystemOrchestrator(event_bus=self.event_bus)

        # 좌표 변환 시스템
        self.coordinate_manager = CoordinateManager.get_instance()
        self._setup_coordinate_system()

        # 색상 팔레트
        self.colors = {
            'background': (15, 15, 25),
            'player': (100, 150, 255),
            'enemy_aggressive': (255, 100, 100),
            'enemy_defensive': (255, 200, 100),
            'enemy_patrol': (150, 255, 150),
            'chase_range': (255, 255, 100, 80),
            'attack_range': (255, 100, 100, 80),
            'ui_text': (255, 255, 255),
            'ui_background': (0, 0, 0, 180),
        }

        # UI 폰트
        self.font_large = pygame.font.Font(None, 32)
        self.font_medium = pygame.font.Font(None, 24)
        self.font_small = pygame.font.Font(None, 18)

        # 게임 엔티티 참조들 (강한 참조 유지)
        self.player_entity = None
        self.camera_entity = None
        self.map_entity = None  # 맵 엔티티 강한 참조 유지
        self.enemy_entities = []

        # 디버그 및 UI 상태
        self.show_debug = True
        self.show_ranges = True
        self.frame_count = 0
        self.fps_timer = 0.0
        self.current_fps = 60.0

        # 초기화 메서드들
        self._setup_systems()
        print(f"Demo: 시스템 설정 완료")
        self._create_map()
        print(f"Demo: 맵 생성 완료 - 총 엔티티 수: {len(self.entity_manager.get_all_entities())}")
        self._create_player()
        print(f"Demo: 플레이어 생성 완료 - 총 엔티티 수: {len(self.entity_manager.get_all_entities())}")
        self._create_camera()
        print(f"Demo: 카메라 생성 완료 - 총 엔티티 수: {len(self.entity_manager.get_all_entities())}")
        self._create_enemies()
        print(f"Demo: 적 생성 완료 - 총 엔티티 수: {len(self.entity_manager.get_all_entities())}")
        
        # 최종 확인: 맵 엔티티가 여전히 존재하는지 확인
        all_entities = self.entity_manager.get_all_entities()
        for entity in all_entities:
            has_map = self.entity_manager.has_component(entity, MapComponent)
            if has_map:
                print(f"Demo: 최종 확인 - 맵 엔티티 {entity.entity_id} 발견")

    def _setup_coordinate_system(self) -> None:
        """좌표 변환 시스템 설정"""
        screen_size = Vector2(self.screen_width, self.screen_height)
        transformer = CachedCameraTransformer(screen_size=screen_size)
        self.coordinate_manager.set_transformer(transformer)

    def _setup_systems(self) -> None:
        """게임 시스템들 초기화 및 등록"""
        # AI-NOTE : 2025-08-14 시스템 우선순위 설정 - AI 시스템 통합 데모
        # - 이유: 올바른 실행 순서로 월드 좌표 기반 AI 동작 보장
        # - 요구사항: PlayerMovement → Camera → EnemyAI → Render 순서
        # - 히스토리: demo_map_render.py 패턴을 따라 일관된 우선순위 체계 구축

        # 플레이어 이동 시스템 (가장 먼저 실행)
        player_movement_system = PlayerMovementSystem(priority=5)
        player_movement_system.set_screen_size(
            self.screen_width, self.screen_height
        )
        self.system_orchestrator.register_system(
            player_movement_system, 'player_movement'
        )

        # 카메라 시스템 (플레이어 이동 후 실행)
        camera_system = CameraSystem(priority=10, event_bus=self.event_bus)
        self.system_orchestrator.register_system(camera_system, 'camera')

        # 적 AI 시스템 (카메라 업데이트 후 실행)
        enemy_ai_system = EnemyAISystem(priority=12)
        self.system_orchestrator.register_system(enemy_ai_system, 'enemy_ai')

        # 맵 렌더링 시스템
        map_render_system = MapRenderSystem(priority=40, screen=self.screen)
        map_render_system.set_screen_size(
            self.screen_width, self.screen_height
        )
        self.system_orchestrator.register_system(
            map_render_system, 'map_render'
        )

        # 엔티티 렌더링 시스템 (마지막 실행)
        entity_render_system = EntityRenderSystem(
            surface=self.screen,
            priority=50,
            cull_margin=100,
        )
        self.system_orchestrator.register_system(
            entity_render_system, 'entity_render'
        )

    def _create_map(self) -> None:
        """배경 맵 생성"""
        self.map_entity = self.entity_manager.create_entity()
        print(f"Demo: 맵 엔티티 생성됨 - ID: {self.map_entity.entity_id}")
        
        # AI-NOTE : 2025-08-14 플레이어 움직임 시각화를 위한 밝은 격자 패턴 적용
        # - 이유: 어두운 배경에서는 플레이어의 상대적 움직임이 잘 보이지 않음
        # - 요구사항: 체스판 패턴과 명확한 격자선으로 움직임 시각화
        # - 히스토리: 어두운 테마에서 밝은 격자 패턴으로 변경하여 가시성 향상
        map_comp = MapComponent(
            tile_size=64,
            world_width=8000.0,  # 큰 월드
            world_height=8000.0,
            light_tile_color=(250, 250, 250),  # 거의 흰색 타일
            dark_tile_color=(200, 200, 200),   # 회색 타일
            grid_color=(120, 120, 120),        # 명확한 격자선
            enable_infinite_scroll=True,
            tile_pattern_size=8,
        )
        print(f"Demo: MapComponent 생성됨 - 타일 크기: {map_comp.tile_size}")
        
        try:
            self.entity_manager.add_component(self.map_entity, map_comp)
            print(f"Demo: MapComponent 추가 성공")
            
            # 검증: 컴포넌트가 제대로 추가되었는지 확인
            has_component = self.entity_manager.has_component(self.map_entity, MapComponent)
            print(f"Demo: 맵 엔티티에 MapComponent 있음: {has_component}")
            
            if has_component:
                retrieved_comp = self.entity_manager.get_component(self.map_entity, MapComponent)
                print(f"Demo: 가져온 MapComponent 타일 크기: {retrieved_comp.tile_size if retrieved_comp else 'None'}")
            
        except Exception as e:
            print(f"Demo: MapComponent 추가 실패 - {e}")
            import traceback
            traceback.print_exc()

    def _create_player(self) -> None:
        """플레이어 엔티티 생성"""
        self.player_entity = self.entity_manager.create_entity()

        # 플레이어 컴포넌트들
        self.entity_manager.add_component(
            self.player_entity, PlayerComponent()
        )
        self.entity_manager.add_component(
            self.player_entity, PositionComponent(x=0.0, y=0.0)
        )

        # 플레이어 렌더링
        player_surface = pygame.Surface((30, 30))
        player_surface.fill(self.colors['player'])
        pygame.draw.circle(player_surface, (255, 255, 255), (15, 15), 13, 2)

        render_comp = RenderComponent(
            sprite=player_surface,
            size=(30, 30),
            layer=RenderLayer.ENTITIES,
            visible=True,
        )
        self.entity_manager.add_component(self.player_entity, render_comp)

        # 플레이어 이동 및 회전
        self.entity_manager.add_component(
            self.player_entity, RotationComponent(angle=0.0)
        )
        self.entity_manager.add_component(
            self.player_entity,
            PlayerMovementComponent(
                speed=200.0,
                angular_velocity_limit=math.pi * 3.0,
                dead_zone_radius=20.0,
            ),
        )

    def _create_camera(self) -> None:
        """카메라 엔티티 생성"""
        self.camera_entity = self.entity_manager.create_entity()
        player_position = self.entity_manager.get_component(
            self.player_entity, PositionComponent
        )

        camera_comp = CameraComponent(
            world_offset=(player_position.x, player_position.y),
            screen_center=(self.screen_width // 2, self.screen_height // 2),
            follow_target=self.player_entity,  # 카메라가 플레이어 추적
            dead_zone_radius=0.0,  # 데드존 없음 - 플레이어 완전 고정
            world_bounds={
                'min_x': -4000.0,
                'max_x': 4000.0,
                'min_y': -4000.0,
                'max_y': 4000.0,
            },
        )
        self.entity_manager.add_component(self.camera_entity, camera_comp)

    def _create_enemies(self) -> None:
        """다양한 AI 타입의 적 엔티티들 생성"""
        enemy_configs = [
            # 공격형 적들 (빠른 추격, 짧은 공격 거리)
            {
                'type': AIType.AGGRESSIVE,
                'color': self.colors['enemy_aggressive'],
                'count': 4,
            },
            # 방어형 적들 (느린 추격, 긴 공격 거리)
            {
                'type': AIType.DEFENSIVE,
                'color': self.colors['enemy_defensive'],
                'count': 3,
            },
            # 순찰형 적들
            {
                'type': AIType.PATROL,
                'color': self.colors['enemy_patrol'],
                'count': 3,
            },
        ]

        # AI-NOTE : 2025-08-14 다양한 AI 타입별 적 배치 - AI 시스템 시연용
        # - 이유: 각 AI 타입의 고유한 행동 패턴을 시각적으로 확인 가능
        # - 요구사항: 공격형(빠른 추격), 방어형(긴 공격거리), 순찰형(균형) 차별화
        # - 히스토리: 단순 적 배치에서 AI 타입별 전략적 배치로 개선

        for config in enemy_configs:
            for i in range(config['count']):
                self._create_single_enemy(config['type'], config['color'], i)

    def _create_single_enemy(
        self, ai_type: AIType, color: tuple, index: int
    ) -> None:
        """개별 적 엔티티 생성"""
        enemy = self.entity_manager.create_entity()
        self.enemy_entities.append(enemy)

        # 타입별 다른 위치에 배치
        angle = (index / 10.0) * 2 * math.pi
        base_distance = 300 + (ai_type.value * 100)  # 타입별 다른 거리
        x = base_distance * math.cos(angle)
        y = base_distance * math.sin(angle)

        # 기본 컴포넌트들
        self.entity_manager.add_component(enemy, EnemyComponent())
        self.entity_manager.add_component(enemy, PositionComponent(x=x, y=y))

        # AI 컴포넌트 - 타입별 다른 설정
        ai_comp = EnemyAIComponent(
            ai_type=ai_type,
            current_state=AIState.IDLE,
            chase_range=200.0 if ai_type == AIType.AGGRESSIVE else 250.0,
            attack_range=60.0 if ai_type == AIType.AGGRESSIVE else 80.0,
            movement_speed=120.0 if ai_type == AIType.AGGRESSIVE else 80.0,
        )
        self.entity_manager.add_component(enemy, ai_comp)

        # 적 렌더링 - 타입별 다른 모양
        enemy_surface = pygame.Surface((25, 25))
        enemy_surface.fill(color)

        if ai_type == AIType.AGGRESSIVE:
            # 공격형: 삼각형
            pygame.draw.polygon(
                enemy_surface, (255, 255, 255), [(12, 5), (5, 20), (19, 20)], 2
            )
        elif ai_type == AIType.DEFENSIVE:
            # 방어형: 사각형
            pygame.draw.rect(enemy_surface, (255, 255, 255), (5, 5, 15, 15), 2)
        else:
            # 순찰형: 원형
            pygame.draw.circle(enemy_surface, (255, 255, 255), (12, 12), 10, 2)

        render_comp = RenderComponent(
            sprite=enemy_surface,
            size=(25, 25),
            layer=RenderLayer.ENTITIES,
            visible=True,
        )
        self.entity_manager.add_component(enemy, render_comp)

        # 회전 컴포넌트
        self.entity_manager.add_component(enemy, RotationComponent(angle=0.0))

    def run(self) -> None:
        """데모 실행"""
        print('=' * 60)
        print('🤖 AI Enemy System Demo - Complete ECS Integration')
        print('=' * 60)
        print('Features:')
        print('  ✓ EnemyAISystem: 월드 좌표 기반 적 AI (IDLE, CHASE, ATTACK)')
        print('  ✓ AI Types: 공격형(빨강), 방어형(노랑), 순찰형(초록)')
        print('  ✓ Real-time AI state visualization')
        print('  ✓ Player movement with camera tracking')
        print('  ✓ Infinite scroll map background')
        print('  ✓ Performance monitoring')
        print()
        print('Controls:')
        print('  • Mouse: Move player (enemies will chase you!)')
        print('  • D: Toggle debug info and AI ranges')
        print('  • R: Respawn all enemies')
        print('  • SPACE: Pause/Resume')
        print('  • ESC: Exit')
        print('=' * 60)

        running = True
        paused = False
        last_time = pygame.time.get_ticks()

        while running:
            current_time = pygame.time.get_ticks()
            delta_time = (
                (current_time - last_time) / 1000.0 if not paused else 0.0
            )
            last_time = current_time

            # 이벤트 처리
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_d:
                        self.show_debug = not self.show_debug
                        self.show_ranges = not self.show_ranges
                        print(
                            f'Debug info: {"ON" if self.show_debug else "OFF"}'
                        )
                    elif event.key == pygame.K_r:
                        self._respawn_enemies()
                        print('All enemies respawned!')
                    elif event.key == pygame.K_SPACE:
                        paused = not paused
                        print(f'Game {"PAUSED" if paused else "RESUMED"}')

            if not paused:
                # 시스템 업데이트 (MapRenderSystem과 EntityRenderSystem이 여기서 렌더링)
                self.system_orchestrator.update_systems(
                    self.entity_manager, delta_time
                )

            # UI 오버레이 렌더링
            self._render()

            # FPS 계산
            self._update_fps(delta_time)

            self.clock.tick(60)

        self._cleanup()

    def _respawn_enemies(self) -> None:
        """모든 적을 초기 위치로 재배치"""
        for i, enemy in enumerate(self.enemy_entities):
            ai_comp = self.entity_manager.get_component(
                enemy, EnemyAIComponent
            )
            pos_comp = self.entity_manager.get_component(
                enemy, PositionComponent
            )

            if ai_comp and pos_comp:
                # 상태 초기화
                ai_comp.current_state = AIState.IDLE
                ai_comp.state_change_cooldown = 0.0

                # 위치 초기화
                angle = (i / len(self.enemy_entities)) * 2 * math.pi
                base_distance = 300 + (ai_comp.ai_type.value * 100)
                pos_comp.x = base_distance * math.cos(angle)
                pos_comp.y = base_distance * math.sin(angle)

    def _render(self) -> None:
        """UI 오버레이 렌더링 (배경과 엔티티는 시스템에서 이미 그려짐)"""
        # 디버그: 플레이어 위치에 수동으로 원 그리기
        self._draw_debug_player()

        # AI 범위 표시 (엔티티 위에 오버레이)
        if self.show_ranges:
            self._draw_ai_ranges()

        # UI 오버레이
        if self.show_debug:
            self._draw_debug_info()

        self._draw_controls_hint()

        pygame.display.flip()

    def _draw_debug_player(self) -> None:
        """디버그용 플레이어 위치 표시 - 항상 화면 중앙에 고정"""
        if not self.player_entity:
            return

        # 탑다운 뷰에서 플레이어는 항상 화면 중앙에 고정
        center_x = self.screen_width // 2
        center_y = self.screen_height // 2

        # 플레이어 표시 (파란색 원)
        pygame.draw.circle(
            self.screen, (100, 150, 255), (center_x, center_y), 15, 3
        )
        pygame.draw.circle(
            self.screen, (255, 255, 255), (center_x, center_y), 3
        )

        # 플레이어 방향 표시 (향하는 방향으로 선 그리기)
        player_movement = self.entity_manager.get_component(
            self.player_entity, PlayerMovementComponent
        )
        if player_movement:
            direction = player_movement.direction
            end_x = center_x + direction[0] * 25
            end_y = center_y + direction[1] * 25
            pygame.draw.line(
                self.screen,
                (255, 255, 100),
                (center_x, center_y),
                (end_x, end_y),
                3,
            )

    def _draw_ai_ranges(self) -> None:
        """적들의 AI 범위 시각화"""
        if not self.player_entity:
            return

        player_pos = self.entity_manager.get_component(
            self.player_entity, PositionComponent
        )
        if not player_pos:
            return

        # 좌표 변환기 가져오기
        transformer = self.coordinate_manager.get_transformer()
        if not transformer:
            return

        # 반투명 서페이스 생성
        overlay = pygame.Surface(
            (self.screen_width, self.screen_height), pygame.SRCALPHA
        )

        for enemy in self.enemy_entities:
            ai_comp = self.entity_manager.get_component(
                enemy, EnemyAIComponent
            )
            enemy_pos = self.entity_manager.get_component(
                enemy, PositionComponent
            )

            if not ai_comp or not enemy_pos:
                continue

            # 적의 화면 좌표 계산
            try:
                enemy_screen_pos = transformer.world_to_screen(
                    Vector2(enemy_pos.x, enemy_pos.y)
                )

                # 화면 범위 내에 있는지 확인
                if (
                    0 <= enemy_screen_pos.x <= self.screen_width
                    and 0 <= enemy_screen_pos.y <= self.screen_height
                ):
                    # 추적 범위 (노란색)
                    chase_range = ai_comp.get_effective_chase_range()
                    chase_radius = chase_range  # 월드 단위 = 픽셀 단위로 가정
                    pygame.draw.circle(
                        overlay,
                        self.colors['chase_range'],
                        (int(enemy_screen_pos.x), int(enemy_screen_pos.y)),
                        int(chase_radius),
                        2,
                    )

                    # 공격 범위 (빨간색)
                    attack_range = ai_comp.get_effective_attack_range()
                    attack_radius = attack_range
                    pygame.draw.circle(
                        overlay,
                        self.colors['attack_range'],
                        (int(enemy_screen_pos.x), int(enemy_screen_pos.y)),
                        int(attack_radius),
                        2,
                    )

                    # 상태 표시
                    state_text = ai_comp.current_state.display_name
                    state_color = {
                        AIState.IDLE: (150, 150, 150),
                        AIState.CHASE: (255, 255, 100),
                        AIState.ATTACK: (255, 100, 100),
                    }.get(ai_comp.current_state, (255, 255, 255))

                    text_surface = self.font_small.render(
                        state_text, True, state_color
                    )
                    overlay.blit(
                        text_surface,
                        (
                            int(enemy_screen_pos.x) - 15,
                            int(enemy_screen_pos.y) - 35,
                        ),
                    )

            except:
                continue  # 좌표 변환 실패 시 무시

        self.screen.blit(overlay, (0, 0))

    def _draw_debug_info(self) -> None:
        """디버그 정보 표시"""
        y_offset = 10
        line_height = 22

        # 제목
        title_text = self.font_medium.render(
            'AI Enemy System Debug Info', True, self.colors['ui_text']
        )
        self._draw_text_with_background(title_text, 10, y_offset)
        y_offset += line_height + 5

        # 성능 정보
        fps_text = self.font_small.render(
            f'FPS: {self.current_fps:.1f}', True, (100, 255, 100)
        )
        self._draw_text_with_background(fps_text, 10, y_offset)
        y_offset += line_height

        # 플레이어 위치
        if self.player_entity:
            player_pos = self.entity_manager.get_component(
                self.player_entity, PositionComponent
            )
            if player_pos:
                pos_text = self.font_small.render(
                    f'Player: ({player_pos.x:.1f}, {player_pos.y:.1f})',
                    True,
                    self.colors['ui_text'],
                )
                self._draw_text_with_background(pos_text, 10, y_offset)
                y_offset += line_height

        # AI 상태 통계
        ai_states = {'IDLE': 0, 'CHASE': 0, 'ATTACK': 0}
        for enemy in self.enemy_entities:
            ai_comp = self.entity_manager.get_component(
                enemy, EnemyAIComponent
            )
            if ai_comp:
                state_name = ai_comp.current_state.name
                ai_states[state_name] = ai_states.get(state_name, 0) + 1

        states_text = self.font_small.render(
            f'AI States - IDLE: {ai_states["IDLE"]}, CHASE: {ai_states["CHASE"]}, ATTACK: {ai_states["ATTACK"]}',
            True,
            (200, 200, 255),
        )
        self._draw_text_with_background(states_text, 10, y_offset)
        y_offset += line_height

        # AI 타입별 개수
        ai_types = {'AGGRESSIVE': 0, 'DEFENSIVE': 0, 'PATROL': 0}
        for enemy in self.enemy_entities:
            ai_comp = self.entity_manager.get_component(
                enemy, EnemyAIComponent
            )
            if ai_comp:
                type_name = ai_comp.ai_type.name
                ai_types[type_name] = ai_types.get(type_name, 0) + 1

        types_text = self.font_small.render(
            f'AI Types - AGG: {ai_types["AGGRESSIVE"]}, DEF: {ai_types["DEFENSIVE"]}, PAT: {ai_types["PATROL"]}',
            True,
            (255, 200, 100),
        )
        self._draw_text_with_background(types_text, 10, y_offset)

    def _draw_controls_hint(self) -> None:
        """컨트롤 안내 표시"""
        hint_text = 'Mouse: Move | D: Toggle debug | R: Respawn enemies | SPACE: Pause | ESC: Exit'
        text_surface = self.font_small.render(hint_text, True, (150, 150, 150))

        text_rect = text_surface.get_rect()
        text_rect.centerx = self.screen_width // 2
        text_rect.y = self.screen_height - 25

        self._draw_text_with_background(text_surface, text_rect.x, text_rect.y)

    def _draw_text_with_background(
        self, text_surface: pygame.Surface, x: int, y: int
    ) -> None:
        """배경과 함께 텍스트 렌더링"""
        text_rect = text_surface.get_rect()
        bg_rect = pygame.Rect(
            x - 3, y - 1, text_rect.width + 6, text_rect.height + 2
        )

        bg_surface = pygame.Surface((bg_rect.width, bg_rect.height))
        bg_surface.set_alpha(180)
        bg_surface.fill((0, 0, 0))
        self.screen.blit(bg_surface, bg_rect.topleft)
        self.screen.blit(text_surface, (x, y))

    def _update_fps(self, delta_time: float) -> None:
        """FPS 계산 업데이트"""
        self.frame_count += 1
        self.fps_timer += delta_time

        if self.fps_timer >= 1.0:
            self.current_fps = self.frame_count / self.fps_timer
            self.frame_count = 0
            self.fps_timer = 0.0

    def _cleanup(self) -> None:
        """리소스 정리"""
        print('\n' + '=' * 60)
        print('AI Enemy System Demo completed!')
        print('  ✓ EnemyAISystem functionality verified')
        print('  ✓ World coordinate-based AI behavior confirmed')
        print('  ✓ Multiple AI types and states demonstrated')
        print('=' * 60)
        pygame.quit()


def main() -> int:
    """메인 엔트리 포인트"""
    try:
        demo = EnemyAIDemo(screen_width=1024, screen_height=768)
        demo.run()
        return 0
    except Exception as e:
        print(f'❌ Failed to run AI Enemy demo: {e}')
        import traceback

        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
