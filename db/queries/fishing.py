from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy import select, delete

from db.models.fish_db import Fish, FishUser, Rod

import random


async def get_random_fish(db_session: AsyncSession, rod_lvl):
    """ Получает рандомную рыбу """
    async with db_session() as session:
        sql = select(Fish).where(Fish.rod_lvl <= rod_lvl)
        data = await session.execute(sql)
        data = data.all()
        return random.choice(data)


async def add_user_fish(db_session: AsyncSession, user_id: int, fish: int, weight: int):
    """ Добавляет пользователю рыбу """
    async with db_session() as session:
        try:
            sql = select(FishUser).where(FishUser.owner == user_id, FishUser.fish == fish)
            data = await session.execute(sql)
            data = data.one()
            data = data[0]
            data.weigh += weight
        except NoResultFound:
            new_fish = FishUser(owner=user_id, fish=fish, weigh=weight)
            await session.merge(new_fish)
        await session.commit()


async def get_all_user_fish(db_session: AsyncSession, user_id: int):
    """ Получает полный список рыб пользователя """
    async with db_session() as session:
        sql = select(FishUser, Fish).join(Fish, FishUser.fish == Fish.id).where(FishUser.owner == user_id)
        data = await session.execute(sql)
        data = data.all()
        print(data)
        return data


async def delete_user_fish(db_session: AsyncSession, user_id: int):

    async with db_session() as session:
        sql = delete(FishUser).where(FishUser.owner == user_id)
        data = await session.execute(sql)
        await session.commit()


async def get_rod_by_id(db_session: AsyncSession, rod_id: int):

    async with db_session() as session:
        rod = await session.get(Rod, rod_id)
        return rod