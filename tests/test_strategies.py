"""
脚質ごとの移動ロジック（逃げ・追込）が設計通りに動くかを検証します
"""
from __future__ import annotations
import pytest
from src.models import Horse, Jockey
from src.strategies import RunawayStrategy, ChaserStrategy

@pytest.fixture
def setup_data():
    jockey = Jockey("テスト", 1.0, 1.0)
    return jockey

def test_runaway_strategy_range(setup_data):
    """逃げ馬の移動距離が規定の範囲内(80%-100%)か確認"""
    strategy = RunawayStrategy()
    horse = Horse("逃げ", 10, 100, strategy, setup_data)
    
    for _ in range(100):
        move = strategy.calculate_step(horse, setup_data, 100)
        # speed 10 * skill 1.0 = 10. 範囲は 8～10
        assert 8 <= move <= 10

def test_chaser_strategy_phases(setup_data):
    """追込馬が前半抑え、後半加速するか確認"""
    strategy = ChaserStrategy()
    horse = Horse("追込", 10, 100, strategy, setup_data)
    
    # 前半（位置0）
    horse.position = 0
    move_early = strategy.calculate_step(horse, setup_data, 100)
    assert move_early <= 5 # 10 * 0.5
    
    # 後半（位置60）
    horse.position = 60
    move_late = strategy.calculate_step(horse, setup_data, 100)
    assert move_late >= 10 # 10 * 1.0