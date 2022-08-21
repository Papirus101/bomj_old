from db.base import Base

from sqlalchemy import TEXT, Column, Integer
from sqlalchemy_utils.types.choice import ChoiceType

from misc.vriables import MONEY_TYPES, STUFF_TYPES


class Stuff(Base):
    __tablename__ = 'stuff'
    
    id = Column(Integer, primary_key=True, autoincrement=True, unique=True)
    name = Column(TEXT)
    price = Column(Integer)
    stuff_type = Column(ChoiceType(STUFF_TYPES), default='shirts')
    money_type = Column(ChoiceType(MONEY_TYPES), default='money')
    coords = Column(TEXT)
    
    def __repr__(self) -> str:
        return f'{self.stuff_type} {self.name}'
    