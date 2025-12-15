"""API routes for gamification features."""

from flask import Blueprint, jsonify
from config import Config

from app.services.gamification_service import GamificationService
from app.repositories.user_profile_repository import UserProfileRepository
from app.repositories.session_repository import JSONSessionRepository

# Create blueprint
gamification_bp = Blueprint('gamification', __name__, url_prefix='/api/gamification')

# Initialize repositories and services
# Note: Using default user_id='default' for single-user application
DEFAULT_USER_ID = 'default'

profile_repository = UserProfileRepository(str(Config.USER_PROFILE_FILE))
session_repository = JSONSessionRepository(str(Config.DATA_FILE))
gamification_service = GamificationService(
    profile_repository=profile_repository,
    session_repository=session_repository
)


@gamification_bp.route('/profile', methods=['GET'])
def get_profile():
    """Get user gamification profile.
    
    Returns:
        JSON response with user profile:
        - user_id: User identifier
        - level: Current level
        - experience_points: Total XP
        - badges: List of earned badge IDs
        - current_streak: Current streak days
        - longest_streak: Longest streak achieved
        
    Status Codes:
        200: Profile retrieved successfully
        500: Internal server error
    """
    try:
        profile = gamification_service.get_profile(DEFAULT_USER_ID)
        
        return jsonify({
            'user_id': profile.user_id,
            'level': profile.level,
            'experience_points': profile.experience_points,
            'xp_to_next_level': 100 - (profile.experience_points % 100),
            'badges': profile.badges,
            'current_streak': profile.current_streak,
            'longest_streak': profile.longest_streak,
            'last_activity_date': profile.last_activity_date
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500


@gamification_bp.route('/badges', methods=['GET'])
def get_badges():
    """Get all badges with earned status.
    
    Returns:
        JSON response with badges list:
        - badges: List of badge objects with earned status
        
    Status Codes:
        200: Badges retrieved successfully
        500: Internal server error
    """
    try:
        badges = gamification_service.get_earned_badges(DEFAULT_USER_ID)
        
        return jsonify({
            'badges': badges
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500


@gamification_bp.route('/stats/weekly', methods=['GET'])
def get_weekly_stats():
    """Get weekly statistics.
    
    Returns:
        JSON response with weekly stats:
        - completed_sessions: Number of completed sessions
        - work_sessions: Number of work sessions
        - total_focus_minutes: Total focus time
        - period: 'week'
        
    Status Codes:
        200: Statistics retrieved successfully
        500: Internal server error
    """
    try:
        stats = gamification_service.get_weekly_stats(DEFAULT_USER_ID)
        
        return jsonify(stats), 200
        
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500


@gamification_bp.route('/stats/monthly', methods=['GET'])
def get_monthly_stats():
    """Get monthly statistics.
    
    Returns:
        JSON response with monthly stats:
        - completed_sessions: Number of completed sessions
        - work_sessions: Number of work sessions
        - total_focus_minutes: Total focus time
        - period: 'month'
        
    Status Codes:
        200: Statistics retrieved successfully
        500: Internal server error
    """
    try:
        stats = gamification_service.get_monthly_stats(DEFAULT_USER_ID)
        
        return jsonify(stats), 200
        
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500
