"""
各ステップの移動量計算と勝敗判定を行う計算機です

- エンジンに「経過時間」の保持機能を追加し、速度 × 時間 で移動距離を算出するように修正します
- エンジン側で、ゴールした馬を順番に記録する rankings リストを管理するようにします
"""
from __future__ import annotations
from typing import List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .models import Horse

class SimulationEngine:
    def __init__(self, course_length: int, horses: List[Horse], tick_time: float):
        self.course_length = course_length
        self.horses = horses
        self.tick_time = tick_time
        self.elapsed_time = 0.0
        self.rankings: List[Horse] = []  # ゴールした順に馬を格納する [1, 2]

    def step(self) -> None:
        self.elapsed_time += self.tick_time
        
        # このステップで新しくゴールした馬を判定するためのリスト
        newly_finished: List[Horse] = []

        for horse in self.horses:
            # すでにゴール済みの馬はスキップ
            if horse in self.rankings:
                continue

            # 移動計算
            speed_per_sec = horse.strategy.calculate_step(horse, horse.jockey, self.course_length)
            horse.position += speed_per_sec * self.tick_time
            
            # ゴール判定
            if horse.position >= self.course_length:
                horse.position = float(self.course_length)
                newly_finished.append(horse)

        # 同時にゴールした場合は、より遠くまで到達していた馬（ハナ差）を優先して順位付け
        newly_finished.sort(key=lambda h: h.position, reverse=True)
        self.rankings.extend(newly_finished)

    def is_all_finished(self) -> bool:
        """全馬がゴールしたかを確認"""
        return len(self.rankings) == len(self.horses)