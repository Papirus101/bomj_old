from db.base import Base

from sqlalchemy import Column, Integer, BigInteger, ForeignKey, TEXT, Boolean


class UserBusiness(Base):
    __tablename__ = 'user_business'
    
    id = Column(Integer, primary_key=True, unique=True, autoincrement=True)
    owner = Column(BigInteger, ForeignKey('users.telegram_id'))
    count_product = Column(Integer)
    name = Column(TEXT)
    need_product = Column(Boolean, default=False)
    count_need_product = Column(Integer)
    business_type = Column(TEXT)