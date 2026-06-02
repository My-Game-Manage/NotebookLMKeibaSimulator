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

def test_engine_winner_detection():
    jockey = Jockey("テスト", 1.0, 1.0)
    horse = Horse("馬", 10, 100, RunawayStrategy(), jockey)
    engine = SimulationEngine(100, [horse], 0.1)
    
    horse.position = 99
    winner = engine.step()
    assert winner is not None
    assert winner.name == "馬"