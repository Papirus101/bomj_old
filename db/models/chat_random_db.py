from db.base import Base

from sqlalchemy import Column, BigInteger, ForeignKey, Integer, TEXT
from sqlalchemy_utils.types.choice import ChoiceType

from misc.vriables import MONEY_TYPES



class ChatRandom(Base):
    __tablename__ = 'chat_random'
    
    id = Column(Integer, primary_key=True, unique=True, autoincrement=True)
    sender = Column(BigInteger, ForeignKey('users.telegram_id'))
    oponent = Column(BigInteger, ForeignKey('users.telegram_id'))
    bet = Column(BigInteger)
    bet_type = Column(ChoiceType(MONEY_TYPES), default='money')
    bet_smile = Column(TEXT)
    time_start = Column(BigInteger)
    winner = Column(BigInteger, default=0)
    chat_id = Column(BigInteger)
    message_id = Column(BigInteger)
    