from pydantic import BaseModel, ConfigDict, EmailStr


# ---------------------------------------------------------------------------
# Request models
# ---------------------------------------------------------------------------

class SignUpRequest(BaseModel):
    name: str
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


# ---------------------------------------------------------------------------
# Response models
# ---------------------------------------------------------------------------

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class UserProfile(BaseModel):
    id: int
    name: str
    email: str
    role: str

    model_config = ConfigDict(from_attributes=True)


class SignUpResponse(BaseModel):
    message: str
    user: UserProfile
    tokens: TokenResponse
