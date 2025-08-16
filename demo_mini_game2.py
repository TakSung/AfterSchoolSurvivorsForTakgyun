"""
Mini Game Demo 2 - Complete ECS with Attack System and Camera

Advanced demo showcasing the complete experience and level-up system with:
- Player movement following mouse with camera tracking
- Automatic projectile attack system
- Enemy AI with different types and behaviors
- Experience gain from enemy kills with level-up
- Real-time UI showing experience, level, health, and weapon stats
- World coordinate system with camera following
"""

import logging
import math
import random
import time
from typing import Any

import pygame

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

from src.components.camera_component import CameraComponent
from src.components.collision_component import (
    CollisionComponent,
    CollisionLayer,
)
from src.components.enemy_component import EnemyComponent
from src.components.experience_component import ExperienceComponent
from src.components.health_component import HealthComponent
from src.components.player_component import PlayerComponent
from src.components.player_movement_component import PlayerMovementComponent
from src.components.position_component import PositionComponent
from src.components.render_component import RenderComponent, RenderLayer
from src.components.rotation_component import RotationComponent
from src.components.weapon_component import WeaponComponent, WeaponType
from src.core.cached_camera_transformer import CachedCameraTransformer
from src.core.coordinate_manager import CoordinateManager
from src.core.entity_manager import EntityManager
from src.core.events.enemy_death_event import EnemyDeathEvent
from src.core.events.event_bus import EventBus
from src.core.projectile_manager import ProjectileManager
from src.core.system_orchestrator import SystemOrchestrator
from src.core.weapon_manager import WeaponManager
from src.systems.auto_attack_system import AutoAttackSystem
from src.systems.camera_system import CameraSystem
from src.systems.collision_system import CollisionSystem
from src.systems.entity_render_system import EntityRenderSystem
from src.systems.experience_system import ExperienceSystem
from src.systems.player_movement_system import PlayerMovementSystem
from src.systems.player_stats_system import PlayerStatsSystem
from src.systems.projectile_system import ProjectileSystem
from src.utils.vector2 import Vector2

# 게임 설정
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
FPS = 60

# 색상 정의
COLORS = {
    'background': (15, 15, 25),
    'player': (100, 150, 255),
    'enemy_basic': (255, 100, 100),
    'enemy_enhanced': (255, 150, 50),
    'enemy_boss': (255, 50, 255),
    'projectile': (255, 255, 100),
    'ui_text': (255, 255, 255),
    'ui_background': (0, 0, 0, 180),
    'health_bar': (50, 255, 50),
    'exp_bar': (255, 255, 0),
    'ui_panel': (64, 64, 64),
}


