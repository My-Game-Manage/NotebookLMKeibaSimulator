"""
ConsoleView が RaceObserver プロトコルを正しく実装しているかを確認します
"""
from __future__ import annotations
from src.view import ConsoleView
from src.observers import RaceObserver

def test_console_view_implements_protocol():
    view = ConsoleView()
    # ConsoleViewがRaceObserverの要件を満たしているか確認
    assert isinstance(view, RaceObserver)