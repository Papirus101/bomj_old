import asyncio
import random

from aiogram import types
from sqlalchemy.ext.asyncio import AsyncSession
from db.queries.active import check_user_online

from db.queries.business import get_current_business
from db.queries.users import get_top_works, update_needs_user, check_characteristic
from misc.convert_money import convert_stats
from misc.vriables import SMILE_MONEY_TYPE, MEDAL_TYPES


async def get_user_business_profit(db_session, user):
    

    profit = {'money': 0, 'bottle': 0}

    print(user)
    
    if user is not None and user.info is not None and user.info.get('business', False):
        for info in user.info.get('business').items():
            current_business = await get_current_business(db_session, int(info[0]))
            
            if profit.get(current_business.money_profit, None) is not None:
                profit[current_business.money_profit] += current_business.profit * info[1]
            else:
                profit[current_business.money_profit] = current_business.profit * info[1]

            print(profit)

    if user is not None and user.bomj != 0:
        profit['bottle'] += user.bomj * 50
    
    return profit


async def text_user_balance(money, bottle, exp, donat, keyses):
    return f'Твой баланс: {convert_stats(a=money)} {SMILE_MONEY_TYPE.get("money")} | ' \
            f'{convert_stats(a=bottle)} {SMILE_MONEY_TYPE.get("bottle")} | ' \
            f'{convert_stats(a=keyses)} {SMILE_MONEY_TYPE.get("keyses")} | ' \
            f'{convert_stats(a=exp)} {SMILE_MONEY_TYPE.get("exp")} | ' \
            f'{convert_stats(a=donat)} {SMILE_MONEY_TYPE.get("donat")}'


async def get_top_by_works(db_session, work):
    data = await get_top_works(db_session, work)
    users = ''
    for pos, user in enumerate(data, start=1):
        users += f'{MEDAL_TYPES.get(pos)}{user.name}: {user.count}\n'
    return 'Топ работяг:\n' \
           f'{users}'


async def get_total_amount(amount: int, vip: bool):
    nalog = 0
    if not vip:
        if random.choice([True, False]):
            nalog = amount * 13 / 100
            amount -= nalog
    else:
        amount *= 2
    return amount, nalog


async def characteristic_change(async_sessionmaker: AsyncSession, user_id):
    characteristic = ['eat', 'luck', 'health']
    answer = False
    for current_characteristic in characteristic:
        if await update_needs_user(async_sessionmaker, user_id, current_characteristic, '-', random.randint(3, 10)):
            answer = True
    return answer


async def check_user_characteristics(db_session: AsyncSession, call: types.CallbackQuery):
    if not await check_characteristic(db_session, call.from_user.id):
        await call.message.answer('Ты не можешь больше работать, проверь свои показатели')
        return False
    return True


async def check_online_user(db_session: AsyncSession, bot):
    users = await check_user_online(db_session)
    for user in users:
        user = user[0]
        await bot.send_message(chat_id=user.user_id, text='Ты был отключён из-за отсутствия активности')
        await asyncio.sleep(0.5)



