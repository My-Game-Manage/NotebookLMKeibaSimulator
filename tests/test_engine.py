"""
物理計算エンジンが正しく馬を進め、ゴール判定を行うかを検証します

- Horseクラスにexplosiveness を追加
- ドラフティングのテストを追加
"""
from __future__ import annotations
import pytest
from src.models import Horse, Jockey
from src.engine import SimulationEngine
from src.strategies import RunawayStrategy

def test_engine_step_advances_horse():
    jockey = Jockey("テスト", 1.0, 1.0)
    # 第5引数に 50 を追加
    horse = Horse("馬", 10, 100, 50, 50, RunawayStrategy(), jockey)
    engine = SimulationEngine(100, [horse], 0.1)
    # 最初のステップでは 0m/s から加速するため、移動距離は以前より短くなることに注意
    engine.step()
    assert horse.position > 0

def test_engine_rankings_order():
    jockey = Jockey("テスト", 1.0, 1.0)
    # 足の速い馬と遅い馬を用意
    # 全ての馬の生成に第5引数 50 を追加
    fast_horse = Horse("速い馬", 100, 100, 50, 50, RunawayStrategy(), jockey)
    slow_horse = Horse("遅い馬", 10, 100, 50, 50, RunawayStrategy(), jockey)
    
    engine = SimulationEngine(100, [fast_horse, slow_horse], 0.1)
    
    # 全馬がゴールするまで進める
    while not engine.is_all_finished():
        engine.step()
    
    # 検証: 2頭ともランキングに入っているか
    assert len(engine.rankings) == 2
    # 検証: 速い馬が1位（インデックス0）か
    assert engine.rankings[0].name == "速い馬"
    assert engine.rankings[1].name == "遅い馬"

def test_engine_drafting_effect():
    """ドラフティング圏内（5m以内）にいる馬のスタミナ消費が軽減されるか検証"""
    jockey = Jockey("テスト騎手", 1.0, 1.0)
    # 同じ能力の馬を2頭用意
    # 全ての馬の生成に第5引数 50 を追加
    leader = Horse("先頭馬", 50, 1000, 50, 50, RunawayStrategy(), jockey)
    drafter = Horse("追走馬", 50, 1000, 50, 50, RunawayStrategy(), jockey)
    
    # 初期位置を設定（差を3.0mにし、ドラフティング圏内に入れる）
    leader.position = 10.0
    drafter.position = 7.0
    
    engine = SimulationEngine(1600, [leader, drafter], 0.1)
    
    # 1ステップ実行前のスタミナ（初期値1000）
    engine.step()
    
    # 消費したスタミナを算出
    loss_leader = 1000.0 - leader.current_stamina
    loss_drafter = 1000.0 - drafter.current_stamina
    
    # 検証1: ドラフターの方がスタミナ消費が少ないこと
    assert loss_drafter < loss_leader
    
    # 検証2: 軽減率が正確に 0.9倍（10%軽減）であること
    # 決定論的モデルなので、浮動小数点の近似（pytest.approx）で完全に一致するはずです
    assert loss_drafter == pytest.approx(loss_leader * 0.9)

def test_engine_no_drafting_outside_range():
    """5mより離れている場合はドラフティング効果が発生しないことを検証"""
    jockey = Jockey("テスト", 1.0, 1.0)
    # 全ての馬の生成に第5引数 50 を追加
    leader = Horse("先頭馬", 50, 1000, 50, 50, RunawayStrategy(), jockey)
    far_horse = Horse("離れた馬", 50, 1000, 50, 50, RunawayStrategy(), jockey)
    
    # 距離を 6.0m に設定（圏外）
    leader.position = 10.0
    far_horse.position = 4.0
    
    engine = SimulationEngine(1600, [leader, far_horse], 0.1)
    engine.step()
    
    loss_leader = 1000.0 - leader.current_stamina
    loss_far = 1000.0 - far_horse.current_stamina
    
    # 圏外なので、先頭馬と同じ量だけスタミナを消費するはず
    assert loss_far == pytest.approx(loss_leader)