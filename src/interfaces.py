from __future__ import annotations
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.models import RaceState

class RaceObserver(ABC):
    """レース状況を監視するための抽象インターフェース"""

    @abstractmethod
    def update(self, states: list[RaceState]) -> None:
        """各ステップの更新通知"""
        pass

    @abstractmethod
    def notify_finish(self, final_results: list[RaceState]) -> None:
        """レース終了時の最終結果通知"""
        pass