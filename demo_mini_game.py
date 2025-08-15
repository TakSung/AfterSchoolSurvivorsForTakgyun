"""
Mini Game Demo - Experience and Level-up System Showcase

This demo showcases the complete experience and level-up system with:
- Player movement following mouse
- Enemy spawning and destruction
- Experience gain from enemy kills
- Level-up with health increases
- Real-time UI showing experience, level, and health
"""

import math
import random
import time
from typing import Any

import pygame

from src.components.experience_component import ExperienceComponent
from src.components.health_component import HealthComponent
from src.components.player_component import PlayerComponent
from src.components.position_component import PositionComponent
from src.components.render_component import RenderComponent
from src.core.entity_manager import EntityManager
from src.core.events.enemy_death_event import EnemyDeathEvent
from src.core.events.event_bus import EventBus
from src.systems.experience_system import ExperienceSystem
from src.systems.player_stats_system import PlayerStatsSystem
from src.utils.vector2 import Vector2

# 게임 설정
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
FPS = 60

# 색상 정의
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 100, 255)
RED = (255, 50, 50)
GREEN = (50, 255, 50)
YELLOW = (255, 255, 0)
PURPLE = (255, 50, 255)
GRAY = (128, 128, 128)
DARK_GRAY = (64, 64, 64)


