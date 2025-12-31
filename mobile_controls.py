"""
모바일 컨트롤 시스템
가상 조이스틱과 버튼을 제공합니다.
"""
import pygame
import math
from utils import Colors


class VirtualJoystick:
    """가상 조이스틱 클래스"""
    
    def __init__(self, x, y, radius=60):
        self.center_x = x
        self.center_y = y
        self.radius = radius
        self.stick_radius = 25
        self.stick_x = x
        self.stick_y = y
        self.is_active = False
        self.touch_id = None
        
    def handle_touch_down(self, touch_pos, touch_id):
        """터치 시작 처리"""
        dx = touch_pos[0] - self.center_x
        dy = touch_pos[1] - self.center_y
        distance = math.sqrt(dx * dx + dy * dy)
        
        if distance <= self.radius:
            self.is_active = True
            self.touch_id = touch_id
            self.update_stick(touch_pos)
            return True
        return False
    
    def handle_touch_move(self, touch_pos, touch_id):
        """터치 이동 처리"""
        if self.is_active and self.touch_id == touch_id:
            self.update_stick(touch_pos)
            return True
        return False
    
    def handle_touch_up(self, touch_id):
        """터치 종료 처리"""
        if self.is_active and self.touch_id == touch_id:
            self.is_active = False
            self.touch_id = None
            self.stick_x = self.center_x
            self.stick_y = self.center_y
            return True
        return False
    
    def update_stick(self, touch_pos):
        """스틱 위치 업데이트"""
        dx = touch_pos[0] - self.center_x
        dy = touch_pos[1] - self.center_y
        distance = math.sqrt(dx * dx + dy * dy)
        
        if distance <= self.radius:
            self.stick_x = touch_pos[0]
            self.stick_y = touch_pos[1]
        else:
            # 조이스틱 범위 밖이면 최대 거리로 제한
            angle = math.atan2(dy, dx)
            self.stick_x = self.center_x + math.cos(angle) * self.radius
            self.stick_y = self.center_y + math.sin(angle) * self.radius
    
    def get_direction(self):
        """조이스틱 방향 벡터 반환 (-1.0 ~ 1.0)"""
        if not self.is_active:
            return 0.0, 0.0
        
        dx = (self.stick_x - self.center_x) / self.radius
        dy = (self.stick_y - self.center_y) / self.radius
        
        return dx, dy
    
    def draw(self, screen):
        """조이스틱 그리기"""
        # 배경 원
        pygame.draw.circle(screen, (100, 100, 100, 180), 
                          (int(self.center_x), int(self.center_y)), 
                          self.radius, 3)
        pygame.draw.circle(screen, (50, 50, 50, 200), 
                          (int(self.center_x), int(self.center_y)), 
                          self.radius)
        
        # 스틱
        pygame.draw.circle(screen, (150, 150, 150), 
                          (int(self.stick_x), int(self.stick_y)), 
                          self.stick_radius)
        pygame.draw.circle(screen, Colors.WHITE, 
                          (int(self.stick_x), int(self.stick_y)), 
                          self.stick_radius, 2)


class MobileButton:
    """모바일 버튼 클래스"""
    
    def __init__(self, x, y, width, height, text="", color=Colors.DARK_GRAY, text_color=Colors.WHITE):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.text_color = text_color
        self.pressed = False
        self.touch_id = None
        self.alpha = 200
        self.was_pressed = False  # 이전 프레임에 눌렸는지 확인
        self.clicked = False  # 한 번만 클릭되었는지 확인
        
    def handle_touch_down(self, touch_pos, touch_id):
        """터치 시작 처리"""
        if self.rect.collidepoint(touch_pos):
            self.pressed = True
            self.touch_id = touch_id
            return True
        return False
    
    def handle_touch_up(self, touch_id):
        """터치 종료 처리"""
        if self.pressed and self.touch_id == touch_id:
            self.pressed = False
            self.touch_id = None
            # 클릭 이벤트 발생 (눌렸다가 떼어졌을 때)
            if self.was_pressed:
                self.clicked = True
            return True
        return False
    
    def is_pressed(self):
        """버튼이 눌려있는지 확인"""
        return self.pressed
    
    def is_clicked(self):
        """버튼이 클릭되었는지 확인 (한 번만)"""
        if self.clicked:
            self.clicked = False
            return True
        return False
    
    def update(self):
        """프레임 업데이트 (이전 상태 저장)"""
        self.was_pressed = self.pressed
    
    def draw(self, screen, font):
        """버튼 그리기"""
        color = self.color
        if self.pressed:
            # 눌렸을 때 더 밝게
            color = tuple(min(255, c + 30) for c in self.color[:3])
        
        button_surface = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        button_surface.fill((*color[:3], self.alpha))
        screen.blit(button_surface, self.rect)
        
        pygame.draw.rect(screen, Colors.WHITE, self.rect, 2)
        
        if self.text:
            text_surface = font.render(self.text, True, self.text_color)
            text_rect = text_surface.get_rect(center=self.rect.center)
            screen.blit(text_surface, text_rect)


