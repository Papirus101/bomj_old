import random
import time

from sqlalchemy.sql import func

from db.models.active import Active
from db.models.banda_db import Banda
from db.models.fish_db import Fish, FishUser, Rod

from db.models.user_db import Users
from db.models.houses_db import Houses
from db.models.guns_war_db import GunsWar

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import NoResultFound
from sqlalchemy import select, desc, update
from sqlalchemy.types import Integer
from sqlalchemy.orm.attributes import flag_modified


async def get_all_users(db_session: AsyncSession):
    async with db_session() as session:
        sql = select(Users.telegram_id)
        data = await session.execute(sql)
        data = data.all()
        return data



async def add_user(db_session: AsyncSession, user_id: int, fullname: str, username: str, referral_id: int = None,
                   vip: bool = False,
                   vip_finish: int = 0):
    name = f'User{user_id}'
    async with db_session() as session:
        await session.merge(
            Users(telegram_id=user_id, name=name, fullname=fullname, username=username, referral_id=referral_id,
                  vip=vip,
                  vip_finish=vip_finish))
        await session.commit()


async def get_user_balance(db_session: AsyncSession, user_id: int):
    async with db_session() as session:
        sql = select(Users.money, Users.bottle, Users.donat).where(Users.telegram_id == user_id)
        data = await session.execute(sql)
        return data.one()


async def get_user_profile(db_session: AsyncSession, user_id):
    async with db_session() as session:
        sql = select(Users, Houses).join(Houses, Houses.id == Users.house).where(Users.telegram_id == user_id)
        user = await session.execute(sql)
    try:
        return user.one()
    except NoResultFound:
        return None


async def get_main_user_info(db_session: AsyncSession, user_id: int):
    async with db_session() as session:
        sql = select(Users.telegram_id, Users.money, Users.bottle, Users.eat,
                     Users.health, Users.luck, Users.event_id,
                     Users.lvl, Users.exp, Users.name, Users.fullname,
                     Users.keyses, Users.donat, Users.vip, Users.info, Users.banda,
                     Users.power).where(Users.telegram_id == user_id)
        user = await session.execute(sql)
    return user.one()


async def get_user_stuff_and_main_info(db_session: AsyncSession, user_id: int):
    async with db_session() as session:
        sql = select(Users.pants, Users.shirts, Users.shoes, Users.jacket, Users.telegram_id, Users.donat_stuff,
                     Users.name, Users.power, Users.gun_war, Users.info, GunsWar.power.label('power_gun'),
                     GunsWar.name.label('name_gun')).join(
            GunsWar, GunsWar.id == Users.gun_war).where(
            Users.telegram_id == user_id)
        data = await session.execute(sql)
        data = data.one()
        return data


async def get_all_users_from_banda(db_session: AsyncSession, banda_id: int):
    async with db_session() as session:
        sql = select(
            Users.telegram_id, Users.name, Users.info,
            Banda.admin.label('banda_admin')
        ).join(
            Banda, Banda.id == Users.banda
        ).where(
            Users.banda == banda_id
        ).order_by(
            desc(Users.info['maxa_all'].astext.cast(Integer))
        )
        data = await session.execute(sql)
        data = data.all()
        return data


async def get_all_online_users_with_business(db_session: AsyncSession):
    async with db_session() as session:
        sql = select(
            Users.telegram_id, Users.info, Users.bomj, Active.active
        ).join(Active, Active.user_id == Users.telegram_id).where(
            Active.active == True, (Users.info['business'] != None) | (Users.bomj != 0)
        )
        data = await session.execute(sql)
        data = data.all()
        return data


async def get_users_with_end_vip(db_session: AsyncSession):
    async with db_session() as session:
        sql = select(Users.telegram_id, Users.vip).where(Users.vip == True, Users.vip_finish <= int(time.time()))
        data = await session.execute(sql)
        data = data.all()
        for user in data:
            await set_user_variable(db_session, user.telegram_id, 'vip', False)
        return data


async def get_top_users_maxa_event(db_session: AsyncSession):
    async with db_session() as session:
        sql = select(
            Banda.id,
            Banda.name,
            Banda.smile
        ).join(
            Users, Users.banda == Banda.id
        ).group_by(
            Banda.id
        ).order_by(
            desc(func.sum(Users.info['maxa_week'].astext.cast(Integer)))
        ).limit(3)
        bands = await session.execute(sql)
        bands = bands.all()
        users = []
        for banda in bands:
            sql = select(
                Users.telegram_id,
                Users.info,
                Users.name,
                Users.banda
            ).where(
                Users.banda == banda.id
            ).order_by(
                desc(Users.info['maxa_week'].astext.cast(Integer))
            ).limit(3)
            user = await session.execute(sql)
            user = user.all()
            users.append(user)
        return bands, users


