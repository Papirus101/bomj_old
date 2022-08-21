from aiogram import types, Dispatcher
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher import FSMContext

import pathlib
from misc.services import redis

from db.queries.user_business import add_new_order_products, change_business_name_by_type, get_business_by_type, \
    update_business_owner, update_business_products, update_count_need_product_to_delivery
from db.queries.users import get_main_user_info, update_needs_user, update_user_balance

from keyboards.inline.needs.needs_inline import needs_business_settings_keyboard, needs_inline, order_products_keyboard, \
    sell_needs_business
from keyboards.inline.needs.needs_data import needs_callback_data

from misc.needs_misc import create_event_delivery_fuel
from misc.states.needs_states import NeedsState
from misc.vriables import BOMJ_TIMES_CHAT_ID
from misc.convert_money import convert_stats

from static.text.needs_text import ACCEPT_BUY_BUSINESS, GET_NEW_NAME_NEED, MAIN_NEEDS_SETTINGS, NEED_DOES_NOT_REGEN, \
    NEED_NOT_OWNER, NEEDS_REGEN, NEW_NAME_NEED, NOT_MONEY_TO_BUY_BUSINESS, get_needs_text, get_text_new_order_product


async def needs_text_prepare(message: types.Message, need_type: str):
    db_session = message.bot.get('db')

    business = await get_business_by_type(db_session, need_type)
    user = await get_main_user_info(db_session, message.from_user.id)
    price_health = user.lvl * 2
    count_need = (100 - getattr(user, need_type)) / 15
    total_price_health = int(price_health * count_need)
    text = get_needs_text(need_type)
    text = text.format(
        business_name=business.name,
        total_price_health=convert_stats(money=total_price_health),
        business_count_product=business.count_product,
        user_health=getattr(user, need_type),
        user_money=convert_stats(money=user.money)
    )
    if business.owner is None:
        text += '\n\nЭтот бизнес свободен, ты можешь купить его за 20.00М руб.'
    return text, business.owner, business.need_product


async def health_need(message: types.Message):
    text, business_owner, need_product = await needs_text_prepare(message, 'health')
    await message.answer_photo(open(f'{pathlib.Path().absolute()}/image/needs/health_main.png', 'rb'),
                               caption=text,
                               reply_markup=await needs_inline('health', business_owner, message.from_user.id,
                                                               need_product))


async def eat_need(message: types.Message):
    text, business_owner, need_product = await needs_text_prepare(message, 'eat')
    await message.answer_photo(open(f'{pathlib.Path().absolute()}/image/needs/eat_main.png', 'rb'),
                               caption=text,
                               reply_markup=await needs_inline('eat', business_owner, message.from_user.id,
                                                               need_product))


async def luck_need(message: types.Message):
    text, business_owner, need_product = await needs_text_prepare(message, 'luck')
    await message.answer_photo(open(f'{pathlib.Path().absolute()}/image/needs/luck_main.png', 'rb'),
                               caption=text,
                               reply_markup=await needs_inline('luck', business_owner, message.from_user.id,
                                                               need_product))


# ------------------------------------------------ Восстановление показателей ------------------------------------------------#
async def regen_needs(call: types.CallbackQuery, callback_data: dict):
    db_session = call.message.bot.get('db')

    need_type = callback_data.get('type')
    business = await get_business_by_type(db_session, need_type)
    user = await get_main_user_info(db_session, call.from_user.id)
    user_need = getattr(user, need_type)
    if user_need >= 100:
        await call.answer(NEED_DOES_NOT_REGEN, show_alert=True)
        return
    await call.answer()
    price_need = user.lvl * 2
    count_need = int((100 - user_need) / 15)
    total_price_need = price_need * count_need
    if not await update_business_products(db_session, need_type, count_need, '-'):
        await update_business_owner(db_session, need_type)
    await update_needs_user(db_session, call.from_user.id, need_type, '+', 100 - count_need)
    if user.lvl < 15 or user.money < total_price_need:
        pass
    else:
        await update_user_balance(db_session, call.from_user.id, 'money', '-', total_price_need)
    if business.owner is not None and business.owner != call.from_user.id:
        await update_user_balance(db_session, business.owner, 'money', '+', total_price_need)
    await call.message.answer(NEEDS_REGEN)


