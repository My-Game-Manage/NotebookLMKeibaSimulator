"""
脚質ごとの計算ロジックをカプセル化します

- calculate_step が「秒速 (m/s)」を返すように定義を変更します。サラブレッドの平均秒速（約16〜20m/s）を基準にします。
- 脚質ごとの計算ロジック内で、horse.current_stamina が 0 になった場合に速度を低下させるペナルティを実装します
- 脚質ごとに、スパートを開始するかどうかの判定ロジックを実装します。ここでは、**「残りスタミナ ≧ 残り距離 × 消費係数」**となったタイミングをスパート開始点とします
- 「先行（Front-runner）」と「差し（Mid-packer）」の2つの脚質を実装
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
    """【逃げ】最初から飛ばすが、スタミナ配分を考え最後に再加速を試みる"""
    def calculate_step(self, horse: Horse, jockey: Jockey, course_length: int) -> float:
        remaining_dist = course_length - horse.position

        # 判定：スタミナに余裕があればスパート（逃げは早めに仕掛ける傾向）
        # 消費係数を1.0と仮定し、残り距離をカバーできるならスパート開始
        # スパート判定（逃げは少し早め）
        if not horse.is_spurting and horse.current_stamina > (remaining_dist * 0.7):
            horse.is_spurting = True
        
        # スパート倍率（50の時に1.03倍に抑制）
        spurt_multiplier = 0.98 + (horse.explosiveness / 1000.0)
        multiplier = spurt_multiplier if horse.is_spurting else 1.0
        
        # ベース速度を 17.5 -> 16.2 に引き下げ
        base_speed = (16.2 + (horse.speed / 100.0) * jockey.front_skill) * multiplier
        stamina_multiplier = 1.0 if horse.current_stamina > 0 else 0.6
        return base_speed * stamina_multiplier * random.uniform(0.99, 1.01)

class FrontRunnerStrategy:
    """【先行】逃げ馬の直後につけ、スタミナを温存しつつ早めに抜け出す"""
    def calculate_step(self, horse: Horse, jockey: Jockey, course_length: int) -> float:
        remaining_dist = course_length - horse.position
        
        # 判定：逃げよりは遅いが、差しよりは早く仕掛ける（係数 0.9）
        if not horse.is_spurting and horse.current_stamina > (remaining_dist * 0.9):
            horse.is_spurting = True

        # スパート倍率（50の時に1.08倍）
        spurt_multiplier = 1.03 + (horse.explosiveness / 1000.0)
        multiplier = spurt_multiplier if horse.is_spurting else 0.97 # 巡航を微減
        
        # ベース速度を 17.5 -> 16.2 に引き下げ
        base_speed = (16.2 + (horse.speed / 100.0) * jockey.front_skill) * multiplier
        stamina_multiplier = 1.0 if horse.current_stamina > 0 else 0.6
        return base_speed * stamina_multiplier * random.uniform(0.98, 1.02)

class MidPackerStrategy:
    """【差し】中団で待機し、追い込み馬よりも一足早くスパートを開始する"""
    def calculate_step(self, horse: Horse, jockey: Jockey, course_length: int) -> float:
        remaining_dist = course_length - horse.position
        
        # 判定：追い込み(1.3)よりは早めに、先行(0.9)よりは溜める（係数 1.1）
        if not horse.is_spurting and horse.current_stamina > (remaining_dist * 1.1):
            horse.is_spurting = True

        # スパート倍率（50の時に1.11倍）
        spurt_multiplier = 1.06 + (horse.explosiveness / 1000.0)
        multiplier = spurt_multiplier if horse.is_spurting else 0.93 # 巡航を抑える
        
        # ベース速度を 17.2 -> 16.0 に引き下げ
        base_speed = (16.0 + (horse.speed / 100.0) * jockey.back_skill) * multiplier
        stamina_multiplier = 1.0 if horse.current_stamina > 0 else 0.6
        return base_speed * stamina_multiplier * random.uniform(0.97, 1.03)

class ChaserStrategy:
    """【追い込み】道中は足を溜め、ゴールまで走りきれる計算が立ったら一気に加速する"""
    def calculate_step(self, horse: Horse, jockey: Jockey, course_length: int) -> float:
        remaining_dist = course_length - horse.position

        # 判定：追い込みはギリギリまで溜める（消費係数を1.2とし、確実なタイミングでスパート）
        # スパート判定：追い込みはギリギリまで溜める（スタミナが残り距離の1.3倍以上必要）
        if not horse.is_spurting and horse.current_stamina > (remaining_dist * 1.3):
            horse.is_spurting = True

        # スパート倍率（50の時に1.08倍、100の時に1.13倍）
        spurt_multiplier = 1.03 + (horse.explosiveness / 1000.0)
        multiplier = spurt_multiplier if horse.is_spurting else 0.88 
        
        # ベース速度を 17.2 -> 16.0 に引き下げ
        base_speed = (16.0 + (horse.speed / 100.0) * jockey.back_skill) * multiplier
        stamina_multiplier = 1.0 if horse.current_stamina > 0 else 0.6
        return base_speed * stamina_multiplier * random.uniform(0.97, 1.03)
