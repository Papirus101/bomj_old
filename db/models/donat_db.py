from db.base import Base

from sqlalchemy import Column, BigInteger, TEXT, ForeignKey, Integer


class Donat(Base):
    __tablename__ = 'donat'
    
    id = Column(Integer, primary_key=True, unique=True, autoincrement=True)
    owner = Column(BigInteger, ForeignKey('users.telegram_id'))
    amount = Column(Integer)
    id_operation = Column(TEXT)
