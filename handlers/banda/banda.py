import asyncio
import pathlib
import random

import emoji
import re

from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import InputMediaPhoto

from db.models.user_db import Users
from db.queries.banda_q import get_all_bands, get_banda_info, get_info_main_banda, check_banda_name_and_smile, \
    create_banda, get_bands_event, delete_banda
from db.queries.users import get_main_user_info, update_user_balance, get_user_info_main_banda, get_user_profile, \
    set_user_variable, get_top_users_by_maxa, get_random_user_for_maxa, get_user_stuff_and_main_info, \
    update_event_count, update_user_exp, get_all_users_from_banda, update_user_variable
from image_generate.banda.banda_menu import generate_image_banda
from image_generate.banda.maxa import maxa_image_generate, generate_winner_maxa_image

from image_generate.profile.generate_profile import generate_profile_user

from keyboards.inline.banda.banda_inline import main_banda_keyboard, new_request_to_banda_keyboard, \
    main_menu_banda_keyboard, maxa_next_keyboard, kick_user_from_banda, choice_user_to_kick_keyboard, \
    variable_leave_from_banda_keyboard
from keyboards.inline.banda.banda_inline_callback import banda_callback_data

# ------------------------------ Список банд ------------------------------ #
from misc.states.banda import BandaCreateState
from misc.vriables import MEDAL_TYPES
from static.text.profile import NEW_LEVEL_TEXT


async def banda_info_text_and_keyboard(db_session, user_id: int, page: int):
    data = await get_user_info_main_banda(db_session, user_id)
    print(page)
    bands = await get_all_bands(db_session, page)

    if len(bands) < 1 and page != 0:
        return None, None

    bands_list = ''
    text = '<strong>☠️ Банды</strong>\n\n' \
           'Участвуй в махачах между бандами, борись за лидерство, зарабатывай рейтинг и поднимайся с низов до тотального лидерства\n' \
           'Для отправки запроса на вступление в банду, просто нажми на соответсвующую кнопку\n\n' \
           'Для создания своей банды тебе надо заплатить смотрящим 50.00М руб.💰\n\n' \
           'Список банд:\n'

    if len(bands) < 1:
        bands_list = 'Банд нет('
    else:
        for banda in bands:
            banda_info, count_users = banda
            bands_list += f'{"✅" if count_users < 10 else "❎"} [{count_users}/10] {banda_info.smile} {banda_info.name} | {banda_info.rating} ⭐️\n'

    text += bands_list
    keyboard = await main_banda_keyboard(data, page, bands)
    return text, keyboard


async def banda_info(message: types.Message):
    db_session = message.bot.get('db')
    text, keyboard = await banda_info_text_and_keyboard(db_session, message.from_user.id, 0)

    await message.answer(text, reply_markup=keyboard)


async def change_page_banda_info(call: types.CallbackQuery, callback_data: dict):
    db_session = call.message.bot.get('db')
    page = int(callback_data.get('type'))

    if page < 0:
        await call.answer('Там больше ничего нет')
        return

    text, keyboard = await banda_info_text_and_keyboard(db_session, call.from_user.id, page)

    if text is None or keyboard is None:
        await call.answer('Там больше ничего нет')
        return

    await call.answer()
    await call.message.answer(text, reply_markup=keyboard)


# ----------------------------- Принятие или отклонение новой заявки в банду ----------------------------- №
async def send_request_to_banda(call: types.CallbackQuery, callback_data: dict):
    db_session = call.message.bot.get('db')
    banda_id = int(callback_data.get('type'))
    user, house = await get_user_profile(db_session, call.from_user.id)

    if user.banda is not None and user.banda != 0:
        await call.answer('Ты уже состоишь в банде, для отправки запроса в другую банду, выйди из текущей',
                          show_alert=True)
        return

    banda, count_users = await get_banda_info(db_session, banda_id)

    if count_users >= 10:
        await call.answer('В банде уже максимальное кол-во пользователей', show_alert=True)
        return

    await generate_profile_user(db_session, user, house)
    await call.message.bot.send_photo(chat_id=banda.admin, photo=open(
        f'{pathlib.Path().absolute()}/image/profile/{user.telegram_id}_profile.png', 'rb'),
                                      caption='Новый игрок хочет вступить в твою банду, тебе надо принять решение',
                                      reply_markup=await new_request_to_banda_keyboard(call.from_user.id, banda.id))
    await call.message.answer('Заявка в банду отправлена, ожидай ответа главы банды.')


