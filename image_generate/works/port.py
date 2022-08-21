from PIL import Image, ImageFont, ImageDraw
import pathlib
import random


async def generate_image(number, user_id):
    port = Image.open(f'{pathlib.Path().absolute()}/image/works/port/port.png')
    corob = Image.open(f'{pathlib.Path().absolute()}/image/works/port/corob.png')
    coords_korob = [(70, 22), (389, 22), (718, 22), (70, 230), (389, 230), (718, 230)]
    draw_image = ImageDraw.Draw(port)
    font = ImageFont.truetype(f'{pathlib.Path().absolute()}/image/font.otf', size=105)
    for pos in range(1, 7):
        coords = random.choice(coords_korob)
        draw_image.text(
            coords,
            f'{pos}',
            font=font,
            fill=('#000000')
        )
        if pos == number:
            port.paste(corob, (coords[0], coords[1] + 118), corob)
        coords_korob.remove(coords)
    port.save(f'{pathlib.Path().absolute()}/image/works/port/{user_id}_port.png')