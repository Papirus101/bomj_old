from db.base import Base

from sqlalchemy import Column, ForeignKey, Integer, BigInteger, TEXT, Boolean
from sqlalchemy_utils.types.choice import ChoiceType

from misc.vriables import MONEY_TYPES


class Fish(Base):
    __tablename__ = 'fish'
    
    id = Column(Integer, primary_key=True, unique=True, autoincrement=True)
    name = Column(TEXT)
    price = Column(Integer)
    rod_lvl = Column(Integer)
    in_boat = Column(Boolean)
    boat_lvl = Column(Integer)
    
    def __repr__(self) -> str:
        return self.name
    
    
class FishUser(Base):
    __tablename__ = 'fish_user'
    
    id = Column(Integer, primary_key=True, unique=True, autoincrement=True)
    owner = Column(BigInteger, ForeignKey('users.telegram_id'))
    fish = Column(Integer, ForeignKey('fish.id'))
    weigh = Column(Integer)


class Boat(Base):
    __tablename__ = 'boat'
    
    id = Column(Integer, primary_key=True, unique=True, autoincrement=True)
    name = Column(TEXT)
    lvl = Column(Integer)


class Rod(Base):
    __tablename__ = 'rod'
    
    id = Column(Integer, primary_key=True, unique=True, autoincrement=True)
    name = Column(TEXT)
    lvl = Column(Integer)
    price = Column(Integer)
    money_type = Column(ChoiceType(MONEY_TYPES), default='money')
