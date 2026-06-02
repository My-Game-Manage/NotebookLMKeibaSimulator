from __future__ import annotations
from src.models import Horse, Jockey, RaceConfig
from src.strategies import (
    RunawayStrategy, LeadingStrategy, MidPackStrategy, ChaserStrategy
)
from src.engine import SimulationEngine
from src.race import Race
from src.views import ConsoleView

def main():
    # 1. 設定の初期化
    config = RaceConfig(distance=1600.0)
    race = Race(config)
    view = ConsoleView()
    race.register_observer(view)

    # 2. 出走馬・騎手のデータ構築
    # (名前, 最高速度, スタミナ, 騎手名, 騎手スキル, 脚質インスタンス)
    entries = [
        ("Silence", 20.5, 750.0, "J.Take", 0.95, RunawayStrategy()),
        ("Teio", 19.8, 880.0, "M.Okabe", 0.90, LeadingStrategy()),
        ("Special", 19.5, 950.0, "Y.Take", 0.88, MidPackStrategy()),
        ("GoldShip", 19.0, 1150.0, "N.Yokoyama", 0.85, ChaserStrategy()),
    ]

    for h_name, speed, stam, j_name, skill, strategy in entries:
        jockey = Jockey(name=j_name, skill=skill)
        horse = Horse(name=h_name, max_speed=speed, stamina=stam, jockey=jockey)
        engine = SimulationEngine(horse, strategy, config)
        race.add_horse(engine)

    # 3. レース開始
    print(f"--- Race Start: {config.distance}m ---")
    race.run()

if __name__ == "__main__":
    main()