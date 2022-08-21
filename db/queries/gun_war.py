from sqlalchemy.exc import NoResultFound
from sqlalchemy import select
from db.models.guns_war_db import GunsWar


async def get_current_gun_war(db_session, gun_id: int):
    
    async with db_session() as session:
        gun = await session.get(GunsWar, gun_id)
        return gun


async def get_gun(db_session, gun_id: int):

    async with db_session() as session:
        sql = select(GunsWar).where(GunsWar.in_store == True).order_by(GunsWar.id)
        data = await session.execute(sql)
        data = data.all()
        try:
            return data[gun_id]
        except IndexError:
            return None
