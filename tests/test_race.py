"""
レースの進行管理と Observer への通知が正しく機能するかを検証します
"""
from __future__ import annotations
import pytest
from src.models import Horse, Jockey, RaceConfig
from src.strategies import RunawayStrategy
from src.race import Race

class MockObserver:
    """テスト用のダミーObserver"""
    def __init__(self):
        self.started = False
        self.finished = False
    def on_race_start(self, horses): self.started = True
    def on_step_executed(self, horses, elapsed_time): pass
    def on_race_finished(self, winner, elapsed_time): self.finished = True

def test_race_lifecycle():
    config = RaceConfig(course_length=10, interval=0.01)
    jockey = Jockey("テスト", 1.0, 1.0)
    horse = Horse("馬", 100, 100, RunawayStrategy(), jockey) # すぐゴールする設定
    
    race = Race(config, [horse])
    observer = MockObserver()
    race.attach(observer)
    
    race.start()
    
    assert observer.started is True
    assert observer.finished is True
    assert race.winner is not None