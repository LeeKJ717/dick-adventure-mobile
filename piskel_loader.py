"""
Piskel 파일 로더
Piskel JSON 파일에서 이미지를 추출하여 Pygame Surface로 변환
"""
import json
import base64
import io
import os
import sys
from PIL import Image
import pygame

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
            "timestamp": 0
        }
        with open(DEBUG_LOG_PATH, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
    except:
        pass
# #endregion


class PiskelLoader:
    """Piskel 파일을 로드하고 Pygame Surface로 변환하는 클래스"""
    
    _cache = {}  # 이미지 캐시
    
    @staticmethod
    def get_resource_path(file_path):
        """실행 파일 또는 일반 스크립트에서 리소스 경로 가져오기"""
        if getattr(sys, 'frozen', False):
            # cx_Freeze 또는 PyInstaller로 빌드된 실행 파일
            if hasattr(sys, '_MEIPASS'):
                # PyInstaller
                base_path = sys._MEIPASS
            else:
                # cx_Freeze - 실행 파일이 있는 디렉토리 사용
                if sys.executable:
                    base_path = os.path.dirname(os.path.abspath(sys.executable))
                else:
                    base_path = os.path.dirname(os.path.abspath(__file__))
        else:
            # 일반 Python 스크립트
            base_path = os.path.dirname(os.path.abspath(__file__))
        
        # 상대 경로 처리
        if not os.path.isabs(file_path):
            full_path = os.path.join(base_path, file_path)
        else:
            full_path = file_path
        
        return full_path
    
    @staticmethod
    def load_piskel(file_path):
        """Piskel 파일을 로드하고 이미지를 반환"""
        # #region agent log
        debug_log("piskel_loader.py:46", "load_piskel called", {"file_path": file_path}, "B")
        # #endregion
        full_path = PiskelLoader.get_resource_path(file_path)
        # #region agent log
        debug_log("piskel_loader.py:50", "Resource path resolved", {"file_path": file_path, "full_path": full_path, "file_exists": os.path.exists(full_path)}, "B")
        # #endregion
        
        # 캐시 확인
        if full_path in PiskelLoader._cache:
            # #region agent log
            debug_log("piskel_loader.py:54", "Cache hit", {"file_path": file_path, "full_path": full_path}, "B")
            # #endregion
            return PiskelLoader._cache[full_path]
        
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Piskel 파일 구조에서 이미지 데이터 추출
            layers = data['piskel']['layers']
            if not layers:
                # #region agent log
                debug_log("piskel_loader.py:63", "No layers found", {"file_path": file_path}, "B")
                # #endregion
                return None
            
            layer_data = json.loads(layers[0])
            chunks = layer_data.get('chunks', [])
            
            if not chunks:
                # #region agent log
                debug_log("piskel_loader.py:69", "No chunks found", {"file_path": file_path}, "B")
                # #endregion
                return None
            
            base64_data = chunks[0].get('base64PNG', '')
            if not base64_data:
                # #region agent log
                debug_log("piskel_loader.py:75", "No base64 data", {"file_path": file_path}, "B")
                # #endregion
                return None
            
            # data:image/png;base64, 접두사 제거
            if base64_data.startswith('data:image/png;base64,'):
                base64_data = base64_data.split(',')[1]
            
            # Base64 디코딩
            image_data = base64.b64decode(base64_data)
            image = Image.open(io.BytesIO(image_data))
            
            # RGBA 모드로 변환
            if image.mode != 'RGBA':
                image = image.convert('RGBA')
            
            # Pygame Surface로 변환
            pygame_image = pygame.image.fromstring(
                image.tobytes(), 
                image.size, 
                image.mode
            )
            
            # 캐시에 저장
            PiskelLoader._cache[full_path] = pygame_image
            # #region agent log
            debug_log("piskel_loader.py:100", "Image loaded successfully", {"file_path": file_path, "image_size": pygame_image.get_size()}, "B")
            # #endregion
            return pygame_image
            
        except Exception as e:
            # #region agent log
            debug_log("piskel_loader.py:105", "Error loading piskel", {"file_path": file_path, "error": str(e)}, "B")
            # #endregion
            print(f"Error loading piskel file {file_path}: {e}")
            # 빨간색 사각형 반환 (에러 표시)
            surf = pygame.Surface((32, 32))
            surf.fill((255, 0, 0))
            return surf
    
    @staticmethod
    def load_piskel_with_cache(file_path, cache=None):
        """캐시를 사용하여 Piskel 파일 로드"""
        if cache is None:
            cache = PiskelLoader._cache
        
        full_path = PiskelLoader.get_resource_path(file_path)
        
        if full_path in cache:
            return cache[full_path]
        
        image = PiskelLoader.load_piskel(file_path)
        if image:
            cache[full_path] = image
        return image

