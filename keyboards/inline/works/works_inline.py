from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from keyboards.inline.works.works_data import works_callback

import random


async def works_menu(works):
    menu = InlineKeyboardMarkup(row_width=2)
    for work in works:
        key = InlineKeyboardButton(work[0].name, callback_data=works_callback.new('info', work[0].id))
        menu.add(key)
    return menu


async def start_work_keyb(work):
    menu = InlineKeyboardMarkup(row_width=1)
    start = InlineKeyboardButton('Начать работу', callback_data=works_callback.new('start', work))
    menu.add(start)
    return menu


async def work_check(work, end):
    keyb = InlineKeyboardMarkup(row_width=3)
    keys = [1, 2, 3, 4, 5, 6]
    while len(keys) != 0:
        key_num = random.choice(keys)
        keys.remove(key_num)
        key = InlineKeyboardButton(f'{key_num}', callback_data=works_callback.new(type=f'{work}_check', event=key_num))
        keyb.insert(key)
    stop = InlineKeyboardButton(f'{end}', callback_data=works_callback.new(type=f'{end}', event='0'))
    keyb.add(stop)
    return keyb


async def security_keyboard(work, end):
    menu = InlineKeyboardMarkup(row_width=2)
    ignore = InlineKeyboardButton('Бездействовать', callback_data=works_callback.new(type=f'{work}_check', event=1))
    grab = InlineKeyboardButton('Остановить воришку', callback_data=works_callback.new(type=f'{work}_check', event=2))
    stop = InlineKeyboardButton(f'{end}', callback_data=works_callback.new(type=f'{end}', event='0'))
    menu.add(ignore, grab, stop)
    return menu


async def security_fight_keyboard():
    menu = InlineKeyboardMarkup(row_width=1)
    head = InlineKeyboardButton('Голова', callback_data=works_callback.new(type=f'security_fight', event=1))
    body = InlineKeyboardButton('Тело', callback_data=works_callback.new(type=f'security_fight', event=2))
    leg = InlineKeyboardButton(f'Ноги', callback_data=works_callback.new(type=f'security_fight', event=3))
    menu.add(head, body, leg)
    return menu


async def work_check_keyboard_generator(buttons: dict, work: str, end: str = 'Уволиться', stop: bool = True):
    menu = InlineKeyboardMarkup(row_width=3)
    for button in buttons:
        key = InlineKeyboardButton(button,
                                   callback_data=works_callback.new(type=f'{work}_check', event=buttons[button]))
        print(key)
        menu.insert(key)
    if stop:
        stop = InlineKeyboardButton(f'{end}', callback_data=works_callback.new(type=f'{end}', event='0'))
        menu.row(stop)
    return menu


async def choice_products_keyboard(products):
    menu = InlineKeyboardMarkup(row_width=3)
    for product in products:
        key = InlineKeyboardButton(f'{product[0].smile} {product[0].name}', callback_data=works_callback.new(type=f'{product[0].id}_{product[0].type}', event='add_product'))
        menu.insert(key)
    back = InlineKeyboardButton('Вернуться к списку отделов', callback_data=works_callback.new(type='back', event='back_to_list_category'))
    menu.add(back)
    return menu
