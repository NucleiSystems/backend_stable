from fastapi import Depends, HTTPException
from nuclei_backend.users.user_models import AuthData, User
from . import user_handler_utils
from .auth_utils import *
from .main import users_router
import pyotp
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


@users_router.get("/has")
async def get_security_measures(
    user: User = Depends(get_current_user),
    db=Depends(user_handler_utils.get_db),
):
    has_measures = [
        has_pfp,
        has_totp,
        has_mail_otp,
        has_sms_otp,
    ]

    result = [result := check() for check in has_measures]

    return {"measures": result}


async def has_pfp(
    user: User = Depends(get_current_user),
    db=Depends(user_handler_utils.get_db),
):
    # Implement the logic for checking if user has a profile picture
    # Example: if user.profile_picture_url: return True
    return False


async def has_totp(
    user: User = Depends(get_current_user),
    db=Depends(user_handler_utils.get_db),
):
    auth_data = db.query(AuthData).filter(AuthData.user_id == user.id).first()
    if auth_data and auth_data.otp_secret_key:
        return True
    return False


async def has_mail_otp(
    user: User = Depends(get_current_user),
    db=Depends(user_handler_utils.get_db),
):
    # Implement the logic for checking if user has mail OTP enabled
    # Example: if user.auth_data.mail_otp_enabled: return True
    auth_data = db.query(AuthData).filter(AuthData.user_id == user.id).first()
    if auth_data and auth_data.mail_otp_enabled:
        return True
    return False


async def has_sms_otp(
    user: User = Depends(get_current_user),
    db=Depends(user_handler_utils.get_db),
):
    # Implement the logic for checking if user has SMS OTP enabled
    # Example: if user.auth_data.sms_otp_enabled: return True
    auth_data = db.query(AuthData).filter(AuthData.user_id == user.id).first()
    if auth_data and auth_data.sms_otp_enabled:
        return True
    return False


@users_router.get("/setup/sms_2fa")  # sends simple true or false
async def setup_sms_2fa(
    user: User = Depends(get_current_user),
    db=Depends(user_handler_utils.get_db),
):
    # Implement the logic for setting up SMS 2FA
    # Example: user.auth_data.sms_otp_enabled = True; db.commit()
    return {"status": "success"}


@users_router.get("/setup/motp")  # sends simple true or false
async def setup_motp(
    user: User = Depends(get_current_user),
    db=Depends(user_handler_utils.get_db),
):
    # Implement the logic for setting up mail OTP
    # Example: user.auth_data.mail_otp_enabled = True; db.commit()
    return {"status": "success"}


@users_router.get("/setup/pfp")  # sends simple true or false
async def setup_pfp(
    user: User = Depends(get_current_user),
    db=Depends(user_handler_utils.get_db),
):
    # Implement the logic for setting up profile picture
    # Example: user.profile_picture_url = request.url; db.commit()
    return {"status": "success"}


@users_router.post("/setup/totp", response_model=dict)
def setup_otp(
    db=Depends(user_handler_utils.get_db),
    current_user: User = Depends(get_current_user),
):
    auth_data = db.query(AuthData).filter(AuthData.user_id == current_user.id).first()
    if auth_data and auth_data.otp_secret_key:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="OTP is already set up"
        )

    # Generate OTP secret key
    totp = pyotp.TOTP()
    otp_secret_key = totp.secret

    # Save the OTP secret key for the user
    auth_data = AuthData(otp_secret_key=otp_secret_key, user=current_user)
    db.add(auth_data)
    db.commit()
    db.refresh(auth_data)

    # Generate QR code
    uri = totp.provisioning_uri(
        name=current_user.username, issuer_name="Nuclei-Systems"
    )
    img = qrcode.make(uri)
    img_byte_array = BytesIO()
    img.save(img_byte_array, format="PNG")
    img_byte_array = img_byte_array.getvalue()

    return JSONResponse(
        content={"provisioning_uri": uri, "qr_code": img_byte_array.decode("utf-8")},
        media_type="application/json",
    )


def get_user_by_otp_token(db, otp_token: str) -> User:
    auth_data = db.query(AuthData).filter(AuthData.otp_secret_key == otp_token).first()
    if auth_data and auth_data.user:
        return auth_data.user
    else:
        return None


@users_router.post("/verify/totp", response_model=dict)
def verify_otp(
    token: str,
    db=Depends(user_handler_utils.get_db),
):
    # Fetch user with the provided OTP secret key
    user = user_handler_utils.get_user_by_otp_token(db, otp_token=token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid OTP",
        )

    # Generate access token for the user
    access_token = create_access_token(
        data={"sub": user.username},
        expire_delta=timedelta(minutes=30),
    )

    return {
        "status": "OTP verified successfully",
        "access_token": access_token,
        "token_type": "bearer",
    }
