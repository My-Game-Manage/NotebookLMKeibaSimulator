"""
表示層との結合度を下げるためのインターフェースです
"""
from __future__ import annotations
from typing import Protocol, List, TYPE_CHECKING, runtime_checkable

if TYPE_CHECKING:
    from .models import Horse

@runtime_checkable
class RaceObserver(Protocol):
    """レース進捗を監視するためのインターフェース定義"""
    def on_race_start(self, horses: List[Horse]) -> None: ...
    def on_step_executed(self, horses: List[Horse]) -> None: ...
    def on_race_finished(self, winner: Horse) -> None: ...
