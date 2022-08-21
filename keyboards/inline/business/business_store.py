from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from keyboards.inline.business.business_store_data import business_store_callback


async def business_store_keyboard(business_id: int):
    menu = InlineKeyboardMarkup(row_width=2)
    next_business = InlineKeyboardButton('>>', callback_data=business_store_callback.new(event='change_business', type=business_id + 1))
    previous_business = InlineKeyboardButton('<<', callback_data=business_store_callback.new(event='change_business', type=business_id - 1))
    buy = InlineKeyboardButton('Купить', callback_data=business_store_callback.new(event='buy_business', type=business_id))
    menu.add(previous_business, next_business, buy)
    return menu