async def accept_new_user_in_band(call: types.CallbackQuery, callback_data: dict):
    await call.answer('Решение принято')
    await call.message.delete()

    db_session = call.message.bot.get('db')
    user_id = int(callback_data.get('type').split('_')[1])
    event = callback_data.get('type').split('_')[0]
    banda_id = int(callback_data.get('type').split('_')[-1])
    banda, count_users = await get_banda_info(db_session, banda_id)
    user = await get_main_user_info(db_session, user_id)

    if event == 'accept' and user.banda is not None and user.banda != 0:
        await call.message.answer('Игрок уже вступил в другую банду')
        return
    if event == 'pass':
        await call.message.bot.send_message(chat_id=user_id, text=f'Тебя не взяли в банду {banda.name}')
        return

    await set_user_variable(db_session, user_id, 'banda', banda_id)
    await call.message.bot.send_message(chat_id=user_id, text=f'Тебя приняли в банду {banda.name}')


# ----------------------------- Создание новой банды ----------------------------- #
async def create_new_banda(call: types.CallbackQuery):
    db_session = call.message.bot.get('db')
    user = await get_main_user_info(db_session, call.from_user.id)

    if user.banda is not None and user.banda != 0:
        await call.answer('Ты уже состоишь в банде')
        return
    if user.money < 50_000_000:
        await call.answer('Недостаточно средств')
        return

    await call.answer()
    await call.message.answer('Пришли мне название банды или 0 для отмены')
    await BandaCreateState.GetBandaName.set()


async def get_name_new_banda(message: types.Message, state: FSMContext):
    banda_name = message.text
    if banda_name == '0':
        await message.answer('Отмена')
        await state.finish()
        return
    if await check_banda_name_and_smile(message.bot.get('db'), banda_name, 'name') is not None:
        await message.answer('Это название банды уже занято, попробуй другое или пришли мне 0 для отмены')
        return
    await state.update_data(banda_name=banda_name)
    await message.answer('Отлично, теперь выбери смайлик для своей банды и пришли мне его\n'
                         'Или пришли мне 0 для отмены')
    await BandaCreateState.GetBandaSmile.set()


async def get_smile_new_banda(message: types.Message, state: FSMContext):
    smile = message.text

    user = await get_main_user_info(message.bot.get('db'), message.from_user.id)
    if user.money < 50_000_000:
        await message.answer('Недостаточно средств')
        return

    if smile == '0':
        await message.answer('Отмена')
        await state.finish()
        return
    if len(re.findall(r':\w+:', emoji.demojize(smile))) < 0 or len(
            re.findall(r':\w+:', emoji.demojize(smile))) > 1:
        await message.answer('Пришли мне 1 смайлик или 0 для отмены')
        return

    smile = emoji.emojize(re.findall(r':\w+:', emoji.demojize(smile))[0])

    if await check_banda_name_and_smile(message.bot.get('db'), smile, 'smile') is not None:
        await message.answer('Это название банды уже занято, попробуй другое или пришли мне 0 для отмены')
        return

    data = await state.get_data()
    new_banda = await create_banda(message.bot.get('db'), message.from_user.id, data.get('banda_name'), smile)
    await set_user_variable(message.bot.get('db'), message.from_user.id, 'banda', new_banda.id)
    await update_user_balance(message.bot.get('db'), message.from_user.id, 'money', '-', 50_000_000)
    await message.answer(f'{smile} {data.get("banda_name")} успешно создана')
    await state.finish()


# ------------------------------ Главное меню банды -------------------------------------- #
async def my_banda_menu(call: types.CallbackQuery):
    db_session = call.message.bot.get('db')
    user = await get_main_user_info(db_session, call.from_user.id)
    banda_info = await get_info_main_banda(db_session, user.banda)
    top_users = await get_top_users_by_maxa(db_session, user.banda)

    await generate_image_banda(user, banda_info, top_users)

    await call.answer()
    await call.message.answer_photo(open(f'{pathlib.Path().absolute()}/image/banda/{banda_info.banda_id}.png', 'rb'),
                                    reply_markup=await main_menu_banda_keyboard())


