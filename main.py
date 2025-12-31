"""
DEQJAM - 2D Open World Side-View Game
Main Game Loop
"""
import pygame
import random
import math
import sys
from player import Player
from world import World
from camera import Camera
from inventory import Inventory
from crafting import Crafting
from chat import Chat
from menu import Menu
from time_system import TimeSystem
from npc import PIKU
from enemy import Zombie
from trade import Trade
from utils import Colors, draw_text_with_shadow, get_chunk_coord
from mobile_controls import MobileControls


# 게임 상수
# 안드로이드에서는 화면 크기를 동적으로 감지
try:
    import os
    # 안드로이드 환경 감지
    if 'ANDROID_ARGUMENT' in os.environ or 'ANDROID_PRIVATE' in os.environ:
        # 안드로이드에서는 화면 크기를 나중에 설정
        SCREEN_WIDTH = 0  # 동적으로 설정
        SCREEN_HEIGHT = 0
    else:
        SCREEN_WIDTH = 1280
        SCREEN_HEIGHT = 720
except:
    SCREEN_WIDTH = 1280
    SCREEN_HEIGHT = 720

FPS = 60
BLOCK_SIZE = 32


def init_game(gender='man'):
    """게임 초기화"""
    # 플레이어 시작 위치 (y좌표 +800 ~ +900, 블록 단위로 변환)
    # y좌표는 위로 올라가면 +1이므로 음수로 표현
    start_y_block = random.randint(800, 900)
    start_y = -start_y_block * BLOCK_SIZE
    start_x = 0
    
    player = Player(start_x, start_y, gender, BLOCK_SIZE)
    world = World(BLOCK_SIZE)
    camera = Camera(SCREEN_WIDTH, SCREEN_HEIGHT)
    inventory = Inventory(SCREEN_WIDTH, SCREEN_HEIGHT)
    crafting = Crafting(SCREEN_WIDTH, SCREEN_HEIGHT)
    chat = Chat(SCREEN_WIDTH, SCREEN_HEIGHT)
    time_system = TimeSystem()
    
    # 플레이어 시작 플랫폼 생성
    # 플랫폼은 24블록 간격이므로 가장 가까운 플랫폼 찾기
    player_chunk_y = get_chunk_coord(start_y, 12 * BLOCK_SIZE)
    # 플랫폼이 있는 청크 찾기 (24의 배수)
    platform_chunk_y = (player_chunk_y // 24) * 24
    world.generate_chunk(0, platform_chunk_y)
    
    # 플레이어를 플랫폼 위에 배치 (플랫폼 위 약간 위에서 시작)
    # 플랫폼 청크 가져오기
    platform_chunk = world.get_chunk(0, platform_chunk_y)
    # 플랫폼 블록 찾기 (local_y=0, local_x=0~11 중 하나)
    # 플랫폼의 월드 y 좌표 계산 (local_y=0이므로 이것이 플랫폼 y 좌표)
    platform_world_y = platform_chunk.get_world_y()
    # 플레이어를 플랫폼 위에 배치 (플랫폼 위 1블록 위)
    player.y = platform_world_y - player.height - BLOCK_SIZE
    # 초기 속도 0으로 설정
    player.vel_y = 0
    player.vel_x = 0
    # 초기 바닥 상태 설정
    player.on_ground = False
    
    # PIKU와 거래 시스템 초기화
    piku = None
    trade = Trade(SCREEN_WIDTH, SCREEN_HEIGHT)
    zombies = []  # 좀비 리스트
    
    # 다른 세계 여부 (False = 원래 세계, True = 다른 세계)
    world.is_other_world = False
    
    return player, world, camera, inventory, crafting, chat, time_system, piku, trade, zombies


def get_block_at_mouse(mouse_x, mouse_y, camera_x, camera_y, world):
    """마우스 위치의 블록 가져오기"""
    world_x = mouse_x + camera_x
    world_y = mouse_y + camera_y
    
    block_x = int(world_x // BLOCK_SIZE)
    block_y = int(world_y // BLOCK_SIZE)
    
    block = world.get_block_at(block_x, block_y)
    if block:
        return block, block_x, block_y
    return None, None, None


def can_mine_block(block, block_x, block_y, player, world):
    """블록을 채굴할 수 있는지 확인"""
    if not block:
        return False
    
    # 물은 채굴 불가
    if block.block_type == 'water':
        return False
    
    # 플레이어와의 거리 확인 (10x10 범위)
    player_block_x = int(player.x // BLOCK_SIZE)
    player_block_y = int(player.y // BLOCK_SIZE)
    
    dist_x = abs(block_x - player_block_x)
    dist_y = abs(block_y - player_block_y)
    
    if dist_x > 10 or dist_y > 10:
        return False
    
    return True


def can_place_block(mouse_x, mouse_y, camera_x, camera_y, player, world):
    """블록을 설치할 수 있는지 확인"""
    world_x = mouse_x + camera_x
    world_y = mouse_y + camera_y
    
    block_x = int(world_x // BLOCK_SIZE)
    block_y = int(world_y // BLOCK_SIZE)
    
    # 플레이어와의 거리 확인 (10x10 범위)
    player_block_x = int(player.x // BLOCK_SIZE)
    player_block_y = int(player.y // BLOCK_SIZE)
    
    dist_x = abs(block_x - player_block_x)
    dist_y = abs(block_y - player_block_y)
    
    if dist_x > 10 or dist_y > 10:
        return False, None, None
    
    # 이미 블록이 있는지 확인
    if world.get_block_at(block_x, block_y):
        return False, None, None
    
    return True, block_x, block_y


def main():
    """메인 함수"""
    try:
        pygame.init()
        
        # 안드로이드에서 화면 크기 자동 감지
        if SCREEN_WIDTH == 0 or SCREEN_HEIGHT == 0:
            # 사용 가능한 모든 디스플레이 모드 가져오기
            modes = pygame.display.list_modes()
            if modes and len(modes) > 0:
                # 가장 큰 해상도 사용 (일반적으로 기기의 네이티브 해상도)
                SCREEN_WIDTH, SCREEN_HEIGHT = modes[0]
            else:
                # 기본값 사용
                SCREEN_WIDTH = 1920
                SCREEN_HEIGHT = 1080
        
        # 하드웨어 가속 및 VSync 활성화로 성능 최적화
        # 안드로이드에서는 FULLSCREEN 사용
        try:
            import os
            if 'ANDROID_ARGUMENT' in os.environ or 'ANDROID_PRIVATE' in os.environ:
                screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
            else:
                screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.HWSURFACE | pygame.DOUBLEBUF)
        except:
            screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        
        pygame.display.set_caption("DEQJAM")
        clock = pygame.time.Clock()
        # 윈도우가 제대로 표시되도록 강제
        pygame.display.flip()
    except Exception as e:
        print(f"Error initializing pygame: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # 폰트 설정 (한국어 폰트 tofu 방지)
    try:
        # Windows 한국어 폰트 시도 (더 많은 옵션)
        korean_fonts = [
            'Malgun Gothic', '맑은 고딕',  # 맑은 고딕
            'Gulim', '굴림',  # 굴림
            'Batang', '바탕',  # 바탕
            'Dotum', '돋움',  # 돋움
            'Gungsuh', '궁서',  # 궁서
            'NanumGothic', '나눔고딕',  # 나눔고딕
            'NanumBarunGothic', '나눔바른고딕',  # 나눔바른고딕
        ]
        font = None
        small_font = None
        
        # 시스템 폰트 목록 가져오기
        available_fonts = pygame.font.get_fonts()
        
        for font_name in korean_fonts:
            try:
                # 폰트 이름이 시스템에 있는지 확인
                if font_name.lower() in [f.lower() for f in available_fonts]:
                    font = pygame.font.SysFont(font_name, 24)
                    small_font = pygame.font.SysFont(font_name, 18)
                    # 테스트로 한국어 렌더링 확인
                    test_surface = font.render('테스트', True, (255, 255, 255))
                    # TOFU 확인: 너비가 0이 아니고, 실제로 렌더링되었는지 확인
                    if test_surface.get_width() > 0:
                        # 간단한 픽셀 체크 (중앙 부분 샘플링)
                        center_x = test_surface.get_width() // 2
                        center_y = test_surface.get_height() // 2
                        if 0 <= center_x < test_surface.get_width() and 0 <= center_y < test_surface.get_height():
                            pixel_color = test_surface.get_at((center_x, center_y))
                            # 흰색이 아니면 렌더링된 것 (TOFU는 보통 검은색 또는 투명)
                            if pixel_color[0] > 0 or pixel_color[1] > 0 or pixel_color[2] > 0:
                                print(f"Korean font loaded: {font_name}")
                                break
            except Exception as e:
                continue
        
        # 한국어 폰트를 찾지 못한 경우 기본 폰트 사용
        if font is None:
            # 기본 폰트도 한국어 지원 시도
            try:
                font = pygame.font.SysFont(None, 24)
                small_font = pygame.font.SysFont(None, 18)
                test_surface = font.render('테스트', True, (255, 255, 255))
                if test_surface.get_width() == 0:
                    font = pygame.font.Font(None, 24)
                    small_font = pygame.font.Font(None, 18)
            except:
                font = pygame.font.Font(None, 24)
                small_font = pygame.font.Font(None, 18)
    except Exception as e:
        print(f"Font loading error: {e}")
        font = pygame.font.Font(None, 24)
        small_font = pygame.font.Font(None, 18)
    
    # 메뉴
    menu = Menu(SCREEN_WIDTH, SCREEN_HEIGHT)
    game_started = False
    selected_gender = None
    
    # 모바일 컨트롤 (항상 활성화)
    mobile_controls = MobileControls(SCREEN_WIDTH, SCREEN_HEIGHT)
    mobile_controls.detect_mobile()
    use_mobile_controls = True  # 항상 모바일 컨트롤 사용
    
    # 게임 상태
    player = None
    world = None
    camera = None
    inventory = None
    crafting = None
    chat = None
    time_system = None
    
    # 채굴 관련
    mining_block = None
    mining_start_time = 0
    mining_duration = 3.0
    mining_range = 10
    mouse_held_time = 0
    
    # 아이템 이름 표시 관련
    item_display_name = None
    item_display_time = 0.0
    item_display_duration = 0.7  # 0.7초
    item_display_fade_duration = 0.3  # 페이드 아웃 시간
    
    def get_mining_duration(block_type, selected_item=None):
        """블록 타입과 선택된 도구에 따른 채굴 시간 반환"""
        # 나뭇잎은 항상 즉시 채굴 (클릭만 하면 됨)
        if block_type == 'tree_leaf':
            return 0.0  # 즉시 채굴
        
        # 물은 채굴 불가
        if block_type == 'water':
            return -1
        
        # portal은 도구 없이 50초
        if block_type == 'portal':
            return 50.0
        
        # 기본 채굴 시간 계산
        base_duration = 3.0  # 일반 블록 기본 시간
        if block_type == 'tree':
            base_duration = 5.0  # 나무 기본 시간
        
        # wood_dt를 사용하는 경우 (일반 속도보다 2초 더 빠르게)
        if selected_item and selected_item.get('type') == 'wood_dt':
            return max(0.1, base_duration - 2.0)  # 최소 0.1초
        
        # 막대기(stick_wood)를 사용하는 경우
        if selected_item and selected_item.get('type') == 'stick_wood':
            if block_type == 'tree':
                return 5.0  # 나무는 여전히 5초
            return 2.7  # 일반 블록은 2.7초
        
        # 기본값
        return base_duration
    
    def get_attack_power(selected_item=None):
        """선택된 도구의 공격력 반환"""
        if selected_item and selected_item.get('type') == 'wood_dt':
            return 6  # wood_dt 공격력 6
        return 0  # 기본 공격력 없음
    
    running = True
    
    while running:
        try:
            dt = clock.tick(FPS) / 1000.0  # 초 단위
            # dt가 0이거나 음수인 경우 최소값 설정
            if dt <= 0:
                dt = 0.016  # 약 60 FPS
            
            # 이벤트 처리
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                # 모바일 터치 이벤트 처리
                if use_mobile_controls:
                    mobile_controls.handle_touch_event(event)
                    # 마우스 이벤트도 터치로 변환 (데스크톱 테스트용)
                    if event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEMOTION, pygame.MOUSEBUTTONUP):
                        mobile_controls.handle_mouse_event(event)
                
                if not game_started:
                    # 메뉴 상태
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if event.button == 1:
                            gender = menu.handle_click(event.pos)
                            if gender:
                                selected_gender = gender
                                player, world, camera, inventory, crafting, chat, time_system, piku, trade, zombies = init_game(gender)
                                game_started = True
                else:
                    # 게임 상태
                    # 모바일 버튼 클릭 처리 (이벤트 루프 외부에서 처리)
                    
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_TAB:
                                if inventory.is_open:
                                    inventory.is_open = False
                                elif crafting.is_open:
                                    crafting.is_open = False
                                elif chat.is_open:
                                    chat.is_open = False
                                else:
                                    inventory.is_open = True
                        
                        if event.key == pygame.K_t:
                            if not chat.is_open:
                                chat.is_open = True
                        
                        if chat.is_open:
                            command_result = chat.handle_input(event)
                            if command_result == "crafting":
                                crafting.is_open = True
                                chat.is_open = False
                            elif command_result == "note":
                                # 노트 모드는 이미 chat에서 처리됨
                                pass
                    
                    if event.type == pygame.MOUSEBUTTONDOWN:
                            if event.button == 1:  # 좌클릭
                                mouse_pos = pygame.mouse.get_pos()
                                
                                if crafting.is_open:
                                    # 제작대가 열려있을 때는 제작대 드래그 우선 처리
                                    crafting.handle_drag(mouse_pos, True, inventory)
                                    # 드래그가 시작되지 않았으면 인벤토리/핫바 드래그 시도
                                    if crafting.dragging_item is None and inventory.is_open:
                                        inventory.handle_drag(mouse_pos, True, crafting)
                                    # 드래그가 시작되지 않았으면 클릭 처리
                                    if crafting.dragging_item is None:
                                        crafting.handle_click(mouse_pos, inventory)
                                elif inventory.is_open:
                                    inventory.handle_drag(mouse_pos, True, crafting)
                                elif trade.is_open:
                                    # 대사 다음 버튼 클릭 처리
                                    if trade.show_dialogue and trade.dialogue_index < len(trade.dialogues) - 1:
                                        button_x = trade.trade_x + trade.trade_width // 2 - 75
                                        button_y = trade.trade_y + trade.trade_height - 80
                                        button_rect = pygame.Rect(button_x, button_y, 150, 40)
                                        if button_rect.collidepoint(mouse_pos):
                                            trade.next_dialogue()
                                    else:
                                        trade.handle_click(mouse_pos, inventory)
                                elif chat.is_open:
                                    chat.handle_click(mouse_pos)
                                elif piku and not trade.is_open:
                                    # PIKU 클릭 확인
                                    if piku.check_click(mouse_pos[0], mouse_pos[1], camera.x, camera.y):
                                        trade.open_trade()
                                else:
                                    # 좀비 공격 (wood_dt 사용 시)
                                    selected_item = inventory.get_selected_hotbar_item()
                                    attack_power = get_attack_power(selected_item)
                                    if attack_power > 0:
                                        mouse_world_x = mouse_pos[0] + camera.x
                                        mouse_world_y = mouse_pos[1] + camera.y
                                        for zombie in zombies:
                                            if zombie.is_alive:
                                                dx = zombie.x - mouse_world_x
                                                dy = zombie.y - mouse_world_y
                                                distance = math.sqrt(dx * dx + dy * dy)
                                                if distance <= 50:  # 50픽셀 이내
                                                    zombie.take_damage(attack_power)
                                                    # wood_dt 내구도 감소
                                                    if inventory.selected_hotbar_slot in inventory.hotbar:
                                                        if 'durability' in inventory.hotbar[inventory.selected_hotbar_slot]:
                                                            inventory.hotbar[inventory.selected_hotbar_slot]['durability'] -= 1
                                                            if inventory.hotbar[inventory.selected_hotbar_slot]['durability'] <= 0:
                                                                # 내구도가 0이 되면 아이템 제거
                                                                del inventory.hotbar[inventory.selected_hotbar_slot]
                                                    break
                                    
                                    # 채굴 시작
                                    block, block_x, block_y = get_block_at_mouse(mouse_pos[0], mouse_pos[1], camera.x, camera.y, world)
                                    if block and can_mine_block(block, block_x, block_y, player, world):
                                        selected_item = inventory.get_selected_hotbar_item()
                                        mining_block = block
                                        mining_start_time = pygame.time.get_ticks() / 1000.0
                                        mouse_held_time = 0
                                        mining_duration = get_mining_duration(block.block_type, selected_item)
                            
                            if event.button == 3:  # 우클릭
                                if not (inventory.is_open or crafting.is_open or chat.is_open):
                                    # 블록 설치
                                    mouse_pos = pygame.mouse.get_pos()
                                    can_place, block_x, block_y = can_place_block(
                                        mouse_pos[0], mouse_pos[1], camera.x, camera.y, player, world
                                    )
                                    if can_place:
                                        selected_item = inventory.get_selected_hotbar_item()
                                        if selected_item and selected_item['type'] not in ['stick_wood']:
                                            if world.place_block_at(block_x, block_y, selected_item['type']):
                                                inventory.remove_from_hotbar(inventory.selected_hotbar_slot, 1)
                
                # 모바일 설치 버튼 처리
                if use_mobile_controls and mobile_controls.is_place_pressed():
                    if not (inventory.is_open or crafting.is_open or chat.is_open):
                        # 플레이어 앞쪽에 블록 설치
                        if player.facing_right:
                            place_x = player.x + player.width + 10
                        else:
                            place_x = player.x - 10
                        place_y = player.y + player.height // 2
                        # 화면 좌표를 월드 좌표로 변환
                        screen_place_x = place_x - camera.x
                        screen_place_y = place_y - camera.y
                        can_place, block_x, block_y = can_place_block(
                            screen_place_x, screen_place_y, camera.x, camera.y, player, world
                        )
                        if can_place:
                            selected_item = inventory.get_selected_hotbar_item()
                            if selected_item and selected_item['type'] not in ['stick_wood']:
                                if world.place_block_at(block_x, block_y, selected_item['type']):
                                    inventory.remove_from_hotbar(inventory.selected_hotbar_slot, 1)
                            
                            if event.button == 4:  # 마우스 휠 위
                                if inventory.is_open:
                                    inventory.handle_mouse_wheel(1)
                                else:
                                    old_slot = inventory.selected_hotbar_slot
                                    inventory.handle_hotbar_wheel(1)
                                    # 핫바 슬롯이 변경되었으면 아이템 이름 표시
                                    if old_slot != inventory.selected_hotbar_slot:
                                        selected_item = inventory.get_selected_hotbar_item()
                                        if selected_item:
                                            item_display_name = selected_item['type']
                                            item_display_time = 0.0
                            
                            if event.button == 5:  # 마우스 휠 아래
                                if inventory.is_open:
                                    inventory.handle_mouse_wheel(-1)
                                else:
                                    old_slot = inventory.selected_hotbar_slot
                                    inventory.handle_hotbar_wheel(-1)
                                    # 핫바 슬롯이 변경되었으면 아이템 이름 표시
                                    if old_slot != inventory.selected_hotbar_slot:
                                        selected_item = inventory.get_selected_hotbar_item()
                                        if selected_item:
                                            item_display_name = selected_item['type']
                                            item_display_time = 0.0
                    
                    if event.type == pygame.MOUSEBUTTONUP:
                        if event.button == 1:
                            mouse_pos = pygame.mouse.get_pos()
                            if crafting.is_open:
                                # 제작대가 열려있을 때는 제작대 드래그 우선 처리
                                crafting.handle_drag(mouse_pos, False, inventory)
                                # 제작대 드래그가 없으면 인벤토리/핫바 드래그 처리
                                if crafting.dragging_item is None and inventory.is_open:
                                    inventory.handle_drag(mouse_pos, False, crafting)
                            elif inventory.is_open:
                                inventory.handle_drag(mouse_pos, False, crafting)
                            mining_block = None
                            mining_start_time = 0
                            mouse_held_time = 0
            
            if not game_started:
                # 메뉴 업데이트 및 그리기
                menu.update(dt)
                menu.draw(screen, font)
            else:
                # 게임 업데이트
                keys = pygame.key.get_pressed()
                
                # 모바일 컨트롤 업데이트
                if use_mobile_controls:
                    mobile_controls.update()
                    
                    # 인벤토리 버튼 클릭
                    if mobile_controls.inventory_button.is_clicked():
                        if inventory.is_open:
                            inventory.is_open = False
                        elif crafting.is_open:
                            crafting.is_open = False
                        elif chat.is_open:
                            chat.is_open = False
                        else:
                            inventory.is_open = True
                    
                    # 제작대 버튼 클릭
                    if mobile_controls.crafting_button.is_clicked():
                        if not crafting.is_open:
                            crafting.is_open = True
                            inventory.is_open = False
                            chat.is_open = False
                        else:
                            crafting.is_open = False
                    
                    # 채팅 버튼 클릭
                    if mobile_controls.chat_button.is_clicked():
                        if not chat.is_open:
                            chat.is_open = True
                        else:
                            chat.is_open = False
                    
                    # 핫바 버튼 클릭
                    for i, btn in enumerate(mobile_controls.hotbar_buttons):
                        if btn.is_clicked():
                            inventory.selected_hotbar_slot = i
                            # 아이템 이름 표시
                            selected_item = inventory.get_selected_hotbar_item()
                            if selected_item:
                                item_display_name = selected_item['type']
                                item_display_time = 0.0
                
                # 시간 시스템 업데이트
                time_system.update(dt)
                
                # 아이템 이름 표시 시간 업데이트
                if item_display_name is not None:
                    item_display_time += dt
                    if item_display_time >= item_display_duration + item_display_fade_duration:
                        item_display_name = None
                        item_display_time = 0.0
                
                # 플레이어 업데이트 (속도 계산)
                # 모바일 입력 처리
                mobile_input = None
                if use_mobile_controls:
                    mobile_input = mobile_controls.get_movement_input()
                    # 점프 버튼 처리
                    if mobile_controls.is_jump_pressed() and not player.jump_held:
                        player.jump()
                        player.jump_held = True
                    elif not mobile_controls.is_jump_pressed():
                        player.jump_held = False
                        if player.on_ground:
                            player.can_jump = True
                
                player.update(keys, dt, mobile_input)
                
                # X축 이동 먼저 처리
                new_x = player.x + player.vel_x
                new_y = player.y
                
                # X축 충돌 검사
                if world.check_block_collision(new_x, new_y, player.width, player.height):
                    # X축 충돌 발생 - 이전 위치 유지
                    new_x = player.x
                    player.vel_x = 0
                
                # Y축 이동 처리
                new_y = player.y + player.vel_y
                
                # Y축 충돌 검사
                if world.check_block_collision(new_x, new_y, player.width, player.height):
                    # Y축 충돌 발생
                    if player.vel_y > 0:  # 아래로 이동 (낙하) - 블록 위에 서도록
                        # 플레이어 발 아래 블록 찾기
                        player_bottom = new_y + player.height
                        # 블록 위에 정확히 서도록 위치 찾기
                        new_y = world.find_ground_y(new_x, player_bottom, player.height)
                    elif player.vel_y < 0:  # 위로 이동 (점프) - 블록 아래에 멈춤
                        # 플레이어 머리 위 블록 찾기
                        player_top = new_y
                        new_y = world.find_ceiling_y(new_x, player_top, player.height)
                    else:
                        new_y = player.y
                    
                    # Y 속도 초기화
                    player.vel_y = 0
                
                # 위치 업데이트
                player.x = new_x
                player.y = new_y
                
                # 포탈 충돌 체크 (원래 세계에서만)
                if not world.is_other_world:
                    if world.check_portal_collision(player.x, player.y, player.width, player.height):
                        # 다른 세계로 이동 (인벤토리는 자동으로 유지됨)
                        world.is_other_world = True
                        world.chunks.clear()
                        world.generated_chunks.clear()
                        
                        # 플레이어를 y+100 이상 위치에 배치
                        spawn_y_block = random.randint(100, 150)  # y 100~150 블록
                        spawn_y = -spawn_y_block * BLOCK_SIZE
                        spawn_x = 0
                        
                        # 새로운 세계의 청크 생성 (플레이어 주변)
                        player_chunk_x = get_chunk_coord(spawn_x, 12 * BLOCK_SIZE)
                        player_chunk_y = get_chunk_coord(spawn_y, 12 * BLOCK_SIZE)
                        
                        # 플레이어 주변 청크 생성
                        for cx in range(player_chunk_x - 2, player_chunk_x + 3):
                            for cy in range(player_chunk_y - 2, player_chunk_y + 3):
                                world.generate_other_world_chunk(cx, cy)
                        
                        # 플랫폼 위에 플레이어 배치
                        # 플랫폼이 있는 청크 찾기 (y 99~50 범위)
                        platform_chunk_y = player_chunk_y
                        platform_chunk = world.get_chunk(player_chunk_x, platform_chunk_y)
                        
                        # 플랫폼의 월드 y 좌표 계산 (y 99 블록 = -99 * BLOCK_SIZE)
                        platform_block_y = 99
                        platform_world_y = -platform_block_y * BLOCK_SIZE
                        
                        # 플레이어를 플랫폼 위에 배치 (플랫폼 위 1블록 위)
                        player.x = spawn_x
                        player.y = platform_world_y - player.height - BLOCK_SIZE
                        player.vel_x = 0
                        player.vel_y = 0
                        player.on_ground = False
                
                # 바닥 확인 (낙하 중일 때만 확인하여 성능 최적화)
                if player.vel_y >= 0:  # 낙하 중일 때만
                    player.on_ground = world.check_on_ground(player.x, player.y, player.width, player.height)
                    # 바닥에 닿았으면 Y 속도를 0으로 설정
                    if player.on_ground:
                        player.vel_y = 0
                else:
                    player.on_ground = False
                
                # 카메라 업데이트 (부드러운 추적)
                camera.update(player.x + player.width // 2, player.y + player.height // 2, dt)
                
                # 청크 업데이트
                world.update_rendered_chunks(player.x, player.y, 3)
                
                # PIKU 스폰 (2일이 되면)
                if piku is None and time_system.days_passed >= 1:  # 2일 = days_passed >= 1
                    # 오른쪽 끝에서 스폰 (플레이어 오른쪽 500픽셀)
                    spawn_x = player.x + 500
                    spawn_y = player.y
                    piku = PIKU(spawn_x, spawn_y, BLOCK_SIZE)
                
                # PIKU 업데이트
                if piku:
                    piku.update(dt, player.x + player.width // 2, player.y + player.height // 2, zombies)
                
                # 좀비 스폰 (밤에만)
                current_period = time_system.get_current_period()
                if current_period == 'night':
                    # 밤에만 좀비 스폰 (플레이어로부터 25블록 밖)
                    alive_zombies = [z for z in zombies if z.is_alive]
                    if len(alive_zombies) < 3:  # 최대 3마리
                        spawn_angle = random.uniform(0, 2 * math.pi)
                        spawn_distance = 25 * BLOCK_SIZE  # 25블록 = 800픽셀
                        zombie_x = player.x + math.cos(spawn_angle) * spawn_distance
                        zombie_y = player.y + math.sin(spawn_angle) * spawn_distance
                        # 땅 위에 스폰되도록 조정
                        zombie_bottom = zombie_y + BLOCK_SIZE * 2
                        zombie_y = world.find_ground_y(zombie_x, zombie_bottom, BLOCK_SIZE * 2)
                        zombies.append(Zombie(zombie_x, zombie_y, BLOCK_SIZE))
                else:
                    # 아침이 되면 모든 좀비 제거
                    zombies.clear()
                
                # 좀비 업데이트
                for zombie in zombies:
                    if zombie.is_alive:
                        zombie.update(dt, player.x + player.width // 2, player.y + player.height // 2, player, world)
                
                # 거래 창 업데이트
                if trade.is_open:
                    trade.update_dialogue(dt)
                
                # 채굴 처리
                mouse_buttons = pygame.mouse.get_pressed()
                # 모바일 채굴 버튼 처리
                mine_pressed = False
                if use_mobile_controls and mobile_controls.is_mine_pressed():
                    mine_pressed = True
                    # 플레이어 앞쪽 블록 채굴 (플레이어가 바라보는 방향)
                    if player.facing_right:
                        mine_x = player.x + player.width + 10
                    else:
                        mine_x = player.x - 10
                    mine_y = player.y + player.height // 2
                    # 화면 좌표를 월드 좌표로 변환
                    screen_mine_x = mine_x - camera.x
                    screen_mine_y = mine_y - camera.y
                    block, block_x, block_y = get_block_at_mouse(screen_mine_x, screen_mine_y, camera.x, camera.y, world)
                    if block and can_mine_block(block, block_x, block_y, player, world):
                        if not mining_block:
                            selected_item = inventory.get_selected_hotbar_item()
                            mining_block = block
                            mining_start_time = pygame.time.get_ticks() / 1000.0
                            mouse_held_time = 0
                            mining_duration = get_mining_duration(block.block_type, selected_item)
                
                if mouse_buttons[0] or mine_pressed:
                    # 마우스가 눌려있는 동안 새로운 블록 찾기
                    if not mining_block:
                        mouse_pos = pygame.mouse.get_pos()
                        block, block_x, block_y = get_block_at_mouse(mouse_pos[0], mouse_pos[1], camera.x, camera.y, world)
                        if block and can_mine_block(block, block_x, block_y, player, world):
                            selected_item = inventory.get_selected_hotbar_item()
                            mining_block = block
                            mining_start_time = pygame.time.get_ticks() / 1000.0
                            mouse_held_time = 0
                            mining_duration = get_mining_duration(block.block_type, selected_item)
                    
                    if mining_block:
                        mouse_held_time += dt
                        
                        # 나뭇잎은 즉시 채굴 (클릭만 하면 됨)
                        if mining_block.block_type == 'tree_leaf':
                            block_x = int(mining_block.x // BLOCK_SIZE)
                            block_y = int(mining_block.y // BLOCK_SIZE)
                            block = world.remove_block_at(block_x, block_y)
                            if block:
                                inventory.add_item(block.block_type, 1)
                                # wood_dt 내구도 감소
                                selected_item = inventory.get_selected_hotbar_item()
                                if selected_item and selected_item.get('type') == 'wood_dt':
                                    if inventory.selected_hotbar_slot in inventory.hotbar:
                                        if 'durability' in inventory.hotbar[inventory.selected_hotbar_slot]:
                                            inventory.hotbar[inventory.selected_hotbar_slot]['durability'] -= 1
                                            if inventory.hotbar[inventory.selected_hotbar_slot]['durability'] <= 0:
                                                # 내구도가 0이 되면 아이템 제거
                                                del inventory.hotbar[inventory.selected_hotbar_slot]
                            mining_block = None
                            mining_start_time = 0
                            mouse_held_time = 0
                        elif mining_duration > 0 and mouse_held_time >= mining_duration:
                            # 블록 채굴 완료
                            block_x = int(mining_block.x // BLOCK_SIZE)
                            block_y = int(mining_block.y // BLOCK_SIZE)
                            block = world.remove_block_at(block_x, block_y)
                            if block:
                                inventory.add_item(block.block_type, 1)
                                # wood_dt 내구도 감소
                                selected_item = inventory.get_selected_hotbar_item()
                                if selected_item and selected_item.get('type') == 'wood_dt':
                                    if inventory.selected_hotbar_slot in inventory.hotbar:
                                        if 'durability' in inventory.hotbar[inventory.selected_hotbar_slot]:
                                            inventory.hotbar[inventory.selected_hotbar_slot]['durability'] -= 1
                                            if inventory.hotbar[inventory.selected_hotbar_slot]['durability'] <= 0:
                                                # 내구도가 0이 되면 아이템 제거
                                                del inventory.hotbar[inventory.selected_hotbar_slot]
                            mining_block = None
                            mining_start_time = 0
                            mouse_held_time = 0
                
                # 화면 그리기
                # 하늘 색상
                sky_color = time_system.get_sky_color()
                screen.fill(sky_color)
                
                # 월드 그리기
                world.draw(screen, camera.x, camera.y, dt)
                
                # 플레이어 그리기
                player.draw(screen, camera.x, camera.y)
                
                # PIKU 그리기
                if piku:
                    piku.draw(screen, camera.x, camera.y)
                
                # 좀비 그리기
                for zombie in zombies:
                    if zombie.is_alive:
                        zombie.draw(screen, camera.x, camera.y)
                
                # 채굴 진행 표시 (최적화: Surface 재사용)
                if mining_block and mouse_buttons[0] and mining_duration > 0:
                    progress = mouse_held_time / mining_duration
                    mining_screen_x = int(mining_block.x - camera.x)
                    mining_screen_y = int(mining_block.y - camera.y)
                    
                    # 빨간색 오버레이 (직접 그리기로 최적화)
                    alpha = int(255 * progress * 0.5)
                    overlay_rect = pygame.Rect(mining_screen_x, mining_screen_y, BLOCK_SIZE, BLOCK_SIZE)
                    overlay_surf = pygame.Surface((BLOCK_SIZE, BLOCK_SIZE), pygame.SRCALPHA)
                    overlay_surf.fill((255, 0, 0, alpha))
                    screen.blit(overlay_surf, overlay_rect)
                
                # UI 그리기 (최적화: 불필요한 Surface 생성 최소화)
                # 좌표 표시 (우측 상단)
                coord_text = f"X: {int(player.x // BLOCK_SIZE)}, Y: {int(player.y // BLOCK_SIZE)}"
                coord_surface = small_font.render(coord_text, True, Colors.WHITE)
                coord_bg_rect = pygame.Rect(SCREEN_WIDTH - coord_surface.get_width() - 15, 10, 
                                            coord_surface.get_width() + 10, coord_surface.get_height() + 5)
                pygame.draw.rect(screen, Colors.BLACK, coord_bg_rect)
                screen.blit(coord_surface, (SCREEN_WIDTH - coord_surface.get_width() - 10, 12))
                
                # 체력바
                health_text = f"HP: {player.health}/{player.max_health}"
                health_surface = small_font.render(health_text, True, Colors.WHITE)
                health_bg_rect = pygame.Rect(SCREEN_WIDTH - health_surface.get_width() - 15, 35,
                                            health_surface.get_width() + 10, health_surface.get_height() + 5)
                pygame.draw.rect(screen, Colors.BLACK, health_bg_rect)
                screen.blit(health_surface, (SCREEN_WIDTH - health_surface.get_width() - 10, 37))
                
                # 체력바 그래픽
                bar_width = 200
                bar_height = 20
                bar_x = SCREEN_WIDTH - bar_width - 15
                bar_y = 60
                pygame.draw.rect(screen, Colors.RED, (bar_x, bar_y, bar_width, bar_height))
                health_width = int(bar_width * (player.health / player.max_health))
                pygame.draw.rect(screen, Colors.GREEN, (bar_x, bar_y, health_width, bar_height))
                pygame.draw.rect(screen, Colors.WHITE, (bar_x, bar_y, bar_width, bar_height), 2)
                
                # 시간 표시
                time_text = time_system.get_time_string()
                time_surface = small_font.render(time_text, True, Colors.WHITE)
                time_bg_rect = pygame.Rect(SCREEN_WIDTH - time_surface.get_width() - 15, 85,
                                          time_surface.get_width() + 10, time_surface.get_height() + 5)
                pygame.draw.rect(screen, Colors.BLACK, time_bg_rect)
                screen.blit(time_surface, (SCREEN_WIDTH - time_surface.get_width() - 10, 87))
                
                # 일수 표시 (시간 아래)
                days_text = time_system.get_days_string()
                days_surface = small_font.render(days_text, True, Colors.WHITE)
                days_bg_rect = pygame.Rect(SCREEN_WIDTH - days_surface.get_width() - 15, 110,
                                          days_surface.get_width() + 10, days_surface.get_height() + 5)
                pygame.draw.rect(screen, Colors.BLACK, days_bg_rect)
                screen.blit(days_surface, (SCREEN_WIDTH - days_surface.get_width() - 10, 112))
                
                # 인벤토리 그리기
                # wood_dt 내구도 게이지 (우측 세로 바)
                selected_item = inventory.get_selected_hotbar_item()
                if selected_item and selected_item.get('type') == 'wood_dt':
                    if inventory.selected_hotbar_slot in inventory.hotbar:
                        item = inventory.hotbar[inventory.selected_hotbar_slot]
                        if 'durability' in item and 'max_durability' in item:
                            durability = item['durability']
                            max_durability = item['max_durability']
                            
                            # 게이지 위치 및 크기
                            gauge_x = SCREEN_WIDTH - 30
                            gauge_y = 100
                            gauge_width = 20
                            gauge_height = 200
                            
                            # 배경 (검은색)
                            bg_rect = pygame.Rect(gauge_x, gauge_y, gauge_width, gauge_height)
                            pygame.draw.rect(screen, Colors.BLACK, bg_rect)
                            pygame.draw.rect(screen, Colors.WHITE, bg_rect, 2)
                            
                            # 내구도 비율 계산
                            durability_ratio = max(0.0, min(1.0, durability / max_durability))
                            fill_height = int(gauge_height * durability_ratio)
                            
                            # 내구도 바 (초록색 -> 노란색 -> 빨간색)
                            if durability_ratio > 0:
                                if durability_ratio > 0.5:
                                    # 초록색 -> 노란색
                                    color_ratio = (durability_ratio - 0.5) * 2.0
                                    r = int(255 * (1.0 - color_ratio))
                                    g = 255
                                    b = 0
                                else:
                                    # 노란색 -> 빨간색
                                    color_ratio = durability_ratio * 2.0
                                    r = 255
                                    g = int(255 * color_ratio)
                                    b = 0
                                
                                fill_rect = pygame.Rect(gauge_x + 2, gauge_y + gauge_height - fill_height, 
                                                       gauge_width - 4, fill_height)
                                pygame.draw.rect(screen, (r, g, b), fill_rect)
                            
                            # 내구도 텍스트
                            durability_text = f"{durability}/{max_durability}"
                            text_surface = small_font.render(durability_text, True, Colors.WHITE)
                            text_x = gauge_x - text_surface.get_width() - 5
                            text_y = gauge_y + gauge_height // 2 - text_surface.get_height() // 2
                            screen.blit(text_surface, (text_x, text_y))
                
                inventory.draw(screen, font, inventory.is_open)
                
                # 호버 아이템 이름 표시
                if inventory.is_open:
                    hover_name = inventory.get_hover_item_name(pygame.mouse.get_pos())
                    if hover_name:
                        mouse_pos = pygame.mouse.get_pos()
                        name_surface = small_font.render(hover_name, True, Colors.WHITE)
                        name_bg = pygame.Surface((name_surface.get_width() + 5, name_surface.get_height() + 3))
                        name_bg.fill((255, 255, 255))
                        name_bg.set_alpha(200)
                        screen.blit(name_bg, (mouse_pos[0] + 10, mouse_pos[1] + 10))
                        screen.blit(name_surface, (mouse_pos[0] + 12, mouse_pos[1] + 12))
                
                # 제작대 그리기
                crafting.draw(screen, font, inventory)
                
                # 채팅창 그리기
                chat.draw(screen, font)
                
                # 거래 창 그리기
                trade.draw(screen, font)
                
                # 아이템 이름 표시 (화면 가운데)
                if item_display_name is not None and item_display_time < item_display_duration + item_display_fade_duration:
                    # 페이드 아웃 계산
                    if item_display_time <= item_display_duration:
                        # 표시 중 (완전 불투명)
                        alpha = 255
                    else:
                        # 페이드 아웃 중
                        fade_progress = (item_display_time - item_display_duration) / item_display_fade_duration
                        alpha = int(255 * (1.0 - fade_progress))
                    
                    # 아이템 이름 텍스트 렌더링
                    item_name_surface = font.render(item_display_name, True, Colors.WHITE)
                    text_width = item_name_surface.get_width()
                    text_height = item_name_surface.get_height()
                    
                    # 배경 크기 (여유 공간 추가)
                    padding = 20
                    bg_width = text_width + padding * 2
                    bg_height = text_height + padding * 2
                    
                    # 화면 가운데 위치
                    bg_x = (SCREEN_WIDTH - bg_width) // 2
                    bg_y = (SCREEN_HEIGHT - bg_height) // 2
                    
                    # 검은 배경 (반투명)
                    bg_surface = pygame.Surface((bg_width, bg_height), pygame.SRCALPHA)
                    bg_surface.fill((0, 0, 0, alpha))
                    screen.blit(bg_surface, (bg_x, bg_y))
                    
                    # 흰색 테두리 (반투명)
                    border_surface = pygame.Surface((bg_width, bg_height), pygame.SRCALPHA)
                    pygame.draw.rect(border_surface, (255, 255, 255, alpha), 
                                   (0, 0, bg_width, bg_height), 2)
                    screen.blit(border_surface, (bg_x, bg_y))
                    
                    # 텍스트 (흰색, 알파 적용)
                    text_surface = font.render(item_display_name, True, Colors.WHITE)
                    text_surface.set_alpha(alpha)
                    screen.blit(text_surface, (bg_x + padding, bg_y + padding))
                
                # 모바일 컨트롤 그리기
                if use_mobile_controls:
                    mobile_controls.draw(screen, small_font)
            
        
            pygame.display.flip()
        except KeyboardInterrupt:
            running = False
        except Exception as e:
            print(f"Error in game loop: {e}")
            import traceback
            traceback.print_exc()
            # 게임을 계속 실행하도록 함
            pygame.time.wait(100)  # 0.1초 대기
            # 예외 발생 시에도 화면 업데이트
            try:
                pygame.display.flip()
            except:
                pass
            continue
    
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()

