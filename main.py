"""
エントリーポイントとして各モジュールを組み立てます

- 生成する馬のスタミナ値を、1600mという距離に対して適切な範囲に設定します
- 「先行（FrontRunnerStrategy）」と「差し（MidPackerStrategy）」を組み込み、4頭サンプルに
- explosiveness は 0〜100 の整数値（int）として、各馬のインスタンス化の際、stamina と strategy の間に引数として追加します
- 各馬の個性を出すために、acceleration を設定
"""
from __future__ import annotations
from src.models import Jockey, Horse, RaceConfig, Corner  # Corner を追加
from src.strategies import (
    RunawayStrategy, 
    FrontRunnerStrategy, 
    MidPackerStrategy, 
    ChaserStrategy
)
from src.race import Race
from src.view import ConsoleView

def main():
    # 1. コース形状（コーナー）の定義
    # start_pos: 開始地点(m), end_pos: 終了地点(m), radius: 半径(m)
    # 半径が小さいほど急カーブとなり、減速効果が強まります
    corners = [
        Corner(start_pos=400.0, end_pos=600.0, radius=150.0),   # 第3コーナー
        Corner(start_pos=600.0, end_pos=1000.0, radius=120.0)  # 第4コーナー（やや急）
    ]

    # 2. レース設定（コーナーリストを注入）
    # 決定論的モデルに基づき、これらの値は全馬に一律の物理制約として作用します
    # 馬場状態で「重」を設定した場合
    config = RaceConfig(
        course_length=1600, 
        tick_time=0.1, 
        interval=0.01,
        corners=corners,
        track_condition="重"  # ここで馬場状態を変更
    )

    # 3. 騎手の作成（脚質への適正を考慮して配置） [2]
    jockey_a = Jockey("山田騎手", front_skill=1.2, back_skill=0.8)
    jockey_b = Jockey("佐藤騎手", front_skill=1.0, back_skill=1.0)
    jockey_c = Jockey("田中騎手", front_skill=0.8, back_skill=1.2)

    # 3. 4つの脚質が揃った馬のラインナップ [1, 2]
    # speed: 基本速度に影響 / stamina: スパート開始タイミングとバテにくさに影響
    # explosiveness（瞬発力）を追加。追い込み馬や差し馬は高めに設定。
    horses = [
        Horse(
            name="サイレンス逃げ", 
            speed=75, stamina=1100, explosiveness=40,  # 逃げは粘り重視
            acceleration=90,  # 逃げ馬はスタートダッシュのために加速力を高く設定
            power=30,
            strategy=RunawayStrategy(), 
            jockey=jockey_a
        ),
        Horse(
            name="テイオー先行", 
            speed=70, stamina=1250, explosiveness=60,
            acceleration=70,  # 先行馬も加速力を高めに設定
            power=60,
            strategy=FrontRunnerStrategy(), 
            jockey=jockey_b
        ),
        Horse(
            name="オグリ差し", 
            speed=68, stamina=1350, explosiveness=85,  # 差し・追込は瞬発力を高く
            acceleration=60,  # 差し馬は序盤は標準
            power=70,
            strategy=MidPackerStrategy(), 
            jockey=jockey_c
        ),
        Horse(
            name="ゴルシ追込", 
            speed=65, stamina=1500, explosiveness=95, 
            acceleration=40,  # 追込馬は序盤はゆっくり、後半の加速もじわじわと
            power=95,
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