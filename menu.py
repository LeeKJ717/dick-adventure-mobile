"""
메뉴 시스템
"""
import pygame
from utils import Colors, draw_text_with_shadow, Animation


class Menu:
    """메뉴 클래스"""
    
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.gender_choice_active = False
        self.selected_gender = None
        self.animation_progress = 0
        self.fade_duration = 0.5  # 0.5초
        
        # 버튼 위치
        self.start_button_rect = pygame.Rect(
            screen_width // 2 - 100,
            screen_height // 2,
            200, 50
        )
        
        self.man_button_rect = pygame.Rect(
            screen_width // 2 - 150,
            screen_height // 2 + 50,
            120, 50
        )
        
        self.woman_button_rect = pygame.Rect(
            screen_width // 2 + 30,
            screen_height // 2 + 50,
            120, 50
        )
    
    def update(self, dt):
        """메뉴 업데이트"""
        if self.gender_choice_active:
            self.animation_progress += dt
            if self.animation_progress > self.fade_duration:
                self.animation_progress = self.fade_duration
    
    def handle_click(self, pos):
        """클릭 처리"""
        if not self.gender_choice_active:
            if self.start_button_rect.collidepoint(pos):
                self.gender_choice_active = True
                self.animation_progress = 0
                return None
        else:
            if self.man_button_rect.collidepoint(pos):
                self.selected_gender = 'man'
                return 'man'
            elif self.woman_button_rect.collidepoint(pos):
                self.selected_gender = 'woman'
                return 'woman'
        
        return None
    
    def _get_korean_font(self, size):
        """한국어 폰트 가져오기"""
        korean_fonts = [
            'Malgun Gothic', '맑은 고딕',  # 맑은 고딕
            'Gulim', '굴림',  # 굴림
            'Batang', '바탕',  # 바탕
            'Dotum', '돋움',  # 돋움
            'Gungsuh', '궁서',  # 궁서
            'NanumGothic', '나눔고딕',  # 나눔고딕
        ]
        
        # 시스템 폰트 목록 가져오기
        try:
            available_fonts = pygame.font.get_fonts()
            for font_name in korean_fonts:
                try:
                    # 폰트 이름이 시스템에 있는지 확인
                    if font_name.lower() in [f.lower() for f in available_fonts]:
                        korean_font = pygame.font.SysFont(font_name, size)
                        # 테스트로 한국어 렌더링 확인
                        test_surface = korean_font.render('테스트', True, (255, 255, 255))
                        # TOFU 확인: 너비가 0이 아니고, 실제로 렌더링되었는지 확인
                        if test_surface.get_width() > 0:
                            # 간단한 픽셀 체크 (중앙 부분 샘플링)
                            center_x = test_surface.get_width() // 2
                            center_y = test_surface.get_height() // 2
                            if 0 <= center_x < test_surface.get_width() and 0 <= center_y < test_surface.get_height():
                                pixel_color = test_surface.get_at((center_x, center_y))
                                # 흰색이 아니면 렌더링된 것 (TOFU는 보통 검은색 또는 투명)
                                if pixel_color[0] > 0 or pixel_color[1] > 0 or pixel_color[2] > 0:
                                    return korean_font
                except:
                    continue
        except:
            pass
        
        # 한국어 폰트를 찾지 못한 경우 기본 폰트 사용
        try:
            return pygame.font.SysFont(None, size)
        except:
            return pygame.font.Font(None, size)
    
    def draw(self, screen, font):
        """메뉴 그리기"""
        screen.fill(Colors.BLACK)
        
        title_font = self._get_korean_font(72)
        title_text = "DEQJAM"
        draw_text_with_shadow(screen, title_text, title_font, Colors.WHITE,
                             (self.screen_width // 2, self.screen_height // 4), center=True)
        
        if not self.gender_choice_active:
            # 시작 버튼
            button_color = Colors.GREEN if self.start_button_rect.collidepoint(pygame.mouse.get_pos()) else Colors.DARK_GRAY
            pygame.draw.rect(screen, button_color, self.start_button_rect)
            pygame.draw.rect(screen, Colors.WHITE, self.start_button_rect, 3)
            
            start_text = font.render("Start Game", True, Colors.WHITE)
            start_text_rect = start_text.get_rect(center=self.start_button_rect.center)
            screen.blit(start_text, start_text_rect)
        else:
            # 페이드 인 계산 (0.0 ~ 1.0)
            fade_progress = min(self.animation_progress / self.fade_duration, 1.0) if self.fade_duration > 0 else 1.0
            fade_alpha = int(255 * fade_progress)
            
            subtitle_font = self._get_korean_font(48)
            subtitle_text = "Choose Your Gender"
            draw_text_with_shadow(screen, subtitle_text, subtitle_font, Colors.WHITE,
                                 (self.screen_width // 2, self.screen_height // 3), center=True)
            
            # 남성 버튼
            man_color = Colors.BLUE if self.man_button_rect.collidepoint(pygame.mouse.get_pos()) else Colors.DARK_GRAY
            man_surface = pygame.Surface((self.man_button_rect.width, self.man_button_rect.height))
            man_surface.set_alpha(fade_alpha)
            man_surface.fill(man_color)
            screen.blit(man_surface, self.man_button_rect)
            pygame.draw.rect(screen, Colors.WHITE, self.man_button_rect, 3)
            
            man_text = font.render("MAN", True, Colors.WHITE)
            man_text_rect = man_text.get_rect(center=self.man_button_rect.center)
            screen.blit(man_text, man_text_rect)
            
            # 여성 버튼
            woman_color = Colors.RED if self.woman_button_rect.collidepoint(pygame.mouse.get_pos()) else Colors.DARK_GRAY
            woman_surface = pygame.Surface((self.woman_button_rect.width, self.woman_button_rect.height))
            woman_surface.set_alpha(fade_alpha)
            woman_surface.fill(woman_color)
            screen.blit(woman_surface, self.woman_button_rect)
            pygame.draw.rect(screen, Colors.WHITE, self.woman_button_rect, 3)
            
            woman_text = font.render("WOMAN", True, Colors.WHITE)
            woman_text_rect = woman_text.get_rect(center=self.woman_button_rect.center)
            screen.blit(woman_text, woman_text_rect)

