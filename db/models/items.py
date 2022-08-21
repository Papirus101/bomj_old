from db.base import Base

from sqlalchemy import Column, VARCHAR, Integer


class Items(Base):
    __tablename__ = 'items'

    id = Column(Integer, primary_key=True, unique=True)
    name = Column(VARCHAR)
    type = Column(Integer)
    smile = Column(VARCHAR)
