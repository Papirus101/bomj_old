import asyncio
import datetime
import pathlib
import random

from aiogram import types, Dispatcher

from db.models.user_db import Users
from db.queries.users import get_main_user_info, update_event_id, update_user_balance, update_user_exp, \
    update_works_count
from image_generate.works.conductor import get_fake
from keyboards.inline.works.works_data import works_callback
from keyboards.inline.works.works_inline import start_work_keyb, work_check_keyboard_generator
from misc.convert_money import convert_stats
from misc.user_misc import get_top_by_works, check_user_characteristics, get_total_amount, characteristic_change
from misc.vriables import CONDUCTOR_WORK_KEYBOARD
from static.text.profile import NEW_LEVEL_TEXT


async def work_info(call: types.CallbackQuery, callback_data: dict):
    db_session = call.message.bot.get('db')
    await call.answer()
    await call.message.delete()
    work = callback_data.get('type')
    user: Users = await get_main_user_info(db_session, call.from_user.id)
    await call.message.answer_photo(open(f'{pathlib.Path().absolute()}/image/works/conductor/tralik.png', 'rb'),
                                    caption="🚎 Тебя отправили работать кондуктором в троллейбусе.\n"
                                            f"Тебе платят за каждые каждого пойманного зайца {convert_stats(money=user.lvl * 30)} руб.\n\n"
                                            "<code>По мере прокачки персонажа, ты сможешь устраиваться на более "
                                            "прибыльные работы</code>\n\n"
                                            f'{await get_top_by_works(db_session, work)}\n',
                                    reply_markup=await start_work_keyb(work))


async def send_work(call: types.CallbackQuery):
    db_session = call.message.bot.get('db')
    await get_fake(db_session, call.from_user.id)
    await call.message.answer_photo(
        open(f'{pathlib.Path().absolute()}/image/works/conductor/{call.from_user.id}_event.png', 'rb'),
        caption=f'<code>Сегодня {datetime.date.today().strftime("%d-%m-%Y")}.</code> Проездной считается действительным до сегодняшнего дня включительно',
        reply_markup=await work_check_keyboard_generator(CONDUCTOR_WORK_KEYBOARD, '5', 'Уволиться'))
    pathlib.Path(f'{pathlib.Path().absolute()}/image/works/conductor/{call.from_user.id}_event.png').unlink()


async def conductor_start(call: types.CallbackQuery):
    db_session = call.message.bot.get('db')
    await call.answer()
    await call.message.delete()
    if not await check_user_characteristics(db_session, call):
        return
    await update_event_id(db_session, call.from_user.id, 0)
    await send_work(call)


async def conductor_check(call: types.CallbackQuery, callback_data: dict):
    db_session = call.message.bot.get('db')
    user_answer = int(callback_data.get('event'))
    work = callback_data.get('type').split('_')[0]
    random_events_text = ''
    user: Users = await get_main_user_info(db_session, call.from_user.id)
    time_sleep = random.randint(3, 7)

    await call.answer()
    await call.message.delete()

    if user_answer == user.event_id:
        await update_works_count(db_session, call.from_user.id, work)
        if user.event_id == 2:
            total_reward, nalog = await get_total_amount(user.lvl * 25, user.vip)
            if nalog > 0:
                random_events_text = f'💥 Ты заплатил налог государству {convert_stats(money=nalog)} руб.'
            await update_user_balance(db_session, call.from_user.id, 'money', '+', total_reward)
            if await update_user_exp(db_session, call.from_user.id, '+', 1, user.vip):
                await call.message.answer(NEW_LEVEL_TEXT)
            system_message = await call.message.answer(
                f'Ты сделал правильный выбор, твоя зарплата составила {convert_stats(money=total_reward)} руб.\n'
                f'{random_events_text}\n'
                f'🏃 <code>Следующий пассажир уже заходит в троллейбус, подожди {time_sleep} сек.</code>')
        else:
            system_message = await call.message.answer(
                f'Ты сделал правильный выбор\n'
                f'🏃 <code>Следующий пассажир уже заходит в троллейбус, подожди {time_sleep} сек.</code>')
    else:
        total_reward, nalog = await get_total_amount(user.lvl * 10, user.vip)
        await update_user_balance(db_session, call.from_user.id, 'money', '-', total_reward)
        await update_user_exp(db_session, call.from_user.id, '-', 1, user.vip)
        system_message = await call.message.answer(f'Ты ошибся, за что начальсто оштрафовало тебя на {convert_stats(money=total_reward)} руб. и ты потерял 1 ед. опыта\n'
                                                   '🏃 <code>Следующий пассажир уже заходит в троллейбус, подожди {time_sleep} сек.</code>')
    if await characteristic_change(db_session, call.from_user.id):
        await call.message.answer('Ты не можешь продолжить работу, проверь свои потребности')
        return
    await asyncio.sleep(time_sleep)
    await system_message.delete()
    await send_work(call)


def register_conductor_work_handler(dp: Dispatcher):
    dp.register_callback_query_handler(work_info, works_callback.filter(event='info', type='5'), chat_type='private')
    dp.register_callback_query_handler(conductor_start, works_callback.filter(event='start', type='5'),
                                       chat_type='private')
    dp.register_callback_query_handler(conductor_check, works_callback.filter(type='5_check'), chat_type='private')