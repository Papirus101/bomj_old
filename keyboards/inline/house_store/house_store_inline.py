from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from keyboards.inline.house_store.house_store_data import house_store_callback_data


async def house_store_keyboard(house_id: int):
    menu = InlineKeyboardMarkup(row_width=2)
    previous = InlineKeyboardButton('<<', callback_data=house_store_callback_data.new(house_id - 1, 'house_store_page'))
    next = InlineKeyboardButton('>>', callback_data=house_store_callback_data.new(house_id + 1, 'house_store_page'))
    buy = InlineKeyboardButton('Купить', callback_data=house_store_callback_data.new(house_id, 'buy_house'))
    menu.row(buy)
    menu.row(previous, next)
    return menu