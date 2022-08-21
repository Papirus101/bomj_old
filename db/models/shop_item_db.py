from db.base import Base

from sqlalchemy import Column, Integer, BigInteger, TEXT, ForeignKey, Boolean


class ShopItem(Base):
    __tablename__ = 'shop_user'
    
    id = Column(Integer, primary_key=True, unique=True, autoincrement=True)
    owner = Column(BigInteger, ForeignKey('users.telegram_id'))
    need_product = Column(TEXT)
    user_product = Column(TEXT)
    close = Column(Boolean, default=False)