from PIL import Image
import pathlib


async def generate_image(event_id: int, user_id: int):
    background = Image.open(f'{pathlib.Path().absolute()}/image/works/security/larek.png')
    bomjs = {1: 'bomj.png', 2: 'bomjvor.png', 3: 'bomjgang.png'}
    bomj = Image.open(f'{pathlib.Path().absolute()}/image/works/security/{bomjs.get(event_id)}')
    coord_x = 540
    coord_y = 350
    background.paste(bomj, (coord_x, coord_y), bomj)
    background.save(f'{pathlib.Path().absolute()}/image/works/security/{user_id}_security.png')


async def generate_gang_image(event_id: int, user_id: int):
    bomj = Image.open(f'{pathlib.Path().absolute()}/image/works/security/bomjgang.png').convert("RGBA")
    aim = Image.open(f'{pathlib.Path().absolute()}/image/works/security/aim.png').convert("RGBA")
    laarek = Image.open(f'{pathlib.Path().absolute()}/image/works/security/larek.png').convert("RGBA")
    coords = {1: (-30, -40), 2: (-30, 230), 3: (-30, 300)}
    bomj.paste(aim, coords.get(event_id), aim)
    laarek.paste(bomj, (540, 350), bomj)
    laarek.save(f'{pathlib.Path().absolute()}/image/works/security/{user_id}_bomjgang.png')