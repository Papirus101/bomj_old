import asyncio
import pathlib
import random

from aiogram import types, Dispatcher

from db.queries.items import new_order, get_user_order, close_user_order, get_products_by_category, add_item_to_order, \
    get_items_names
from db.queries.users import get_main_user_info, update_user_balance, update_user_exp, \
    update_works_count
from keyboards.inline.works.works_data import works_callback
from keyboards.inline.works.works_inline import start_work_keyb, work_check_keyboard_generator, choice_products_keyboard
from misc.convert_money import convert_stats
from misc.user_misc import get_top_by_works, check_user_characteristics, get_total_amount, characteristic_change
from misc.vriables import ORDER_PICKER_ORDERS, ORDER_PICKER_TYPES_KEYBOARD
from static.text.profile import NEW_LEVEL_TEXT


async def work_info(call: types.CallbackQuery, callback_data: dict):
    db_session = call.message.bot.get('db')
    await call.answer()
    await call.message.delete()
    work = callback_data.get('type')
    await call.message.answer_photo(open(f'{pathlib.Path().absolute()}/image/works/order_picker/work.png', 'rb'),
                                    caption="🏪 Тебя отправили работать сборщиков онлайн заказов в местный магазин.\n"
                                            f"Тебе платят за каждый собранный заказ\n\n"
                                            "<code>По мере прокачки персонажа, ты сможешь устраиваться на более "
                                            "прибыльные работы</code>\n\n"
                                            f'{await get_top_by_works(db_session, work)}\n',
                                    reply_markup=await start_work_keyb(work))


async def send_order(call: types.CallbackQuery):
    system_message = await call.message.answer('Ожидаем новый заказ')
    await asyncio.sleep(random.randint(3, 10))
    await system_message.delete()
    db_session = call.message.bot.get('db')
    products = await new_order(db_session, call.from_user.id)
    products_text = ''
    for product in products:
        products_text += f'• {product}\n'
    await call.message.answer('Поступил новый заказ:\n\n'
                              f'{products_text}\n'
                              f'Удалить товар из корзины нельзя, поэтому будь придельно внимателен',
                              reply_markup=await work_check_keyboard_generator(ORDER_PICKER_ORDERS, '6'))


async def get_user_cart_text(db_session, user_id: int):
    order = await get_user_order(db_session, user_id)
    text = 'Твоя корзина:\n\n'
    if order[0].user_product is not None:
        items = await get_items_names(db_session, order[0].user_product)
        for item in items:
            text += f'{item}\n'
        return text
    return f'{text}Твоя корзина пуста'


async def order_picker_start(call: types.CallbackQuery):
    db_session = call.message.bot.get('db')
    await call.answer()
    await call.message.delete()
    if await get_user_order(db_session, call.from_user.id, False):
        await call.message.answer(
            'У тебя уже есть не собранный заказ, если ты откажешься от сборки заказа, начальство оштрафует тебя на 50.00К руб.',
            reply_markup=await work_check_keyboard_generator({'Отказаться от заказа': 'cancel_order_6'}, '6',
                                                             stop=False))
        return
    if not await check_user_characteristics(db_session, call):
        return
    await send_order(call)


async def cancel_order(call: types.CallbackQuery):
    db_session = call.message.bot.get('db')

    await call.answer()
    await call.message.delete()

    await update_user_balance(db_session, call.from_user.id, 'money', '-', 50_000)
    await close_user_order(db_session, (call.from_user.id))
    await call.message.answer('Ты отказался от сборки прошлого заказа и был оштрафован на 50.00К руб.')


async def cancel_new_order(call: types.CallbackQuery):
    db_session = call.message.bot.get('db')

    await call.answer()
    await call.message.delete()
    await call.message.answer('Ты отказался от заказа')
    await send_order(call)


async def accept_new_order(call: types.CallbackQuery):
    await call.answer()
    await call.message.answer_photo(open(f'{pathlib.Path().absolute()}/image/works/order_picker/check_type.png', 'rb'),
                                    caption=await get_user_cart_text(call.message.bot.get('db'), call.from_user.id),
                                    reply_markup=await work_check_keyboard_generator(ORDER_PICKER_TYPES_KEYBOARD,
                                                                                     '6_category', stop=False))


