from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr, Field, validator
from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta
from app.database import get_user_by_email, create_user
from app.config import settings

router = APIRouter()

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# Helper functions for password hashing
def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    # Ensure password is within bcrypt's 72-byte limit
    if len(password.encode('utf-8')) > 72:
        raise ValueError("Password is too long")
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)


# Pydantic models
class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserSignup(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=72)
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) > 72:
            raise ValueError('Password must be 72 characters or less')
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        return v


class Token(BaseModel):
    access_token: str
    token_type: str
    user: dict


def create_access_token(data: dict) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


@router.post("/auth/signup", response_model=Token)
async def signup(user_data: UserSignup):
    """
    Create new user account
    
    - Validates email is unique
    - Hashes password
    - Creates user with free tier
    - Returns JWT token
    """
    
    # Check if user already exists
    existing_user = await get_user_by_email(user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )
    
    # Hash password (validation already done by Pydantic)
    try:
        hashed_password = hash_password(user_data.password)
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    
    # Create user
    user = await create_user(user_data.email, hashed_password)
    
    if not user:
        raise HTTPException(
            status_code=500,
            detail="Failed to create user"
        )
    
    # Create access token
    access_token = create_access_token(
        data={"sub": user["email"], "user_id": user["id"]}
    )
    
    # Return token and user info
    return Token(
        access_token=access_token,
        token_type="bearer",
        user={
            "id": user["id"],
            "email": user["email"],
            "subscription_tier": user.get("subscription_tier", "free"),
            "credits_remaining": user.get("credits_remaining", 10)
        }
    )


@router.post("/auth/login", response_model=Token)
async def login(user_data: UserLogin):
    """
    Login user
    
    - Validates credentials
    - Returns JWT token
    """
    
    # Get user by email
    user = await get_user_by_email(user_data.email)
    
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )
    
    # Verify password
    if not verify_password(user_data.password, user.get("password_hash", "")):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )
    
    # Create access token
    access_token = create_access_token(
        data={"sub": user["email"], "user_id": user["id"]}
    )
    
    # Return token and user info
    return Token(
        access_token=access_token,
        token_type="bearer",
        user={
            "id": user["id"],
            "email": user["email"],
            "subscription_tier": user.get("subscription_tier", "free"),
            "credits_remaining": user.get("credits_remaining", 10)
        }
    )