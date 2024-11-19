import discord, utils, json, os
from logging import Logger, INFO
import logging
from discord.ext import commands

PREFIXES = ["!"]
INTENTS = discord.Intents.all()
DEBUG_MODE = False

class DiscordBot(commands.Bot):
    appinfo: discord.AppInfo
    """Application info for the bot provided by Discord."""

    config: dict
    """The config loaded directly from 'config/*.json'."""

    db: utils.DataSQL
    """Represent the database connection."""

    acl: utils.ACL

    logger: Logger
    """Logging Object of the bot."""

    def __init__(self, command_prefix, intents, *, debug: bool = False):
        """ Maintain class """
        super().__init__(command_prefix, intents=intents)
        self.debug = debug
        with open("config.json") as f:
            self.config = json.load(f)
        self.acl = utils.ACL()
    

    def log(self, message: str, name: str, level: int = INFO, **kwargs) -> None:
        """ Log a message to the console and the log file. """
        self.logger.name = name
        self.logger.log(level = level, msg = message, **kwargs)


    async def start(self, *args, **kwargs):
        """ Start database connection when bot run """
        if self.config["database"] == "mysql":
            # Database initialization
            server = self.config["mysql"]
            self.db = utils.DataSQL(server["host"], server["port"], self.loop)
            await self.db.auth(server["user"], server["password"], server["database"])
            self.log(message=f"Database connection established ({server['host']}:{server['port']})", name="discord.setup_hook")
        await super().start(*args, **kwargs)


    async def setup_hook(self):
        """ Load all extensions """
        for filename in os.listdir("./cogs"):
            if filename.endswith(".py"):
                await self.load_extension(f"cogs.{filename[:-3]}")
                # await send_log("info", f"Cog **{filename[:-3]}** successfully loaded.")
                self.log(f"Cog {filename[:-3]} successfully loaded.", "discord.setup_hook")


    async def on_ready(self):
        """ Run when bot is ready """
        # await send_log("info", "Bot is **Up** and **Ready**!")
        self.log("Bot is Up and Ready.", "discord.on_ready")

        try:
            for guild in self.acl.guilds:
                await self.tree.sync(guild=guild)
            synced = await self.tree.sync()
            for sync in synced:
                self.log("Command `%s` synced." % sync.name, "discord.on_ready")
                # await send_log("success", "Command `%s` synced." % sync.name)
            self.log(f"Synced {len(synced)} command(s)", "discord.on_ready")
        except Exception as e:
            self.log(str(e), "discord.on_ready", logging.ERROR)
            # await send_log("error", e)

    
    # async def on_command_error(self, context: commands.Context, exception: commands.CommandError):
    #     await context.reply(f"Use slash `(/)` commands.\n- Error: `{exception}`")
    #     if self.debug:
    #         return await super().on_error()


    async def on_error(self, event: str, *args, **kwargs):
        self.log(f"Error: {event} Args: {args} Kwargs: {kwargs}", "discord.error", logging.ERROR)
        # await send_log("error", f"**Error** - Error: `{event}` Args: `{args}` Kwargs: `{kwargs}`")
        if self.debug:
            return await super().on_error()


    async def close(self):
        """ Close database when bot is down """
        if self.db is not None:
            await self.db.close()
            self.log("Database successfully disconnected.", "discord.close")
            # await send_log("success", "**Database** successfully disconnected!")
        await super().close()


bot = utils.DiscordBot(commands.when_mentioned_or(*PREFIXES), INTENTS, debug=DEBUG_MODE)

if __name__ == "__main__":
    bot.run(bot.config["token"])
