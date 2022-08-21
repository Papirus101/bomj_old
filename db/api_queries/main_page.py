from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import NoResultFound
from sqlalchemy import select, func, Integer

import datetime

from db.models.active import Active
from db.models.models_settings import ModelSettings
from db.models.user_db import Users


async def get_online_info(db_session: AsyncSession):
    async with db_session() as session:
        date_todat = datetime.datetime.today() - datetime.timedelta(days=1)
        date = datetime.datetime(date_todat.year, date_todat.month, date_todat.day, 0, 0, 0).timestamp()
        sql_count_users_and_message = select(func.count(Active.user_id).label('total_users'),
                                             func.sum(Active.count_message).label('total_message')
                                             ).where(Active.date >= date).group_by(Active.last_active)
        count_users_and_message = await session.execute(sql_count_users_and_message)
        return count_users_and_message.one()


async def get_graph_online(db_session: AsyncSession, date_start: str, date_end: str):
    async with db_session() as session:
        date_start = datetime.datetime.strptime(date_start, '%Y-%m-%d')
        date_end = datetime.datetime.strptime(date_end, '%Y-%m-%d')
        graph_sql = select(
            func.count(Active.user_id).label('count_users'),
            func.sum(Active.count_message).label('total_message'),
            Active.last_active
        ).where(
            Active.last_active >= int(datetime.datetime(date_start.year, date_start.month, date_start.day).timestamp()),
            Active.last_active <= int(
                datetime.datetime(date_end.year, date_end.month, date_end.day).timestamp())).order_by(
            Active.last_active).group_by(Active.last_active)
        graph = await session.execute(graph_sql)
        graph = graph.all()
        return graph


async def get_all_user_money_and_bottle(db_session: AsyncSession):
    async with db_session() as session:
        sql = select(func.sum(Users.money).label('money'),
                     func.sum(Users.bottle).label('bottle'))
        total_money_and_bottle = await session.execute(sql)
        return total_money_and_bottle.one()


async def get_info_model(db_session: AsyncSession):
    async with db_session() as session:
        sql = select(ModelSettings.settings)
        info = await session.execute(sql)
        try:
            info = info.one()
        except NoResultFound:
            return False
        return info


async def get_info_by_current_model_sql(db_session: AsyncSession, model: str, columns, page: int):
    async with db_session() as session:
        sql = 'SELECT %s FROM %s LIMIT 20 OFFSET %s' % (','.join(columns), model, page)
        info = await session.execute(sql)
        return info.all()


async def search_by_fields(db_session: AsyncSession, model: str, search_columns: list, columns: list, value: str):
    async with db_session() as session:

        answer = []
        for search_column in search_columns:
            sql = 'SELECT %s FROM %s WHERE %s = %s' % (','.join(columns), model, search_column, value)
            data = await session.execute(sql)
            data = data.all()
            if len(data) > 0:
                for result in data:
                    answer.append(result)
        return answer
