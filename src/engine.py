"""
各ステップの移動量計算と勝敗判定を行う計算機です

- エンジンに「経過時間」の保持機能を追加し、速度 × 時間 で移動距離を算出するように修正します
"""
from __future__ import annotations
from typing import List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .models import Horse

class SimulationEngine:
    """秒単位の物理計算を行うエンジン"""
    def __init__(self, course_length: int, horses: List[Horse], tick_time: float):
        self.course_length = course_length
        self.horses = horses
        self.tick_time = tick_time
        self.elapsed_time = 0.0  # 経過時間を管理

    def step(self) -> Optional[Horse]:
        """全馬を1ステップ進め、勝者がいれば返す"""
        self.elapsed_time += self.tick_time
        winner: Optional[Horse] = None
        
        for horse in self.horses:
            # 1. 現在の秒速を取得
            speed_per_sec = horse.strategy.calculate_step(horse, horse.jockey, self.course_length)
            # 2. 移動距離 = 秒速 × ステップ秒数
            distance = speed_per_sec * self.tick_time
            horse.position += distance
            
            if horse.position >= self.course_length and winner is None:
                winner = horse
        return winner
