"""
脚質ごとの計算ロジックをカプセル化します

- calculate_step が「秒速 (m/s)」を返すように定義を変更します。サラブレッドの平均秒速（約16〜20m/s）を基準にします。
"""
from __future__ import annotations
import random
from typing import Protocol, TYPE_CHECKING, runtime_checkable

if TYPE_CHECKING:
    from .models import Horse, Jockey

@runtime_checkable
class MoveStrategy(Protocol):
    """移動戦略のインターフェース規約"""
    def calculate_step(self, horse: Horse, jockey: Jockey, course_length: int) -> float: ...

class RunawayStrategy:
    """【逃げ】秒速約17m前後で安定走行"""
    def calculate_step(self, horse: Horse, jockey: Jockey, course_length: int) -> float:
        # 1600mを約95秒で走るベース速度 (16.8 m/s)
        base_speed = 16.0 + (horse.speed / 100.0) * jockey.front_skill
        return base_speed * random.uniform(0.98, 1.02)

class ChaserStrategy:
    """【追い込み】後半に時速を上げる"""
    def calculate_step(self, horse: Horse, jockey: Jockey, course_length: int) -> float:
        is_latter_half = horse.position > (course_length / 2)
        # 前半は抑え(15m/s)、後半にスパート(19m/s)
        multiplier = 1.2 if is_latter_half else 0.9
        base_speed = 16.5 * multiplier * jockey.back_skill
        return base_speed * random.uniform(0.95, 1.05)
