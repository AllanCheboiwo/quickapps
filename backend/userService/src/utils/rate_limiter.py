from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from src.models.resume_rate_limit import ResumeRateLimit
from src.core.exceptions import RateLimitExceeded
import logging

logger = logging.getLogger(__name__)

class ResumeRateLimiter:
    """
    Rate limiter for resume generation
    - Max 5 resumes per hour per user
    - Prevents token waste from spam requests
    """
    
    MAX_RESUMES_PER_HOUR = 5
    HOUR_IN_SECONDS = 3600
    
    @staticmethod
    def check_rate_limit(user_id: int, db: Session) -> bool:
        """
        Check if user has exceeded rate limit
        Returns True if allowed, raises RateLimitExceeded if blocked
        """
        one_hour_ago = datetime.utcnow() - timedelta(seconds=ResumeRateLimiter.HOUR_IN_SECONDS)
        
        # Count resumes generated in last hour
        recent_resumes = db.query(ResumeRateLimit).filter(
            ResumeRateLimit.user_id == user_id,
            ResumeRateLimit.created_at >= one_hour_ago
        ).count()
        
        if recent_resumes >= ResumeRateLimiter.MAX_RESUMES_PER_HOUR:
            logger.warning(f"User {user_id} exceeded resume generation rate limit")
            raise RateLimitExceeded(
                detail=f"Rate limit exceeded. You can generate {ResumeRateLimiter.MAX_RESUMES_PER_HOUR} resumes per hour. "
                       f"Try again in {ResumeRateLimiter._get_reset_time(db, user_id)} minutes."
            )
        
        return True
    
    @staticmethod
    def log_generation(user_id: int, profile_id: int, db: Session) -> None:
        """Log a resume generation for rate limiting"""
        try:
            rate_limit_entry = ResumeRateLimit(user_id=user_id, profile_id=profile_id)
            db.add(rate_limit_entry)
            db.commit()
            logger.info(f"Logged resume generation for user {user_id}")
        except Exception as e:
            logger.error(f"Failed to log rate limit for user {user_id}: {e}")
            db.rollback()
    
    @staticmethod
    def _get_reset_time(db: Session, user_id: int) -> int:
        """Get minutes until rate limit resets"""
        one_hour_ago = datetime.utcnow() - timedelta(seconds=ResumeRateLimiter.HOUR_IN_SECONDS)
        
        oldest_entry = db.query(ResumeRateLimit).filter(
            ResumeRateLimit.user_id == user_id,
            ResumeRateLimit.created_at >= one_hour_ago
        ).order_by(ResumeRateLimit.created_at.asc()).first()
        
        if oldest_entry:
            reset_time = oldest_entry.created_at + timedelta(seconds=ResumeRateLimiter.HOUR_IN_SECONDS)
            minutes_left = max(1, int((reset_time - datetime.utcnow()).total_seconds() / 60))
            return minutes_left
        
        return 0

