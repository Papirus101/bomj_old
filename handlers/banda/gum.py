import asyncio
import pathlib
import random

from aiogram import types, Dispatcher

from db.models.user_db import Users
from db.queries.users import get_main_user_info, update_event_id, update_event_count, update_user_variable, \
    update_user_balance
from image_generate.banda.gum import generate_image_gum
from keyboards.inline.banda.banda_inline import gum_main_keyboard, gum_event_keyboard
from keyboards.inline.banda.banda_inline_callback import banda_callback_data
from misc.user_misc import check_user_characteristics, characteristic_change


async def gum_main(call: types.CallbackQuery):
    await call.answer()
    await call.message.delete()
    text = f'🏋️‍♂️ Качалка\n\n' \
           f'Для большего количесто побед в махачах, тебе необходимо не только самое крутое оружие, но и сила персонажа\n' \
           f'Одно занятие в качалке стоит 500 руб. и затрачивает все потребности игрока\n' \
           f'Как и в любом спорте, результат не виден сразу, для достижения результата необходимо отзаниматься хотя бы 5 раз\n\n'
    await call.message.answer_photo(open(f'{pathlib.Path().absolute()}/image/gum/profile.png', 'rb'),
                                    caption=text,
                                    reply_markup=await gum_main_keyboard())


async def gum_event(call: types.CallbackQuery):
    db_session = call.message.bot.get('db')
    user: Users = await get_main_user_info(db_session, call.from_user.id)
    await call.answer()

    if user.money < 500:
        await call.message.answer('Недостаточно средств, одно занятие стоит 500 руб.')
        return

    if not await check_user_characteristics(db_session, call):
        await call.message.answer('Ты не можешь тренироваться, проверь свои показатели')
        return

    event_id = random.randint(1, 3)
    await update_user_balance(db_session, call.from_user.id, 'money', '-', 500)
    await generate_image_gum(event_id, call.from_user.id)
    await call.message.answer_photo(open(f'{pathlib.Path().absolute()}/image/gum/{call.from_user.id}.png', 'rb'),
                                    caption='🥊 Вы выскочили махаца с другим посетителем качалки',
                                    reply_markup=await gum_event_keyboard())
    await update_event_id(db_session, call.from_user.id, event_id)
    pathlib.Path(f'{pathlib.Path().absolute()}/image/gum/{call.from_user.id}.png').unlink()


async def gum_event_check(call: types.CallbackQuery, callback_data: dict):
    await call.answer()
    await call.message.delete()
    db_session = call.message.bot.get('db')
    user_answer = int(callback_data.get('type'))
    user: Users = await get_main_user_info(db_session, call.from_user.id)
    text = ''

    if user.event_id == user_answer:
        text += '🗡 Ты попал прямо в цель'
        await update_event_count(db_session, call.from_user.id, 'gum', '+', 1)
        if (user.info['gum'] + 1) % 5 == 0:
            await update_user_variable(db_session, call.from_user.id, 'power', '+', 1)
            text += '\n🔥 Твои занятия дают результат ➕ 1️⃣ к урону 🩸'
    else:
        text = '\n😞 Ты промазал('
    if await characteristic_change(db_session, call.from_user.id):
        await call.message.answer('❌ Ты не можешь продолжать тренировки, проверь свои потребности')
        return

    system_message = await call.message.answer(text)

    await asyncio.sleep(random.randint(3, 7))
    await gum_event(call)
    await system_message.delete()


def register_gum_handlers(dp: Dispatcher):
    dp.register_callback_query_handler(gum_main, banda_callback_data.filter(event='gum', type='gum'),
                                       chat_type='private')
    dp.register_callback_query_handler(gum_event, banda_callback_data.filter(event='start_gum', type='start_gum'),
                                       chat_type='private')
    dp.register_callback_query_handler(gum_event_check, banda_callback_data.filter(event='gum_check'),
                                       chat_type='private')
