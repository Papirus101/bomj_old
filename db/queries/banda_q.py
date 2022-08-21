from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from sqlalchemy.types import Integer

from db.models.user_db import Users
from db.models.banda_db import Banda


async def get_all_bands(db_session: AsyncSession, offset: int):
    """Получает список всех банд"""
    async with db_session() as session:
        sql = select(Banda, func.count(Users.telegram_id)).join(Users, Users.banda == Banda.id).group_by(
            Banda.id).order_by(desc(Banda.rating)).offset(offset * 6).limit(6)
        print(sql)
        data = await session.execute(sql)
        data = data.all()
        print(data)
        return data


async def get_banda_info(db_session: AsyncSession, banda_id: int):
    """Получает информацию по конкретной банде"""
    async with db_session() as session:
        sql = select(Banda, func.count(Users.telegram_id)).join(Users, Users.banda == Banda.id).where(
            Banda.id == banda_id).group_by(Banda.id)
        data = await session.execute(sql)
        data = data.one()
        return data


async def get_info_main_banda(db_session: AsyncSession, banda_id: int):
    async with db_session() as session:
        sql = select(Banda.name.label('banda_name'),
                     Banda.id.label('banda_id'),
                     func.sum(Users.info['maxa_week'].astext.cast(Integer)).label('banda_maxa_week'),
                     func.sum(Users.info['maxa_all'].astext.cast(Integer)).label('banda_maxa_all'),
                     func.count(Users.telegram_id).label('count_users'),
                     func.sum(Users.money).label('all_money'),
                     func.sum(Users.bottle).label('all_bottle')
                     ).join(
                     Users, Users.banda == Banda.id
                     ).where(
                     Banda.id == banda_id
                     ).group_by(Banda.id)
        data = await session.execute(sql)
        data = data.one()
        return data


async def check_banda_name_and_smile(db_session: AsyncSession, name: str, value: str):
    async with db_session() as session:
        if value == 'name':
            sql = select(Banda.id).where(Banda.name == name)
        elif value == 'smile':
            sql = select(Banda.id).where(Banda.smile == name)
        try:
            data = await session.execute(sql)
            data = data.one()
        except NoResultFound:
            data = None
        return data


async def create_banda(db_session: AsyncSession, user_id: int, name: str, smile: str):
    async with db_session() as session:
        new_banda = await session.merge(Banda(admin=user_id, name=name, smile=smile))
        await session.commit()
        return new_banda


async def get_bands_event(db_session: AsyncSession):
    async with db_session() as session:
        sql = select(Banda.name, Banda.smile, func.sum(Users.info['maxa_week'].astext.cast(Integer)).label('count_maxa')
                     ).join(Users, Users.banda == Banda.id).group_by(Banda.id).order_by(desc('count_maxa')).limit(5)
        data = await session.execute(sql)
        data = data.all()
        return data


async def delete_banda(db_session: AsyncSession, banda_id: int):
    async with db_session() as session:
        sql = select(Banda).where(Banda.id == banda_id)
        data = await session.execute(sql)
        data = data.scalar_one()
        await session.delete(data)
        await session.commit()


async def update_banda_stars(db_session: AsyncSession, banda_id: int, operation: str, amount: int):
    async with db_session() as session:
        banda = await session.get(Banda, banda_id)
        if operation == '+':
            banda.rating += amount
        elif operation == '-':
            banda.rating -= amount
        await session.commit()