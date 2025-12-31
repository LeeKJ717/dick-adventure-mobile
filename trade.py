"""
거래 시스템
"""
import pygame
from utils import Colors
from piskel_loader import PiskelLoader


class Trade:
    """거래 시스템 클래스"""
    
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.is_open = False
        self.trade_width = 500
        self.trade_height = 500
        self.trade_x = (screen_width - self.trade_width) // 2
        self.trade_y = (screen_height - self.trade_height) // 2
        
        # 거래 슬롯 (아이템 1개)
        self.trade_slot = None  # {'type': str, 'count': int} or None
        self.slot_size = 50
        self.slot_x = self.trade_x + 20
        self.slot_y = self.trade_y + 150
        
        # 거래 내용
        self.requested_item = 'tree'
        self.requested_count = 50
        self.dialogue_index = 0  # 대사 인덱스
        self.dialogues = [
            "옜날에는 이곳이 엄청난 도시였어",
            "하지만 사람들이 악마에의해 성욕이 늘어났지",
            "그래서 사람들이 점점 많아지고",
            "사람들이 깔려 죽고 너만남았어",
            "너는 냉동수면상태여서"
        ]
        self.show_dialogue = False  # 대사 표시 여부
        self.dialogue_complete = False  # 대사 완료 여부
        self.trade_complete = False  # 거래 완료 여부
        self.completion_dialogue_index = 0  # 완료 대사 인덱스
        self.completion_dialogues = [
            "잘했어요",
            "차원의 문을 드리겠습니다"
        ]
        self.error_message = None  # 에러 메시지
        self.error_message_time = 0  # 에러 메시지 표시 시간
        
    def open_trade(self):
        """거래 창 열기"""
        self.is_open = True
        self.dialogue_index = 0
        self.show_dialogue = False
        self.dialogue_complete = False
        self.trade_complete = False
        self.completion_dialogue_index = 0
        self.trade_slot = None
        self.error_message = None
        self.error_message_time = 0
    
    def close_trade(self):
        """거래 창 닫기"""
        self.is_open = False
        self.show_dialogue = False
        self.dialogue_index = 0
        self.dialogue_complete = False
        self.trade_complete = False
        self.completion_dialogue_index = 0
        self.trade_slot = None
    
    def get_trade_slot_at_pos(self, pos):
        """거래 슬롯 위치 확인"""
        x, y = pos
        slot_rect = pygame.Rect(self.slot_x, self.slot_y, self.slot_size, self.slot_size)
        if slot_rect.collidepoint(x, y):
            return True
        return False
    
    def handle_drag_drop(self, dragging_item, dragging_source, inventory):
        """드래그 앤 드롭 처리"""
        if dragging_item is None:
            return False
        
        # 거래 슬롯에 드롭
        if self.trade_slot is None:
            # 빈 슬롯에 이동
            self.trade_slot = dragging_item.copy()
            # 인벤토리/핫바에서 제거
            if dragging_source[0] == 'inventory':
                del inventory.items[dragging_source[1]]
            else:
                del inventory.hotbar[dragging_source[1]]
            return True
        else:
            # 같은 타입이면 합치기
            if self.trade_slot['type'] == dragging_item['type']:
                total = self.trade_slot['count'] + dragging_item['count']
                if total <= 100:  # 최대 스택
                    self.trade_slot['count'] = total
                    if dragging_source[0] == 'inventory':
                        del inventory.items[dragging_source[1]]
                    else:
                        del inventory.hotbar[dragging_source[1]]
                    return True
            # 다른 타입이면 교체
            else:
                # 기존 아이템을 인벤토리로 반환
                if inventory.add_item(self.trade_slot['type'], self.trade_slot['count']):
                    self.trade_slot = dragging_item.copy()
                    if dragging_source[0] == 'inventory':
                        del inventory.items[dragging_source[1]]
                    else:
                        del inventory.hotbar[dragging_source[1]]
                    return True
        
        return False
    
    def handle_click(self, pos, inventory):
        """클릭 처리"""
        if not self.is_open:
            return False
        
        x, y = pos
        
        # 닫기 버튼
        close_x = self.trade_x + self.trade_width - 30
        close_y = self.trade_y + 10
        close_rect = pygame.Rect(close_x, close_y, 20, 20)
        if close_rect.collidepoint(x, y):
            self.close_trade()
            return False
        
        # 대사 완료 전
        if not self.dialogue_complete:
            # 대사 버튼
            if not self.show_dialogue:
                button_x = self.trade_x + self.trade_width // 2 - 75
                button_y = self.trade_y + self.trade_height - 80
                button_rect = pygame.Rect(button_x, button_y, 150, 40)
                if button_rect.collidepoint(x, y):
                    self.show_dialogue = True
                    return False
            
            # 다음 대사 버튼
            if self.show_dialogue and self.dialogue_index < len(self.dialogues) - 1:
                next_button_x = self.trade_x + self.trade_width // 2 - 75
                next_button_y = self.trade_y + self.trade_height - 80
                next_button_rect = pygame.Rect(next_button_x, next_button_y, 150, 40)
                if next_button_rect.collidepoint(x, y):
                    self.dialogue_index += 1
                    return False
            
            # 대사 완료 확인
            if self.show_dialogue and self.dialogue_index >= len(self.dialogues) - 1:
                self.dialogue_complete = True
                return False
        
        # 거래 완료 후 완료 대사
        if self.trade_complete:
            if self.completion_dialogue_index < len(self.completion_dialogues) - 1:
                next_button_x = self.trade_x + self.trade_width // 2 - 75
                next_button_y = self.trade_y + self.trade_height - 80
                next_button_rect = pygame.Rect(next_button_x, next_button_y, 150, 40)
                if next_button_rect.collidepoint(x, y):
                    self.completion_dialogue_index += 1
                    if self.completion_dialogue_index >= len(self.completion_dialogues):
                        self.close_trade()
                    return False
        
        # 거래 실행 버튼 (대사 완료 후)
        if self.dialogue_complete and not self.trade_complete:
            trade_button_x = self.trade_x + self.trade_width // 2 - 75
            trade_button_y = self.trade_y + self.trade_height - 80
            trade_button_rect = pygame.Rect(trade_button_x, trade_button_y, 150, 40)
            if trade_button_rect.collidepoint(x, y):
                self.execute_trade(inventory)
                return False
        
        return False
    
    def execute_trade(self, inventory):
        """거래 실행 - 인벤토리/핫바에서 자동으로 나무 50개 제거"""
        # 인벤토리/핫바에서 나무 개수 확인
        tree_count = inventory.count_item(self.requested_item)
        
        if tree_count < self.requested_count:
            # 부족한 경우 에러 메시지 표시
            self.error_message = "부족합니다"
            self.error_message_time = 2.0  # 2초간 표시
            return False
        
        # 나무 50개 제거
        if inventory.remove_item_type(self.requested_item, self.requested_count):
            # 차원의 문 지급
            inventory.add_item('portal', 1)
            
            # 거래 완료
            self.trade_complete = True
            self.completion_dialogue_index = 0
            self.error_message = None
            return True
        
        return False
    
    def update_dialogue(self, dt):
        """대사 업데이트"""
        if self.show_dialogue and self.dialogue_index < len(self.dialogues):
            # 대사는 자동으로 다음으로 넘어가지 않음 (버튼 클릭으로만)
            pass
        
        # 에러 메시지 시간 업데이트
        if self.error_message_time > 0:
            self.error_message_time -= dt
            if self.error_message_time <= 0:
                self.error_message = None
    
    def next_dialogue(self):
        """다음 대사로"""
        if self.show_dialogue and self.dialogue_index < len(self.dialogues) - 1:
            self.dialogue_index += 1
    
    def draw(self, screen, font):
        """거래 창 그리기"""
        if not self.is_open:
            return
        
        # 배경
        trade_surface = pygame.Surface((self.trade_width, self.trade_height))
        trade_surface.fill((50, 50, 50))
        trade_surface.set_alpha(240)
        screen.blit(trade_surface, (self.trade_x, self.trade_y))
        
        # 테두리
        pygame.draw.rect(screen, Colors.WHITE,
                        (self.trade_x, self.trade_y, self.trade_width, self.trade_height), 3)
        
        # 닫기 버튼
        close_x = self.trade_x + self.trade_width - 30
        close_y = self.trade_y + 10
        pygame.draw.rect(screen, Colors.RED, (close_x, close_y, 20, 20))
        close_text = font.render("X", True, Colors.WHITE)
        screen.blit(close_text, (close_x + 5, close_y + 2))
        
        # 거래 완료 후 완료 대사 표시
        if self.trade_complete:
            if self.completion_dialogue_index < len(self.completion_dialogues):
                dialogue_text = self.completion_dialogues[self.completion_dialogue_index]
                dialogue_surface = font.render(dialogue_text, True, Colors.WHITE)
                screen.blit(dialogue_surface, (self.trade_x + 20, self.trade_y + 100))
                
                # 다음 버튼
                if self.completion_dialogue_index < len(self.completion_dialogues) - 1:
                    next_button_x = self.trade_x + self.trade_width // 2 - 75
                    next_button_y = self.trade_y + self.trade_height - 80
                    pygame.draw.rect(screen, Colors.BLUE, (next_button_x, next_button_y, 150, 40))
                    next_text = font.render("다음", True, Colors.WHITE)
                    screen.blit(next_text, (next_button_x + 50, next_button_y + 10))
            return
        
        # 대사 완료 전
        if not self.dialogue_complete:
            if not self.show_dialogue:
                # 거래 요청 표시
                title_text = font.render("PIKU의 거래 요청", True, Colors.WHITE)
                screen.blit(title_text, (self.trade_x + 20, self.trade_y + 30))
                
                request_text = f"{self.requested_item.upper()} {self.requested_count}개를 가져와줘"
                request_surface = font.render(request_text, True, Colors.WHITE)
                screen.blit(request_surface, (self.trade_x + 20, self.trade_y + 70))
                
                # 대사 버튼
                button_x = self.trade_x + self.trade_width // 2 - 75
                button_y = self.trade_y + self.trade_height - 80
                pygame.draw.rect(screen, Colors.GREEN, (button_x, button_y, 150, 40))
                button_text = font.render("이야기 듣기", True, Colors.WHITE)
                screen.blit(button_text, (button_x + 30, button_y + 10))
            else:
                # 대사 표시
                if self.dialogue_index < len(self.dialogues):
                    dialogue_text = self.dialogues[self.dialogue_index]
                    dialogue_surface = font.render(dialogue_text, True, Colors.WHITE)
                    screen.blit(dialogue_surface, (self.trade_x + 20, self.trade_y + 100))
                    
                    # 다음 버튼
                    if self.dialogue_index < len(self.dialogues) - 1:
                        next_button_x = self.trade_x + self.trade_width // 2 - 75
                        next_button_y = self.trade_y + self.trade_height - 80
                        pygame.draw.rect(screen, Colors.BLUE, (next_button_x, next_button_y, 150, 40))
                        next_text = font.render("다음", True, Colors.WHITE)
                        screen.blit(next_text, (next_button_x + 50, next_button_y + 10))
        else:
            # 대사 완료 후 거래 안내 표시
            title_text = font.render("거래 안내", True, Colors.WHITE)
            screen.blit(title_text, (self.trade_x + 20, self.trade_y + 30))
            
            request_text = f"{self.requested_item.upper()} {self.requested_count}개가 필요합니다"
            request_surface = font.render(request_text, True, Colors.WHITE)
            screen.blit(request_surface, (self.trade_x + 20, self.trade_y + 70))
            
            info_text = "거래하기 버튼을 누르면 인벤토리/핫바에서 자동으로 차감됩니다"
            info_surface = font.render(info_text, True, Colors.YELLOW)
            screen.blit(info_surface, (self.trade_x + 20, self.trade_y + 100))
            
            # 거래 실행 버튼
            trade_button_x = self.trade_x + self.trade_width // 2 - 75
            trade_button_y = self.trade_y + self.trade_height - 80
            button_color = Colors.GREEN
            pygame.draw.rect(screen, button_color, (trade_button_x, trade_button_y, 150, 40))
            trade_text = font.render("거래하기", True, Colors.WHITE)
            screen.blit(trade_text, (trade_button_x + 35, trade_button_y + 10))
            
            # 에러 메시지 표시
            if self.error_message:
                error_surface = font.render(self.error_message, True, Colors.RED)
                screen.blit(error_surface, (self.trade_x + 20, self.trade_y + 200))


