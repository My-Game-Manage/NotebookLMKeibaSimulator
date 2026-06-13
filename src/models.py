"""
データクラスのみを定義する安定した土台です。

- レース設定に論理的な時間単位（tick_time）を追加し、距離を float で扱えるようにします
- レース中の残りスタミナを管理する current_stamina プロパティを追加します
- 馬が現在スパート状態にあるかどうかを保持するフラグ is_spurting を追加します
- 「瞬発力（explosiveness）」を追加。このパラメータは、0〜100の範囲で馬の「終いの脚の鋭さ」を表現する数値として定義します
- acceleration を追加し、現在の速度を保持する current_speed フィールドを導入します
- Corner クラス を追加し、RaceConfig でそれらを保持できるように拡張
"""

from __future__ import annotations
from dataclasses import dataclass, field # field を追加
from typing import List, TYPE_CHECKING # List を追加

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
    explosiveness: int  # 新規追加：瞬発力（0〜100。スパート時の加速力に影響）
    acceleration: int  # 新規追加：加速力（0〜100）
    strategy: MoveStrategy
    jockey: Jockey
    position: float = 0.0
    current_stamina: float = 0.0 # レース開始時に stamina の値で初期化する
    current_speed: float = 0.0  # 新規追加：現在の速度（m/s）
    is_spurting: bool = False  # スパート中かどうかのフラグを追加

    def __post_init__(self):
        # インスタンス化の直後に現在のスタミナを最大値に設定
        self.current_stamina = float(self.stamina)
        # レース開始時は停止状態から始まる
        self.current_speed = 0.0

@dataclass
class Corner:
    """コースのコーナー区間を定義するデータクラス"""
    start_pos: float  # コーナー開始地点 (m)
    end_pos: float    # コーナー終了地点 (m)
    radius: float     # 曲率半径 (m)。数値が小さいほど急カーブとなる [2, 3]

@dataclass
class RaceConfig:
    """1600mレースと秒単位計算に対応した設定"""
    course_length: int = 1600  # 100mから1600mへ拡張 [3]
    tick_time: float = 0.1     # 1ステップあたりの論理時間（秒）
    interval: float = 0.01     # 実際の表示更新間隔（秒）
    # 決定論的なコース形状を定義するため、コーナーのリストを追加 [3]
    corners: List[Corner] = field(default_factory=list) 
