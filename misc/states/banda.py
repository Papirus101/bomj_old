from aiogram.dispatcher.filters.state import StatesGroup, State


class BandaCreateState(StatesGroup):
    GetBandaName = State()
    GetBandaSmile = State()