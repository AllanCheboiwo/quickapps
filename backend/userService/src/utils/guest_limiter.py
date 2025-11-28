"""
Guest mode rate limiter and utility functions
"""
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func
from src.models.users import User
from src.models.generated_resumes import GeneratedResume


class GuestLimiter:
    """Rate limiter for guest users"""
    
    MAX_RESUMES_PER_DAY = 1
    MAX_PROFILES = 1
    GUEST_EXPIRY_DAYS = 7
    
    @staticmethod
    def is_guest_expired(user: User) -> bool:
        """Check if guest user session has expired"""
        if not user.is_guest:
            return False
        if user.guest_expires_at is None:
            return True
        return datetime.utcnow() > user.guest_expires_at
    
    @staticmethod
    def can_generate_resume(user: User, db: Session) -> tuple[bool, str]:
        """
        Check if user can generate a resume
        Returns: (can_generate: bool, message: str)
        """
        if not user.is_guest:
            return True, ""
        
        # Check if guest has expired
        if GuestLimiter.is_guest_expired(user):
            return False, "Guest session expired. Please create an account to continue."
        
        # Check daily limit
        today = datetime.utcnow().date()
        resume_count = db.query(GeneratedResume).filter(
            GeneratedResume.user_id == user.id,
            func.date(GeneratedResume.created_at) == today
        ).count()
        
        if resume_count >= GuestLimiter.MAX_RESUMES_PER_DAY:
            return False, f"Guest limit reached ({GuestLimiter.MAX_RESUMES_PER_DAY} resume/day). Sign up for unlimited!"
        
        return True, ""
    
    @staticmethod
    def can_create_profile(user: User, db: Session) -> tuple[bool, str]:
        """
        Check if user can create a profile
        Returns: (can_create: bool, message: str)
        """
        if not user.is_guest:
            return True, ""
        
        # Check if guest has expired
        if GuestLimiter.is_guest_expired(user):
            return False, "Guest session expired. Please create an account to continue."
        
        # Check profile limit
        profile_count = db.query(func.count("*")).select_from(
            __import__('src.models.profiles', fromlist=['Profile']).Profile
        ).filter(
            __import__('src.models.profiles', fromlist=['Profile']).Profile.user_id == user.id
        ).scalar()
        
        if profile_count >= GuestLimiter.MAX_PROFILES:
            return False, f"Guest limit reached ({GuestLimiter.MAX_PROFILES} profile max). Sign up for unlimited!"
        
        return True, ""
    
    @staticmethod
    def get_guest_info(user: User) -> dict:
        """Get guest user info and remaining limits"""
        if not user.is_guest:
            return {}
        
        days_remaining = 0
        if user.guest_expires_at:
            days_remaining = max(0, (user.guest_expires_at - datetime.utcnow()).days)
        
        return {
            "is_guest": True,
            "expires_at": user.guest_expires_at,
            "days_remaining": days_remaining,
            "max_profiles": GuestLimiter.MAX_PROFILES,
            "max_resumes_per_day": GuestLimiter.MAX_RESUMES_PER_DAY,
        }