# ------------------------------ Махачи -------------------------------------- #
async def maxa_start(call: types.CallbackQuery):
    db_session = call.message.bot.get('db')
    await call.answer()

    user = await get_user_stuff_and_main_info(db_session, call.from_user.id)
    enemy_info = await get_random_user_for_maxa(db_session, call.from_user.id)
    enemy = await get_user_stuff_and_main_info(db_session, enemy_info.telegram_id)

    await maxa_image_generate(db_session, user.name, enemy.name, user, enemy)
    image = f'{pathlib.Path().absolute()}/image/banda/{call.from_user.id}.png'
    await call.message.edit_media(InputMediaPhoto(open(image, 'rb'),
                                                  caption=f'Вы выскочили МАХАЦА с {enemy.name}\n\n'
                                                          f'⚔️ Твоё оружие: {user.name_gun} {user.power_gun} 🩸 + {user.power} 👊\n'
                                                          f'⚔️ Оружие соперника: {enemy.name_gun} {user.power_gun} 🩸 + {enemy.power} 👊'))

    await asyncio.sleep(1, 3)

    total_damage = user.power + user.power_gun + enemy.power + enemy.power_gun
    chance_winner_user = (user.power + user.power_gun) / total_damage * 100
    chance_winner_enemy = (enemy.power + enemy.power_gun) / total_damage * 100
    winner = random.choices([user, enemy], weights=[chance_winner_user, chance_winner_enemy])[0]
    await generate_winner_maxa_image(True if winner.telegram_id == user.telegram_id else False, user.telegram_id)

    if winner.telegram_id == user.telegram_id:
        await update_event_count(db_session, user.telegram_id, 'maxa_all', '+', 1)
        await update_event_count(db_session, user.telegram_id, 'maxa_week', '+', 1)
        if (user.info.get('maxa_all') + 1) % 5 == 0:
            if await update_user_exp(db_session, user.telegram_id, '+', 1):
                await call.message.answer(NEW_LEVEL_TEXT)
        user = await get_user_stuff_and_main_info(db_session, call.from_user.id)

    await call.message.edit_media(
        InputMediaPhoto(media=open(image, 'rb'), caption=f'Вы выскочили МАХАЦА с {enemy.name}\n\n'
                                                         f'⚔️ Твоё оружие: {user.name_gun} {user.power_gun} 🩸 + {user.power} 👊\n'
                                                         f'⚔️ Оружие соперника: {enemy.name_gun} {user.power_gun} 🩸 + {enemy.power} 👊\n\n'
                                                         f'🏆 В этой не лёгкой битве победителем стал {winner.name}\n'
                                                         f'⚔️🏆 Побед за неделю: {user.info.get("maxa_week")}\n'
                                                         f'⚔️🏆 Побед за всё время: {user.info.get("maxa_all")}'),
        reply_markup=await maxa_next_keyboard())


async def event_info(call: types.CallbackQuery):
    await call.answer()
    db_session = call.message.bot.get('db')
    bands_list = await get_bands_event(db_session)
    text = 'Лидирующие банды в текущем соревновании:\n'
    for i, banda in enumerate(bands_list, start=1):
        text += f'{MEDAL_TYPES.get(i)} {banda.smile} {banda.name} {banda.count_maxa} ⚔️\n'
    await call.message.answer(text)


async def get_users_banda(db_session, user_id: int):
    user: Users = await get_main_user_info(db_session, user_id)

    if user.banda is None or user.banda == 0:
        return None, None, None

    users = await get_all_users_from_banda(db_session, user.banda)
    text = ''
    for pos, user_banda in enumerate(users, start=1):
        text += f'{MEDAL_TYPES.get(pos, "🎖")} {user_banda.name} | всего побед: {user_banda.info.get("maxa_all", 0)} ⚔️ | за неделю {user_banda.info.get("maxa_week", 0)} ⚔️\n'
    return user, users, text


async def users_banda(call: types.CallbackQuery):
    await call.answer()
    db_session = call.message.bot.get('db')
    user, users, text = await get_users_banda(db_session, call.from_user.id)
    if user is None:
        await call.message.answer("Ты не состоишь в банде")
    await call.message.answer(text, reply_markup=await kick_user_from_banda(users[0].banda_admin))


async def choice_user_kick(call: types.CallbackQuery):
    await call.answer()
    await call.message.delete()
    db_session = call.message.bot.get('db')
    user, users, text = await get_users_banda(db_session, call.from_user.id)

    if user is None:
        await call.message.answer("Ты не состоишь в банде")

    await call.message.answer('Выбери пользователя, которого хочешь выгнать из банды\n'
                              f'{text}',
                              reply_markup=await choice_user_to_kick_keyboard(users))


async def kick_user(call: types.CallbackQuery, callback_data: dict):
    await call.answer()
    user_id = int(callback_data.get('type'))
    if user_id == call.from_user.id:
        await call.message.answer('Ты не можешь выгнать сам себя')
        return
    await set_user_variable(call.message.bot.get('db'), user_id, 'banda', None)
    await call.message.bot.send_message(chat_id=user_id, text='Тебя выгнали из банды')
    await call.message.answer('Игрок изгнан из банды')


