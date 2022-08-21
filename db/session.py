import os

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker

from db.models import ammo_db, user_db, animals_db, banda_db, cars_db, chat_random_db, donat_db, fish_db, \
    gas_station_db, guns_db, guns_war_db, houses_db, pizza_components_db, pizza_db, race_event_db, \
    shop_item_db, stuff_db, user_business_db, user_stuff_db, api_user_db, active, models_settings, items

from dotenv import load_dotenv

load_dotenv('.env')

engine = create_async_engine(
    f"postgresql+asyncpg://{os.getenv('DB_USER')}:{os.getenv('DB_PASS')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}",
    future=True
)

sync_engine = create_engine(
    f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASS')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}",
    future=True)

metadata = MetaData()
metadata.reflect(bind=sync_engine)

async_sessionmaker = sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession
)
