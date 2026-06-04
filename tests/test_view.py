"""
ConsoleView が RaceObserver プロトコルを正しく実装しているかを確認します
"""
from __future__ import annotations
from src.view import ConsoleView
from src.observers import RaceObserver

def test_console_view_implements_protocol():
    view = ConsoleView()
    # ConsoleViewが修正後のRaceObserver（rankingsを受け取る形式）に
    # 適合しているか runtime_checkable で確認
    assert isinstance(view, RaceObserver)