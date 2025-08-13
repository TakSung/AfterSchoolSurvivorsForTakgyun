#!/usr/bin/env python3
"""
E2E Demo for MapRenderSystem infinite scroll tile system.

This demo showcases the complete MapRenderSystem implementation with:
- Visible tile range calculation algorithm (Task 17.1)
- Checkerboard pattern tile generation and rendering (Task 17.2)
- visible_tiles set-based performance optimization (Task 17.3)
- Player movement with camera tracking for map scrolling
- Real-time performance monitoring and statistics
"""

import sys

import pygame

from src.components.camera_component import CameraComponent
from src.components.map_component import MapComponent
from src.components.player_component import PlayerComponent
from src.components.player_movement_component import PlayerMovementComponent
from src.components.position_component import PositionComponent
from src.core.coordinate_manager import CoordinateManager
from src.core.entity_manager import EntityManager
from src.core.system_orchestrator import SystemOrchestrator
from src.systems.camera_system import CameraSystem
from src.systems.map_render_system import MapRenderSystem
from src.systems.player_movement_system import PlayerMovementSystem


class InfiniteCameraSystem(CameraSystem):
    """무한 스크롤 카메라 시스템 - 데드존 토글 및 무한 오프셋 기능 포함."""

    def __init__(self, priority: int = 10):
        super().__init__(priority=priority)
        self.dead_zone_enabled = (
            False  # 데드존 비활성화 상태로 시작 (무한 스크롤)
        )
        self.original_dead_zone = 30.0  # 원래 데드존 크기
        self.infinite_offset_enabled = True  # 무한 오프셋 모드로 시작
        self.camera_component_ref = None  # 카메라 컴포넌트 참조

    def toggle_dead_zone(self) -> bool:
        """데드존 활성화/비활성화 토글.

        Returns:
            현재 데드존 활성화 상태
        """
        self.dead_zone_enabled = not self.dead_zone_enabled
        return self.dead_zone_enabled

    def toggle_infinite_offset(self) -> bool:
        """무한 오프셋 모드 활성화/비활성화 토글.

        Returns:
            현재 무한 오프셋 모드 활성화 상태
        """
        self.infinite_offset_enabled = not self.infinite_offset_enabled

        # 카메라 컴포넌트의 world_bounds를 동적으로 변경
        if self.camera_component_ref:
            if self.infinite_offset_enabled:
                # 무한 오프셋 모드: 매우 큰 경계 설정
                self.camera_component_ref.world_bounds = {
                    'min_x': -1000000.0,
                    'max_x': 1000000.0,
                    'min_y': -1000000.0,
                    'max_y': 1000000.0,
                }
            else:
                # 제한 오프셋 모드: 원래 경계로 복원
                self.camera_component_ref.world_bounds = {
                    'min_x': -10000.0,
                    'max_x': 10000.0,
                    'min_y': -10000.0,
                    'max_y': 10000.0,
                }

        return self.infinite_offset_enabled

    def set_camera_component(self, camera_comp):
        """카메라 컴포넌트 참조 설정 (토글 기능을 위해 필요)."""
        self.camera_component_ref = camera_comp

    def _update_camera_by_mouse_tracking(
        self, camera_comp, mouse_x: float, mouse_y: float, delta_time: float
    ) -> None:
        """데드존 토글 기능이 포함된 카메라 업데이트."""
        center_x, center_y = camera_comp.screen_center
        distance = (
            (mouse_x - center_x) ** 2 + (mouse_y - center_y) ** 2
        ) ** 0.5

        # 데드존이 활성화되어 있고 데드존 내부라면 이동하지 않음
        effective_dead_zone = (
            self.original_dead_zone if self.dead_zone_enabled else 0.0
        )
        if distance <= effective_dead_zone:
            return

        direction_x = (mouse_x - center_x) / distance
        direction_y = (mouse_y - center_y) / distance

        # 무한 스크롤을 위한 빠른 카메라 이동
        if self.dead_zone_enabled:
            # 데드존 모드: 데드존 밖 거리에 비례한 이동
            excess_distance = distance - effective_dead_zone
            move_speed = min(excess_distance * 8.0, 500.0)
        else:
            # 무한 스크롤 모드: 마우스 위치에 직접 비례한 이동
            move_speed = min(distance * 2.0, 800.0)  # 더 빠른 무한 스크롤

        current_offset = camera_comp.world_offset
        new_offset_x = (
            current_offset[0] - direction_x * move_speed * delta_time
        )
        new_offset_y = (
            current_offset[1] - direction_y * move_speed * delta_time
        )

        new_offset = (new_offset_x, new_offset_y)
        camera_comp.update_world_offset(new_offset)


