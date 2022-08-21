from aiogram.dispatcher.filters.state import StatesGroup, State


class SettingsState(StatesGroup):
    ChangeUserName = State()
    GetUserImage = State()


class ChangeBottleState(StatesGroup):
    CountBottleChange = State()


class FishingState(StatesGroup):
    GetCountBaitBuy = State()