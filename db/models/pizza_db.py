from db.base import Base

from sqlalchemy import Column, Integer, TEXT


class Pizza(Base):
    __tablename__ = 'pizza'
    
    id = Column(Integer, primary_key=True, unique=True, autoincrement=True)
    name = Column(TEXT)
    components = Column(TEXT)
