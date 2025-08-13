"""
간단한 EntityRenderSystem 데모

현재까지 구현된 핵심 시스템들만 사용하는 최소한의 데모입니다.
"""

import sys

import pygame

from src.components.player_component import PlayerComponent
from src.components.position_component import PositionComponent
from src.components.render_component import RenderComponent, RenderLayer
from src.core.cached_camera_transformer import CachedCameraTransformer
from src.core.coordinate_manager import CoordinateManager
from src.core.entity_manager import EntityManager
from src.systems.entity_render_system import EntityRenderSystem
from src.utils.vector2 import Vector2


class SimpleDemo:
    def __init__(self):
        # 게임 설정
        self.screen_width = 800
        self.screen_height = 600
        self.fps = 60

        # Pygame 초기화
        pygame.init()
        self.screen = pygame.display.set_mode(
            (self.screen_width, self.screen_height)
        )
        pygame.display.set_caption('Simple ECS Demo')
        self.clock = pygame.time.Clock()

        # ECS 시스템
        self.entity_manager = EntityManager()

        # 좌표 변환 시스템 설정
        screen_size = Vector2(self.screen_width, self.screen_height)
        transformer = CachedCameraTransformer(screen_size=screen_size)
        coordinate_manager = CoordinateManager.get_instance()
        coordinate_manager.set_transformer(transformer)

        # 렌더링 시스템
        self.render_system = EntityRenderSystem(
            surface=self.screen, priority=50, cull_margin=50
        )
        self.render_system.initialize()

        # 엔티티들 생성
        self._create_entities()

        self.running = True
        self.camera_offset = Vector2(0, 0)

    def _create_entities(self):
        print('Creating entities...')

        # 플레이어 엔티티 (화면 중앙 고정)
        player_entity = self.entity_manager.create_entity()
        self.entity_manager.add_component(
            player_entity, PlayerComponent(player_id=0)
        )
        self.entity_manager.add_component(
            player_entity, PositionComponent(x=0.0, y=0.0)
        )
        self.entity_manager.add_component(
            player_entity,
            RenderComponent(
                color=(0, 150, 255),  # 파란색
                size=(40, 40),
                layer=RenderLayer.ENTITIES,
                visible=True,
            ),
        )
        print(f'Player entity created: {player_entity.entity_id}')

        # 고정된 테스트 엔티티들
        positions = [
            (-100, -100),
            (100, -100),
            (-100, 100),
            (100, 100),  # 네 모서리
            (0, -150),
            (0, 150),
            (-150, 0),
            (150, 0),  # 십자 패턴
            (-200, -200),
            (200, 200),
            (-200, 200),
            (200, -200),  # 더 먼 모서리
        ]
        colors = [
            (255, 100, 100),
            (100, 255, 100),
            (255, 255, 100),
            (255, 100, 255),
            (100, 255, 255),
            (255, 200, 100),
            (200, 100, 255),
            (150, 150, 255),
            (255, 150, 150),
            (150, 255, 150),
            (255, 255, 150),
            (255, 150, 255),
        ]

        for i, (x, y) in enumerate(positions):
            entity = self.entity_manager.create_entity()
            self.entity_manager.add_component(
                entity, PositionComponent(x=float(x), y=float(y))
            )
            self.entity_manager.add_component(
                entity,
                RenderComponent(
                    color=colors[i],
                    size=(30, 30),
                    layer=RenderLayer.ENTITIES,
                    visible=True,
                ),
            )
            print(f'Test entity {i + 1} created at ({x}, {y})')

        # 배경 격자 (간단하게)
        for x in range(-2, 3):
            for y in range(-2, 3):
                if x == 0 and y == 0:  # 중앙 건너뛰기
                    continue

                entity = self.entity_manager.create_entity()
                self.entity_manager.add_component(
                    entity, PositionComponent(x=x * 200.0, y=y * 200.0)
                )
                self.entity_manager.add_component(
                    entity,
                    RenderComponent(
                        color=(100, 100, 100),
                        size=(20, 20),
                        layer=RenderLayer.BACKGROUND,
                        visible=True,
                    ),
                )

        total_entities = len(self.entity_manager.get_all_entities())
        print(f'Total entities created: {total_entities}')

    def handle_input(self):
        # 마우스 위치로 카메라 오프셋 계산
        mouse_pos = pygame.mouse.get_pos()
        center_x, center_y = self.screen_width // 2, self.screen_height // 2

        # 마우스 위치에 따른 카메라 오프셋 (반대 방향)
        offset_x = (mouse_pos[0] - center_x) * 0.5
        offset_y = (mouse_pos[1] - center_y) * 0.5
        self.camera_offset = Vector2(offset_x, offset_y)

        # 좌표 변환기에 오프셋 적용
        transformer = CoordinateManager.get_instance().get_transformer()
        if transformer:
            transformer.set_camera_offset(self.camera_offset)

        # 이벤트 처리
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False

    def update(self, delta_time):
        # 렌더링 시스템 업데이트
        self.render_system.update(self.entity_manager, delta_time)

    def render(self):
        # 배경
        self.screen.fill((30, 30, 50))

        # UI 정보
        font = pygame.font.Font(None, 36)
        title = font.render('Simple ECS Demo', True, (255, 255, 255))
        self.screen.blit(title, (10, 10))

        font_small = pygame.font.Font(None, 24)
        instructions = [
            'Move mouse to control camera',
            'ESC to exit',
            f'Camera offset: ({self.camera_offset.x:.1f}, {self.camera_offset.y:.1f})',
        ]

        for i, text in enumerate(instructions):
            rendered = font_small.render(text, True, (200, 200, 200))
            self.screen.blit(rendered, (10, 50 + i * 25))

        # 렌더링 통계
        stats = self.render_system.get_render_stats()
        stats_text = [
            f'Total: {stats["total_entities"]}',
            f'Visible: {stats["visible_entities"]}',
            f'Culled: {stats["culled_entities"]}',
            f'Player: {stats["player_entities"]}',
        ]

        for i, text in enumerate(stats_text):
            rendered = font_small.render(text, True, (100, 255, 100))
            self.screen.blit(rendered, (self.screen_width - 150, 50 + i * 25))

        pygame.display.flip()

    def run(self):
        print('🎮 Simple ECS Demo Starting...')
        print('🎯 Move mouse to see camera movement!')
        print('🚪 Press ESC to exit')

        while self.running:
            delta_time = self.clock.tick(self.fps) / 1000.0

            self.handle_input()
            self.update(delta_time)
            self.render()

        pygame.quit()
        print('✅ Demo ended!')


def main():
    try:
        demo = SimpleDemo()
        demo.run()
        return 0
    except Exception as e:
        print(f'❌ Error: {e}')
        import traceback

        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
