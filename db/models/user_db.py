from sqlalchemy import Column, ForeignKey, Integer, BigInteger, TEXT, Boolean, BOOLEAN
from sqlalchemy.dialects.postgresql import JSON

from db.base import Base


class Users(Base):
    __tablename__ = "users"

    telegram_id = Column(BigInteger, primary_key=True, unique=True, autoincrement=False)
    username = Column(TEXT)
    fullname = Column(TEXT, nullable=True)
    name = Column(TEXT, unique=True)
    money = Column(BigInteger, default=200)
    bottle = Column(BigInteger, default=0)
    keyses = Column(Integer, default=0)
    event_id = Column(Integer, default=0)
    donat = Column(Integer, default=0)
    house = Column(Integer, ForeignKey('houses.id'), default=1)
    custom_image = Column(Boolean, default=False)
    unlim_health = Column(Boolean, default=False)
    bomj = Column(Integer, default=0)
    health = Column(Integer, default=100)
    eat = Column(Integer, default=100)
    luck = Column(Integer, default=100)
    rating = Column(Integer, default=0)
    lvl = Column(Integer, default=1)
    exp = Column(Integer, default=0)
    vip = Column(Boolean, default=False)
    vip_finish = Column(BigInteger, default=0)
    gun = Column(Integer, ForeignKey('guns.id'), nullable=True, default=None)
    ammo_type = Column(Integer, default=0)
    ammo_count = Column(Integer, default=0)
    banda = Column(Integer, ForeignKey('banda.id'), nullable=True, default=None)
    gun_war = Column(Integer, ForeignKey('guns_war.id'), default=1)
    shirts = Column(Integer, ForeignKey('stuff.id'), nullable=True, default=None)
    shoes = Column(Integer, ForeignKey('stuff.id'), nullable=True, default=None)
    jacket = Column(Integer, ForeignKey('stuff.id'), nullable=True, default=None)
    pants = Column(Integer, ForeignKey('stuff.id'), nullable=True, default=None)
    donat_stuff = Column(Integer, ForeignKey('stuff.id'), nullable=True, default=None)
    slots_bet = Column(BigInteger, default=500)
    rod = Column(Integer, ForeignKey('rod.id'), nullable=False, default=1)
    rod_detail = Column(Integer, default=0)
    bait = Column(Integer, default=0)
    boat = Column(Integer, ForeignKey('boat.id'), default=None, nullable=True)
    ban_mail = Column(Boolean, default=False)
    close_profile = Column(Boolean, default=False)
    referral_id = Column(BigInteger, ForeignKey('users.telegram_id'), nullable=True, default=None)
    power = Column(Integer, default=0)
    info = Column(JSON)
    
    def __repr__(self) -> str:
        return f'{self.name} {self.username} {self.telegram_id}'

    
