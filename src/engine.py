"""
各ステップの移動量計算と勝敗判定を行う計算機です
"""
from __future__ import annotations
from typing import List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .models import Horse

class SimulationEngine:
    """各ステップの移動量計算と勝敗判定を司る"""
    def __init__(self, course_length: int, horses: List[Horse]):
        self.course_length = course_length
        self.horses = horses

    def step(self) -> Optional[Horse]:
        """全馬を1ステップ進め、勝者がいれば返す"""
        winner: Optional[Horse] = None
        for horse in self.horses:
            # 各馬の戦略に基づいて移動距離を計算
            move = horse.strategy.calculate_step(horse, horse.jockey, self.course_length)
            horse.position += move
            
            # ゴール判定（最初に超えた馬を勝者とする）
            if horse.position >= self.course_length and winner is None:
                winner = horse
        return winner