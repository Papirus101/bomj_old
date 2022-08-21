from db.base import Base

from sqlalchemy import Column, ForeignKey, BigInteger, Integer


class UserStuff(Base):
    __tablename__ = 'user_stuff'
    
    id = Column(Integer, primary_key=True, unique=True, autoincrement=True)
    owner = Column(BigInteger, ForeignKey('users.telegram_id'))
    stuff = Column(Integer, ForeignKey('stuff.id'))