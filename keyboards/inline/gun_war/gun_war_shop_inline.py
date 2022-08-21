from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from keyboards.inline.gun_war.gun_war_shop_data import gun_war_shop_callback


async def get_gun_war_shop_keyboard(gun_id: int):
    print(gun_id)
    menu = InlineKeyboardMarkup(row_width=2)
    previous = InlineKeyboardButton('<<', callback_data=gun_war_shop_callback.new(gun_id - 1, 'change_gun_shop_shop'))
    next = InlineKeyboardButton('>>', callback_data=gun_war_shop_callback.new(gun_id + 1, 'change_gun_shop_shop'))
    buy = InlineKeyboardButton('Купить', callback_data=gun_war_shop_callback.new(gun_id, 'buy_gun_war'))
    menu.row(buy)
    menu.row(previous, next)
    return menu
