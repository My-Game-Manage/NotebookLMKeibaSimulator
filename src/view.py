"""
コンソールへの出力処理を担います
"""
from __future__ import annotations
from typing import List, TYPE_CHECKING
from .strategies import RunawayStrategy

if TYPE_CHECKING:
    from .models import Horse

class ConsoleView:
    """コンソールでの可視化を担当する具象Observer"""
    def on_race_start(self, horses: List[Horse]):
        print("--- レース開始 ---")
        self._print_status(horses)

    def on_step_executed(self, horses: List[Horse]):
        self._print_status(horses)

    def on_race_finished(self, winner: Horse):
        print(f"\n--- レース終了 ---\n🏆 勝者: {winner.name} 🏆 (騎手: {winner.jockey.name})")

    def _print_status(self, horses: List[Horse]):
        print("\n現在の状況:")
        for horse in horses:
            visual_path = "-" * (horse.position // 5)
            strategy_name = "逃げ" if isinstance(horse.strategy, RunawayStrategy) else "追込"
            # v0.1.0ベースのバテ表示（位置50以上かつスタミナ50未満）
            status_tag = "（バテ）" if horse.position > 50 and horse.stamina < 50 else ""
            print(f"{horse.name}{status_tag} ({horse.jockey.name}騎手) [{strategy_name}]: {visual_path}▶ ({horse.position}m)")
