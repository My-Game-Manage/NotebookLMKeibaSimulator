"""
脚質ごとの計算ロジックをカプセル化します
"""
from __future__ import annotations
import random
from typing import Protocol, TYPE_CHECKING

if TYPE_CHECKING:
    from .models import Horse, Jockey

class MoveStrategy(Protocol):
    """移動戦略のインターフェース規約"""
    def calculate_step(self, horse: Horse, jockey: Jockey, course_length: int) -> int: ...

class RunawayStrategy:
    """【逃げ】常に安定して前を走る戦略"""
    def calculate_step(self, horse: Horse, jockey: Jockey, course_length: int) -> int:
        effective_speed = int(horse.speed * jockey.front_skill)
        return random.randint(int(effective_speed * 0.8), effective_speed)

class ChaserStrategy:
    """【追い込み】終盤に爆発力を発揮する戦略"""
    def calculate_step(self, horse: Horse, jockey: Jockey, course_length: int) -> int:
        effective_speed = int(horse.speed * jockey.back_skill)
        if horse.position < (course_length / 2):
            return random.randint(1, int(effective_speed * 0.5))
        else:
            return random.randint(effective_speed, int(effective_speed * 1.5))