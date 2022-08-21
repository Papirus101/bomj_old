from db.queries.banda_q import update_banda_stars
from db.queries.users import get_all_online_users_with_business, update_user_balance, get_top_users_maxa_event, \
    get_users_with_end_vip, update_user_variable, clear_event_count, get_winner_fishing_event
from db.session import async_sessionmaker
from misc.convert_money import convert_stats
from misc.user_misc import get_user_business_profit
from misc.vriables import SMILE_MONEY_TYPE, MEDAL_TYPES, MAXA_FINISH, BOMJ_CHAT_ID, COUNT_BANDA_RATING, \
    PRISE_FISHING_EVENT


async def business_add_money(bot):
    users = await get_all_online_users_with_business(async_sessionmaker)
    for user in users:
        profit = await get_user_business_profit(async_sessionmaker, user)
        profit_text = ''
        for profit_type in profit.keys():
            profit_text += f'➕ {profit.get(profit_type)} {SMILE_MONEY_TYPE.get(profit_type)}\n'
            await update_user_balance(async_sessionmaker, user.telegram_id, profit_type, '+', profit.get(profit_type))
        await bot.send_message(chat_id=user.telegram_id, text='<strong>🕓 PAYDAY 🕓</strong>\n'
                                                              '🤑 Тебе пришёл доход с бизнеса\n'
                                                              f'{profit_text}')


async def check_vip(bot):
    users = await get_users_with_end_vip(async_sessionmaker)
    for user in users:
        print(user)
        await bot.send_message(chat_id=user.telegram_id, text='<strong>👑 Срок действия ВИП статуса закончился</strong>')


async def banda_event_finish(bot):
    bands, users = await get_top_users_maxa_event(async_sessionmaker)
    if len(bands) < 1:
        return
    text = '<strong>❗ ☠️ ️Итоги еженедельного соревнования между бандами ⚔️ ❗️</strong>'
    for pos, banda in enumerate(bands, start=1):
        print(banda.name, pos)
        await update_banda_stars(async_sessionmaker, banda.id, '+', COUNT_BANDA_RATING.get(pos))
        text += f'\n\nБанда {banda.smile} {banda.name} занимает {MEDAL_TYPES.get(pos)} {pos}-е место:\n'
        for user_pos, user in enumerate(users[pos - 1], start=1):
            prise = MAXA_FINISH.get(pos).get(user_pos)
            prise_text = ''
            for current_prise in prise.keys():
                await update_user_variable(async_sessionmaker, user.telegram_id, current_prise, '+', prise.get(current_prise))
                prise_text += f'--- {SMILE_MONEY_TYPE.get(current_prise)} {convert_stats(m=prise.get(current_prise))}\n'
            await bot.send_message(chat_id=user.telegram_id, text=f'🥳 Ты занял {MEDAL_TYPES.get(user_pos)} {user_pos}-е место в соревноавнии среди своей банды\n'
                                                                  f'- Твоя нагарада:\n'
                                                                  f'{prise_text}')
            text += f'- {MEDAL_TYPES.get(user_pos)} {user.name} {convert_stats(m=user.info.get("maxa_week"))} ⚔️\n' \
                    f'-- Получает:\n' \
                    f'{prise_text}'
    await clear_event_count(async_sessionmaker, 'maxa_week')
    await bot.send_message(chat_id=BOMJ_CHAT_ID, text=text)


async def fishing_event_finish(bot):
    users = await get_winner_fishing_event(async_sessionmaker)
    text = '<strong>❗ 🎣 Итоги рыболовного соревнования 🐟 ❗</strong>'
    for pos, user in enumerate(users, start=1):
        prise = PRISE_FISHING_EVENT.get(pos)
        prise_text = ''
        for current_prise in prise.keys():
            prise_text += f'-- {convert_stats(m=prise.get(current_prise))} {SMILE_MONEY_TYPE.get(current_prise)}\n'
            await update_user_variable(async_sessionmaker, user.telegram_id, current_prise, '+',
                                       prise.get(current_prise))
        try:
            await bot.send_message(chat_id=user.telegram_id, text=f'Ты занял {pos}-e {MEDAL_TYPES.get(pos)} место в рыболовнов совревновании\n'
                                                                  f'Твоя награда:\n'
                                                                  f'{prise_text}')
        except:
            pass
        text += f'{MEDAL_TYPES.get(pos)} {user.name} {convert_stats(m=user.info.get("fishing"))} 🐟\n' \
                f'- Получает:\n' \
                f'{prise_text}'
    await clear_event_count(async_sessionmaker, 'fishing')
    await bot.send_message(chat_id=BOMJ_CHAT_ID, text=text)
