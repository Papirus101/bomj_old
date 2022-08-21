from aiogram import types, Dispatcher
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher import FSMContext
from aiogram.types.input_media import InputMediaPhoto

from misc.convert_money import convert_stats

import pathlib

from db.queries.house import get_house_store
from db.queries.users import get_main_user_info, update_user_balance, update_user_house

from keyboards.inline.house_store.house_store_inline import house_store_keyboard
from keyboards.inline.house_store.house_store_data import house_store_callback_data
from misc.vriables import SMILE_MONEY_TYPE


async def get_info_house(db_session, house_id: int, user_id: int):
    house = await get_house_store(db_session, house_id)
    if not house:
        return False, False
    user = await get_main_user_info(db_session, user_id)
    text = f'🏚{house.name}\n\n' \
           f'{SMILE_MONEY_TYPE.get(house.money_type)} Цена: {convert_stats(money=house.price)}' \
           f'| У тебя {convert_stats(money=getattr(user, str(house.money_type)))} {SMILE_MONEY_TYPE.get(house.money_type)}\n' \
           f'👨 Работников: {house.bomj}\n' \
           f'📊 Необходимый уровень: {house.lvl} | Твой уроовень: {user.lvl}'
    image = f'{pathlib.Path().absolute()}/image/profile/{house.id}.png'
    return text, image


async def house_store_main(message: types.Message):
    db_session = message.bot.get('db')

    text, image = await get_info_house(db_session, 0, message.from_user.id)
    await message.answer_photo(open(image, 'rb'),
                               caption=text,
                               reply_markup=await house_store_keyboard(0))


async def next_house(call: types.CallbackQuery, callback_data: dict):
    db_session = call.message.bot.get('db')

    house_id = callback_data.get('event')
    text, image = await get_info_house(db_session, int(house_id), call.from_user.id)
    if not text and not image or int(house_id) < 0:
        await call.answer('Там больше ничего нет')
        return
    await call.answer()
    await call.message.edit_media(InputMediaPhoto(open(image, 'rb'), caption=text),
                                  reply_markup=await house_store_keyboard(int(house_id)))


async def buy_house(call: types.CallbackQuery, callback_data: dict):
    db_session = call.message.bot.get('db')

    house_id = int(callback_data.get('event'))
    house = await get_house_store(db_session, house_id)
    user = await get_main_user_info(db_session, call.from_user.id)
    if getattr(user, str(house.money_type)) < house.price:
        await call.answer('Недостаточно средств', show_alert=True)
        return
    await call.answer()
    await call.message.delete()
    await update_user_house(db_session, call.from_user.id, house.id)
    await update_user_balance(db_session, call.from_user.id, str(house.money_type), '-', house.price)
    await call.message.answer_photo(open(f'{pathlib.Path().absolute()}/image/profile/{house.id}.png', 'rb'),
                                    caption='Жильё успешно приобретино')


def register_house_store_handler(dp: Dispatcher):
    dp.register_message_handler(house_store_main, Text(equals='🏚 Жильё'), chat_type='private')
    dp.register_callback_query_handler(next_house, house_store_callback_data.filter(type='house_store_page'),
                                       chat_type='private')
    dp.register_callback_query_handler(buy_house, house_store_callback_data.filter(type='buy_house'),
                                       chat_type='private')
