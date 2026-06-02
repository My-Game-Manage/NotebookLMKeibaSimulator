"""
データクラスのみを定義する安定した土台です。
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .strategies import MoveStrategy

@dataclass
class Jockey:
    """騎手の能力値を保持するデータクラス"""
    name: str
    front_skill: float
    back_skill: float

@dataclass
class Horse:
    """馬の属性と状態を管理するドメインモデル"""
    name: str
    speed: int
    stamina: int
    strategy: MoveStrategy
    jockey: Jockey
    position: int = 0

@dataclass
class RaceConfig:
    """レースの環境設定"""
    course_length: int = 100
    interval: float = 0.5