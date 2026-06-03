"""
脚質ごとの計算ロジックをカプセル化します

- calculate_step が「秒速 (m/s)」を返すように定義を変更します。サラブレッドの平均秒速（約16〜20m/s）を基準にします。
- 脚質ごとの計算ロジック内で、horse.current_stamina が 0 になった場合に速度を低下させるペナルティを実装します
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
    """【逃げ】スタミナがある限り飛ばすが、切れると失速する"""
    def calculate_step(self, horse: Horse, jockey: Jockey, course_length: int) -> float:
        # ベース速度の計算
        base_speed = 16.0 + (horse.speed / 100.0) * jockey.front_skill
        
        # スタミナ切れペナルティ（スタミナ0なら速度60%に低下）
        stamina_multiplier = 1.0 if horse.current_stamina > 0 else 0.6
        
        return base_speed * stamina_multiplier * random.uniform(0.98, 1.02)

class ChaserStrategy:
    """【追い込み】後半にスパートするが、スパートでスタミナを激しく消費する"""
    def calculate_step(self, horse: Horse, jockey: Jockey, course_length: int) -> float:
        is_latter_half = horse.position > (course_length / 2)
        multiplier = 1.2 if is_latter_half else 0.9
        
        base_speed = 16.5 * multiplier * jockey.back_skill
        
        # スタミナ切れペナルティ
        stamina_multiplier = 1.0 if horse.current_stamina > 0 else 0.6
        
        return base_speed * stamina_multiplier * random.uniform(0.95, 1.05)
