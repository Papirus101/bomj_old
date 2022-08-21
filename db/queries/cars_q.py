from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from db.models.cars_db import CarsUser, Cars, TireCars, EngineCars, Tranmission


async def get_user_active_car(db_session: AsyncSession, user_id: int):
    async with db_session() as session:
        sql = select(CarsUser).where(CarsUser.owner == user_id, CarsUser.is_active == True)
        try:
            data = await session.execute(sql)
            data = data.one()
            return data
        except NoResultFound:
            return None


async def get_car_in_store(db_session: AsyncSession, car_id: int):
    async with db_session() as session:
        sql = select(
            Cars, Tranmission, EngineCars, TireCars
        ).join(
            Tranmission, Cars.transmission
        ).join(
            TireCars, Cars.tire
        ).join(
            EngineCars, Cars.engine
        ).where(Cars.id == car_id)
        data = await session.execute(sql)
        data = data.one()
        return data
