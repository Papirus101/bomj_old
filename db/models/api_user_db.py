from email.policy import default
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID

import uuid

from db.base import Base


class UsersApi(Base):
    __tablename__ = 'users_api'
    
    id = Column(Integer, primary_key=True)
    email = Column(String(40), unique=True, index=True)
    name = Column(String(150), unique=True, index=True)
    hashed_password = Column(String())
    is_active = Column(Boolean, default=True, nullable=False)
    
    
class Tokens(Base):
    __tablename__ = 'tokens_api'
    
    id = Column(Integer, primary_key=True)
    token = Column(UUID(as_uuid=True), unique=True, index=True, nullable=False, default=uuid.uuid4)
    expires = Column(DateTime)
    owner = Column(Integer, ForeignKey('users_api.id'))
    