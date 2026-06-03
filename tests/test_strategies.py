"""
脚質ごとの移動ロジック（逃げ・追込）が設計通りに動くかを検証します
"""
from __future__ import annotations
import pytest
from src.models import Horse, Jockey
from src.strategies import RunawayStrategy, ChaserStrategy

@pytest.fixture
def setup_data():
    """テスト用の共通騎手データを生成"""
    jockey = Jockey("テスト", 1.0, 1.0)
    return jockey

def test_runaway_strategy_stamina_penalty(setup_data):
    """スタミナ切れ時に逃げ馬の速度が低下するか確認"""
    strategy = RunawayStrategy()
    
    # 1. スタミナが十分にある状態
    horse_ok = Horse("元気な逃げ馬", 50, 1000, strategy, setup_data)
    speed_ok = strategy.calculate_step(horse_ok, setup_data, 1600)
    
    # 2. スタミナが切れた状態 (current_staminaを0に設定)
    horse_tired = Horse("バテた逃げ馬", 50, 1000, strategy, setup_data)
    horse_tired.current_stamina = 0.0
    speed_tired = strategy.calculate_step(horse_tired, setup_data, 1600)
    
    # 検証: スタミナ切れの方が明らかに遅いこと
    assert speed_tired < speed_ok
    # ペナルティ倍率(0.6)が概ね適用されているか（ランダム誤差を考慮して0.5〜0.7の範囲か）
    assert 0.5 < (speed_tired / speed_ok) < 0.7

def test_chaser_strategy_stamina_penalty(setup_data):
    """スタミナ切れ時に追込馬のスパート速度が低下するか確認"""
    strategy = ChaserStrategy()
    
    # 後半(900m)でスパート中の元気な馬
    horse_ok = Horse("元気な追込馬", 50, 1000, strategy, setup_data)
    horse_ok.position = 900.0
    speed_ok = strategy.calculate_step(horse_ok, setup_data, 1600)
    
    # 後半(900m)でスタミナが切れた馬
    horse_tired = Horse("バテた追込馬", 50, 1000, strategy, setup_data)
    horse_tired.position = 900.0
    horse_tired.current_stamina = 0.0
    speed_tired = strategy.calculate_step(horse_tired, setup_data, 1600)
    
    # 検証
    assert speed_tired < speed_ok
    assert 0.5 < (speed_tired / speed_ok) < 0.7

def test_chaser_strategy_phases_with_stamina(setup_data):
    """スタミナがある状態で、追込馬が後半に加速することを確認"""
    strategy = ChaserStrategy()
    horse = Horse("追込馬", 50, 2000, strategy, setup_data)
    
    # 前半 (400m地点)
    horse.position = 400.0
    speed_first = strategy.calculate_step(horse, setup_data, 1600)
    
    # 後半 (1200m地点)
    horse.position = 1200.0
    speed_second = strategy.calculate_step(horse, setup_data, 1600)
    
    # 検証: 後半の方が速い（スパートがかかっている）
    assert speed_second > speed_first

def test_runaway_strategy_range(setup_data):
    """逃げ馬の移動速度が概ね期待される範囲(16.0m/s以上)にあるか確認"""
    strategy = RunawayStrategy()
    horse = Horse("逃げ", 50, 1000, strategy, setup_data)
    speed = strategy.calculate_step(horse, setup_data, 1600)
    
    # 基準速度16.0m/s付近であることを確認
    assert 15.0 < speed < 18.0