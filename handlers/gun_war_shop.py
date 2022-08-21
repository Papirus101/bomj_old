from aiogram import types, Dispatcher
from aiogram.dispatcher.filters import Text
from aiogram.types.input_media import InputMediaPhoto

from db.queries.gun_war import get_current_gun_war, get_gun
from db.queries.users import get_main_user_info, get_user_info_and_gun_war, update_user_balance, update_user_gun_war

from keyboards.inline.gun_war.gun_war_shop_data import gun_war_shop_callback
from keyboards.inline.gun_war.gun_war_shop_inline import get_gun_war_shop_keyboard

from misc.convert_money import convert_stats

from PIL import Image

import pathlib

from misc.vriables import SMILE_MONEY_TYPE


async def generate_image_gun_war_shop(gun_id: int):
    image = Image.open(f'{pathlib.Path().absolute()}/image/gun_war/profile.png')
    gun = Image.open(f'{pathlib.Path().absolute()}/image/gun_war/{gun_id}.png').convert("RGBA")
    gun = gun.resize((384, 384), Image.ANTIALIAS)
    image.paste(gun, (408, 169), gun)
    image.save(f'{pathlib.Path().absolute()}/image/gun_war/{gun_id}_im.png')
    
    
async def get_info_by_gun_id(gun_id: int, db_session, user_id: int):
    user_info = await get_user_info_and_gun_war(db_session, user_id)
    new_gun_info = await get_gun(db_session, gun_id)
    
    if new_gun_info is None:
        return False, False, False
    new_gun_info = new_gun_info[0]

    print(new_gun_info.id)
    
    text = f'<strong>{new_gun_info.name}</strong>\n\n' \
           f'Цена: {convert_stats(m=new_gun_info.price)} {SMILE_MONEY_TYPE.get(str(new_gun_info.money_type))}' \
           f'| у тебя {convert_stats(m=getattr(user_info[0], str(new_gun_info.money_type)))} {SMILE_MONEY_TYPE.get(new_gun_info.money_type)}\n' \
           f'Урон: {new_gun_info.power} 🩸\n' \
           '------------------------------------------------\n' \
           f'Твоё оружие:\n' \
           f'{user_info[1].name}\n' \
           f'Урон: {user_info[1].power} 🩸'
    image = f'{pathlib.Path().absolute()}/image/gun_war/{new_gun_info.id}_im.png'
    keyboard = await get_gun_war_shop_keyboard(gun_id)
    return text, image, keyboard


async def gun_war_shop_start(message: types.Message):
    db_session = message.bot.get('db')
    
    text, image, keyboard = await get_info_by_gun_id(0, db_session, message.from_user.id)
    
    await message.answer_photo(open(image, 'rb'),
                               caption=text,
                               reply_markup=keyboard)
    
    
async def change_page_gun_war_shop(call: types.CallbackQuery, callback_data: dict):
    db_session = call.message.bot.get('db')
    gun_id = int(callback_data.get('event'))
    if gun_id < 0:
        await call.answer('Там больше ничего нет')
        return
    
    text, image, keyboard = await get_info_by_gun_id(gun_id, db_session, call.from_user.id)
    if not text:
        await call.answer('Там больше ничего нет')
        return
    
    await call.answer()
    await call.message.edit_media(InputMediaPhoto(open(image, 'rb'),
                               caption=text),
                               reply_markup=keyboard)
    
    
async def buy_gun_war(call: types.CallbackQuery, callback_data: dict):
    db_session = call.message.bot.get('db')
    gun_id = int(callback_data.get('event'))
    
    user_info = await get_main_user_info(db_session, call.from_user.id)
    new_gun_info = await get_gun(db_session, gun_id)
    new_gun_info = new_gun_info[0]
    
    if getattr(user_info, str(new_gun_info.money_type)) < new_gun_info.price:
        await call.answer('Недостаточно средств для покупки', show_alert=True)
        return
    
    await call.answer()
    await update_user_gun_war(db_session, call.from_user.id, new_gun_info.id)
    await update_user_balance(db_session, call.from_user.id, str(new_gun_info.money_type), '-', new_gun_info.price)
    await call.message.delete()
    await call.message.answer('Оружие успешно приобретено')


def register_shop_gun_war_handlers(dp: Dispatcher):
    dp.register_message_handler(gun_war_shop_start, Text(equals='🔫 Снаряжение'), chat_type='private')
    dp.register_callback_query_handler(change_page_gun_war_shop, gun_war_shop_callback.filter(type='change_gun_shop_shop'), chat_type='private')
    dp.register_callback_query_handler(buy_gun_war, gun_war_shop_callback.filter(type='buy_gun_war'), chat_type='private')
