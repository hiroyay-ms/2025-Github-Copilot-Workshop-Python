"""統計モデル"""
from dataclasses import dataclass
from datetime import date


@dataclass
class DailyStats:
    """日次統計データクラス"""
    date: date
    completed_sessions: int
    total_focus_minutes: int
    work_sessions: int
    break_sessions: int
    
    def to_dict(self) -> dict:
        """辞書形式に変換"""
        return {
            'date': self.date.isoformat(),
            'completed_sessions': self.completed_sessions,
            'total_focus_minutes': self.total_focus_minutes,
            'work_sessions': self.work_sessions,
            'break_sessions': self.break_sessions
        }
