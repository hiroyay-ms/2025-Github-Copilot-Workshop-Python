"""Tests for StatsService"""
import pytest
from datetime import datetime, date, timedelta
from freezegun import freeze_time

from app.models.session import Session
from app.models.stats import DailyStats
from app.services.stats_service import StatsService
from app.repositories.session_repository import InMemorySessionRepository


class TestStatsServiceCalculateToday:
    """Tests for StatsService.calculate_today()"""
    
    def test_calculate_today_with_no_sessions(self):
        """空のリポジトリで統計計算"""
        with freeze_time('2025-12-15 10:00:00'):
            repository = InMemorySessionRepository()
            service = StatsService(repository=repository)
            
            stats = service.calculate_today()
            
            assert stats.date == date(2025, 12, 15)
            assert stats.completed_sessions == 0
            assert stats.total_focus_minutes == 0
            assert stats.work_sessions == 0
            assert stats.break_sessions == 0
    
    def test_calculate_today_with_completed_work_sessions(self):
        """完了した作業セッションがある場合"""
        with freeze_time('2025-12-15 10:00:00'):
            repository = InMemorySessionRepository()
            service = StatsService(repository=repository)
            
            # 2つの完了済み作業セッションを作成
            session1 = Session(
                id='session-1',
                session_type='work',
                start_time=datetime(2025, 12, 15, 9, 0, 0),
                end_time=datetime(2025, 12, 15, 9, 25, 0),
                duration_minutes=25,
                completed=True
            )
            session2 = Session(
                id='session-2',
                session_type='work',
                start_time=datetime(2025, 12, 15, 9, 30, 0),
                end_time=datetime(2025, 12, 15, 9, 55, 0),
                duration_minutes=25,
                completed=True
            )
            repository.save(session1)
            repository.save(session2)
            
            stats = service.calculate_today()
            
            assert stats.date == date(2025, 12, 15)
            assert stats.completed_sessions == 2
            assert stats.total_focus_minutes == 50  # 25 + 25
            assert stats.work_sessions == 2
            assert stats.break_sessions == 0
    
    def test_calculate_today_with_work_and_break_sessions(self):
        """作業セッションと休憩セッションの両方がある場合"""
        with freeze_time('2025-12-15 15:00:00'):
            repository = InMemorySessionRepository()
            service = StatsService(repository=repository)
            
            # 作業セッション
            work_session = Session(
                id='work-1',
                session_type='work',
                start_time=datetime(2025, 12, 15, 14, 0, 0),
                end_time=datetime(2025, 12, 15, 14, 25, 0),
                duration_minutes=25,
                completed=True
            )
            # 休憩セッション
            break_session = Session(
                id='break-1',
                session_type='break',
                start_time=datetime(2025, 12, 15, 14, 25, 0),
                end_time=datetime(2025, 12, 15, 14, 30, 0),
                duration_minutes=5,
                completed=True
            )
            repository.save(work_session)
            repository.save(break_session)
            
            stats = service.calculate_today()
            
            assert stats.completed_sessions == 2
            assert stats.total_focus_minutes == 25  # 作業セッションのみカウント
            assert stats.work_sessions == 1
            assert stats.break_sessions == 1
    
    def test_calculate_today_ignores_incomplete_sessions(self):
        """未完了のセッションは統計に含まれない"""
        with freeze_time('2025-12-15 12:00:00'):
            repository = InMemorySessionRepository()
            service = StatsService(repository=repository)
            
            # 完了済みセッション
            completed_session = Session(
                id='completed-1',
                session_type='work',
                start_time=datetime(2025, 12, 15, 10, 0, 0),
                end_time=datetime(2025, 12, 15, 10, 25, 0),
                duration_minutes=25,
                completed=True
            )
            # 未完了セッション
            incomplete_session = Session(
                id='incomplete-1',
                session_type='work',
                start_time=datetime(2025, 12, 15, 11, 0, 0),
                end_time=None,
                duration_minutes=25,
                completed=False
            )
            repository.save(completed_session)
            repository.save(incomplete_session)
            
            stats = service.calculate_today()
            
            assert stats.completed_sessions == 1
            assert stats.total_focus_minutes == 25
            assert stats.work_sessions == 1
    
    def test_calculate_today_ignores_previous_day_sessions(self):
        """前日のセッションは含まれない"""
        with freeze_time('2025-12-15 10:00:00'):
            repository = InMemorySessionRepository()
            service = StatsService(repository=repository)
            
            # 前日のセッション
            yesterday_session = Session(
                id='yesterday-1',
                session_type='work',
                start_time=datetime(2025, 12, 14, 10, 0, 0),
                end_time=datetime(2025, 12, 14, 10, 25, 0),
                duration_minutes=25,
                completed=True
            )
            # 今日のセッション
            today_session = Session(
                id='today-1',
                session_type='work',
                start_time=datetime(2025, 12, 15, 9, 0, 0),
                end_time=datetime(2025, 12, 15, 9, 25, 0),
                duration_minutes=25,
                completed=True
            )
            repository.save(yesterday_session)
            repository.save(today_session)
            
            stats = service.calculate_today()
            
            assert stats.completed_sessions == 1
            assert stats.total_focus_minutes == 25
    
    def test_calculate_today_with_multiple_work_sessions(self):
        """複数の作業セッションの集計"""
        with freeze_time('2025-12-15 16:00:00'):
            repository = InMemorySessionRepository()
            service = StatsService(repository=repository)
            
            # 4つの作業セッション（合計100分）
            for i in range(4):
                session = Session(
                    id=f'work-{i}',
                    session_type='work',
                    start_time=datetime(2025, 12, 15, 9 + i, 0, 0),
                    end_time=datetime(2025, 12, 15, 9 + i, 25, 0),
                    duration_minutes=25,
                    completed=True
                )
                repository.save(session)
            
            stats = service.calculate_today()
            
            assert stats.completed_sessions == 4
            assert stats.total_focus_minutes == 100
            assert stats.work_sessions == 4


