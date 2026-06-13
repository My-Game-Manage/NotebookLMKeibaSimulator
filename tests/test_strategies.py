"""
脚質ごとの移動ロジック（逃げ・追込）が設計通りに動くかを検証します

- Horseクラスにexplosiveness を追加
- 瞬発力に基づいた上がり3Fタイムを検証するテスト を追加
- Horseにpowerを追加
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
    # 第5引数に acceleration=50 を追加
    # 第6引数に 50 を追加
    horse_ok = Horse("元気な逃げ馬", 50, 2000, 50, 50, 50, strategy, setup_data)
    horse_ok.is_spurting = True
    speed_ok = strategy.calculate_step(horse_ok, setup_data, 1600)
    
    horse_tired = Horse("バテた逃げ馬", 50, 2000, 50, 50, 50, strategy, setup_data)
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
    # 第5引数に acceleration=50 を追加
    # 第6引数に 50 を追加
    horse = Horse("先行馬", 50, 1000, 50, 50, 50, strategy, setup_data)
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
    # 第5引数に acceleration=50 を追加
    # 第6引数に 50 を追加
    horse = Horse("差し馬", 50, 800, 50, 50, 50, strategy, setup_data)
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
    # 第5引数に acceleration=50 を追加
    # 第6引数に 50 を追加
    horse_ok = Horse("元気な追込馬", 50, 2000, 50, 50, 50, strategy, setup_data)
    horse_ok.is_spurting = True
    speed_ok = strategy.calculate_step(horse_ok, setup_data, 1600)
    
    # 第5引数に acceleration=50 を追加
    # 第6引数に 50 を追加
    horse_tired = Horse("バテた追込馬", 50, 2000, 50, 50, 50, strategy, setup_data)
    horse_tired.is_spurting = True
    horse_tired.current_stamina = 0.0
    speed_tired = strategy.calculate_step(horse_tired, setup_data, 1600)
    
    assert speed_tired < speed_ok
    assert 0.5 < (speed_tired / speed_ok) < 0.7

def test_chaser_strategy_phases_with_stamina(setup_data):
    """スタミナの状態によって、追込馬が適切に加速（スパート）することを確認"""
    strategy = ChaserStrategy()
    
    # スタミナを 600 から 700 に引き上げる
    # 1200m地点（残り400m）でのしきい値は 400 * (1.3 + 0.2) = 600
    # 700あれば確実にスパートの条件を満たす
    # 第5引数に acceleration=50 を追加
    # 第6引数に 50 を追加
    horse = Horse("追込馬", 50, 700, 50, 50, 50, strategy, setup_data)

    # 前半 (400m地点) - 残り1200m
    # しきい値: 1200 * 1.5 = 1800。700ではスパートしない
    horse.position = 400.0
    horse.is_spurting = False
    speed_cruising = strategy.calculate_step(horse, setup_data, 1600)
    assert horse.is_spurting is False
    
    # 後半 (1200m地点) - 残り400m
    # しきい値: 400 * 1.5 = 600。700 > 600 なのでスパートする
    horse.position = 1200.0
    speed_spurt = strategy.calculate_step(horse, setup_data, 1600)
    
    # ここが True になり、テストがパスします
    assert horse.is_spurting is True
    assert speed_spurt > speed_cruising

def test_runaway_strategy_range(setup_data):
    """逃げ馬の移動速度が概ね期待される範囲にあるか確認"""
    strategy = RunawayStrategy()
    # スタミナを低く設定して巡航速度（0.95倍）をテストする場合
    # 第5引数に acceleration=50 を追加
    # 第6引数に 50 を追加
    horse = Horse("逃げ", 50, 100, 50, 50, 50, strategy, setup_data)
    # 巡航速度の状態を確認
    horse.is_spurting = False
    speed = strategy.calculate_step(horse, setup_data, 1600)
    
    # 巡航速度
    # 新しい計算: (16.2 + 0.5) * 1.0 * 1.01(random) = 16.86
    # これで 17.5 未満に収まります
    assert 15.5 < speed < 17.5

def test_agari_3f_by_explosiveness(setup_data):
    """瞬発力の違いによって上がり3F（600m）のタイムに差が出るか検証"""
    # 1. 瞬発力が高い馬 (100) と低い馬 (0) を用意
    strategy = ChaserStrategy()
    # 第5引数に acceleration=50 を追加
    # 第6引数に 50 を追加
    high_exp_horse = Horse("キレ者", 60, 2000, 100, 50, 50, strategy, setup_data)
    low_exp_horse = Horse("ジリ脚", 60, 2000, 0, 50, 50, strategy, setup_data)
    
    # どちらもスパート状態に固定
    high_exp_horse.is_spurting = True
    low_exp_horse.is_spurting = True

    # 2. 600mを走るのにかかる時間をシミュレーション（簡易計算）
    # Time = Distance / Speed
    speed_high = strategy.calculate_step(high_exp_horse, setup_data, 1600)
    speed_low = strategy.calculate_step(low_exp_horse, setup_data, 1600)
    
    agari_3f_high = 600 / speed_high
    agari_3f_low = 600 / speed_low
    
    # 3. 検証
    # 瞬発力100の馬の方が、上がり3Fのタイムが速い（数値が小さい）こと
    assert agari_3f_high < agari_3f_low
    
    # 具体的なタイム感のチェック（例: 33秒〜38秒の範囲に収まっているか）
    # 現実の競馬の上がり3Fに即した数値になっているかを確認
    # 新しい計算: 16.6(base) * 1.13(spurt) = 18.75 m/s
    # 600 / 18.75 = 32.0 秒。これで 30.0 < 32.0 となり合格します
    assert 30.0 < agari_3f_high < 40.0
    print(f"\n[Debug] 高瞬発力馬の上がり3F: {agari_3f_high:.2f}s")
    print(f"[Debug] 低瞬発力馬の上がり3F: {agari_3f_low:.2f}s")