# ------------------------------------------------ Покупка бизнеса ------------------------------------------------#
async def buy_business(call: types.CallbackQuery, callback_data: dict):
    db_session = call.message.bot.get('db')

    await call.answer()
    user = await get_main_user_info(db_session, call.from_user.id)
    if user.money < 20_000_000:
        await call.message.answer(NOT_MONEY_TO_BUY_BUSINESS.format(user_money={convert_stats(money=user.money)}))
        return
    business_type = callback_data.get('type')
    business = await get_business_by_type(db_session, business_type)
    if business.owner is not None:
        await call.message.answer('Воу, кто-то успел купить этот бизнес до тебя(')
        return
    if not await update_business_owner(db_session, business_type, call.from_user.id):
        await call.message.answer('У тебя уже есть приообирётнный бизнес!')
        return
    await update_user_balance(db_session, call.from_user.id, 'money', '-', 20_000_000)
    await call.message.delete()
    await call.message.answer(ACCEPT_BUY_BUSINESS)


# ------------------------------------------------ Настройки бизнеса ------------------------------------------------#
async def needs_settings(call: types.CallbackQuery, callback_data: dict):
    await call.answer()
    business_type = callback_data.get('type')
    await call.message.edit_caption(f'{call.message.caption}\n\n' +
                                    MAIN_NEEDS_SETTINGS,
                                    reply_markup=await needs_business_settings_keyboard(business_type))


async def needs_settings_back(call: types.CallbackQuery, callback_data: dict):
    await call.answer()
    business_type = callback_data.get('type')
    await call.message.edit_caption(caption=call.message.caption.replace(MAIN_NEEDS_SETTINGS, ''),
                                    reply_markup=await needs_inline(business_type, call.from_user.id, call.from_user.id,
                                                                    False))


