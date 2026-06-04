"""
エントリーポイントとして各モジュールを組み立てます

- 生成する馬のスタミナ値を、1600mという距離に対して適切な範囲に設定します
- 「先行（FrontRunnerStrategy）」と「差し（MidPackerStrategy）」を組み込み、4頭サンプルに
- explosiveness は 0〜100 の整数値（int）として、各馬のインスタンス化の際、stamina と strategy の間に引数として追加します
"""
from __future__ import annotations
from src.models import Jockey, Horse, RaceConfig
from src.strategies import (
    RunawayStrategy, 
    FrontRunnerStrategy, 
    MidPackerStrategy, 
    ChaserStrategy
)
from src.race import Race
from src.view import ConsoleView

def main():
    # 1. レース設定（1600m、計算精度0.1秒、表示間隔0.01秒） [1, 3]
    config = RaceConfig(course_length=1600, tick_time=0.1, interval=0.01)

    # 2. 騎手の作成（脚質への適正を考慮して配置） [2]
    jockey_a = Jockey("山田騎手", front_skill=1.2, back_skill=0.8)
    jockey_b = Jockey("佐藤騎手", front_skill=1.0, back_skill=1.0)
    jockey_c = Jockey("田中騎手", front_skill=0.8, back_skill=1.2)

    # 3. 4つの脚質が揃った馬のラインナップ [1, 2]
    # speed: 基本速度に影響 / stamina: スパート開始タイミングとバテにくさに影響
    # explosiveness（瞬発力）を追加。追い込み馬や差し馬は高めに設定。
    horses = [
        Horse(
            name="サイレンス逃げ", 
            speed=75, stamina=1150, explosiveness=40,  # 逃げは粘り重視
            strategy=RunawayStrategy(), 
            jockey=jockey_a
        ),
        Horse(
            name="テイオー先行", 
            speed=70, stamina=1300, explosiveness=60, 
            strategy=FrontRunnerStrategy(), 
            jockey=jockey_b
        ),
        Horse(
            name="オグリ差し", 
            speed=65, stamina=1400, explosiveness=80,  # 差し・追込は瞬発力を高く
            strategy=MidPackerStrategy(), 
            jockey=jockey_c
        ),
        Horse(
            name="ゴルシ追込", 
            speed=60, stamina=1550, explosiveness=90, 
            strategy=ChaserStrategy(), 
            jockey=jockey_c
        ),
    ]

    # 4. レースの組み立てと実行 [4]
    race = Race(config, horses)
    
    # 表示用のView（Observer）を追加 [5, 6]
    view = ConsoleView()
    race.attach(view)

    # レース開始
    race.run()

if __name__ == "__main__":
    main()