from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from .db import get_db
from .models import User
from .schemas import (
    UserRegisterRequest,
    UserLoginRequest,
    UserResponse,
    AuthTokenResponse,
    RegisterResponse
)
from .security import hash_password, verify_password, create_access_token, get_current_user_token
from .email_sender import send_email

router = APIRouter()


@router.post(
    "/register",
    response_model=RegisterResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Регистрация нового пользователя",
    description="Позволяет новому пользователю зарегистрироваться в системе и отправляет приветственное письмо."
)
async def register_user(
    user_data: UserRegisterRequest,
    db: Session = Depends(get_db)
):
    """
    Эндпоинт для регистрации нового пользователя.

    - **name**: Имя пользователя
    - **email**: Электронная почта пользователя
    - **password**: Пароль пользователя
    - **role**: Роль пользователя (user, admin, seller)
    """
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this email already exists"
        )

    if user_data.role not in ["user", "admin", "seller"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid role"
        )

    new_user = User(
        name=user_data.name,
        email=user_data.email,
        password_hash=hash_password(user_data.password),
        role=user_data.role
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    token = create_access_token(new_user.email, new_user.role, new_user.id)

    # Отправка приветственного письма
    subject = "Добро пожаловать в наш интернет-магазин!"
    html_content = f"""
        <html>
            <body>
                <p>Здравствуйте, {new_user.name}!</p>
                <p>Спасибо за регистрацию в нашем интернет-магазине кондитерских изделий.</p>
                <p>Вы можете использовать следующий токен для аутентификации:</p>
                <p><strong>{token}</strong></p>
                <p>С уважением,<br>Команда интернет-магазина</p>
            </body>
        </html>
        """

    try:
        await send_email(to_email=new_user.email, subject=subject, html_content=html_content)
    except Exception as e:
        # Логирование ошибки отправки email
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send welcome email"
        )

    return RegisterResponse(
        message="User registered successfully",
        token=token
    )


@router.post(
    "/login",
    response_model=AuthTokenResponse,
    summary="Вход пользователя",
    description="Позволяет пользователю войти в систему, предоставляя JWT токен."
)
def login_user(
    login_data: UserLoginRequest,
    db: Session = Depends(get_db)
):
    """
    Эндпоинт для входа пользователя.

    - **email**: Электронная почта пользователя
    - **password**: Пароль пользователя
    """
    user = db.query(User).filter(User.email == login_data.email).first()
    if not user or not verify_password(login_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    token = create_access_token(user.email, user.role, user.id)
    return AuthTokenResponse(token=token)


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Получить текущего пользователя",
    description="Возвращает информацию о текущем аутентифицированном пользователе."
)
def get_me(
    user_token=Depends(get_current_user_token),
    db: Session = Depends(get_db)
):
    """
    Эндпоинт для получения информации о текущем пользователе.

    - **Authorization**: Bearer токен
    """
    user = db.query(User).filter(User.email == user_token["email"]).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    return user




@router.get(
    "/users",
    response_model=List[UserResponse],
    summary="Получить всех пользователей",
    description="Возвращает список всех пользователей системы.",
)
def get_all_users(
    db: Session = Depends(get_db),
    user_token: dict = Depends(get_current_user_token),
):
    """
    Эндпоинт для получения всех пользователей.

    - **Authorization**: Bearer токен (только для администраторов)
    """
    if user_token["role"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to view all users",
        )

    users = db.query(User).all()
    return users
