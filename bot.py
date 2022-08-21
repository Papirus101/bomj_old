import asyncio
import logging
import os

from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand
from aiogram.types.bot_command_scope import BotCommandScopeDefault

from aiogram.contrib.fsm_storage.memory import MemoryStorage

from handlers.ChatFunc import register_chat_func_handlers
from handlers.banda.banda import register_banda_handlers
from handlers.banda.gum import register_gum_handlers
from handlers.bottle.change_bottle import register_change_bottle_handler
from handlers.bottle.collect_bottle import register_collect_bottle_handler
from handlers.business.business_store import register_business_store_nandler
from handlers.donat import register_donat_handler
from handlers.fishing.fishing import register_fishing_handlers
from handlers.fishing.fishing_store import register_fishing_store_handlers
from handlers.fishing.main_fishing import register_main_fishing_handlers
from handlers.gun_war_shop import register_shop_gun_war_handlers
from handlers.houses import register_house_store_handler
from handlers.keys import register_private_keys_handler
from handlers.referral import register_referral_handlers
from handlers.settings import register_settings_handler
from handlers.top_users import register_top_users_handler
from handlers.workers import register_workers_handler
from handlers.works.ConductorWork import register_conductor_work_handler
from handlers.works.DvorWork import register_work_dvor_handler
from handlers.works.OrderPickerWork import register_order_picker_work_handler
from handlers.works.SecurityWork import register_security_work_handler
from handlers.works.SortTrashWork import register_sort_rash_work_handler
from handlers.works.WorkPort import register_port_work
from handlers.works.works_main import register_works_main_handler
from middleware.middleware import UserActiveMiddleware
from misc.schedule_functions import business_add_money, check_vip, banda_event_finish, fishing_event_finish
from misc.services import scheduler

from db.session import engine, async_sessionmaker
from db.base import Base

from handlers.needs import register_needs_handlers
from handlers.start import register_start_handler
from updatesworker import get_handled_updates_list

from misc.user_misc import check_online_user


async def set_bot_commands(bot: Bot):
    commands = [
        BotCommand(command="start", description="Начать/Восставновить меню"),
        BotCommand(command="id", description="Узнать свой ID"),
        BotCommand(command='online', description='Общая информация'),
        BotCommand(command='my_online', description='Моя статистика')
    ]
    await bot.set_my_commands(commands, scope=BotCommandScopeDefault())


async def main():
    logging.basicConfig(
        level=logging.WARNING,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    bot = Bot(os.getenv('BOT_TOKEN'), parse_mode="HTML")
    bot["db"] = async_sessionmaker
    storage = MemoryStorage()
    dp = Dispatcher(bot, storage=storage)
    dp.middleware.setup(UserActiveMiddleware())

    scheduler.start()
    scheduler.add_job(check_online_user, 'interval', minutes=3, args=(async_sessionmaker, bot,))
    scheduler.add_job(business_add_money, 'cron', hour='*', args=(bot,))
    scheduler.add_job(check_vip, 'interval', minutes=1, args=(bot,))
    scheduler.add_job(banda_event_finish, 'cron', day_of_week=0, hour=12, args=(bot,))
    scheduler.add_job(fishing_event_finish, 'cron', day_of_week=0, hour=8, args=(bot,))
    scheduler.add_job(fishing_event_finish, 'cron', day_of_week=2, hour=8, args=(bot,))
    scheduler.add_job(fishing_event_finish, 'cron', day_of_week=4, hour=8, args=(bot,))
    # scheduler.add_job(banda_event_finish, 'interval', minutes=1, args=(bot,))

    # REGISTER ALL HANDLERES
    register_start_handler(dp)
    # ------------ Потребности ------------#
    register_needs_handlers(dp)
    # ------------ Магазин жилья ------------#
    register_house_store_handler(dp)
    # ------------ Найм работников ------------#
    register_workers_handler(dp)
    # ------------ Магазин оружия для махчаей ------------#
    register_shop_gun_war_handlers(dp)
    register_private_keys_handler(dp)
    register_referral_handlers(dp)
    register_settings_handler(dp)
    register_top_users_handler(dp)
    register_works_main_handler(dp)
    # ------------ РАБОТЫ ------------#
    register_port_work(dp)
    register_work_dvor_handler(dp)
    register_security_work_handler(dp)
    register_sort_rash_work_handler(dp)
    register_conductor_work_handler(dp)
    register_order_picker_work_handler(dp)
    # ------------ ОПЕРАЦИИ С БУТЫЛКАМИ ------------#
    register_change_bottle_handler(dp)
    register_collect_bottle_handler(dp)
    # ------------ БИЗНЕСЫ -------------- #
    register_business_store_nandler(dp)
    # ------------ РЫБАЛКА ГЛАВНАЯ -------------- #
    register_main_fishing_handlers(dp)
    # ------------ РЫБАЛКА --------------- #
    register_fishing_handlers(dp)
    # ------------ МАГАЗИН РЫБАЛКИ --------------- #
    register_fishing_store_handlers(dp)
    # ------------ БАНДА --------------- #
    register_banda_handlers(dp)
    # ------------ КАЧАЛКА --------------- #
    register_gum_handlers(dp)
    register_chat_func_handlers(dp)

    register_donat_handler(dp)

    await set_bot_commands(bot)

    try:
        await dp.start_polling(allowed_updates=get_handled_updates_list(dp))
    finally:
        await dp.storage.close()
        await dp.storage.wait_closed()
        await bot.session.close()


try:
    asyncio.run(main())
except (RuntimeError, KeyboardInterrupt, SystemExit):
    logging.error("Bot stopped!")