class MiniGameDemo2:
    """완전한 ECS 아키텍처를 활용한 고급 미니 게임 데모"""

    def __init__(self) -> None:
        """게임 초기화"""
        # pygame 초기화
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(
            '고급 경험치 시스템 데모 v2 - After School Survivors'
        )
        self.clock = pygame.time.Clock()

        # 폰트 설정 (한글 지원)
        try:
            # 한글 폰트 시도 (macOS)
            self.font_large = pygame.font.Font(
                '/System/Library/Fonts/AppleSDGothicNeo.ttc', 32
            )
            self.font_medium = pygame.font.Font(
                '/System/Library/Fonts/AppleSDGothicNeo.ttc', 24
            )
            self.font_small = pygame.font.Font(
                '/System/Library/Fonts/AppleSDGothicNeo.ttc', 18
            )
        except:
            try:
                # 한글 폰트 시도 (일반적인 경로)
                self.font_large = pygame.font.Font(
                    '/System/Library/Fonts/Arial Unicode MS.ttf', 32
                )
                self.font_medium = pygame.font.Font(
                    '/System/Library/Fonts/Arial Unicode MS.ttf', 24
                )
                self.font_small = pygame.font.Font(
                    '/System/Library/Fonts/Arial Unicode MS.ttf', 18
                )
            except:
                # 기본 폰트로 fallback
                self.font_large = pygame.font.Font(None, 32)
                self.font_medium = pygame.font.Font(None, 24)
                self.font_small = pygame.font.Font(None, 18)

        # ECS 시스템 초기화
        self.entity_manager = EntityManager()
        self.event_bus = EventBus()
        self.system_orchestrator = SystemOrchestrator(event_bus=self.event_bus)

        # ProjectileManager 초기화 및 이벤트 구독
        self.projectile_manager = ProjectileManager()
        self.event_bus.subscribe(self.projectile_manager)

        # WeaponManager 초기화 및 이벤트 구독 (레벨업 이벤트 처리)
        self.weapon_manager = WeaponManager()
        self.weapon_manager.set_entity_manager(self.entity_manager)
        self.event_bus.subscribe(self.weapon_manager)

        # 좌표 변환 시스템 설정
        self.coordinate_manager = CoordinateManager.get_instance()
        self._setup_coordinate_system()

        # 게임 상태
        self.running = True
        self.paused = False

        # 엔티티 참조들
        self.player_entity = None
        self.camera_entity = None
        self.enemies: list[Any] = []

        # 게임 타이밍
        self.last_enemy_spawn = 0.0
        self.enemy_spawn_interval = 2.0
        self.game_start_time = time.time()

        # 통계
        self.enemies_killed = 0
        self.shots_fired = 0

        # 성능 모니터링
        self.frame_count = 0
        self.fps_timer = 0.0
        self.current_fps = 60.0

        # 초기화
        self._setup_systems()
        self._create_player()
        self._create_camera()

        print('=== 고급 미니 게임 데모 v2 시작 ===')
        print('🎮 마우스로 이동, 자동 공격으로 적을 처치하세요!')
        print('⚡ 경험치를 얻어 레벨업하고 더 강해지세요!')

    def _setup_coordinate_system(self) -> None:
        """좌표 변환 시스템 설정"""
        screen_size = Vector2(SCREEN_WIDTH, SCREEN_HEIGHT)
        transformer = CachedCameraTransformer(screen_size=screen_size)
        self.coordinate_manager.set_transformer(transformer)

    def _setup_systems(self) -> None:
        """게임 시스템들 초기화 및 등록"""
        # 플레이어 이동 시스템
        player_movement_system = PlayerMovementSystem(priority=5)
        player_movement_system.set_screen_size(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.system_orchestrator.register_system(
            player_movement_system, 'player_movement'
        )

        # 카메라 시스템
        camera_system = CameraSystem(priority=10, event_bus=self.event_bus)
        self.system_orchestrator.register_system(camera_system, 'camera')

        # 자동 공격 시스템
        auto_attack_system = AutoAttackSystem(
            priority=15, event_bus=self.event_bus
        )
        auto_attack_system.set_projectile_manager(self.projectile_manager)
        self.system_orchestrator.register_system(
            auto_attack_system, 'auto_attack'
        )

        # 투사체 시스템
        projectile_system = ProjectileSystem(
            priority=18,
            projectile_manager=self.projectile_manager,
            event_bus=self.event_bus,
        )
        self.system_orchestrator.register_system(
            projectile_system, 'projectile'
        )

        # 경험치 시스템
        experience_system = ExperienceSystem(priority=20)
        experience_system.set_event_bus(self.event_bus)
        self.system_orchestrator.register_system(
            experience_system, 'experience'
        )

        # 플레이어 스탯 시스템
        player_stats_system = PlayerStatsSystem(priority=25)
        self.event_bus.subscribe(player_stats_system)
        self.system_orchestrator.register_system(
            player_stats_system, 'player_stats'
        )

        # 충돌 시스템
        collision_system = CollisionSystem(priority=100)
        self.system_orchestrator.register_system(collision_system, 'collision')

        # 엔티티 렌더링 시스템
        entity_render_system = EntityRenderSystem(
            surface=self.screen, priority=50
        )
        self.system_orchestrator.register_system(
            entity_render_system, 'entity_render'
        )

    def _create_player(self) -> None:
        """플레이어 엔티티 생성"""
        self.player_entity = self.entity_manager.create_entity()

        # 플레이어 컴포넌트들 추가
        self.entity_manager.add_component(
            self.player_entity, PlayerComponent()
        )

        self.entity_manager.add_component(
            self.player_entity, PositionComponent(x=0.0, y=0.0)
        )

        self.entity_manager.add_component(
            self.player_entity, RotationComponent(angle=0.0)
        )

        # 플레이어 이동
        self.entity_manager.add_component(
            self.player_entity,
            PlayerMovementComponent(
                speed=200.0,
                angular_velocity_limit=math.pi * 3.0,
                dead_zone_radius=15.0,
            ),
        )

        # 플레이어 렌더링
        player_surface = pygame.Surface((30, 30), pygame.SRCALPHA)
        player_surface.fill(COLORS['player'])
        pygame.draw.circle(player_surface, (255, 255, 255), (15, 15), 13, 2)

        render_comp = RenderComponent(
            sprite=player_surface,
            size=(30, 30),
            layer=RenderLayer.ENTITIES,
            visible=True,
        )
        self.entity_manager.add_component(self.player_entity, render_comp)

        # 경험치 컴포넌트
        self.entity_manager.add_component(
            self.player_entity, ExperienceComponent(current_exp=0, level=1)
        )

        # 체력 컴포넌트
        self.entity_manager.add_component(
            self.player_entity,
            HealthComponent(current_health=100, max_health=100),
        )

        # 무기 컴포넌트 - 즉시 공격 가능하도록 쿨다운 충분히 설정
        self.entity_manager.add_component(
            self.player_entity,
            WeaponComponent(
                weapon_type=WeaponType.SOCCER_BALL,
                damage=25,
                attack_speed=2.0,  # 초당 2발
                range=300.0,
                last_attack_time=1.0,  # 즉시 공격 가능하도록 충분한 시간 설정
            ),
        )

        # 충돌 컴포넌트
        self.entity_manager.add_component(
            self.player_entity,
            CollisionComponent(
                width=30.0,
                height=30.0,
                layer=CollisionLayer.PLAYER,
                collision_mask={CollisionLayer.ENEMY},
            ),
        )

    def _create_camera(self) -> None:
        """카메라 엔티티 생성 - 플레이어 중앙 고정"""
        self.camera_entity = self.entity_manager.create_entity()

        player_pos = self.entity_manager.get_component(
            self.player_entity, PositionComponent
        )

        camera_comp = CameraComponent(
            world_offset=(player_pos.x, player_pos.y),
            screen_center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2),
            follow_target=self.player_entity,
            dead_zone_radius=0.0,  # 완전히 중앙 고정
            world_bounds={
                'min_x': -2000.0,
                'max_x': 2000.0,
                'min_y': -2000.0,
                'max_y': 2000.0,
            },
        )
        self.entity_manager.add_component(self.camera_entity, camera_comp)

    def _create_enemy(self) -> Any:
        """적 엔티티 생성"""
        enemy = self.entity_manager.create_entity()

        # 플레이어 주변 랜덤 위치에 생성
        if self.player_entity:
            player_pos = self.entity_manager.get_component(
                self.player_entity, PositionComponent
            )
            if player_pos:
                # 화면 밖 거리에서 생성
                angle = random.uniform(0, 2 * math.pi)
                distance = random.uniform(400, 600)
                x = player_pos.x + distance * math.cos(angle)
                y = player_pos.y + distance * math.sin(angle)
            else:
                x, y = 0, 0
        else:
            x, y = 0, 0

        # 적 타입 결정 (시간에 따른 난이도 증가)
        game_time = time.time() - self.game_start_time
        if game_time > 120:  # 2분 후 보스 등장
            enemy_type = random.choices(
                ['basic', 'enhanced', 'boss'], weights=[30, 50, 20], k=1
            )[0]
        elif game_time > 60:  # 1분 후 강화 적 등장
            enemy_type = random.choices(
                ['basic', 'enhanced'], weights=[50, 50], k=1
            )[0]
        else:
            enemy_type = 'basic'

        # 적 타입별 설정
        if enemy_type == 'boss':
            color = COLORS['enemy_boss']
            size = (35, 35)
            speed = 60
            health = 150
        elif enemy_type == 'enhanced':
            color = COLORS['enemy_enhanced']
            size = (25, 25)
            speed = 100
            health = 75
        else:  # basic
            color = COLORS['enemy_basic']
            size = (20, 20)
            speed = 80
            health = 50

        # 위치 컴포넌트
        self.entity_manager.add_component(enemy, PositionComponent(x=x, y=y))

        # 회전 컴포넌트
        self.entity_manager.add_component(enemy, RotationComponent(angle=0.0))

        # 적 렌더링
        enemy_surface = pygame.Surface(size, pygame.SRCALPHA)
        enemy_surface.fill(color)
        if enemy_type == 'boss':
            # 보스는 육각형
            center = (size[0] // 2, size[1] // 2)
            radius = size[0] // 2 - 3
            points = []
            for i in range(6):
                angle = i * math.pi / 3
                px = center[0] + radius * math.cos(angle)
                py = center[1] + radius * math.sin(angle)
                points.append((px, py))
            pygame.draw.polygon(enemy_surface, (255, 255, 255), points, 2)
        elif enemy_type == 'enhanced':
            # 강화 적은 다이아몬드
            center = (size[0] // 2, size[1] // 2)
            points = [
                (center[0], 5),
                (size[0] - 5, center[1]),
                (center[0], size[1] - 5),
                (5, center[1]),
            ]
            pygame.draw.polygon(enemy_surface, (255, 255, 255), points, 2)
        else:
            # 기본 적은 원
            pygame.draw.circle(
                enemy_surface,
                (255, 255, 255),
                (size[0] // 2, size[1] // 2),
                size[0] // 2 - 2,
                2,
            )

        render_comp = RenderComponent(
            sprite=enemy_surface,
            size=size,
            layer=RenderLayer.ENTITIES,
            visible=True,
        )
        self.entity_manager.add_component(enemy, render_comp)

        # 체력 컴포넌트
        self.entity_manager.add_component(
            enemy, HealthComponent(current_health=health, max_health=health)
        )

        # 적 컴포넌트 (타겟팅용)
        self.entity_manager.add_component(enemy, EnemyComponent())

        # 충돌 컴포넌트
        self.entity_manager.add_component(
            enemy,
            CollisionComponent(
                width=size[0],
                height=size[1],
                layer=CollisionLayer.ENEMY,
                collision_mask={
                    CollisionLayer.PLAYER,
                    CollisionLayer.PROJECTILE,
                },
            ),
        )

        # 적 정보 저장
        enemy.enemy_type = enemy_type
        enemy.speed = speed
        enemy.max_health = health

        self.enemies.append(enemy)
        return enemy

    def _update_enemies(self, delta_time: float) -> None:
        """적 AI 업데이트 - 플레이어 추적"""
        if not self.player_entity:
            return

        player_pos = self.entity_manager.get_component(
            self.player_entity, PositionComponent
        )
        if not player_pos:
            return

        for enemy in self.enemies[:]:
            enemy_pos = self.entity_manager.get_component(
                enemy, PositionComponent
            )
            enemy_health = self.entity_manager.get_component(
                enemy, HealthComponent
            )

            if not enemy_pos or not enemy_health:
                continue

            # 적이 죽었으면 처리
            if enemy_health.is_dead():
                self._kill_enemy(enemy)
                continue

            # 플레이어 추적 AI
            dx = player_pos.x - enemy_pos.x
            dy = player_pos.y - enemy_pos.y
            distance = math.sqrt(dx * dx + dy * dy)

            if distance > 0:
                # 정규화된 방향벡터
                move_x = (dx / distance) * enemy.speed * delta_time
                move_y = (dy / distance) * enemy.speed * delta_time

                enemy_pos.x += move_x
                enemy_pos.y += move_y

                # 회전 업데이트
                rotation = self.entity_manager.get_component(
                    enemy, RotationComponent
                )
                if rotation:
                    rotation.angle = math.atan2(dy, dx)

    def _spawn_enemies(self) -> None:
        """적 자동 생성"""
        current_time = time.time()
        if current_time - self.last_enemy_spawn > self.enemy_spawn_interval:
            self._create_enemy()
            self.last_enemy_spawn = current_time

            # 시간이 지날수록 생성 간격 단축
            game_time = current_time - self.game_start_time
            min_interval = 0.8
            self.enemy_spawn_interval = max(
                min_interval,
                2.0 - (game_time / 90.0),  # 1.5분마다 약간씩 단축
            )

    def _kill_enemy(self, enemy: Any) -> None:
        """적 처치 및 경험치 부여"""
        if enemy not in self.enemies:
            return

        # 적 사망 이벤트 생성
        enemy_id = f'enemy_{enemy.enemy_type}_{enemy.entity_id}'
        death_event = EnemyDeathEvent.create_from_id(
            enemy_entity_id=enemy_id, timestamp=time.time()
        )

        # 경험치 시스템에 이벤트 전달
        experience_system = self.system_orchestrator.get_system('experience')
        if experience_system:
            experience_system.handle_event(death_event)

        # 이벤트 버스 처리 (레벨업 이벤트 포함)
        self.event_bus.process_events()

        # 통계 업데이트
        self.enemies_killed += 1

        # 적 제거
        self.enemies.remove(enemy)
        self.entity_manager.destroy_entity(enemy)

    def _render_world_entities(self) -> None:
        """월드 엔티티 렌더링 (좌표 변환 적용)"""
        # 좌표 변환기 가져오기
        transformer = self.coordinate_manager.get_transformer()
        if not transformer:
            return

        # 렌더링 가능한 엔티티들 가져오기
        entities_with_render = self.entity_manager.get_entities_with_component(
            RenderComponent
        )

        # 레이어별로 정렬
        entities_with_render.sort(
            key=lambda x: self.entity_manager.get_component(
                x[0], RenderComponent
            ).layer
        )

        for entity, render_comp in entities_with_render:
            if not render_comp.visible:
                continue

            pos_comp = self.entity_manager.get_component(
                entity, PositionComponent
            )
            if not pos_comp:
                continue

            try:
                # 월드 좌표를 화면 좌표로 변환
                screen_pos = transformer.world_to_screen(
                    Vector2(pos_comp.x, pos_comp.y)
                )

                # 화면 범위 내에 있는지 확인 (컬링)
                margin = 50
                if (
                    -margin <= screen_pos.x <= SCREEN_WIDTH + margin
                    and -margin <= screen_pos.y <= SCREEN_HEIGHT + margin
                ):
                    # 스프라이트 렌더링
                    if render_comp.sprite:
                        sprite_rect = render_comp.sprite.get_rect()
                        sprite_rect.center = (
                            int(screen_pos.x),
                            int(screen_pos.y),
                        )
                        self.screen.blit(render_comp.sprite, sprite_rect)

                    # 체력바 표시 (적만)
                    if (
                        entity in self.enemies
                        and self.entity_manager.has_component(
                            entity, HealthComponent
                        )
                    ):
                        health_comp = self.entity_manager.get_component(
                            entity, HealthComponent
                        )
                        if (
                            health_comp
                            and health_comp.get_health_ratio() < 1.0
                        ):
                            self._draw_health_bar(screen_pos, health_comp)

            except:
                continue  # 변환 실패 시 무시

    def _draw_health_bar(
        self, screen_pos: Vector2, health_comp: HealthComponent
    ) -> None:
        """적 체력바 그리기"""
        bar_width = 30
        bar_height = 4
        bar_x = int(screen_pos.x - bar_width // 2)
        bar_y = int(screen_pos.y - 25)

        # 배경
        bg_rect = pygame.Rect(bar_x, bar_y, bar_width, bar_height)
        pygame.draw.rect(self.screen, (100, 100, 100), bg_rect)

        # 체력
        health_ratio = health_comp.get_health_ratio()
        health_width = int(bar_width * health_ratio)
        if health_width > 0:
            health_rect = pygame.Rect(bar_x, bar_y, health_width, bar_height)
            color = (
                COLORS['health_bar'] if health_ratio > 0.3 else (255, 100, 100)
            )
            pygame.draw.rect(self.screen, color, health_rect)

        # 테두리
        pygame.draw.rect(self.screen, (200, 200, 200), bg_rect, 1)

    def _render_ui(self) -> None:
        """UI 렌더링"""
        if not self.player_entity:
            return

        exp_comp = self.entity_manager.get_component(
            self.player_entity, ExperienceComponent
        )
        health_comp = self.entity_manager.get_component(
            self.player_entity, HealthComponent
        )
        weapon_comp = self.entity_manager.get_component(
            self.player_entity, WeaponComponent
        )

        if not exp_comp or not health_comp:
            return

        # UI 패널 배경
        panel_rect = pygame.Rect(10, 10, 350, 140)
        panel_surface = pygame.Surface((panel_rect.width, panel_rect.height))
        panel_surface.set_alpha(200)
        panel_surface.fill(COLORS['ui_panel'])
        self.screen.blit(panel_surface, panel_rect)
        pygame.draw.rect(self.screen, COLORS['ui_text'], panel_rect, 2)

        y_offset = 20

        # 레벨 표시
        level_text = self.font_medium.render(
            f'레벨: {exp_comp.level}', True, COLORS['ui_text']
        )
        self.screen.blit(level_text, (20, y_offset))
        y_offset += 25

        # 경험치 바
        exp_bar_rect = pygame.Rect(20, y_offset, 320, 16)
        pygame.draw.rect(self.screen, (80, 80, 80), exp_bar_rect)

        exp_ratio = exp_comp.get_exp_progress_ratio()
        exp_fill_width = int(320 * exp_ratio)
        if exp_fill_width > 0:
            exp_fill_rect = pygame.Rect(20, y_offset, exp_fill_width, 16)
            pygame.draw.rect(self.screen, COLORS['exp_bar'], exp_fill_rect)

        pygame.draw.rect(self.screen, COLORS['ui_text'], exp_bar_rect, 1)

        # 경험치 텍스트
        exp_text = self.font_small.render(
            f'EXP: {exp_comp.current_exp}/{exp_comp.get_exp_to_next_level()}',
            True,
            COLORS['ui_text'],
        )
        self.screen.blit(exp_text, (22, y_offset + 2))
        y_offset += 25

        # 체력 바
        health_bar_rect = pygame.Rect(20, y_offset, 320, 16)
        pygame.draw.rect(self.screen, (80, 80, 80), health_bar_rect)

        health_ratio = health_comp.get_health_ratio()
        health_fill_width = int(320 * health_ratio)
        if health_fill_width > 0:
            health_fill_rect = pygame.Rect(20, y_offset, health_fill_width, 16)
            pygame.draw.rect(
                self.screen, COLORS['health_bar'], health_fill_rect
            )

        pygame.draw.rect(self.screen, COLORS['ui_text'], health_bar_rect, 1)

        # 체력 텍스트
        health_text = self.font_small.render(
            f'HP: {health_comp.current_health}/{health_comp.max_health}',
            True,
            COLORS['ui_text'],
        )
        self.screen.blit(health_text, (22, y_offset + 2))
        y_offset += 25

        # 무기 정보 (WeaponManager를 통한 효과적인 스탯 조회)
        if weapon_comp:
            # WeaponManager를 통해 레벨업 보너스가 적용된 공격 속도 조회
            effective_attack_speed = (
                self.weapon_manager.get_effective_attack_speed(
                    self.player_entity
                )
            )
            effective_damage = self.weapon_manager.get_effective_damage(
                self.player_entity
            )

            weapon_text = self.font_small.render(
                f'무기: {weapon_comp.weapon_type.display_name} '
                f'(데미지: {effective_damage}, '
                f'속도: {effective_attack_speed:.1f}/s)',
                True,
                COLORS['ui_text'],
            )
            self.screen.blit(weapon_text, (20, y_offset))

        # 게임 통계
        stats_y = 170

        # 실제 투사체 개수를 ProjectileSystem에서 가져오기
        projectile_system = self.system_orchestrator.get_system('projectile')
        projectile_count = 0
        if projectile_system:
            projectile_count = projectile_system.get_projectile_count(
                self.entity_manager
            )

        stats_texts = [
            f'적 처치: {self.enemies_killed}',
            f'현재 적: {len(self.enemies)}',
            f'투사체: {projectile_count}',
            f'FPS: {self.current_fps:.1f}',
            f'게임 시간: {int(time.time() - self.game_start_time)}초',
        ]

        for i, text in enumerate(stats_texts):
            stat_surface = self.font_small.render(
                text, True, COLORS['ui_text']
            )
            self.screen.blit(stat_surface, (20, stats_y + i * 20))

    def _render_instructions(self) -> None:
        """게임 조작법 표시"""
        instructions = [
            '=== 고급 미니 게임 데모 v2 ===',
            '',
            '조작법:',
            '• 마우스 이동 - 플레이어 이동',
            '• 자동 공격 - 가장 가까운 적 공격',
            '• SPACE - 일시정지/재개',
            '• ESC - 종료',
            '',
            '시스템:',
            '• 월드 좌표 + 카메라 추적',
            '• 자동 투사체 공격',
            '• 경험치 획득 & 레벨업',
            '• 적 AI & 타입별 차별화',
            '',
            '적 타입:',
            '• 빨강 원 - 기본 적 (50 EXP)',
            '• 주황 다이아몬드 - 강화 적 (75 EXP)',
            '• 보라 육각형 - 보스 (200 EXP)',
        ]

        start_y = SCREEN_HEIGHT - 400
        for i, text in enumerate(instructions):
            if text.startswith('==='):
                color = (255, 255, 100)
                font = self.font_medium
            elif text.startswith('•'):
                color = (200, 200, 255)
                font = self.font_small
            elif text in ['조작법:', '시스템:', '적 타입:']:
                color = (100, 255, 100)
                font = self.font_small
            else:
                color = COLORS['ui_text']
                font = self.font_small

            if text:  # 빈 줄이 아닌 경우만
                instruction_surface = font.render(text, True, color)
                self.screen.blit(
                    instruction_surface, (SCREEN_WIDTH - 280, start_y + i * 20)
                )

    def _update_fps(self, delta_time: float) -> None:
        """FPS 계산"""
        self.frame_count += 1
        self.fps_timer += delta_time

        if self.fps_timer >= 1.0:
            self.current_fps = self.frame_count / self.fps_timer
            self.frame_count = 0
            self.fps_timer = 0.0

    def run(self) -> None:
        """메인 게임 루프"""
        last_time = pygame.time.get_ticks()

        while self.running:
            current_time = pygame.time.get_ticks()
            delta_time = (
                (current_time - last_time) / 1000.0 if not self.paused else 0.0
            )
            last_time = current_time

            # 이벤트 처리
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                    elif event.key == pygame.K_SPACE:
                        self.paused = not self.paused
                        print(f'게임 {"일시정지" if self.paused else "재개"}')

            if not self.paused:
                # 시스템 업데이트
                self.system_orchestrator.update_systems(
                    self.entity_manager, delta_time
                )

                # 이벤트 처리 (투사체 등록 등을 위해)
                self.event_bus.process_events()

                # 커스텀 게임 로직
                self._update_enemies(delta_time)
                self._spawn_enemies()

            # 렌더링
            self.screen.fill(COLORS['background'])
            self._render_world_entities()
            self._render_ui()
            self._render_instructions()

            # 일시정지 표시
            if self.paused:
                pause_text = self.font_large.render(
                    '⏸️ 일시정지 - SPACE로 재개', True, (255, 255, 0)
                )
                text_rect = pause_text.get_rect(
                    center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
                )
                pygame.draw.rect(
                    self.screen, (0, 0, 0, 180), text_rect.inflate(20, 10)
                )
                self.screen.blit(pause_text, text_rect)

            pygame.display.flip()

            # FPS 업데이트
            self._update_fps(delta_time)
            self.clock.tick(FPS)

        # 게임 종료 통계
        self._show_final_stats()
        pygame.quit()

    def _show_final_stats(self) -> None:
        """게임 종료 통계 출력"""
        final_level = 1
        final_exp = 0
        final_health = 100

        if self.player_entity:
            exp_comp = self.entity_manager.get_component(
                self.player_entity, ExperienceComponent
            )
            health_comp = self.entity_manager.get_component(
                self.player_entity, HealthComponent
            )
            if exp_comp:
                final_level = exp_comp.level
                final_exp = exp_comp.total_exp_earned
            if health_comp:
                final_health = health_comp.current_health

        play_time = int(time.time() - self.game_start_time)

        print(f'\n{"=" * 50}')
        print('🎮 게임 종료 통계')
        print(f'{"=" * 50}')
        print(f'⚡ 최종 레벨: {final_level}')
        print(f'📊 총 경험치: {final_exp}')
        print(f'💖 최종 체력: {final_health}')
        print(f'💀 적 처치 수: {self.enemies_killed}')
        print(f'⏱️  플레이 시간: {play_time}초')
        print(f'📈 평균 FPS: {self.current_fps:.1f}')
        print(f'{"=" * 50}')


if __name__ == '__main__':
    try:
        demo = MiniGameDemo2()
        demo.run()
    except Exception as e:
        print(f'❌ 게임 실행 오류: {e}')
        import traceback

        traceback.print_exc()
