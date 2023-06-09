from fastapi import Depends, HTTPException

from . import user_handler_utils
from .auth_utils import *  # noqa: F403
from .main import users_router


@users_router.post("/register", response_model=user_handler_utils.user_schemas.User)
def create_user(
    user: user_handler_utils.user_schemas.UserCreate,
    db: user_handler_utils.Session = Depends(user_handler_utils.get_db),
):
    if db_user := user_handler_utils.get_user_by_username(
        db, username=user.username
    ):  
        return {
            "status_code" : 400, 
            "detail" : "User with this email already exists",
        }
    
    return user_handler_utils.create_user(db=db, user=user)
