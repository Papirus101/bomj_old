from aiogram import types, Dispatcher
from aiogram.dispatcher.filters import Text
from aiogram.utils.exceptions import BotBlocked
from db.queries.active import get_all_online_users, get_online_by_user

from db.queries.users import add_user, get_user_profile, get_top_users_maxa_event

from image_generate.profile.generate_profile import generate_profile_user

import time
import pathlib
import asyncio

from keyboards.inline.main_inline import profile_keyb

from keyboards.reply.main_keyboard import main_keyboard, potreb_keyb

from static.text.profile import FIRST_START_TEXT, NEW_REFERRAL


async def start_message(message: types.Message):
    db_session = message.bot.get('db')
    db_user = await get_user_profile(db_session, message.from_user.id)
    if db_user is None:
        referral_id = int(message.text.split('_')[1]) if message.text.find('ref_') > -1 else None
        vip = True if referral_id is not None else False
        vip_finish = int(time.time()) + 259200 if vip else 0
        await add_user(db_session, message.from_user.id, message.from_user.full_name, message.from_user.username,
                       referral_id, vip, vip_finish)
        db_user = await get_user_profile(db_session, message.from_user.id)
        if referral_id is not None:
            try:
                await message.bot.send_message(chat_id=referral_id,
                                               text=NEW_REFERRAL.format(username=message.from_user.username,
                                                                        fullname=message.from_user.full_name),
                                               disable_web_page_preview=True,
                                               disable_notification=True)
            except BotBlocked:
                pass
        await message.answer(FIRST_START_TEXT)
        await asyncio.sleep(5)
    try:
        profile_image = await message.bot.get_user_profile_photos(message.from_user.id)
        file_id = profile_image.photos[0][0].file_id
        await message.bot.download_file_by_id(file_id,
                                              f'{pathlib.Path().absolute()}/image/profile/{message.from_user.id}_image.png')
    except:
        pass
    await generate_profile_user(db_session, db_user[0], db_user[1])
    await message.answer('♻️ Загрузка профиля...', reply_markup=main_keyboard())
    await message.answer_photo(
        open(f'{pathlib.Path().absolute()}/image/profile/{message.from_user.id}_profile.png', 'rb'),
        reply_markup=profile_keyb())
    pathlib.Path(f'{pathlib.Path().absolute()}/image/profile/{message.from_user.id}_profile.png').unlink()


async def profile_message(message: types.Message):
    await start_message(message)


async def needs_info(message: types.Message):
    await message.answer('Выбери потребность, которую хочешь восставновить\n\n'
                         'До достижения 15 уровня, восстановление потребностей оплачивает государство',
                         reply_markup=potreb_keyb())


async def online_users(message: types.Message):
    users = await get_all_online_users(message.bot.get('db'))
    await message.answer(f'{len(users)} игроков онлайн 🔴')


async def my_online(message: types.Message):
    user_active = await get_online_by_user(message.bot.get('db'), message.from_user.id)
    total_active = time.gmtime(user_active.total_time)
    await message.answer(f'Твоя статистика:\n'
                         f'📨 Всего сообщений: {user_active.count_message}\n'
                         f'🕓 Всего времени в боте: {time.strftime("%H ч. %M мин. %S сек.", total_active)}')


async def get_id(message: types.Message):
    if message.reply_to_message is not None:
        await message.answer(f'<code>{message.reply_to_message.from_user.id}</code>', reply=True)
    else:
        await message.answer(f'<code>{message.from_user.id}</code>', reply=True)


async def other(message: types.Message):
    await message.answer('В разработке... ( нужны картинки машинок) )')


def register_start_handler(dp: Dispatcher):
    dp.register_message_handler(start_message, commands='start', chat_type='private')
    dp.register_message_handler(profile_message, Text(equals='👤 Профиль'), chat_type='private')
    dp.register_message_handler(needs_info, Text(equals='❤ Потребности'), chat_type='private')
    dp.register_message_handler(online_users, commands='online')
    dp.register_message_handler(my_online, commands='my_online')
    dp.register_message_handler(get_id, commands='id')
    dp.register_message_handler(other, Text(equals='🤔 Остальное'), chat_type='private')
