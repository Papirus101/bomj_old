import random

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.models.items import Items
from db.models.shop_item_db import ShopItem


async def new_order(db_session: AsyncSession, user_id: int):
    async with db_session() as session:
        sql = select(Items)
        items = await session.execute(sql)
        items = items.all()
        count_items = random.randint(5, 20)
        products = []
        products_names = []
        for i, x in enumerate(items):
            if i == count_items:
                break
            item = random.choice(items)
            if item[0].id not in products:
                products.append(item[0].id)
                products_names.append(f'{item[0].smile}{item[0].name}')
        await session.merge(ShopItem(owner=user_id, need_product=','.join(str(elem) for elem in products)))
        await session.commit()
        return products_names


async def get_user_order(db_session: AsyncSession, user_id: int, close: bool = False):
    async with db_session() as session:
        sql = select(ShopItem).where(ShopItem.owner == user_id, ShopItem.close == close)
        data = await session.execute(sql)
        data = data.all()
        if len(data) < 1:
            return False
        return data[0]


async def close_user_order(db_session: AsyncSession, user_id: int):
    async with db_session() as session:
        sql = select(ShopItem).where(ShopItem.owner == user_id, ShopItem.close == False)
        data = await session.execute(sql)
        data = data.all()
        if len(data) > 0:
            for elem in data:
                elem[0].close = True
                await session.commit()


async def get_products_by_category(db_session: AsyncSession, category: int):
    async with db_session() as session:
        sql = select(Items).where(Items.type == category)
        data = await session.execute(sql)
        data = data.all()
        return data


async def add_item_to_order(db_session: AsyncSession, user_id: int, product_id: str):
    async with db_session() as session:
        sql = select(ShopItem).where(ShopItem.owner == user_id, ShopItem.close == False)
        order = await session.execute(sql)
        data = order.one()
        if data[0].user_product is None:
            data[0].user_product = str(product_id)
        else:
            data[0].user_product += f',{product_id}'
        await session.commit()


async def get_items_names(db_session: AsyncSession, items: list):
    products = []
    async with db_session() as session:
        for item in items.split(','):
            product = await session.get(Items, int(item))
            products.append(f'{product.smile} {product.name}')
    return products
