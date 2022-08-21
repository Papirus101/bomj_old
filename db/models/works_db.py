from db.base import Base

from sqlalchemy import Column, Integer, TEXT


class Works(Base):
    __tablename__ = 'works'
    
    id = Column(Integer, primary_key=True)
    name = Column(TEXT)
    lvl = Column(Integer)