def main():
    """Run the MapRenderSystem E2E demo."""
    # Initialize Pygame
    pygame.init()

    # AI-NOTE : 2025-08-13 E2E 데모 화면 설정 - MapRenderSystem 테스트용
    # - 이유: MapRenderSystem의 체스판 패턴과 무한 스크롤 기능 검증
    # - 요구사항: 실제 게임 환경과 유사한 800x600 해상도
    # - 히스토리: 개별 시스템 데모에서 통합 E2E 데모로 확장
    screen_width = 800
    screen_height = 600
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption(
        'MapRenderSystem E2E Demo - Infinite Scroll Tiles'
    )
    clock = pygame.time.Clock()

    # Initialize coordinate manager
    coordinate_manager = CoordinateManager.get_instance()

    # Entity Manager and System setup
    entity_manager = EntityManager()
    system_orchestrator = SystemOrchestrator()

    # AI-DEV : 시스템 우선순위 설정으로 올바른 실행 순서 보장
    # - 문제: 카메라 업데이트 전에 맵 렌더링이 실행되면 이전 프레임 오프셋 사용
    # - 해결책: PlayerMovement(5) → Camera(10) → MapRender(15) 순서로 실행
    # - 주의사항: 우선순위 번호가 낮을수록 먼저 실행됨
    player_movement_system = PlayerMovementSystem(priority=5)
    camera_system = InfiniteCameraSystem(
        priority=10
    )  # 무한 스크롤 카메라 시스템 사용
    map_render_system = MapRenderSystem(priority=15, screen=screen)

    # Set screen sizes for systems
    player_movement_system.set_screen_size(screen_width, screen_height)
    map_render_system.set_screen_size(screen_width, screen_height)

    # Register systems in order
    system_orchestrator.register_system(player_movement_system)
    system_orchestrator.register_system(camera_system)
    system_orchestrator.register_system(map_render_system)

    # Create map entity with checkerboard configuration
    map_entity = entity_manager.create_entity()
    map_comp = MapComponent(
        tile_size=64,  # Task 17 requirement: 64x64 pixel tiles
        world_width=4000.0,  # Large world for infinite scroll testing
        world_height=4000.0,
        light_tile_color=(240, 240, 240),  # Light gray for checkerboard
        dark_tile_color=(220, 220, 220),  # Dark gray for checkerboard
        grid_color=(0, 0, 0),  # Black 1px border lines
        enable_infinite_scroll=True,  # Enable infinite scrolling
        tile_pattern_size=4,  # 4x4 tile pattern repetition
    )
    entity_manager.add_component(map_entity, map_comp)

    # Create player entity for camera tracking
    player_entity = entity_manager.create_entity()
    player_comp = PlayerComponent()
    position_comp = PositionComponent(0.0, 0.0)  # Start at world origin
    movement_comp = PlayerMovementComponent(
        world_position=(0.0, 0.0),
        direction=(1.0, 0.0),
        speed=300.0,  # Faster movement for scroll testing
        dead_zone_radius=15.0,
    )

    entity_manager.add_component(player_entity, player_comp)
    entity_manager.add_component(player_entity, position_comp)
    entity_manager.add_component(player_entity, movement_comp)

    # Create camera entity for map scrolling
    camera_entity = entity_manager.create_entity()

    # AI-DEV : 진짜 무한 스크롤을 위한 초대형 카메라 경계 설정
    # - 문제: 기본 경계로 인한 스크롤 제한
    # - 해결책: 실질적 무한 범위로 처음부터 설정
    # - 주의사항: D키와 C키로 제한/무한 모드 토글 가능
    infinite_bounds = {
        'min_x': -1000000.0,  # 진짜 무한 스크롤
        'max_x': 1000000.0,
        'min_y': -1000000.0,
        'max_y': 1000000.0,
    }

    camera_comp = CameraComponent(
        world_offset=(0.0, 0.0),  # 초기 오프셋은 (0,0)으로 설정
        screen_center=(screen_width // 2, screen_height // 2),
        follow_target=player_entity,  # Follow player for map scrolling
        dead_zone_radius=30.0,  # 데드존 크기 (처음엔 비활성화됨)
        world_bounds=infinite_bounds,  # 무한 스크롤 경계로 시작
    )
    entity_manager.add_component(camera_entity, camera_comp)

    # 카메라 시스템에 컴포넌트 참조 설정 (토글 기능을 위해)
    camera_system.set_camera_component(camera_comp)

    # 디버그: 초기 카메라 설정 확인
    print(f'Initial camera offset: {camera_comp.world_offset}')
    print(f'Initial screen center: {camera_comp.screen_center}')
    print(f'Initial player position: {movement_comp.world_position}')

    # AI-NOTE : 2025-08-13 E2E 데모 시작 메시지 - 사용자 가이드
    # - 이유: 데모 기능과 조작 방법을 명확히 안내
    # - 요구사항: MapRenderSystem의 모든 기능 시연 가능한 인터페이스
    # - 히스토리: 단순 시작 메시지에서 상세 가이드로 개선
    print('=' * 60)
    print('MapRenderSystem E2E Demo - Infinite Scroll Tiles')
    print('=' * 60)
    print('Features being demonstrated:')
    print('  ✓ Task 17.1: Visible tile range calculation algorithm')
    print('  ✓ Task 17.2: Checkerboard pattern tile rendering (64x64px)')
    print('  ✓ Task 17.3: visible_tiles set-based memory optimization')
    print('  ✓ Infinite scroll with camera offset integration')
    print('  ✓ Real-time performance monitoring')
    print()
    print('Controls:')
    print('  • Move mouse to control player direction')
    print('  • Player moves automatically following mouse')
    print('  • Camera follows player (reverse map scrolling)')
    print('  • Press D to toggle dead zone (Currently: OFF - Infinite scroll)')
    print('  • Press C to toggle camera offset bounds (Currently: Infinite)')
    print('  • Press P to toggle performance stats')
    print('  • Press R to reset player to origin')
    print('  • Press ESC to quit')
    print('=' * 60)

    running = True
    last_time = pygame.time.get_ticks()
    show_performance = True
    frame_count = 0
    fps_timer = 0

    while running:
        current_time = pygame.time.get_ticks()
        delta_time = (current_time - last_time) / 1000.0
        last_time = current_time

        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_p:
                    show_performance = not show_performance
                    print(
                        f'Performance stats: {"ON" if show_performance else "OFF"}'
                    )
                elif event.key == pygame.K_r:
                    # Reset player to origin
                    movement_comp.world_position = (0.0, 0.0)
                    position_comp.x = 0.0
                    position_comp.y = 0.0
                    print('Player reset to origin (0, 0)')
                elif event.key == pygame.K_d:
                    # Toggle dead zone
                    dead_zone_active = camera_system.toggle_dead_zone()
                    status = 'ON' if dead_zone_active else 'OFF'
                    print(f'Dead zone: {status}')
                elif event.key == pygame.K_c:
                    # Toggle infinite camera offset
                    infinite_offset_active = (
                        camera_system.toggle_infinite_offset()
                    )
                    status = (
                        'ON (Infinite)'
                        if infinite_offset_active
                        else 'OFF (Limited)'
                    )
                    print(f'Camera offset bounds: {status}')

        # Update mouse position for player movement
        mouse_pos = pygame.mouse.get_pos()
        camera_system.set_mouse_position(mouse_pos[0], mouse_pos[1])

        # Update all systems (MapRenderSystem will render tiles automatically)
        system_orchestrator.update_systems(entity_manager, delta_time)

        # AI-DEV : pygame 화면 지우기를 맵 렌더링 전에 수행
        # - 문제: 이전 프레임의 타일이 남아있어 시각적 잔상 발생
        # - 해결책: 시스템 업데이트 후 화면 지우기로 깨끗한 렌더링
        # - 주의사항: MapRenderSystem이 pygame 렌더링을 담당하므로 별도 지우기 불필요
        # Clear screen is handled by MapRenderSystem rendering

        # Draw player indicator at screen center
        center_x = screen_width // 2
        center_y = screen_height // 2
        pygame.draw.circle(screen, (255, 100, 100), (center_x, center_y), 15)

        # Draw player direction indicator
        direction = movement_comp.direction
        end_x = center_x + direction[0] * 25
        end_y = center_y + direction[1] * 25
        pygame.draw.line(
            screen, (255, 255, 100), (center_x, center_y), (end_x, end_y), 3
        )

        # Draw dead zone circle (if enabled)
        if camera_system.dead_zone_enabled:
            pygame.draw.circle(
                screen,
                (100, 100, 100),
                (center_x, center_y),
                int(camera_system.original_dead_zone),
                1,
            )
        else:
            # Draw infinite scroll indicator (crosshair)
            pygame.draw.line(
                screen,
                (100, 100, 100),
                (center_x - 10, center_y),
                (center_x + 10, center_y),
                1,
            )
            pygame.draw.line(
                screen,
                (100, 100, 100),
                (center_x, center_y - 10),
                (center_x, center_y + 10),
                1,
            )

        # Draw mouse cursor indicator
        pygame.draw.circle(screen, (100, 255, 100), mouse_pos, 3)

        # Debug: Print detailed camera and tile info
        if frame_count % 60 == 0:  # Print every second
            world_pos = movement_comp.world_position
            camera_offset = camera_comp.world_offset
            tile_stats = map_render_system.get_tile_stats()

            # 원점 근처 타일의 화면 좌표 확인 (화면 중앙에 나타나야 함)
            render_tiles = map_render_system.get_render_tiles()
            center_tile = None
            if render_tiles:
                # 타일 (0,0) 또는 가장 가까운 타일 찾기
                for tile in render_tiles:
                    if tile['tile_x'] == 0 and tile['tile_y'] == 0:
                        center_tile = tile
                        break

                if center_tile is None and render_tiles:
                    center_tile = render_tiles[
                        len(render_tiles) // 2
                    ]  # 중간 타일 사용

                if center_tile:
                    print(
                        f'DEBUG - Player: ({world_pos[0]:.1f}, {world_pos[1]:.1f}) | '
                        f'Camera: ({camera_offset[0]:.1f}, {camera_offset[1]:.1f}) | '
                        f'CenterTile({center_tile["tile_x"]},{center_tile["tile_y"]}) screen: ({center_tile["screen_x"]:.1f}, {center_tile["screen_y"]:.1f}) | '
                        f'Tiles: {tile_stats["total_visible"]}'
                    )
                else:
                    first_tile = render_tiles[0]
                    print(
                        f'DEBUG - Player: ({world_pos[0]:.1f}, {world_pos[1]:.1f}) | '
                        f'Camera: ({camera_offset[0]:.1f}, {camera_offset[1]:.1f}) | '
                        f'FirstTile screen: ({first_tile["screen_x"]:.1f}, {first_tile["screen_y"]:.1f}) | '
                        f'Tiles: {tile_stats["total_visible"]}'
                    )
            else:
                print(
                    f'DEBUG - Player: ({world_pos[0]:.1f}, {world_pos[1]:.1f}) | '
                    f'Camera: ({camera_offset[0]:.1f}, {camera_offset[1]:.1f}) | '
                    f'Tiles: {tile_stats["total_visible"]}'
                )

        # Display information and performance stats
        if show_performance:
            display_performance_info(
                screen,
                movement_comp,
                camera_comp,
                map_render_system,
                camera_system,
            )

        display_controls_hint(screen)

        pygame.display.flip()

        # FPS tracking
        frame_count += 1
        fps_timer += delta_time

        if fps_timer >= 1.0:  # Print FPS every second
            current_fps = frame_count / fps_timer
            if show_performance:
                print(
                    f'FPS: {current_fps:.1f} | Tiles: {map_render_system.get_tile_stats()["total_visible"]}'
                )
            frame_count = 0
            fps_timer = 0

        clock.tick(60)  # Target 60 FPS

    # Cleanup and summary
    print('\n' + '=' * 60)
    print('Demo completed! MapRenderSystem performance summary:')
    tile_stats = map_render_system.get_tile_stats()
    print(f'  • Final visible tiles: {tile_stats["total_visible"]}')
    print(f'  • Last new tiles: {tile_stats["new_tiles"]}')
    print(f'  • Last removed tiles: {tile_stats["removed_tiles"]}')
    print(f'  • Total managed tiles: {tile_stats["total_managed"]}')
    print('  • All Task 17 features demonstrated successfully! ✓')
    print('=' * 60)

    pygame.quit()
    sys.exit()


def display_performance_info(
    screen, movement_comp, camera_comp, map_render_system, camera_system
):
    """Display real-time performance and system information."""
    font = pygame.font.Font(None, 24)
    small_font = pygame.font.Font(None, 20)
    y_offset = 10
    line_height = 22

    # AI-DEV : 성능 모니터링 정보 표시로 Task 17.3 검증
    # - 문제: visible_tiles 최적화 효과를 시각적으로 확인하기 어려움
    # - 해결책: 실시간 타일 통계와 메모리 사용량 표시
    # - 주의사항: 너무 많은 정보로 인한 화면 가독성 저하 방지

    # Performance header
    header_text = small_font.render(
        'Performance Stats (Press P to toggle)', True, (255, 255, 0)
    )
    screen.blit(header_text, (10, y_offset))
    y_offset += line_height

    # Dead zone status
    dead_zone_status = (
        'ON' if camera_system.dead_zone_enabled else 'OFF (Infinite)'
    )
    color = (
        (255, 200, 100) if camera_system.dead_zone_enabled else (100, 255, 200)
    )
    text = font.render(f'Dead Zone: {dead_zone_status}', True, color)
    screen.blit(text, (10, y_offset))
    y_offset += line_height

    # Camera offset bounds status
    offset_status = (
        'Infinite' if camera_system.infinite_offset_enabled else 'Limited'
    )
    offset_color = (
        (100, 255, 200)
        if camera_system.infinite_offset_enabled
        else (255, 200, 100)
    )
    text = font.render(f'Offset Bounds: {offset_status}', True, offset_color)
    screen.blit(text, (10, y_offset))
    y_offset += line_height

    # Player world position
    world_pos = movement_comp.world_position
    text = font.render(
        f'Player: ({world_pos[0]:.1f}, {world_pos[1]:.1f})',
        True,
        (255, 255, 255),
    )
    screen.blit(text, (10, y_offset))
    y_offset += line_height

    # Camera offset
    camera_offset = camera_comp.world_offset
    text = font.render(
        f'Camera: ({camera_offset[0]:.1f}, {camera_offset[1]:.1f})',
        True,
        (255, 255, 255),
    )
    screen.blit(text, (10, y_offset))
    y_offset += line_height

    # Tile statistics (Task 17.3 verification)
    tile_stats = map_render_system.get_tile_stats()
    text = font.render(
        f'Visible Tiles: {tile_stats["total_visible"]}', True, (100, 255, 100)
    )
    screen.blit(text, (10, y_offset))
    y_offset += line_height

    text = font.render(
        f'New/Removed: {tile_stats["new_tiles"]}/{tile_stats["removed_tiles"]}',
        True,
        (200, 200, 255),
    )
    screen.blit(text, (10, y_offset))
    y_offset += line_height

    # Render tiles count
    render_tiles = map_render_system.get_render_tiles()
    text = font.render(f'Rendered: {len(render_tiles)}', True, (255, 200, 100))
    screen.blit(text, (10, y_offset))


def display_controls_hint(screen):
    """Display control hints at bottom of screen."""
    font = pygame.font.Font(None, 20)
    screen_width, screen_height = screen.get_size()

    hints = [
        'Mouse: Move player | D: Toggle dead zone | C: Toggle offset bounds | P: Toggle stats | R: Reset | ESC: Quit'
    ]

    y_start = screen_height - 30
    for i, hint in enumerate(hints):
        text = font.render(hint, True, (150, 150, 150))
        text_rect = text.get_rect()
        text_rect.centerx = screen_width // 2
        text_rect.y = y_start + i * 20
        screen.blit(text, text_rect)


if __name__ == '__main__':
    main()
