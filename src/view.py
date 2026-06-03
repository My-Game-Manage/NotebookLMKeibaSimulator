"""
コンソールへの出力処理を担います

- メートル表示が float になるため、フォーマットを整えます
- 1着表示から着順表示に変更
"""
from __future__ import annotations
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from .models import Horse

class ConsoleView:
    """コンソールでの可視化を担当する具象Observer"""
    
    def on_race_start(self, horses: List[Horse]):
        print("--- レース開始 ---")
        self._print_status(horses, 0.0)

    def on_step_executed(self, horses: List[Horse], elapsed_time: float):
        # 1秒ごとに現在の各馬の位置を表示（表示がうるさくならないよう調整可能）
        if int(elapsed_time * 10) % 10 == 0:
            self._print_status(horses, elapsed_time)

    def on_race_finished(self, rankings: List[Horse], elapsed_time: float):
        """
        全馬ゴール後の最終順位を表示する。
        引数が winner: Horse から rankings: List[Horse] に変更。
        """
        print(f"\n--- レース終了 (タイム: {elapsed_time:.1f}秒) ---")
        print("最終着順:")
        for i, horse in enumerate(rankings, 1):
            # 1着、2着...と順番に表示
            print(f" {i}着: {horse.name}")

    def _print_status(self, horses: List[Horse], elapsed_time: float):
        """現在の各馬の位置を簡易的なバーで表示"""
        print(f"\n時刻: {elapsed_time:.1f}秒")
        for horse in horses:
            # 進捗を20段階のプロットで表現
            progress = int(horse.position / 80) # 1600m / 20 = 80
            bar = "." * progress + ">" + "." * (20 - progress)
            print(f"[{bar}] {horse.name:10} ({horse.position:6.1f}m)")