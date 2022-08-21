from aiogram import types, Dispatcher
from aiogram.dispatcher.filters import Text

from db.queries.items import close_user_order
from db.queries.users import get_main_user_info
from db.queries.works import get_user_works
from keyboards.inline.works.works_data import works_callback

from keyboards.inline.works.works_inline import works_menu
from keyboards.reply.works_keyboard import works_optional

from misc.user_misc import text_user_balance


async def works_main(message: types.Message):
    await message.answer('Выбери интересующий тебя вид заработка',
                         reply_markup=await works_optional())


async def works_info(message: types.Message):
    db_session = message.bot.get('db')

    user = await get_main_user_info(db_session, message.from_user.id)
    works = await get_user_works(db_session, user.lvl)
    user_balance = await text_user_balance(user.money, user.bottle, user.lvl, user.donat, user.keyses)

    await message.answer('<strong>Центр занятости</strong>\n\n'
                         'Выбери работу, которая тебя интересует, но не забывай, что ты устраиваишься'
                         'на официальную работу и тебе надо будет платить налоги\n'
                         'Каждый раз случайным образом будет выбирать, успешность укланения от налогов\n'
                         'Подоходный налог состовляет 13% от заработанной суммы\n\n'
                         f'{user_balance}',
                         reply_markup=await works_menu(works))


async def dismissal(call: types.CallbackQuery):
    await call.answer('Ты уволился', show_alert=True)
    await close_user_order(call.message.bot.get('db'), call.from_user.id)
    await call.message.delete()


def register_works_main_handler(dp: Dispatcher):
    dp.register_message_handler(works_main, Text(equals='🛠 Работы'), chat_type='private')
    dp.register_message_handler(works_info, Text(equals='💰 Работать'), chat_type='private')
    dp.register_callback_query_handler(dismissal, works_callback.filter(event='0'))
