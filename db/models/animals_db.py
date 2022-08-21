from db.base import Base

from sqlalchemy import Column, Integer, TEXT


class Animals(Base):
    __tablename__ = 'animals'
    
    id = Column(Integer, primary_key=True, unique=True, autoincrement=True)
    name = Column(TEXT)
    price = Column(Integer)
    power = Column(Integer)
    
    def __repr__(self) -> str:
        return self.name