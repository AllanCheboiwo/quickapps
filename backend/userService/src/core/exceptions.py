from fastapi import HTTPException, status


class AppException(HTTPException):
    """Base application exception"""
    def __init__(self, detail: str, status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR):
        super().__init__(status_code=status_code, detail=detail)


class ValidationException(AppException):
    """Validation error"""
    def __init__(self, detail: str):
        super().__init__(detail=detail, status_code=status.HTTP_400_BAD_REQUEST)


class UnauthorizedException(AppException):
    """Authentication/Authorization error"""
    def __init__(self, detail: str = "Unauthorized"):
        super().__init__(detail=detail, status_code=status.HTTP_401_UNAUTHORIZED)


class NotFoundException(AppException):
    """Resource not found"""
    def __init__(self, resource: str = "Resource"):
        super().__init__(detail=f"{resource} not found", status_code=status.HTTP_404_NOT_FOUND)


class ConflictException(AppException):
    """Resource conflict (e.g., duplicate)"""
    def __init__(self, detail: str):
        super().__init__(detail=detail, status_code=status.HTTP_409_CONFLICT)


class ForbiddenException(AppException):
    """Access forbidden"""
    def __init__(self, detail: str = "Access forbidden"):
        super().__init__(detail=detail, status_code=status.HTTP_403_FORBIDDEN)


class InternalServerException(AppException):
    """Internal server error"""
    def __init__(self, detail: str = "Internal server error"):
        super().__init__(detail=detail, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ServiceUnavailableException(AppException):
    """Service unavailable"""
    def __init__(self, detail: str = "Service temporarily unavailable"):
        super().__init__(detail=detail, status_code=status.HTTP_503_SERVICE_UNAVAILABLE)


class RateLimitExceeded(AppException):
    """Rate limit exceeded - too many requests"""
    def __init__(self, detail: str = "Rate limit exceeded. Please try again later."):
        super().__init__(detail=detail, status_code=status.HTTP_429_TOO_MANY_REQUESTS)
