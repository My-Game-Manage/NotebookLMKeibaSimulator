from __future__ import annotations
from dataclasses import dataclass, field

@dataclass(frozen=True)
class Jockey:
    """騎手データクラス"""
    name: str
    skill: float  # 0.0 ~ 1.0 (スタミナ効率に影響)

    def __post_init__(self):
        if not (0.0 <= self.skill <= 1.0):
            raise ValueError("Jockey skill must be between 0.0 and 1.0")

@dataclass
class Horse:
    """馬データクラス"""
    name: str
    max_speed: float  # 基本最高速度 (m/s)
    stamina: float    # 総スタミナ量
    jockey: Jockey

@dataclass(frozen=True)
class RaceConfig:
    """レース設定クラス"""
    distance: float = 1600.0
    weather: str = "Sunny"

    def __post_init__(self):
        if self.distance <= 0:
            raise ValueError("Race distance must be positive")

@dataclass(frozen=True)
class RaceState:
    """ステップごとの状態を通知するためのDTO"""
    name: str
    distance: float
    speed: float
    stamina: float
    is_finished: bool
    rank_order: int = 0