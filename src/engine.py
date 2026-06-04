"""
各ステップの移動量計算と勝敗判定を行う計算機です

- エンジンに「経過時間」の保持機能を追加し、速度 × 時間 で移動距離を算出するように修正します
- エンジン側で、ゴールした馬を順番に記録する rankings リストを管理するようにします
- 移動距離に応じてスタミナを減算する処理を追加します
- スパート中はスタミナ消費を激しくすることで、より戦略的なシミュレーションになります
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

            # --- 決定論的なスタミナ消費の効率化 ---
            # 騎手スキルの平均をベースに、消費効率を算出（1.0が基準）
            # スキルの平均値が高いほど、消費係数が下がる（乱数なし）
            skill_average = (horse.jockey.front_skill + horse.jockey.back_skill) / 2.0
            efficiency = 1.1 - (skill_average * 0.1)  # スキル1.0なら1.0倍、1.2なら0.98倍

            # 激しく走るほど（速度が速いほど）消費量が増える計算
            # 移動距離に係数をかけてスタミナを減らす（0.6〜0.8程度に抑える）
            consumption = distance * 0.7 * efficiency
            if horse.is_spurting:
                consumption *= 1.3  # スパート中は1.5倍スタミナを消費する　→ スパート時の追加負荷を少し軽減（1.5 -> 1.3）
            if horse.current_stamina > 0:
                horse.current_stamina -= consumption
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