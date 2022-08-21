from sqlalchemy import Column, Integer, JSON, ForeignKey
from db.base import Base

class ModelSettings(Base):
    __tablename__ = 'model_settings'
    
    id = Column(Integer, primary_key=True)
    settings = Column(JSON)