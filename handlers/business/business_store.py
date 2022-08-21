import pathlib

from aiogram import types, Dispatcher
from aiogram.dispatcher.filters import Text
from aiogram.types.input_media import InputMediaPhoto
from db.models.user_db import Users

from db.queries.business import get_business_store
from db.queries.gun_war import get_current_gun_war
from db.queries.users import get_count_business, get_main_user_info, get_user_info_and_gun_war, update_business_count, \
    update_user_balance, update_user_gun_war

from keyboards.inline.business.business_store import business_store_keyboard
from keyboards.inline.business.business_store_data import business_store_callback

from misc.convert_money import convert_stats
from misc.user_misc import text_user_balance
from misc.vriables import SMILE_MONEY_TYPE


async def get_business_info(business_id: int, db_session, user_id: int):
    business = await get_business_store(db_session, business_id)
    if business is None:
        return None, None, None
    business = business[0]
    price_business = business.price
    user: Users = await get_main_user_info(db_session, user_id)
    count_current_business = 0
    amount_current_profit = 0
    if user.info is not None and user.info.get('business', None) is not None:
        if user.info.get('business').get(str(business.id), None) is not None:
            count_current_business = user.info.get('business').get(str(business.id))
            amount_current_profit = int(count_current_business) * business.profit
        price_business = count_current_business * business.price if count_current_business > 0 else business.price
    image = f'{pathlib.Path().absolute()}/image/business/{business.id}.png'
    keyboard = await business_store_keyboard(business_id)
    text = f'🏘 {business.name}\n\n' \
           f'Доход в час: {convert_stats(m=business.profit)} {SMILE_MONEY_TYPE.get(business.money_profit)}\n' \
           f'Цена: {convert_stats(m=price_business)} {SMILE_MONEY_TYPE.get(business.money_price)}\n\n' \
           f'{await text_user_balance(user.money, user.bottle, user.lvl, user.donat, user.keyses)}\n\n' \
           f'В твоём владении таких бизнесов: {count_current_business}, они приносят {convert_stats(m=amount_current_profit)} {SMILE_MONEY_TYPE.get(business.money_profit)}\n' \
           f'Всего бизнесов в твоём владении {await get_count_business(db_session, user_id)} из {int(user.lvl / 10)} доступных\n\n' \
           f'<strong>Доход с бизнесов приходит каждый час, только пользователем находящимся онлайн в боте</strong>'
    return keyboard, text, image


async def business_store_main(message: types.Message):
    db_session = message.bot.get('db')
    keyboard, text, image = await get_business_info(0, db_session, message.from_user.id)
    await message.answer_photo(open(image, 'rb'), caption=text, reply_markup=keyboard)


async def change_business_store(call: types.CallbackQuery, callback_data: dict):
    db_session = call.message.bot.get('db')
    business_id = int(callback_data.get('type'))
    if business_id < 0:
        await call.answer('Там больше ничего нет')
        return

    keyboard, text, image = await get_business_info(business_id, db_session, call.from_user.id)
    if keyboard is None:
        await call.answer('Там больше ничего нет')
        return
    await call.message.edit_media(InputMediaPhoto(media=open(image, 'rb'), caption=text), reply_markup=keyboard)


async def buy_business(call: types.CallbackQuery, callback_data: dict):
    db_session = call.message.bot.get('db')
    business_id = int(callback_data.get('type'))
    user: Users = await get_main_user_info(db_session, call.from_user.id)

    if await get_count_business(db_session, call.from_user.id) >= user.lvl / 10:
        await call.answer()
        await call.message.answer(
            'У тебя не хватает уровня для покупки бизнеса. Можно покупать 1 бизнес раз в 10 уровней')
        return

    business = await get_business_store(db_session, business_id)
    business = business[0]
    price_business = business.price

    if user.info is not None and user.info.get('business', None) is not None:
        if user.info.get('business').get(str(business.id), None) is not None:
            count_current_business = user.info.get('business').get(str(business.id))
            amount_current_profit = int(count_current_business) * business.profit
        price_business = count_current_business * business.price if count_current_business > 0 else business.price

    if getattr(user, str(business.money_price)) < price_business:
        await call.answer('Недостаточно средств для покупки бизнеса', show_alert=True)
        return

    await call.answer()
    await update_user_balance(db_session, call.from_user.id, business.money_price, '-', price_business)
    await update_business_count(db_session, call.from_user.id, business.id)
    await call.message.answer('Бизнес успешно приобритён')
    await call.message.delete()


def register_business_store_nandler(dp: Dispatcher):
    dp.register_message_handler(business_store_main, Text(equals='🤵‍♂️ Бизнес'), chat_type='private')
    dp.register_callback_query_handler(change_business_store, business_store_callback.filter(event='change_business'),
                                       chat_type='private')
    dp.register_callback_query_handler(buy_business, business_store_callback.filter(event='buy_business'),
                                       chat_type='private')
