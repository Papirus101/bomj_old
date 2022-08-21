import pathlib

from PIL import Image, ImageDraw, ImageFont


async def generate_fish_image(fish_id: int, user_id: int):
    print('kek')
    main_img = Image.open(f'{pathlib.Path().absolute()}/image/fishing/1.png')
    fish_image = Image.open(f'{pathlib.Path().absolute()}/image/fishing/{fish_id}_fish.png')
    fish_image = fish_image.resize((1248, 364), Image.ANTIALIAS)
    main_img.paste(fish_image, (51, 302), fish_image)
    main_img.save(f'{pathlib.Path().absolute()}/image/fishing/{user_id}_fishing.png')