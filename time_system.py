"""
시간 시스템
"""
import pygame
from utils import lerp


class TimeSystem:
    """시간 시스템 - 아침/점심/저녁/밤/새벽 주기"""
    
    def __init__(self):
        self.total_cycle = 300  # 5분 (초)
        self.period_duration = 60  # 각 시간대 1분 (초)
        self.time = 0  # 현재 시간 (초)
        self.days_passed = 0  # 경과 일수
        
        # 각 시간대의 하늘 색상 (RGB)
        self.period_colors = {
            'morning': (255, 200, 150),      # 아침: 따뜻한 오렌지-핑크
            'noon': (135, 206, 250),         # 점심: 밝은 하늘색
            'evening': (255, 165, 0),        # 저녁: 오렌지
            'night': (25, 25, 112),          # 밤: 어두운 파란색
            'dawn': (75, 0, 130)             # 새벽: 어두운 보라색
        }
    
    def update(self, dt):
        """시간 업데이트"""
        old_time = self.time
        self.time += dt
        if self.time >= self.total_cycle:
            self.time -= self.total_cycle
            self.days_passed += 1  # 하루 경과
    
    def get_current_period(self):
        """현재 시간대 반환"""
        period_index = int(self.time // self.period_duration)
        periods = ['morning', 'noon', 'evening', 'night', 'dawn']
        return periods[period_index % len(periods)]
    
    def get_sky_color(self):
        """하늘 색상 반환 (그라데이션 적용)"""
        period_index = int(self.time // self.period_duration)
        periods = ['morning', 'noon', 'evening', 'night', 'dawn']
        current_period = periods[period_index % len(periods)]
        next_period = periods[(period_index + 1) % len(periods)]
        
        # 현재 시간대 내에서의 진행률 (0.0 ~ 1.0)
        time_in_period = self.time % self.period_duration
        progress = time_in_period / self.period_duration
        
        # 현재 시간대와 다음 시간대의 색상
        current_color = self.period_colors[current_period]
        next_color = self.period_colors[next_period]
        
        # 그라데이션으로 색상 보간
        r = int(lerp(current_color[0], next_color[0], progress))
        g = int(lerp(current_color[1], next_color[1], progress))
        b = int(lerp(current_color[2], next_color[2], progress))
        
        return (r, g, b)
    
    def get_time_string(self):
        """시간 문자열 반환"""
        period_index = int(self.time // self.period_duration)
        periods = ['Morning', 'Noon', 'Evening', 'Night', 'Dawn']
        period = periods[period_index % len(periods)]
        
        time_in_period = self.time % self.period_duration
        minutes = int(time_in_period // 60)
        seconds = int(time_in_period % 60)
        
        return f"{period} {minutes:02d}:{seconds:02d}"
    
    def get_days_string(self):
        """경과 일수 문자열 반환"""
        return f"Day {self.days_passed + 1}"