async def back_to_main_menu(call: types.CallbackQuery):
    await call.answer()
    await call.message.delete()
    await call.message.answer_photo(open(f'{pathlib.Path().absolute()}/image/works/order_picker/check_type.png', 'rb'),
                                    caption=await get_user_cart_text(call.message.bot.get('db'), call.from_user.id),
                                    reply_markup=await work_check_keyboard_generator(ORDER_PICKER_TYPES_KEYBOARD,
                                                                                     '6_category', stop=False))


async def choice_product_by_category(call: types.CallbackQuery, callback_data: dict):
    await call.answer()
    await call.message.delete()

    db_session = call.message.bot.get('db')
    category = int(callback_data.get('event'))
    products = await get_products_by_category(db_session, category)
    keyboard = await choice_products_keyboard(products)

    await call.message.answer_photo(
        open(f'{pathlib.Path().absolute()}/image/works/order_picker/type_{category}.png', 'rb'),
        reply_markup=keyboard,
        caption=await get_user_cart_text(call.message.bot.get('db'), call.from_user.id))


async def add_product_to_cart(call: types.CallbackQuery, callback_data: dict):
    db_session = call.message.bot.get('db')
    product_id = callback_data.get('type').split('_')[0]
    product_type = callback_data.get('type').split('_')[1]
    products = await get_products_by_category(db_session, int(product_type))
    await add_item_to_order(db_session, call.from_user.id, product_id)
    await call.message.edit_caption(caption=await get_user_cart_text(db_session, call.from_user.id),
                                    reply_markup=await choice_products_keyboard(products))


async def finish_work(call: types.CallbackQuery):
    db_session = call.message.bot.get('db')
    user_order = await get_user_order(db_session, call.from_user.id)
    try:
        user_order = user_order[0]
    except TypeError:
        await call.message.answer('Ты пытаешься меня обмануть!')
        return
    random_events_text = ''
    main_text = ''
    reward_text = ''

    await call.answer()
    await call.message.delete()
    await close_user_order(db_session, call.from_user.id)

    if user_order.user_product is not None and sorted(user_order.need_product) == sorted(user_order.user_product):
        count_products = len(user_order.need_product.split(','))
        user = await get_main_user_info(db_session, call.from_user.id)
        total_reward, nalog = await get_total_amount(user.lvl * (25 + count_products), user.vip)
        if nalog > 0:
            random_events_text = f'💥 Ты заплатил налог государству {convert_stats(money=nalog)} руб.'
        reward_text = f'Ты заработал {convert_stats(money=total_reward)} руб.'
        await update_user_balance(db_session, call.from_user.id, 'money', '+', total_reward)
        if await update_user_exp(db_session, call.from_user.id, '+', 1, user.vip):
            await call.message.answer(NEW_LEVEL_TEXT)
        await update_works_count(db_session, call.from_user.id, '6')
        await characteristic_change(db_session, call.from_user.id)
        main_text = 'Ты успешно справился с задачей, заказчик полностью доволен твоей работой'
    else:
        main_text = 'Ты не справился с поставленной задачей, за что был оштрафован на 50.00К руб.'
        await update_user_balance(db_session, call.from_user.id, 'money', '-', 50_000)
    await call.message.answer(f'{main_text}\n{random_events_text}\n{reward_text}')
    await send_order(call)


def register_order_picker_work_handler(dp: Dispatcher):
    dp.register_callback_query_handler(work_info, works_callback.filter(event='info', type='6'), chat_type='private')
    dp.register_callback_query_handler(order_picker_start, works_callback.filter(event='start', type='6'),
                                       chat_type='private')
    dp.register_callback_query_handler(cancel_order, works_callback.filter(event='cancel_order_6'), chat_type='private')
    dp.register_callback_query_handler(cancel_new_order, works_callback.filter(event='cancel_new_order'),
                                       chat_type='private')
    dp.register_callback_query_handler(accept_new_order, works_callback.filter(event='accept_new_order'),
                                       chat_type='private')
    dp.register_callback_query_handler(finish_work, works_callback.filter(event='order_finish'), chat_type='private')
    dp.register_callback_query_handler(choice_product_by_category, works_callback.filter(type='6_category_check'),
                                       chat_type='private')
    dp.register_callback_query_handler(back_to_main_menu,
                                       works_callback.filter(type='back', event='back_to_list_category'),
                                       chat_type='private')
    dp.register_callback_query_handler(add_product_to_cart, works_callback.filter(event='add_product'),
                                       chat_type='private')
