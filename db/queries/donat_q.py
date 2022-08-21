from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from db.models.donat_db import Donat


async def check_new_donat(db_session: AsyncSession, user_id: int, transaction_id: str, amount: int):
    async with db_session() as session:
        sql = select(Donat.id).where(Donat.id_operation == transaction_id, Donat.owner == user_id, Donat.amount == amount)
        try:
            data = await session.execute(sql)
            data = data.one()
        except NoResultFound:
            return None
        return data


async def new_donat(db_session: AsyncSession, user_id: int, transaction_id: str, amount: int):
    async with db_session() as session:
        await session.merge(Donat(user_id=user_id, amount=amount, id_operation=transaction_id))
        await session.commit()