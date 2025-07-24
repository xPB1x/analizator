import asyncio
import os

from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart, Command
from aiogram.types import BotCommandScopeAllPrivateChats
from dotenv import find_dotenv, load_dotenv

from Bot.handlers.user_private import user_private_router
from Bot.handlers.sportorg_handlers import sportorg_router
from Bot.handlers.winorient_handlers import winorient_router
from Bot.handlers.sfr_handlers import sfr_router
from Bot.handlers.bot_cmds_list import private

load_dotenv(find_dotenv())


bot = Bot(token=os.getenv('TOKEN'))
dp = Dispatcher()

dp.include_router(user_private_router)
dp.include_router(sportorg_router)
dp.include_router(winorient_router)
dp.include_router(sfr_router)


async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await bot.set_my_commands(commands=private, scope=BotCommandScopeAllPrivateChats())
    await dp.start_polling(bot)

asyncio.run(main())