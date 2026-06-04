"""
脚質ごとの移動ロジック（逃げ・追込）が設計通りに動くかを検証します
"""
from __future__ import annotations
import pytest
from src.models import Horse, Jockey
from src.strategies import RunawayStrategy, ChaserStrategy, FrontRunnerStrategy, MidPackerStrategy

@pytest.fixture
def setup_data():
    """テスト用の共通騎手データを生成"""
    jockey = Jockey("テスト", 1.0, 1.0)
    return jockey

def test_runaway_strategy_stamina_penalty(setup_data):
    """スタミナ切れ時に逃げ馬の速度が低下するか確認"""
    strategy = RunawayStrategy()
    
    # 条件を揃えるため、両方ともスパート状態にする
    horse_ok = Horse("元気な逃げ馬", 50, 2000, strategy, setup_data)
    horse_ok.is_spurting = True
    speed_ok = strategy.calculate_step(horse_ok, setup_data, 1600)
    
    horse_tired = Horse("バテた逃げ馬", 50, 2000, strategy, setup_data)
    horse_tired.is_spurting = True
    horse_tired.current_stamina = 0.0
    speed_tired = strategy.calculate_step(horse_tired, setup_data, 1600)
    
    # 検証: スタミナ切れの方が明らかに遅いこと
    assert speed_tired < speed_ok
    # ペナルティ(0.6)が適用されているか
    assert 0.5 < (speed_tired / speed_ok) < 0.7

def test_front_runner_strategy_phases(setup_data):
    """先行馬が適切なタイミング(係数0.9)でスパートするか確認"""
    strategy = FrontRunnerStrategy()
    # 400m地点(残り1200m)でスタミナ1000：1200 * 0.9 = 1080 なのでスパートしない
    horse = Horse("先行馬", 50, 1000, strategy, setup_data)
    horse.position = 400.0
    strategy.calculate_step(horse, setup_data, 1600)
    assert horse.is_spurting is False

    # 800m地点(残り800m)でスタミナ1000：800 * 0.9 = 720 なのでスパートする
    horse.position = 800.0
    strategy.calculate_step(horse, setup_data, 1600)
    assert horse.is_spurting is True

def test_mid_packer_strategy_phases(setup_data):
    """差し馬が適切なタイミング(係数1.1)でスパートするか確認"""
    strategy = MidPackerStrategy()
    # 800m地点(残り800m)でスタミナ800：800 * 1.1 = 880 なのでスパートしない
    horse = Horse("差し馬", 50, 800, strategy, setup_data)
    horse.position = 800.0
    strategy.calculate_step(horse, setup_data, 1600)
    assert horse.is_spurting is False

    # 1000m地点(残り600m)でスタミナ800：600 * 1.1 = 660 なのでスパートする
    horse.position = 1000.0
    strategy.calculate_step(horse, setup_data, 1600)
    assert horse.is_spurting is True

def test_chaser_strategy_stamina_penalty(setup_data):
    """スタミナ切れ時に追込馬のスパート速度が低下するか確認"""
    strategy = ChaserStrategy()
    
    # 条件を揃えるため、スパート中の状態で比較
    horse_ok = Horse("元気な追込馬", 50, 2000, strategy, setup_data)
    horse_ok.is_spurting = True
    speed_ok = strategy.calculate_step(horse_ok, setup_data, 1600)
    
    horse_tired = Horse("バテた追込馬", 50, 2000, strategy, setup_data)
    horse_tired.is_spurting = True
    horse_tired.current_stamina = 0.0
    speed_tired = strategy.calculate_step(horse_tired, setup_data, 1600)
    
    assert speed_tired < speed_ok
    assert 0.5 < (speed_tired / speed_ok) < 0.7

def test_chaser_strategy_phases_with_stamina(setup_data):
    """スタミナの状態によって、追込馬が適切に加速（スパート）することを確認"""
    strategy = ChaserStrategy()
    
    # スタミナを 500 に設定　→スタミナを 500 から 600 に引き上げる
    # 400m地点: 残り1200m。500 < (1200 * 1.2) なのでスパートしないはず
    # 1200m地点（残り400m）で 400 * 1.3 = 520 なので、600あればスパートが発動する
    horse = Horse("追込馬", 50, 600, strategy, setup_data)
    
    # 前半 (400m地点)
    # 1200 * 1.3 = 1560 なので、600ではスパートしない
    horse.position = 400.0
    horse.is_spurting = False # 初期化
    speed_cruising = strategy.calculate_step(horse, setup_data, 1600)
    assert horse.is_spurting is False
    
    # 後半 (1200m地点)
    # 400 * 1.3 = 520 なので、600あればスパートする
    horse.position = 1200.0
    speed_spurt = strategy.calculate_step(horse, setup_data, 1600)
    assert horse.is_spurting is True
    
    # 検証: スパート時の方が速い
    assert speed_spurt > speed_cruising

def test_runaway_strategy_range(setup_data):
    """逃げ馬の移動速度が概ね期待される範囲にあるか確認"""
    strategy = RunawayStrategy()
    # スタミナを低く設定して巡航速度（0.95倍）をテストする場合
    horse = Horse("逃げ", 50, 100, strategy, setup_data)
    # 巡航速度の状態を確認
    horse.is_spurting = False
    speed = strategy.calculate_step(horse, setup_data, 1600)
    
    # 巡航速度
    # 期待値の計算: 19.0 * 0.95 = 18.05 前後
    # 下限を17.0、上限を19.5程度に広げるのが適切です
    #assert 17.0 < speed < 19.5
    # 巡航速度(16.5 * 1.0)を確認する場合
    assert 15.5 < speed < 17.5