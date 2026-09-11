from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.database.models import User
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

    existing_user = (
        db.query(User)
        .filter(
            User.username == request.username
        )
        .first()
    )

    if existing_user:

        raise HTTPException(
            status_code=400,
            detail="Username already exists."
        )

    if len(request.username.strip()) < 3:

        raise HTTPException(
            status_code=400,
            detail="Username must contain at least 3 characters."
        )

    if len(request.password) < 6:

        raise HTTPException(
            status_code=400,
            detail="Password must contain at least 6 characters."
        )

    auth_service = AuthService()

    password_hash = (
        auth_service.hash_password(
            request.password
        )
    )

    user = User(
        username=request.username.strip(),
        password_hash=password_hash
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    access_token = (
        auth_service.create_access_token(
            user.username
        )
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

    user = (
        db.query(User)
        .filter(
            User.username == request.username.strip()
        )
        .first()
    )

    if not user:

        raise HTTPException(
            status_code=401,
            detail="Invalid username or password."
        )

    auth_service = AuthService()

    password_valid = (
        auth_service.verify_password(
            request.password,
            user.password_hash
        )
    )

    if not password_valid:

        raise HTTPException(
            status_code=401,
            detail="Invalid username or password."
        )

    access_token = (
        auth_service.create_access_token(
            user.username
        )
    )

    return AuthResponse(
        message="Login successful.",
        access_token=access_token,
        token_type="bearer"
    )