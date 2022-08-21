from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from keyboards.inline.main_callback import profile_callback


def profile_keyb():
    keyb = InlineKeyboardMarkup(row_width=2)
    keys = InlineKeyboardButton('🗃 Кейсы', callback_data=profile_callback.new(event='keys'))
    donat = InlineKeyboardButton('🛒 Магазин', callback_data=profile_callback.new(event='donat'))
    top = InlineKeyboardButton('🏆 Топ игроков', callback_data=profile_callback.new(event='top'))
    refferal = InlineKeyboardButton('Рефералы', callback_data=profile_callback.new(event='ref'))
    settings = InlineKeyboardButton('Настройки', callback_data=profile_callback.new(event='settings'))
    keyb.add(keys, donat)
    keyb.add(top, refferal)
    keyb.add(settings)
    return keyb


async def workers_keyboard():
    menu = InlineKeyboardMarkup()
    add = InlineKeyboardButton('Нанять', callback_data=profile_callback.new(event='add_workers'))
    menu.add(add)
    return menu


async def open_keys_keyboard():
    menu = InlineKeyboardMarkup()
    open = InlineKeyboardButton('Открыть кейс', callback_data=profile_callback.new(event='open_keys'))
    menu.add(open)
    return menu


async def settings_keyboard(open: bool):
    menu = InlineKeyboardMarkup(row_width=1)
    open_profile = InlineKeyboardButton('Открыть профиль', callback_data=profile_callback.new(event='open_profile'))
    close_profile = InlineKeyboardButton('Закрыть профиль', callback_data=profile_callback.new(event='close_profile'))
    change_photo = InlineKeyboardButton('Изменить фон', callback_data=profile_callback.new(event='change_photo'))
    change_name = InlineKeyboardButton('Изменить имя', callback_data=profile_callback.new(event='change_name'))
    if open:
        menu.add(open_profile)
    else:
        menu.add(close_profile)
    menu.add(change_photo, change_name)
    return menu


async def change_bottle_keyboard():
    menu = InlineKeyboardMarkup(row_width=1)
    menu.add(InlineKeyboardButton('Поменять бутылки', callback_data=profile_callback.new(event='change_bottle')))
    return menu


async def donat_keyboard(user_id):
    menu = InlineKeyboardMarkup(row_width=1)
    link = f'https://qiwi.com/payment/form/99?extra%5B%27account%27%5D=79883158831&extra%5B%27comment%27%5D=' \
           f'donat:{user_id}&currency=643&blocked%5B1%5D=comment&blocked%5B2%5D=account'
    add_balance = InlineKeyboardButton('Пополнить баланс', url=link)
    check_donat = InlineKeyboardButton('Проверить пополнение', callback_data=profile_callback.new(event='check_donat'))
    unlim_health = InlineKeyboardButton('❤️🍗😄 Бесконечные показатели', callback_data=profile_callback.new(event='buy_unlim_health'))
    # vip_week =  InlineKeyboardButton('VIP неделя', callback_data=profile_callback.new(event='buy_vip_week'))
    menu.add(add_balance, check_donat, unlim_health)
    return menu