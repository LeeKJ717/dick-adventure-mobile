"""
플레이어 클래스
"""
import pygame
import math
from utils import Colors, clamp, distance
from piskel_loader import PiskelLoader


class Player:
    """플레이어 클래스"""
    
    def __init__(self, x, y, gender='man', block_size=32):
        self.block_size = block_size
        self.gender = gender
        # 플레이어 크기는 마우스 커서의 2배 (블록 크기의 2배)
        self.width = block_size * 2
        self.height = block_size * 2
        self.x = x
        self.y = y
        self.vel_x = 0
        self.vel_y = 0
        self.speed = 9  # 5 * 1.8 = 9
        self.jump_power = 27  # 15 * 1.8 = 27
        self.gravity = 2.0
        self.on_ground = False
        self.jump_held = False
        self.can_jump = True
        self.max_health = 100
        self.health = 100
        self.image = None
        self.image_flipped = None  # 뒤집힌 이미지 캐시
        self.load_image()
        self.animation_timer = 0
        self.facing_right = True
    
    def load_image(self):
        """플레이어 이미지 로드"""
        if self.gender == 'man':
            image_path = 'fig/player/Species/MAN SPECIES/1no species.piskel'
        else:
            image_path = 'fig/player/Species/WOMAN  SPECIES/2no speicies.piskel'
        
        self.image = PiskelLoader.load_piskel_with_cache(image_path)
        if self.image:
            self.image = pygame.transform.scale(self.image, (self.width, self.height))
            # 뒤집힌 이미지 미리 생성 (성능 최적화)
            self.image_flipped = pygame.transform.flip(self.image, True, False)
        else:
            # 기본 이미지 (빨간색 사각형)
            self.image = pygame.Surface((self.width, self.height))
            self.image.fill(Colors.RED)
            self.image_flipped = pygame.transform.flip(self.image, True, False)
    
    def update(self, keys, dt, mobile_input=None):
        """플레이어 업데이트
        Args:
            keys: 키보드 입력
            dt: 델타 타임
            mobile_input: 모바일 입력 (dx, dy) 튜플 또는 None
        """
        # 이동 처리 (부드러운 가속/감속)
        acceleration = 0.5  # 가속도
        friction = 0.85  # 마찰력 (0.0 ~ 1.0, 작을수록 더 빠르게 멈춤)
        
        # 모바일 입력 우선 처리
        if mobile_input:
            dx, dy = mobile_input
            if abs(dx) > 0.1:  # 조이스틱이 움직였을 때
                self.vel_x += acceleration * dx * (60.0 * dt)
                self.vel_x = max(-self.speed, min(self.speed, self.vel_x))
                if dx > 0:
                    self.facing_right = True
                elif dx < 0:
                    self.facing_right = False
            else:
                # 조이스틱이 중앙에 있으면 마찰로 감속
                self.vel_x *= friction
        else:
            # 키보드 입력 처리
            if keys[pygame.K_a]:
                self.vel_x -= acceleration * (60.0 * dt)  # dt를 고려하여 프레임레이트 독립적
                self.vel_x = max(self.vel_x, -self.speed)
                self.facing_right = False
            elif keys[pygame.K_d]:
                self.vel_x += acceleration * (60.0 * dt)
                self.vel_x = min(self.vel_x, self.speed)
                self.facing_right = True
            else:
                # 키를 누르지 않으면 마찰로 감속
                self.vel_x *= friction
        
        # 속도가 매우 작으면 0으로 설정 (떨림 방지)
        if abs(self.vel_x) < 0.1:
            self.vel_x = 0
        
        # 점프 처리 (모바일 점프 버튼은 외부에서 처리)
        if keys[pygame.K_w]:
            if not self.jump_held:
                self.jump_held = True
                if self.on_ground and self.can_jump:
                    self.vel_y = -self.jump_power
                    self.on_ground = False
                    self.can_jump = False
        else:
            self.jump_held = False
            # 바닥에 닿으면 자동으로 점프 가능하게
            if self.on_ground:
                self.can_jump = True
    
    def jump(self):
        """점프 실행 (모바일 버튼용)"""
        if self.on_ground and self.can_jump:
            self.vel_y = -self.jump_power
            self.on_ground = False
            self.can_jump = False
        
        # 중력 적용
        if not self.on_ground:
            self.vel_y += self.gravity
        
        # Y 좌표 제한 (+2000 이상 올라갈 수 없음)
        if self.y < -2000 * self.block_size:
            self.y = -2000 * self.block_size
            self.vel_y = 0
        
        # 애니메이션 타이머 업데이트
        self.animation_timer += dt
    
    def apply_velocity(self):
        """속도 적용"""
        self.x += self.vel_x
        self.y += self.vel_y
    
    def get_rect(self):
        """플레이어의 충돌 사각형 반환"""
        return pygame.Rect(self.x, self.y, self.width, self.height)
    
    def draw(self, screen, camera_x, camera_y):
        """플레이어 그리기 - 최적화된 버전"""
        screen_x = int(self.x - camera_x)
        screen_y = int(self.y - camera_y)
        
        # 화면 밖이면 그리지 않음 (더 빠른 검사)
        screen_width = screen.get_width()
        screen_height = screen.get_height()
        if (screen_x < -self.width or screen_x > screen_width + self.width or
            screen_y < -self.height or screen_y > screen_height + self.height):
            return
        
        # 이미지 뒤집기 (캐시된 이미지 사용)
        if not self.facing_right:
            draw_image = self.image_flipped
        else:
            draw_image = self.image
        
        # 플레이어 그리기
        if draw_image:
            screen.blit(draw_image, (screen_x, screen_y))

