import asyncio
import pathlib
import random

from aiogram import types, Dispatcher

from db.models.user_db import Users
from db.queries.users import get_main_user_info, update_event_id, update_user_balance, update_user_exp, \
    update_works_count
from image_generate.works.security import generate_image, generate_gang_image
from keyboards.inline.works.works_data import works_callback
from keyboards.inline.works.works_inline import start_work_keyb, security_keyboard, security_fight_keyboard
from misc.convert_money import convert_stats
from misc.user_misc import get_top_by_works, check_user_characteristics, get_total_amount, characteristic_change
from static.text.profile import NEW_LEVEL_TEXT


async def work_info(call: types.CallbackQuery, callback_data: dict):
    db_session = call.message.bot.get('db')
    await call.answer()
    await call.message.delete()
    work = callback_data.get('type')
    user = await get_main_user_info(db_session, call.from_user.id)
    await call.message.answer_photo(open(f'{pathlib.Path().absolute()}/image/works/security/larek.png', 'rb'),
                                    caption="💂‍♂️ Тебя отправили в местный ларёк для работы охранником.\n"
                                            f"Тебе платят за каждого пойманного воришку {convert_stats(money=user.lvl * 20 if user.lvl > 0 else 20)} руб.\n\n"
                                            "<code>По мере прокачки персонажа, ты сможешь устраиваться на более "
                                            "прибыльные работы</code>\n\n"
                                            f'{await get_top_by_works(db_session, work)}\n',
                                    reply_markup=await start_work_keyb(work))


async def send_work(call: types.CallbackQuery, fight: bool = False):
    db_session = call.message.bot.get('db')

    event_id = random.randint(1, 3)
    await update_event_id(db_session, call.from_user.id, event_id)
    if fight:
        await generate_gang_image(event_id, call.from_user.id)
        await call.message.answer_photo(
            open(f'{pathlib.Path().absolute()}/image/works/security/{call.from_user.id}_bomjgang.png', 'rb'),
            caption='Выбери место для удара, куда указывает прицел',
            reply_markup=await security_fight_keyboard())
        pathlib.Path(f'{pathlib.Path().absolute()}/image/works/security/{call.from_user.id}_bomjgang.png').unlink()
        return
    await generate_image(event_id, call.from_user.id)
    await call.message.answer_photo(
        open(f'{pathlib.Path().absolute()}/image/works/security/{call.from_user.id}_security.png', 'rb'),
        reply_markup=await security_keyboard('3', 'Уволиться'))
    pathlib.Path(f'{pathlib.Path().absolute()}/image/works/security/{call.from_user.id}_security.png').unlink()


async def security_start(call: types.CallbackQuery):
    db_session = call.message.bot.get('db')
    await call.answer()
    await call.message.delete()
    if not await check_user_characteristics(db_session, call):
        return
    await update_event_id(db_session, call.from_user.id, 0)
    await send_work(call)


