"""
5. スタミナ消費およびスパート機能検証 (test_engine.py)

SimulationEngine の物理計算を検証します。現時点（v0.1.1）では step メソッドの実装が進行中であるため、本テストは TDD（テスト駆動開発）における Red 状態として機能します。
"""
from __future__ import annotations
import pytest
from src.models import Horse, Jockey
from src.engine import SimulationEngine
from src.strategies import RunawayStrategy

@pytest.fixture
def setup_engine():
    """テスト用のエンジン、馬、騎手のセットアップ"""
    jockey = Jockey(name="テスト騎手", front_skill=1.0, back_skill=1.0)
    # 速度100, スタミナ100の逃げ馬
    horse = Horse(
        name="テスト馬", 
        speed=100, 
        stamina=100, 
        strategy=RunawayStrategy(), 
        jockey=jockey
    )
    # 1600mのコース、0.1秒刻みの計算
    tick_time = 0.1
    engine = SimulationEngine(course_length=1600, horses=[horse], tick_time=tick_time)
    return engine, horse

def test_engine_initialization(setup_engine):
    """エンジンが正しく初期化されているか確認"""
    engine, horses = setup_engine
    assert engine.course_length == 1600
    assert engine.elapsed_time == 0.0
    assert len(engine.horses) == 1

def test_step_advances_time(setup_engine):
    """step()を実行するたびに経過時間が正しく増えるか確認"""
    engine, _ = setup_engine
    tick = engine.tick_time
    
    engine.step()
    assert engine.elapsed_time == pytest.approx(tick)
    
    engine.step()
    assert engine.elapsed_time == pytest.approx(tick * 2)

def test_step_updates_horse_position(setup_engine):
    """step()によって馬の位置が更新されるか確認"""
    engine, horse = setup_engine
    initial_pos = horse.position
    
    engine.step()
    
    # 位置が初期状態（0）より進んでいることを確認
    assert horse.position > initial_pos
    # v0.1.1の計算式: 逃げ馬(speed 100)は秒速 17.5m なので、0.1秒で 1.75m 進むはず
    assert horse.position == pytest.approx(1.75)

def test_winner_detection(setup_engine):
    """馬がゴールラインを越えたときに正しく勝者を返すか確認"""
    engine, horse = setup_engine
    
    # 馬をゴール直前（1599m地点）にワープさせる
    horse.position = 1599.0
    
    # まだゴールしていないので、戻り値は None のはず
    winner_before = engine.step()
    assert winner_before is None
    
    # 次のステップで 1.75m 進むので 1600.75m となりゴール
    winner_after = engine.step()
    
    assert winner_after is not None
    assert winner_after.name == "テスト馬"
    assert winner_after.position >= engine.course_length

def test_multiple_horses_winner(neutral_jockey):
    """複数の馬がいる場合、最初にゴールした馬が勝者になるか確認"""
    jockey = Jockey("騎手", 1.0, 1.0)
    # 速い馬と遅い馬を用意
    fast_horse = Horse("速い馬", 100, 500, RunawayStrategy(), jockey)
    slow_horse = Horse("遅い馬", 10, 500, RunawayStrategy(), jockey)
    
    # 既にゴールに近い状態にする
    fast_horse.position = 1590
    slow_horse.position = 1590
    
    engine = SimulationEngine(1600, [fast_horse, slow_horse], 0.1)
    
    # 数ステップ実行して勝者を判定
    winner = None
    for _ in range(10):
        winner = engine.step()
        if winner:
            break
            
    assert winner == fast_horse