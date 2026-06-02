from dataclasses import dataclass
import random
import time
from typing import List, Optional, Protocol

# ==========================================
# 1. データ構造の定義 (データクラス)
# ==========================================

@dataclass
class Jockey:
    name: str
    front_skill: float
    back_skill: float


@dataclass
class Horse:
    name: str
    speed: int        # 【新規】最高速度（歩幅のベース）
    stamina: int      # 【新規】持久力（後半の粘り強さ。今回は 1〜100 のイメージ）
    strategy: 'MoveStrategy'
    jockey: Jockey
    position: int = 0


@dataclass
class RaceConfig:
    course_length: int = 100
    interval: float = 0.5


# ==========================================
# 2. Strategy（作戦・脚質）の定義
# ==========================================

class MoveStrategy(Protocol):
    """馬の移動戦略インターフェース。位置情報とコース長を引数に追加"""
    def calculate_step(self, horse: Horse, jockey: Jockey, course_length: int) -> int: ...


class RunawayStrategy:
    """【逃げ】常に安定して前を走る戦略"""
    def calculate_step(self, horse: Horse, jockey: Jockey, course_length: int) -> int:
        # 騎手補正を加味した実質スピード
        effective_speed = int(horse.speed * jockey.front_skill)
        
        # --- 最低限のスタミナ計算ロジック ---
        # レース後半（50%経過）かつ、馬のスタミナがコース長より低い（スタミナ不足）場合、スピード半減
        if horse.position > (course_length / 2) and horse.stamina < 50:
            effective_speed = max(1, int(effective_speed * 0.5))
            
        min_step = max(1, int(effective_speed * 0.5))
        return random.randint(min_step, effective_speed)


class ChaserStrategy:
    """【追い込み】一発逆転がある爆発型戦略"""
    def calculate_step(self, horse: Horse, jockey: Jockey, course_length: int) -> int:
        # 騎手補正を加味した実質スピード
        effective_speed = int(horse.speed * jockey.back_skill)
        
        # --- 最低限のスタミナ計算ロジック ---
        if horse.position > (course_length / 2) and horse.stamina < 50:
            effective_speed = max(1, int(effective_speed * 0.5))
            
        max_step = int(effective_speed * 1.4)
        return random.randint(1, max_step)


# ==========================================
# 3. シミュレーション実行エンジン
# ==========================================

class SimulationEngine:
    def __init__(self, course_length: int, horses: List[Horse]):
        self.course_length = course_length
        self.horses = horses

    def step(self) -> Optional[Horse]:
        winner = None
        for horse in self.horses:
            # ★リファクタリングのポイント:
            # 引数に horse 自身と course_length を渡すことで、Strategy側でスタミナ計算が可能に
            step_distance = horse.strategy.calculate_step(horse, horse.jockey, self.course_length)
            horse.position += step_distance
            
            if horse.position >= self.course_length and winner is None:
                winner = horse
        return winner


# ==========================================
# 4. レース管理（Subject）＆ Observer ＆ 表示処理
# ==========================================
# ※前回のコードと同じため、Race / RaceObserver / ConsoleView の定義は省略（裏で同様に動作）
class RaceObserver(Protocol):
    def on_race_start(self, horses: List[Horse]) -> None: ...
    def on_step_executed(self, horses: List[Horse]) -> None: ...
    def on_race_finished(self, winner: Horse) -> None: ...

class Race:
    def __init__(self, config: RaceConfig, horses: List[Horse]):
        self.config = config
        self.horses = horses
        self.engine = SimulationEngine(config.course_length, horses)
        self.winner: Optional[Horse] = None
        self._observers: List[RaceObserver] = []
    def attach(self, observer: RaceObserver): self._observers.append(observer)
    def start(self):
        for o in self._observers: o.on_race_start(self.horses)
        while self.winner is None:
            p_winner = self.engine.step()
            for o in self._observers: o.on_step_executed(self.horses)
            if p_winner: self.winner = p_winner
            else: time.sleep(self.config.interval)
        for o in self._observers: o.on_race_finished(self.winner)

class ConsoleView:
    def on_race_start(self, horses: List[Horse]):
        print("--- レース開始 ---")
        self._print_status(horses)
    def on_step_executed(self, horses: List[Horse]): self._print_status(horses)
    def on_race_finished(self, winner: Horse):
        print(f"\n--- レース終了 ---\n🏆 勝者: {winner.name} 🏆 (騎手: {winner.jockey.name})")
    def _print_status(self, horses: List[Horse]):
        print("\n現在の状況:")
        for horse in horses:
            visual_path = "-" * (horse.position // 5)
            strategy_name = "逃げ" if isinstance(horse.strategy, RunawayStrategy) else "追込"
            # 表示にスタミナ状態を少し匂わせる（50未満で後半ならバテマークを表示するなどアレンジも可能）
            status_tag = "（バテ）" if horse.position > 50 and horse.stamina < 50 else ""
            print(f"{horse.name}{status_tag} ({horse.jockey.name}騎手) [{strategy_name}]: {visual_path}▶ ({horse.position}m)")

# ==========================================
# 5. メイン処理
# ==========================================
if __name__ == "__main__":
    # コース長 100
    config = RaceConfig(course_length=100, interval=0.5)
    
    jockey_a = Jockey(name="ルメール", front_skill=1.1, back_skill=1.2)
    jockey_b = Jockey(name="武豊", front_skill=1.2, back_skill=1.0)
    
    entry_horses = [
        # サクラバクシンオー：圧倒的スピード(16)だが、スタミナ(20)が無く後半バテる設定
        Horse(name="サクラバクシンオー", speed=16, stamina=20, strategy=RunawayStrategy(), jockey=jockey_a),
        
        # メジロマックイーン：スピード(12)は並だが、スタミナ(80)があり後半もバテない設定
        Horse(name="メジロマックイーン", speed=12, stamina=80, strategy=RunawayStrategy(), jockey=jockey_b),
        
        # オグリキャップ：スピード(12)・スタミナ(80)のバランス型、ルメールの追い込み
        Horse(name="オグリキャップ", speed=12, stamina=80, strategy=ChaserStrategy(), jockey=jockey_a),
    ]

    race = Race(config=config, horses=entry_horses)
    view = ConsoleView()
    race.attach(view)
    
    race.start()