async def get_top_users_fishing_event(db_session: AsyncSession):
    pass


async def update_user_balance(db_session: AsyncSession, user_id: int, money_type: str, operation: str,
                              amount: int, vip_active: bool = False, nalog: bool = False):
    """ Обновляет баланс пользователя """
    async with db_session() as session:
        user = await session.get(Users, user_id)
        if money_type == 'money':
            if operation == '+' and vip_active:
                user.money += amount * 2
            elif operation == '+' and nalog and not vip_active:
                user.money += amount - (amount * (13 / 100))
            elif operation == '+' and not vip_active and not nalog:
                user.money += amount
            elif operation == '-':
                if user.money - amount < 0:
                    user.money = 0
                user.money -= amount
        elif money_type == 'bottle':
            if operation == '+' and vip_active:
                user.bottle += amount * 2
            elif operation == '+' and nalog and not vip_active:
                user.bottle += amount - (amount * (13 / 100))
            elif operation == '+' and not vip_active and not nalog:
                user.bottle += amount
            elif operation == '-':
                if user.bottle - amount < 0:
                    user.bottle = 0
                user.bottle -= amount
        elif money_type == 'donat':
            if operation == '+':
                user.donat += amount
            elif operation == '-':
                if user.donat - amount < 0:
                    user.donat = 0
                user.donat -= amount
        await session.commit()
        return True


async def update_user_exp(db_session: AsyncSession, user_id: int, operation: str, amount: int,
                          vip_active: bool = False):
    """ Обновляет опыт пользователя """
    async with db_session() as session:
        return_data = False
        user = await session.get(Users, user_id)
        if operation == '+':
            if vip_active:
                user.exp += amount * 2
            else:
                user.exp += amount
        elif operation == '-':
            user.exp -= amount
        if user.exp >= (user.lvl + 1) * 50:
            user.lvl = user.exp / 50
            return_data = True
        if user.exp < user.lvl * 50 and user.lvl > 1:
            if user.exp / 50 < 1:
                return return_data
            user.lvl = user.exp / 50
        await session.commit()
        return return_data


async def update_user_keys(db_session: AsyncSession, user_id: int, operation: str, amount: int):
    """ Обновляет кол-во кейсов пользователя """
    async with db_session() as session:
        user = await session.get(Users, user_id)
        if operation == '+':
            user.keyses += amount
        elif operation == '-':
            user.keyses -= amount
        await session.commit()


async def update_needs_user(db_session, user_id: int, need_type: str, operation: str, amount: int):
    """ Обновляет потребности пользователя """
    async with db_session() as session:
        answer = False
        user = await session.get(Users, user_id)
        if user.unlim_health:
            return answer
        if operation == '+':
            setattr(user, need_type, getattr(user, need_type) + amount)
            if getattr(user, need_type) > 100:
                setattr(user, need_type, 100)
        elif operation == '-':
            setattr(user, need_type, getattr(user, need_type) - amount)
            if getattr(user, need_type) <= 15:
                answer = True
            if getattr(user, need_type) < 0:
                setattr(user, need_type, 0)
        await session.commit()
        return answer


async def update_user_house(db_session, user_id: int, house_id: int):
    """ Изменяет жильё пользователя """
    async with db_session() as session:
        user = await session.get(Users, user_id)
        user.house = house_id
        await session.commit()


async def update_workers(db_session: AsyncSession, user_id: int, operation: str, amount: int):
    """ Обновляет кол-во работников пользователя """
    async with db_session() as session:
        user = await session.get(Users, user_id)
        if operation == '+':
            user.bomj += amount
        elif operation == '-':
            user.bomj -= amount
        await session.commit()


async def get_user_info_and_gun_war(db_session: AsyncSession, user_id: int):
    """ Получает всю информацию о пользователе и его оружии для махачей """
    async with db_session() as session:
        sql = select(Users, GunsWar).join(GunsWar, GunsWar.id == Users.gun_war).where(Users.telegram_id == user_id)
        info = await session.execute(sql)
        info = info.one()
        return info


async def update_user_gun_war(db_session: AsyncSession, user_id: int, gun_war: int):
    """ Меняет оружие для махачей пользователя """
    async with db_session() as session:
        user = await session.get(Users, user_id)
        user.gun_war = gun_war
        await session.commit()


