import discord, utils, json, os, aiohttp
from logging import Logger, INFO
import logging
import time
from discord.ext import commands


INTENTS = discord.Intents.all()
DEBUG_MODE = False


class DiscordBot(commands.Bot):
    appinfo: discord.AppInfo
    db: utils.DataSQL
    acl: utils.ACL
    logger: Logger

    def __init__(self, intents, *, debug: bool = False):
        """ Maintain class """
        with open("config.json") as f:
            self.config = json.load(f)
        super().__init__(commands.when_mentioned_or(*self.config["prefixes"]), intents=intents)
        self.debug = debug
        self.acl = utils.ACL()
    

    def _level_type(self, level: int) -> str:
        if level == logging.DEBUG:
            return "debug"
        elif level == logging.INFO:
            return "info"
        elif level == logging.WARNING:
            return "warning"
        elif level == logging.ERROR:
            return "error"
        elif level == logging.CRITICAL:
            return "critical"
        else:
            return "notset"


    async def _send_log(self, level: int, message: str, model: str = "default", *, limit: int = 2000):
        """ Advance logging system """
        webhooks = self.config["webhooks"]
        if model not in webhooks:
            model = "default"

        type = self._level_type(level)
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
        self.loop.create_task(self._send_log(level, message, name))


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
                self.log(f"Cog **{filename[:-3]}** successfully loaded.", "discord.setup_hook")


    async def on_ready(self):
        """ Run when bot is ready """
        self.log("Bot is **Up** and **Ready**!", "discord.on_ready")

        try:
            for guild in self.acl.guilds:
                await self.tree.sync(guild=guild)
            synced = await self.tree.sync()
            for sync in synced:
                self.log("Command `%s` synced." % sync.name, "discord.on_ready")
            self.log(f"Synced **{len(synced)}** command(s)", "discord.on_ready")
        except Exception as e:
            self.log(str(e), "discord.on_ready", logging.ERROR)


    async def on_error(self, event: str, *args, **kwargs):
        self.log(f"Error: `{event}` Args: `{args}` Kwargs: `{kwargs}`", "discord.error", logging.ERROR)
        if self.debug:
            return await super().on_error()


    async def close(self):
        """ Close database when bot is down """
        if self.config["database"] == "mysql":
            await self.db.close()
            self.log("**Database** successfully disconnected!", "discord.close")
        self.log("**Bot** is **Shutting down** successfully!", "discord.close")
        await super().close()


bot = DiscordBot(INTENTS, debug=DEBUG_MODE)

if __name__ == "__main__":
    file_level = logging.INFO
    console_level = logging.INFO

    if DEBUG_MODE:
        file_level = logging.DEBUG

    bot.logger, stream_handler = utils.set_logging(file_level, console_level)
    bot.run(bot.config["token"], log_handler=stream_handler, log_level=logging.DEBUG)
