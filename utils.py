"""
유틸리티 함수 및 상수
"""
import pygame
import math


class Colors:
    """색상 상수"""
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)
    GRAY = (128, 128, 128)
    DARK_GRAY = (64, 64, 64)
    BROWN = (139, 69, 19)
    YELLOW = (255, 255, 0)


def get_chunk_coord(world_pos, chunk_size):
    """월드 좌표를 청크 좌표로 변환"""
    return int(world_pos // chunk_size)


def clamp(value, min_value, max_value):
    """값을 범위 내로 제한"""
    return max(min_value, min(value, max_value))


def distance(x1, y1, x2, y2):
    """두 점 사이의 거리 계산"""
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)


def draw_text_with_shadow(screen, text, font, color, pos, center=False, shadow_color=None):
    """그림자가 있는 텍스트 그리기"""
    if shadow_color is None:
        shadow_color = Colors.BLACK
    
    text_surface = font.render(text, True, color)
    shadow_surface = font.render(text, True, shadow_color)
    
    if center:
        text_rect = text_surface.get_rect(center=pos)
        shadow_rect = shadow_surface.get_rect(center=(pos[0] + 2, pos[1] + 2))
    else:
        text_rect = text_surface.get_rect(topleft=pos)
        shadow_rect = shadow_surface.get_rect(topleft=(pos[0] + 2, pos[1] + 2))
    
    screen.blit(shadow_surface, shadow_rect)
    screen.blit(text_surface, text_rect)
    
    return text_rect


class ShadowRenderer:
    """그림자 렌더링 유틸리티"""
    
    @staticmethod
    def draw_shadow(screen, image, pos, offset=(2, 2), alpha=60):
        """이미지에 그림자 그리기"""
        shadow = image.copy()
        shadow.set_alpha(alpha)
        shadow.fill((0, 0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        screen.blit(shadow, (pos[0] + offset[0], pos[1] + offset[1]))


class Animation:
    """애니메이션 유틸리티"""
    
    @staticmethod
    def fade_in(time, start_time, duration):
        """페이드 인 애니메이션 (0.0 ~ 1.0)"""
        if duration <= 0:
            return 1.0
        elapsed = time - start_time
        return clamp(elapsed / duration, 0.0, 1.0)
    
    @staticmethod
    def fade_out(time, start_time, duration):
        """페이드 아웃 애니메이션 (1.0 ~ 0.0)"""
        if duration <= 0:
            return 0.0
        elapsed = time - start_time
        return clamp(1.0 - (elapsed / duration), 0.0, 1.0)


def lerp(start, end, t):
    """선형 보간"""
    return start + (end - start) * t


def ease_in_out(t):
    """이징 함수 (ease in-out)"""
    return t * t * (3.0 - 2.0 * t)






