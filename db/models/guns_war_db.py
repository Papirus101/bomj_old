from db.base import Base

from sqlalchemy import Column, Integer, TEXT, Boolean
from sqlalchemy_utils.types.choice import ChoiceType

from misc.vriables import MONEY_TYPES


class GunsWar(Base):
    __tablename__ = 'guns_war'
    
    id = Column(Integer, primary_key=True, unique=True, autoincrement=True)
    name = Column(TEXT)
    power = Column(Integer)
    price = Column(Integer)
    money_type = Column(ChoiceType(MONEY_TYPES), default='money')
    in_store = Column(Boolean, default=True) 

    def __repr__(self) -> str:
        return self.name
