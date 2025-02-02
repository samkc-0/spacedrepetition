from datetime import datetime, timedelta, timezone
from dotenv import dotenv_values
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
import jwt
from pydantic import BaseModel
from sqlmodel import Session, select
from sqlalchemy.exc import NoResultFound
from typing import Literal, Optional


from models import User
from db import engine, get_session
from password import verify_password

config = dotenv_values(".env")

SECRET_KEY = config["JWT_SECRET_KEY"]
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRES_MINUTES = 30
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/token")


class Token(BaseModel):
    access_token: str
    token_type: Literal["bearer"]


class TokenData(BaseModel):
    username: str


def get_user(username: str, session: Session) -> Optional[User]:
    try:
        user = session.exec(select(User).where(User.username == username)).one()
        return user
    except NoResultFound:
        return None


def authenticate_user(username: str, password: str, session: Session) -> bool | User:
    user = get_user(username, session)
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt: str = jwt.encode(to_encode, SECRET_KEY, algorithm=JWT_ALGORITHM)
    return encoded_jwt


def get_current_user(
    token: str = Depends(oauth2_scheme), session: Session = Depends(get_session)
) -> Optional[User]:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[JWT_ALGORITHM])
        username: str | None = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except jwt.InvalidTokenError:
        raise credentials_exception
    user = get_user(token_data.username, session)
    if user is None:
        raise credentials_exception
    return user


def get_current_user_cookie(
    request: Request, session: Session = Depends(get_session)
) -> Optional[User]:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    token = request.cookies.get("Authorization")
    if not token:
        raise credentials_exception
    token = token.replace("Bearer ", "")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[JWT_ALGORITHM])
        username: str | None = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except jwt.InvalidTokenError:
        raise credentials_exception
    user = get_user(token_data.username, session)
    if user is None:
        raise credentials_exception
    return user
