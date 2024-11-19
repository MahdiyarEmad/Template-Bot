import discord, utils, json, os, aiohttp, asyncio
from logging import Logger, INFO
import logging
import time
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
    

    async def __send_log(self, level: int, message: str, model: str = "default", *, limit: int = 2000):
        """ Advance logging system """
        webhooks = self.config["webhooks"]
        if model not in webhooks:
            model = "default"

        if level == logging.NOTSET:
            type = "notset"
        elif level == logging.DEBUG:
            type = "debug"
        elif level == logging.INFO:
            type = "info"
        elif level == logging.WARNING:
            type = "warning"
        elif level == logging.ERROR:
            type = "error"
        elif level == logging.CRITICAL:
            type = "critical"

        content = f"**[{type.capitalize()}]** <t:{round(time.time())}:f> {str(message)}"

        async with aiohttp.ClientSession() as session:
            webhook = discord.Webhook.from_url(webhooks.get(model), session=session)
            for slice in [(content[i:i+limit]) for i in range(0, len(content), limit)]:
                await webhook.send(slice)


    def log(self, message: str, name: str, level: int = INFO, **kwargs) -> None:
        """ Log a message to the console and the log file. """
        self.logger.name = name
        text = message.replace("*", "").replace("`", "")
        self.logger.log(level = level, msg = text, **kwargs)
        self.loop.create_task(self.__send_log(level, message, name))


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


bot = DiscordBot(commands.when_mentioned_or(*PREFIXES), INTENTS, debug=DEBUG_MODE)

if __name__ == "__main__":
    file_level = logging.INFO
    console_level = logging.INFO

    if DEBUG_MODE:
        file_level = logging.DEBUG

    bot.logger, stream_handler = utils.set_logging(file_level, console_level)
    bot.run(bot.config["token"], log_handler=stream_handler, log_level=logging.DEBUG)
