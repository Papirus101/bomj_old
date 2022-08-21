from db.base import Base

from sqlalchemy import Column, TEXT, Integer


class PizzaComponents(Base):
    __tablename__ = 'pizza_components'
    
    id = Column(Integer, primary_key=True, unique=True, autoincrement=True)
    name = Column(TEXT)