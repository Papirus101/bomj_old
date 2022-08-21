import pathlib

from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.utils.exceptions import BadRequest

from db.queries.fishing import get_all_user_fish, delete_user_fish, get_rod_by_id
from db.queries.users import update_user_balance, get_main_info_fishing, get_main_user_info, update_user_variable
from keyboards.inline.fishing.fishing_inline import sell_fish_keyboard, fishing_store_info, rod_store_keyboard
from keyboards.inline.fishing.fishing_inline_data import fishing_callback
from misc.convert_money import convert_stats
from misc.states.settings_states import FishingState
from misc.user_misc import text_user_balance
from misc.vriables import SMILE_MONEY_TYPE


# ----------------------------- Продажа рыбы --------------------------------#
async def get_fish_info(db_session, user_id):
    user_fish = await get_all_user_fish(db_session, user_id)
    if len(user_fish) < 1:
        text = 'У тебя нет рыбы'

    text = ''
    total_weight = 0
    total_price = 0

    for fish in user_fish:
        fish_user, fish_info = fish
        total_weight += fish_user.weigh
        total_price += fish_user.weigh * fish_info.price
        text += f'🐟 {fish_info.name} {fish_user.weigh} кг. ~ {fish_user.weigh * fish_info.price} руб. {SMILE_MONEY_TYPE.get("money")}\n'

    return total_weight, total_price, text


async def sell_fish_info(call: types.CallbackQuery):
    await call.answer()

    db_session = call.message.bot.get('db')

    total_weight, total_price, text_fish = await get_fish_info(db_session, call.from_user.id)

    text = f'<strong>Скупщик рыбы</strong>\n' \
           f'Точно хочешь продать всю рыбу скупщику?\n\n' \
           f'{text_fish}' \
           f'\nОбщий вес рыбы {convert_stats(m=total_weight)} кг. на {convert_stats(m=total_price)} руб. {SMILE_MONEY_TYPE.get("money")}'
    try:
        await call.message.answer_photo(open(f'{pathlib.Path().absolute()}/image/fishing/fence.png', 'rb'),
                                        text,
                                        reply_markup=await sell_fish_keyboard())
    except BadRequest:
        await call.message.answer_photo(open(f'{pathlib.Path().absolute()}/image/fishing/fence.png', 'rb'),
                                        f'<strong>Скупщик рыбы</strong>\n'
                                        f'Точно хочешь продать всю рыбу скупщику?\n\n'
                                        f'😱 ОГО, у тебя так много рыбы, что она не помещается в соообщение 😱'
                                        f'\nОбщий вес рыбы {convert_stats(m=total_weight)} кг. на {convert_stats(m=total_price)} руб. {SMILE_MONEY_TYPE.get("money")}',
                                        reply_markup=await sell_fish_keyboard()
                                        )


async def accept_sell_fish(call: types.CallbackQuery):
    await call.answer()
    await call.message.delete()
    db_session = call.message.bot.get('db')
    total_weight, total_price, text_fish = await get_fish_info(db_session, call.from_user.id)
    if total_weight <= 0:
        return
    await update_user_balance(db_session, call.from_user.id, 'money', '+', total_price)
    await delete_user_fish(db_session, call.from_user.id)
    await call.message.answer(
        f'Ты продал {convert_stats(vv=total_weight)} кг. рыбы на {convert_stats(m=total_price)} руб. {SMILE_MONEY_TYPE.get("money")}')


# ----------------------------- Покупка наживки --------------------------------#
async def store_fish_info(call: types.CallbackQuery):
    await call.answer()
    await call.message.delete()
    await call.message.answer_photo(open(f'{pathlib.Path().absolute()}/image/fishing/store.png', 'rb'),
                                    '<strong>🎣 Рыболовный магазин</strong>\n\n'
                                    'Выбери, что ты хочешь купить в рыболовном магазине',
                                    reply_markup=await fishing_store_info())