class MobileControls:
    """모바일 컨트롤 시스템"""
    
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.is_mobile = False
        
        # 조이스틱 (왼쪽 하단)
        joystick_x = 80
        joystick_y = screen_height - 100
        self.joystick = VirtualJoystick(joystick_x, joystick_y, 60)
        
        # 점프 버튼 (오른쪽 하단)
        jump_size = 70
        jump_x = screen_width - jump_size - 20
        jump_y = screen_height - jump_size - 20
        self.jump_button = MobileButton(jump_x, jump_y, jump_size, jump_size, 
                                        "점프", Colors.BLUE)
        
        # 채굴/공격 버튼 (점프 버튼 왼쪽)
        mine_size = 70
        mine_x = jump_x - mine_size - 15
        mine_y = jump_y
        self.mine_button = MobileButton(mine_x, mine_y, mine_size, mine_size, 
                                         "채굴", Colors.RED)
        
        # 설치 버튼 (채굴 버튼 왼쪽)
        place_size = 70
        place_x = mine_x - place_size - 15
        place_y = mine_y
        self.place_button = MobileButton(place_x, place_y, place_size, place_size, 
                                         "설치", Colors.GREEN)
        
        # 인벤토리 버튼 (우측 상단)
        inv_size = 50
        inv_x = screen_width - inv_size - 10
        inv_y = 10
        self.inventory_button = MobileButton(inv_x, inv_y, inv_size, inv_size, 
                                             "I", Colors.DARK_GRAY)
        
        # 제작대 버튼 (인벤토리 버튼 아래)
        craft_size = 50
        craft_x = inv_x
        craft_y = inv_y + craft_size + 10
        self.crafting_button = MobileButton(craft_x, craft_y, craft_size, craft_size, 
                                            "C", Colors.BROWN)
        
        # 채팅 버튼 (제작대 버튼 아래)
        chat_size = 50
        chat_x = craft_x
        chat_y = craft_y + chat_size + 10
        self.chat_button = MobileButton(chat_x, chat_y, chat_size, chat_size, 
                                        "T", Colors.DARK_GRAY)
        
        # 핫바 슬롯 선택 버튼들 (화면 하단 중앙)
        self.hotbar_buttons = []
        hotbar_size = 5
        button_size = 50
        button_spacing = 5
        total_width = hotbar_size * button_size + (hotbar_size - 1) * button_spacing
        start_x = (screen_width - total_width) // 2
        hotbar_y = screen_height - 60
        
        for i in range(hotbar_size):
            btn_x = start_x + i * (button_size + button_spacing)
            btn = MobileButton(btn_x, hotbar_y, button_size, button_size, 
                              str(i + 1), Colors.DARK_GRAY)
            self.hotbar_buttons.append(btn)
    
    def detect_mobile(self):
        """모바일 환경 감지"""
        # 터치 이벤트가 있으면 모바일로 간주
        if pygame.version.vernum >= (2, 0, 0):
            # pygame 2.0+ 에서는 터치 이벤트 지원
            self.is_mobile = True
        # 화면 크기로도 판단 (작은 화면이면 모바일로 간주)
        if self.screen_width < 800 or self.screen_height < 600:
            self.is_mobile = True
        return self.is_mobile
    
    def update(self):
        """모든 버튼 업데이트"""
        self.jump_button.update()
        self.mine_button.update()
        self.place_button.update()
        self.inventory_button.update()
        self.crafting_button.update()
        self.chat_button.update()
        for btn in self.hotbar_buttons:
            btn.update()
    
    def handle_touch_event(self, event):
        """터치 이벤트 처리"""
        if event.type == pygame.FINGERDOWN:
            touch_pos = (int(event.x * self.screen_width), 
                        int(event.y * self.screen_height))
            touch_id = event.finger_id
            
            # 조이스틱
            if self.joystick.handle_touch_down(touch_pos, touch_id):
                return True
            
            # 점프 버튼
            if self.jump_button.handle_touch_down(touch_pos, touch_id):
                return True
            
            # 채굴 버튼
            if self.mine_button.handle_touch_down(touch_pos, touch_id):
                return True
            
            # 설치 버튼
            if self.place_button.handle_touch_down(touch_pos, touch_id):
                return True
            
            # 인벤토리 버튼
            if self.inventory_button.handle_touch_down(touch_pos, touch_id):
                return True
            
            # 제작대 버튼
            if self.crafting_button.handle_touch_down(touch_pos, touch_id):
                return True
            
            # 채팅 버튼
            if self.chat_button.handle_touch_down(touch_pos, touch_id):
                return True
            
            # 핫바 버튼들
            for i, btn in enumerate(self.hotbar_buttons):
                if btn.handle_touch_down(touch_pos, touch_id):
                    return True
        
        elif event.type == pygame.FINGERMOTION:
            touch_pos = (int(event.x * self.screen_width), 
                        int(event.y * self.screen_height))
            touch_id = event.finger_id
            
            # 조이스틱
            self.joystick.handle_touch_move(touch_pos, touch_id)
            
            # 버튼들은 이동 시 처리하지 않음
        
        elif event.type == pygame.FINGERUP:
            touch_id = event.finger_id
            
            # 조이스틱
            self.joystick.handle_touch_up(touch_id)
            
            # 점프 버튼
            self.jump_button.handle_touch_up(touch_id)
            
            # 채굴 버튼
            self.mine_button.handle_touch_up(touch_id)
            
            # 설치 버튼
            self.place_button.handle_touch_up(touch_id)
            
            # 인벤토리 버튼
            self.inventory_button.handle_touch_up(touch_id)
            
            # 제작대 버튼
            self.crafting_button.handle_touch_up(touch_id)
            
            # 채팅 버튼
            self.chat_button.handle_touch_up(touch_id)
            
            # 핫바 버튼들
            for btn in self.hotbar_buttons:
                btn.handle_touch_up(touch_id)
        
        return False
    
    def handle_mouse_event(self, event):
        """마우스 이벤트를 터치로 변환 (데스크톱에서 테스트용)"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # 좌클릭
                touch_pos = event.pos
                touch_id = 0
                
                # 조이스틱
                if self.joystick.handle_touch_down(touch_pos, touch_id):
                    return True
                
                # 점프 버튼
                if self.jump_button.handle_touch_down(touch_pos, touch_id):
                    return True
                
                # 채굴 버튼
                if self.mine_button.handle_touch_down(touch_pos, touch_id):
                    return True
                
                # 설치 버튼
                if self.place_button.handle_touch_down(touch_pos, touch_id):
                    return True
                
                # 인벤토리 버튼
                if self.inventory_button.handle_touch_down(touch_pos, touch_id):
                    return True
                
                # 제작대 버튼
                if self.crafting_button.handle_touch_down(touch_pos, touch_id):
                    return True
                
                # 채팅 버튼
                if self.chat_button.handle_touch_down(touch_pos, touch_id):
                    return True
                
                # 핫바 버튼들
                for i, btn in enumerate(self.hotbar_buttons):
                    if btn.handle_touch_down(touch_pos, touch_id):
                        return True
        
        elif event.type == pygame.MOUSEMOTION:
            if pygame.mouse.get_pressed()[0]:  # 마우스가 눌려있는 동안
                touch_pos = event.pos
                touch_id = 0
                self.joystick.handle_touch_move(touch_pos, touch_id)
        
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:  # 좌클릭 해제
                touch_id = 0
                
                self.joystick.handle_touch_up(touch_id)
                self.jump_button.handle_touch_up(touch_id)
                self.mine_button.handle_touch_up(touch_id)
                self.place_button.handle_touch_up(touch_id)
                self.inventory_button.handle_touch_up(touch_id)
                self.crafting_button.handle_touch_up(touch_id)
                self.chat_button.handle_touch_up(touch_id)
                
                for btn in self.hotbar_buttons:
                    btn.handle_touch_up(touch_id)
        
        return False
    
    def get_movement_input(self):
        """이동 입력 반환 (조이스틱)
        Returns:
            (dx, dy): x 방향 (-1.0 ~ 1.0), y 방향은 사용하지 않음 (점프는 별도 버튼)
        """
        dx, dy = self.joystick.get_direction()
        # x 방향만 반환 (y는 점프 버튼으로 처리)
        return dx, 0.0
    
    def is_jump_pressed(self):
        """점프 버튼이 눌려있는지 확인"""
        return self.jump_button.is_pressed()
    
    def is_mine_pressed(self):
        """채굴 버튼이 눌려있는지 확인"""
        return self.mine_button.is_pressed()
    
    def is_place_pressed(self):
        """설치 버튼이 눌려있는지 확인"""
        return self.place_button.is_pressed()
    
    def get_inventory_button_click(self):
        """인벤토리 버튼 클릭 확인 (한 번만)"""
        if self.inventory_button.is_pressed():
            # 버튼이 눌렸다가 떼어졌을 때만 True 반환
            # 실제로는 이벤트 기반으로 처리해야 함
            return False
        return False
    
    def get_crafting_button_click(self):
        """제작대 버튼 클릭 확인"""
        return False
    
    def get_chat_button_click(self):
        """채팅 버튼 클릭 확인"""
        return False
    
    def get_hotbar_selection(self):
        """핫바 버튼 선택 확인 (인덱스 반환)"""
        for i, btn in enumerate(self.hotbar_buttons):
            if btn.is_pressed():
                return i
        return None
    
    def draw(self, screen, font):
        """모바일 컨트롤 그리기"""
        # 조이스틱
        self.joystick.draw(screen)
        
        # 점프 버튼
        self.jump_button.draw(screen, font)
        
        # 채굴 버튼
        self.mine_button.draw(screen, font)
        
        # 설치 버튼
        self.place_button.draw(screen, font)
        
        # 인벤토리 버튼
        self.inventory_button.draw(screen, font)
        
        # 제작대 버튼
        self.crafting_button.draw(screen, font)
        
        # 채팅 버튼
        self.chat_button.draw(screen, font)
        
        # 핫바 버튼들
        for btn in self.hotbar_buttons:
            btn.draw(screen, font)

