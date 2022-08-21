from PIL import Image, ImageDraw, ImageFont
import pathlib

from misc.convert_money import convert_stats


async def generate_image_banda(user, banda_info, top_maxa):
    profile = Image.open(f'{pathlib.Path().absolute()}/image/banda/profile.png')
    font = ImageFont.truetype(f'{pathlib.Path().absolute()}/image/font.otf', size=25)
    draw_text = ImageDraw.Draw(profile)
    (width, height) = profile.size
    text = f'{banda_info.banda_name}'

    top_maxa_week = []
    top_maxa_coords = {0: (111, 318), 1: (111, 351), 2: (111, 384)}
    for top in top_maxa:
        count_win = top.info.get('maxa_week', 0) if top.info is not None else 0
        top_maxa_week.append({'name': top.name, 'maxa_week': count_win})
    try:
        user_maxa_week = user.info["maxa_week"]
    except (KeyError, TypeError):
        user_maxa_week = 0
    if banda_info.banda_maxa_week is not None:
        all_maxa_week = banda_info.banda_maxa_week
    else:
        all_maxa_week = 0
    maxa_week = f'{user_maxa_week}' \
                f' ~ {float("%.2f" % ((user_maxa_week / all_maxa_week) * 100)) if all_maxa_week > 0 else 0}%'

    w, h = draw_text.textsize(text, font=font)
    draw_text.text(((width - w) / 2, 35), text, fill="white", font=font)
    draw_text.text(
        (529, 106),
        f'{banda_info.count_users}',
        font=font,
        fill=('black')
    )
    draw_text.text(
        (418, 170),
        f'{banda_info.banda_maxa_all}',
        font=font,
        fill=('black')
    )
    draw_text.text(
        (567, 200),
        f'{banda_info.banda_maxa_week}',
        font=font,
        fill=('black')
    )
    draw_text.text(
        (410, 229),
        maxa_week,
        font=font,
        fill=('black')
    )
    for i, top_win in enumerate(top_maxa_week):
        draw_text.text(
            top_maxa_coords.get(i),
            f'{top_win.get("name")} {top_win.get("maxa_week")}',
            font=font,
            fill=('black')
        )
    draw_text.text(
        (304, 433),
        f'{convert_stats(money=banda_info.all_money)} | Твоя доля {float("%.2f" % ((user.money / banda_info.all_money) * 100))}%',
        font=font,
        fill=('black')
    )
    draw_text.text(
        (308, 462),
        f'{convert_stats(money=banda_info.all_bottle)} | Твоя доля {float("%.3f" % ((user.bottle / banda_info.all_bottle) * 100)) if banda_info.all_bottle > 0 else 0}%',
        font=font,
        fill=('black')
    )
    profile.save(f'{pathlib.Path().absolute()}/image/banda/{banda_info.banda_id}.png')