async def get_referral_user(db_session: AsyncSession, user_id: int):
    """ Получает рефералов пользователя """
    async with db_session() as session:
        sql = select(Users.name, Users.username).where(Users.referral_id == user_id)
        users = await session.execute(sql)
        users = users.all()
        return users


async def change_user_name(db_session: AsyncSession, user_id: int, new_name: str):
    """ Меняет имя пользователя в базе """
    async with db_session() as session:
        user = await session.get(Users, user_id)
        user.name = new_name
        await session.commit()


async def get_user_close_profile(db_session: AsyncSession, user_id: int):
    async with db_session() as session:
        sql = select(Users.close_profile).where(Users.telegram_id == user_id)
        user = await session.execute(sql)
        user = user.one()
        user = user[0]
        return user


async def change_close_profile_user(db_session: AsyncSession, user_id: int, close: bool):
    """ Изменяет статус профиля пользователя """
    async with db_session() as session:
        user = await session.get(Users, user_id)
        user.close_profile = close
        await session.commit()


async def get_top_with_category(db_session: AsyncSession, category: str):
    async with db_session() as session:
        sql = 'SELECT %s, name FROM users WHERE %s <> 0 ORDER BY %s DESC LIMIT 5' % (category, category, category)
        users = await session.execute(sql)
        users = users.all()
        return users


async def get_works_for_user(db_session: AsyncSession, user_id: int):
    """ Получает работы доступные пользователю """
    async with db_session() as session:
        sql = 'SELECT id, name FROM works WHERE lvl <= (SELECT lvl FROM users WHERE telegram_id=%s)' % user_id
        works = await session.execute(sql)
        return works.all()


async def get_top_works(db_session: AsyncSession, work: int):
    """ Получает топ пользователей на работе """
    async with db_session() as session:
        sql = select(Users.name, Users.info['works'][work].label('count')).where(
            Users.info['works'][work].astext.cast(Integer) != None).order_by(
            desc(Users.info['works'][work].astext.cast(Integer))).limit(5)
        data = await session.execute(sql)
        data = data.all()
        return data


async def get_top_event(db_session: AsyncSession, event: str):
    """ Получает топ пользователей в соревновании """
    async with db_session() as session:
        sql = select(
            Users.name,
            Users.info[event].label(event)
        ).where(
            Users.info[event].astext.cast(Integer) != None
        ).order_by(
            desc(Users.info[event].astext.cast(Integer))
        ).limit(5)
        data = await session.execute(sql)
        data = data.all()
        return data


async def get_count_business(db_session: AsyncSession, user_id: int):
    """ Получает кол-во бизнесов пользователя """

    async with db_session() as session:
        user = await session.get(Users, user_id)
        if user.info is None or user.info.get('business', None) is None:
            return 0
        count_business = 0
        for business in user.info.get('business').values():
            count_business += business
        return count_business


async def update_business_count(db_session: AsyncSession, user_id: int, business_id: int):
    """ Обновляет кол-во бизнесов у пользователя """
    business_id = str(business_id)

    async with db_session() as session:
        user = await session.get(Users, user_id)
        try:
            user_info = dict(user.info)
        except TypeError:
            user.info = {'business': {business_id: 1}}
            flag_modified(user, 'info')
            await session.commit()
            return
        if user_info is None:
            user_info = {'business': {business_id: 1}}
        elif user_info is not None:
            if user_info.get('business', None) is None:
                user_info['business'] = {business_id: 1}
            else:
                if user_info['business'].get(business_id, None) is None:
                    user_info['business'][business_id] = 1
                else:
                    new_count = user_info['business'][business_id] + 1
                    user_info['business'][business_id] = new_count
        user.info = user_info
        flag_modified(user, 'info')
        await session.commit()


async def update_works_count(db_session: AsyncSession, user_id: int, work: str):
    """ Обновляет кол-во отработанных дней на конкретной работе """
    async with db_session() as session:
        user = await session.get(Users, user_id)
        try:
            user_info = dict(user.info)
        except TypeError:
            user.info = {'works': {work: 1}}
            flag_modified(user, "info")
            await session.commit()
            return
        if user_info is None:
            user_info = {'works': {work: 1}}
        elif user_info is not None:
            if user_info.get('works', None) is None:
                user_info['works'] = {work: 1}
            else:
                if user_info['works'].get(work, None) is None:
                    user_info['works'][work] = 1
                else:
                    old_count = user_info['works'][work] + 1
                    user_info['works'][work] = old_count
        user.info = user_info
        flag_modified(user, "info")
        await session.commit()


async def clear_event_count(db_session: AsyncSession, event: str):
    async with db_session() as session:
        sql = select(Users.telegram_id).where(
            Users.info[event].astext.cast(Integer) != 0
        )
        data = await session.execute(sql)
        data = data.all()
        print(data)
        for user in data:
            await update_event_count(db_session, user.telegram_id, event, '~', 0)


async def get_winner_fishing_event(db_session: AsyncSession):
    async with db_session() as session:
        sql = select(Users.telegram_id, Users.name, Users.info).where(
            Users.info['fishing'].astext.cast(Integer) != 0
        ).order_by(
            desc(Users.info['fishing'].astext.cast(Integer))
        ).limit(3)
        data = await session.execute(sql)
        data = data.all()
        return data



async def update_event_count(db_session: AsyncSession, user_id: int, event: str, operation: str, amount: int):
    """ Обновляет значение пользователя в соревновании """
    async with db_session() as session:
        user = await session.get(Users, user_id)
        try:
            user_info = dict(user.info)
        except TypeError:
            user.info = {event: amount}
            flag_modified(user, "info")
            await session.commit()
            return
        if user_info is None:
            user_info = {event: amount}
        elif user_info is not None:
            if user_info.get(event, None) is None:
                user_info[event] = amount
            else:
                if operation == '+':
                    new_count = user_info[event] + amount
                elif operation == '-':
                    new_count = user_info[event] - amount
                elif operation == '~':
                    new_count = 0
                user_info[event] = new_count
        user.info = user_info
        flag_modified(user, "info")
        await session.commit()


async def update_event_id(db_session: AsyncSession, user_id: int, event_id: int):
    """ Обновляет значение евента в базе у пользователя """
    async with db_session() as session:
        user = await session.get(Users, user_id)
        user.event_id = event_id
        await session.commit()


async def check_characteristic(db_session: AsyncSession, user_id: int):
    """ Проверяет в БД значения голода, счастья и настроения """
    async with db_session() as session:
        user: Users = await session.get(Users, user_id)
        if user.health <= 15 or user.eat <= 15 or user.luck <= 15:
            return False
        return True


async def get_main_info_fishing(db_session: AsyncSession, user_id: int):
    async with db_session() as session:
        sql = select(Users.rod_detail, Users.lvl, Users.bait, Users.info, Users.event_id, Rod).join(Rod,
                                                                                         Rod.id == Users.rod).where(
            Users.telegram_id == user_id)
        data = await session.execute(sql)
        data = data.all()
        user = data[0]
        rod = data[0][-1]
        sql_fish = select(
            func.sum(Fish.price * FishUser.weigh).label('price'), func.sum(FishUser.weigh).label('weight')
        ).join(
            Fish, Fish.id == FishUser.fish
        ).where(
            FishUser.owner == user_id
        ).group_by(
            Fish.id
        )
        fishs = await session.execute(sql_fish)
        fishs = fishs.all()
        return user, rod, fishs


async def update_user_variable(db_session: AsyncSession, user_id: int, variable: str, operation: str,
                               amount: int) -> None:
    async with db_session() as session:
        user = await session.get(Users, user_id)
        if operation == '+':
            setattr(user, variable, getattr(user, variable) + amount)
        elif operation == '-':
            setattr(user, variable, getattr(user, variable) - amount)
        await session.commit()


async def set_user_variable(db_session: AsyncSession, user_id: int, variable: str, value) -> None:
    async with db_session() as session:
        user = await session.get(Users, user_id)
        setattr(user, variable, value)
        await session.commit()


async def get_user_info_main_banda(db_session: AsyncSession, user_id: int):
    async with db_session() as session:
        sql = select(Users, Banda).join(Banda, Banda.id == Users.banda).where(Users.telegram_id == user_id)
        data = await session.execute(sql)
        try:
            data = data.one()
        except NoResultFound:
            data = None
        return data


async def get_top_users_by_maxa(db_session: AsyncSession, banda_id: int):
    async with db_session() as session:
        sql = select(Users.name, Users.info).where(Users.banda == banda_id, Users.info['maxa_week'] != None).order_by(
            desc(Users.info['maxa_week'].astext.cast(Integer))).limit(3)
        data = await session.execute(sql)
        data = data.all()
        return data


async def get_random_user_for_maxa(db_session: AsyncSession, user_id: int):
    async with db_session() as session:
        sql = select(Users.name, Users.telegram_id).where(Users.telegram_id != user_id)
        data = await session.execute(sql)
        data = data.all()
        return random.choice(data)
