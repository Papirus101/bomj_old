import asyncio
import pathlib
import random

from aiogram import types, Dispatcher

from db.models.user_db import Users
from db.queries.users import get_main_user_info, update_event_id, update_user_balance, update_user_exp, \
    update_works_count
from image_generate.works.sort_trash import generate_image
from keyboards.inline.works.works_data import works_callback
from keyboards.inline.works.works_inline import start_work_keyb, work_check_keyboard_generator
from misc.convert_money import convert_stats
from misc.user_misc import get_top_by_works, check_user_characteristics, get_total_amount, characteristic_change
from misc.vriables import SORT_TRASH_WORK_KEYBOARD
from static.text.profile import NEW_LEVEL_TEXT


async def work_info(call: types.CallbackQuery, callback_data: dict):
    db_session = call.message.bot.get('db')
    await call.answer()
    await call.message.delete()
    work = callback_data.get('type')
    user = await get_main_user_info(db_session, call.from_user.id)
    await call.message.answer_photo(open(f'{pathlib.Path().absolute()}/image/works/sort/zavod_info.png', 'rb'),
                                    caption="🗑 Тебя отправили на местный завод по переработке мусора для сортировки.\n"
                                            f"Тебе платят за каждые 3 правильно отсортированные еденицы мусора {convert_stats(money=user.lvl * 25)} руб.\n\n"
                                            "<code>По мере прокачки персонажа, ты сможешь устраиваться на более "
                                            "прибыльные работы</code>\n\n"
                                            f'{await get_top_by_works(db_session, work)}\n',
                                    reply_markup=await start_work_keyb(work))


async def send_work(call: types.CallbackQuery):
    db_session = call.message.bot.get('db')
    event_id = random.randint(1, 3)
    await update_event_id(db_session, call.from_user.id, event_id)
    await generate_image(event_id, call.from_user.id)
    await call.message.answer_photo(
        open(f'{pathlib.Path().absolute()}/image/works/sort/{call.from_user.id}_sort.png', 'rb'),
        reply_markup=await work_check_keyboard_generator(SORT_TRASH_WORK_KEYBOARD, '4', 'Уволиться'))
    pathlib.Path(f'{pathlib.Path().absolute()}/image/works/sort/{call.from_user.id}_sort.png').unlink()


async def sort_trash_start(call: types.CallbackQuery):
    db_session = call.message.bot.get('db')
    await call.answer()
    await call.message.delete()
    if not await check_user_characteristics(db_session, call):
        return
    await update_event_id(db_session, call.from_user.id, 0)
    await send_work(call)


async def sort_trash_check(call: types.CallbackQuery, callback_data: dict):
    db_session = call.message.bot.get('db')
    user_answer = int(callback_data.get('event'))
    work = callback_data.get('type').split('_')[0]
    random_events_text = ''
    reward_text = ''
    user: Users = await get_main_user_info(db_session, call.from_user.id)
    time_sleep = random.randint(3, 7)
    try:
        total_sorted = dict(user.info).get('works').get(work)
    except:
        total_sorted = 1

    await call.answer()
    await call.message.delete()

    if user_answer == user.event_id:
        await update_works_count(db_session, call.from_user.id, work)
        if total_sorted is not None and (total_sorted + 1) % 3 == 0:
            total_reward, nalog = await get_total_amount(user.lvl * 20 if user.lvl > 0 else 20, user.vip)
            reward_text = f', твой заработок составил {convert_stats(money=total_reward)} руб.'
            if nalog > 0:
                random_events_text = f'💥 Ты заплатил налог государству {convert_stats(money=nalog)} руб.'
            await update_user_balance(db_session, call.from_user.id, 'money', '+', total_reward)
            if await update_user_exp(db_session, call.from_user.id, '+', 1, user.vip):
                await call.message.answer(NEW_LEVEL_TEXT)
        system_message = await call.message.answer(f'Ты усешно отсортировал данный тебе мусор{reward_text}\n'
                                  f'{random_events_text}\n'
                                  f'<code>🏃 Следующий мусор уже подъезжает, подожди {time_sleep} сек.</code>')
    else:
        system_message = await call.message.answer('Ты не правильно отсортировал данный тебе мусор.')
    if await characteristic_change(db_session, call.from_user.id):
        await call.message.answer('Ты не можешь продолжить работу, проверь свои потребности')
        return
    await asyncio.sleep(time_sleep)
    await system_message.delete()
    await send_work(call)


def register_sort_rash_work_handler(dp: Dispatcher):
    dp.register_callback_query_handler(work_info, works_callback.filter(event='info', type='4'), chat_type='private')
    dp.register_callback_query_handler(sort_trash_start, works_callback.filter(event='start', type='4'), chat_type='private')
    dp.register_callback_query_handler(sort_trash_check, works_callback.filter(type='4_check'), chat_type='private')
