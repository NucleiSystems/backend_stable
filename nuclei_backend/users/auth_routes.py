from datetime import timedelta, datetime

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from nuclei_backend.users import user_handler_utils
from jose import JWTError, jwt

from .auth_utils import authenticate_user, create_access_token, get_current_user
from .main import users_router
from .user_models import User, AuthData
from .Config import UsersConfig

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/user/token")


from fastapi.responses import JSONResponse
import pyotp
import qrcode
from io import BytesIO


@users_router.post("/register")
def create_user(
    user: user_handler_utils.user_schemas.UserCreate = Depends(),
    db: user_handler_utils.Session = Depends(user_handler_utils.get_db),
):
    print(user)

    if db_user := user_handler_utils.get_user_by_username(db, username=user.username):
        return {
            "status_code": 400,
            "detail": "User with this email already exists",
            "user": db_user,
        }

    try:
        db_user = user_handler_utils.create_user(db=db, user=user)
        otp_secret_key = pyotp.random_base32()
        user_handler_utils.create_auth_data(
            db=db, user_id=db_user.id, otp_secret_key=otp_secret_key
        )

        return {"status_code": 200, "detail": "User created successfully"}
    except Exception as e:
        return {"status_code": 400, "detail": str(e)}


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
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(
        data={"sub": user.username},
        expire_delta=timedelta(minutes=30),
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
def login_for_access_token(
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
