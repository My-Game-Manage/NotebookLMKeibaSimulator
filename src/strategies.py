"""
脚質ごとの計算ロジックをカプセル化します

- calculate_step が「秒速 (m/s)」を返すように定義を変更します。サラブレッドの平均秒速（約16〜20m/s）を基準にします。
- 脚質ごとの計算ロジック内で、horse.current_stamina が 0 になった場合に速度を低下させるペナルティを実装します
- 脚質ごとに、スパートを開始するかどうかの判定ロジックを実装します。ここでは、**「残りスタミナ ≧ 残り距離 × 消費係数」**となったタイミングをスパート開始点とします
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
        
        # ベース速度の計算
        # 巡航時は少し抑え、スパート時に本来の能力を出す設定
        # 巡航時も 1.0倍（減速させない）とし、スパートで 1.1倍に加速
        # ベース速度を 16.5 前後に設定
        speed_rate = 1.1 if horse.is_spurting else 1.0
        base_speed = (16.5 + (horse.speed / 100.0) * jockey.front_skill) * speed_rate
        
        # スタミナ切れペナルティ（スタミナ0なら速度60%に低下）
        stamina_multiplier = 1.0 if horse.current_stamina > 0 else 0.6
        
        return base_speed * stamina_multiplier * random.uniform(0.99, 1.01)

class ChaserStrategy:
    """【追い込み】道中は足を溜め、ゴールまで走りきれる計算が立ったら一気に加速する"""
    def calculate_step(self, horse: Horse, jockey: Jockey, course_length: int) -> float:
        remaining_dist = course_length - horse.position

        # 判定：追い込みはギリギリまで溜める（消費係数を1.2とし、確実なタイミングでスパート）
        # スパート判定：追い込みはギリギリまで溜める（スタミナが残り距離の1.3倍以上必要）
        if not horse.is_spurting and horse.current_stamina > (remaining_dist * 1.3):
            horse.is_spurting = True

        # 倍率の設定：
        # 巡航時は 0.85倍まで抑え、スパートで 1.3倍まで一気に上げる
        # ベース速度は逃げよりわずかに低めの 16.0
        multiplier = 1.3 if horse.is_spurting else 0.85
        base_speed = 16.0 * multiplier * jockey.back_skill

        # スタミナ切れペナルティ
        stamina_multiplier = 1.0 if horse.current_stamina > 0 else 0.6
        
        return base_speed * stamina_multiplier * random.uniform(0.97, 1.03)
