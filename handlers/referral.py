from aiogram import types, Dispatcher
from db.queries.users import get_referral_user

from keyboards.inline.main_callback import profile_callback


async def referral(call: types.CallbackQuery):
    db_session = call.message.bot.get('db')
    
    users = await get_referral_user(db_session, call.from_user.id)
    
    text = '<strong>Реферальная система</strong>\n\n' \
           'При достижении твоим рефералом 3-го уровня, ты получаешь +2 дня вип статуса\n\n' \
           f'Всего рефералов: {len(users)}\n'
    
    if len(users) > 0:
        for user in users:
            text += f'<a href="https://t.me/{user.username}">{user.name}</a>\n'
            
    if len(text) > 4000:
        text = 'Воу, у тебя так много рефералов, что они даже не помещаются в одно сообщение\n' \
            f'Всего рефералов: {len(users)}'
    
    await call.answer()
    await call.message.answer(text)
    await call.message.answer(f'Начни играть прямо сейчас и получи ВИП статус на 2 для быстрого старта\n'
                              f'<a href="https://t.me/BomjSimBot?start=ref_{call.from_user.id}">Начать играть</a>',
                              disable_web_page_preview=False)


def register_referral_handlers(dp: Dispatcher):
    dp.register_callback_query_handler(referral, profile_callback.filter(event='ref'))