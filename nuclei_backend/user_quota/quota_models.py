from sqlalchemy import Column, ForeignKey, Integer, String, DateTime

from sqlalchemy.orm import relationship
from ..database import Base
from sqlalchemy.dialects.postgresql import UUID


class UserQuota(Base):
    __tablename__ = "user_quota"

    id = Column(Integer, primary_key=True, index=True)
    user_quota = Column(Integer)
    last_update = Column(DateTime)
    amount_of_files = Column(Integer)

    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    owner = relationship("User", back_populates="data_quota")
