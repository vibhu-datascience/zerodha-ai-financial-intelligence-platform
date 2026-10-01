from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.database.models import User, Portfolio
from app.schemas.auth import (
    RegisterRequest,
    LoginRequest,
    AuthResponse
)
from app.services.auth_service import AuthService


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


@router.post(
    "/register",
    response_model=AuthResponse
)
def register(
    request: RegisterRequest,
    db: Session = Depends(get_db)
):
    username = request.username.strip()

    # -----------------------------
    # Validate username
    # -----------------------------
    if len(username) < 3:
        raise HTTPException(
            status_code=400,
            detail="Username must contain at least 3 characters."
        )

    # -----------------------------
    # Validate password
    # -----------------------------
    if len(request.password) < 6:
        raise HTTPException(
            status_code=400,
            detail="Password must contain at least 6 characters."
        )

    # -----------------------------
    # Check existing user
    # -----------------------------
    existing_user = (
        db.query(User)
        .filter(User.username == username)
        .first()
    )

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Username already exists."
        )

    # -----------------------------
    # Create password hash
    # -----------------------------
    auth_service = AuthService()

    password_hash = auth_service.hash_password(
        request.password
    )

    # -----------------------------
    # Create user
    # -----------------------------
    user = User(
        username=username,
        password_hash=password_hash
    )

    db.add(user)
    db.flush()

    # -----------------------------
    # Create default portfolio
    # -----------------------------
    portfolio = Portfolio(
        user_id=user.id,
        name="Growth Portfolio"
    )

    db.add(portfolio)

    # Commit user + portfolio together
    db.commit()

    db.refresh(user)

    # -----------------------------
    # Create JWT
    # -----------------------------
    access_token = auth_service.create_access_token(
        user.id,
        user.username
    )

    return AuthResponse(
        message="Registration successful.",
        access_token=access_token,
        token_type="bearer"
    )


@router.post(
    "/login",
    response_model=AuthResponse
)
def login(
    request: LoginRequest,
    db: Session = Depends(get_db)
):
    username = request.username.strip()

    # -----------------------------
    # Find user
    # -----------------------------
    user = (
        db.query(User)
        .filter(User.username == username)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password."
        )

    # -----------------------------
    # Verify password
    # -----------------------------
    auth_service = AuthService()

    password_valid = auth_service.verify_password(
        request.password,
        user.password_hash
    )

    if not password_valid:
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password."
        )

    # -----------------------------
    # Create JWT
    # -----------------------------
    access_token = auth_service.create_access_token(
        user.id,
        user.username
    )

    return AuthResponse(
        message="Login successful.",
        access_token=access_token,
        token_type="bearer"
    )
