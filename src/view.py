"""
コンソールへの出力処理を担います

- メートル表示が float になるため、フォーマットを整えます
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
        self._print_status(horses, 0.0)

    def on_step_executed(self, horses: List[Horse], elapsed_time: float):
        self._print_status(horses, elapsed_time)

    def on_race_finished(self, winner: Horse, elapsed_time: float):
        print(f"\n--- レース終了 ---")
        print(f"タイム: {elapsed_time:.2f}秒")
        print(f"🏆 勝者: {winner.name} 🏆 (騎手: {winner.jockey.name})")

    def _print_status(self, horses: List[Horse], elapsed_time: float):
        print(f"\n現在の状況 (経過時間: {elapsed_time:.1f}秒):")
        for horse in horses:
            # 表示上の進捗バー（1600mを32文字分などで表現）
            # 1600mを32文字分（50mにつき1文字）で表現
            visual_path = "-" * int(horse.position // 50)
            # v0.1.0の名残である「バテ表示」などの条件があればここに追加可能
            print(f"{horse.name}: {visual_path}▶ ({horse.position:.1f}m)")
