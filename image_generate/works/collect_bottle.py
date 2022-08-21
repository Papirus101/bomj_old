import pathlib
import random
import datetime

from PIL import Image, ImageDraw, ImageFont
from sqlalchemy.ext.asyncio import AsyncSession


async def generate_collect_bottle_image(event_id: int, user_id: int):
    svalka = Image.open(f'{pathlib.Path().absolute()}/image/bottle/svalka.jpeg')
    bottle = Image.open(f'{pathlib.Path().absolute()}/image/bottle/bottle.png')
    coords = {1: (70, 120), 2: (310, 120), 3: (570, 120), 4: (70, 340), 5: (310, 340), 6: (570, 340)}
    svalka.paste(bottle, coords.get(event_id), bottle)
    svalka.save(f'{pathlib.Path().absolute()}/image/bottle/{user_id}_bottle.png')
