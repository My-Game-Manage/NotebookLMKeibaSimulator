from __future__ import annotations
from src.interfaces import RaceObserver
from src.models import RaceState

class ConsoleView(RaceObserver):
    """コンソール出力を担当するビュークラス"""

    def update(self, states: list[RaceState]) -> None:
        print("\n" + "="*60)
        print(f"{'Name':<12} | {'Pos':<8} | {'Speed':<8} | {'Stamina':<8} | {'Rank'}")
        print("-"*60)
        for s in sorted(states, key=lambda x: x.rank_order):
            dist_str = f"{s.distance:7.1f}m" if not s.is_finished else "GOALED"
            print(f"{s.name:<12} | {dist_str:<8} | {s.speed:5.2f}m/s | {max(0, s.stamina):7.1f} | {s.rank_order}")

    def notify_finish(self, final_results: list[RaceState]) -> None:
        print("\n\n" + "#"*30)
        print(" FINAL RACE RESULTS ")
        print("#"*30)
        for i, res in enumerate(final_results, 1):
            print(f"{i}位: {res.name}")
        print("#"*30 + "\n")