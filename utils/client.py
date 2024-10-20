import discord, os
from discord.ext import commands
import json
import aiosqlite
from .logs import send_log
from .database import SQLite
from .acl import ACL


class DiscordBot(commands.Bot):
    def __init__(self, command_prefix, intents, *, debug: bool = False):
        """ Maintain class """
        super().__init__(command_prefix, intents=intents)
        self.db = None
        self.debug = debug
        with open("config.json") as f:
            self.config = json.load(f)
        self.acl = ACL(self.config["acl"])
    

    async def start(self, *args, **kwargs):
        """ Start database connection when bot run """
        self.db = await SQLite(self.bot)
        if self.db:
            await send_log("success", "**Database** successfully connected.")
        await super().start(*args, **kwargs)


    async def setup_hook(self):
        """ Load all extensions """
        for filename in os.listdir("./cogs"):
            if filename.endswith(".py"):
                await self.load_extension(f"cogs.{filename[:-3]}")
                await send_log("info", f"Cog **{filename[:-3]}** successfully loaded.")


    async def on_ready(self):
        """ Run when bot is ready """
        await send_log("info", "Bot is **Up** and **Ready**!")

        try:
            synced = await self.tree.sync()
            for sync in synced:
                await send_log("success", "Command `%s` synced." % sync.name)
            await send_log("info", f"Synced `{len(synced)}` command(s)")
        except Exception as e:
            await send_log("error", e)

    
    async def on_command_error(self, context: commands.Context, exception: commands.CommandError):
        await context.reply(f"Use slash `(/)` commands.\n- Error: `{exception}`")
        await send_log("error", f"**Command Error** - `@{context.author.name}#{context.author.discriminator} ({context.author.id})` Error: `{exception}`")
        if self.debug:
            return await super().on_error()


    async def on_error(self, event: str, *args, **kwargs):
        await send_log("error", f"**Error** - Error: `{event}` Args: `{args}` Kwargs: `{kwargs}`")
        if self.debug:
            return await super().on_error()


    async def close(self):
        """ Close database when bot is down """
        if self.db is not None:
            await self.db.close()
            await send_log("success", "**Database** successfully disconnected!")
        await super().close()