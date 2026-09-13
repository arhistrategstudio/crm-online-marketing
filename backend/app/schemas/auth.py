from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, computed_field


class SignupRequest(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    email: EmailStr
    password: str = Field(min_length=8, max_length=255)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=255)


class GoogleAuthRequest(BaseModel):
    id_token: str


class ChangePasswordRequest(BaseModel):
    current_password: str | None = None
    new_password: str = Field(min_length=8, max_length=255)


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: str
    role: str
    status: str
    auth_provider: str
    password_hash: str | None = Field(default=None, exclude=True)
    created_at: datetime

    @computed_field
    @property
    def has_password(self) -> bool:
        return self.password_hash is not None


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserRead
