from PIL import Image
import pathlib
from sqlalchemy.ext.asyncio import AsyncSession

from db.queries.stuff import get_current_item


async def generate_bomj_image(db_session: AsyncSession, user, stuff_id: int = 0, stuff_type: str = None, store: bool = False,
                              garderob: bool = False):
    bomj_img = Image.open(f'{pathlib.Path().absolute()}/image/profile/bomj.png')
    if user.pants is not None and stuff_type != 'pants':
        part = Image.open(f'{pathlib.Path().absolute()}/image/stuff/{user.pants}.png')
        staff = await get_current_item(db_session, user.pants)
        bomj_img.paste(part, (int(staff.coords.split(',')[0]), int(staff.coords.split(',')[1])), part)
    if user.shoes is not None and stuff_type != 'shoes':
        part = Image.open(f'{pathlib.Path().absolute()}/image/stuff/{user.shoes}.png')
        staff = await get_current_item(db_session, user.shoes)
        bomj_img.paste(part, (int(staff.coords.split(',')[0]), int(staff.coords.split(',')[1])), part)
    if user.shirts is not None and stuff_type != 'shirts':
        part = Image.open(f'{pathlib.Path().absolute()}/image/stuff/{user.shirts}.png')
        staff = await get_current_item(db_session, user.shirts)
        bomj_img.paste(part, (int(staff.coords.split(',')[0]), int(staff.coords.split(',')[1])), part)
    if user.jacket is not None and stuff_type != 'jacket':
        part = Image.open(f'{pathlib.Path().absolute()}/image/stuff/{user.jacket}.png')
        staff = await get_current_item(db_session, user.jacket)
        bomj_img.paste(part, (int(staff.coords.split(',')[0]), int(staff.coords.split(',')[1])), part)
    if stuff_id != 0:
        part = Image.open(f'{pathlib.Path().absolute()}/image/stuff/{stuff_id}.png')
        staff = await get_current_item(db_session, stuff_id)
        bomj_img.paste(part, (int(staff.coords.split(',')[0]), int(staff.coords.split(',')[1])), part)
    if stuff_id != 0 and stuff_type == 'donat_stuff':
        bomj_img = Image.open(f'{pathlib.Path().absolute()}/image/stuff/{stuff_id}.png')
    if stuff_id == 0 and stuff_type is None and user.donat_stuff is not None:
        bomj_img = Image.open(f'{pathlib.Path().absolute()}/image/stuff/{user.donat_stuff}.png')
    if store:
        bomj_img = bomj_img.resize((234, 531), Image.ANTIALIAS)
        phone = Image.open(f'{pathlib.Path().absolute()}/image/stuff/store.png')
        phone.paste(bomj_img, (395, 139), bomj_img)
        phone.save(f'{pathlib.Path().absolute()}/image/profile/{user.telegram_id}_bomj.png')
    elif garderob:
        bomj_img = bomj_img.resize((286, 647), Image.ANTIALIAS)
        phone = Image.open(f'{pathlib.Path().absolute()}/image/stuff/garderob.png')
        phone.paste(bomj_img, (357, 41), bomj_img)
        phone.save(f'{pathlib.Path().absolute()}/image/profile/{user.telegram_id}_bomj.png')
    else:
        bomj_img.save(f'{pathlib.Path().absolute()}/image/profile/{user.telegram_id}_bomj.png')