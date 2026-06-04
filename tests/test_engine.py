"""
物理計算エンジンが正しく馬を進め、ゴール判定を行うかを検証します
"""
from __future__ import annotations
import pytest
from src.models import Horse, Jockey
from src.engine import SimulationEngine
from src.strategies import RunawayStrategy

def test_engine_step_advances_horse():
    jockey = Jockey("テスト", 1.0, 1.0)
    horse = Horse("馬", 10, 100, RunawayStrategy(), jockey)
    engine = SimulationEngine(100, [horse], 0.1)
    
    initial_pos = horse.position
    engine.step()
    assert horse.position > initial_pos

def test_engine_rankings_order():
    jockey = Jockey("テスト", 1.0, 1.0)
    # 足の速い馬と遅い馬を用意
    fast_horse = Horse("速い馬", 100, 100, RunawayStrategy(), jockey)
    slow_horse = Horse("遅い馬", 10, 100, RunawayStrategy(), jockey)
    
    engine = SimulationEngine(100, [fast_horse, slow_horse], 0.1)
    
    # 全馬がゴールするまで進める
    while not engine.is_all_finished():
        engine.step()
    
    # 検証: 2頭ともランキングに入っているか
    assert len(engine.rankings) == 2
    # 検証: 速い馬が1位（インデックス0）か
    assert engine.rankings[0].name == "速い馬"
    assert engine.rankings[1].name == "遅い馬"