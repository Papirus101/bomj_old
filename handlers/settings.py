from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext

import re
import pathlib
from PIL import Image

from db.queries.users import change_close_profile_user, change_user_name, \
    get_user_close_profile, get_user_profile

from keyboards.inline.main_callback import profile_callback
from keyboards.inline.main_inline import settings_keyboard
from misc.states.settings_states import SettingsState

async def settings_main(call: types.CallbackQuery):
    db_session = call.message.bot.get('db')
    user = await get_user_close_profile(db_session, call.from_user.id)
    
    close_text = '🔓 На данный момент твой профиль закрыт и его могут видеть только ВИП игроки'
    open_text = '🔓 На данный момент твой профиль открыт и его могут видеть все игроки'
    
    await call.message.answer('⚙️ <strong>Настройки</strong>\n\n'
                              f'{close_text if user else open_text}',
                              reply_markup=await settings_keyboard(user))
    
    
async def close_profile(call: types.CallbackQuery):
    db_session = call.message.bot.get('db')
    
    await call.answer()
    await change_close_profile_user(db_session, call.from_user.id, True)
    await call.message.edit_text('⚙️ <strong>Настройки</strong>\n\n'
                                 '🔓 На данный момент твой профиль закрыт и его могут видеть только ВИП игроки',
                                 reply_markup=await settings_keyboard(True))
    
    
async def open_profile(call: types.CallbackQuery):
    db_session = call.message.bot.get('db')
    
    await call.answer()
    await change_close_profile_user(db_session, call.from_user.id, False)
    await call.message.edit_text('⚙️ <strong>Настройки</strong>\n\n'
                                 '🔓 На данный момент твой профиль открыт и его могут видеть все игроки',
                                 reply_markup=await settings_keyboard(False))
    

async def change_name(call: types.CallbackQuery):
    await call.message.answer('Пришли мне новое имя персонажа\n'
                              'Имя должно состоять только из букв русского или английского алфавита. Максимальная длинна - 15 символов | Минимальная - 5\n'
                              'Или пришли мне 0 для отмены')
    await SettingsState.ChangeUserName.set()
    
    
async def get_new_user_name(message: types.Message, state: FSMContext):
    if message.text == '0':
        await message.answer('Отмена')
        await state.finish()
        return
    
    db_session = message.bot.get('db')
    new_name = message.text.strip()
    new_name = ''.join(re.findall(r'[А-яA-z\s]', new_name))
    
    if not new_name.isalpha() or len(new_name) > 15 or len(new_name) < 5:
        await message.answer('Ты использовал недопустимые символы в имени или оно не подходит по длинне\n'
                             'Минимальное кол-во символов 5, максимальное 15\n'
                             'Попробуй ещё раз или пришли мне 0 для отмены')
        return
    await change_user_name(db_session, message.from_user.id, new_name)
    await message.answer(f'Ты изменил имя персонажа на {new_name}')
    await state.finish()


async def change_profile_image(call: types.CallbackQuery):
    db_session = call.message.bot.get('db')
    
    user = await get_user_profile(db_session, call.from_user.id)
    user = user[0]
    
    if not user.custom_image:
        await call.answer('Тебе недоступна установка индивидуального изображения')
        return
    
    await call.answer()
    await call.message.answer('Пришли мне изображение размером 800х500 или 0 для отмены')
    await SettingsState.GetUserImage.set()
    

async def get_custom_image(message: types.Message, state: FSMContext):
    await message.photo[-1].download(f'{pathlib.Path().absolute()}/image/profile/{message.from_user.id}.png')
    im = Image.open(f'{pathlib.Path().absolute()}/image/profile/{message.from_user.id}.png')
    w, h = im.size
    if w < 700 or w > 900 or h < 400 or h > 600:
        await message.answer('Изображение не подходит по размеру\n'
                             'Размер изображения должен быть 800х500\n'
                             'Для отмены пришли не 0')
        pathlib.Path(f'{pathlib.Path().absolute()}/image/profile/{message.from_user.id}.png').unlink()
    else:
        await message.answer('Изображение успешно установлено')
        await state.finish()    


async def cancel_user_photo(message: types.Message, state: FSMContext):
    if message.text == '0':
        await state.finish()
        await message.answer('Отмена')
    else:
        await message.answer('Пришли мне изображение размером 800х500 или 0 для отмены')


def register_settings_handler(dp: Dispatcher):
    dp.register_callback_query_handler(settings_main, profile_callback.filter(event='settings'), chat_type='private')
    dp.register_callback_query_handler(close_profile, profile_callback.filter(event='close_profile'), chat_type='private')
    dp.register_callback_query_handler(open_profile, profile_callback.filter(event='open_profile'), chat_type='private')
    #--------------------------------------------- CHANGE NAME -------------------------------------------------------#
    dp.register_callback_query_handler(change_name, profile_callback.filter(event='change_name'), chat_type='private')
    dp.register_message_handler(get_new_user_name, state=SettingsState.ChangeUserName, chat_type='private')
    #--------------------------------------------- CHANGE IMAGE -------------------------------------------------------#
    dp.register_callback_query_handler(change_profile_image, profile_callback.filter(event='change_photo'), chat_type='private')
    dp.register_message_handler(get_custom_image, state=SettingsState.GetUserImage, content_types=types.ContentTypes.PHOTO,
                                chat_type='private')
    dp.register_message_handler(cancel_user_photo, state=SettingsState.GetUserImage, chat_type='private')