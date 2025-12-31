"""
적 클래스 (Zombie)
"""
import pygame
import math
from piskel_loader import PiskelLoader
from utils import Colors


class Zombie:
    """좀비 적 클래스"""
    
    def __init__(self, x, y, block_size=32):
        self.block_size = block_size
        self.width = block_size * 2
        self.height = block_size * 2
        self.x = x
        self.y = y
        self.max_health = 150
        self.health = 150
        self.attack_power = 23
        self.attack_speed = 3.0  # 3초마다 공격
        self.attack_timer = 0.0
        self.speed = 3.0  # 플레이어보다 3배 느림 (플레이어 속도 9)
        self.image = None
        self.load_image()
        self.is_alive = True
        
    def load_image(self):
        """좀비 이미지 로드"""
        image_path = 'fig/enemy/ZOMBIE.piskel'
        self.image = PiskelLoader.load_piskel(image_path)
        if self.image:
            self.image = pygame.transform.scale(self.image, (self.width, self.height))
        else:
            # 기본 이미지 (초록색 사각형) - 항상 생성
            self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            self.image.fill((0, 150, 0))
            # 눈과 입 그리기 (더 명확하게 보이도록)
            pygame.draw.circle(self.image, (255, 0, 0), (self.width // 3, self.height // 3), 3)
            pygame.draw.circle(self.image, (255, 0, 0), (self.width * 2 // 3, self.height // 3), 3)
            pygame.draw.ellipse(self.image, (100, 0, 0), (self.width // 3, self.height * 2 // 3, self.width // 3, self.height // 6))
    
    def update(self, dt, player_x, player_y, player, world):
        """좀비 업데이트 - 플레이어처럼 엄격한 충돌 처리"""
        if not self.is_alive:
            return
        
        # 플레이어를 향해 이동 (X축만)
        dx = player_x - (self.x + self.width // 2)
        distance = math.sqrt(dx * dx)
        
        # X축 이동 처리 (플레이어처럼 분리)
        new_x = self.x
        if distance > 0:
            # 플레이어 쪽으로 이동 (X축만, dt를 고려하여 프레임레이트 독립적)
            move_x = (dx / distance) * self.speed * dt * 60.0  # 60 FPS 기준으로 정규화
            new_x = self.x + move_x
        
        # X축 충돌 검사 (절대로 블록 통과 불가)
        if world.check_block_collision(new_x, self.y, self.width, self.height):
            # X축 충돌 발생 - 이전 위치 유지
            new_x = self.x
        
        # Y축 이동 처리 (땅에 붙어서 다니기, 점프 불가)
        # 현재 위치에서 땅 찾기
        zombie_bottom = self.y + self.height
        ground_y = world.find_ground_y(new_x, zombie_bottom, self.height)
        new_y = ground_y
        
        # Y축 충돌 검사 (절대로 블록 통과 불가)
        if world.check_block_collision(new_x, new_y, self.width, self.height):
            # Y축 충돌 발생 - 블록 위에 정확히 서도록
            # 바닥에 정확히 서도록 다시 계산
            zombie_bottom = new_y + self.height
            new_y = world.find_ground_y(new_x, zombie_bottom, self.height)
            # 다시 충돌 검사
            if world.check_block_collision(new_x, new_y, self.width, self.height):
                # 여전히 충돌하면 현재 위치 유지
                new_y = self.y
        
        # 위치 업데이트 (충돌 검사 완료 후)
        self.x = new_x
        self.y = new_y
        
        # 공격 처리 (X축과 Y축 모두 겹쳐야 데미지)
        # AABB 충돌 검사
        zombie_left = self.x
        zombie_right = self.x + self.width
        zombie_top = self.y
        zombie_bottom = self.y + self.height
        
        player_left = player.x
        player_right = player.x + player.width
        player_top = player.y
        player_bottom = player.y + player.height
        
        # X축과 Y축 모두 겹치는지 확인
        x_overlap = zombie_right > player_left and zombie_left < player_right
        y_overlap = zombie_bottom > player_top and zombie_top < player_bottom
        
        if x_overlap and y_overlap and self.attack_timer >= self.attack_speed:
            # 플레이어에게 데미지
            player.health -= self.attack_power
            if player.health < 0:
                player.health = 0
            self.attack_timer = 0.0
        
        # 공격 타이머 업데이트
        self.attack_timer += dt
    
    def take_damage(self, damage):
        """데미지 받기"""
        self.health -= damage
        if self.health <= 0:
            self.health = 0
            self.is_alive = False
    
    def draw(self, screen, camera_x, camera_y):
        """좀비 그리기"""
        if not self.is_alive:
            return
        
        screen_x = int(self.x - camera_x)
        screen_y = int(self.y - camera_y)
        
        # 화면 밖에 있으면 그리지 않음 (최적화)
        if screen_x + self.width < 0 or screen_x > screen.get_width() or \
           screen_y + self.height < 0 or screen_y > screen.get_height():
            return
        
        # 이미지가 없으면 기본 이미지 생성
        if self.image is None:
            self.load_image()
        
        # 좀비 이미지 그리기
        if self.image:
            screen.blit(self.image, (screen_x, screen_y))
        else:
            # 이미지 로드 실패 시 기본 사각형 그리기
            pygame.draw.rect(screen, (0, 150, 0), (screen_x, screen_y, self.width, self.height))
        
        # 체력바 그리기
        bar_width = self.width
        bar_height = 5
        bar_x = screen_x
        bar_y = screen_y - 10
        
        # 배경 (빨간색)
        pygame.draw.rect(screen, (150, 0, 0), (bar_x, bar_y, bar_width, bar_height))
        # 체력 (초록색)
        health_width = int(bar_width * (self.health / self.max_health))
        pygame.draw.rect(screen, (0, 150, 0), (bar_x, bar_y, health_width, bar_height))
        # 테두리
        pygame.draw.rect(screen, Colors.WHITE, (bar_x, bar_y, bar_width, bar_height), 1)


