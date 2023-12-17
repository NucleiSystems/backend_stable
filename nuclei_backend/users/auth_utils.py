from datetime import datetime, timedelta, timezone

from typing import Dict, Literal, Union

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from pydantic import BaseModel
from starlette.config import Config
from authlib.integrations.starlette_client import OAuth
from typing import Optional

from fastapi import Depends, HTTPException, status
from jose import jwt
from authlib.integrations.starlette_client import OAuthError
from authlib.integrations.starlette_client import OAuth
from fastapi.security import OAuth2PasswordBearer
from fastapi import Request

from nuclei_backend.users import user_handler_utils

from .user_handler_utils import get_user_by_username

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/token")

from .Config import UsersConfig  # noqa: E402

GOOGLE_CLIENT_SECRET = "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"
GOOGLE_CLIENT_ID = (
    "1027503910283-dnt0gts6q65bfvp14b9cg279q9n3fi30.apps.googleusercontent.com"
)


# Set up oauth
config_data = {
    "GOOGLE_CLIENT_ID": GOOGLE_CLIENT_ID,
    "GOOGLE_CLIENT_SECRET": GOOGLE_CLIENT_SECRET,
}
starlette_config = Config(environ=config_data)

oauth = OAuth(starlette_config)

oauth.register(
    name="google",
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"},
)


class TokenData(BaseModel):
    username: str | None = None


class Token(BaseModel):
    access_token: str
    token_type: Literal["bearer"]


async def get_google_oauth_token(request: Request) -> dict:
    try:
        token = await oauth.google.authorize_access_token(request)
        return token
    except OAuthError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Google OAuth2 authentication failed",
        )


def create_access_token(
    data: dict,
    expire_delta: Optional[timedelta] = UsersConfig.ACCESS_TOKEN_EXPIRE_MINUTES,
) -> str:
    data_to_encode = data.copy()
    if expire_delta:
        expire = datetime.utcnow() + expire_delta
        data_to_encode.update({"exp": expire})
    return jwt.encode(
        data_to_encode, UsersConfig.SECRET_KEY, algorithm=UsersConfig.ALGORITHM
    )


def create_access_token(
    data: dict, expire_delta: Optional[int] = UsersConfig.ACCESS_TOKEN_EXPIRE_MINUTES
) -> str:
    data_to_encode = data.copy()
    if expire_delta:
        expire = datetime.utcnow() + expire_delta
        data_to_encode.update({"exp": expire})
    return jwt.encode(
        data_to_encode, UsersConfig.SECRET_KEY, algorithm=UsersConfig.ALGORITHM
    )


def authenticate_user(
    username: str,
    password: str,
    db: user_handler_utils.Session = Depends(user_handler_utils.get_db),
):
    if user := get_user_by_username(db, username=username):
        return (
            user
            if user_handler_utils.verify_password(password, user.hashed_password)
            else False
        )
    else:
        return False


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: user_handler_utils.Session = Depends(user_handler_utils.get_db),
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token, UsersConfig.SECRET_KEY, algorithms=[UsersConfig.ALGORITHM]
        )
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError as e:
        raise credentials_exception from e
    user = get_user_by_username(db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user
