"""SQLAlchemy database models."""

from datetime import datetime

from sqlalchemy import JSON, Boolean, Column, DateTime, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class UserModel(Base):
    """User database model."""

    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    status = Column(String, nullable=False, default="active")
    email_verified = Column(Boolean, nullable=False, default=False)
    last_login_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    roles = Column(JSON, nullable=False, default=list)

