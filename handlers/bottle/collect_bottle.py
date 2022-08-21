import asyncio
import pathlib
import random
from typing import Optional

from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text

from db.models.user_db import Users
from db.queries.users import get_main_user_info, update_user_balance, update_event_id, update_user_exp

from image_generate.works.collect_bottle import generate_collect_bottle_image

from keyboards.inline.main_callback import profile_callback
from keyboards.inline.main_inline import change_bottle_keyboard
from keyboards.inline.works.works_inline import work_check_keyboard_generator
from keyboards.inline.works.works_data import works_callback

from misc.convert_money import convert_stats
from misc.states.settings_states import ChangeBottleState
from misc.user_misc import get_total_amount, text_user_balance, characteristic_change, check_user_characteristics
from misc.vriables import COLLECT_BOTTLE_KEYBOARD
from static.text.profile import NEW_LEVEL_TEXT


async def send_event(call: Optional[types.CallbackQuery] = None, message: Optional[types.Message] = None,
                     db_session=None):
    event_id = random.randint(1, 6)

    user_id = call.from_user.id if call is not None else message.from_user.id
    keyboard = await work_check_keyboard_generator(COLLECT_BOTTLE_KEYBOARD, 'collect_bottle', 'Уйти со свалки', True)

    await update_event_id(db_session, user_id, event_id)
    await generate_collect_bottle_image(event_id, user_id)

    if call is not None:
        await call.message.answer_photo(open(f'{pathlib.Path().absolute()}/image/bottle/{user_id}_bottle.png', 'rb'),
                                        reply_markup=keyboard)
    else:
        await message.answer_photo(open(f'{pathlib.Path().absolute()}/image/bottle/{user_id}_bottle.png', 'rb'),
                                   reply_markup=keyboard)
    pathlib.Path(f'{pathlib.Path().absolute()}/image/bottle/{user_id}_bottle.png').unlink()


async def collect_bottle_info(message: types.Message):
    await message.answer('Ты отправился на местную свалку, для сбора бутылок.\n'
                         'Посмотрим, какие приключения судьба приготовила для тебя на этот раз')

    if not await check_user_characteristics(message.bot.get('db'), message):
        return

    await asyncio.sleep(random.randint(3, 10))
    await send_event(message=message, db_session=message.bot.get('db'))


async def check_bottle_collect_answer(call: types.CallbackQuery, callback_data: dict):
    db_session = call.message.bot.get('db')
    user_answer = int(callback_data.get('event'))
    user: Users = await get_main_user_info(db_session, call.from_user.id)
    random_events_text = ''

    await call.answer()
    await call.message.delete()

    if user.event_id == user_answer:
        count_bottle = user.lvl * random.randint(3, 10) if user.lvl <= 40 else user.lvl * random.randint(1, 2)
        total_reward, nalog = await get_total_amount(count_bottle, user.vip)
        if nalog > 0:
            random_events_text = f'💥 Местные бомжи отжали у тебя {convert_stats(money=nalog)} бут.'
        await update_user_balance(db_session, call.from_user.id, 'bottle', '+', total_reward)
        if await update_user_exp(db_session, call.from_user.id, '+', 1, user.vip):
            await call.message.answer(NEW_LEVEL_TEXT)
        event_text = f'🍾 Ты нашёл {convert_stats(money=total_reward)} бут.'
    else:
        event_text = 'Ты наклонился к бутылке, но не удержал равновесие и уткнулся носом прямо в фекалии местного кота'

    time_to_sleep = random.randint(3, 10)
    system_message = await call.message.answer(f'{event_text}\n'
                                               f'{random_events_text}\n'
                                               '🏃 Ты отправился дальше по свалке в поисках бутылок\n'
                                               f'Вот уже на горизонте ты увидел новую бутылку, ты дойдёшь до неё ~ за {time_to_sleep} сек.')
    if await characteristic_change(db_session, call.from_user.id):
        await call.message.answer('Ты не можешь продолжить работу, проверь свои потребности')
        return
    await asyncio.sleep(time_to_sleep)
    await send_event(call=call, db_session=db_session)
    await system_message.delete()


def register_collect_bottle_handler(dp: Dispatcher):
    dp.register_message_handler(collect_bottle_info, Text(equals='🍾 Собирать бутылки'), chat_type='private')
    dp.register_callback_query_handler(check_bottle_collect_answer, works_callback.filter(type='collect_bottle_check'),
                                       chat_type='private')
