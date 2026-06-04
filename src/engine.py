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
        """1ステップ（tick_time）分のシミュレーションを実行"""
        self.elapsed_time += self.tick_time

        # 1. ドラフティング判定のために、現在コース上にいる馬を位置順（降順）にソート
        active_horses = [h for h in self.horses if h not in self.rankings]
        sorted_horses = sorted(active_horses, key=lambda x: x.position, reverse=True)
        
        # このステップで新しくゴールした馬を判定するためのリスト
        #newly_finished: List[Horse] = []

        for i, horse in enumerate(sorted_horses):
            # 速度計算（strategies.py の決定論的ロジックを呼び出し）
            speed = horse.strategy.calculate_step(horse, horse.jockey, self.course_length)
            distance = speed * self.tick_time
            horse.position += distance

            # --- 2. ドラフティング（スリップストリーム）判定 ---
            drafting_multiplier = 1.0
            if i > 0:  # 自分が先頭ではない場合のみ判定
                front_horse = sorted_horses[i - 1]
                gap = front_horse.position - horse.position
                # 前方の馬との距離が 0m より大きく 5.0m 以内なら恩恵を受ける
                if 0 < gap <= 5.0:
                    drafting_multiplier = 0.9  # スタミナ消費を10%軽減

            # --- 3. 決定論的なスタミナ消費計算 ---
            # 騎手スキルの平均による効率化（1.0が基準）
            skill_average = (horse.jockey.front_skill + horse.jockey.back_skill) / 2.0
            jockey_efficiency = 1.1 - (skill_average * 0.1) 
            
            # 消費量 = 移動距離 * 基準係数 * 騎手効率 * ドラフティング補正
            consumption = distance * 0.7 * jockey_efficiency * drafting_multiplier

            if horse.is_spurting:
                consumption *= 1.3  # スパート中は1.5倍スタミナを消費する　→ スパート時の追加負荷を少し軽減（1.5 -> 1.3）
            if horse.current_stamina > 0:
                horse.current_stamina -= consumption
                if horse.current_stamina < 0:
                    horse.current_stamina = 0.0

            # ゴール判定
            if horse.position >= self.course_length:
                horse.position = float(self.course_length)
                if horse not in self.rankings:
                    self.rankings.append(horse)

        # 同時にゴールした場合は、より遠くまで到達していた馬（ハナ差）を優先して順位付け
        #newly_finished.sort(key=lambda h: h.position, reverse=True)
        #self.rankings.extend(newly_finished)

    def is_all_finished(self) -> bool:
        """全馬がゴールしたかを確認"""
        return len(self.rankings) == len(self.horses)