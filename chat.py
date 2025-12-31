"""
채팅 시스템
"""
import pygame
from utils import Colors, draw_text_with_shadow


class Chat:
    """채팅 시스템 클래스"""
    
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.is_open = False
        self.input_text = ""
        self.messages = []
        self.note_text = ""
        self.show_note = False
        self.show_rules = False
        
        # 채팅창 UI
        self.chat_width = 600
        self.chat_height = 400
        self.chat_x = (screen_width - self.chat_width) // 2
        self.chat_y = (screen_height - self.chat_height) // 2
    
    def handle_input(self, event):
        """입력 처리"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                return self.process_command()
            elif event.key == pygame.K_BACKSPACE:
                self.input_text = self.input_text[:-1]
            else:
                self.input_text += event.unicode
        return None
    
    def process_command(self):
        """명령어 처리"""
        command = self.input_text.strip().lower()
        self.input_text = ""  # 입력 초기화
        
        if command == "table":
            return "crafting"
        elif command == "rule":
            self.show_rules = True
            self.messages = []
            self.messages.append("Game Rules:")
            self.messages.append("- Use WASD to move")
            self.messages.append("- Left click to mine blocks")
            self.messages.append("- Right click to place blocks")
            self.messages.append("- Press TAB to open inventory")
            return None
        elif command == "note":
            self.show_note = True
            return "note"
        
        return None
    
    def draw(self, screen, font):
        """채팅창 그리기"""
        if not self.is_open:
            return
        
        # 배경
        chat_surface = pygame.Surface((self.chat_width, self.chat_height))
        chat_surface.fill((30, 30, 30))
        chat_surface.set_alpha(240)
        screen.blit(chat_surface, (self.chat_x, self.chat_y))
        
        # 테두리
        pygame.draw.rect(screen, Colors.WHITE,
                        (self.chat_x, self.chat_y, self.chat_width, self.chat_height), 3)
        
        # 나가기 버튼
        close_x = self.chat_x + self.chat_width - 60
        close_y = self.chat_y + 10
        pygame.draw.rect(screen, Colors.RED, (close_x, close_y, 50, 30))
        close_text = font.render("Close", True, Colors.WHITE)
        screen.blit(close_text, (close_x + 10, close_y + 5))
        
        if self.show_rules:
            # 게임 규칙 표시
            rules_y = self.chat_y + 50
            for i, msg in enumerate(self.messages[-10:]):  # 최근 10개만
                msg_surface = font.render(msg, True, Colors.WHITE)
                screen.blit(msg_surface, (self.chat_x + 10, rules_y + i * 25))
        elif self.show_note:
            # 노트 표시
            note_y = self.chat_y + 50
            note_label = font.render("Note:", True, Colors.WHITE)
            screen.blit(note_label, (self.chat_x + 10, note_y))
            
            # 노트 텍스트 입력 영역
            pygame.draw.rect(screen, Colors.WHITE,
                           (self.chat_x + 10, note_y + 30, self.chat_width - 20, self.chat_height - 100))
            note_lines = self.note_text.split('\n')
            for i, line in enumerate(note_lines[:20]):  # 최대 20줄
                line_surface = font.render(line, True, Colors.BLACK)
                screen.blit(line_surface, (self.chat_x + 15, note_y + 35 + i * 20))
        else:
            # 메시지 표시
            msg_y = self.chat_y + 50
            for i, msg in enumerate(self.messages[-10:]):  # 최근 10개만
                msg_surface = font.render(msg, True, Colors.WHITE)
                screen.blit(msg_surface, (self.chat_x + 10, msg_y + i * 25))
        
        # 입력창
        input_y = self.chat_y + self.chat_height - 40
        pygame.draw.rect(screen, Colors.WHITE, (self.chat_x + 10, input_y, self.chat_width - 20, 30))
        if self.show_note:
            # 노트 모드에서는 입력 텍스트를 노트에 추가
            display_text = self.input_text
        else:
            display_text = self.input_text
        input_surface = font.render(display_text, True, Colors.BLACK)
        screen.blit(input_surface, (self.chat_x + 15, input_y + 5))
    
    def handle_click(self, pos):
        """클릭 처리"""
        x, y = pos
        
        # 나가기 버튼
        close_x = self.chat_x + self.chat_width - 60
        close_y = self.chat_y + 10
        close_rect = pygame.Rect(close_x, close_y, 50, 30)
        if close_rect.collidepoint(x, y):
            self.is_open = False
            self.show_rules = False
            self.show_note = False
            return True
        
        return False

