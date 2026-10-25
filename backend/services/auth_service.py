import os
from sqlalchemy.orm import Session
from sqlalchemy import or_
from fastapi import HTTPException, status
from backend.models import User, UserRole
from backend.schemas import UserRegisterRequest, UserLoginRequest, TokenResponse
from backend.dependencies import hash_password, verify_password, create_access_token


def bootstrap_default_admin(db: Session) -> User:
    """Ensures a default administrator account exists on startup without plaintext passwords."""
    admin_email = os.getenv("ADMIN_EMAIL", "admin@bidsphere.com")
    admin_username = os.getenv("ADMIN_USERNAME", "admin")
    admin_full_name = os.getenv("ADMIN_FULL_NAME", "System Administrator")
    admin_initial_password = os.getenv("ADMIN_INITIAL_PASSWORD", "Admin@BidSphere2026!")

    existing_admin = db.query(User).filter(
        or_(User.email == admin_email, User.username == admin_username)
    ).first()

    if not existing_admin:
        admin_user = User(
            username=admin_username,
            email=admin_email,
            password_hash=hash_password(admin_initial_password),
            full_name=admin_full_name,
            role=UserRole.ADMIN,
            phone="+91-9876543210",
            address="BidSphere Headquarters, Bangalore",
            is_active=True,
        )
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        return admin_user
    return existing_admin


def register_user(db: Session, req: UserRegisterRequest) -> User:
    """Registers a new user after verifying unique username and email."""
    # Check duplicate username
    if db.query(User).filter(User.username == req.username).first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Username '{req.username}' is already taken. Please choose another.",
        )
    # Check duplicate email
    if db.query(User).filter(User.email == req.email).first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Email address '{req.email}' is already registered.",
        )

    # Disallow self-registering as ADMIN
    assigned_role = req.role
    if assigned_role == UserRole.ADMIN:
        assigned_role = UserRole.BUYER

    new_user = User(
        username=req.username,
        email=req.email,
        password_hash=hash_password(req.password),
        full_name=req.full_name,
        role=assigned_role,
        phone=req.phone,
        address=req.address,
        is_active=True,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


def authenticate_user(db: Session, req: UserLoginRequest) -> TokenResponse:
    """Authenticates user by username/email and password, returning JWT."""
    identifier = req.username_or_email.strip()
    user = db.query(User).filter(
        or_(User.username == identifier, User.email == identifier)
    ).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials. Check your username/email and password.",
        )

    if not verify_password(req.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials. Check your username/email and password.",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated. Please contact support.",
        )

    token = create_access_token(
        data={"sub": str(user.user_id), "username": user.username, "role": user.role.value}
    )

    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user_id=user.user_id,
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        role=user.role,
    )
