"""
データクラスのみを定義する安定した土台です。

- レース設定に論理的な時間単位（tick_time）を追加し、距離を float で扱えるようにします
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
    """1600mレースと秒単位計算に対応した設定"""
    course_length: int = 1600  # 100mから1600mへ拡張 [3]
    tick_time: float = 0.1     # 1ステップあたりの論理時間（秒）
    interval: float = 0.01     # 実際の表示更新間隔（秒）