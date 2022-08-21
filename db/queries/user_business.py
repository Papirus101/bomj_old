from doctest import FAIL_FAST
from db.models.user_business_db import UserBusiness

from sqlalchemy import select
from sqlalchemy.exc import NoResultFound


async def get_business_by_type(db_session, business_type: str):
    
    async with db_session() as session:
        sql = select(UserBusiness).where(UserBusiness.business_type == business_type)
        business = await session.execute(sql)
        business = business.one()[0]
    return business


async def update_business_owner(db_session, business_type: str, user_id: int = None):
    
    async with db_session() as session:
        sql = select(UserBusiness).where(UserBusiness.owner == user_id)
        user_business = await session.execute(sql)
        try:
            if user_id is not None:
                user_business.one()
                return False
            raise NoResultFound
        except NoResultFound:
            sql = select(UserBusiness).where(UserBusiness.business_type == business_type)
            business = await session.execute(sql)
            business = business.one()
            business[0].owner = user_id
            await session.commit()
            return True
        

async def update_business_products(db_session, business_type: str, amount: int, operation: str):
    
    async with db_session() as session:
        sql = select(UserBusiness).where(UserBusiness.business_type == business_type)
        business = await session.execute(sql)
        business = business.one()
        if operation == '+':
            business[0].count_product += amount
        elif operation == '-':
            business[0].count_product -= amount
        if business[0].count_product <= 0:
            business[0].count_product = 0
            await session.commit()
            return False
        await session.commit()
        return True
    
    
async def change_business_name_by_type(db_session, business_type: str, new_name: str, user_id: int):
    
    async with db_session() as session:
        sql = select(UserBusiness).where(UserBusiness.business_type == business_type)
        business = await session.execute(sql)
        business = business.one()
        if business[0].owner != user_id:
            return False
        business[0].name = new_name
        await session.commit()
        return True
        

async def add_new_order_products(db_session, business_type: str, count_products: int):
    
    async with db_session() as session:
        sql = select(UserBusiness).where(UserBusiness.business_type == business_type)
        business = await session.execute(sql)
        business = business.one()
        if business[0].need_product:
            return False
        business[0].need_product = True
        business[0].count_need_product = count_products
        await session.commit()
        return True
    
    
async def update_count_need_product_to_delivery(db_session, business_type: str, operation: str, amount: int):
    
    async with db_session() as session:
        sql = select(UserBusiness).where(UserBusiness.business_type == business_type)
        business = await session.execute(sql)
        business = business.one()
        if operation == '+':
            business[0].count_need_product += amount
        elif operation == '-':
            business[0].count_need_product -= amount
        await session.commit()
