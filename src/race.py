from __future__ import annotations
from src.models import RaceConfig, RaceState
from src.engine import SimulationEngine
from src.interfaces import RaceObserver

class Race:
    """レース全体の進行とライフサイクルを管理するクラス"""

    def __init__(self, config: RaceConfig):
        self.config = config
        self.engines: list[SimulationEngine] = []
        self.observers: list[RaceObserver] = []

    def add_horse(self, horse_engine: SimulationEngine) -> None:
        """出走馬（エンジン）の追加"""
        self.engines.append(horse_engine)

    def register_observer(self, observer: RaceObserver) -> None:
        """オブザーバーの登録"""
        self.observers.append(observer)

    def run(self) -> None:
        """シミュレーションループの実行"""
        while not all(e.is_finished for e in self.engines):
            for e in self.engines:
                e.step()
            
            current_states = self._generate_states()
            for observer in self.observers:
                observer.update(current_states)

        # 最終リザルトの通知 (ゴールした順序 = finish_time の昇順)
        final_results = sorted(
            self._generate_states(), 
            key=lambda x: self._get_finish_time(x.name)
        )
        for observer in self.observers:
            observer.notify_finish(final_results)

    def _get_finish_time(self, name: str) -> float:
        """特定の馬のゴールタイムを取得(ソート用)"""
        for e in self.engines:
            if e.horse.name == name:
                return e.finish_time
        return float('inf')

    def _generate_states(self) -> list[RaceState]:
        """現在の全エンジンの状態をRaceState DTOに変換"""
        states = []
        # 現在の順位付け（走行距離ベース）
        sorted_engines = sorted(self.engines, key=lambda x: x.current_distance, reverse=True)
        
        for e in self.engines:
            rank = sorted_engines.index(e) + 1
            states.append(RaceState(
                name=e.horse.name,
                distance=e.current_distance,
                speed=e.current_speed,
                stamina=e.current_stamina,
                is_finished=e.is_finished,
                rank_order=rank
            ))
        return states