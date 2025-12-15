"""API routes for Pomodoro timer."""

from flask import Blueprint, request, jsonify
from config import Config

from app.services.timer_service import TimerService
from app.services.stats_service import StatsService
from app.services.gamification_service import GamificationService
from app.repositories.session_repository import JSONSessionRepository
from app.repositories.user_profile_repository import UserProfileRepository
from app.repositories.settings_repository import JSONSettingsRepository

# Create blueprint
api_bp = Blueprint('api', __name__, url_prefix='/api')

# Initialize repository and services
# Note: In a production app, you'd use dependency injection
repository = JSONSessionRepository(str(Config.DATA_FILE))
timer_service = TimerService(
    repository=repository,
    work_duration=Config.WORK_DURATION,
    break_duration=Config.SHORT_BREAK_DURATION
)
stats_service = StatsService(repository=repository)

# Gamification services
profile_repository = UserProfileRepository(str(Config.USER_PROFILE_FILE))
gamification_service = GamificationService(
    profile_repository=profile_repository,
    session_repository=repository
)

# Settings repository
settings_repository = JSONSettingsRepository(str(Config.SETTINGS_FILE))

# Default user ID for single-user application
DEFAULT_USER_ID = 'default'


@api_bp.route('/session/start', methods=['POST'])
def start_session():
    """Start a new Pomodoro session.
    
    Request JSON:
        {
            "type": "work" or "break"
        }
        
    Response JSON:
        {
            "id": "session-uuid",
            "session_type": "work",
            "start_time": "2025-12-15T10:00:00",
            "duration_minutes": 25,
            "completed": false
        }
    """
    try:
        data = request.get_json(force=True, silent=True)
        
        if data is None:
            return jsonify({'error': 'No data provided'}), 400
        
        session_type = data.get('type')
        
        if not session_type:
            return jsonify({'error': 'session type is required'}), 400
        
        # Start the session
        session = timer_service.start_session(session_type)
        
        return jsonify({
            'id': session.id,
            'session_type': session.session_type,
            'start_time': session.start_time.isoformat(),
            'duration_minutes': session.duration_minutes,
            'completed': session.completed
        }), 201
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500


@api_bp.route('/session/complete', methods=['POST'])
def complete_session():
    """Complete a Pomodoro session.
    
    Request JSON:
        {
            "id": "session-uuid"
        }
        
    Response JSON:
        {
            "id": "session-uuid",
            "session_type": "work",
            "start_time": "2025-12-15T10:00:00",
            "end_time": "2025-12-15T10:25:00",
            "duration_minutes": 25,
            "completed": true,
            "gamification": {
                "xp_earned": 10,
                "total_xp": 110,
                "level": 2,
                "level_up": true,
                "current_streak": 5,
                "streak_continued": true,
                "newly_earned_badges": [...]
            }
        }
    """
    try:
        data = request.get_json(force=True, silent=True)
        
        if data is None:
            return jsonify({'error': 'No data provided'}), 400
        
        session_id = data.get('id')
        
        if not session_id:
            return jsonify({'error': 'session id is required'}), 400
        
        # Complete the session
        session = timer_service.complete_session(session_id)
        
        # Process gamification for completed session
        gamification_result = gamification_service.process_session_completion(
            user_id=DEFAULT_USER_ID,
            session_type=session.session_type
        )
        
        return jsonify({
            'id': session.id,
            'session_type': session.session_type,
            'start_time': session.start_time.isoformat(),
            'end_time': session.end_time.isoformat() if session.end_time else None,
            'duration_minutes': session.duration_minutes,
            'completed': session.completed,
            'gamification': gamification_result
        }), 200
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500


@api_bp.route('/session/reset', methods=['DELETE'])
def reset_session():
    """Reset (cancel) a Pomodoro session.
    
    Request JSON:
        {
            "id": "session-uuid"
        }
        
    Response JSON:
        {
            "message": "Session reset successfully"
        }
    """
    try:
        data = request.get_json(force=True, silent=True)
        
        if data is None:
            return jsonify({'error': 'No data provided'}), 400
        
        session_id = data.get('id')
        
        if not session_id:
            return jsonify({'error': 'session id is required'}), 400
        
        # Reset the session
        timer_service.reset_session(session_id)
        
        return jsonify({
            'message': 'Session reset successfully'
        }), 200
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500


@api_bp.route('/stats/today', methods=['GET'])
def get_today_stats():
    """Get today's statistics.
    
    Returns:
        JSON response with today's statistics:
        - completed_sessions: Number of completed sessions
        - total_focus_minutes: Total focus time in minutes
        - formatted_time: Formatted time string
        - work_sessions: Number of completed work sessions
        - break_sessions: Number of completed break sessions
        
    Status Codes:
        200: Statistics retrieved successfully
        500: Internal server error
    """
    try:
        stats = stats_service.calculate_today()
        formatted_time = StatsService.format_time(stats.total_focus_minutes)
        
        return jsonify({
            'completed_sessions': stats.completed_sessions,
            'total_focus_minutes': stats.total_focus_minutes,
            'formatted_time': formatted_time,
            'work_sessions': stats.work_sessions,
            'break_sessions': stats.break_sessions,
            'date': stats.date.isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500


@api_bp.route('/settings', methods=['GET'])
def get_settings():
    """Get user settings.
    
    Returns:
        JSON response with current user settings:
        - work_duration: Work session duration in minutes
        - break_duration: Break session duration in minutes
        - theme: UI theme ('light', 'dark', 'focus')
        - sound_start: Enable start sound
        - sound_end: Enable end/completion sound
        - sound_tick: Enable tick sound
        
    Status Codes:
        200: Settings retrieved successfully
        500: Internal server error
    """
    try:
        settings = settings_repository.load()
        return jsonify(settings.to_dict()), 200
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500


@api_bp.route('/settings', methods=['POST'])
def save_settings():
    """Save user settings.
    
    Request JSON:
        {
            "work_duration": 25,
            "break_duration": 5,
            "theme": "light",
            "sound_start": true,
            "sound_end": true,
            "sound_tick": false
        }
        
    Response JSON:
        {
            "work_duration": 25,
            "break_duration": 5,
            "theme": "light",
            "sound_start": true,
            "sound_end": true,
            "sound_tick": false
        }
        
    Status Codes:
        200: Settings saved successfully
        400: Invalid settings data
        500: Internal server error
    """
    try:
        data = request.get_json(force=True, silent=True)
        
        if data is None:
            return jsonify({'error': 'No data provided'}), 400
        
        # Create and validate settings
        from app.models.settings import UserSettings
        settings = UserSettings.from_dict(data)
        
        # Save settings
        settings_repository.save(settings)
        
        return jsonify(settings.to_dict()), 200
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500
