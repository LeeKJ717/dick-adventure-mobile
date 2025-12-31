"""
월드 및 블록 클래스
"""
import pygame
import random
import json
import os
import math
from utils import Colors, get_chunk_coord, clamp
from piskel_loader import PiskelLoader

# #region agent log
DEBUG_ENABLED = False  # 성능 최적화를 위해 비활성화
DEBUG_LOG_PATH = r"c:\Users\UserK\Desktop\DEQJAM\.cursor\debug.log"
def debug_log(location, message, data, hypothesis_id="A"):
    if not DEBUG_ENABLED:
        return
    try:
        log_entry = {
            "sessionId": "debug-session",
            "runId": "run1",
            "hypothesisId": hypothesis_id,
            "location": location,
            "message": message,
            "data": data,
            "timestamp": pygame.time.get_ticks() if pygame.get_init() else 0
        }
        with open(DEBUG_LOG_PATH, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
    except:
        pass
# #endregion


class Block:
    """블록 클래스"""
    
    def __init__(self, x, y, block_type='ground', block_size=32):
        # #region agent log
        debug_log("world.py:13", "Block.__init__ called", {"block_type": block_type, "x": x, "y": y}, "A")
        # #endregion
        self.x = x
        self.y = y
        self.block_type = block_type
        self.block_size = block_size
        # 블록은 정확히 block_size 크기 (간격 없이 붙어있도록)
        self.width = block_size
        self.height = block_size
        self.image = None
        self.load_image()
        # #region agent log
        debug_log("world.py:23", "Block.__init__ after load_image", {"block_type": self.block_type, "image_is_none": self.image is None}, "A")
        # #endregion
        self.is_natural = True  # 자연 생성된 블록인지
        self.health = 1  # 블록 체력 (나무는 5)
        
        # 나무 블록은 체력 설정
        if self.block_type == 'tree':
            self.health = 5  # 5초 = 5
        elif self.block_type == 'water':
            self.health = -1  # 물은 채굴 불가
        elif self.block_type == 'portal':
            self.health = 50  # portal은 50초
        
        # portal 애니메이션을 위한 시간 변수 (모든 블록에 초기화)
        self.animation_time = 0.0
        
    def load_image(self):
        """블록 이미지 로드"""
        # #region agent log
        debug_log("world.py:30", "Block.load_image called", {"block_type": self.block_type}, "A")
        # #endregion
        image_paths = {
            'ground': 'fig/block/ground.piskel',
            'tree': 'fig/block/tree.piskel',
            'tree_leaf': 'fig/block/tree_leaf.piskel',
            'wood_plank': 'fig/block/나무판자.piskel',
            'plank_board': 'fig/block/판자판.piskel',
            'water': 'fig/block/water.piskel',  # 물 piskel 이미지 사용
            'portal': 'fig/block/portal.piskel',
            'rock': 'fig/block/rock.piskel',
        }
        
        if self.block_type in image_paths:
            image_path = image_paths[self.block_type]
            # #region agent log
            debug_log("world.py:41", "Loading image", {"block_type": self.block_type, "image_path": image_path}, "A")
            # #endregion
            self.image = PiskelLoader.load_piskel(image_path)
            # #region agent log
            debug_log("world.py:43", "After load_piskel", {"block_type": self.block_type, "image_is_none": self.image is None, "image_path": image_path}, "A")
            # #endregion
            if self.image:
                # 블록 크기를 정확히 block_size에 맞게 (간격 없이 붙어있도록)
                self.image = pygame.transform.scale(self.image, (self.block_size, self.block_size))
                # #region agent log
                debug_log("world.py:46", "Image scaled", {"block_type": self.block_type}, "A")
                # #endregion
        
        if not self.image:
            # #region agent log
            debug_log("world.py:49", "Using fallback image", {"block_type": self.block_type}, "A")
            # #endregion
            # 기본 이미지
            self.image = pygame.Surface((self.block_size, self.block_size))
            if self.block_type == 'ground':
                self.image.fill(Colors.BROWN)
            elif self.block_type == 'tree':
                self.image.fill((34, 139, 34))
            elif self.block_type == 'tree_leaf':
                self.image.fill((0, 128, 0))
            elif self.block_type == 'water':
                # 물 piskel이 없을 경우를 위한 폴백 (반투명 파란색)
                self.image = pygame.Surface((self.block_size, self.block_size), pygame.SRCALPHA)
                self.image.fill((64, 164, 223, 128))  # 반투명 파란색 (alpha=128)
            elif self.block_type == 'portal':
                # portal 폴백 이미지 (보라색)
                self.image = pygame.Surface((self.block_size, self.block_size))
                self.image.fill((128, 0, 128))  # 보라색
            elif self.block_type == 'rock':
                # rock 폴백 이미지 (회색)
                self.image.fill((100, 100, 100))  # 회색
            else:
                self.image.fill(Colors.GRAY)
    
    def get_rect(self):
        """블록의 충돌 사각형 반환"""
        return pygame.Rect(self.x, self.y, self.block_size, self.block_size)
    
    def draw(self, screen, camera_x, camera_y, dt=0.0):
        """블록 그리기 - 최적화된 버전"""
        # dt가 None이거나 음수인 경우 처리
        if dt is None or dt < 0:
            dt = 0.0
            
        screen_x = int(self.x - camera_x)
        screen_y = int(self.y - camera_y)
        
        # 화면 밖이면 그리지 않음 (더 빠른 검사)
        screen_width = screen.get_width()
        screen_height = screen.get_height()
        if (screen_x < -self.block_size or screen_x > screen_width + self.block_size or
            screen_y < -self.block_size or screen_y > screen_height + self.block_size):
            return
        
        # #region agent log
        if self.block_type == 'tree':
            debug_log("world.py:62", "Drawing tree block", {"block_type": self.block_type, "image_is_none": self.image is None}, "A")
        # #endregion
        
        # portal 애니메이션 처리
        if self.block_type == 'portal':
            self.animation_time += dt
            # 색상이 변하는 애니메이션 (보라색 -> 파란색 -> 보라색)
            color_cycle = (math.sin(self.animation_time * 3.0) + 1.0) / 2.0  # 0.0 ~ 1.0
            # 보라색(128, 0, 128)과 파란색(0, 0, 255) 사이를 보간
            r = int(128 + (0 - 128) * color_cycle)
            g = int(0 + (0 - 0) * color_cycle)
            b = int(128 + (255 - 128) * color_cycle)
            
            # 원본 이미지가 있으면 색상 조정, 없으면 새로 생성
            if self.image:
                # 이미지 복사 후 색상 조정
                try:
                    animated_image = self.image.copy()
                    # 색상 조정 (HSV 방식보다 간단한 방법)
                    color_mult = pygame.Surface((self.block_size, self.block_size))
                    color_mult.fill((r, g, b))
                    animated_image.blit(color_mult, (0, 0), special_flags=pygame.BLEND_MULT)
                    screen.blit(animated_image, (screen_x, screen_y))
                except Exception:
                    # 오류 발생 시 단순히 원본 이미지 표시
                    screen.blit(self.image, (screen_x, screen_y))
            else:
                # 폴백 이미지
                portal_surface = pygame.Surface((self.block_size, self.block_size))
                portal_surface.fill((r, g, b))
                screen.blit(portal_surface, (screen_x, screen_y))
        else:
            # 블록 그리기 (그림자 제거하여 성능 최적화)
            if self.image:
                # 모든 블록을 동일하게 그리기 (물도 일반 이미지로 처리하여 성능 향상)
                screen.blit(self.image, (screen_x, screen_y))


class Chunk:
    """청크 클래스 (12블록 길이)"""
    
    def __init__(self, chunk_x, chunk_y, block_size=32):
        self.chunk_x = chunk_x
        self.chunk_y = chunk_y
        self.block_size = block_size
        self.blocks = {}  # {(block_x, block_y): Block}
        self.generated = False
    
    def get_world_x(self):
        """청크의 월드 X 좌표"""
        return self.chunk_x * 12 * self.block_size
    
    def get_world_y(self):
        """청크의 월드 Y 좌표"""
        return self.chunk_y * 12 * self.block_size
    
    def add_block(self, block_x, block_y, block_type='ground'):
        """블록 추가"""
        # #region agent log
        debug_log("world.py:106", "Chunk.add_block called", {"block_type": block_type, "block_x": block_x, "block_y": block_y}, "A")
        # #endregion
        world_x = self.get_world_x() + block_x * self.block_size
        world_y = self.get_world_y() + block_y * self.block_size
        block = Block(world_x, world_y, block_type, self.block_size)
        # #region agent log
        debug_log("world.py:111", "Block created and added", {"block_type": block.block_type, "actual_block_type": block.block_type}, "A")
        # #endregion
        self.blocks[(block_x, block_y)] = block
    
    def has_block(self, block_x, block_y):
        """블록이 있는지 확인"""
        return (block_x, block_y) in self.blocks
    
    def get_block(self, block_x, block_y):
        """블록 가져오기"""
        return self.blocks.get((block_x, block_y))
    
    def remove_block(self, block_x, block_y):
        """블록 제거"""
        if (block_x, block_y) in self.blocks:
            del self.blocks[(block_x, block_y)]
    
    def draw(self, screen, camera_x, camera_y, dt=0.0):
        """청크의 모든 블록 그리기 - 최적화된 버전"""
        screen_width = screen.get_width()
        screen_height = screen.get_height()
        
        # 화면 범위 계산 (마진 추가하여 부드러운 스크롤)
        margin = self.block_size * 2
        screen_left = camera_x - margin
        screen_right = camera_x + screen_width + margin
        screen_top = camera_y - margin
        screen_bottom = camera_y + screen_height + margin
        
        for block in self.blocks.values():
            # 화면 밖 블록은 그리지 않음 (성능 최적화) - 빠른 AABB 검사
            block_right = block.x + block.width
            block_bottom = block.y + block.height
            if (block_right < screen_left or block.x > screen_right or
                block_bottom < screen_top or block.y > screen_bottom):
                continue
            try:
                block.draw(screen, camera_x, camera_y, dt)
            except Exception:
                # 오류 발생 시 기본 렌더링
                if block.image:
                    screen_x = int(block.x - camera_x)
                    screen_y = int(block.y - camera_y)
                    screen.blit(block.image, (screen_x, screen_y))


class World:
    """월드 클래스 (무한 맵)"""
    
    def __init__(self, block_size=32):
        self.block_size = block_size
        self.chunk_size = 12  # 1청크 = 12블록
        self.chunks = {}  # {(chunk_x, chunk_y): Chunk}
        self.generated_chunks = set()
    
    def get_chunk(self, chunk_x, chunk_y):
        """청크 가져오기 또는 생성"""
        key = (chunk_x, chunk_y)
        if key not in self.chunks:
            self.chunks[key] = Chunk(chunk_x, chunk_y, self.block_size)
        return self.chunks[key]
    
    def generate_chunk(self, chunk_x, chunk_y):
        """청크 생성"""
        key = (chunk_x, chunk_y)
        if key in self.generated_chunks:
            return
        
        chunk = self.get_chunk(chunk_x, chunk_y)
        
        # 기본 플랫폼 생성 (두께 2-3블록, y=1부터 시작하여 나무 생성 공간 확보)
        platform_thickness = random.randint(2, 3)  # 2-3블록 두께
        platform_start_y = 1  # y=1부터 시작 (y=0은 나무 생성 공간)
        for x in range(12):
            for y in range(platform_start_y, platform_start_y + platform_thickness):
                chunk.add_block(x, y, 'ground')
        
        # 산 생성 (큰 산)
        if random.random() < 0.4:  # 40% 확률로 산 생성
            mountain_type = random.choice(['small', 'medium', 'large'])
            if mountain_type == 'small':
                mountain_height = random.randint(3, 6)
                mountain_start = random.randint(0, 6)
                mountain_width = random.randint(3, 6)
            elif mountain_type == 'medium':
                mountain_height = random.randint(6, 10)
                mountain_start = random.randint(0, 4)
                mountain_width = random.randint(5, 8)
            else:  # large
                mountain_height = random.randint(10, 15)
                mountain_start = random.randint(0, 2)
                mountain_width = random.randint(7, 12)
            
            mountain_end = min(mountain_start + mountain_width, 12)
            
            # 산 생성 (삼각형 모양)
            for x in range(mountain_start, mountain_end):
                # 삼각형 높이 계산
                center_x = (mountain_start + mountain_end) / 2
                distance_from_center = abs(x - center_x)
                max_distance = (mountain_end - mountain_start) / 2
                if max_distance > 0:
                    height_factor = 1.0 - (distance_from_center / max_distance)
                    current_height = int(mountain_height * height_factor)
                else:
                    current_height = mountain_height
                
                # 산 블록 생성
                for y in range(platform_thickness, platform_thickness + current_height):
                    if not chunk.has_block(x, y):
                        chunk.add_block(x, y, 'ground')
        
        # 작은 언덕 생성
        elif random.random() < 0.5:  # 50% 확률로 작은 언덕
            hill_height = random.randint(2, 5)
            hill_start = random.randint(0, 8)
            hill_width = random.randint(2, 5)
            hill_end = min(hill_start + hill_width, 12)
            
            for x in range(hill_start, hill_end):
                for y in range(platform_thickness, platform_thickness + hill_height):
                    if not chunk.has_block(x, y):
                        chunk.add_block(x, y, 'ground')
        
        # 구덩이 생성 (더 큰 구덩이)
        if random.random() < 0.4:  # 40% 확률로 구덩이 생성
            hole_type = random.choice(['small', 'medium', 'large'])
            if hole_type == 'small':
                hole_start = random.randint(2, 8)
                hole_width = random.randint(1, 2)
            elif hole_type == 'medium':
                hole_start = random.randint(1, 7)
                hole_width = random.randint(3, 5)
            else:  # large
                hole_start = random.randint(0, 5)
                hole_width = random.randint(5, 8)
            
            hole_end = min(hole_start + hole_width, 12)
            
            # 구덩이 생성 (양쪽에 블록이 있어야 함)
            can_create_hole = True
            platform_start_y = 1
            if hole_start > 0 and not chunk.has_block(hole_start - 1, platform_start_y):
                can_create_hole = False
            if hole_end < 12 and not chunk.has_block(hole_end, platform_start_y):
                can_create_hole = False
            
            if can_create_hole:
                # 구덩이에 물 채우기 (큰 구덩이에만 15% 확률로 생성, 작은 구덩이는 생성 안 함)
                fill_with_water = False
                if hole_type == 'large' and random.random() < 0.15:  # 큰 구덩이에만 15% 확률
                    fill_with_water = True
                
                for x in range(hole_start, hole_end):
                    # 플랫폼 두께만큼 제거
                    for y in range(platform_start_y, platform_start_y + platform_thickness):
                        if chunk.has_block(x, y):
                            chunk.remove_block(x, y)
                        
                        # 물 채우기 (구덩이 바닥에만, 큰 구덩이에만)
                        if fill_with_water and y == platform_start_y + platform_thickness - 1:
                            chunk.add_block(x, y, 'water')
        
        # 나무 생성 (맵에 많이 생성되도록)
        # 플랫폼이 있는 청크에서 80% 확률로 나무 생성
        # 청크당 1-3개의 나무 생성
        if random.random() < 0.8:  # 80% 확률로 나무 생성
            tree_count = random.randint(1, 3)  # 청크당 1-3개의 나무
            trees_generated = 0
            
            for _ in range(tree_count):
                tree_x = random.randint(1, 10)
                attempts = 0
                while attempts < 10:  # 최대 10번 시도
                    if self.generate_tree(chunk, tree_x):
                        trees_generated += 1
                        break
                    tree_x = random.randint(1, 10)
                    attempts += 1
        
        # 블록 연결 확인 및 수정 (모든 블록이 붙어있도록 보장)
        # 나무는 연결 확인에서 제외되므로 항상 실행
        self.ensure_block_connectivity(chunk)
        
        self.generated_chunks.add(key)
        chunk.generated = True
    
    def generate_other_world_chunk(self, chunk_x, chunk_y):
        """다른 세계 청크 생성 (y 99~50은 ground, 그 이후는 복잡한 rock 지형)"""
        key = (chunk_x, chunk_y)
        if key in self.generated_chunks:
            return
        
        chunk = self.get_chunk(chunk_x, chunk_y)
        
        # 청크의 월드 y 좌표 범위 계산
        chunk_world_y = chunk.get_world_y()
        chunk_world_y_end = chunk_world_y + self.chunk_size * self.block_size
        
        # 블록 인덱스로 변환 (y 좌표는 위로 올라갈수록 음수이므로 절댓값 사용)
        chunk_block_y_start = int(abs(chunk_world_y) // self.block_size)
        chunk_block_y_end = int(abs(chunk_world_y_end) // self.block_size)
        
        # y 99에서 50까지는 ground 블록 (블록 인덱스는 양수)
        ground_start_y = 99
        ground_end_y = 50
        
        # 기본 ground 플랫폼 생성
        for x in range(12):
            for block_y in range(chunk_block_y_start, chunk_block_y_end + 1):
                local_x = x
                local_y = block_y - chunk_block_y_start
                
                if local_y < 0 or local_y >= self.chunk_size:
                    continue
                
                # y 99~50: ground 블록
                if ground_end_y <= block_y <= ground_start_y:
                    chunk.add_block(local_x, local_y, 'ground')
        
        # 복잡한 rock 지형 생성 (y 50 미만)
        # 랜덤 시드 생성 (청크 좌표 기반)
        random.seed(chunk_x * 1000 + chunk_y)
        
        # 다양한 rock 구조물 생성
        structure_type = random.choice(['pillars', 'bridge', 'maze', 'spikes', 'tower', 'chaos'])
        
        if structure_type == 'pillars':
            # 기둥들 생성
            pillar_count = random.randint(2, 4)
            for _ in range(pillar_count):
                pillar_x = random.randint(0, 11)
                pillar_height = random.randint(5, 20)
                pillar_start_y = ground_end_y - 1
                for y in range(pillar_start_y - pillar_height, pillar_start_y):
                    local_x = pillar_x
                    local_y = y - chunk_block_y_start
                    if 0 <= local_y < self.chunk_size:
                        chunk.add_block(local_x, local_y, 'rock')
        
        elif structure_type == 'bridge':
            # 다리 생성
            bridge_start_x = random.randint(0, 5)
            bridge_width = random.randint(4, 8)
            bridge_y = ground_end_y - random.randint(3, 8)
            for x in range(bridge_start_x, min(bridge_start_x + bridge_width, 12)):
                local_x = x
                local_y = bridge_y - chunk_block_y_start
                if 0 <= local_y < self.chunk_size:
                    chunk.add_block(local_x, local_y, 'rock')
                    # 다리 아래 기둥
                    for y in range(bridge_y + 1, ground_end_y):
                        local_y = y - chunk_block_y_start
                        if 0 <= local_y < self.chunk_size:
                            chunk.add_block(local_x, local_y, 'rock')
        
        elif structure_type == 'maze':
            # 미로 같은 구조
            for x in range(12):
                for y in range(ground_end_y - random.randint(10, 30), ground_end_y):
                    if random.random() < 0.6:  # 60% 확률로 블록 생성
                        local_x = x
                        local_y = y - chunk_block_y_start
                        if 0 <= local_y < self.chunk_size:
                            chunk.add_block(local_x, local_y, 'rock')
        
        elif structure_type == 'spikes':
            # 가시 구조
            spike_count = random.randint(3, 6)
            for _ in range(spike_count):
                spike_x = random.randint(0, 11)
                spike_height = random.randint(3, 10)
                spike_y = ground_end_y - 1
                for y in range(spike_y - spike_height, spike_y):
                    local_x = spike_x
                    local_y = y - chunk_block_y_start
                    if 0 <= local_y < self.chunk_size:
                        chunk.add_block(local_x, local_y, 'rock')
        
        elif structure_type == 'tower':
            # 탑 구조
            tower_x = random.randint(2, 9)
            tower_width = random.randint(2, 4)
            tower_height = random.randint(15, 30)
            tower_y = ground_end_y - 1
            for x in range(tower_x, min(tower_x + tower_width, 12)):
                for y in range(tower_y - tower_height, tower_y):
                    local_x = x
                    local_y = y - chunk_block_y_start
                    if 0 <= local_y < self.chunk_size:
                        chunk.add_block(local_x, local_y, 'rock')
        
        elif structure_type == 'chaos':
            # 완전히 미친 지형 (무작위 rock 블록)
            for x in range(12):
                for y in range(ground_end_y - random.randint(20, 40), ground_end_y):
                    if random.random() < 0.4:  # 40% 확률로 블록 생성
                        local_x = x
                        local_y = y - chunk_block_y_start
                        if 0 <= local_y < self.chunk_size:
                            chunk.add_block(local_x, local_y, 'rock')
        
        # 랜덤 시드 초기화 (다른 부분에 영향 주지 않도록)
        random.seed()
        
        self.generated_chunks.add(key)
        chunk.generated = True
    
    def ensure_block_connectivity(self, chunk):
        """청크의 모든 블록이 연결되어 있는지 확인하고 수정"""
        # 연결되지 않은 블록 제거
        blocks_to_remove = []
        
        # 플랫폼 최대 두께 찾기 (y=1, 2, 3 중 가장 높은 블록)
        max_platform_y = -1
        for (block_x, block_y), block in chunk.blocks.items():
            if block.block_type == 'ground' and 1 <= block_y <= 3:
                if block_y > max_platform_y:
                    max_platform_y = block_y
        
        for (block_x, block_y), block in chunk.blocks.items():
            if block.block_type in ['tree', 'tree_leaf']:
                continue  # 나무는 별도 처리
            
            # 아래, 위, 왼쪽, 오른쪽 중 하나라도 블록이 있어야 함
            has_connection = False
            
            # 아래 확인 (플랫폼 최대 두께까지는 연결된 것으로 간주)
            if block_y <= max_platform_y:
                has_connection = True  # 플랫폼은 항상 연결됨
            elif chunk.has_block(block_x, block_y - 1):
                has_connection = True
            
            # 위 확인
            if chunk.has_block(block_x, block_y + 1):
                has_connection = True
            
            # 왼쪽 확인
            if block_x > 0 and chunk.has_block(block_x - 1, block_y):
                has_connection = True
            
            # 오른쪽 확인
            if block_x < 11 and chunk.has_block(block_x + 1, block_y):
                has_connection = True
            
            if not has_connection:
                blocks_to_remove.append((block_x, block_y))
        
        # 연결되지 않은 블록 제거
        for block_pos in blocks_to_remove:
            chunk.remove_block(block_pos[0], block_pos[1])
    
    def generate_tree(self, chunk, tree_x=None):
        """나무 생성 (tree_x가 None이면 랜덤 위치) - 더 길고 다양한 모양"""
        # 나무 크기 결정 (작은 나무 50%, 중간 나무 30%, 큰 나무 20%)
        rand = random.random()
        if rand < 0.5:
            # 작은 나무 (더 길게)
            tree_height = random.randint(8, 15)
            leaf_count = random.randint(20, 40)
            tree_type = 'small'
        elif rand < 0.8:
            # 중간 나무
            tree_height = random.randint(15, 25)
            leaf_count = random.randint(50, 100)
            tree_type = 'medium'
        else:
            # 큰 나무 (매우 길게)
            tree_height = random.randint(25, 40)
            leaf_count = random.randint(100, 200)
            tree_type = 'large'
        
        # 플랫폼 최상단 찾기 (모든 ground 블록 확인, y=1부터 시작)
        platform_top = None
        for (block_x, block_y), block in chunk.blocks.items():
            if block.block_type == 'ground' and 1 <= block_y <= 3:
                if platform_top is None or block_y < platform_top:
                    platform_top = block_y
        
        if platform_top is None:
            return False
        
        # platform_top이 0이면 나무를 생성할 수 없음 (y=-1은 불가능)
        if platform_top == 0:
            return False
        
        # 나무 위치 찾기 (플랫폼 최상단에 ground 블록이 있는 곳)
        if tree_x is None:
            tree_x = random.randint(1, 10)
        
        # 플랫폼 최상단에 ground 블록이 있는지 확인
        block_at_pos = chunk.get_block(tree_x, platform_top)
        if not block_at_pos or block_at_pos.block_type != 'ground':
            # 다른 위치 시도
            valid_positions = []
            for x in range(12):
                block = chunk.get_block(x, platform_top)
                if block and block.block_type == 'ground':
                    valid_positions.append(x)
            
            if not valid_positions:
                return False
            
            tree_x = random.choice(valid_positions)
            block_at_pos = chunk.get_block(tree_x, platform_top)
        
        # 이미 나무가 있는 위치면 건너뛰기
        if block_at_pos and block_at_pos.block_type in ['tree', 'tree_leaf']:
            return False
        
        # 나무 줄기 생성 (platform_top-1부터 시작해서 위로 올라감)
        tree_start_y = platform_top - 1
        
        # 나무 모양 결정 (직선형, 곡선형, 가지형)
        tree_shape = random.choice(['straight', 'curved', 'branching'])
        
        if tree_shape == 'straight':
            # 직선형 나무 (기본)
            for y in range(tree_start_y, max(-1, tree_start_y - tree_height), -1):
                if y >= 0 and not chunk.has_block(tree_x, y):
                    chunk.add_block(tree_x, y, 'tree')
        
        elif tree_shape == 'curved':
            # 곡선형 나무 (약간 좌우로 흔들림)
            curve_offset = 0
            for i, y in enumerate(range(tree_start_y, max(-1, tree_start_y - tree_height), -1)):
                if y >= 0:
                    current_x = tree_x + curve_offset
                    if 0 <= current_x < 12 and not chunk.has_block(current_x, y):
                        chunk.add_block(current_x, y, 'tree')
                    # 곡선 생성 (매 3블록마다 방향 변경)
                    if i % 3 == 0:
                        curve_offset += random.choice([-1, 0, 1])
                        curve_offset = max(-1, min(1, curve_offset))  # -1 ~ 1 범위로 제한
        
        else:  # branching
            # 가지형 나무 (주 줄기 + 옆 가지) - 단순화
            main_trunk_height = int(tree_height * 0.7)  # 주 줄기 높이
            
            # 주 줄기 생성
            for y in range(tree_start_y, max(-1, tree_start_y - main_trunk_height), -1):
                if y >= 0 and not chunk.has_block(tree_x, y):
                    chunk.add_block(tree_x, y, 'tree')
            
            # 가지 생성 (2-3개) - 범위 검증 강화
            branch_start_y = max(0, tree_start_y - main_trunk_height)
            branch_end_y = max(0, tree_start_y - 3)
            
            if branch_end_y > branch_start_y:
                branch_count = random.randint(2, 3)
                for _ in range(branch_count):
                    branch_y = random.randint(branch_start_y, branch_end_y)
                    branch_direction = random.choice([-1, 1])  # 왼쪽 또는 오른쪽
                    branch_length = random.randint(2, 4)
                    
                    for i in range(branch_length):
                        branch_x = tree_x + (branch_direction * (i + 1))
                        if 0 <= branch_x < 12 and branch_y >= 0 and not chunk.has_block(branch_x, branch_y):
                            chunk.add_block(branch_x, branch_y, 'tree')
        
        # 나뭇잎 생성 (나무 줄기 위쪽에 생성, 단순화하여 성능 개선)
        leaf_positions = []
        
        # 나뭇잎 생성 범위 (단순화)
        leaf_start_y = max(0, tree_start_y - tree_height + 2)
        leaf_end_y = max(0, tree_start_y - tree_height - 3)
        
        # 나뭇잎 생성 패턴 (단순화)
        leaf_pattern = random.choice(['circular', 'wide'])
        leaf_width = random.randint(3, 5) if leaf_pattern == 'wide' else random.randint(2, 4)
        
        # 나뭇잎 생성 (성능 최적화)
        for y in range(leaf_start_y, leaf_end_y - 1, -1):
            if y < 0:
                break
            
            for x in range(tree_x - leaf_width, tree_x + leaf_width + 1):
                if 0 <= x < 12:
                    # 원형 패턴인 경우 거리 체크
                    if leaf_pattern == 'circular':
                        distance = abs(x - tree_x)
                        if distance > leaf_width:
                            continue
                    
                    # 이미 나뭇잎이 있거나 나무 줄기가 아닌 경우에만 추가
                    block = chunk.get_block(x, y)
                    if not block or block.block_type != 'tree':
                        if (x, y) not in leaf_positions:
                            if random.random() < 0.7:  # 70% 확률로 나뭇잎 생성
                                leaf_positions.append((x, y))
        
        # 나뭇잎 개수 조정 (최대 개수 제한)
        if len(leaf_positions) > leaf_count:
            leaf_positions = random.sample(leaf_positions, min(leaf_count, len(leaf_positions)))
        
        # 나뭇잎 생성
        for x, y in leaf_positions:
            if not chunk.has_block(x, y):
                chunk.add_block(x, y, 'tree_leaf')
        
        return True
    
    def update_rendered_chunks(self, player_x, player_y, render_distance=3, use_other_world=False):
        """플레이어 주변 청크 렌더링"""
        player_chunk_x = get_chunk_coord(player_x, self.chunk_size * self.block_size)
        player_chunk_y = get_chunk_coord(player_y, self.chunk_size * self.block_size)
        
        # 플레이어 주변 청크 생성
        for dx in range(-render_distance, render_distance + 1):
            for dy in range(-render_distance, render_distance + 1):
                chunk_x = player_chunk_x + dx
                chunk_y = player_chunk_y + dy
                if use_other_world or self.is_other_world:
                    self.generate_other_world_chunk(chunk_x, chunk_y)
                else:
                    self.generate_chunk(chunk_x, chunk_y)
        
        # 멀리 떨어진 청크 제거 (메모리 관리)
        chunks_to_remove = []
        for (chunk_x, chunk_y), chunk in self.chunks.items():
            dist_x = abs(chunk_x - player_chunk_x)
            dist_y = abs(chunk_y - player_chunk_y)
            if dist_x > render_distance + 2 or dist_y > render_distance + 2:
                chunks_to_remove.append((chunk_x, chunk_y))
        
        for key in chunks_to_remove:
            del self.chunks[key]
            self.generated_chunks.discard(key)
    
    def find_ground_y(self, x, player_bottom, height):
        """플레이어 발 아래 블록 위에 정확히 서도록 Y 좌표 찾기 - 최적화된 버전"""
        # 플레이어 발 아래 블록 검색 (더 좁은 범위)
        player_left = int(x)
        player_right = int(x + height)
        search_top = int(player_bottom - height * 2)
        search_bottom = int(player_bottom + self.block_size)
        
        min_chunk_x = get_chunk_coord(x, self.chunk_size * self.block_size)
        max_chunk_x = get_chunk_coord(x + height, self.chunk_size * self.block_size)
        min_chunk_y = get_chunk_coord(search_top, self.chunk_size * self.block_size)
        max_chunk_y = get_chunk_coord(search_bottom, self.chunk_size * self.block_size)
        
        best_block_top = None  # 가장 높은 블록의 top
        
        for chunk_x in range(min_chunk_x, max_chunk_x + 1):
            for chunk_y in range(min_chunk_y, max_chunk_y + 1):
                chunk = self.chunks.get((chunk_x, chunk_y))
                if chunk:
                    for block in chunk.blocks.values():
                        # 물 블록은 통과 가능하므로 바닥 계산에서 제외
                        if block.block_type == 'water':
                            continue
                        
                        # AABB 충돌 검사 (X축 겹침 확인)
                        block_left = int(block.x)
                        block_right = int(block.x + block.width)
                        block_top = int(block.y)
                        
                        if player_right > block_left and player_left < block_right:
                            # 블록이 플레이어 발 아래에 있는지 확인
                            if block_top <= player_bottom and block_top >= search_top:
                                # 가장 높은 블록 찾기
                                if best_block_top is None or block_top > best_block_top:
                                    best_block_top = block_top
        
        if best_block_top is not None:
            # 블록 위에 정확히 서도록
            return best_block_top - height
        else:
            return player_bottom - height
    
    def find_ceiling_y(self, x, player_top, height):
        """플레이어 머리 위 블록 아래에 정확히 멈추도록 Y 좌표 찾기 - 최적화된 버전"""
        # 플레이어 머리 위 블록 검색 (더 좁은 범위)
        player_left = int(x)
        player_right = int(x + height)
        search_top = int(player_top - self.block_size * 2)
        search_bottom = int(player_top + height)
        
        min_chunk_x = get_chunk_coord(x, self.chunk_size * self.block_size)
        max_chunk_x = get_chunk_coord(x + height, self.chunk_size * self.block_size)
        min_chunk_y = get_chunk_coord(search_top, self.chunk_size * self.block_size)
        max_chunk_y = get_chunk_coord(search_bottom, self.chunk_size * self.block_size)
        
        best_block_bottom = None  # 가장 낮은 블록의 bottom
        
        for chunk_x in range(min_chunk_x, max_chunk_x + 1):
            for chunk_y in range(min_chunk_y, max_chunk_y + 1):
                chunk = self.chunks.get((chunk_x, chunk_y))
                if chunk:
                    for block in chunk.blocks.values():
                        # 물 블록은 통과 가능하므로 천장 계산에서 제외
                        if block.block_type == 'water':
                            continue
                        
                        # AABB 충돌 검사 (X축 겹침 확인)
                        block_left = int(block.x)
                        block_right = int(block.x + block.width)
                        block_bottom = int(block.y + block.height)
                        
                        if player_right > block_left and player_left < block_right:
                            # 블록이 플레이어 머리 위에 있는지 확인
                            if block_bottom >= player_top and block_bottom <= search_bottom:
                                # 가장 낮은 블록 찾기
                                if best_block_bottom is None or block_bottom < best_block_bottom:
                                    best_block_bottom = block_bottom
        
        if best_block_bottom is not None:
            # 블록 아래에 정확히 멈추도록
            return best_block_bottom
        else:
            return player_top
    
    def check_block_collision(self, x, y, width, height):
        """블록과의 충돌 검사 - 최적화된 버전"""
        # 플레이어 AABB 계산
        player_left = int(x)
        player_right = int(x + width)
        player_top = int(y)
        player_bottom = int(y + height)
        
        # 플레이어 주변 청크 범위 계산 (더 좁은 범위)
        min_chunk_x = get_chunk_coord(x, self.chunk_size * self.block_size)
        max_chunk_x = get_chunk_coord(x + width, self.chunk_size * self.block_size)
        min_chunk_y = get_chunk_coord(y, self.chunk_size * self.block_size)
        max_chunk_y = get_chunk_coord(y + height, self.chunk_size * self.block_size)
        
        # 주변 청크의 블록만 검사
        for chunk_x in range(min_chunk_x, max_chunk_x + 1):
            for chunk_y in range(min_chunk_y, max_chunk_y + 1):
                chunk = self.chunks.get((chunk_x, chunk_y))
                if chunk:
                    for block in chunk.blocks.values():
                        # 물 블록은 통과 가능
                        if block.block_type == 'water':
                            continue
                        
                        # AABB 충돌 검사 (Rect 생성 없이)
                        block_left = int(block.x)
                        block_right = int(block.x + block.width)
                        block_top = int(block.y)
                        block_bottom = int(block.y + block.height)
                        
                        if (player_right > block_left and player_left < block_right and
                            player_bottom > block_top and player_top < block_bottom):
                            return True
        
        return False
    
    def check_portal_collision(self, player_x, player_y, player_width, player_height):
        """포탈과 플레이어의 충돌 검사 (더 넓은 범위로 검사)"""
        # 플레이어 중심점
        player_center_x = player_x + player_width // 2
        player_center_y = player_y + player_height // 2
        
        # 플레이어 주변 청크 범위 계산 (더 넓은 범위)
        search_range = 2  # 2청크 범위까지 검사
        min_chunk_x = get_chunk_coord(player_x - self.chunk_size * self.block_size * search_range, self.chunk_size * self.block_size)
        max_chunk_x = get_chunk_coord(player_x + player_width + self.chunk_size * self.block_size * search_range, self.chunk_size * self.block_size)
        min_chunk_y = get_chunk_coord(player_y - self.chunk_size * self.block_size * search_range, self.chunk_size * self.block_size)
        max_chunk_y = get_chunk_coord(player_y + player_height + self.chunk_size * self.block_size * search_range, self.chunk_size * self.block_size)
        
        # 주변 청크의 포탈 블록 검사
        for chunk_x in range(min_chunk_x, max_chunk_x + 1):
            for chunk_y in range(min_chunk_y, max_chunk_y + 1):
                chunk = self.chunks.get((chunk_x, chunk_y))
                if chunk:
                    for block in chunk.blocks.values():
                        if block.block_type == 'portal':
                            # 포탈 중심점
                            portal_center_x = block.x + block.width // 2
                            portal_center_y = block.y + block.height // 2
                            
                            # 플레이어 중심점과 포탈 중심점 사이의 거리
                            dx = player_center_x - portal_center_x
                            dy = player_center_y - portal_center_y
                            distance = (dx * dx + dy * dy) ** 0.5
                            
                            # 포탈 블록 크기의 1.5배 범위 내에 있으면 충돌
                            collision_range = max(block.width, block.height) * 1.5
                            
                            if distance <= collision_range:
                                return True
        
        return False
    
    def check_on_ground(self, x, y, width, height):
        """바닥에 닿았는지 확인 - 최적화된 버전"""
        # 플레이어 발 아래에 블록이 있는지 확인
        player_bottom = int(y + height)
        test_left = int(x)
        test_right = int(x + width)
        test_top = player_bottom
        test_bottom = player_bottom + 5  # 5픽셀 높이로 검사
        
        # 주변 청크의 블록 검사 (더 좁은 범위)
        min_chunk_x = get_chunk_coord(x, self.chunk_size * self.block_size)
        max_chunk_x = get_chunk_coord(x + width, self.chunk_size * self.block_size)
        min_chunk_y = get_chunk_coord(player_bottom, self.chunk_size * self.block_size)
        max_chunk_y = get_chunk_coord(player_bottom + 5, self.chunk_size * self.block_size)
        
        for chunk_x in range(min_chunk_x, max_chunk_x + 1):
            for chunk_y in range(min_chunk_y, max_chunk_y + 1):
                chunk = self.chunks.get((chunk_x, chunk_y))
                if chunk:
                    for block in chunk.blocks.values():
                        # 물 블록은 통과 가능
                        if block.block_type == 'water':
                            continue
                        
                        # AABB 충돌 검사
                        block_left = int(block.x)
                        block_right = int(block.x + block.width)
                        block_top = int(block.y)
                        block_bottom = int(block.y + block.height)
                        
                        if (test_right > block_left and test_left < block_right and
                            test_bottom > block_top and test_top < block_bottom):
                            return True
        
        return False
    
    def get_block_at(self, block_x, block_y):
        """블록 인덱스에서 블록 가져오기 (block_x, block_y는 블록 인덱스)"""
        # 블록 인덱스를 청크 좌표로 변환
        chunk_x = block_x // self.chunk_size
        chunk_y = block_y // self.chunk_size
        
        # 청크 내부 좌표 계산
        local_x = block_x % self.chunk_size
        if local_x < 0:
            local_x += self.chunk_size
            chunk_x -= 1
        
        local_y = block_y % self.chunk_size
        if local_y < 0:
            local_y += self.chunk_size
            chunk_y -= 1
        
        chunk = self.chunks.get((chunk_x, chunk_y))
        if not chunk:
            return None
        
        return chunk.get_block(local_x, local_y)
    
    def remove_block_at(self, block_x, block_y):
        """블록 제거 (block_x, block_y는 블록 인덱스)"""
        # 블록 인덱스를 청크 좌표로 변환
        chunk_x = block_x // self.chunk_size
        chunk_y = block_y // self.chunk_size
        
        # 청크 내부 좌표 계산
        local_x = block_x % self.chunk_size
        if local_x < 0:
            local_x += self.chunk_size
            chunk_x -= 1
        
        local_y = block_y % self.chunk_size
        if local_y < 0:
            local_y += self.chunk_size
            chunk_y -= 1
        
        chunk = self.chunks.get((chunk_x, chunk_y))
        if not chunk:
            return None
        
        block = chunk.get_block(local_x, local_y)
        if block:
            chunk.remove_block(local_x, local_y)
            return block
        return None
    
    def place_block_at(self, block_x, block_y, block_type='ground'):
        """블록 설치 (block_x, block_y는 블록 인덱스) - 옆, 아래, 위 어디든 설치 가능"""
        # 이미 블록이 있으면 설치 불가
        if self.get_block_at(block_x, block_y):
            return False
        
        # 주변에 블록이 하나라도 있어야 설치 가능
        # y가 작을수록 위쪽이므로:
        # - 위쪽: block_y - 1
        # - 아래쪽: block_y + 1
        # - 왼쪽: block_x - 1
        # - 오른쪽: block_x + 1
        
        has_adjacent_block = False
        
        # 위쪽 확인
        if self.get_block_at(block_x, block_y - 1):
            has_adjacent_block = True
        
        # 아래쪽 확인
        if self.get_block_at(block_x, block_y + 1):
            has_adjacent_block = True
        
        # 왼쪽 확인
        if self.get_block_at(block_x - 1, block_y):
            has_adjacent_block = True
        
        # 오른쪽 확인
        if self.get_block_at(block_x + 1, block_y):
            has_adjacent_block = True
        
        # 주변에 블록이 없으면 설치 불가
        if not has_adjacent_block:
            return False
        
        # 블록 인덱스를 청크 좌표로 변환
        chunk_x = block_x // self.chunk_size
        chunk_y = block_y // self.chunk_size
        
        # 청크 내부 좌표 계산
        local_x = block_x % self.chunk_size
        if local_x < 0:
            local_x += self.chunk_size
            chunk_x -= 1
        
        local_y = block_y % self.chunk_size
        if local_y < 0:
            local_y += self.chunk_size
            chunk_y -= 1
        
        chunk = self.get_chunk(chunk_x, chunk_y)
        
        world_x = chunk.get_world_x() + local_x * self.block_size
        world_y = chunk.get_world_y() + local_y * self.block_size
        block = Block(world_x, world_y, block_type, self.block_size)
        block.is_natural = False
        chunk.blocks[(local_x, local_y)] = block
        
        return True
    
    def draw(self, screen, camera_x, camera_y, dt=0.0):
        """월드 그리기 - 최적화된 버전"""
        # 화면에 보이는 청크만 그리기 (더 좁은 범위로 최적화)
        screen_width = screen.get_width()
        screen_height = screen.get_height()
        
        # 화면 범위를 약간 확장하여 부드러운 스크롤 지원
        margin = self.chunk_size * self.block_size  # 1청크 여유
        min_chunk_x = get_chunk_coord(camera_x - margin, self.chunk_size * self.block_size)
        max_chunk_x = get_chunk_coord(camera_x + screen_width + margin, self.chunk_size * self.block_size)
        min_chunk_y = get_chunk_coord(camera_y - margin, self.chunk_size * self.block_size)
        max_chunk_y = get_chunk_coord(camera_y + screen_height + margin, self.chunk_size * self.block_size)
        
        for chunk_x in range(min_chunk_x, max_chunk_x + 1):
            for chunk_y in range(min_chunk_y, max_chunk_y + 1):
                chunk = self.chunks.get((chunk_x, chunk_y))
                if chunk:
                    chunk.draw(screen, camera_x, camera_y, dt)

