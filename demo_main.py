"""
After School Survivors - Enhanced Pygame UI Demo

완성된 ECS 아키텍처와 pygame UI를 보여주는 향상된 데모입니다:
- GameLoop를 사용한 완전한 게임 루프
- EntityManager를 통한 엔티티 관리
- CoordinateManager와 좌표 변환 시스템
- EntityRenderSystem을 통한 고성능 렌더링
- CameraSystem과 PlayerMovementSystem 연동
- 마우스 추적 및 플레이어 중앙 고정 렌더링
- 완전한 pygame UI (FPS 카운터, 성능 통계, 컨트롤 안내)
- 게임 상태 관리 (실행/일시정지/종료)
"""

import math
import sys

import pygame

from src.components.camera_component import CameraComponent
from src.components.player_component import PlayerComponent
from src.components.player_movement_component import PlayerMovementComponent
from src.components.position_component import PositionComponent
from src.components.render_component import RenderComponent, RenderLayer
from src.components.rotation_component import RotationComponent
from src.core.cached_camera_transformer import CachedCameraTransformer
from src.core.coordinate_manager import CoordinateManager
from src.core.entity_manager import EntityManager
from src.core.game_loop import GameLoop
from src.core.game_state_manager import GameState, GameStateManager
from src.core.system_orchestrator import SystemOrchestrator
from src.systems.camera_system import CameraSystem
from src.systems.entity_render_system import EntityRenderSystem
from src.systems.player_movement_system import PlayerMovementSystem
from src.utils.vector2 import Vector2


