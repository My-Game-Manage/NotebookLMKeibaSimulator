from __future__ import annotations
from src.models import Horse, RaceConfig
from src.strategies import Strategy

class SimulationEngine:
    """レースの物理計算を司るエンジン"""

    def __init__(self, horse: Horse, strategy: Strategy, config: RaceConfig):
        self.horse = horse
        self.strategy = strategy
        self.config = config
        
        self.current_distance = 0.0
        self.current_stamina = horse.stamina
        self.current_speed = 0.0
        self.finish_time = 0.0  # ステップ数（浮動小数）
        self.is_finished = False
        self._elapsed_steps = 0

    def step(self) -> None:
        """1ステップ(1秒想定)の進行処理"""
        if self.is_finished:
            return

        self._elapsed_steps += 1
        prev_distance = self.current_distance

        # 1. 戦略に基づいたベース目標速度の取得
        target_speed = self.strategy.calculate_step(
            self.current_distance, self.config.distance, self.horse.max_speed
        )

        # 2. スパート判定 (残り600m地点)
        if (self.config.distance - self.current_distance) <= 600.0:
            target_speed *= self.strategy.spurt_multiplier

        # 3. スタミナ消費計算 (速度の二乗に比例、騎手スキルで軽減)
        # 基本定数 50.0 でスケーリング
        efficiency = 1.0 - (self.horse.jockey.skill * 0.2)
        stamina_cost = ((target_speed ** 2) / 50.0) * efficiency
        self.current_stamina -= stamina_cost

        # 4. スタミナ切れによる減速
        if self.current_stamina <= 0:
            self.current_stamina = 0
            target_speed *= 0.3  # 大幅な減速

        self.current_speed = target_speed
        self.current_distance += self.current_speed

        # 5. 完走判定と正確なタイム算出
        if self.current_distance >= self.config.distance:
            # オーバーシュート分を考慮した正確なゴール時間の計算
            overshoot = self.current_distance - self.config.distance
            time_fraction = 1.0 - (overshoot / self.current_speed)
            self.finish_time = float(self._elapsed_steps - 1) + time_fraction
            
            self.current_distance = self.config.distance
            self.is_finished = True