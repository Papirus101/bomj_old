from sqlalchemy import select
from db.models.houses_db import Houses


async def get_house_store(db_session, house_id: int = 0):
    
    async with db_session() as session:
        sql = select(Houses).where(Houses.in_store == True).order_by(Houses.lvl)
        houses = await session.execute(sql)
        try:
            house = houses.all()[house_id][0]
        except IndexError:
            return False
        return house