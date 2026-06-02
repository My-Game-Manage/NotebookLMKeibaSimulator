"""
レースのライフサイクルを管理します

- Race クラスで、エンジンの elapsed_time を View に渡せるように調整します
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

