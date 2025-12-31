"""
카메라 클래스
"""
import pygame
from utils import lerp


class Camera:
    """카메라 클래스 - 플레이어를 부드럽게 따라감"""
    
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.x = 0
        self.y = 0
        self.target_x = 0
        self.target_y = 0
        self.smooth_factor = 0.15  # 부드러움 정도 (0.0 ~ 1.0, 작을수록 더 부드러움)
    
    def update(self, target_x, target_y, dt):
        """카메라를 타겟(플레이어) 위치로 부드럽게 업데이트"""
        # 타겟 위치 계산 (플레이어를 화면 중앙에 위치시키기)
        self.target_x = target_x - self.screen_width // 2
        self.target_y = target_y - self.screen_height // 2
        
        # 부드러운 보간 (lerp)을 사용하여 카메라 이동
        # dt를 고려하여 프레임레이트에 독립적으로 작동하도록 함
        lerp_factor = min(1.0, self.smooth_factor * (60.0 * dt))  # 60 FPS 기준으로 정규화
        self.x = lerp(self.x, self.target_x, lerp_factor)
        self.y = lerp(self.y, self.target_y, lerp_factor)
    
    def get_pos(self):
        """카메라 위치 반환"""
        return (self.x, self.y)

