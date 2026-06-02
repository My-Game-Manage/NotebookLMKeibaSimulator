from __future__ import annotations
from abc import ABC, abstractmethod

class Strategy(ABC):
    """脚質戦略の抽象基底クラス"""

    @abstractmethod
    def calculate_step(self, current_dist: float, total_dist: float, base_speed: float) -> float:
        """
        現在の走行距離に基づき、目標速度を算出する。
        """
        pass

    @property
    @abstractmethod
    def spurt_multiplier(self) -> float:
        """スパート時の速度倍率"""
        pass

class RunawayStrategy(Strategy):
    """逃げ: 序盤から飛ばしてリードを作る"""
    def calculate_step(self, current_dist: float, total_dist: float, base_speed: float) -> float:
        return base_speed * 1.10

    @property
    def spurt_multiplier(self) -> float:
        return 1.02

class LeadingStrategy(Strategy):
    """先行: 前方で安定して走行する"""
    def calculate_step(self, current_dist: float, total_dist: float, base_speed: float) -> float:
        return base_speed * 1.05

    @property
    def spurt_multiplier(self) -> float:
        return 1.05

class MidPackStrategy(Strategy):
    """差し: 中盤まで抑え、終盤に加速の準備をする"""
    def calculate_step(self, current_dist: float, total_dist: float, base_speed: float) -> float:
        if current_dist < total_dist * 0.6:
            return base_speed * 0.95
        return base_speed * 1.0

    @property
    def spurt_multiplier(self) -> float:
        return 1.12

class ChaserStrategy(Strategy):
    """追込: 後方で待機し、最後の一瞬にかける"""
    def calculate_step(self, current_dist: float, total_dist: float, base_speed: float) -> float:
        if current_dist < total_dist * 0.7:
            return base_speed * 0.90
        return base_speed * 0.95

    @property
    def spurt_multiplier(self) -> float:
        return 1.20