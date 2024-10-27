import aiosqlite
from discord.ext import commands


class SQLite:
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.db: aiosqlite.Connection = bot.db

