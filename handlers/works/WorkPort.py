import asyncio
import pathlib
import random

from aiogram import types, Dispatcher

from db.queries.users import get_main_user_info, update_event_id, update_user_balance, update_user_exp, \
    update_works_count

from keyboards.inline.works.works_data import works_callback
from keyboards.inline.works.works_inline import start_work_keyb, work_check

from misc.convert_money import convert_stats
from misc.user_misc import get_top_by_works, get_total_amount, check_user_characteristics, characteristic_change

from image_generate.works.port import generate_image
from static.text.profile import NEW_LEVEL_TEXT


async def send_work(call):
    db_session = call.message.bot.get('db')

    box_id = random.randint(1, 6)
    await update_event_id(db_session, call.from_user.id, box_id)
    await generate_image(box_id, call.from_user.id)
    await call.message.answer_photo(
        open(f'{pathlib.Path().absolute()}/image/works/port/{call.from_user.id}_port.png', 'rb'),
        reply_markup=await work_check('1', 'Уволиться'))
    pathlib.Path(f'{pathlib.Path().absolute()}/image/works/port/{call.from_user.id}_port.png').unlink()


async def work_info(call: types.CallbackQuery, callback_data: dict):
    db_session = call.message.bot.get('db')
    await call.answer()
    await call.message.delete()
    work = callback_data.get('type')
    user = await get_main_user_info(db_session, call.from_user.id)
    await call.message.answer_photo(open(f'{pathlib.Path().absolute()}/image/works/port/port.png', 'rb'),
                                    caption=f'⛴ Тебя отправили в порт для работы грузчиком. Отличная работа для начала\n'
                                            f'За каждый ящик ты будешь получать {convert_stats(money=user.lvl * 15 if user.lvl > 0 else 20)} руб.\n\n'
                                            f'<code>По мере прокачки персонажа, ты сможешь устраиваться на более'
                                            f' прибыльные работы</code>\n\n'
                                            f'{await get_top_by_works(db_session, work)}\n',
                                    reply_markup=await start_work_keyb(work))


async def start_work(call: types.CallbackQuery):
    db_session = call.message.bot.get('db')

    await call.answer()
    await call.message.delete()
    if not await check_user_characteristics(db_session, call):
        return
    await update_event_id(db_session, call.from_user.id, 0)
    await send_work(call)


async def check_user_answer(call: types.CallbackQuery, callback_data: dict):
    db_session = call.message.bot.get('db')
    work = callback_data.get('type').split('_')[0]
    await call.answer('Проверяем...')
    await call.message.delete()

    user = await get_main_user_info(db_session, call.from_user.id)
    user_answer = callback_data.get('event')
    random_events_text = ''

    if user.event_id == int(user_answer):
        total_reward, nalog = await get_total_amount(user.lvl * 15 if user.lvl > 0 else 15, user.vip)
        if nalog > 0:
            random_events_text = f'💥 Ты заплатил налог государству {convert_stats(money=nalog)} руб.'
        await update_user_balance(db_session, call.from_user.id, 'money', '+', total_reward)
        if await update_user_exp(db_session, call.from_user.id, '+', 1, user.vip):
            await call.message.answer(NEW_LEVEL_TEXT)
        await update_works_count(db_session, call.from_user.id, work)
        event_text = f'💰 Ты отнёс нужный ящик, твой заработок {convert_stats(money=total_reward)} руб.'
    else:
        event_text = 'Ты отнёс не тот ящик, работа продолжается...'
    time_to_sleep = random.randint(3, 6)
    system_message = await call.message.answer(f'{event_text}\n'
                                               f'{random_events_text}\n'
                                               f'🏃 <code>Ты пошёл к следующему ящику, дорога займёт {time_to_sleep} с.</code>')
    if await characteristic_change(db_session, call.from_user.id):
        await call.message.answer('Ты не можешь продолжить работу, проверь свои потребности')
        return
    await asyncio.sleep(time_to_sleep)
    await send_work(call)
    await system_message.delete()


def register_port_work(dp: Dispatcher):
    dp.register_callback_query_handler(work_info, works_callback.filter(event='info', type='1'), chat_type='private')
    dp.register_callback_query_handler(start_work, works_callback.filter(event='start', type='1'), chat_type='private')
    dp.register_callback_query_handler(check_user_answer, works_callback.filter(type='1_check'), chat_type='private')
