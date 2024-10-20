import aiosqlite
from .client import DiscordBot


class SQLite:
    async def __init__(self, bot: DiscordBot):
        self.bot = bot
        self.db = await aiosqlite.connect(bot.config["database"])