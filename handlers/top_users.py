from this import d
from aiogram import types, Dispatcher

from db.queries.users import get_top_with_category

from misc.convert_money import convert_stats

from keyboards.inline.main_callback import profile_callback
from keyboards.inline.top_users.top_users_inline import top_users_keyboard
from keyboards.inline.top_users.top_users_data import top_users_callback

from misc.vriables import MEDAL_TYPES, SMILE_MONEY_TYPE


async def get_top_by_category(db_session, category):
    users = await get_top_with_category(db_session, category)
    text = f'Топ игроков по {SMILE_MONEY_TYPE.get(category)}\n'
    for id, user in enumerate(users, start=1):
        text += (
            f'{MEDAL_TYPES.get(id) if MEDAL_TYPES.get(id, False) else "🎖"} {user[1]}: {convert_stats(money=user[0])} {SMILE_MONEY_TYPE.get(category)}\n')
    return text


async def main_top(call: types.CallbackQuery):
    await call.answer()

    await call.message.answer('Выбери категорию, по которой хочешь получить лучших игроков',
                              reply_markup=await top_users_keyboard())


async def get_current_top(call: types.CallbackQuery, callback_data: dict):
    await call.answer()

    category = callback_data.get('event')
    db_session = call.message.bot.get('db')
    text = await get_top_by_category(db_session, category)
    await call.message.edit_text(text, reply_markup=await top_users_keyboard())


def register_top_users_handler(dp: Dispatcher):
    dp.register_callback_query_handler(main_top, profile_callback.filter(event='top'))
    dp.register_callback_query_handler(get_current_top, top_users_callback.filter(), chat_type='private')
