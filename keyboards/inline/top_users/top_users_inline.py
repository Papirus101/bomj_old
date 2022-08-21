from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from keyboards.inline.top_users.top_users_data import top_users_callback

async def top_users_keyboard():
    menu = InlineKeyboardMarkup(row_width=2)
    money = InlineKeyboardButton('💰 Деньги', callback_data=top_users_callback.new('money'))
    bottle = InlineKeyboardButton('🍾 Бутылки', callback_data=top_users_callback.new('bottle'))
    rating = InlineKeyboardButton('⭐️ Рейтинг', callback_data=top_users_callback.new('rating'))
    lvl = InlineKeyboardButton('📊 Уровень', callback_data=top_users_callback.new('lvl'))
    donat = InlineKeyboardButton('💵 Донат', callback_data=top_users_callback.new('donat'))
    keys = InlineKeyboardButton('🗃 Кейсы', callback_data=top_users_callback.new('keyses'))
    menu.add(money, bottle, rating, lvl, donat, keys)
    return menu