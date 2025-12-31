"""
인벤토리 시스템
"""
import pygame
from utils import Colors, draw_text_with_shadow
from piskel_loader import PiskelLoader


class Inventory:
    """인벤토리 클래스"""
    
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.slots = 50  # 총 50칸
        self.slots_per_row = 5  # 한 줄에 5칸
        self.max_stack = 100  # 아이템당 최대 100개
        self.items = {}  # {slot_index: {'type': str, 'count': int}}
        self.scroll_offset = 0  # 스크롤 오프셋
        self.dragging_item = None  # 드래그 중인 아이템
        self.dragging_slot = None
        self.hotbar_size = 5
        self.hotbar = {}  # {slot_index: {'type': str, 'count': int}}
        self.selected_hotbar_slot = 0  # 선택된 핫바 슬롯
        self.is_open = False  # 인벤토리 열림 상태
        
        # 인벤토리 UI 크기 (화면의 7/10)
        self.inv_width = int(screen_width * 0.7)
        self.inv_height = int(screen_height * 0.7)
        self.inv_x = (screen_width - self.inv_width) // 2
        self.inv_y = (screen_height - self.inv_height) // 2
        
        # 슬롯 크기
        self.slot_size = 50
        self.slot_spacing = 5
    
    def add_item(self, item_type, count=1):
        """아이템 추가 (핫바 우선, 그 다음 인벤토리)"""
        # 먼저 핫바에 추가 시도
        for slot_idx in range(self.hotbar_size):
            if slot_idx in self.hotbar:
                if self.hotbar[slot_idx]['type'] == item_type:
                    current_count = self.hotbar[slot_idx]['count']
                    if current_count < self.max_stack:
                        add_amount = min(count, self.max_stack - current_count)
                        self.hotbar[slot_idx]['count'] += add_amount
                        # wood_dt 추가 시 내구도 초기화
                        if item_type == 'wood_dt' and 'durability' not in self.hotbar[slot_idx]:
                            self.hotbar[slot_idx]['durability'] = 30
                            self.hotbar[slot_idx]['max_durability'] = 30
                        count -= add_amount
                        if count <= 0:
                            return True
        
        # 핫바 빈 슬롯에 추가
        for slot_idx in range(self.hotbar_size):
            if slot_idx not in self.hotbar:
                add_amount = min(count, self.max_stack)
                item_data = {'type': item_type, 'count': add_amount}
                # wood_dt는 내구도 추가
                if item_type == 'wood_dt':
                    item_data['durability'] = 30
                    item_data['max_durability'] = 30
                self.hotbar[slot_idx] = item_data
                count -= add_amount
                if count <= 0:
                    return True
        
        # 인벤토리에 추가 시도
        for slot_idx in range(self.slots):
            if slot_idx in self.items:
                if self.items[slot_idx]['type'] == item_type:
                    current_count = self.items[slot_idx]['count']
                    if current_count < self.max_stack:
                        add_amount = min(count, self.max_stack - current_count)
                        self.items[slot_idx]['count'] += add_amount
                        # wood_dt 추가 시 내구도 초기화
                        if item_type == 'wood_dt' and 'durability' not in self.items[slot_idx]:
                            self.items[slot_idx]['durability'] = 30
                            self.items[slot_idx]['max_durability'] = 30
                        count -= add_amount
                        if count <= 0:
                            return True
        
        # 인벤토리 빈 슬롯에 추가
        for slot_idx in range(self.slots):
            if slot_idx not in self.items:
                add_amount = min(count, self.max_stack)
                item_data = {'type': item_type, 'count': add_amount}
                # wood_dt는 내구도 추가
                if item_type == 'wood_dt':
                    item_data['durability'] = 30
                    item_data['max_durability'] = 30
                self.items[slot_idx] = item_data
                count -= add_amount
                if count <= 0:
                    return True
        
        return count > 0  # 일부만 추가된 경우 False
    
    def remove_item(self, slot_idx, count=1):
        """아이템 제거 (인벤토리 슬롯)"""
        if slot_idx in self.items:
            self.items[slot_idx]['count'] -= count
            if self.items[slot_idx]['count'] <= 0:
                del self.items[slot_idx]
                return True
        return False
    
    def remove_from_inventory(self, slot_idx, count=1):
        """인벤토리에서 아이템 제거"""
        return self.remove_item(slot_idx, count)
    
    def get_item_image(self, item_type):
        """아이템 이미지 가져오기"""
        image_paths = {
            'portal': 'fig/block/portal.piskel',
            'ground': 'fig/block/ground.piskel',
            'tree': 'fig/block/tree.piskel',
            'tree_leaf': 'fig/block/tree_leaf.piskel',
            'wood_plank': 'fig/block/나무판자.piskel',
            'plank_board': 'fig/block/판자판.piskel',
            'water': 'fig/block/water.piskel',
            'stick_wood': 'fig/tool/tool/stick/stick_wood.piskel',
            'wood_dt': 'fig/tool/ax/wood_DT.piskel',
        }
        
        if item_type in image_paths and image_paths[item_type]:
            image = PiskelLoader.load_piskel(image_paths[item_type])
            if image:
                return pygame.transform.scale(image, (self.slot_size - 4, self.slot_size - 4))
        
        return None
    
    def handle_mouse_wheel(self, scroll):
        """마우스 휠 처리"""
        if scroll > 0:
            self.scroll_offset = max(0, self.scroll_offset - 1)
        else:
            max_scroll = max(0, (self.slots // self.slots_per_row) - (self.inv_height // (self.slot_size + self.slot_spacing)) + 1)
            self.scroll_offset = min(max_scroll, self.scroll_offset + 1)
    
    def handle_hotbar_wheel(self, scroll):
        """핫바 휠 처리"""
        if scroll > 0:
            self.selected_hotbar_slot = (self.selected_hotbar_slot - 1) % self.hotbar_size
        else:
            self.selected_hotbar_slot = (self.selected_hotbar_slot + 1) % self.hotbar_size
    
    def get_slot_at_pos(self, pos):
        """위치에 해당하는 슬롯 인덱스 반환"""
        x, y = pos
        if not (self.inv_x <= x <= self.inv_x + self.inv_width and
                self.inv_y <= y <= self.inv_y + self.inv_height):
            return None
        
        rel_x = x - self.inv_x
        rel_y = y - self.inv_y
        
        slot_x = int(rel_x // (self.slot_size + self.slot_spacing))
        slot_y = int((rel_y // (self.slot_size + self.slot_spacing)) + self.scroll_offset)
        
        slot_idx = slot_y * self.slots_per_row + slot_x
        if 0 <= slot_idx < self.slots:
            return slot_idx
        return None
    
    def get_hotbar_slot_at_pos(self, pos):
        """핫바 위치에 해당하는 슬롯 인덱스 반환"""
        x, y = pos
        hotbar_y = self.inv_y + self.inv_height + 20 if self.is_open else self.screen_height - 70
        hotbar_x = (self.screen_width - (self.hotbar_size * (self.slot_size + self.slot_spacing))) // 2
        
        if not (hotbar_y <= y <= hotbar_y + self.slot_size):
            return None
        
        rel_x = x - hotbar_x
        if rel_x < 0:
            return None
        
        slot_idx = int(rel_x // (self.slot_size + self.slot_spacing))
        if 0 <= slot_idx < self.hotbar_size:
            return slot_idx
        return None
    
    def handle_drag(self, mouse_pos, mouse_button_down, crafting=None):
        """드래그 처리 (인벤토리 <-> 핫바 <-> 제작대)"""
        if mouse_button_down:
            # 인벤토리 슬롯에서 드래그 시작
            slot_idx = self.get_slot_at_pos(mouse_pos)
            if slot_idx is not None and slot_idx in self.items:
                if self.dragging_item is None:
                    self.dragging_item = self.items[slot_idx].copy()
                    self.dragging_slot = ('inventory', slot_idx)
                    return
            
            # 핫바 슬롯에서 드래그 시작
            hotbar_slot = self.get_hotbar_slot_at_pos(mouse_pos)
            if hotbar_slot is not None and hotbar_slot in self.hotbar:
                if self.dragging_item is None:
                    self.dragging_item = self.hotbar[hotbar_slot].copy()
                    self.dragging_slot = ('hotbar', hotbar_slot)
                    return
        else:
            # 드래그 종료
            if self.dragging_item is not None:
                source_type, source_slot = self.dragging_slot
                
                # 제작대가 열려있고 제작대 그리드에 드롭 시도
                if crafting and crafting.is_open:
                    drop_success = crafting.handle_drag_from_inventory(
                        mouse_pos, self.dragging_item, self.dragging_slot, self
                    )
                    if drop_success:
                        self.dragging_item = None
                        self.dragging_slot = None
                        return
                
                # 인벤토리 슬롯에 드롭
                slot_idx = self.get_slot_at_pos(mouse_pos)
                if slot_idx is not None:
                    if slot_idx in self.items:
                        # 같은 타입이면 합치기
                        if self.items[slot_idx]['type'] == self.dragging_item['type']:
                            total = self.items[slot_idx]['count'] + self.dragging_item['count']
                            if total <= self.max_stack:
                                self.items[slot_idx]['count'] = total
                                if source_type == 'inventory':
                                    del self.items[source_slot]
                                else:
                                    del self.hotbar[source_slot]
                            else:
                                self.items[slot_idx]['count'] = self.max_stack
                                remaining = total - self.max_stack
                                if source_type == 'inventory':
                                    self.items[source_slot]['count'] = remaining
                                else:
                                    self.hotbar[source_slot]['count'] = remaining
                        else:
                            # 교환
                            temp = self.items[slot_idx]
                            self.items[slot_idx] = self.dragging_item
                            if source_type == 'inventory':
                                self.items[source_slot] = temp
                            else:
                                self.hotbar[source_slot] = temp
                    else:
                        # 빈 슬롯에 이동
                        self.items[slot_idx] = self.dragging_item
                        if source_type == 'inventory':
                            del self.items[source_slot]
                        else:
                            del self.hotbar[source_slot]
                    
                    self.dragging_item = None
                    self.dragging_slot = None
                    return
                
                # 핫바 슬롯에 드롭
                hotbar_slot = self.get_hotbar_slot_at_pos(mouse_pos)
                if hotbar_slot is not None:
                    if hotbar_slot in self.hotbar:
                        # 같은 타입이면 합치기
                        if self.hotbar[hotbar_slot]['type'] == self.dragging_item['type']:
                            total = self.hotbar[hotbar_slot]['count'] + self.dragging_item['count']
                            if total <= self.max_stack:
                                self.hotbar[hotbar_slot]['count'] = total
                                if source_type == 'inventory':
                                    del self.items[source_slot]
                                else:
                                    del self.hotbar[source_slot]
                            else:
                                self.hotbar[hotbar_slot]['count'] = self.max_stack
                                remaining = total - self.max_stack
                                if source_type == 'inventory':
                                    self.items[source_slot]['count'] = remaining
                                else:
                                    self.hotbar[source_slot]['count'] = remaining
                        else:
                            # 교환
                            temp = self.hotbar[hotbar_slot]
                            self.hotbar[hotbar_slot] = self.dragging_item
                            if source_type == 'inventory':
                                self.items[source_slot] = temp
                            else:
                                self.hotbar[source_slot] = temp
                    else:
                        # 빈 슬롯에 이동
                        self.hotbar[hotbar_slot] = self.dragging_item
                        if source_type == 'inventory':
                            del self.items[source_slot]
                        else:
                            del self.hotbar[source_slot]
                    
                    self.dragging_item = None
                    self.dragging_slot = None
                    return
                
                # 드롭 실패 - 원래 위치로 복귀
                self.dragging_item = None
                self.dragging_slot = None
    
    def get_selected_hotbar_item(self):
        """선택된 핫바 아이템 반환"""
        if self.selected_hotbar_slot in self.hotbar:
            return self.hotbar[self.selected_hotbar_slot].copy()
        return None
    
    def add_to_hotbar(self, slot_idx, item_type, count=1):
        """핫바에 아이템 추가"""
        if slot_idx in self.hotbar:
            if self.hotbar[slot_idx]['type'] == item_type:
                self.hotbar[slot_idx]['count'] = min(self.hotbar[slot_idx]['count'] + count, self.max_stack)
            else:
                self.hotbar[slot_idx] = {'type': item_type, 'count': count}
        else:
            self.hotbar[slot_idx] = {'type': item_type, 'count': count}
    
    def remove_from_hotbar(self, slot_idx, count=1):
        """핫바에서 아이템 제거"""
        if slot_idx in self.hotbar:
            self.hotbar[slot_idx]['count'] -= count
            if self.hotbar[slot_idx]['count'] <= 0:
                del self.hotbar[slot_idx]
                return True
        return False
    
    def count_item(self, item_type):
        """특정 아이템의 총 개수 반환 (핫바 + 인벤토리)"""
        total = 0
        # 핫바에서 개수 세기
        for slot_idx in self.hotbar:
            if self.hotbar[slot_idx]['type'] == item_type:
                total += self.hotbar[slot_idx]['count']
        # 인벤토리에서 개수 세기
        for slot_idx in self.items:
            if self.items[slot_idx]['type'] == item_type:
                total += self.items[slot_idx]['count']
        return total
    
    def remove_item_type(self, item_type, count):
        """특정 아이템을 지정된 개수만큼 제거 (핫바 우선, 그 다음 인벤토리)"""
        remaining = count
        
        # 핫바에서 제거
        slots_to_remove = []
        for slot_idx in list(self.hotbar.keys()):
            if remaining <= 0:
                break
            if self.hotbar[slot_idx]['type'] == item_type:
                remove_amount = min(remaining, self.hotbar[slot_idx]['count'])
                self.hotbar[slot_idx]['count'] -= remove_amount
                remaining -= remove_amount
                if self.hotbar[slot_idx]['count'] <= 0:
                    slots_to_remove.append(slot_idx)
        
        # 빈 슬롯 제거
        for slot_idx in slots_to_remove:
            del self.hotbar[slot_idx]
        
        # 인벤토리에서 제거
        slots_to_remove = []
        for slot_idx in list(self.items.keys()):
            if remaining <= 0:
                break
            if self.items[slot_idx]['type'] == item_type:
                remove_amount = min(remaining, self.items[slot_idx]['count'])
                self.items[slot_idx]['count'] -= remove_amount
                remaining -= remove_amount
                if self.items[slot_idx]['count'] <= 0:
                    slots_to_remove.append(slot_idx)
        
        # 빈 슬롯 제거
        for slot_idx in slots_to_remove:
            del self.items[slot_idx]
        
        return remaining == 0  # 모든 아이템을 제거했는지 반환
    
    def draw(self, screen, font, is_open):
        """인벤토리 그리기"""
        self.is_open = is_open
        if not is_open:
            # 핫바만 그리기
            self.draw_hotbar(screen, font)
            # 드래그 중인 아이템 그리기
            if self.dragging_item:
                mouse_pos = pygame.mouse.get_pos()
                item_image = self.get_item_image(self.dragging_item['type'])
                if item_image:
                    screen.blit(item_image, (mouse_pos[0] - self.slot_size // 2, mouse_pos[1] - self.slot_size // 2))
            return
        
        # 인벤토리 배경
        inv_surface = pygame.Surface((self.inv_width, self.inv_height))
        inv_surface.fill((50, 50, 50))
        inv_surface.set_alpha(240)
        screen.blit(inv_surface, (self.inv_x, self.inv_y))
        
        # 테두리
        pygame.draw.rect(screen, Colors.WHITE, 
                        (self.inv_x, self.inv_y, self.inv_width, self.inv_height), 3)
        
        # 슬롯 그리기
        visible_rows = self.inv_height // (self.slot_size + self.slot_spacing)
        for row in range(visible_rows):
            for col in range(self.slots_per_row):
                slot_idx = (row + self.scroll_offset) * self.slots_per_row + col
                if slot_idx >= self.slots:
                    continue
                
                slot_x = self.inv_x + col * (self.slot_size + self.slot_spacing) + 10
                slot_y = self.inv_y + row * (self.slot_size + self.slot_spacing) + 10
                
                # 슬롯 배경
                pygame.draw.rect(screen, Colors.DARK_GRAY,
                               (slot_x, slot_y, self.slot_size, self.slot_size))
                pygame.draw.rect(screen, Colors.WHITE,
                               (slot_x, slot_y, self.slot_size, self.slot_size), 2)
                
                # 아이템 그리기
                if slot_idx in self.items:
                    item = self.items[slot_idx]
                    item_image = self.get_item_image(item['type'])
                    if item_image:
                        screen.blit(item_image, (slot_x + 2, slot_y + 2))
                    
                    # 개수 표시
                    if item['count'] > 1:
                        count_text = font.render(str(item['count']), True, Colors.WHITE)
                        screen.blit(count_text, (slot_x + 2, slot_y + self.slot_size - 15))
        
        # 핫바 그리기
        self.draw_hotbar(screen, font, is_inventory_open=True)
        
        # 드래그 중인 아이템 그리기
        if self.dragging_item:
            mouse_pos = pygame.mouse.get_pos()
            item_image = self.get_item_image(self.dragging_item['type'])
            if item_image:
                screen.blit(item_image, (mouse_pos[0] - self.slot_size // 2, mouse_pos[1] - self.slot_size // 2))
                # 개수 표시
                if self.dragging_item['count'] > 1:
                    count_text = font.render(str(self.dragging_item['count']), True, Colors.WHITE)
                    screen.blit(count_text, (mouse_pos[0] - self.slot_size // 2 + 2, mouse_pos[1] - self.slot_size // 2 + self.slot_size - 15))
    
    def draw_hotbar(self, screen, font, is_inventory_open=False):
        """핫바 그리기"""
        if is_inventory_open:
            hotbar_y = self.inv_y + self.inv_height + 20
        else:
            hotbar_y = self.screen_height - 70
        hotbar_x = (self.screen_width - (self.hotbar_size * (self.slot_size + self.slot_spacing))) // 2
        
        for i in range(self.hotbar_size):
            slot_x = hotbar_x + i * (self.slot_size + self.slot_spacing)
            
            # 선택된 슬롯 강조
            if i == self.selected_hotbar_slot:
                pygame.draw.rect(screen, Colors.YELLOW,
                               (slot_x - 2, hotbar_y - 2, self.slot_size + 4, self.slot_size + 4))
            
            # 슬롯 배경
            pygame.draw.rect(screen, Colors.DARK_GRAY,
                           (slot_x, hotbar_y, self.slot_size, self.slot_size))
            pygame.draw.rect(screen, Colors.WHITE,
                           (slot_x, hotbar_y, self.slot_size, self.slot_size), 2)
            
            # 아이템 그리기
            if i in self.hotbar:
                item = self.hotbar[i]
                item_image = self.get_item_image(item['type'])
                if item_image:
                    screen.blit(item_image, (slot_x + 2, hotbar_y + 2))
                
                # 개수 표시
                if item['count'] > 1:
                    count_text = font.render(str(item['count']), True, Colors.WHITE)
                    screen.blit(count_text, (slot_x + 2, hotbar_y + self.slot_size - 15))
    
    def get_hover_item_name(self, mouse_pos):
        """마우스 위치의 아이템 이름 반환"""
        slot_idx = self.get_slot_at_pos(mouse_pos)
        if slot_idx is not None and slot_idx in self.items:
            return self.items[slot_idx]['type']
        return None

