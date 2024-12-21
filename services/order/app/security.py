import os
from jose import jwt, JWTError
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import logging

JWT_SECRET = os.getenv("JWT_SECRET_KEY")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM")

oauth2_scheme = HTTPBearer()
logger = logging.getLogger(__name__)


def get_current_user_token(token: HTTPAuthorizationCredentials = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token.credentials, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        email: str = payload.get("sub")
        role: str = payload.get("role")
        user_id: int = payload.get("user_id")

        logger.debug(f"Decoded token payload: {payload}")  # Логируем payload для отладки

        if email is None or role is None or user_id is None:
            raise credentials_exception
        return {"email": email, "role": role, "user_id": user_id}
    except JWTError as e:
        logger.error(f"JWT decode error: {str(e)}")  # Логируем ошибку декодирования
        raise credentials_exception
