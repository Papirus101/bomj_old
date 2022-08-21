import pathlib

from PIL import Image, ImageDraw, ImageFont

from misc.convert_money import convert_stats
from misc.user_misc import get_user_business_profit

from image_generate.profile.generate_bomj import generate_bomj_image


async def health_generate(health: int, draw_image, health_type: str):
    health_coord = {
        'health': (580, 380),
        'luck': (638, 380),
        'eat': (608, 380)
    }
    color = '#13FF00'
    if health <= 15:
        color = 'red'
    elif health < 80:
        color = 'yellow'
    draw_image.rounded_rectangle(xy=((health_coord.get(health_type)[0],
                                      health_coord.get(health_type)[1]),
                                     (health_coord.get(health_type)[0] + 1,
                                      health_coord.get(health_type)[1] + (80 * health / 100))),
                                 fill=color,
                                 radius=10)


# async def generate_car_profile(car_id: int, number: str):
#     main = Image.open(f'{pathlib.Path().absolute()}/image/profile/car_background.png')
#     car = Image.open(f'{pathlib.Path().absolute()}/image/cars/{car_id}.png')


async def generate_gun_image(gun_id: int):
    gun = Image.open(f'{pathlib.Path().absolute()}/image/gun_war/{gun_id}.png')
    background = Image.open(f'{pathlib.Path().absolute()}/image/profile/gn_background.png')
    gun = gun.resize((101, 93), Image.ANTIALIAS)
    background.paste(gun, (35, 14), gun)
    return background


async def generate_profile_user(db_session, user, house):
    if user.custom_image:
        try:
            profile = Image.open(f'{pathlib.Path().absolute()}/image/profile/profile_{user.telegram_id}_photo.png')
        except FileNotFoundError:
            profile = Image.open(f'{pathlib.Path().absolute()}/image/profile/18_house.png')
    else:
        profile = Image.open(f'{pathlib.Path().absolute()}/image/profile/{user.house}.png')
    profile = profile.resize((800, 499), Image.ANTIALIAS)
    info = Image.open(f'{pathlib.Path().absolute()}/image/profile/info.png')
    profile.paste(info, info)
    draw_image = ImageDraw.Draw(profile)
    font = ImageFont.truetype(f'{pathlib.Path().absolute()}/image/font.otf', size=17)
    business_profit = await get_user_business_profit(db_session, user)

    await health_generate(user.health, draw_image, 'health')
    await health_generate(user.luck, draw_image, 'luck')
    await health_generate(user.eat, draw_image, 'eat')

    if user.gun_war > 1:
        gun_image = await generate_gun_image(user.gun_war)
        profile.paste(gun_image, (357, 394), gun_image)

    # Вставка текста на картинку
    draw_image.text(
        (117, 47),
        user.name,
        font=font,
        fill=('#000000')
    )
    draw_image.text(
        (152, 75),
        f'{user.lvl} | exp: {user.exp} / {(user.lvl + 1) * 50 if user.lvl != 0 else 50}',
        font=font,
        fill=('#000000')
    )
    draw_image.text(
        (147, 104),
        f'{user.rating}',
        font=font,
        fill=('#000000')
    )
    draw_image.text(
        (131, 182),
        f"{convert_stats(money=user.money)}",
        font=font,
        fill=('#000000')
    )
    draw_image.text(
        (152, 212),
        f"{convert_stats(money=user.bottle)}",
        font=font,
        fill=('#000000')
    )
    draw_image.text(
        (152, 242),
        f'{convert_stats(money=business_profit.get("money"))} руб. • {convert_stats(money=business_profit.get("bottle"))} бут. в чаc',
        font=font,
        fill=('#000000')
    )
    draw_image.text(
        (178, 296),
        f'{house.name}',
        font=font,
        fill=('#000000')
    )
    draw_image.text(
        (178, 327),
        f'{user.bomj}',
        font=font,
        fill=('#000000')
    )
    try:
        user_photo = Image.open(f'{pathlib.Path().absolute()}/image/profile/{user.telegram_id}_image.png')
        user_photo = user_photo.resize((70, 70), Image.ANTIALIAS)
        profile.paste(user_photo, (713, 27))
        pathlib.Path(f'{pathlib.Path().absolute()}/image/profile/{user.telegram_id}_image.png').unlink()
    except:
        pass
    if user.vip:
        vip = Image.open(f'{pathlib.Path().absolute()}/image/profile/vip.png')
        vip_font = ImageFont.truetype(f'{pathlib.Path().absolute()}/image/font.otf', size=16)
        # text = f'{user.vip_count} дн'
        # (width, height) = vip.size
        # draw_vip = ImageDraw.Draw(vip)
        # w, h = draw_vip.textsize(text, font=font)
        # draw_vip.text((((width - w) / 2) + 2, 40),
        #                 text=text,
        #                 fill='black',
        #                 font=vip_font)
        profile.paste(vip, (621, 27), vip)
    await generate_bomj_image(db_session, user)
    bomj_img = Image.open(f'{pathlib.Path().absolute()}/image/profile/{user.telegram_id}_bomj.png')
    profile.paste(bomj_img, (620, 138), bomj_img)
    profile.save(f'{pathlib.Path().absolute()}/image/profile/{user.telegram_id}_profile.png')
