from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models import User
from backend.schemas import (
    UserRegisterRequest,
    UserLoginRequest,
    TokenResponse,
    UserOut,
    UserProfileUpdate,
)
from backend.dependencies import get_current_user
from backend.services.auth_service import register_user, authenticate_user

router = APIRouter(prefix="/auth", tags=["Authentication & Users"])


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(req: UserRegisterRequest, db: Session = Depends(get_db)):
    """Register a new user account (Buyer or Seller)."""
    return register_user(db, req)


@router.post("/login", response_model=TokenResponse)
def login(req: UserLoginRequest, db: Session = Depends(get_db)):
    """Authenticate with username/email and password to receive a JWT access token."""
    return authenticate_user(db, req)


@router.get("/me", response_model=UserOut)
def get_current_user_profile(current_user: User = Depends(get_current_user)):
    """Retrieve profile and role information of currently authenticated user."""
    return current_user


@router.put("/me", response_model=UserOut)
def update_profile(
    req: UserProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update profile details of currently authenticated user."""
    if req.full_name is not None:
        current_user.full_name = req.full_name
    if req.phone is not None:
        current_user.phone = req.phone
    if req.address is not None:
        current_user.address = req.address
    db.commit()
    db.refresh(current_user)
    return current_user
