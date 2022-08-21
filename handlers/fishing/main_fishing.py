from aiogram import types, Dispatcher
from aiogram.dispatcher.filters import Text

from db.queries.users import get_main_info_fishing, get_top_event
from keyboards.inline.fishing.fishing_inline import fishing_main_keyboard

from misc.convert_money import convert_stats

import pathlib

from misc.vriables import MEDAL_TYPES, SMILE_MONEY_TYPE
from static.text.fishing import MAIN_FISHING_TEXT


async def fishing_info(message: types.Message):
    db_session = message.bot.get('db')
    user, rod, fishs = await get_main_info_fishing(db_session, message.from_user.id)
    top_users = await get_top_event(db_session, 'fishing')
    top_text = ''
    total_price = 0
    total_weight = 0
    for fish in fishs:
        total_price += fish.price
        total_weight += fish.weight
    for pos, top_user in enumerate(top_users, start=1):
        top_text += f'{MEDAL_TYPES.get(pos)} {top_user.name}: {top_user.fishing} шт.\n'
    await message.answer_photo(open(f'{pathlib.Path().absolute()}/image/fishing/main.png', 'rb'),
                               caption=MAIN_FISHING_TEXT.format(
                                   top_users=top_text,
                                   user_fish=user.info.get('fishing', 0) if user.info is not None else 0,
                                   user_detail=user.rod_detail,
                                   user_bait=user.bait,
                                   user_rod=rod.name,
                                   user_fish_weight=0 if len(fishs) < 1 else total_weight,
                                   user_fish_price=0 if len(fishs) < 1 else convert_stats(m=total_price),
                                   money_smile=SMILE_MONEY_TYPE.get('money')
                                   ),
                               reply_markup=await fishing_main_keyboard())



def register_main_fishing_handlers(dp: Dispatcher):
    dp.register_message_handler(fishing_info, Text(equals='🎣 Рыбалка'), chat_type='private')
