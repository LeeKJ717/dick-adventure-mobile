"""
제작 시스템
"""
import pygame
from utils import Colors, draw_text_with_shadow
from piskel_loader import PiskelLoader


class Crafting:
    """제작 시스템 클래스"""
    
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.is_open = False
        self.crafting_grid = {}  # {(x, y): {'type': str, 'count': int}}
        self.result_item = None
        self.search_text = ""
        self.show_search = False
        self.dragging_item = None  # 드래그 중인 아이템
        self.dragging_source = None  # 드래그 소스 ('grid', (x, y)) 또는 ('result', None)
        self.max_stack = 100  # 제작대 슬롯당 최대 100개
        
        # 제작대 UI 크기
        self.craft_width = 600
        self.craft_height = 500
        self.craft_x = (screen_width - self.craft_width) // 2
        self.craft_y = (screen_height - self.craft_height) // 2
        
        # 제작 레시피
        self.recipes = {
            'wood_plank': [{'type': 'tree', 'count': 1}],
            'plank_board': [{'type': 'wood_plank', 'count': 1}],  # 4개 나옴
            'stick_wood': [{'type': 'plank_board', 'count': 2}],
            'wood_dt': [{'type': 'stick_wood', 'count': 2}],
        }
        
        # 제작 결과 개수
        self.result_counts = {
            'wood_plank': 1,
            'plank_board': 4,
            'stick_wood': 1,
            'wood_dt': 1,
        }
        
        self.slot_size = 50
    
    def check_recipe(self):
        """현재 제작 그리드에서 레시피 확인"""
        # 그리드의 모든 아이템 수집
        grid_items = {}
        for pos, item in self.crafting_grid.items():
            if item['type'] not in grid_items:
                grid_items[item['type']] = 0
            grid_items[item['type']] += item['count']
        
        # 레시피 확인
        for result_type, recipe in self.recipes.items():
            match = True
            for ingredient in recipe:
                if ingredient['type'] not in grid_items:
                    match = False
                    break
                if grid_items[ingredient['type']] < ingredient['count']:
                    match = False
                    break
            
            if match:
                # 추가 재료가 없는지 확인
                total_needed = sum(ing['count'] for ing in recipe)
                total_in_grid = sum(item['count'] for item in self.crafting_grid.values())
                if total_in_grid == total_needed:
                    self.result_item = result_type
                    return result_type
        
        self.result_item = None
        return None
    
    def craft(self, inventory, add_to_inventory=True):
        """제작 실행
        
        Args:
            inventory: 인벤토리 객체
            add_to_inventory: True면 결과물을 인벤토리에 추가, False면 추가하지 않음 (드래그 시 사용)
        """
        if self.result_item is None:
            return False
        
        # 재료 소모
        recipe = self.recipes[self.result_item]
        grid_items = {}
        for pos, item in self.crafting_grid.items():
            if item['type'] not in grid_items:
                grid_items[item['type']] = []
            grid_items[item['type']].append((pos, item))
        
        # 재료가 충분한지 확인
        for ingredient in recipe:
            total_count = sum(item['count'] for item in self.crafting_grid.values() 
                            if item['type'] == ingredient['type'])
            if total_count < ingredient['count']:
                return False
        
        # 재료 소모
        for ingredient in recipe:
            needed = ingredient['count']
            if ingredient['type'] in grid_items:
                for pos, item in grid_items[ingredient['type']]:
                    if needed > 0:
                        remove_count = min(needed, item['count'])
                        item['count'] -= remove_count
                        needed -= remove_count
                        if item['count'] <= 0:
                            del self.crafting_grid[pos]
        
        # 결과물 추가 (드래그로 가져가는 경우는 추가하지 않음)
        if add_to_inventory:
            result_count = self.result_counts.get(self.result_item, 1)
            inventory.add_item(self.result_item, result_count)
        
        # 레시피 다시 확인
        self.check_recipe()
        return True
    
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
    
    def get_grid_slot_at_pos(self, pos):
        """제작 그리드 위치에 해당하는 슬롯 반환"""
        x, y = pos
        grid_start_x = self.craft_x + 100
        grid_start_y = self.craft_y + 50
        for grid_y in range(2):
            for grid_x in range(2):
                slot_x = grid_start_x + grid_x * (self.slot_size + 5)
                slot_y = grid_start_y + grid_y * (self.slot_size + 5)
                slot_rect = pygame.Rect(slot_x, slot_y, self.slot_size, self.slot_size)
                if slot_rect.collidepoint(x, y):
                    return (grid_x, grid_y)
        return None
    
    def get_result_slot_at_pos(self, pos):
        """결과물 슬롯 위치 확인"""
        x, y = pos
        grid_start_x = self.craft_x + 100
        grid_start_y = self.craft_y + 50
        result_x = grid_start_x + 2 * (self.slot_size + 5) + 20
        result_y = grid_start_y
        result_rect = pygame.Rect(result_x, result_y, self.slot_size, self.slot_size)
        if result_rect.collidepoint(x, y):
            return True
        return False
    
    def handle_click(self, pos, inventory):
        """클릭 처리"""
        x, y = pos
        
        # 제작 버튼
        button_x = self.craft_x + self.craft_width // 2 - 50
        button_y = self.craft_y + 200
        button_rect = pygame.Rect(button_x, button_y, 100, 30)
        if button_rect.collidepoint(x, y):
            self.craft(inventory)
            return
        
        # 책 버튼 (검색)
        book_x = self.craft_x + 20
        book_y = self.craft_y + 20
        book_rect = pygame.Rect(book_x, book_y, 40, 40)
        if book_rect.collidepoint(x, y):
            self.show_search = not self.show_search
            return
        
        # 제작 그리드 (2x2) - 클릭으로 아이템 추가 (기존 기능 유지)
        grid_pos = self.get_grid_slot_at_pos(pos)
        if grid_pos is not None:
            # 인벤토리에서 아이템 가져오기
            selected = inventory.get_selected_hotbar_item()
            if selected:
                if grid_pos in self.crafting_grid:
                    if self.crafting_grid[grid_pos]['type'] == selected['type']:
                        # 같은 타입이면 합치기 (최대 100개)
                        if self.crafting_grid[grid_pos]['count'] < self.max_stack:
                            self.crafting_grid[grid_pos]['count'] += 1
                            # 핫바에서 아이템 제거
                            inventory.remove_from_hotbar(inventory.selected_hotbar_slot, 1)
                    else:
                        # 다른 타입이면 교환
                        temp = self.crafting_grid[grid_pos]
                        self.crafting_grid[grid_pos] = {'type': selected['type'], 'count': 1}
                        # 핫바에서 아이템 제거하고 교환된 아이템 추가
                        inventory.remove_from_hotbar(inventory.selected_hotbar_slot, 1)
                        inventory.add_item(temp['type'], temp['count'])
                else:
                    # 빈 슬롯에 추가
                    self.crafting_grid[grid_pos] = {'type': selected['type'], 'count': 1}
                    # 핫바에서 아이템 제거
                    inventory.remove_from_hotbar(inventory.selected_hotbar_slot, 1)
                self.check_recipe()
            return
        
        # 결과물 슬롯 - 클릭으로 아이템 가져오기 (기존 기능 유지)
        if self.get_result_slot_at_pos(pos):
            if self.result_item:
                inventory.add_item(self.result_item, self.result_counts.get(self.result_item, 1))
                # 재료 소모
                self.craft(inventory)
    
    def handle_drag_from_inventory(self, mouse_pos, dragging_item, dragging_source, inventory):
        """인벤토리에서 제작대로 드래그 앤 드롭 처리"""
        if dragging_item is None:
            return None
        
        # 제작 그리드에 드롭
        grid_pos = self.get_grid_slot_at_pos(mouse_pos)
        if grid_pos is not None:
            if grid_pos in self.crafting_grid:
                # 같은 타입이면 합치기 (최대 100개)
                if self.crafting_grid[grid_pos]['type'] == dragging_item['type']:
                    total = self.crafting_grid[grid_pos]['count'] + dragging_item['count']
                    if total <= self.max_stack:
                        self.crafting_grid[grid_pos]['count'] = total
                        # 인벤토리/핫바에서 제거
                        if dragging_source[0] == 'inventory':
                            del inventory.items[dragging_source[1]]
                        else:
                            del inventory.hotbar[dragging_source[1]]
                        self.check_recipe()
                        return True  # 드롭 성공
                    else:
                        # 최대치까지 채우고 남은 것은 원래 위치에 유지
                        add_amount = self.max_stack - self.crafting_grid[grid_pos]['count']
                        self.crafting_grid[grid_pos]['count'] = self.max_stack
                        # 인벤토리/핫바에서 일부만 제거
                        if dragging_source[0] == 'inventory':
                            inventory.items[dragging_source[1]]['count'] -= add_amount
                            if inventory.items[dragging_source[1]]['count'] <= 0:
                                del inventory.items[dragging_source[1]]
                        else:
                            inventory.hotbar[dragging_source[1]]['count'] -= add_amount
                            if inventory.hotbar[dragging_source[1]]['count'] <= 0:
                                del inventory.hotbar[dragging_source[1]]
                        self.check_recipe()
                        return True  # 드롭 성공 (일부만)
                else:
                    # 교환
                    temp = self.crafting_grid[grid_pos]
                    self.crafting_grid[grid_pos] = dragging_item.copy()
                    # 인벤토리/핫바에 교환된 아이템 배치
                    if dragging_source[0] == 'inventory':
                        inventory.items[dragging_source[1]] = temp
                    else:
                        inventory.hotbar[dragging_source[1]] = temp
                    self.check_recipe()
                    return True  # 드롭 성공
            else:
                # 빈 슬롯에 이동
                self.crafting_grid[grid_pos] = dragging_item.copy()
                # 인벤토리/핫바에서 제거
                if dragging_source[0] == 'inventory':
                    del inventory.items[dragging_source[1]]
                else:
                    del inventory.hotbar[dragging_source[1]]
                self.check_recipe()
                return True  # 드롭 성공
        
        return False  # 드롭 실패
    
    def handle_drag(self, mouse_pos, mouse_button_down, inventory):
        """드래그 처리 (제작대 <-> 인벤토리/핫바)"""
        if mouse_button_down:
            # 제작 그리드에서 드래그 시작
            grid_pos = self.get_grid_slot_at_pos(mouse_pos)
            if grid_pos is not None and grid_pos in self.crafting_grid:
                if self.dragging_item is None:
                    # 드래그 시작 시 원본 아이템 복사 및 제거 (복사 버그 방지)
                    self.dragging_item = self.crafting_grid[grid_pos].copy()
                    self.dragging_source = ('grid', grid_pos)
                    # 원본 제거 (드롭 실패 시 복원)
                    del self.crafting_grid[grid_pos]
                    self.check_recipe()
                    return
            
            # 결과물 슬롯에서 드래그 시작
            if self.get_result_slot_at_pos(mouse_pos) and self.result_item:
                if self.dragging_item is None:
                    result_count = self.result_counts.get(self.result_item, 1)
                    self.dragging_item = {'type': self.result_item, 'count': result_count}
                    self.dragging_source = ('result', None)
                    # 결과물은 드롭 성공 시에만 제작 실행하므로 여기서는 제거하지 않음
                    # 하지만 드래그 중에는 결과물 슬롯에서 보이지 않도록 처리
                    return
        else:
            # 드래그 종료
            if self.dragging_item is not None:
                source_type, source_pos = self.dragging_source
                
                # 인벤토리 슬롯에 드롭 (인벤토리가 열려있을 때만)
                slot_idx = None
                if inventory.is_open:
                    slot_idx = inventory.get_slot_at_pos(mouse_pos)
                if slot_idx is not None:
                    if slot_idx in inventory.items:
                        # 같은 타입이면 합치기
                        if inventory.items[slot_idx]['type'] == self.dragging_item['type']:
                            total = inventory.items[slot_idx]['count'] + self.dragging_item['count']
                            if total <= inventory.max_stack:
                                inventory.items[slot_idx]['count'] = total
                                # 원본은 이미 드래그 시작 시 제거됨 (grid인 경우)
                                # 결과물인 경우 제작 실행 (재료 소모만)
                                if source_type == 'result':
                                    self.craft(inventory, add_to_inventory=False)
                            else:
                                inventory.items[slot_idx]['count'] = inventory.max_stack
                                remaining = total - inventory.max_stack
                                # 남은 아이템을 원래 위치에 복원
                                if source_type == 'grid':
                                    self.crafting_grid[source_pos] = {'type': self.dragging_item['type'], 'count': remaining}
                                    self.check_recipe()
                                elif source_type == 'result':
                                    # 결과물인 경우 남은 아이템은 버림 (이미 제작됨)
                                    pass
                            self.dragging_item = None
                            self.dragging_source = None
                            return
                        else:
                            # 교환
                            temp = inventory.items[slot_idx]
                            inventory.items[slot_idx] = self.dragging_item
                            # 원래 위치에 교환된 아이템 배치
                            if source_type == 'grid':
                                self.crafting_grid[source_pos] = temp
                            elif source_type == 'result':
                                # 결과물인 경우 제작 실행 (재료 소모만)
                                self.craft(inventory, add_to_inventory=False)
                            self.check_recipe()
                            self.dragging_item = None
                            self.dragging_source = None
                            return
                    else:
                        # 빈 슬롯에 이동
                        inventory.items[slot_idx] = self.dragging_item
                        # 원래 위치는 이미 드래그 시작 시 제거됨 (grid인 경우)
                        if source_type == 'result':
                            # 결과물은 제작 실행 (재료 소모만, 결과물은 드래그 아이템으로 이미 추가됨)
                            self.craft(inventory, add_to_inventory=False)
                    
                    self.check_recipe()
                    self.dragging_item = None
                    self.dragging_source = None
                    return
                
                # 핫바 슬롯에 드롭 (항상 가능)
                hotbar_slot = inventory.get_hotbar_slot_at_pos(mouse_pos)
                if hotbar_slot is not None:
                    if hotbar_slot in inventory.hotbar:
                        # 같은 타입이면 합치기
                        if inventory.hotbar[hotbar_slot]['type'] == self.dragging_item['type']:
                            total = inventory.hotbar[hotbar_slot]['count'] + self.dragging_item['count']
                            if total <= inventory.max_stack:
                                inventory.hotbar[hotbar_slot]['count'] = total
                                # 원본은 이미 드래그 시작 시 제거됨 (grid인 경우)
                                # 결과물인 경우 제작 실행 (재료 소모만)
                                if source_type == 'result':
                                    self.craft(inventory, add_to_inventory=False)
                            else:
                                inventory.hotbar[hotbar_slot]['count'] = inventory.max_stack
                                remaining = total - inventory.max_stack
                                # 남은 아이템을 원래 위치에 복원
                                if source_type == 'grid':
                                    self.crafting_grid[source_pos] = {'type': self.dragging_item['type'], 'count': remaining}
                                    self.check_recipe()
                                elif source_type == 'result':
                                    # 결과물인 경우 남은 아이템은 버림 (이미 제작됨)
                                    pass
                            self.dragging_item = None
                            self.dragging_source = None
                            return
                        else:
                            # 교환
                            temp = inventory.hotbar[hotbar_slot]
                            inventory.hotbar[hotbar_slot] = self.dragging_item
                            # 원래 위치에 교환된 아이템 배치
                            if source_type == 'grid':
                                self.crafting_grid[source_pos] = temp
                            elif source_type == 'result':
                                # 결과물인 경우 제작 실행 (재료 소모만)
                                self.craft(inventory, add_to_inventory=False)
                            self.check_recipe()
                            self.dragging_item = None
                            self.dragging_source = None
                            return
                    else:
                        # 빈 슬롯에 이동
                        inventory.hotbar[hotbar_slot] = self.dragging_item
                        # 원래 위치는 이미 드래그 시작 시 제거됨 (grid인 경우)
                        if source_type == 'result':
                            # 결과물은 제작 실행 (재료 소모만, 결과물은 드래그 아이템으로 이미 추가됨)
                            self.craft(inventory, add_to_inventory=False)
                    
                    self.check_recipe()
                    self.dragging_item = None
                    self.dragging_source = None
                    return
                
                # 드롭 실패 - 원래 위치로 복귀
                if self.dragging_item is not None:
                    source_type, source_pos = self.dragging_source
                    if source_type == 'grid':
                        # 제작 그리드에 원본 복원
                        self.crafting_grid[source_pos] = self.dragging_item
                        self.check_recipe()
                    # result인 경우는 드래그 시작 시 제거하지 않았으므로 복원 불필요
                    self.dragging_item = None
                    self.dragging_source = None
    
    def draw(self, screen, font, inventory):
        """제작대 그리기"""
        if not self.is_open:
            return
        
        # 배경
        craft_surface = pygame.Surface((self.craft_width, self.craft_height))
        craft_surface.fill((50, 50, 50))
        craft_surface.set_alpha(240)
        screen.blit(craft_surface, (self.craft_x, self.craft_y))
        
        # 테두리
        pygame.draw.rect(screen, Colors.WHITE,
                        (self.craft_x, self.craft_y, self.craft_width, self.craft_height), 3)
        
        # 책 버튼 (검색)
        book_x = self.craft_x + 20
        book_y = self.craft_y + 20
        pygame.draw.rect(screen, Colors.BROWN, (book_x, book_y, 40, 40))
        book_text = font.render("Book", True, Colors.WHITE)
        screen.blit(book_text, (book_x + 5, book_y + 10))
        
        # 제작 그리드 (2x2)
        grid_start_x = self.craft_x + 100
        grid_start_y = self.craft_y + 50
        for grid_y in range(2):
            for grid_x in range(2):
                slot_x = grid_start_x + grid_x * (self.slot_size + 5)
                slot_y = grid_start_y + grid_y * (self.slot_size + 5)
                
                pygame.draw.rect(screen, Colors.DARK_GRAY,
                               (slot_x, slot_y, self.slot_size, self.slot_size))
                pygame.draw.rect(screen, Colors.WHITE,
                               (slot_x, slot_y, self.slot_size, self.slot_size), 2)
                
                grid_pos = (grid_x, grid_y)
                # 드래그 중인 아이템의 원본 위치는 그리지 않음 (복사 버그 방지)
                if grid_pos in self.crafting_grid and not (self.dragging_item and self.dragging_source and self.dragging_source[0] == 'grid' and self.dragging_source[1] == grid_pos):
                    item = self.crafting_grid[grid_pos]
                    item_image = self.get_item_image(item['type'])
                    if item_image:
                        screen.blit(item_image, (slot_x + 2, slot_y + 2))
                    if item['count'] > 1:
                        count_text = font.render(str(item['count']), True, Colors.WHITE)
                        screen.blit(count_text, (slot_x + 2, slot_y + self.slot_size - 15))
        
        # 결과물 슬롯
        result_x = grid_start_x + 2 * (self.slot_size + 5) + 20
        result_y = grid_start_y
        pygame.draw.rect(screen, Colors.DARK_GRAY,
                        (result_x, result_y, self.slot_size, self.slot_size))
        pygame.draw.rect(screen, Colors.WHITE,
                        (result_x, result_y, self.slot_size, self.slot_size), 2)
        
        # 결과물 슬롯에 아이템 표시 (드래그 중이 아닐 때만)
        if self.result_item and not (self.dragging_item and self.dragging_source and self.dragging_source[0] == 'result'):
            item_image = self.get_item_image(self.result_item)
            if item_image:
                screen.blit(item_image, (result_x + 2, result_y + 2))
            result_count = self.result_counts.get(self.result_item, 1)
            if result_count > 1:
                count_text = font.render(str(result_count), True, Colors.WHITE)
                screen.blit(count_text, (result_x + 2, result_y + self.slot_size - 15))
        
        # 제작 버튼
        button_x = self.craft_x + self.craft_width // 2 - 50
        button_y = self.craft_y + 200
        pygame.draw.rect(screen, Colors.GREEN, (button_x, button_y, 100, 30))
        craft_text = font.render("Craft", True, Colors.WHITE)
        screen.blit(craft_text, (button_x + 25, button_y + 5))
        
        # 검색창
        if self.show_search:
            search_x = self.craft_x + 20
            search_y = self.craft_y + 70
            pygame.draw.rect(screen, Colors.WHITE, (search_x, search_y, 200, 30))
            search_text = font.render(self.search_text, True, Colors.BLACK)
            screen.blit(search_text, (search_x + 5, search_y + 5))
            
            # 검색 결과 표시
            if self.search_text in self.recipes:
                recipe = self.recipes[self.search_text]
                result_y = search_y + 40
                recipe_text = "Recipe: "
                for ing in recipe:
                    recipe_text += f"{ing['type']} x{ing['count']} + "
                recipe_text = recipe_text.rstrip(" + ")
                recipe_text += f" = {self.search_text}"
                recipe_surface = font.render(recipe_text, True, Colors.WHITE)
                screen.blit(recipe_surface, (search_x, result_y))
        
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