class MiniGameDemo:
    """경험치 시스템을 활용한 미니 게임 데모"""

    def __init__(self) -> None:
        """게임 초기화"""
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("경험치 시스템 데모 - After School Survivors")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        
        # ECS 시스템 초기화
        self.entity_manager = EntityManager()
        self.event_bus = EventBus()
        
        # 시스템들 초기화
        self.experience_system = ExperienceSystem(priority=20)
        self.player_stats_system = PlayerStatsSystem(priority=30)
        
        # 이벤트 버스 연결
        self.experience_system.set_event_bus(self.event_bus)
        self.event_bus.subscribe(self.player_stats_system)
        
        # 시스템 초기화
        self.experience_system.initialize()
        self.player_stats_system.initialize()
        
        # 게임 상태
        self.running = True
        self.player_entity = None
        self.enemies: list[Any] = []
        self.last_enemy_spawn = 0.0
        self.enemy_spawn_interval = 2.0  # 2초마다 적 생성
        self.game_start_time = time.time()
        
        # 통계
        self.enemies_killed = 0
        self.total_experience = 0
        
        self._create_player()

    def _create_player(self) -> None:
        """플레이어 엔티티 생성"""
        self.player_entity = self.entity_manager.create_entity()
        
        # 플레이어 컴포넌트들 추가
        self.entity_manager.add_component(
            self.player_entity,
            PlayerComponent()
        )
        
        self.entity_manager.add_component(
            self.player_entity,
            PositionComponent(x=SCREEN_WIDTH // 2, y=SCREEN_HEIGHT // 2)
        )
        
        self.entity_manager.add_component(
            self.player_entity,
            RenderComponent(
                color=BLUE,
                size=Vector2(20, 20),
                layer=1
            )
        )
        
        self.entity_manager.add_component(
            self.player_entity,
            ExperienceComponent(current_exp=0, level=1)
        )
        
        self.entity_manager.add_component(
            self.player_entity,
            HealthComponent(current_health=100, max_health=100)
        )
        
        # 시스템들에 엔티티 매니저 설정
        self.experience_system._entity_manager = self.entity_manager
        self.player_stats_system._entity_manager = self.entity_manager

    def _create_enemy(self) -> Any:
        """적 엔티티 생성"""
        enemy = self.entity_manager.create_entity()
        
        # 화면 가장자리에서 랜덤 위치 생성
        edge = random.choice(['top', 'bottom', 'left', 'right'])
        if edge == 'top':
            x, y = random.randint(0, SCREEN_WIDTH), 0
        elif edge == 'bottom':
            x, y = random.randint(0, SCREEN_WIDTH), SCREEN_HEIGHT
        elif edge == 'left':
            x, y = 0, random.randint(0, SCREEN_HEIGHT)
        else:  # right
            x, y = SCREEN_WIDTH, random.randint(0, SCREEN_HEIGHT)
        
        # 적 타입 결정 (난이도에 따른 강화)
        game_time = time.time() - self.game_start_time
        if game_time > 60:  # 1분 후 보스 등장
            enemy_type = random.choices(
                ['basic', 'enhanced', 'boss'],
                weights=[40, 40, 20],
                k=1
            )[0]
        elif game_time > 30:  # 30초 후 강화 적 등장
            enemy_type = random.choices(
                ['basic', 'enhanced'],
                weights=[60, 40],
                k=1
            )[0]
        else:
            enemy_type = 'basic'
        
        # 적 타입별 설정
        if enemy_type == 'boss':
            color = PURPLE
            size = Vector2(30, 30)
            speed = 30
        elif enemy_type == 'enhanced':
            color = RED
            size = Vector2(18, 18)
            speed = 50
        else:  # basic
            color = RED
            size = Vector2(15, 15)
            speed = 40
        
        self.entity_manager.add_component(
            enemy,
            PositionComponent(x=x, y=y)
        )
        
        self.entity_manager.add_component(
            enemy,
            RenderComponent(
                color=color,
                size=size,
                layer=0
            )
        )
        
        # 적 정보를 저장 (속도와 타입)
        enemy.speed = speed
        enemy.enemy_type = enemy_type
        
        self.enemies.append(enemy)
        return enemy

    def _update_player_movement(self, mouse_pos: tuple[int, int]) -> None:
        """플레이어 이동 처리 (마우스 추적)"""
        if not self.player_entity:
            return
            
        pos_comp = self.entity_manager.get_component(
            self.player_entity, PositionComponent
        )
        if not pos_comp:
            return
        
        # 마우스 방향으로 이동
        dx = mouse_pos[0] - pos_comp.x
        dy = mouse_pos[1] - pos_comp.y
        distance = math.sqrt(dx * dx + dy * dy)
        
        if distance > 5:  # 데드존
            # 정규화 및 속도 적용
            player_speed = 150  # 픽셀/초
            dt = 1.0 / FPS
            
            pos_comp.x += (dx / distance) * player_speed * dt
            pos_comp.y += (dy / distance) * player_speed * dt
            
            # 화면 경계 제한
            pos_comp.x = max(10, min(SCREEN_WIDTH - 10, pos_comp.x))
            pos_comp.y = max(10, min(SCREEN_HEIGHT - 10, pos_comp.y))

    def _update_enemies(self) -> None:
        """적 AI 업데이트 (플레이어 추적)"""
        if not self.player_entity:
            return
            
        player_pos = self.entity_manager.get_component(
            self.player_entity, PositionComponent
        )
        if not player_pos:
            return
        
        dt = 1.0 / FPS
        
        for enemy in self.enemies[:]:  # 복사본으로 순회
            enemy_pos = self.entity_manager.get_component(
                enemy, PositionComponent
            )
            if not enemy_pos:
                continue
            
            # 플레이어 방향으로 이동
            dx = player_pos.x - enemy_pos.x
            dy = player_pos.y - enemy_pos.y
            distance = math.sqrt(dx * dx + dy * dy)
            
            if distance > 0:
                enemy_pos.x += (dx / distance) * enemy.speed * dt
                enemy_pos.y += (dy / distance) * enemy.speed * dt

    def _check_enemy_clicks(self, mouse_pos: tuple[int, int]) -> None:
        """마우스 클릭으로 적 처치"""
        for enemy in self.enemies[:]:  # 복사본으로 순회
            enemy_pos = self.entity_manager.get_component(
                enemy, PositionComponent
            )
            enemy_render = self.entity_manager.get_component(
                enemy, RenderComponent
            )
            if not enemy_pos or not enemy_render:
                continue
            
            # 적과 마우스 클릭 거리 계산
            dx = mouse_pos[0] - enemy_pos.x
            dy = mouse_pos[1] - enemy_pos.y
            distance = math.sqrt(dx * dx + dy * dy)
            
            # 적의 크기를 고려한 클릭 범위
            click_range = max(enemy_render.size.x, enemy_render.size.y) / 2 + 5
            
            if distance <= click_range:
                self._kill_enemy(enemy)
                break  # 한 번에 하나씩만 처치

    def _kill_enemy(self, enemy: Any) -> None:
        """적 처치 및 경험치 부여"""
        if enemy not in self.enemies:
            return
        
        # 적 사망 이벤트 생성
        enemy_id = f"enemy_{enemy.enemy_type}_{enemy.entity_id}"
        death_event = EnemyDeathEvent.create_from_id(
            enemy_entity_id=enemy_id,
            timestamp=time.time()
        )
        
        # 경험치 시스템에 이벤트 전달
        self.experience_system.handle_event(death_event)
        
        # 이벤트 버스 처리 (레벨업 이벤트 포함)
        self.event_bus.process_events()
        
        # 통계 업데이트
        self.enemies_killed += 1
        
        # 적 제거
        self.enemies.remove(enemy)
        self.entity_manager.destroy_entity(enemy)

    def _spawn_enemies(self) -> None:
        """적 자동 생성"""
        current_time = time.time()
        if current_time - self.last_enemy_spawn > self.enemy_spawn_interval:
            self._create_enemy()
            self.last_enemy_spawn = current_time
            
            # 시간이 지날수록 생성 간격 단축 (최대 난이도)
            game_time = current_time - self.game_start_time
            min_interval = 0.5
            self.enemy_spawn_interval = max(
                min_interval, 
                2.0 - (game_time / 60.0)  # 1분마다 1초씩 단축
            )

    def _render_ui(self) -> None:
        """UI 렌더링 (경험치, 레벨, 체력)"""
        if not self.player_entity:
            return
        
        exp_comp = self.entity_manager.get_component(
            self.player_entity, ExperienceComponent
        )
        health_comp = self.entity_manager.get_component(
            self.player_entity, HealthComponent
        )
        
        if not exp_comp or not health_comp:
            return
        
        # UI 배경
        ui_rect = pygame.Rect(10, 10, 300, 120)
        pygame.draw.rect(self.screen, DARK_GRAY, ui_rect)
        pygame.draw.rect(self.screen, WHITE, ui_rect, 2)
        
        # 레벨 표시
        level_text = self.font.render(f"레벨: {exp_comp.level}", True, WHITE)
        self.screen.blit(level_text, (20, 20))
        
        # 경험치 바
        exp_bar_rect = pygame.Rect(20, 50, 280, 20)
        pygame.draw.rect(self.screen, GRAY, exp_bar_rect)
        
        exp_ratio = exp_comp.get_exp_progress_ratio()
        exp_fill_width = int(280 * exp_ratio)
        if exp_fill_width > 0:
            exp_fill_rect = pygame.Rect(20, 50, exp_fill_width, 20)
            pygame.draw.rect(self.screen, YELLOW, exp_fill_rect)
        
        pygame.draw.rect(self.screen, WHITE, exp_bar_rect, 2)
        
        # 경험치 텍스트
        exp_text = self.small_font.render(
            f"EXP: {exp_comp.current_exp}/{exp_comp.get_exp_to_next_level()}", 
            True, WHITE
        )
        self.screen.blit(exp_text, (25, 53))
        
        # 체력 바
        health_bar_rect = pygame.Rect(20, 80, 280, 20)
        pygame.draw.rect(self.screen, GRAY, health_bar_rect)
        
        health_ratio = health_comp.get_health_ratio()
        health_fill_width = int(280 * health_ratio)
        if health_fill_width > 0:
            health_fill_rect = pygame.Rect(20, 80, health_fill_width, 20)
            pygame.draw.rect(self.screen, GREEN, health_fill_rect)
        
        pygame.draw.rect(self.screen, WHITE, health_bar_rect, 2)
        
        # 체력 텍스트
        health_text = self.small_font.render(
            f"HP: {health_comp.current_health}/{health_comp.max_health}", 
            True, WHITE
        )
        self.screen.blit(health_text, (25, 83))
        
        # 통계 표시
        stats_y = 150
        stats_texts = [
            f"적 처치: {self.enemies_killed}",
            f"현재 적: {len(self.enemies)}",
            f"게임 시간: {int(time.time() - self.game_start_time)}초",
            f"생성 간격: {self.enemy_spawn_interval:.1f}초",
        ]
        
        for i, text in enumerate(stats_texts):
            stat_surface = self.small_font.render(text, True, WHITE)
            self.screen.blit(stat_surface, (20, stats_y + i * 25))

    def _render_entities(self) -> None:
        """엔티티 렌더링"""
        # 모든 렌더링 가능한 엔티티 가져오기
        entities_with_render = self.entity_manager.get_entities_with_component(
            RenderComponent
        )
        
        # 레이어별로 정렬 (낮은 레이어가 먼저)
        entities_with_render.sort(
            key=lambda x: self.entity_manager.get_component(x[0], RenderComponent).layer
        )
        
        for entity, render_comp in entities_with_render:
            pos_comp = self.entity_manager.get_component(entity, PositionComponent)
            if not pos_comp:
                continue
            
            # 사각형으로 렌더링
            rect = pygame.Rect(
                pos_comp.x - render_comp.size.x // 2,
                pos_comp.y - render_comp.size.y // 2,
                render_comp.size.x,
                render_comp.size.y
            )
            pygame.draw.rect(self.screen, render_comp.color, rect)
            
            # 플레이어는 테두리 추가
            if self.entity_manager.has_component(entity, PlayerComponent):
                pygame.draw.rect(self.screen, WHITE, rect, 2)

    def _render_instructions(self) -> None:
        """게임 조작법 표시"""
        instructions = [
            "조작법:",
            "• 마우스 이동 - 플레이어 이동",
            "• 마우스 클릭 - 적 처치",
            "• ESC - 종료",
            "",
            "적 타입:",
            "• 빨강 (작은) - 기본 적 (50 EXP)",
            "• 빨강 (중간) - 강화 적 (75 EXP)", 
            "• 보라 (큰) - 보스 (200 EXP)",
        ]
        
        start_y = SCREEN_HEIGHT - 250
        for i, text in enumerate(instructions):
            color = YELLOW if text.startswith("•") else WHITE
            instruction_surface = self.small_font.render(text, True, color)
            self.screen.blit(instruction_surface, (SCREEN_WIDTH - 250, start_y + i * 25))

    def run(self) -> None:
        """메인 게임 루프"""
        print("=== 경험치 시스템 데모 시작 ===")
        print("마우스로 플레이어 이동, 클릭으로 적 처치!")
        print("적을 처치하여 경험치를 얻고 레벨업하세요!")
        
        while self.running:
            # 이벤트 처리
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # 좌클릭
                        self._check_enemy_clicks(pygame.mouse.get_pos())
            
            # 게임 로직 업데이트
            mouse_pos = pygame.mouse.get_pos()
            self._update_player_movement(mouse_pos)
            self._update_enemies()
            self._spawn_enemies()
            
            # 시스템 업데이트
            dt = 1.0 / FPS
            self.experience_system.update(self.entity_manager, dt)
            self.player_stats_system.update(self.entity_manager, dt)
            
            # 렌더링
            self.screen.fill(BLACK)
            self._render_entities()
            self._render_ui()
            self._render_instructions()
            
            pygame.display.flip()
            self.clock.tick(FPS)
        
        # 게임 종료 통계
        final_level = 1
        if self.player_entity:
            exp_comp = self.entity_manager.get_component(
                self.player_entity, ExperienceComponent
            )
            if exp_comp:
                final_level = exp_comp.level
        
        print(f"\n=== 게임 종료 ===")
        print(f"최종 레벨: {final_level}")
        print(f"적 처치 수: {self.enemies_killed}")
        print(f"플레이 시간: {int(time.time() - self.game_start_time)}초")
        
        pygame.quit()


if __name__ == "__main__":
    demo = MiniGameDemo()
    demo.run()