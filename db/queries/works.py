from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.models.works_db import Works


async def get_user_works(db_session: AsyncSession, user_lvl: int):
    
    async with db_session() as session:
        sql = select(Works).where(Works.lvl <= user_lvl).order_by(Works.lvl)
        data = await session.execute(sql)
        data = data.all()
        return data
