from PIL import Image
import pathlib


async def generate_image(event_id: int, user_id: int):
    conveer = Image.open(f'{pathlib.Path().absolute()}/image/works/sort/conveer.png')
    musor_name = {1: 'disk.png', 2: 'bottle.png', 3: 'plastik.png'}
    musor = Image.open(f'{pathlib.Path().absolute()}/image/works/sort/{musor_name.get(event_id)}')
    conveer.paste(musor, (390, 260), musor)
    conveer.save(f'{pathlib.Path().absolute()}/image/works/sort/{user_id}_sort.png')