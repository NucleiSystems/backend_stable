from datetime import datetime, timedelta

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt

from nuclei_backend.users import user_handler_utils

from .auth_utils import authenticate_user, create_access_token, get_current_user
from .Config import UsersConfig
from .main import users_router
from .user_models import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/user/token")


@users_router.post("/token")
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db=Depends(user_handler_utils.get_db),
):
    user = authenticate_user(
        username=form_data.username,
        password=form_data.password,
        db=db,
    )
    # if not user:
    #     raise HTTPException(
    #         status_code=status.HTTP_401_UNAUTHORIZED,
    #         detail="Incorrect username or password",
    #         headers={"WWW-Authenticate": "Bearer"},
    #     )
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": user.username},
        expire_delta=access_token_expires,
    )

    return {"access_token": access_token, "token_type": "bearer"}


@users_router.post("/token/check")
async def verify_token(token: str):
    try:
        token_data = jwt.decode(
            token, UsersConfig.SECRET_KEY, algorithms=[UsersConfig.ALGORITHM]
        )

        sub = token_data.get("sub")
        expiration_time = datetime.fromtimestamp(token_data["exp"])

        if expiration_time >= datetime.now():
            return {"token": f"expired: {expiration_time}", "sub": sub, "status": 401}

    except JWTError:
        raise HTTPException(
            status_code=401, detail="Invalid authentication credentials"
        )

    return {"status": "checked"}


@users_router.post("/token/refresh")
def refresh(
    db=Depends(user_handler_utils.get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        access_token_expires = timedelta(minutes=30)
        access_token = create_access_token(
            data={"sub": current_user.username}, expire_delta=access_token_expires
        )

    except Exception as e:
        return {"error": e, "status": 500}

    return {"access_token": access_token, "token_type": "bearer", "status": 200}
