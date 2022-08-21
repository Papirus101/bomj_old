from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from keyboards.inline.fishing.fishing_inline_data import fishing_callback

import random


async def fishing_main_keyboard():
    menu = InlineKeyboardMarkup(row_width=2)
    store = InlineKeyboardButton('Магазин', callback_data=fishing_callback.new('store', 'store'))
    sell = InlineKeyboardButton('Скупщик', callback_data=fishing_callback.new('sell', 'sell'))
    start = InlineKeyboardButton('Рыбачить', callback_data=fishing_callback.new('start_fish', 'start_fish'))
    menu.add(store, sell, start)
    return menu


async def fish_keyboard():
    menu = InlineKeyboardMarkup(row_width=2)
    keyses = [['Подсечь', 1], ['Подождать ещё', 0], ['Пустая кнопка', 'none']]
    while len(keyses) != 0:
        key = random.choice(keyses)
        menu.insert(InlineKeyboardButton(key[0], callback_data=fishing_callback.new('fishing', key[1])))
        keyses.remove(key)
    return menu


async def sell_fish_keyboard():
    menu = InlineKeyboardMarkup()
    menu.add(InlineKeyboardButton('Продать рыбу', callback_data=fishing_callback.new('sell_fish', 'sell_fish')))
    return menu


async def fishing_store_info():
    menu = InlineKeyboardMarkup(row_width=2)
    bait = InlineKeyboardButton('Наживка', callback_data=fishing_callback.new('bait_buy', 'bait_buy'))
    rod = InlineKeyboardButton('Удочка', callback_data=fishing_callback.new('rod_buy', 'rod_buy'))
    menu.add(bait, rod)
    return menu


async def rod_store_keyboard():
    menu = InlineKeyboardMarkup()
    menu.add(InlineKeyboardButton('Улучшить удочку', callback_data=fishing_callback.new('update_bait', 'update_bait')))
    return menu
