from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text

from db.models.user_db import Users
from db.queries.users import get_main_user_info, update_user_balance
from keyboards.inline.main_callback import profile_callback
from keyboards.inline.main_inline import change_bottle_keyboard
from misc.convert_money import convert_stats
from misc.states.settings_states import ChangeBottleState
from misc.user_misc import text_user_balance


async def bottle_change_info(message: types.Message):
    db_session = message.bot.get('db')
    user: Users = await get_main_user_info(db_session, message.from_user.id)
    await message.answer('💱 Приём стеклотары\n\n'
                         'Тут ты можешь поменять свои накопленные бутылки на рубли\n'
                         '1 бутылка - 3 рубля\n'
                         f'{await text_user_balance(user.money, user.bottle, user.exp, user.donat, user.keyses)}',
                         reply_markup=await change_bottle_keyboard())


async def change_bottle(call: types.CallbackQuery):
    db_session = call.message.bot.get('db')
    await call.answer()
    await call.message.delete()
    user: Users = await get_main_user_info(db_session, call.from_user.id)

    await call.message.answer('Пришли мне, сколько бутылок ты хочешь поменять или 0 для отмены\n'
                              f'У тебя бутылок ~ на {convert_stats(money=user.bottle * 3)} руб.\n'
                              f'{await text_user_balance(user.money, user.bottle, user.exp, user.donat, user.keyses)}')
    await ChangeBottleState.CountBottleChange.set()


async def get_count_bottle_change(message: types.Message, state: FSMContext):
    if message.text == '0':
        await message.answer('Отмена')
        await state.finish()
        return
    if not message.text.isdigit():
        await message.answer('Пришли мне кол-во бутылок для обмена числом или 0 для отмены')
        return

    db_session = message.bot.get('db')
    count_sell_bottle = int(message.text)
    total_money = count_sell_bottle * 3
    user: Users = await get_main_user_info(db_session, message.from_user.id)

    if user.bottle < count_sell_bottle:
        await message.answer('У тебя нет столько бутылок, попробуй ещё раз или пришли мне 0 для отмены\n\n'
                             f'{await text_user_balance(user.money, user.bottle, user.exp, user.donat, user.keyses)}')
        return

    await message.delete()
    await update_user_balance(db_session, message.from_user.id, 'money', '+', total_money)
    await update_user_balance(db_session, message.from_user.id, 'bottle', '-', count_sell_bottle)
    await message.answer(f'Ты поменял {convert_stats(money=count_sell_bottle)} бут. на {convert_stats(money=total_money)} руб.')
    await state.finish()


def register_change_bottle_handler(dp: Dispatcher):
    dp.register_message_handler(bottle_change_info, Text(equals='💱🍾 Обмен бутылок'), chat_type='private')
    dp.register_callback_query_handler(change_bottle, profile_callback.filter(event='change_bottle'), chat_type='private')
    dp.register_message_handler(get_count_bottle_change, state=ChangeBottleState.CountBottleChange, chat_type='private')
