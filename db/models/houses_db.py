from db.base import Base

from sqlalchemy import BigInteger, Column, Integer, TEXT, Boolean
from sqlalchemy_utils.types.choice import ChoiceType

from misc.vriables import MONEY_TYPES


class Houses(Base):
    __tablename__ = 'houses'
    
    id = Column(Integer, primary_key=True, unique=True, autoincrement=True)
    name = Column(TEXT)
    price = Column(BigInteger)
    money_type = Column(ChoiceType(MONEY_TYPES), default='money')
    in_store = Column(Boolean)
    bomj = Column(Integer)
    lvl = Column(Integer)
