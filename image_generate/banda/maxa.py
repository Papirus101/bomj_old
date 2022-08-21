from PIL import Image, ImageFont, ImageDraw
import pathlib

from image_generate.profile.generate_bomj import generate_bomj_image


async def maxa_image_generate(db_session, first_name, second_name, user, enemy):
    image = Image.open(f'{pathlib.Path().absolute()}/image/banda/maxa.png')

    await generate_bomj_image(db_session, user)
    bomj_img = Image.open(f'{pathlib.Path().absolute()}/image/profile/{user.telegram_id}_bomj.png')
    bomj_img = bomj_img.resize((214, 485), Image.ANTIALIAS)
    image.paste(bomj_img, (827, 43), bomj_img)

    await generate_bomj_image(db_session, user)
    bomj_img = Image.open(f'{pathlib.Path().absolute()}/image/profile/{enemy.telegram_id}_bomj.png')
    bomj_img = bomj_img.resize((214, 485), Image.ANTIALIAS)
    image.paste(bomj_img, (191, 237), bomj_img)

    font = ImageFont.truetype(f'{pathlib.Path().absolute()}/image/font.otf', size=40)
    sky_first = Image.open(f'{pathlib.Path().absolute()}/image/banda/sky_first.png')
    sky_second = Image.open(f'{pathlib.Path().absolute()}/image/banda/sky_second.png')
    draw_text_sky_first = ImageDraw.Draw(sky_first)
    draw_text_sky_seocnd = ImageDraw.Draw(sky_second)

    if len(first_name.split()) > 1:
        first_name = first_name.replace(' ', '\n')
    if len(second_name.split()) > 1:
        second_name = second_name.replace(' ', '\n')

    (width, height) = sky_first.size
    w, h = draw_text_sky_first.textsize(first_name, font=font)
    draw_text_sky_first.text(((width - w) / 2, 120), first_name, fill="black", font=font)

    (width, height) = sky_second.size
    w, h = draw_text_sky_seocnd.textsize(second_name, font=font)
    draw_text_sky_seocnd.text(((width - w) / 2, 70), second_name, fill="black", font=font)

    image.paste(sky_first, (725, 479), sky_first)
    image.paste(sky_second, (191, 21), sky_second)
    image.save(f'{pathlib.Path().absolute()}/image/banda/{user.telegram_id}.png')


async def generate_winner_maxa_image(winner: bool, user_id: int):
    image = Image.open(f'{pathlib.Path().absolute()}/image/banda/{user_id}.png')
    win = Image.open(f'{pathlib.Path().absolute()}/image/banda/win.png')
    lose = Image.open(f'{pathlib.Path().absolute()}/image/banda/bam.png')
    if winner:
        image.paste(win, (636, 2), win)
        image.paste(lose, (184, 298), lose)
    else:
        image.paste(win, (57, 209), win)
        image.paste(lose, (730, 129), lose)
    image.save(f'{pathlib.Path().absolute()}/image/banda/{user_id}.png')