async def bait_store(call: types.CallbackQuery):
    await call.answer()
    db_session = call.message.bot.get('db')
    user_fish, rod, _ = await get_main_info_fishing(db_session, call.from_user.id)
    user = await get_main_user_info(db_session, call.from_user.id)
    await call.message.answer('Пришли мне, сколько наживки ты хочешь купить\n'
                              f'💰 Стоимость одной наживки: {rod.lvl * 10} р.\n'
                              f'💰 Твой баланс: {await text_user_balance(user.money, user.bottle, user.lvl, user.donat, user.keyses)} | {user_fish.bait} 🍣\n'
                              f'Для отмены пришли мне 0')
    await FishingState.GetCountBaitBuy.set()


async def count_bait_buy(message: types.Message, state: FSMContext):
    if message.text == '0':
        await message.answer('Отмена')
        await state.finish()
        return
    if not message.text.isdigit():
        await message.answer('Пришли мне сколько наживки ты хочешь купить числом или 0 для отмены')
        return

    db_session = message.bot.get('db')
    user = await get_main_user_info(db_session, message.from_user.id)
    user_fish, rod, _ = await get_main_info_fishing(db_session, message.from_user.id)
    count_bait = int(message.text)
    price_bait = count_bait * (rod.lvl * 10)

    if user.money < price_bait:
        await message.answer('Недостаточно средств для покупки.\n'
                             f'💰 Стоимость одной наживки: {rod.lvl * 10} р.\n'
                             f'💰 Твой баланс: {await text_user_balance(user.money, user.bottle, user.lvl, user.donat, user.keyses)} | {user_fish.bait} 🍣\n'
                             f'Для отмены пришли мне 0')
        return

    await update_user_balance(db_session, message.from_user.id, 'money', '-', price_bait)
    await update_user_variable(db_session, message.from_user.id, 'bait', '+', count_bait)
    await message.answer(f'Ты купил {count_bait} 🍣 за {convert_stats(m=price_bait)}')
    await state.finish()


async def rod_store(call: types.CallbackQuery):
    await call.answer()
    await call.message.delete()

    db_session = call.message.bot.get('db')
    user_fish, rod, _ = await get_main_info_fishing(db_session, call.from_user.id)
    next_rod = await get_rod_by_id(db_session, rod.id + 1)

    await call.message.answer_photo(open(f'{pathlib.Path().absolute()}/image/fishing/store.png', 'rb'),
                                    caption='<strong>🎣 Магазин удочек</strong>\n\n'
                                            'Твоя удочка на данный момент:\n'
                                            f'🎣 {rod.name}\n'
                                            f'Следующая удочка:\n'
                                            f'🎣 {next_rod.name}\n'
                                            f'Стоимость улучшения: {next_rod.price} ⚙️',
                                    reply_markup=await rod_store_keyboard())


async def update_rod(call: types.CallbackQuery):
    await call.answer()
    await call.message.delete()

    db_session = call.message.bot.get('db')
    user_fish, rod, _ = await get_main_info_fishing(db_session, call.from_user.id)
    next_rod = await get_rod_by_id(db_session, rod.id + 1)

    if user_fish.rod_detail < next_rod.price:
        await call.message.answer('Недостаточно средств для покупки')
        return

    await update_user_variable(db_session, call.from_user.id, 'rod', '+', 1)
    await update_user_variable(db_session, call.from_user.id, 'rod_detail', '-', next_rod.price)

    await call.message.answer(f'Удочка улучшена до {next_rod.name}')


def register_fishing_store_handlers(dp: Dispatcher):
    dp.register_callback_query_handler(sell_fish_info, fishing_callback.filter(event='sell', type='sell'),
                                       chat_type='private')
    dp.register_callback_query_handler(accept_sell_fish, fishing_callback.filter(event='sell_fish', type='sell_fish'),
                                       chat_type='private')
    dp.register_callback_query_handler(store_fish_info, fishing_callback.filter(event='store', type='store'),
                                       chat_type='private')
    dp.register_callback_query_handler(bait_store, fishing_callback.filter(event='bait_buy', type='bait_buy'),
                                       chat_type='private')
    dp.register_message_handler(count_bait_buy, state=FishingState.GetCountBaitBuy, chat_type='private')
    dp.register_callback_query_handler(rod_store, fishing_callback.filter(event='rod_buy', type='rod_buy'),
                                       chat_type='private')
    dp.register_callback_query_handler(update_rod, fishing_callback.filter(event='update_bait', type='update_bait'),
                                       chat_type='private')
