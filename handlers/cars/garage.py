from aiogram import types, Dispatcher
from aiogram.dispatcher.filters import Text

from db.queries.cars_q import get_user_active_car, get_car_in_store
from db.queries.users import get_main_user_info
from keyboards.inline.cars_inline import none_car_keyboard


async def garage_main(message: types.Message):
    db_session = message.bot.get('db')
    user_car = await get_user_active_car(db_session, message.from_user.id)
    if user_car is None:
        await message.answer('У тебя нет машины, приобрести её можно в автосалоне',
                             reply_markup=await none_car_keyboard())


async def get_info_by_car(car_id: int, db_session):
    car = await get_car_in_store(db_session, 1)


async def car_store(call: types.CallbackQuery):
    db_session = call.message.bot.get('db')
    user = await get_main_user_info(db_session, call.from_user.id)
    await call.answer()
    await call.message.delete()


def register_garage_handlers(dp: Dispatcher):
    dp.register_message_handler(garage_main, Text(equals='🚘 Гараж'), chat_type='private')
