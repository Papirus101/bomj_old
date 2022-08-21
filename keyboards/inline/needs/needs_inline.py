from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from keyboards.inline.needs.needs_data import needs_callback_data


async def needs_inline(business_type: str, business_free: bool = False, user_id: int = None, need_product: bool = False):
    menu = InlineKeyboardMarkup(row_width=1)
    regen = InlineKeyboardButton('Восставновить потребности', callback_data=needs_callback_data.new('regen', business_type))
    menu.insert(regen)
    if business_free is None:
        buy_business = InlineKeyboardButton('Купить бизнес', callback_data=needs_callback_data.new('buy', business_type))
        menu.insert(buy_business)
    if business_free == user_id:
        business_settings = InlineKeyboardButton('Настройки', callback_data=needs_callback_data.new('settings', business_type))
        menu.insert(business_settings)
    if need_product:
        delivery_product = InlineKeyboardButton('Доставить продукты', callback_data=needs_callback_data.new('delivery_product', business_type))
        menu.insert(delivery_product)
    return menu


async def needs_business_settings_keyboard(business_type: str):
    menu = InlineKeyboardMarkup(row_width=1)
    order_product = InlineKeyboardButton('Заказать доставку', callback_data=needs_callback_data.new('order_product', business_type))
    change_name_business = InlineKeyboardButton('Изменить название бизнеса', callback_data=needs_callback_data.new('change_name', business_type))
    sell_business = InlineKeyboardButton('Продать бизнес', callback_data=needs_callback_data.new('sell_business', business_type))
    back = InlineKeyboardButton('Назад', callback_data=needs_callback_data.new('settings_back', business_type))
    menu.add(order_product, change_name_business, sell_business, back)
    return menu


async def order_products_keyboard(business_type: str, user_money: bool = False):
    menu = InlineKeyboardMarkup(row_width=2)
    if user_money:
        accept_order = InlineKeyboardButton('Заказать', callback_data=needs_callback_data.new('accept_order', business_type))
        menu.add(accept_order)
    except_order = InlineKeyboardButton('Отмена', callback_data=needs_callback_data.new('except_order', business_type))
    menu.add(except_order)
    return menu


async def sell_needs_business(business_type: str, seller_id: int, price: int):
    menu = InlineKeyboardMarkup(row_width=2)
    buy_business = InlineKeyboardButton('Купить', callback_data=needs_callback_data.new('buy_business', f'{business_type}_{seller_id}_{price}'))
    excpet_buy = InlineKeyboardButton('Отмена', callback_data=needs_callback_data.new('except_buy_business', seller_id))
    menu.add(buy_business, excpet_buy)
    return menu

async def needs_event_delivery_keyboard():
    menu = InlineKeyboardMarkup(row_width=2)
    go_straight = InlineKeyboardButton('Прямо', callback_data=needs_callback_data.new(5, 'needs_delivery_event'))
    right = InlineKeyboardButton('Направо', callback_data=needs_callback_data.new(3, 'needs_delivery_event'))
    left = InlineKeyboardButton('Налево', callback_data=needs_callback_data.new(4, 'needs_delivery_event'))
    menu.add(left, right, go_straight)
    return menu