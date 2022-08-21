from sqlalchemy import Column, Integer, BIGINT, VARCHAR, Boolean, ForeignKey

from db.base import Base

from time import time


class Active(Base):
    __tablename__ = 'active'

    id = Column(Integer, primary_key=True, unique=True)
    user_id = Column(BIGINT, ForeignKey('users.telegram_id'))
    active = Column(Boolean, default=False)
    last_active = Column(BIGINT, default=0)
    count_message = Column(Integer, default=1)
    total_time = Column(Integer, default=0)
