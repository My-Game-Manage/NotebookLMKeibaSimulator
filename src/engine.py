"""
各ステップの移動量計算と勝敗判定を行う計算機です

- エンジンに「経過時間」の保持機能を追加し、速度 × 時間 で移動距離を算出するように修正します
- エンジン側で、ゴールした馬を順番に記録する rankings リストを管理するようにします
- 移動距離に応じてスタミナを減算する処理を追加します
- スパート中はスタミナ消費を激しくすることで、より戦略的なシミュレーションになります
- trategy.calculate_step が返す速度を 「目標速度」 とみなし、acceleration に基づいて current_speed を段階的に近づけます
- step メソッド内で、馬場状態に応じたスタミナ消費倍率を適用します
"""
from __future__ import annotations
from typing import List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .models import Horse, Corner

class SimulationEngine:
    def __init__(self, course_length: int, horses: List[Horse], tick_time: float,
                 corners: list[Corner] = None, track_condition: str = "良"):
        self.course_length = course_length
        self.horses = horses
        self.tick_time = tick_time
        self.corners = corners or [] # RaceConfigから渡されるコーナーリスト
        self.track_condition = track_condition  # 馬場状態を保持
        self.elapsed_time = 0.0
        self.rankings: List[Horse] = []

    def step(self) -> None:
        """1ステップ（tick_time）分のシミュレーションを実行"""
        self.elapsed_time += self.tick_time

        # 1. ドラフティング判定のために、現在コース上にいる馬を位置順（降順）にソート
        active_horses = [h for h in self.horses if h not in self.rankings]
        sorted_horses = sorted(active_horses, key=lambda x: x.position, reverse=True)
        
        for i, horse in enumerate(sorted_horses):
            # 速度計算（strategies.py の決定論的ロジックを呼び出し）

            # --- 2. 目標速度の算出とコーナー制限 ---
            # 戦略による目標速度を取得
            target_speed = horse.strategy.calculate_step(horse, horse.jockey, self.course_length)

            # 現在地がコーナー内か判定
            current_corner = next(
                (c for c in self.corners if c.start_pos <= horse.position <= c.end_pos), 
                None
            )

            corner_stamina_load = 0.0
            if current_corner:
                # 遠心力に基づく速度制限： V = 2.0 * sqrt(R) [会話履歴]
                corner_limit = 2.0 * (current_corner.radius ** 0.5)
                target_speed = min(target_speed, corner_limit)
                
                # コーナー走行によるスタミナ追加負荷 (v^2 / R*10) [会話履歴]
                corner_stamina_load = (horse.current_speed ** 2) / (current_corner.radius * 10.0)

            # --- 3. 加速力(acceleration)による現在速度の更新 [5, 会話履歴] ---
            # acceleration 0-100 を 加速度 0.5〜1.5 m/s^2 程度にマッピング
            accel_val = 0.5 + (horse.acceleration / 100.0)

            speed_diff = target_speed - horse.current_speed
            
            if speed_diff > 0:
                # 加速：目標速度を超えない範囲で加速
                horse.current_speed += min(speed_diff, accel_val * self.tick_time)
            elif speed_diff < 0:
                # 減速（スタミナ切れ等）：目標速度まで減速
                horse.current_speed += max(speed_diff, -accel_val * self.tick_time)

            # 更新された現在速度で移動
            distance = horse.current_speed * self.tick_time
            horse.position += distance

            # --- 4. ドラフティング判定 [13, 会話履歴] ---
            drafting_multiplier = 1.0
            if i > 0:  # 自分が先頭ではない場合のみ判定
                front_horse = sorted_horses[i - 1]
                gap = front_horse.position - horse.position
                # 前方の馬との距離が 0m より大きく 5.0m 以内なら恩恵を受ける
                if 0 < gap <= 5.0:
                    drafting_multiplier = 0.9  # スタミナ消費を10%軽減

            # --- 5. スタミナ消費計算（決定論的） [1, 9, 会話履歴] ---
            # --- 馬場状態による係数の設定 ---
            # "重" の場合はスタミナ消費を 20% 増加させる (1.2倍)
            track_multiplier = 1.2 if self.track_condition == "重" else 1.0

            # --- スタミナ消費計算（決定論的） ---
            # 騎手スキルの平均による効率化 [1, 会話履歴]
            skill_average = (horse.jockey.front_skill + horse.jockey.back_skill) / 2.0
            jockey_efficiency = 1.1 - (skill_average * 0.1) 

            # 消費 = (基本消費 + コーナー負荷) * 騎手効率 * ドラフティング * スパート補正 * 馬場補正
            # 基本消費: 距離 * 0.7 [1, 会話履歴]
            base_consumption = (distance * 0.7) + corner_stamina_load
            spurt_multiplier = 1.3 if horse.is_spurting else 1.0

            # 最終的なスタミナ減算
            horse.current_stamina -= (
                base_consumption * 
                jockey_efficiency * 
                drafting_multiplier * 
                spurt_multiplier * 
                track_multiplier  # 馬場状態の影響を乗算
            )

            # ゴール判定
            if horse.position >= self.course_length:
                horse.position = float(self.course_length)
                if horse not in self.rankings:
                    self.rankings.append(horse)

    def is_all_finished(self) -> bool:
        """全馬がゴールしたかを確認"""
        return len(self.rankings) == len(self.horses)