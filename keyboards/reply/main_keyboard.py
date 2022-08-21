from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def main_keyboard():
	menu = ReplyKeyboardMarkup(resize_keyboard=True)
	profile = KeyboardButton('👤 Профиль')
	houses = KeyboardButton('🏚 Жильё')
	bomj = KeyboardButton('👨 Работники')
	work = KeyboardButton('🛠 Работы')
	potreb = KeyboardButton('❤ Потребности')
	banda = KeyboardButton('☠ Банда')
	equip = KeyboardButton('🔫 Снаряжение')
	more = KeyboardButton('🤔 Остальное')
	menu.add(profile)
	menu.add(houses, bomj)
	menu.add(banda, equip)
	menu.add(work, potreb)
	menu.add(more)
	return menu


def potreb_keyb():
	menu = ReplyKeyboardMarkup(resize_keyboard=True)
	health = KeyboardButton('❤️ Здоровье')
	eat = KeyboardButton('🍗 Еда')
	luck = KeyboardButton('😄 Счастье')
	profile = KeyboardButton('👤 Профиль')
	menu.add(health, eat, luck)
	menu.add(profile)
	return menu