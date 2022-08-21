from PIL import Image
import pathlib


async def generate_image(number, user_id):
    dvor = Image.open(f'{pathlib.Path().absolute()}/image/works/dvor/dvor_number.png')
    trash = Image.open(f'{pathlib.Path().absolute()}/image/works/dvor/trash.png')
    pos = {1: (600, 425), 2: (320, 412), 3: (919, 401), 4: (382, 404), 5: (728, 403), 6: (67, 521)}
    scale = {1: (52, 66), 2: (42, 53), 3: (24, 31), 4: (19, 24), 5: (19, 24), 6: (114, 145)}
    trash = trash.resize(scale.get(number), Image.ANTIALIAS)
    dvor.paste(trash, pos.get(number), trash)
    dvor.save(f'{pathlib.Path().absolute()}/image/works/dvor/{user_id}_dvor.png')