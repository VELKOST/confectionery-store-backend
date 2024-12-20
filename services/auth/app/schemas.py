from pydantic import BaseModel, EmailStr, Field


class UserRegisterRequest(BaseModel):
    name: str = Field(..., example="Иван Иванов", description="Имя пользователя")
    email: EmailStr = Field(..., example="ivan@example.com", description="Электронная почта пользователя")
    password: str = Field(..., min_length=6, example="securepassword", description="Пароль пользователя")
    role: str = Field(..., example="user", description="Роль пользователя (user, admin, seller)")


class UserLoginRequest(BaseModel):
    email: EmailStr = Field(..., example="ivan@example.com", description="Электронная почта пользователя")
    password: str = Field(..., example="securepassword", description="Пароль пользователя")


class UserResponse(BaseModel):
    id: int = Field(..., example=1, description="Уникальный идентификатор пользователя")
    name: str = Field(..., example="Иван Иванов", description="Имя пользователя")
    email: EmailStr = Field(..., example="ivan@example.com", description="Электронная почта пользователя")
    role: str = Field(..., example="user", description="Роль пользователя")

    class Config:
        orm_mode = True


class AuthTokenResponse(BaseModel):
    token: str = Field(..., example="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...", description="JWT токен для аутентификации")


class RegisterResponse(BaseModel):
    message: str = Field(..., example="User registered successfully", description="Сообщение об успешной регистрации")
    token: str = Field(..., example="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...", description="JWT токен для аутентификации")
