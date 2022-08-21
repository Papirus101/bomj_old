from random import random
from db.queries.user_business import update_business_products
from db.queries.users import update_user_balance
from misc.convert_money import convert_stats
from misc.services import scheduler, redis

from aiogram import types
import pathlib
import random

from PIL import Image

from keyboards.inline.needs.needs_inline import needs_event_delivery_keyboard


async def needs_check_event_delivery(message):
    event_info = await redis.hgetall(f'{message.from_user.id}_delivery')
    scheduler.remove_job(job_id=f'{message.from_user.id}_delivery')
    if event_info['event_id'] == '-1':
        return
    if event_info['event_id'] != '0':
        await message.answer('Ты ничего не выбрал, задание провалено')
        return
    if event_info['count_events'] == '5':
        db_session = message.bot.get('db')
        await message.answer('Воу, ты справился с задачей и довёз неообходимое кол-во товаров до бизнеса\n'
                             f'Твой заработок составил {convert_stats(m=int(event_info["count_delivery_product"]) * 30)} руб.')
        await redis.delete(f'{message.from_user.id}_delivery')
        await update_business_products(db_session, event_info['business_type'], int(event_info['count_delivery_product']), '+')
        await update_user_balance(db_session, message.from_user.id, 'money', '+', int(event_info['count_delivery_product']) * 30)
        return
    await create_event_delivery_fuel(message, int(event_info['count_delivery_product']), event_info['business_type'], int(event_info['count_events']) + 1)
    


async def create_event_delivery_fuel(message, count_product_delivery, business_type, count_events):
    event_id = random.randint(3, 5)
    await redis.hmset(f'{message.from_user.id}_delivery',
                {'count_delivery_product': count_product_delivery,
                'event_id': event_id,
                'business_type': business_type,
                'count_events': count_events})
    event = Image.open(f'{pathlib.Path().absolute()}/image/race/race_event_345.png')
    arrows = {3: 'arrow_right', 4: 'arrow_left', 5: 'arrow_pryamo'}
    arrow = Image.open(f'{pathlib.Path().absolute()}/image/race/{arrows.get(event_id)}.png')
    event.paste(arrow, (350, 51), arrow)
    event.save(f'{pathlib.Path().absolute()}/image/race/{message.from_user.id}_event.png')
    if event_id == 3:
        text = 'Поворачивай направо!'
    elif event_id == 4:
        text = 'Поворачивай налево!'
    elif event_id == 5:
        text = "Газуй прямо!"
    await message.answer_photo(
        open(f'{pathlib.Path().absolute()}/image/race/{message.from_user.id}_event.png', 'rb'),
        caption=f'{text}\n'
                f'У тебя есть {count_product_delivery / 20} с. чтобы решить',
        reply_markup=await needs_event_delivery_keyboard())
    scheduler.add_job(needs_check_event_delivery, "interval", seconds=count_product_delivery / 20, args=(message,), id=f'{message.from_user.id}_delivery')