async def leave_from_banda(call: types.CallbackQuery):
    await call.answer()
    await call.message.answer('Ты точно хочешь покинуть банду?',
                              reply_markup=await variable_leave_from_banda_keyboard())


async def accept_leave_from_banda(call: types.CallbackQuery):
    await call.answer()
    await call.message.delete()
    db_session = call.message.bot.get('db')
    user = await get_main_user_info(db_session, call.from_user.id)

    if user.banda is None or user.banda == 0:
        await call.message.answer('Ты не в банде')
        return

    banda, count_users = await get_banda_info(db_session, user.banda)

    if banda.admin == user.telegram_id:
        users = await get_all_users_from_banda(db_session, user.banda)
        for user_banda in users:
            await set_user_variable(db_session, user_banda[0], 'banda', None)
            if user_banda[0] != banda.admin:
                await call.message.bot.send_message(user_banda[0], 'Глава банды ушёл в нибытие, ваша группировка распалась')
                await asyncio.sleep(0.5)
        await delete_banda(db_session, banda.id)
    else:
        await set_user_variable(db_session, call.from_user.id, 'banda', None)
        await call.message.answer('Ты покинул банду')
        await call.message.bot.send_message(banda.admin, f'{user.name} покинул банду')


async def no_leave_from_banda(call: types.CallbackQuery):
    await call.answer()
    await call.message.delete()
    await call.message.answer('Ну и правильно)')




def register_banda_handlers(dp: Dispatcher):
    # ------------------------------ Список банд ------------------------------ #
    dp.register_message_handler(banda_info, Text(equals='☠ Банда'), chat_type='private')
    dp.register_callback_query_handler(change_page_banda_info,
                                       banda_callback_data.filter(event='change_page'),
                                       chat_type='private')
    # ----------------------------- Принятие или отклонение новой заявки в банду ----------------------------- №
    dp.register_callback_query_handler(send_request_to_banda, banda_callback_data.filter(event='send_request_banda'),
                                       chat_type='private')
    dp.register_callback_query_handler(accept_new_user_in_band, banda_callback_data.filter(event='accept_new_user'),
                                       chat_type='private')
    # ------------------------------ Главное меню банды -------------------------------------- #
    dp.register_callback_query_handler(my_banda_menu, banda_callback_data.filter(event='my_band', type='my_band'),
                                       chat_type='private')
    # ----------------------------- Создание новой банды ----------------------------- #
    dp.register_callback_query_handler(create_new_banda,
                                       banda_callback_data.filter(event='create_banda', type='create_banda'),
                                       chat_type='private')
    dp.register_message_handler(get_name_new_banda, state=BandaCreateState.GetBandaName, chat_type='private')
    dp.register_message_handler(get_smile_new_banda, state=BandaCreateState.GetBandaSmile, chat_type='private')
    # ------------------------------ Махачи -------------------------------------- #
    dp.register_callback_query_handler(maxa_start, banda_callback_data.filter(event='maxa_start', type='maxa_start'),
                                       chat_type='private')
    # ------------------------------ ТОП банд в соревновании -------------------------------------- #
    dp.register_callback_query_handler(event_info, banda_callback_data.filter(event='event', type='event'),
                                       chat_type='private')
    # ------------------------------ Пользователи в банде -------------------------------------- #
    dp.register_callback_query_handler(users_banda, banda_callback_data.filter(event='banda_users', type='banda_users'),
                                       chat_type='private')
    # ------------------------------ Выгнать пользователя -------------------------------------- #
    dp.register_callback_query_handler(choice_user_kick, banda_callback_data.filter(event='kick_user'),
                                       chat_type='private')
    dp.register_callback_query_handler(kick_user, banda_callback_data.filter(event='choice_kick_user'),
                                       chat_type='private')
    # ------------------------------ Выйти из банды -------------------------------------- #
    dp.register_callback_query_handler(leave_from_banda, banda_callback_data.filter(event='leave_from_banda',
                                                                                    type='leave_from_banda'),
                                       chat_type='private')
    dp.register_callback_query_handler(accept_leave_from_banda, banda_callback_data.filter(event='yes_leave',
                                                                                           type='yes_leave'),
                                       chat_type='private')
    dp.register_callback_query_handler(no_leave_from_banda, banda_callback_data.filter(event='no_leave',
                                                                                       type='no_leave'),
                                       chat_type='private')
