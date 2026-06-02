"""
データ構造が正しく定義され、初期化できるかを検証します
"""
from __future__ import annotations
import pytest
from src.models import Jockey, Horse, RaceConfig
from src.strategies import RunawayStrategy

def test_jockey_creation():
    jockey = Jockey("武豊", 1.2, 1.0)
    assert jockey.name == "武豊"
    assert jockey.front_skill == 1.2

def test_horse_creation():
    jockey = Jockey("テスト", 1.0, 1.0)
    strategy = RunawayStrategy()
    horse = Horse("テスト馬", 10, 100, strategy, jockey)
    assert horse.name == "テスト馬"
    assert horse.position == 0

def test_race_config_defaults():
    config = RaceConfig()
    assert config.course_length == 100
    assert config.interval == 0.5