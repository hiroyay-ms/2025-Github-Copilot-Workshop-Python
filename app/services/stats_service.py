"""統計サービス"""
from datetime import datetime, date
from typing import Callable
from app.models.stats import DailyStats
from app.repositories.base import SessionRepositoryInterface


class StatsService:
    """統計計算サービス"""
    
    def __init__(self, 
                 repository: SessionRepositoryInterface,
                 time_provider: Callable[[], datetime] = None):
        """
        Args:
            repository: セッションリポジトリ
            time_provider: 現在時刻を返す関数（デフォルトはdatetime.now）
        """
        self.repository = repository
        self.time_provider = time_provider or datetime.now
    
    def calculate_today(self) -> DailyStats:
        """今日の統計を計算
        
        Returns:
            DailyStats: 今日の統計データ
        """
        current_time = self.time_provider()
        today = current_time.date()
        
        # 今日のセッションを取得
        sessions = self.repository.find_by_date(today)
        
        # 完了セッションのみをフィルタ
        completed_sessions = [s for s in sessions if s.completed]
        
        # 統計計算
        work_sessions = [s for s in completed_sessions if s.session_type == 'work']
        break_sessions = [s for s in completed_sessions if s.session_type == 'break']
        
        # 総集中時間（作業セッションのみ）
        total_focus_minutes = sum(s.duration_minutes for s in work_sessions)
        
        return DailyStats(
            date=today,
            completed_sessions=len(completed_sessions),
            total_focus_minutes=total_focus_minutes,
            work_sessions=len(work_sessions),
            break_sessions=len(break_sessions)
        )
    
    @staticmethod
    def format_time(minutes: int) -> str:
        """分を「X時間Y分」形式にフォーマット
        
        Args:
            minutes: 分数
            
        Returns:
            str: フォーマットされた文字列
            
        Examples:
            >>> StatsService.format_time(0)
            '0分'
            >>> StatsService.format_time(30)
            '30分'
            >>> StatsService.format_time(60)
            '1時間'
            >>> StatsService.format_time(100)
            '1時間40分'
        """
        if minutes == 0:
            return '0分'
        
        hours = minutes // 60
        mins = minutes % 60
        
        if hours > 0 and mins > 0:
            return f'{hours}時間{mins}分'
        elif hours > 0:
            return f'{hours}時間'
        else:
            return f'{mins}分'
