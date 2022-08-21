import asyncio

from aiogram import types, Dispatcher
from db.queries.fishing import add_user_fish, get_random_fish

from db.queries.users import get_main_info_fishing, update_event_count, \
    update_event_id, update_user_exp, update_user_variable
from image_generate.works.fishing import generate_fish_image
from keyboards.inline.fishing.fishing_inline import fish_keyboard
from keyboards.inline.fishing.fishing_inline_data import fishing_callback

import pathlib
import random

from misc.user_misc import characteristic_change
from static.text.profile import NEW_LEVEL_TEXT


async def new_event(call):
    db_session = call.message.bot.get('db')
    user_id = call.from_user.id
    event_id = 1 if random.choices([True, False], weights=[60, 40])[0] else 0

    await update_event_id(db_session, user_id, event_id)

    await call.message.answer_photo(open(f'{pathlib.Path().absolute()}/image/fishing/{event_id}.png', 'rb'),
                                    reply_markup=await fish_keyboard())


async def fishing_start(call: types.CallbackQuery):
    await call.answer()
    await call.message.delete()

    user, _, _ = await get_main_info_fishing(call.message.bot.get('db'), call.from_user.id)

    if user.lvl < 15:
        await call.message.answer('Рыбалка открывается на 15 уровне')
        return
    if user.bait <= 0:
        await call.message.answer('У тебя нет наживки, чтобы рыбачить')
        return

    system_message = await call.message.answer('Ты закинул удочку, ждём улов')
    await asyncio.sleep(random.randint(3, 10))
    await new_event(call)
    await system_message.delete()


async def fishing_check(call: types.CallbackQuery, callback_data: dict):
    user_answer = callback_data.get('type')

    if user_answer == 'none':
        await call.answer('Не тыкай сюда', show_alert=True)
        return

    await call.answer()
    await call.message.delete()
    db_session = call.message.bot.get('db')
    user, rod, fishs = await get_main_info_fishing(db_session, call.from_user.id)
    text = ''
    image = False

    if user.event_id == int(user_answer) and int(user_answer) == 1:
        await update_user_variable(db_session, call.from_user.id, 'bait', '-', 1)
        if random.choices([True, False], weights=[15, 85])[0]:
            text = '🔥 Вот это улов\n' \
                   'Ты выловил 1 деталь ⚙️\n' \
                   f'Рыбалка продолжается\n' \
                   f'⚙️ Деталей: {user.rod_detail + 1}\n' \
                   f'🍣 Наживка: {user.bait - 1}\n' \
                   f'🎣 Удочка: {rod.name}\n'
            await update_user_variable(db_session, call.from_user.id, 'rod_detail', '+', 1)
        else:
            weight_fish = random.randint(1, 3) * rod.lvl
            fish = await get_random_fish(db_session, rod.lvl)
            fish = fish[0]
            if fish.price != 0:
                image = True
                if await update_user_exp(db_session, call.from_user.id, '+', 1):
                    await call.message.answer(NEW_LEVEL_TEXT)
                await add_user_fish(db_session, call.from_user.id, fish.id, weight_fish)
                await update_event_count(db_session, call.from_user.id, 'fishing', '+', 1)
                await generate_fish_image(fish.id, call.from_user.id)
            text = f'🔥 Вот это улов\n' \
                   f'{"🐟" if fish.price != 0 else "🗑"} {fish.name} {f"весом {weight_fish} кг. " if fish.price != 0 else ""}\n' \
                   f'Рыбалка продолжается\n' \
                   f'⚙️ Деталей: {user.rod_detail}\n' \
                   f'🍣 Наживка: {user.bait - 1}\n' \
                   f'🎣 Удочка: {rod.name}\n'
    elif user.event_id == int(user_answer) and int(user_answer) == 0:
        text = 'Ех, рыбалка дело не быстрое, ждём дальше'
    else:
        await update_user_variable(db_session, call.from_user.id, 'bait', '-', 1)
        text = 'Ты слишком рано вытащил удочку, на крючке ещё нет рыбы, ты потерял одну наживку\n' \
               f'Рыбалка продолжается\n' \
               f'⚙️ Деталей: {user.rod_detail}\n' \
               f'🍣 Наживка: {user.bait - 1}\n' \
               f'🎣 Удочка: {rod.name}\n'

    if await characteristic_change(db_session, call.from_user.id):
        await call.message.answer('Ты не можешь продолжить рыбалку, проверь свои потребности')
        return
    if user.bait - 1 <= 0:
        await call.message.answer('У тебя закончилась наживка')
        return

    if image:
        system_message = await call.message.answer_photo(open(f'{pathlib.Path().absolute()}/image/fishing/{call.from_user.id}_fishing.png', 'rb'),
                                                         caption=text)
    else:
        system_message = await call.message.answer(text)

    await asyncio.sleep(random.randint(3, 10))
    await system_message.delete()
    await new_event(call)


def register_fishing_handlers(dp: Dispatcher):
    dp.register_callback_query_handler(fishing_start, fishing_callback.filter(event='start_fish', type='start_fish'),
                                       chat_type='private')
    dp.register_callback_query_handler(fishing_check, fishing_callback.filter(event='fishing'), chat_type='private')
