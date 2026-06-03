"""
レースのライフサイクルを管理します

- Race クラスで、エンジンの elapsed_time を View に渡せるように調整します
- レースの終了条件を「勝者が決まるまで」から「全馬がゴールするまで」に変更します
"""
from __future__ import annotations
import time
from typing import List, Optional, TYPE_CHECKING
from .engine import SimulationEngine

if TYPE_CHECKING:
    from .models import Horse, RaceConfig
    from .observers import RaceObserver

class Race:
    """各コンポーネントを統合し、レース進行を制御する"""
    def __init__(self, config: RaceConfig, horses: List[Horse]):
        self.config = config
        self.horses = horses
        self.engine = SimulationEngine(config.course_length, horses, config.tick_time)
        self.winner: Optional[Horse] = None
        self._observers: List[RaceObserver] = []

    def attach(self, observer: RaceObserver):
        self._observers.append(observer)

    def start(self):
        for o in self._observers:
            o.on_race_start(self.horses)

        while self.winner is None:
            self.winner = self.engine.step()
            # Viewに現在の経過時間を伝える（必要に応じてObserverを拡張）
            # エンジンの経過時間を取得して通知
            current_time = self.engine.elapsed_time
            for o in self._observers:
                o.on_step_executed(self.horses, current_time)
        
            if not self.winner:
                time.sleep(self.config.interval)
                    
        for o in self._observers:
            o.on_race_finished(self.winner, self.engine.elapsed_time)
            
    def run(self) -> None:
        for observer in self._observers:
            observer.on_race_start(self.horses)

        # 全馬がゴールするまでループを回す
        while not self.engine.is_all_finished():
            self.engine.step()
            
            for observer in self._observers:
                observer.on_step_executed(self.horses, self.engine.elapsed_time)
            
            time.sleep(self.config.interval)

        # 全馬の順位（rankings）を渡して終了通知
        for observer in self._observers:
            # Observerのインターフェースも List[Horse] を受け取れるよう修正が必要
            observer.on_race_finished(self.engine.rankings, self.engine.elapsed_time)


