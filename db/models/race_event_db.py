from db.base import Base

from sqlalchemy import Column, ForeignKey, Integer, BigInteger, TEXT, Boolean


class RaceEvent(Base):
    __tablename__ = 'race_event'
    
    id = Column(Integer, primary_key=True, unique=True, autoincrement=True)
    owner = Column(BigInteger, ForeignKey('users.telegram_id'))
    time_start = Column(BigInteger)
    event_id = Column(Integer)
    count_event = Column(Integer)
    time_race = Column(Integer)
    rival_car = Column(Integer, ForeignKey('cars.id'))
    win = Column(Boolean)
    clas = Column(TEXT)
    close = Column(Boolean, default=False)