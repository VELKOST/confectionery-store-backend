import os
from datetime import datetime, timedelta, UTC
from jose import jwt, JWTError
from passlib.hash import bcrypt
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

JWT_SECRET = os.getenv("JWT_SECRET_KEY")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM")
JWT_EXPIRE_SECONDS = 3600

oauth2_scheme = HTTPBearer()


def hash_password(password: str) -> str:
    return bcrypt.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.verify(plain_password, hashed_password)


def create_access_token(email: str, role: str, user_id: int) -> str:
    expire = datetime.now(UTC) + timedelta(seconds=JWT_EXPIRE_SECONDS)
    to_encode = {
        "sub": email,
        "exp": expire,
        "role": role,
        "user_id": user_id
    }
    return jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)


def get_current_user_token(token: HTTPAuthorizationCredentials = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token.credentials, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        return {"email": email, "role": payload.get("role"), "user_id": payload.get("user_id")}
    except JWTError:
        raise credentials_exception
