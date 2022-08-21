from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


async def works_optional():
    menu = ReplyKeyboardMarkup(resize_keyboard=True)
    works = KeyboardButton('💰 Работать')
    fishing = KeyboardButton('🎣 Рыбалка')
    collect_bottle = KeyboardButton('🍾 Собирать бутылки')
    sell_bottle = KeyboardButton('💱🍾 Обмен бутылок')
    business = KeyboardButton('🤵‍♂️ Бизнес')
    profile = KeyboardButton('👤 Профиль')
    menu.row(works)
    menu.row(fishing)
    menu.row(collect_bottle, sell_bottle)
    menu.row(business)
    menu.row(profile)
    return menu