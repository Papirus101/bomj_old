import asyncio

from aiogram import types
from aiogram.dispatcher.middlewares import BaseMiddleware

from db.queries.active import update_user_active
from db.session import async_sessionmaker


class UserActiveMiddleware(BaseMiddleware):
    skip_patterns = ["error", "update"]

    async def on_pre_process_callback_query(self, callback: types.CallbackQuery, data, *args):
        text = callback.data.split(':')[0]
        chat_type = callback.message.chat.type
        if chat_type == 'private':
            print(callback.from_user.full_name, text)
            try:
                data_active = await update_user_active(async_sessionmaker, callback.from_user.id)
            except:
                data_active = True
            if data_active:
                await callback.answer('Подключаемся к серверу...', show_alert=True)
                await asyncio.sleep(2)
        elif chat_type == 'supergroup':
            pass

    async def on_pre_process_message(self, message: types.Message, data, *args):
        text = message.text.split(':')[0]
        chat_type = message.chat.type
        if chat_type == 'private':
            print(message.from_user.full_name, text)
        elif chat_type == 'supergroup':
            pass
