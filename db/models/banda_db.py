from db.base import Base

from sqlalchemy import BigInteger, Column, Integer, TEXT, ForeignKey


class Banda(Base):
    __tablename__ = 'banda'
    
    id = Column(Integer, primary_key=True, unique=True, autoincrement=True)
    name = Column(TEXT)
    rating = Column(Integer, default=0)
    smile = Column(TEXT)
    admin = Column(BigInteger, ForeignKey('users.telegram_id'))
    
    
    def __repr__(self) -> str:
        return self.name