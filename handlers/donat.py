from aiogram import types, Dispatcher

from db.queries.donat_q import check_new_donat, new_donat
from db.queries.users import update_user_balance, get_user_balance, set_user_variable
from keyboards.inline.main_callback import profile_callback
from keyboards.inline.main_inline import donat_keyboard

import requests


async def donat_info(call: types.CallbackQuery):
    await call.answer()
    await call.message.answer('❤️🍗😄 Бсконечные показатели - 299 рублей\n',
                              # '<strong>👑 VIP статус на неделю</strong> - 100 рублей',
                              reply_markup=await donat_keyboard(call.from_user.id))


async def check_donat(call: types.CallbackQuery):
    db_session = call.message.bot.get('db')
    s = requests.Session()
    s.headers['authorization'] = 'Bearer ' + 'a979fe52f14f7b4239de82a810435175'
    parameters = {'rows': 5, 'operation': 'IN'}
    h = s.get('https://edge.qiwi.com/payment-history/v2/persons/' + '79883158831' + '/payments', params=parameters)
    payments = h.json()
    for p in payments['data']:
        if str(p['comment']) == f'donat:{call.from_user.id}':
            transactions_id = p['txnId']
            donat = await check_new_donat(db_session, call.from_user.id, str(transactions_id),
                                          int(p["total"]["amount"]))
            if donat is not None:
                await call.message.answer('Новых пополнений не найдено')
                return
            await call.message.bot.send_message(chat_id=341163252,
                                                text=f'❗️❗️❗️❗️❗️❗️ <strong>НОВЫЙ ДОНАТ {p["total"]["amount"]} руб </strong> ❗️❗️❗️❗️❗️❗️')
            await new_donat(db_session, call.from_user.id, str(transactions_id), int(p["total"]["amount"]))
            await update_user_balance(db_session, call.from_user.id, 'donat', '+', int(p["total"]["amount"]))
            await call.message.answer(f'На твой баланс зачисленно {p["total"]["amount"]} руб.')
            return
    await call.message.answer('Новых пополнений не найдено')


async def buy_unlim_health(call: types.CallbackQuery):
    await call.answer()
    db_session = call.message.bot.get('db')
    user = get_user_balance(db_session, call.from_user.id)
    if user.donat >= 299:
        await set_user_variable(db_session, call.from_user.id, 'unlim_health', True)
        await update_user_balance(db_session, call.from_user.id, 'donat', '-', 299)
        await call.message.answer('Бесконечные показатели приобретены')
        return
    await call.message.answer('Недостаточно средств')


def register_donat_handler(dp: Dispatcher):
    dp.register_callback_query_handler(donat_info, profile_callback.filter(event='donat'), chat_type='private')
    dp.register_callback_query_handler(check_donat, profile_callback.filter(event='check_donat'), chat_type='private')
    dp.register_callback_query_handler(buy_unlim_health, profile_callback.filter(event='buy_unlim_health'),
                                       chat_type='private')
