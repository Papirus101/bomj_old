from db.base import Base

from sqlalchemy import TEXT, Column, Integer


class Ammo(Base):
    __tablename__ = 'ammo'
    
    id = Column(Integer, primary_key=True, unique=True, autoincrement=True)
    name = Column(TEXT)
    price = Column(Integer)
    power = Column(Integer)
    
    def __repr__(self) -> str:
        return f'{self.name} патроны'