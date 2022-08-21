from db.base import Base

from sqlalchemy import Column, Integer, BigInteger, Boolean, ForeignKey, TEXT


class GasStation(Base):
    __tablename__ = 'gas_station'
    
    id = Column(Integer, primary_key=True, unique=True, autoincrement=True)
    name = Column(TEXT)
    owner = Column(BigInteger, ForeignKey('users.telegram_id'))
    count_fuel = Column(Integer)
    need_fuel = Column(Boolean)
    count_need_fuel = Column(Integer)