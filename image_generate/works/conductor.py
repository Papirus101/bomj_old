import pathlib
import random
import datetime

from faker import Faker
from PIL import Image, ImageDraw, ImageFont
from sqlalchemy.ext.asyncio import AsyncSession

from db.queries.users import update_event_id


async def get_fake(db_session: AsyncSession, user_id: int):
    faker = Faker('ru_RU')
    passenger_name_true = random.choices([True, False], [80, 20])[0]
    passenger_date_true = random.choices([True, False], [80, 20])[0]
    if passenger_name_true and passenger_date_true:
        await update_event_id(db_session, user_id, 1)
        name_pass = faker.name_male()
        fake_name = name_pass
        date_pass = faker.date_between(start_date='today')
    else:
        await update_event_id(db_session, user_id, 2)
        if not passenger_date_true:
            date_pass = faker.date_between(start_date='-20d', end_date='-3d')
        else:
            date_pass = faker.date_between(start_date='+10d', end_date='+200d')
        if not passenger_name_true:
            name_pass = faker.name_male()
            fake_name = faker.name_male()
        else:
            name_pass = faker.name_male()
            fake_name = name_pass
    adress = faker.address()
    birthday = faker.date(pattern='%d-%m-%Y')
    await generate_image(user_id, name_pass, fake_name, date_pass, adress, birthday)


async def generate_image(user_id, name, fake_name, date, address, birthday):
    tralik = Image.open(f'{pathlib.Path().absolute()}/image/works/conductor/check.png')
    draw_text = ImageDraw.Draw(tralik)
    font = ImageFont.truetype(f'{pathlib.Path().absolute()}/image/font.otf', size=18)
    text = f'Сегодня {datetime.datetime.now().strftime("%d-%m-%Y")}'
    w, h = draw_text.textsize(text, font=font)
    (width, height) = tralik.size
    draw_text.text(((width - w) / 2, height - h), text, fill="white", font=font)
    draw_text.text(
        (1027, 576),
        name.replace(' ', '\n'),
        font=font,
        fill=('black')
    )
    draw_text.text(
        (1098, 644),
        f'{birthday}',
        font=font,
        fill=('black'))
    draw_text.text(
        (1028, 684),
        address.replace(", ", '\n'),
        font=font,
        fill=('black')
    )
    draw_text.text(
        (67, 596),
        fake_name,
        font=font,
        fill=('black')
    )
    draw_text.text(
        (67, 690),
        str(date.strftime("%d-%m-%Y")),
        font=font,
        fill=('black')
    )
    tralik.save(f'{pathlib.Path().absolute()}/image/works/conductor/{user_id}_event.png')