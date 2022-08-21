from db.models.business_db import Business

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select


async def get_current_business(db_session: AsyncSession, business_id):
    
    async with db_session() as session:
        business = await session.get(Business, business_id)
    return business
 

async def get_all_business_in_store(db_session: AsyncSession):

    async with db_session() as session:
        sql = select(Busienss)
        data = await session.execute(sql)
        data = data.all()
        return data


async def get_business_store(db_session: AsyncSession, business_id: int):

    async with db_session() as session:
        sql = select(Business)
        data = await session.execute(sql)
        data = data.all()
        try:
            return data[business_id]
        except IndexError:
            return None
