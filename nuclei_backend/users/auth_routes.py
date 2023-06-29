from datetime import timedelta, datetime

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from nuclei_backend.users import user_handler_utils
from jose import JWTError, jwt

from .auth_utils import authenticate_user, create_access_token, get_current_user
from .main import users_router
from .user_models import User
from .Config import UsersConfig

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/user/token")


@users_router.post("/token")
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db=Depends(user_handler_utils.get_db),
):
    """
    This function handles user authentication and generates an access token for the user to access
    protected routes.

    :param form_data: The form data is the data submitted by the user in the login form, which includes
    the username and password
    :type form_data: OAuth2PasswordRequestForm
    :param db: The `db` parameter is a dependency that is used to get a database connection object. It
    is passed to the function using the `Depends()` function from the `fastapi` library. The `get_db`
    function from the `user_handler_utils` module is used to get the database connection
    :return: A dictionary containing an access token and token type.
    """
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
