from PIL import Image
import pathlib


async def generate_image_gum(shot_type, user_id):
    image = Image.open(f'{pathlib.Path().absolute()}/image/gum/profile.png')
    bomj = Image.open(f'{pathlib.Path().absolute()}/image/gum/bomj.png')
    aim = Image.open(f'{pathlib.Path().absolute()}/image/gum/aim.png').convert('RGBA')
    aim = aim.resize((94, 94), Image.ANTIALIAS)
    coords = {1: (45, 16), 2: (45, 140), 3: (72, 418)}
    bomj.paste(aim, coords.get(shot_type), aim)
    image.paste(bomj, (428, 65), bomj)
    image.save(f'{pathlib.Path().absolute()}/image/gum/{user_id}.png')