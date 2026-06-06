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
    """【逃げ】巡航から速いが、スパートの伸びは控えめ"""
    def calculate_step(self, horse: Horse, jockey: Jockey, course_length: int) -> float:
        remaining_dist = course_length - horse.position
        
        # 騎手スキルによるスパート判断の固定調整
        # スキル1.2なら基準の0.7倍地点。スキルが低いほど早仕掛け（残り距離があるうちに開始）になる
        skill_bonus = 1.2 - jockey.front_skill
        spurt_threshold = remaining_dist * (0.7 + skill_bonus)

        if not horse.is_spurting and horse.current_stamina > spurt_threshold:
            horse.is_spurting = True

        spurt_multiplier = 0.98 + (horse.explosiveness / 1000.0)
        multiplier = spurt_multiplier if horse.is_spurting else 1.0
        
        base_speed = (16.2 + (horse.speed / 100.0) * jockey.front_skill) * multiplier
        stamina_multiplier = 1.0 if horse.current_stamina > 0 else 0.6
        return base_speed * stamina_multiplier

class FrontRunnerStrategy:
    """【先行】バランス重視。スキルが高いほど理想的なスパート地点を維持"""
    def calculate_step(self, horse: Horse, jockey: Jockey, course_length: int) -> float:
        remaining_dist = course_length - horse.position
        skill_bonus = 1.2 - jockey.front_skill
        spurt_threshold = remaining_dist * (0.9 + skill_bonus)

        if not horse.is_spurting and horse.current_stamina > spurt_threshold:
            horse.is_spurting = True

        spurt_multiplier = 1.03 + (horse.explosiveness / 1000.0)
        multiplier = spurt_multiplier if horse.is_spurting else 0.97
        
        base_speed = (16.2 + (horse.speed / 100.0) * jockey.front_skill) * multiplier
        return base_speed * (1.0 if horse.current_stamina > 0 else 0.6)

class MidPackerStrategy:
    """【差し】後半の鋭さを騎手スキルで制御"""
    def calculate_step(self, horse: Horse, jockey: Jockey, course_length: int) -> float:
        remaining_dist = course_length - horse.position
        skill_bonus = 1.2 - jockey.back_skill
        spurt_threshold = remaining_dist * (1.1 + skill_bonus)

        if not horse.is_spurting and horse.current_stamina > spurt_threshold:
            horse.is_spurting = True

        spurt_multiplier = 1.06 + (horse.explosiveness / 1000.0)
        multiplier = spurt_multiplier if horse.is_spurting else 0.93
        
        base_speed = (16.0 + (horse.speed / 100.0) * jockey.back_skill) * multiplier
        return base_speed * (1.0 if horse.current_stamina > 0 else 0.6)

class ChaserStrategy:
    """【追い込み】名手ほどギリギリまでスパートを我慢し、鋭い脚を温存する"""
    def calculate_step(self, horse: Horse, jockey: Jockey, course_length: int) -> float:
        remaining_dist = course_length - horse.position
        skill_bonus = 1.2 - jockey.back_skill
        spurt_threshold = remaining_dist * (1.3 + skill_bonus)

        if not horse.is_spurting and horse.current_stamina > spurt_threshold:
            horse.is_spurting = True

        spurt_multiplier = 1.03 + (horse.explosiveness / 1000.0)
        multiplier = spurt_multiplier if horse.is_spurting else 0.88 
        
        base_speed = (16.0 + (horse.speed / 100.0) * jockey.back_skill) * multiplier
        return base_speed * (1.0 if horse.current_stamina > 0 else 0.6)