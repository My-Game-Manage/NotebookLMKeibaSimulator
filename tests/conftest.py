"""
6. テスト用モックとフィクスチャの設定 (conftest.py)

テストの再現性を担保するため、共通のフィクスチャを定義します。脚質名ではなく、実際の戦略クラスをインスタンス化して Horse に渡すことで、型安全なテストを実現します。
"""

from __future__ import annotations
import pytest
from src.models import Horse, Jockey, RaceConfig
from src.strategies import RunawayStrategy, ChaserStrategy

@pytest.fixture
def standard_race_config():
    """標準的な2000m、良馬場のレース設定"""
    return RaceConfig(
        distance=2000,
        weather="Sunny",
        track_condition="Good"
    )

@pytest.fixture
def runaway_horse():
    """標準的な『逃げ』馬のインスタンス"""
    return Horse(
        name="テストサイレンス",
        stamina=1000,
        speed=75,
        strategy=RunawayStrategy()
    )

@pytest.fixture
def chaser_horse():
    """標準的な『追込』馬のインスタンス"""
    return Horse(
        name="テストシップ",
        stamina=1200,
        speed=70,
        strategy=ChaserStrategy()
    )