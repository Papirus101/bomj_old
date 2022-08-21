import random

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from keyboards.inline.banda.banda_inline_callback import banda_callback_data


async def main_banda_keyboard(user_banda: bool, page: int, bands):
    menu = InlineKeyboardMarkup(row_width=2)
    if not user_banda:
        for banda in bands:
            banda = banda[0]
            key = InlineKeyboardButton(banda.name, callback_data=banda_callback_data.new('send_request_banda', banda.id))
            menu.insert(key)
    if user_banda:
        menu.row(InlineKeyboardButton('Моя банда', callback_data=banda_callback_data.new('my_band', 'my_band')))
    previous = InlineKeyboardButton('<<', callback_data=banda_callback_data.new('change_page', page - 1))
    next = InlineKeyboardButton('>>', callback_data=banda_callback_data.new('change_page', page + 1))
    menu.row(previous, next)
    menu.row(InlineKeyboardButton('Создать банду', callback_data=banda_callback_data.new('create_banda', 'create_banda')))
    return menu


async def new_request_to_banda_keyboard(user_id: int, banda_id: int):
    menu = InlineKeyboardMarkup(row_width=2)
    accept = InlineKeyboardButton('Принять',
                                  callback_data=banda_callback_data.new('accept_new_user', f'accept_{user_id}_{banda_id}'))
    not_accept = InlineKeyboardButton('Отклонить',
                                      callback_data=banda_callback_data.new('accept_new_user', f'pass_{user_id}_{banda_id}'))
    menu.add(accept, not_accept)
    return menu


async def main_menu_banda_keyboard():
    menu = InlineKeyboardMarkup(row_width=2)
    maxa = InlineKeyboardButton('МАХАЦА', callback_data=banda_callback_data.new('maxa_start', 'maxa_start'))
    gum = InlineKeyboardButton('Качалка', callback_data=banda_callback_data.new('gum', 'gum'))
    banda_users = InlineKeyboardButton('Участники банды', callback_data=banda_callback_data.new('banda_users', 'banda_users'))
    event = InlineKeyboardButton('Соревнование', callback_data=banda_callback_data.new('event', 'event'))
    banda_leave = InlineKeyboardButton('Покинуть банду', callback_data=banda_callback_data.new('leave_from_banda', 'leave_from_banda'))
    menu.add(maxa, gum, banda_users, event, banda_leave)
    return menu


async def maxa_next_keyboard():
    menu = InlineKeyboardMarkup(row_width=3)
    MAXA_KEYBOARD = [['МАХАЦА', 'maxa_start'], ['-!-', 'none'], ['-!-', 'none']]
    while len(MAXA_KEYBOARD) != 0:
        key = random.choice(MAXA_KEYBOARD)
        maxa = InlineKeyboardButton(key[0], callback_data=banda_callback_data.new('maxa_start', key[1]))
        menu.insert(maxa)
        MAXA_KEYBOARD.remove(key)
    return menu


async def gum_main_keyboard():
    menu = InlineKeyboardMarkup()
    menu.add(InlineKeyboardButton('Начать качаться', callback_data=banda_callback_data.new('start_gum', 'start_gum')))
    return menu


async def gum_event_keyboard():
    menu = InlineKeyboardMarkup(row_width=1)
    buttons = [['Голова', 1], ['Тело', 2], ['Ноги', 3]]
    while len(buttons) != 0:
        key = random.choice(buttons)
        menu.add(InlineKeyboardButton(key[0], callback_data=banda_callback_data.new('gum_check', key[1])))
        buttons.remove(key)
    return menu


async def kick_user_from_banda(banda_admin: bool):
    if not banda_admin:
        return None
    menu = InlineKeyboardMarkup(row_width=1)
    kick_user = InlineKeyboardButton('Выгнать игрока', callback_data=banda_callback_data.new('kick_user', 'kick_user'))
    menu.add(kick_user)
    return menu


async def choice_user_to_kick_keyboard(users):
    menu = InlineKeyboardMarkup(row_width=2)
    for user in users:
        menu.add(InlineKeyboardButton(user.name, callback_data=banda_callback_data.new('choice_kick_user', user.telegram_id)))
    return menu


async def variable_leave_from_banda_keyboard():
    menu = InlineKeyboardMarkup(row_width=2)
    yes = InlineKeyboardButton('ДА!', callback_data=banda_callback_data.new('yes_leave', 'yes_leave'))
    no = InlineKeyboardButton('НЕТ', callback_data=banda_callback_data.new('no_leave', 'no_leave'))
    menu.add(yes, no)
    return menu