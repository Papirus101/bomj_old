from aiogram.dispatcher.filters.state import StatesGroup, State

class NeedsState(StatesGroup):
    ChangeNeedsName = State()
    GetPriceToSellBusiness = State()
    GetIdUserToSellBusiness = State()
    GetCountProductsToDelivery = State()