async def check_security_answer(call: types.CallbackQuery, callback_data: dict):
    db_session = call.message.bot.get('db')
    user_answer = callback_data.get('event')
    work = callback_data.get('type').split('_')[0]
    random_events_text = ''
    user: Users = await get_main_user_info(db_session, call.from_user.id)
    time_sleep = random.randint(3, 7)

    await call.answer()
    await call.message.delete()

    if user.event_id == int(user_answer) and user.event_id == 1:
        system_message = await call.message.answer('Это был обычный покупатель, рабочий день продолжается\n'
                                  f'🏃 <code>Следующий покупатель уже рассчитывается на кассе, он будет проходить мимо тебя примерно через {time_sleep} сек.</code>')
    elif user.event_id == int(user_answer) and user.event_id == 2:
        total_reward, nalog = await get_total_amount(user.lvl * 20 if user.lvl > 0 else 20, user.vip)
        if nalog > 0:
            random_events_text = f'💥 Ты заплатил налог государству {convert_stats(money=nalog)} руб.'
        await update_user_balance(db_session, call.from_user.id, 'money', '+', total_reward)
        if await update_user_exp(db_session, call.from_user.id, '+', 1, user.vip):
            await call.message.answer(NEW_LEVEL_TEXT)
        await update_works_count(db_session, call.from_user.id, work)
        system_message = await call.message.answer(f'Ты поймал злошного нарушителя, который пытался украсть товар из магазина, твой заработок {convert_stats(money=total_reward)} руб.\n'
                                  f'{random_events_text}\n'
                                  f'🏃 <code>Следующий покупатель уже рассчитывается на кассе, он будет проходить мимо тебя примерно через {time_sleep} сек.</code>')
    elif int(user_answer) == 2 and user.event_id == 3:
        system_message = await call.message.answer('В магазин опять пришёл Иннокентий и пытается вас ограбить, дай ему отпор или он вырубит тебя')
        await send_work(call, True)
        await system_message.delete()
        return
    else:
        total_reward, nalog = await get_total_amount(user.lvl * 10, user.vip)
        await update_user_balance(db_session, call.from_user.id, 'money', '-', total_reward)
        await update_user_exp(db_session, call.from_user.id, '-', 1, user.vip)
        system_message = await call.message.answer(f'Ты ошибся в своём выборе, а ведь возможно это был очередной воришка, начальство оштрафовало тебя на {total_reward} руб. и ты потерял 1 ед. опыта'
                                  f'🏃 <code>Следующий покупатель уже рассчитывается на кассе, он будет проходить мимо тебя примерно через {time_sleep} сек.</code>')
    if user.event_id != 1:
        if await characteristic_change(db_session, call.from_user.id):
            await call.message.answer('Ты не можешь продолжить работу, проверь свои потребности')
            return
    await asyncio.sleep(time_sleep)
    await system_message.delete()
    await send_work(call)


async def check_fight(call: types.CallbackQuery, callback_data: dict):
    db_session = call.message.bot.get('db')
    user_answer = int(callback_data.get('event'))
    user: Users = await get_main_user_info(db_session, call.from_user.id)
    random_events_text = ''
    work = '3'
    time_sleep = random.randint(3, 7)

    await call.answer()
    await call.message.delete()

    if user_answer == user.event_id:
        total_reward, nalog = await get_total_amount(user.lvl * 22, user.vip)
        if nalog > 0:
            random_events_text = f'💥 Ты заплатил налог государству {convert_stats(money=nalog)} руб.'
        await update_user_balance(db_session, call.from_user.id, 'money', '+', total_reward)
        if await update_user_exp(db_session, call.from_user.id, '+', 1, user.vip):
            await call.message.answer(NEW_LEVEL_TEXT)
        await update_works_count(db_session, call.from_user.id, work)
        system_message = await call.message.answer(
            f'Ты дал отпор Иннокентию, за что тебе выписали премию в размере {convert_stats(money=total_reward)} руб.\n'
            f'{random_events_text}\n'
            f'🏃 <code>Следующий покупатель уже рассчитывается на кассе, он будет проходить мимо тебя примерно через {time_sleep} сек.</code>')
    else:
        time_sleep = random.randint(10, 20)
        total_reward, nalog = await get_total_amount(user.lvl * 10, user.vip)
        await update_user_balance(db_session, call.from_user.id, 'money', '-', total_reward)
        await update_user_exp(db_session, call.from_user.id, '-', 1, user.vip)
        system_message = await call.message.answer(f'Ты не смог дать отпор Иннокентию, из-за чего он смог ограбить магазин, ты понёс наказание в размере {convert_stats(money=total_reward)} руб. и 1 ед. опыта\n'
                                  f'🏃 Тебе пришлось проехать в местный травмпункт, из-за чего ты сможешь вернуться на работу только через {time_sleep} сек.')
    if await characteristic_change(db_session, call.from_user.id):
        await call.message.answer('Ты не можешь продолжить работу, проверь свои потребности')
        return
    await asyncio.sleep(time_sleep)
    await system_message.delete()
    await send_work(call)


def register_security_work_handler(dp: Dispatcher):
    dp.register_callback_query_handler(work_info, works_callback.filter(event='info', type='3'), chat_type='private')
    dp.register_callback_query_handler(security_start, works_callback.filter(event='start', type='3'), chat_type='private')
    dp.register_callback_query_handler(check_security_answer, works_callback.filter(type='3_check'), chat_type='private')
    dp.register_callback_query_handler(check_fight, works_callback.filter(type='security_fight'), chat_type='private')