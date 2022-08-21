from db.base import Base

from sqlalchemy import Column, Integer, TEXT


class Gun(Base):
    __tablename__ = 'guns'
    
    id = Column(Integer, primary_key=True, unique=True, autoincrement=True)
    name = Column(TEXT)
    price = Column(Integer)
    range = Column(Integer)
    count_ammo = Column(Integer)
    
    def __repr__(self) -> str:
        return self.name