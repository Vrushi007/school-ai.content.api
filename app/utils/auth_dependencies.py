"""
Authentication dependencies for securing API endpoints.
This module provides FastAPI dependency functions to verify JWT tokens.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from typing import Dict, Any
import os
from dotenv import load_dotenv

load_dotenv()

security = HTTPBearer()

# These should match your auth service settings
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
SECRET_KEY = os.getenv("JWT_SECRET_KEY")

if not SECRET_KEY:
    raise ValueError("JWT_SECRET_KEY must be set in environment variables")


async def verify_token(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Dict[str, Any]:
    """
    Verify JWT token and extract payload.
    
    This is a lightweight verification that only validates the token signature
    and expiry. It does NOT check session revocation status in the database.
    
    Args:
        credentials: HTTP Bearer token credentials
        
    Returns:
        Dict containing token payload (user_id, jti, etc.)
        
    Raises:
        HTTPException: If token is invalid or expired
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # Verify token type
        if payload.get("type") != "access":
            raise credentials_exception
        
        # Extract user_id and jti
        sub = payload.get("sub")
        try:
            user_id = int(sub) if sub is not None else None
        except (TypeError, ValueError):
            user_id = None
            
        jti: str = payload.get("jti")
        
        if user_id is None or jti is None:
            raise credentials_exception
            
        return {
            "user_id": user_id,
            "jti": jti,
            "payload": payload
        }
        
    except JWTError:
        raise credentials_exception
    except Exception:
        raise credentials_exception


async def get_current_user_id(
    token_data: Dict[str, Any] = Depends(verify_token)
) -> int:
    """
    Extract and return the current user ID from the verified token.
    
    Use this dependency when you need the user ID for your endpoint.
    
    Example:
        @app.post("/lesson-plans")
        async def create_lesson_plan(
            data: LessonPlanCreate,
            user_id: int = Depends(get_current_user_id)
        ):
            # Your endpoint logic here
            # You can use user_id to associate data with the teacher
            lesson_plan = LessonPlan(
                title=data.title,
                user_id=user_id,  # Store which teacher created it
                ...
            )
            pass
    """
    return token_data["user_id"]


async def get_current_token(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> str:
    """
    Extract and return the raw JWT token string.
    
    Use this dependency when you need to pass the token to other services.
    
    Example:
        @app.post("/lesson-plans")
        async def create_lesson_plan(
            data: LessonPlanCreate,
            token: str = Depends(get_current_token)
        ):
            # Pass token to external service
            await external_service.call_api(data, token=token)
    """
    # First verify the token is valid
    await verify_token(credentials)
    # Return the raw token string
    return credentials.credentials


async def get_token_payload(
    token_data: Dict[str, Any] = Depends(verify_token)
) -> Dict[str, Any]:
    """
    Get the full token payload.
    
    Use this if you need access to additional token data beyond just user_id.
    """
    return token_data["payload"]


async def require_authentication(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> bool:
    """
    Simple dependency to require authentication without extracting user data.
    Returns True if token is valid.
    
    Use this when you just need to ensure the endpoint is protected
    but don't need the user information.
    
    Example:
        @app.get("/boards")
        async def get_boards(auth: bool = Depends(require_authentication)):
            return boards
    """
    await verify_token(credentials)
    return True
