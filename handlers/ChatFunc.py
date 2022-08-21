import asyncio

from aiogram import Dispatcher, types

import pathlib

from aiogram.dispatcher.filters import Text, IsReplyFilter

from db.queries.users import get_user_profile, get_all_users
from image_generate.profile.generate_profile import generate_profile_user


async def send_all_users_message(message: types.Message):
    users = await get_all_users(message.bot.get('db'))
    for user in users:
        try:
            await message.bot.send_message(chat_id=user.telegram_id, text=message.text.replace('/send', ''))
        except:
            pass
        await asyncio.sleep(1)


async def my_profile(message: types.Message):
    db_session = message.bot.get('db')
    db_user = await get_user_profile(db_session, message.from_user.id)

    try:
        profile_image = await message.bot.get_user_profile_photos(message.from_user.id)
        file_id = profile_image.photos[0][0].file_id
        await message.bot.download_file_by_id(file_id,
                                              f'{pathlib.Path().absolute()}/image/profile/{message.from_user.id}_image.png')
    except:
        pass

    await generate_profile_user(db_session, db_user[0], db_user[1])
    await message.answer_photo(
        open(f'{pathlib.Path().absolute()}/image/profile/{message.from_user.id}_profile.png', 'rb'),
        reply=True)
    pathlib.Path(f'{pathlib.Path().absolute()}/image/profile/{message.from_user.id}_profile.png').unlink()


async def user_profile(message: types.Message):
    user_id = message.reply_to_message.from_user.id
    db_session = message.bot.get('db')
    db_user = await get_user_profile(db_session, user_id)

    await generate_profile_user(db_session, db_user[0], db_user[1])
    await message.answer_photo(
        open(f'{pathlib.Path().absolute()}/image/profile/{user_id}_profile.png', 'rb'),
        reply=True)
    pathlib.Path(f'{pathlib.Path().absolute()}/image/profile/{user_id}_profile.png').unlink()


def register_chat_func_handlers(dp: Dispatcher):
    dp.register_message_handler(user_profile, Text(equals='профиль', ignore_case=True), chat_type='supergroup',
                                is_reply=True)
    dp.register_message_handler(my_profile, Text(equals='профиль', ignore_case=True), chat_type='supergroup', is_reply=False)
    dp.register_message_handler(send_all_users_message, Text(startswith='/send'), chat_type='private')