class TestStatsServiceFormatTime:
    """Tests for StatsService.format_time()"""
    
    def test_format_time_zero_minutes(self):
        """0分のフォーマット"""
        result = StatsService.format_time(0)
        assert result == '0分'
    
    def test_format_time_only_minutes(self):
        """分のみの場合"""
        assert StatsService.format_time(1) == '1分'
        assert StatsService.format_time(30) == '30分'
        assert StatsService.format_time(59) == '59分'
    
    def test_format_time_exact_hours(self):
        """ちょうど時間の場合"""
        assert StatsService.format_time(60) == '1時間'
        assert StatsService.format_time(120) == '2時間'
        assert StatsService.format_time(180) == '3時間'
    
    def test_format_time_hours_and_minutes(self):
        """時間と分の両方がある場合"""
        assert StatsService.format_time(65) == '1時間5分'
        assert StatsService.format_time(90) == '1時間30分'
        assert StatsService.format_time(100) == '1時間40分'
        assert StatsService.format_time(145) == '2時間25分'
        assert StatsService.format_time(200) == '3時間20分'
    
    def test_format_time_large_values(self):
        """大きな値のフォーマット"""
        assert StatsService.format_time(360) == '6時間'
        assert StatsService.format_time(500) == '8時間20分'


class TestStatsServiceWithCustomTimeProvider:
    """Tests for StatsService with custom time provider"""
    
    def test_calculate_today_uses_custom_time_provider(self):
        """カスタム時刻プロバイダーの使用"""
        repository = InMemorySessionRepository()
        
        # 固定時刻を返すプロバイダー
        fixed_time = datetime(2025, 12, 20, 14, 30, 0)
        service = StatsService(
            repository=repository,
            time_provider=lambda: fixed_time
        )
        
        stats = service.calculate_today()
        
        assert stats.date == date(2025, 12, 20)


class TestDailyStatsModel:
    """Tests for DailyStats model"""
    
    def test_daily_stats_to_dict(self):
        """DailyStatsの辞書変換"""
        stats = DailyStats(
            date=date(2025, 12, 15),
            completed_sessions=4,
            total_focus_minutes=100,
            work_sessions=4,
            break_sessions=0
        )
        
        result = stats.to_dict()
        
        assert result == {
            'date': '2025-12-15',
            'completed_sessions': 4,
            'total_focus_minutes': 100,
            'work_sessions': 4,
            'break_sessions': 0
        }
