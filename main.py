"""
エントリーポイントとして各モジュールを組み立てます

- 生成する馬のスタミナ値を、1600mという距離に対して適切な範囲に設定します
"""
from __future__ import annotations
from src.models import Jockey, Horse, RaceConfig
from src.strategies import RunawayStrategy, ChaserStrategy
from src.race import Race
from src.view import ConsoleView

def main():
    # 1. コンフィグ設定
    config = RaceConfig(course_length=1600, interval=0.01, tick_time=0.1)
    
    # 2. 騎手と馬の生成
    # 1600mを走り切るには、消費係数0.7の場合、約1120のスタミナが必要です
    j1 = Jockey("武豊", 1.2, 1.0)
    j2 = Jockey("ルメール", 1.0, 1.2)
    
    h1 = Horse("サイレンススズカ", speed=70, stamina=1200, strategy=RunawayStrategy(), jockey=j1)
    h2 = Horse("ゴールドシップ", speed=50, stamina=1500, strategy=ChaserStrategy(), jockey=j2)
    
    # 3. レースの構築
    race = Race(config, [h1, h2])
    race.attach(ConsoleView())
    
    # 4. レース開始
    race.run()

if __name__ == "__main__":
    main()