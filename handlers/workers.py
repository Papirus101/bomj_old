from aiogram import types, Dispatcher
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher import FSMContext

from db.queries.users import get_user_profile, update_user_balance, update_workers

from keyboards.inline.main_inline import workers_keyboard
from keyboards.inline.main_callback import profile_callback

from misc.states.workers_state import WorkersState
from misc.convert_money import convert_stats
from misc.vriables import SMILE_MONEY_TYPE

async def workers_info(message: types.Message):
    db_session = message.bot.get('db')
    
    user_info = await get_user_profile(db_session, message.from_user.id)
    await message.answer('Ты пришёл в местный вытрезвитель\n'
                         'Тут ты можешь нанять других бомжей, чтобы они носили тебе бутылки, поселив у себя в жилье\n'
                         f'Цена за наём одного бомжа: 2.000 руб {SMILE_MONEY_TYPE.get("money")}\n'
                         f'У тебя {user_info[0].bomj}/{user_info[1].bomj} чел. 👨\n'
                         f'Твой баланс: {convert_stats(money=user_info[0].money)} {SMILE_MONEY_TYPE.get("money")}'
                         f'| {convert_stats(m=user_info[0].bottle)} {SMILE_MONEY_TYPE.get("bottle")}\n',
                         reply_markup=await workers_keyboard())
    
    
async def add_workers(call: types.CallbackQuery, state: FSMContext):
    db_session = call.message.bot.get('db')

    user_info = await get_user_profile(db_session, call.from_user.id)
    await call.answer()
    await call.message.answer('Пришли мне, сколько работяг ты хочещь нанять или 0 для отмены\n'
                              f'У тебя {user_info[0].bomj}/{user_info[1].bomj} чел.\n'
                              f'Твой баланс: {convert_stats(money=user_info[0].money)} {SMILE_MONEY_TYPE.get("money")}'
                              f'| {convert_stats(m=user_info[0].bottle)} {SMILE_MONEY_TYPE.get("bottle")}\n')
    await WorkersState.GetCountWorkers.set()
    
    
async def get_count_workers(message: types.Message, state: FSMContext):
    count_workers = message.text
    if count_workers == '0':
        await message.answer('Отмена')
        await state.finish()
        return
    if not count_workers.isdigit():
        await message.answer('Пришли мне количество работяг числом или 0 для отмены')
        return
    
    db_session = message.bot.get('db')
    user_info = await get_user_profile(db_session, message.from_user.id)
    count_workers = int(count_workers)
    if count_workers > user_info[1].bomj or user_info[0].bomj + count_workers > user_info[1].bomj:
        await message.answer('В твоём жилье недостаточно мест для такого количества рабочих\n'
                             f'У тебя {user_info[0].bomj}/{user_info[1].bomj} чел.\n'
                             f'Твой баланс: {convert_stats(money=user_info[0].money)} {SMILE_MONEY_TYPE.get("money")}'
                             f'| {convert_stats(m=user_info[0].bottle)} {SMILE_MONEY_TYPE.get("bottle")}\n'
                             'Попробуй ещё раз или пришли мне 0 для отмены')
        return
    price_workers = count_workers * 2000
    if price_workers > user_info[0].money:
        await message.answer('У тебя недостаточно средтс для найма такого количества рабочих\n'
                             f'У тебя {user_info[0].bomj}/{user_info[1].bomj} чел.\n'
                             f'Твой баланс: {convert_stats(money=user_info[0].money)} {SMILE_MONEY_TYPE.get("money")}'
                             f'| {convert_stats(m=user_info[0].bottle)} {SMILE_MONEY_TYPE.get("bottle")}\n'
                             'Попробуй ещё раз или пришли мне 0 для отмены')
        return
    await update_workers(db_session, message.from_user.id, '+', count_workers)
    await update_user_balance(db_session, message.from_user.id, 'money', '-', price_workers)
    await message.answer(f'Ты нанял {count_workers} чел. за {price_workers} руб. {SMILE_MONEY_TYPE.get("money")}')
    await state.finish()
    


def register_workers_handler(dp: Dispatcher):
    dp.register_message_handler(workers_info, Text(equals='👨 Работники'), chat_type='private')
    dp.register_callback_query_handler(add_workers, profile_callback.filter(event='add_workers'), chat_type='private')
    dp.register_message_handler(get_count_workers, state=WorkersState.GetCountWorkers, chat_type='private')