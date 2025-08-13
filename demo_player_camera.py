#!/usr/bin/env python3
"""
Demo for player movement and camera system integration.

This demo shows how the player movement system and camera system work together
to provide the player-centered camera view with reverse map movement.
"""

import sys

import pygame

from src.components.camera_component import CameraComponent
from src.components.player_component import PlayerComponent
from src.components.player_movement_component import PlayerMovementComponent
from src.components.position_component import PositionComponent
from src.core.entity_manager import EntityManager
from src.core.system_orchestrator import SystemOrchestrator
from src.systems.camera_system import CameraSystem
from src.systems.player_movement_system import PlayerMovementSystem


def main():
    """Run the player movement and camera demo."""
    # Initialize Pygame
    pygame.init()

    # AI-NOTE : 2025-08-11 데모 화면 설정 - 개발용 해상도
    # - 이유: 마우스 추적과 카메라 동작을 시각적으로 확인하기 위한 설정
    # - 요구사항: PlayerMovementSystem의 화면 크기와 동일한 해상도
    screen_width = 800
    screen_height = 600
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption('Player Movement + Camera Demo')
    clock = pygame.time.Clock()

    # Entity Manager and System setup
    entity_manager = EntityManager()
    system_orchestrator = SystemOrchestrator()

    # Systems
    player_movement_system = PlayerMovementSystem(priority=5)
    camera_system = CameraSystem(priority=10)

    # Set screen size for player movement system
    player_movement_system.set_screen_size(screen_width, screen_height)

    system_orchestrator.register_system(player_movement_system)
    system_orchestrator.register_system(camera_system)

    # Create player entity
    player_entity = entity_manager.create_entity()

    # Add components to player
    player_comp = PlayerComponent()
    position_comp = PositionComponent(0.0, 0.0)  # Start at world origin
    movement_comp = PlayerMovementComponent(
        world_position=(0.0, 0.0),
        direction=(1.0, 0.0),
        speed=200.0,
        dead_zone_radius=20.0,  # Slightly larger dead zone for demo
    )

    entity_manager.add_component(player_entity, player_comp)
    entity_manager.add_component(player_entity, position_comp)
    entity_manager.add_component(player_entity, movement_comp)

    # Create camera entity
    camera_entity = entity_manager.create_entity()
    camera_comp = CameraComponent(
        world_offset=(0.0, 0.0),
        screen_center=(screen_width // 2, screen_height // 2),
        follow_target=player_entity,  # Follow the player
        dead_zone_radius=10.0,
    )
    entity_manager.add_component(camera_entity, camera_comp)

    print('Player Movement + Camera Demo Started!')
    print('Move mouse to control player direction')
    print('Press ESC to quit')

    running = True
    last_time = pygame.time.get_ticks()

    while running:
        current_time = pygame.time.get_ticks()
        delta_time = (current_time - last_time) / 1000.0  # Convert to seconds
        last_time = current_time

        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

        # Update mouse position for camera system
        mouse_pos = pygame.mouse.get_pos()
        camera_system.set_mouse_position(mouse_pos[0], mouse_pos[1])

        # Update systems
        system_orchestrator.update_systems(entity_manager, delta_time)

        # Clear screen
        screen.fill((20, 20, 30))  # Dark blue background

        # AI-NOTE : 2025-08-11 시각적 피드백을 위한 렌더링
        # - 이유: 플레이어 위치와 카메라 오프셋을 시각적으로 확인
        # - 요구사항: 마우스 추적과 카메라 역방향 이동 확인
        # - 히스토리: 콘솔 출력에서 시각적 렌더링으로 개선

        # Draw grid for visual reference (simulated map)
        draw_grid(screen, camera_comp, 50)

        # Draw player at screen center (fixed position)
        center_x = screen_width // 2
        center_y = screen_height // 2
        pygame.draw.circle(screen, (255, 100, 100), (center_x, center_y), 20)

        # Draw direction indicator
        direction = movement_comp.direction
        end_x = center_x + direction[0] * 30
        end_y = center_y + direction[1] * 30
        pygame.draw.line(
            screen, (255, 255, 100), (center_x, center_y), (end_x, end_y), 3
        )

        # Draw mouse position indicator
        pygame.draw.circle(screen, (100, 255, 100), mouse_pos, 5)

        # Draw dead zone
        pygame.draw.circle(
            screen,
            (100, 100, 100),
            (center_x, center_y),
            int(movement_comp.dead_zone_radius),
            2,
        )

        # Display info
        display_info(screen, movement_comp, camera_comp, mouse_pos)

        pygame.display.flip()
        clock.tick(60)  # 60 FPS

    pygame.quit()
    sys.exit()


def draw_grid(screen, camera_comp, grid_size):
    """Draw a grid pattern to show camera movement."""
    screen_width, screen_height = screen.get_size()
    offset_x, offset_y = camera_comp.world_offset

    # Grid lines with camera offset applied
    for x in range(-grid_size, screen_width + grid_size, grid_size):
        grid_x = x + offset_x % grid_size
        pygame.draw.line(
            screen, (50, 50, 50), (grid_x, 0), (grid_x, screen_height)
        )

    for y in range(-grid_size, screen_height + grid_size, grid_size):
        grid_y = y + offset_y % grid_size
        pygame.draw.line(
            screen, (50, 50, 50), (0, grid_y), (screen_width, grid_y)
        )


def display_info(screen, movement_comp, camera_comp, mouse_pos):
    """Display debug information on screen."""
    font = pygame.font.Font(None, 24)
    y_offset = 10
    line_height = 25

    # Player world position
    world_pos = movement_comp.world_position
    text = font.render(
        f'Player World Pos: ({world_pos[0]:.1f}, {world_pos[1]:.1f})',
        True,
        (255, 255, 255),
    )
    screen.blit(text, (10, y_offset))
    y_offset += line_height

    # Camera offset
    camera_offset = camera_comp.world_offset
    text = font.render(
        f'Camera Offset: ({camera_offset[0]:.1f}, {camera_offset[1]:.1f})',
        True,
        (255, 255, 255),
    )
    screen.blit(text, (10, y_offset))
    y_offset += line_height

    # Mouse position
    text = font.render(f'Mouse Pos: {mouse_pos}', True, (255, 255, 255))
    screen.blit(text, (10, y_offset))
    y_offset += line_height

    # Player direction
    direction = movement_comp.direction
    text = font.render(
        f'Direction: ({direction[0]:.2f}, {direction[1]:.2f})',
        True,
        (255, 255, 255),
    )
    screen.blit(text, (10, y_offset))


if __name__ == '__main__':
    main()
