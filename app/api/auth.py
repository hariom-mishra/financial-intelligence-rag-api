from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from core.db import get_db
from core.security import get_current_user
from core.exceptions import UserAlreadyExistsError, InvalidCredentialsError
from repo.user_repo import get_user_by_email, create_user
from services.auth_service import hash_password, verify_password, create_access_token, create_refresh_token
from services.qdrant_services import create_user_collection
from model.users import SignUpRequest, LoginRequest, TokenResponse, UserProfile, SignUpResponse
from schema.users import Users

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/signup", response_model=SignUpResponse, status_code=201)
async def signup(payload: SignUpRequest, db: AsyncSession = Depends(get_db)):
    """
    Register a new user.
    - Checks for duplicate email.
    - Hashes the password with bcrypt.
    - Persists the user in PostgreSQL.
    - Pre-creates a dedicated Qdrant vector collection for this user.
    - Returns JWT access + refresh tokens.
    """
    # 1. Check for duplicate email
    existing = await get_user_by_email(db, payload.email)
    if existing:
        raise UserAlreadyExistsError(payload.email)

    # 2. Hash password and persist user
    hashed = hash_password(payload.password)
    user = await create_user(
        db=db,
        name=payload.name,
        email=payload.email,
        hashed_password=hashed,
    )

    # 3. Pre-create the user's Qdrant vector collection
    await create_user_collection(user.id)

    # 4. Issue tokens  (sub = str(user_id) — standard JWT convention)
    token_data = {"sub": str(user.id)}
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)

    return SignUpResponse(
        message="Account created successfully.",
        user=UserProfile.model_validate(user),
        tokens=TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
        ),
    )


@router.post("/login", response_model=TokenResponse)
async def login(payload: LoginRequest, db: AsyncSession = Depends(get_db)):
    """
    Authenticate an existing user and return JWT tokens.
    Uses constant-time bcrypt comparison to prevent timing attacks.
    """
    user = await get_user_by_email(db, payload.email)
    if not user or not verify_password(payload.password, user.hashed_password):
        raise InvalidCredentialsError()

    token_data = {"sub": str(user.id)}
    return TokenResponse(
        access_token=create_access_token(token_data),
        refresh_token=create_refresh_token(token_data),
    )


@router.get("/me", response_model=UserProfile)
async def get_me(current_user: Users = Depends(get_current_user)):
    """Return the authenticated user's profile."""
    return UserProfile.model_validate(current_user)
