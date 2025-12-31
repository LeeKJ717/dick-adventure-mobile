"""
NPC 클래스 (PIKU)
"""
import pygame
import math
from piskel_loader import PiskelLoader
from utils import Colors


class PIKU:
    """PIKU NPC 클래스"""
    
    def __init__(self, x, y, block_size=32):
        self.block_size = block_size
        self.width = block_size * 2
        self.height = block_size * 2
        self.x = x
        self.y = y
        self.float_offset = 0.0  # 둥둥 떠다니는 오프셋
        self.float_speed = 2.0  # 떠다니는 속도
        self.target_x = x  # 목표 위치
        self.target_y = y
        self.speed = 3.0  # 이동 속도
        self.following_player = False  # 플레이어를 따라다니는지
        self.image = None
        self.load_image()
        self.damage_timer = 0.0  # 좀비에게 데미지를 주는 타이머
        
    def load_image(self):
        """PIKU 이미지 로드"""
        image_path = 'fig/alliance/PIKU.piskel'
        self.image = PiskelLoader.load_piskel(image_path)
        if self.image:
            self.image = pygame.transform.scale(self.image, (self.width, self.height))
        else:
            # 기본 이미지 (파란색 원)
            self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            pygame.draw.circle(self.image, (100, 150, 255), (self.width // 2, self.height // 2), self.width // 2)
    
    def update(self, dt, player_x, player_y, zombies):
        """PIKU 업데이트"""
        # 둥둥 떠다니는 애니메이션
        self.float_offset += self.float_speed * dt
        float_y = math.sin(self.float_offset) * 5  # 5픽셀 범위로 떠다님
        
        # 플레이어와의 거리 확인
        dx_to_player = player_x - self.x
        dy_to_player = player_y - self.y
        distance_to_player = math.sqrt(dx_to_player * dx_to_player + dy_to_player * dy_to_player)
        
        # 플레이어를 따라다니는 경우 (항상 따라다님)
        if distance_to_player > 200:  # 너무 멀면 빠르게 따라옴
            # 플레이어 쪽으로 빠르게 이동
            if distance_to_player > 0:
                self.x += (dx_to_player / distance_to_player) * self.speed * 2
                self.y += (dy_to_player / distance_to_player) * self.speed * 2 + float_y
        else:
            # 플레이어 주위에서 둥둥 떠다님 (플레이어 주변 100픽셀 반경)
            angle = self.float_offset * 0.5
            radius = 100
            target_x = player_x + math.cos(angle) * radius
            target_y = player_y + math.sin(angle) * radius + float_y
            
            # 목표 위치로 부드럽게 이동
            dx = target_x - self.x
            dy = target_y - self.y
            distance = math.sqrt(dx * dx + dy * dy)
            
            if distance > 2:  # 2픽셀 이상 떨어져 있으면 이동
                if distance > 0:
                    move_speed = min(self.speed * 1.5, distance)  # 빠르게 따라옴
                    self.x += (dx / distance) * move_speed
                    self.y += (dy / distance) * move_speed
            else:
                # 목표 위치에 도달
                self.x = target_x
                self.y = target_y
        
        # 좀비에게 자동으로 데미지 (1초에 5씩)
        self.damage_timer += dt
        if self.damage_timer >= 1.0:  # 1초마다
            for zombie in zombies:
                # PIKU와 좀비의 거리 확인 (100픽셀 이내)
                dx = zombie.x - self.x
                dy = zombie.y - self.y
                distance = math.sqrt(dx * dx + dy * dy)
                if distance <= 100:
                    zombie.take_damage(5)
            self.damage_timer = 0.0
    
    def check_click(self, mouse_x, mouse_y, camera_x, camera_y):
        """마우스 클릭 확인"""
        screen_x = self.x - camera_x
        screen_y = self.y - camera_y
        rect = pygame.Rect(screen_x, screen_y, self.width, self.height)
        return rect.collidepoint(mouse_x, mouse_y)
    
    def draw(self, screen, camera_x, camera_y):
        """PIKU 그리기"""
        screen_x = int(self.x - camera_x)
        screen_y = int(self.y - camera_y)
        
        if self.image:
            screen.blit(self.image, (screen_x, screen_y))

