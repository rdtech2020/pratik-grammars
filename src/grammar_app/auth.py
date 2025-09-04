"""
Authentication Module

This module handles JWT token creation, validation, and user authentication.
"""

from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from config.settings import settings

from .crud import get_user_by_email
from .database import get_db

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT token scheme
security = HTTPBearer()


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def create_user_token(user_id: int, expires_delta: Optional[timedelta] = None):
    """Create JWT access token for user (secure - uses ID instead of email)."""
    now = datetime.utcnow()
    
    # Enhanced JWT payload with security claims
    to_encode = {
        "sub": str(user_id),  # Subject (user ID)
        "iat": now,  # Issued at
        "iss": settings.JWT_ISSUER,  # Issuer
        "aud": settings.JWT_AUDIENCE,  # Audience
        "type": "access",  # Token type
        "jti": f"token_{user_id}_{int(now.timestamp())}"  # Unique token ID
    }
    
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    
    # Encode with enhanced security
    encoded_jwt = jwt.encode(
        to_encode, 
        settings.SECRET_KEY, 
        algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def verify_token(token: str) -> Optional[dict]:
    """Verify JWT token and return payload with enhanced security checks."""
    try:
        # Decode with audience and issuer verification
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM],
            audience=settings.JWT_AUDIENCE,
            issuer=settings.JWT_ISSUER
        )
        
        # Additional security checks
        user_id: str = payload.get("sub")
        token_type: str = payload.get("type")
        
        if user_id is None:
            print("❌ JWT Security: Missing subject claim")
            return None
            
        if token_type != "access":
            print("❌ JWT Security: Invalid token type")
            return None
            
        # Check if token is in blacklist (future implementation)
        # if is_token_blacklisted(payload.get("jti")):
        #     return None
            
        return payload
        
    except JWTError as e:
        print(f"❌ JWT Security: Token verification failed - {e}")
        return None


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    """Get current authenticated user from JWT token with enhanced security."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        token = credentials.credentials
        payload = verify_token(token)
        if payload is None:
            raise credentials_exception

        user_id: str = payload.get("sub")
        jti: str = payload.get("jti")
        
        if user_id is None:
            raise credentials_exception

        # Check if token is blacklisted
        from .crud import is_token_blacklisted
        if is_token_blacklisted(db, jti):
            print(f"❌ JWT Security: Token {jti} is blacklisted")
            raise credentials_exception

        # Get user by ID
        from .crud import get_user
        user = get_user(db, user_id=int(user_id))
        if user is None:
            raise credentials_exception

        return user
    except JWTError:
        raise credentials_exception


def get_current_active_user(current_user=Depends(get_current_user)):
    """Get current active user (for future use if we add user status)."""
    return current_user


def get_current_admin_user(current_user=Depends(get_current_user)):
    """Get current user only if they have admin role."""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required"
        )
    return current_user


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


def authenticate_user(email: str, password: str, db: Session):
    """Authenticate user with email and password."""
    user = get_user_by_email(db, email=email)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user
