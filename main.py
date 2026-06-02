"""
エントリーポイントとして各モジュールを組み立てます
"""
from __future__ import annotations
from src.models import Jockey, Horse, RaceConfig
from src.strategies import RunawayStrategy, ChaserStrategy
from src.race import Race
from src.view import ConsoleView

def main():
    # 1. コンフィグ設定
    config = RaceConfig(course_length=100, interval=0.5)
    
    # 2. 騎手と馬の生成
    j1 = Jockey("武豊", 1.2, 1.0)
    j2 = Jockey("ルメール", 1.0, 1.2)
    
    h1 = Horse("サイレンススズカ", 8, 80, RunawayStrategy(), j1)
    h2 = Horse("ゴールドシップ", 10, 95, ChaserStrategy(), j2)
    
    # 3. レースの構築
    race = Race(config, [h1, h2])
    race.attach(ConsoleView())
    
    # 4. レース開始
    race.start()

if __name__ == "__main__":
    main()