class EnhancedGameDemo:
    """
    향상된 pygame UI 데모를 보여주는 메인 애플리케이션 클래스

    Features:
    - GameLoop 기반 완전한 게임 상태 관리
    - 고성능 ECS 아키텍처
    - 실시간 성능 모니터링 UI
    - 마우스 기반 플레이어 컨트롤
    - 좌표 변환 시스템 시각화
    """

    def __init__(self, screen_width: int = 1024, screen_height: int = 768):
        """
        초기화

        Args:
            screen_width: 창 너비
            screen_height: 창 높이
        """
        # 화면 설정
        self.screen_width = screen_width
        self.screen_height = screen_height

        # pygame 초기화
        pygame.init()
        pygame.display.set_caption('After School Survivors - Enhanced UI Demo')
        self.screen = pygame.display.set_mode((screen_width, screen_height))

        # ECS 시스템 초기화
        self.entity_manager = EntityManager()
        self.system_orchestrator = SystemOrchestrator()

        # 게임 상태 및 루프 관리
        self.game_state_manager = GameStateManager()
        self.game_loop = GameLoop(self.game_state_manager, target_fps=60)

        # 좌표 변환 시스템
        self.coordinate_manager = CoordinateManager.get_instance()

        # UI 요소들
        self.font_large = pygame.font.Font(None, 36)
        self.font_medium = pygame.font.Font(None, 24)
        self.font_small = pygame.font.Font(None, 18)

        # 색상 팔레트
        self.colors = {
            'background': (15, 15, 25),
            'ui_background': (0, 0, 0, 180),
            'ui_text': (255, 255, 255),
            'ui_accent': (100, 200, 255),
            'player': (100, 150, 255),
            'grid': (40, 40, 50),
            'entity_colors': [
                (255, 100, 100),
                (100, 255, 100),
                (100, 100, 255),
                (255, 255, 100),
                (255, 100, 255),
                (100, 255, 255),
                (255, 150, 100),
                (150, 100, 255),
                (100, 255, 150),
            ],
        }

        # 데모 엔티티 참조들
        self.player_entity = None
        self.camera_entity = None
        self.demo_entities = []

        # 초기화 메서드들 호출
        self._setup_coordinate_system()
        self._setup_systems()
        self._create_demo_entities()

        # GameLoop 콜백 설정
        self.game_loop.set_update_callback(self._update)
        self.game_loop.set_render_callback(self._render)

    def _setup_coordinate_system(self) -> None:
        """좌표 변환 시스템 설정"""
        screen_size = Vector2(self.screen_width, self.screen_height)
        transformer = CachedCameraTransformer(screen_size=screen_size)
        self.coordinate_manager.set_transformer(transformer)

    def _setup_systems(self) -> None:
        """게임 시스템들 초기화 및 등록"""
        # 카메라 시스템 (최고 우선순위 - 먼저 실행)
        camera_system = CameraSystem(priority=10)
        self.system_orchestrator.register_system(camera_system, 'camera')

        # 플레이어 이동 시스템
        player_movement_system = PlayerMovementSystem(priority=20)
        # 화면 크기 설정
        player_movement_system._screen_width = self.screen_width
        player_movement_system._screen_height = self.screen_height
        player_movement_system._screen_center = (
            self.screen_width // 2,
            self.screen_height // 2,
        )
        self.system_orchestrator.register_system(
            player_movement_system, 'player_movement'
        )

        # 엔티티 렌더링 시스템 (최저 우선순위 - 마지막 실행)
        entity_render_system = EntityRenderSystem(
            surface=self.screen,
            priority=50,
            cull_margin=75,  # 더 넓은 컬링 마진
        )
        self.system_orchestrator.register_system(
            entity_render_system, 'entity_render'
        )

    def _create_demo_entities(self) -> None:
        """데모용 엔티티들 생성"""
        # 카메라 엔티티 생성
        self.camera_entity = self.entity_manager.create_entity()
        camera_comp = CameraComponent(
            world_offset=(0.0, 0.0),
            screen_center=(self.screen_width // 2, self.screen_height // 2),
        )
        self.entity_manager.add_component(self.camera_entity, camera_comp)

        # 플레이어 엔티티 생성
        self.player_entity = self.entity_manager.create_entity()

        # 플레이어 컴포넌트들
        self.entity_manager.add_component(
            self.player_entity, PlayerComponent()
        )
        self.entity_manager.add_component(
            self.player_entity,
            PositionComponent(x=0.0, y=0.0),  # 월드 중심에 시작
        )

        # 플레이어 렌더링 (pygame Surface 사용)
        player_surface = pygame.Surface((40, 40))
        player_surface.fill(self.colors['player'])
        player_render_comp = RenderComponent(
            sprite=player_surface,
            size=(40, 40),
            layer=RenderLayer.ENTITIES,
            visible=True,
        )
        self.entity_manager.add_component(
            self.player_entity, player_render_comp
        )

        # 플레이어 회전 및 이동 컴포넌트
        self.entity_manager.add_component(
            self.player_entity, RotationComponent(angle=0.0)
        )
        self.entity_manager.add_component(
            self.player_entity,
            PlayerMovementComponent(
                speed=250.0,  # 픽셀/초
                angular_velocity_limit=math.pi * 2.0,  # 라디안/초
                dead_zone_radius=15.0,  # 픽셀
            ),
        )

        # 배경 및 테스트 엔티티들 생성
        self._create_world_entities()

        # 카메라가 플레이어를 추적하도록 설정
        camera_comp.follow_target = self.player_entity

    def _update(self, delta_time: float) -> None:
        """게임 로직 업데이트."""
        # 데모 엔티티들 회전 애니메이션
        current_time = pygame.time.get_ticks() / 1000.0

        for i, entity in enumerate(self.demo_entities):
            rotation_comp = self.entity_manager.get_component(
                entity, RotationComponent
            )
            if rotation_comp:
                # 각 엔티티마다 다른 속도로 회전
                rotation_speed = 20 + (i % 5) * 10  # 20-60 도/초
                rotation_comp.angle += rotation_speed * delta_time
                if rotation_comp.angle >= 360.0:
                    rotation_comp.angle -= 360.0

        # 시스템들 업데이트
        self.system_orchestrator.update_systems(
            self.entity_manager, delta_time
        )

    def _render(self) -> None:
        """화면 렌더링."""
        # 배경 클리어
        self.screen.fill(self.colors['background'])

        # 월드 그리드 드로잉 (좌표 시스템 시각화)
        self._draw_world_grid()

        # 엔티티 렌더링은 EntityRenderSystem에서 자동 처리
        # (시스템 오케스트레이터에서 update 시 호출됨)

        # UI 오버레이 렌더링
        self._draw_ui_overlay()

        # 화면 업데이트
        pygame.display.flip()

    def _create_world_entities(self) -> None:
        """월드에 배치될 다양한 엔티티들 생성"""
        # 원형으로 배치된 컬러풀한 엔티티들
        num_entities = 12
        radius = 200

        for i in range(num_entities):
            angle = (i / num_entities) * 2 * math.pi
            x = radius * math.cos(angle)
            y = radius * math.sin(angle)

            entity = self.entity_manager.create_entity()
            self.demo_entities.append(entity)

            # 위치
            self.entity_manager.add_component(
                entity, PositionComponent(x=x, y=y)
            )

            # 렌더링 - 다양한 크기와 색상
            size = 20 + (i % 4) * 10  # 20-50픽셀 크기
            color = self.colors['entity_colors'][
                i % len(self.colors['entity_colors'])
            ]

            surface = pygame.Surface((size, size))
            surface.fill(color)

            render_comp = RenderComponent(
                sprite=surface,
                size=(size, size),
                layer=RenderLayer.ENTITIES,
                visible=True,
            )
            self.entity_manager.add_component(entity, render_comp)

            # 회전 컴포넌트 (일부 엔티티만)
            if i % 2 == 0:
                rotation_comp = RotationComponent(angle=float(i * 30))
                self.entity_manager.add_component(entity, rotation_comp)

        # 더 멀리 떨어진 정적 엔티티들 (배경 역할)
        self._create_background_entities()

    def _create_background_entities(self) -> None:
        """배경 격자 패턴의 정적 엔티티들 생성"""
        grid_size = 150
        grid_range = 8

        for x in range(-grid_range, grid_range + 1, 2):
            for y in range(-grid_range, grid_range + 1, 2):
                if abs(x) <= 1 and abs(y) <= 1:
                    continue  # 중앙 근처는 건너뛰기

                entity = self.entity_manager.create_entity()

                # 위치
                world_x = x * grid_size
                world_y = y * grid_size
                self.entity_manager.add_component(
                    entity, PositionComponent(x=world_x, y=world_y)
                )

                # 거리에 따른 크기와 밝기 조절
                distance = math.sqrt(x * x + y * y)
                size = max(8, int(24 - distance * 2))
                brightness = max(30, int(100 - distance * 8))

                surface = pygame.Surface((size, size))
                surface.fill((brightness, brightness, brightness + 10))

                render_comp = RenderComponent(
                    sprite=surface,
                    size=(size, size),
                    layer=RenderLayer.BACKGROUND,
                    visible=True,
                )
                self.entity_manager.add_component(entity, render_comp)

    def _draw_world_grid(self) -> None:
        """월드 좌표계 시각화를 위한 그리드 드로잉."""
        if not self.player_entity:
            return

        # 플레이어 위치 가져오기
        pos_comp = self.entity_manager.get_component(
            self.player_entity, PositionComponent
        )
        if not pos_comp:
            return

        grid_size = 100
        player_x, player_y = pos_comp.x, pos_comp.y

        # 플레이어 위치를 기준으로 격자 오프셋 계산
        # 플레이어가 이동하면 격자도 반대방향으로 이동하여 시각적 피드백 제공
        grid_offset_x = int(player_x) % grid_size
        grid_offset_y = int(player_y) % grid_size

        # 세로 선들 - 플레이어 이동에 따라 격자가 움직임
        for x in range(
            -grid_offset_x, self.screen_width + grid_size, grid_size
        ):
            if 0 <= x <= self.screen_width:
                pygame.draw.line(
                    self.screen,
                    self.colors['grid'],
                    (x, 0),
                    (x, self.screen_height),
                    1,
                )

        # 가로 선들 - 플레이어 이동에 따라 격자가 움직임
        for y in range(
            -grid_offset_y, self.screen_height + grid_size, grid_size
        ):
            if 0 <= y <= self.screen_height:
                pygame.draw.line(
                    self.screen,
                    self.colors['grid'],
                    (0, y),
                    (self.screen_width, y),
                    1,
                )

        # 월드 중심점 (0,0) 표시 - 좌표 변환을 통해 실제 위치 계산
        transformer = self.coordinate_manager.get_transformer()
        if transformer:
            try:
                world_center = transformer.world_to_screen(Vector2(0, 0))
                if (
                    0 <= world_center.x <= self.screen_width
                    and 0 <= world_center.y <= self.screen_height
                ):
                    pygame.draw.circle(
                        self.screen,
                        (150, 150, 200),
                        (int(world_center.x), int(world_center.y)),
                        8,
                    )
                    # 중심점 라벨
                    center_text = self.font_small.render(
                        '(0,0)', True, (150, 150, 200)
                    )
                    self.screen.blit(
                        center_text,
                        (int(world_center.x) + 10, int(world_center.y) + 10),
                    )
            except:
                pass  # 좌표 변환 실패 시 무시

    def _draw_ui_overlay(self) -> None:
        """향상된 UI 오버레이 렌더링."""
        # 메인 제목
        title_text = self.font_large.render(
            'After School Survivors - Enhanced UI Demo',
            True,
            self.colors['ui_text'],
        )
        self._draw_text_with_background(title_text, 10, 10)

        # 성능 통계
        self._draw_performance_stats()

        # 엔티티 정보
        self._draw_entity_info()

        # 컨트롤 안내
        self._draw_controls_help()

        # 좌표 정보
        self._draw_coordinate_info()

        # 게임 상태 표시
        self._draw_game_state_indicator()

    def _draw_performance_stats(self) -> None:
        """성능 통계 렌더링."""
        stats = self.game_loop.get_performance_stats()

        perf_texts = [
            f'FPS: {stats["current_fps"]:.1f} / {stats["target_fps"]}',
            f'Delta: {stats["delta_time"] * 1000:.1f}ms',
            f'Frame: {stats["frame_count"]}',
            f'State: {stats["state"]}',
        ]

        start_y = 60
        for i, text in enumerate(perf_texts):
            surface = self.font_medium.render(
                text, True, self.colors['ui_accent']
            )
            self._draw_text_with_background(surface, 10, start_y + i * 25)

    def _draw_entity_info(self) -> None:
        """엔티티 정보 렌더링."""
        total_entities = len(self.entity_manager._entities)

        render_system = None
        for system in self.system_orchestrator._systems:
            if isinstance(system, EntityRenderSystem):
                render_system = system
                break

        entity_texts = [f'Total Entities: {total_entities}']

        if render_system:
            render_stats = render_system.get_render_stats()
            entity_texts.extend(
                [
                    f'Visible: {render_stats.get("visible_entities", 0)}',
                    f'Culled: {render_stats.get("culled_entities", 0)}',
                    f'Rotated: {render_stats.get("rotated_sprites", 0)}',
                ]
            )

        start_y = 180
        for i, text in enumerate(entity_texts):
            surface = self.font_medium.render(text, True, (150, 255, 150))
            self._draw_text_with_background(surface, 10, start_y + i * 25)

    def _draw_controls_help(self) -> None:
        """컨트롤 도움말 렌더링."""
        controls = [
            'Controls:',
            '  Mouse - Move player',
            '  ESC - Exit',
            '  SPACE - Pause/Resume',
        ]

        start_y = 300
        for i, text in enumerate(controls):
            color = self.colors['ui_text'] if i == 0 else (200, 200, 200)
            surface = self.font_small.render(text, True, color)
            self._draw_text_with_background(surface, 10, start_y + i * 20)

    def _draw_coordinate_info(self) -> None:
        """좌표 정보 표시."""
        if not self.player_entity:
            return

        pos_comp = self.entity_manager.get_component(
            self.player_entity, PositionComponent
        )
        if pos_comp:
            mouse_pos = pygame.mouse.get_pos()

            coord_texts = [
                f'Player Pos: ({pos_comp.x:.1f}, {pos_comp.y:.1f})',
                f'Mouse: ({mouse_pos[0]}, {mouse_pos[1]})',
            ]

            start_y = self.screen_height - 80
            for i, text in enumerate(coord_texts):
                surface = self.font_small.render(
                    text, True, self.colors['ui_accent']
                )
                self._draw_text_with_background(surface, 10, start_y + i * 20)

    def _draw_game_state_indicator(self) -> None:
        """게임 상태 인디케이터."""
        state = self.game_loop.current_state
        state_color = {
            GameState.RUNNING: (100, 255, 100),
            GameState.PAUSED: (255, 255, 100),
            GameState.STOPPED: (255, 100, 100),
        }.get(state, (255, 255, 255))

        state_text = f'State: {state.display_name if hasattr(state, "display_name") else str(state)}'
        surface = self.font_medium.render(state_text, True, state_color)

        text_rect = surface.get_rect()
        x = self.screen_width - text_rect.width - 10
        self._draw_text_with_background(surface, x, 10)

    def _draw_text_with_background(
        self, text_surface: pygame.Surface, x: int, y: int
    ) -> None:
        """배경과 함께 텍스트 렌더링."""
        text_rect = text_surface.get_rect()
        bg_rect = pygame.Rect(
            x - 3, y - 1, text_rect.width + 6, text_rect.height + 2
        )

        bg_surface = pygame.Surface((bg_rect.width, bg_rect.height))
        bg_surface.set_alpha(180)
        bg_surface.fill((0, 0, 0))
        self.screen.blit(bg_surface, bg_rect.topleft)

        self.screen.blit(text_surface, (x, y))

    def run(self) -> None:
        """데모 애플리케이션 실행."""
        print('🎮 After School Survivors - Enhanced UI Demo')
        print('=' * 50)
        print('Features:')
        print('  ✓ Complete ECS Architecture')
        print('  ✓ GameLoop-based State Management')
        print('  ✓ Coordinate Transformation System')
        print('  ✓ Mouse-controlled Player Movement')
        print('  ✓ Real-time Performance Monitoring')
        print('  ✓ Enhanced pygame UI')
        print('  ✓ Visual World Grid System')
        print('')
        print('🎮 Move your mouse to control the blue player!')
        print('⏸️  Press SPACE to pause/resume')
        print('🚪 Press ESC to exit')
        print('=' * 50)

        try:
            self.game_loop.run()
        except KeyboardInterrupt:
            print('\n🛑 Interrupted by user')
        except Exception as e:
            print(f'\n❌ Error: {e}')
            import traceback

            traceback.print_exc()
        finally:
            self.cleanup()

    def cleanup(self) -> None:
        """리소스 정리."""
        # SystemOrchestrator에는 cleanup이 없으므로 생략
        if hasattr(self.entity_manager, 'cleanup'):
            self.entity_manager.cleanup()
        pygame.quit()
        print('✅ Demo ended successfully!')


def main() -> int:
    """메인 엔트리 포인트."""
    try:
        demo = EnhancedGameDemo(screen_width=1024, screen_height=768)
        demo.run()
        return 0
    except Exception as e:
        print(f'❌ Failed to run demo: {e}')
        import traceback

        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
