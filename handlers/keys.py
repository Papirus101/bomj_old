import random
from aiogram import types, Dispatcher
from db.queries.users import get_main_user_info, update_user_balance, update_user_exp, update_user_keys

from keyboards.inline.main_callback import profile_callback
from keyboards.inline.main_inline import open_keys_keyboard
from misc.user_misc import text_user_balance
from misc.vriables import SMILE_MONEY_TYPE
from static.text.profile import NEW_LEVEL_TEXT


async def keys_main(call: types.CallbackQuery):
    db_session = call.message.bot.get('db')
    user = await get_main_user_info(db_session, call.from_user.id)
    
    await call.answer()
    user_balance = await text_user_balance(user.money, user.bottle, user.exp, user.donat, user.keyses)
    await call.message.answer(f'{SMILE_MONEY_TYPE.get("keyses")} кейсы\n\n'
                              'Из кейса могут выпасть:\n'
                              f'{SMILE_MONEY_TYPE.get("money")} Рубли\n'
                              f'{SMILE_MONEY_TYPE.get("bottle")} Бутылки\n'
                              '📊 Опыт\n\n'
                              f'{user_balance}',
                              reply_markup=await open_keys_keyboard())
    
    
async def open_keys(call: types.CallbackQuery):
    db_session = call.message.bot.get('db')
    
    user = await get_main_user_info(db_session, call.from_user.id)
    if user.keyses <= 0:
        await call.answer('У тебя нет кейсов')
        return
    
    prize_variable = ['money', 'bottle', 'exp']
    prize = random.choices(prize_variable, weights=[60, 30, 10])[0]
    
    if prize in ['money', 'bottle']:
        count_prize = random.randint(100, user.lvl * 250 if user.lvl > 0 else 250)
        await update_user_balance(db_session, call.from_user.id, prize, '+', count_prize)
    elif prize in ['exp']:
        count_prize = random.randint(1, 5)
        if await update_user_exp(db_session, call.from_user.id, '+', count_prize):
            await call.message.answer(NEW_LEVEL_TEXT)
    await update_user_keys(db_session, call.from_user.id, '-', 1)
        
    user = await get_main_user_info(db_session, call.from_user.id)
    await call.answer()
    user_balance = await text_user_balance(user.money, user.bottle, user.exp, user.donat, user.keyses)
    await call.message.edit_text(f'{SMILE_MONEY_TYPE.get("keyses")} кейсы\n\n'
                                    'Из кейса могут выпасть:\n'
                                    f'{SMILE_MONEY_TYPE.get("money")} Рубли\n'
                                    f'{SMILE_MONEY_TYPE.get("bottle")} Бутылки\n'
                                    '📊 Опыт\n\n'
                                    f'🎉 Тебе выпало {count_prize} {SMILE_MONEY_TYPE.get(prize)}\n\n'
                                    f'{user_balance}',
                                    reply_markup=await open_keys_keyboard())
        


def register_private_keys_handler(dp: Dispatcher):
    dp.register_callback_query_handler(keys_main, profile_callback.filter(event='keys'), chat_type='private')
    dp.register_callback_query_handler(open_keys, profile_callback.filter(event='open_keys'), chat_type='private')