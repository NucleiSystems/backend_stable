from sqlalchemy import Boolean, Column, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid
from ..database import Base

from pydantic import BaseModel


class AuthData(Base):
    __tablename__ = "auth_data"

    id = Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    otp_secret_key = Column(String, unique=True, index=True)
    mail_otp_enabled = Column(Boolean, default=False)
    sms_otp_enabled = Column(Boolean, default=False)

    user = relationship("User", back_populates="auth_data")


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)

    auth_data = relationship("AuthData", back_populates="user")
    data = relationship("DataStorage", back_populates="owner")


class UserCreate(BaseModel):
    email: str
    username: str
    password: str
    otp_secret_key: str  # New field for OTP secret key


class UserData(BaseModel):
    email: str
    username: str
    is_active: bool
    otp_enabled: bool  # New field to indicate whether OTP is enabled


class UserInDB(UserData):
    hashed_password: str


class AuthDataCreate(BaseModel):
    otp_secret_key: str
