from sqlalchemy import select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio.session import AsyncSession
from db.models.active import Active
from time import time


async def update_user_active(db_session: AsyncSession, user_id: int):
    async with db_session() as session:
        sql = select(Active).where(Active.user_id == user_id)
        data = await session.execute(sql)
        new_active = False
        try:
            data = data.one()
            data = data[0]
            if data.active is False:
                new_active = True
            data.active = True
            data.last_active = time()
            data.count_message += 1
        except NoResultFound:
            await session.merge(Active(user_id=user_id, active=True, last_active=time()))
            new_active = True
        await session.commit()
        return new_active


async def check_user_online(db_session: AsyncSession):
    async with db_session() as session:
        sql = select(Active).where(Active.active == True, Active.last_active + 180 < time())
        data = await session.execute(sql)
        data = data.all()
        for user in data:
            user = user[0]
            user.active = False
            user.total_time += time() - user.last_active
            await session.commit()
        return data


async def get_all_online_users(db_session: AsyncSession):
    async with db_session() as session:
        sql = select(Active).where(Active.active == True)
        data = await session.execute(sql)
        data = data.all()
        return data


async def get_online_by_user(db_session: AsyncSession, user_id: int):
    async with db_session() as session:
        sql = select(Active).where(Active.user_id == user_id)
        data = await session.execute(sql)
        data = data.one()
        return data[0]
