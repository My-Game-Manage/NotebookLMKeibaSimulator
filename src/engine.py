"""
各ステップの移動量計算と勝敗判定を行う計算機です

- エンジンに「経過時間」の保持機能を追加し、速度 × 時間 で移動距離を算出するように修正します
- エンジン側で、ゴールした馬を順番に記録する rankings リストを管理するようにします
- 移動距離に応じてスタミナを減算する処理を追加します
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

            # 1. 現在の能力とスタミナ状態に基づき速度を計算
            speed_per_sec = horse.strategy.calculate_step(
                horse, horse.jockey, self.course_length
            )
        
            # 2. 移動とスタミナ消費
            distance = speed_per_sec * self.tick_time
            horse.position += distance
        
            # スタミナ消費ロジック（例: 移動距離分だけスタミナを減らす）
            # 激しく走るほど（速度が速いほど）消費量が増える計算
            if horse.current_stamina > 0:
                horse.current_stamina -= distance
                if horse.current_stamina < 0:
                    horse.current_stamina = 0.0

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