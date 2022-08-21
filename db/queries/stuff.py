
from select import select
from db.models.stuff_db import Stuff
from sqlalchemy.ext.asyncio import AsyncSession

async def get_current_item(db_session: AsyncSession, stuff_id: int):
    
    async with db_session() as session:
        sql = select(Stuff).where(Stuff.id == stuff_id)
        stuff = session.execute(sql)
    return stuff.one()