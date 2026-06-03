"""
レースの進行管理と Observer への通知が正しく機能するかを検証します
"""
from __future__ import annotations
import pytest
from src.models import Horse, Jockey, RaceConfig
from src.strategies import RunawayStrategy
from src.race import Race

class MockObserver:
    """テスト用のダミーObserver（修正版）"""
    def __init__(self):
        self.started = False
        self.finished = False
        self.final_rankings = []

    def on_race_start(self, horses):
        self.started = True

    def on_step_executed(self, horses, elapsed_time):
        pass

    def on_race_finished(self, rankings, elapsed_time):
        """引数を winner から rankings (List) に変更"""
        self.finished = True
        self.final_rankings = rankings

def test_race_lifecycle_with_rankings():
    config = RaceConfig(course_length=10, interval=0.01)
    jockey = Jockey("テスト", 1.0, 1.0)
    horses = [Horse("馬1", 100, 100, RunawayStrategy(), jockey)]
    
    race = Race(config, horses)
    observer = MockObserver()
    race.attach(observer)
    
    race.run()
    
    assert observer.finished is True
    # 渡されたランキングがリストであることを確認
    assert isinstance(observer.final_rankings, list)
    assert len(observer.final_rankings) == 1