# ------------------------------------------------ Изменение название бизнеса ------------------------------------------------#
async def needs_change_name(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    db_session = call.message.bot.get('db')

    await call.answer()
    await call.message.delete()
    business_type = callback_data.get('type')
    business = await get_business_by_type(db_session, business_type)
    if business.owner != call.from_user.id:
        await call.message.answer(NEED_NOT_OWNER)
        return
    await NeedsState.ChangeNeedsName.set()
    await state.update_data(business_type=business_type)
    await call.message.answer(GET_NEW_NAME_NEED)


async def needs_settings_get_new_name(message: types.Message, state: FSMContext):
    if message.text == '0':
        await state.finish()
        await message.answer('Отмена')
        return

    db_session = message.bot.get('db')
    data = await state.get_data()
    business_type = data.get('business_type')
    if not await change_business_name_by_type(db_session, business_type, message.text, message.from_user.id):
        await message.answer(NEED_NOT_OWNER)
        return
    await message.answer(NEW_NAME_NEED.format(new_name=message.text))
    await state.finish()


# ------------------------------------------------ Заказ продуктов ------------------------------------------------#
async def needs_order_products(call: types.CallbackQuery, callback_data: dict):
    db_session = call.message.bot.get('db')

    await call.answer()
    business_type = callback_data.get('type')
    business = await get_business_by_type(db_session, business_type)
    user = await get_main_user_info(db_session, call.from_user.id)
    if business.owner != call.from_user.id:
        await call.message.answer(NEED_NOT_OWNER)
        return
    total_need_products = 15_000 - business.count_product
    total_price_need_products = (15_000 - business.count_product) * 10
    await call.message.edit_caption(get_text_new_order_product(
        user.money >= total_price_need_products).format(
        count_product=business.count_product,
        total_need_product=convert_stats(money=total_need_products),
        total_price_product=convert_stats(money=total_price_need_products),
        user_money=convert_stats(money=user.money)
    ),
        reply_markup=await order_products_keyboard(business_type, user.money >= total_price_need_products))


async def needs_accept_new_order_product(call: types.CallbackQuery, callback_data: dict):
    db_session = call.message.bot.get('db')

    await call.answer()
    business_type = callback_data.get('type')
    business = await get_business_by_type(db_session, business_type)
    total_need_products = 15_000 - business.count_product
    if total_need_products <= 0:
        await call.message.answer('Твой бизнес не нуждается в доставке')
        return
    total_price_need_products = (15_000 - business.count_product) * 10
    if not await update_user_balance(db_session, call.from_user.id, 'money', '-', total_price_need_products):
        await call.message.answer('Недостаточно средств для оформления заказа')
        return
    if not await add_new_order_products(db_session, business_type, total_need_products):
        await call.message.answer('У тебя уже есть оформленный заказ.')
        return
    await call.message.answer("Заказ успешно оформлен")
    await call.message.bot.send_message(chat_id=BOMJ_TIMES_CHAT_ID,
                                        text=f'{business.name} оформил новый заказ на {total_need_products} шт. продуктов.')


# ------------------------------------------------ Продажа бизнеса ------------------------------------------------#
async def needs_sell_business(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    db_session = call.message.bot.get('db')

    await call.answer()
    business_type = callback_data.get('type')
    business = await get_business_by_type(db_session, business_type)
    if business.owner != call.from_user.id:
        await call.message.answer(NEED_NOT_OWNER)
        return
    await call.message.answer('Пришли мне цену за которую хочешь продать бизнес или 0 для отмены\n'
                              'Минимальная цена для продажи: 20.00М руб.')
    await NeedsState.GetPriceToSellBusiness.set()
    await state.update_data(business_type=business_type)


async def needs_get_money_for_sell_business(message: types.Message, state: FSMContext):
    price = message.text
    if price == '0':
        await message.answer('Отмена')
        await state.finish()
        return
    if not price.isdigit():
        await message.answer('Пришли мне цену, за которую хочешь продать бизнес цифрой или 0 для отмены\n'
                             'Минимальная цена продажи бизнеса 20.00M руб.')
        return
    if int(price) < 20_000_000:
        await message.answer('Минимальная цена продажи бизнеса 20.00М руб\n'
                             'Или пришли мне 0 для отмены')
        return
    await state.update_data(price=price)
    await message.answer('Пришли мне ID игрока, которому хочешь продать бизнес\n'
                         'Получить его можно в чате ответив на сообщение игрока командой /id, либо пусть'
                         'покупатель отправит команду /id в личные сообщения боту и перешлет тебе ответ')
    await NeedsState.GetIdUserToSellBusiness.set()


async def needs_get_user_id_to_sell_business(message: types.Message, state: FSMContext):
    db_session = message.bot.get('db')

    user_id = message.text
    data = await state.get_data()
    business_type = data.get('business_type')
    price = int(data.get('price'))
    if user_id == '0':
        await message.answer('Отмена')
        await state.finish()
        return
    if not user_id.isdigit():
        await message.answer('Пришли мне ID игрока, которому хочешь продать бизнес или 0 для отмены')
        return
    await state.finish()
    user_buy = await get_main_user_info(db_session, int(user_id))
    await message.answer(
        f'Отправили предложение о покупке бизнеса игроку {user_buy.name if user_buy.name is not None else user_buy.fullname}, ожидаем ответа')
    await message.bot.send_message(chat_id=int(user_id),
                                   text=f'{message.from_user.full_name} предлагает тебе купить его бизнес\n'
                                        f'Тип бизнеса: {business_type}\n'
                                        f'Цена: {convert_stats(money=price)} руб. | Твой баланс: {convert_stats(m=user_buy.money)} руб.',
                                   reply_markup=await sell_needs_business(business_type, message.from_user.id, price))


async def needs_accept_buy_business_from_user(call: types.CallbackQuery, callback_data: dict):
    await call.answer()
    await call.message.delete()

    db_session = call.message.bot.get('db')
    price = int(callback_data.get('type').split('_')[-1])
    business_type = callback_data.get('type').split('_')[0]
    seller_id = int(callback_data.get('type').split('_')[1])
    business = await get_business_by_type(db_session, business_type)
    if business.owner != seller_id:
        await call.message.answer('К сожалению продавец более не является владельцем этого бизнеса')
        return
    if not await update_user_balance(db_session, call.from_user.id, 'money', '-', price):
        await call.message.answer('У тебя недостаточно средств для покупки этого бизнеса')
        await call.message.bot.send_message(chat_id=seller_id,
                                            text=f'У {call.from_user.full_name} недостаточно средств для покупки твоего бизнеса')
        return
    await update_business_owner(db_session, business_type, call.from_user.id)
    await update_user_balance(db_session, seller_id, 'money', '+', price)
    await call.message.answer('Бизнес успешно приобритён')
    await call.message.bot.send_message(chat_id=seller_id, text=f'{call.from_user.full_name}'
                                                                'приобрёл твой бизнес за {convert_stats(m=price)} руб.')


async def needs_except_buy_business_from_user(call: types.CallbackQuery, callback_data: dict):
    await call.answer()
    await call.message.delete()

    seller_id = int(callback_data.get('type'))
    await call.message.answer('Ты отказался от покупки бизнеса')
    await call.message.bot.send_message(chat_id=seller_id,
                                        text=f'{call.from_user.full_name} отказался от покупки твоего бизнеса')


async def needs_delivery_products_to_business(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    await call.answer()

    db_session = call.message.bot.get('db')
    business_type = callback_data.get('type')
    business = await get_business_by_type(db_session, business_type)
    if not business.need_product:
        await call.message.answer('Бизнес больше не нуждается в доставке продуктов')
        return
    await call.message.edit_caption(f'{call.message.caption}\n'
                                    f'Всего бизнесу необходимо {business.count_need_product} шт. товаров\n\n'
                                    'Пришли мне, сколько товаров ты хочешь доставить\n'
                                    'Минимальный объём 500 шт.\n'
                                    'Максимальный объём 5000 шт.\n'
                                    f'{"Похоже что последняя партия товаров уже в пути, но никто не знает что может случится с водителем в дороге, попробуй вернуться через 10 минут" if business.count_need_product <= 0 else ""}')
    await NeedsState.GetCountProductsToDelivery.set()
    await state.update_data(business_type=business_type)


async def needs_get_count_products_to_delivery(message: types.Message, state: FSMContext):
    count_products_delivery = message.text

    if count_products_delivery == '0':
        await message.answer('Отмена')
        await state.finish()
        return
    if not count_products_delivery.isdigit():
        await message.answer('Пришли мне кол-во товаров цифрой или 0 для отмены')
        return

    data = await state.get_data()
    business_type = data.get('business_type')
    db_session = message.bot.get('db')
    count_products_delivery = int(count_products_delivery)
    business = await get_business_by_type(db_session, business_type)

    if count_products_delivery > business.count_need_product:
        await message.answer(f'Бизнесу необходимо {business.count_need_product} шт. товаров, попробуй ещё раз'
                             ' или пришли мне 0 для отмены')
        return
    # if count_products_delivery > 5_000 or count_products_delivery < 500:
    #     await message.answer('Минимальный объём 500 шт.\n'
    #                         'Максимальный объём 5000 шт.\n'
    #                         'Попробуй ещё раз или пришли мне 0 для отмены')
    #     return
    await update_count_need_product_to_delivery(db_session, business_type, '-', count_products_delivery)
    await message.answer('Приключение начинается...')
    await create_event_delivery_fuel(message, count_products_delivery, business_type, 0)
    await state.finish()


async def needs_check_event_id_delivery(call: types.CallbackQuery, callback_data: dict):
    await call.answer()
    await call.message.delete()

    event_info = await redis.hgetall(f'{call.from_user.id}_delivery')
    event_id = int(event_info['event_id'])
    user_answer = int(callback_data.get('event'))
    if event_id == user_answer:
        await redis.hmset(f'{call.from_user.id}_delivery',
                          {'count_delivery_product': event_info['count_delivery_product'],
                           'event_id': 0,
                           'business_type': event_info['business_type'],
                           'count_events': int(event_info['count_events'])})
        await call.message.answer('Ты принял правильное решение')
    else:
        db_session = call.message.bot.get('db')
        if int(event_info['count_delivery_product']) - 100 <= 0:
            await call.message.answer(
                'Ты окончательно запутался в поворотах и не смог добраться до пункта назначения, задание провалено.')
            await redis.hmset(f'{call.from_user.id}_delivery',
                              {'count_delivery_product': event_info['count_delivery_product'],
                               'event_id': -1,
                               'business_type': event_info['business_type'],
                               'count_events': int(event_info['count_events'])})
            await update_count_need_product_to_delivery(db_session, event_info['business_type'], '+',
                                                        int(event_info['count_delivery_product']))
        else:
            await call.message.answer('Ты выбрал не правильное направление'
                                      ', на дорогах возрадились банды из 90-х и отжали часть товара')
            await redis.hmset(f'{call.from_user.id}_delivery',
                              {'count_delivery_product': int(event_info['count_delivery_product']) - 100,
                               'event_id': 0,
                               'business_type': event_info['business_type'],
                               'count_events': int(event_info['count_events'])})
            await update_count_need_product_to_delivery(db_session, event_info['business_type'], '+', 100)


def register_needs_handlers(dp: Dispatcher):
    # ------------------------------------------------ Основная информация ------------------------------------------------#
    dp.register_message_handler(health_need, Text(equals='❤️ Здоровье'), chat_type='private')
    dp.register_message_handler(eat_need, Text(equals='🍗 Еда'), chat_type='private')
    dp.register_message_handler(luck_need, Text(equals='😄 Счастье'), chat_type='private')
    # ------------------------------------------------ Покупка бизнеса ------------------------------------------------#
    dp.register_callback_query_handler(buy_business, needs_callback_data.filter(event='buy'), chat_type='private')
    # ------------------------------------------------ Восстановление показателей ------------------------------------------------#
    dp.register_callback_query_handler(regen_needs, needs_callback_data.filter(event='regen'), chat_type='private')
    # ------------------------------------------------ Настройки бизнеса ------------------------------------------------#
    dp.register_callback_query_handler(needs_settings, needs_callback_data.filter(event='settings'),
                                       chat_type='private')
    dp.register_callback_query_handler(needs_settings_back, needs_callback_data.filter(event='settings_back'),
                                       chat_type='private')
    # ________________________________________________ Настройки бизнеса: изменение имени бизнеса ________________________________________________#
    dp.register_callback_query_handler(needs_change_name, needs_callback_data.filter(event='change_name'),
                                       chat_type='private')
    dp.register_message_handler(needs_settings_get_new_name, state=NeedsState.ChangeNeedsName, chat_type='private')
    # ________________________________________________ Настройки бизнеса: заказ продуктов ________________________________________________#
    dp.register_callback_query_handler(needs_order_products, needs_callback_data.filter(event='order_product'),
                                       chat_type='private')
    dp.register_callback_query_handler(needs_accept_new_order_product, needs_callback_data.filter(event='accept_order'),
                                       chat_type='private')
    # ________________________________________________ Настройки бизнеса: продажа бизнеса ________________________________________________#
    dp.register_callback_query_handler(needs_sell_business, needs_callback_data.filter(event='sell_business'),
                                       chat_type='private')
    dp.register_message_handler(needs_get_money_for_sell_business, state=NeedsState.GetPriceToSellBusiness,
                                chat_type='private')
    dp.register_message_handler(needs_get_user_id_to_sell_business, state=NeedsState.GetIdUserToSellBusiness,
                                chat_type='private')
    dp.register_callback_query_handler(needs_accept_buy_business_from_user,
                                       needs_callback_data.filter(event='accept_buy_business'),
                                       chat_type='private')
    dp.register_callback_query_handler(needs_except_buy_business_from_user,
                                       needs_callback_data.filter(event='except_buy_business'),
                                       chat_type='private')
    # ------------------------------------------------ Доставка продуктов ------------------------------------------------#
    dp.register_callback_query_handler(needs_delivery_products_to_business,
                                       needs_callback_data.filter(event='delivery_product'), chat_type='private')
    dp.register_message_handler(needs_get_count_products_to_delivery, state=NeedsState.GetCountProductsToDelivery,
                                chat_type='private')
    dp.register_callback_query_handler(needs_check_event_id_delivery,
                                       needs_callback_data.filter(type='needs_delivery_event'), chat_type='private')
