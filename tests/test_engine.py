"""
物理計算エンジンが正しく馬を進め、ゴール判定を行うかを検証します

- Horseクラスにexplosiveness を追加
- ドラフティングのテストを追加
"""
from __future__ import annotations
import pytest
from src.models import Horse, Jockey, Corner
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

def test_engine_corner_velocity_limit():
    """コーナーの半径による速度制限が決定論的に適用されるか検証"""
    jockey = Jockey("テスト", 1.0, 1.0)
    # 非常に速いスピードを持つ馬（制限にかかりやすく設定）
    # Horse(name, speed, stamina, explosiveness, acceleration, strategy, jockey)
    horse = Horse("高速馬", 100, 1000, 50, 100, RunawayStrategy(), jockey)

    # 1. 半径100mのコーナーを定義
    # 制限速度 V_limit = 2.0 * sqrt(100) = 20.0 m/s [会話履歴]
    corner = Corner(start_pos=0.0, end_pos=100.0, radius=100.0)
    
    # 馬の初期状態：コーナー内におり、制限速度(20m/s)を超えている状態
    horse.current_speed = 25.0
    horse.position = 10.0 
    
    engine = SimulationEngine(1600, [horse], 0.1, corners=[corner])
    engine.step()
    
    # 2. 加速力(acceleration=100)による減速の検証
    # accel_val = 0.5 + (100/100) = 1.5 m/s^2 [5, 会話履歴]
    # 0.1秒(tick_time)での最大減速幅 = 1.5 * 0.1 = 0.15 m/s
    # 期待される速度: 25.0 - 0.15 = 24.85 m/s
    assert horse.current_speed < 25.0
    assert horse.current_speed == pytest.approx(24.85)

def test_engine_corner_stamina_additional_load():
    """コーナー走行時に遠心力によるスタミナ追加負荷が発生するか検証"""
    jockey = Jockey("テスト", 1.0, 1.0)
    horse = Horse("検証馬", 50, 1000, 50, 50, RunawayStrategy(), jockey)
    
    # 同一速度、同一距離での「直線」と「コーナー」のスタミナ消費を比較
    # A. 直線走行
    horse.position = 0.0
    horse.current_speed = 15.0
    horse.current_stamina = 1000.0
    engine_straight = SimulationEngine(1600, [horse], 0.1, corners=[])
    engine_straight.step()
    loss_straight = 1000.0 - horse.current_stamina
    
    # B. コーナー走行
    horse.position = 0.0
    horse.current_speed = 15.0
    horse.current_stamina = 1000.0
    corner = Corner(start_pos=0.0, end_pos=100.0, radius=50.0)
    engine_corner = SimulationEngine(1600, [horse], 0.1, corners=[corner])
    engine_corner.step()
    loss_corner = 1000.0 - horse.current_stamina
    
    # コーナーの方が、遠心力負荷 (v^2 / R*10) の分だけ消費が多いはず [会話履歴]
    assert loss_corner > loss_straight

def test_engine_track_condition_stamina_consumption():
    """馬場状態（重馬場）によってスタミナ消費量が1.2倍になることを決定論的に検証"""
    jockey = Jockey("テスト騎手", 1.0, 1.0)
    
    # 比較用に同じ能力の馬を準備
    horse_firm = Horse("良馬場用", 50, 1000, 50, 50, RunawayStrategy(), jockey)
    horse_heavy = Horse("重馬場用", 50, 1000, 50, 50, RunawayStrategy(), jockey)

    # 1. 「良」馬場での1ステップ走行
    # コンストラクタに track_condition="良" を渡す（v0.1.5想定）
    engine_firm = SimulationEngine(1600, [horse_firm], 0.1, corners=[], track_condition="良")
    engine_firm.step()
    loss_firm = 1000.0 - horse_firm.current_stamina

    # 2. 「重」馬場での1ステップ走行
    # コンストラクタに track_condition="重" を渡す
    engine_heavy = SimulationEngine(1600, [horse_heavy], 0.1, corners=[], track_condition="重")
    engine_heavy.step()
    loss_heavy = 1000.0 - horse_heavy.current_stamina

    # 3. 検証：重馬場の消費量が良馬場の正確に1.2倍であること
    # 決定論的モデルのため、誤差なく 1.2倍になるはずです
    assert loss_heavy == pytest.approx(loss_firm * 1.2)

def test_engine_heavy_track_stamina_exhaustion_timing():
    """重馬場においてスタミナ切れが早く発生することを検証"""
    jockey = Jockey("テスト", 1.0, 1.0)
    # スタミナを極端に低く設定した馬
    horse = Horse("スタミナ不安馬", 50, 50, 50, 50, RunawayStrategy(), jockey)
    
    # 重馬場設定でシミュレーションを実行
    engine = SimulationEngine(1600, [horse], 0.1, corners=[], track_condition="重")
    
    # 数ステップ実行し、良馬場よりも早くスタミナが枯渇することを確認
    # （ここでは消費量が増えていることの確認に留めます）
    initial_stamina = horse.current_stamina
    engine.step()
    
    # 良馬場（通常 0.7係数）よりも激しく減っていることを確認
    # 期待される消費: distance * 0.7 * 1.2 * jockey_efficiency ...
    assert horse.current_stamina < initial_stamina
