"""
4. 脚質ロジック検証 (test_strategies.py)

全ての脚質が、それぞれの特性（序盤の加速、終盤の伸び）を正しく計算できているかを検証します。ここでは、単なる型のチェックではなく、脚質間の相対的な性能差をアサーションの対象とします。
"""

from __future__ import annotations
import pytest
from src.strategies import (
    RunawayStrategy, LeadingStrategy, MidPackStrategy, ChaserStrategy
)

class TestStrategies:
    """脚質別ロジックの相対的な妥当性を検証する"""

    @pytest.mark.parametrize("phase, dist_traveled", [
        ("Early", 100),   # レース序盤 (100m地点)
        ("Middle", 1000), # 中盤 (1000m地点)
        ("Final", 1800),  # 終盤 (1800m地点)
    ])
    def test_strategy_relative_speeds(self, phase: str, dist_traveled: float):
        """各脚質のフェーズごとの速度差がドメイン知識と整合しているか検証"""
        total_dist = 2000.0
        
        runaway = RunawayStrategy().calculate_step(dist_traveled, total_dist)
        leading = LeadingStrategy().calculate_step(dist_traveled, total_dist)
        betwixt = MidPackStrategy().calculate_step(dist_traveled, total_dist)
        chaser = ChaserStrategy().calculate_step(dist_traveled, total_dist)

        if phase == "Early":
            # 序盤は「逃げ」が最も速く、「追込」が最も遅い
            assert runaway > leading > betwixt > chaser
        elif phase == "Final":
            # 終盤は「追込」や「差し」の計算値が伸びる設計であることを確認
            assert chaser > betwixt > leading