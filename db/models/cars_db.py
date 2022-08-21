from db.base import Base

from sqlalchemy import BigInteger, Column, Integer, TEXT, ForeignKey, Boolean
from sqlalchemy_utils.types.choice import ChoiceType

from misc.vriables import MONEY_TYPES, NUMBER_TYPES


class Cars(Base):
    __tablename__ = 'cars'
    
    id = Column(Integer, primary_key=True, unique=True, autoincrement=True)
    name = Column(TEXT)
    price = Column(Integer)
    money_type = Column(ChoiceType(MONEY_TYPES), default='рубли')
    engine = Column(Integer, ForeignKey('engine.id'))
    transmission = Column(Integer, ForeignKey('transmission.id'))
    tire = Column(Integer, ForeignKey('tire.id'))
    clas = Column(TEXT)
    
    def __repr__(self) -> str:
        return self.name
    
    
class EngineCars(Base):
    __tablename__ = 'engine'
    
    id = Column(Integer, primary_key=True, unique=True, autoincrement=True)
    name = Column(TEXT)
    price = Column(Integer)
    money_type = Column(ChoiceType(MONEY_TYPES), default='рубли')
    power = Column(Integer)
    clas = Column(TEXT)
    
    def __repr__(self) -> str:
        return self.name
    
    
class TireCars(Base):
    __tablename__ = 'tire'
    
    id = Column(Integer, primary_key=True, unique=True, autoincrement=True)
    name = Column(TEXT)
    price = Column(Integer)
    money_type = Column(ChoiceType(MONEY_TYPES), default='рубли')
    grip = Column(Integer)
    
    def __repr__(self) -> str:
        return self.name
    
    
class Tranmission(Base):
    __tablename__ = 'transmission'
    
    id = Column(Integer, primary_key=True, unique=True, autoincrement=True)
    name = Column(TEXT)
    price = Column(Integer)
    money_type = Column(ChoiceType(MONEY_TYPES), default='рубли')
    drive = Column(TEXT)
    clas = Column(TEXT)
    
    def __repr__(self) -> str:
        return self.name
    
    
class CarsUser(Base):
    __tablename__ = 'cars_user'
    
    id = Column(Integer, primary_key=True, unique=True, autoincrement=True)
    owner = Column(BigInteger, ForeignKey('users.telegram_id'))
    car = Column(Integer, ForeignKey('cars.id'))
    engine = Column(Integer, ForeignKey('engine.id'))
    tire = Column(Integer, ForeignKey('tire.id'))
    transmission = Column(Integer, ForeignKey('transmission.id'))
    clas = Column(TEXT)
    is_active = Column(Boolean, default=False)
    number = Column(TEXT)
    number_type = Column(ChoiceType(NUMBER_TYPES), default='regular')
    fuel = Column(Integer, default=100)
    in_garage = Column(Boolean, default=False)
    
    def __repr__(self) -> str:
        return self.name