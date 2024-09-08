import discord, json, time, aiosqlite, os, aiohttp, utils
from discord.ext import commands


class DiscordBot(commands.Bot):
    def __init__(self, command_prefix, intents):
        """ Maintain class """
        super().__init__(command_prefix, intents=intents)
        self.db = None
        with open("config.json") as f:
            self.config = json.load(f)
    

    async def start(self, *args, **kwargs):
        """ Start database connection when bot run """

        self.db = await aiosqlite.connect(self.config["database"])
        if self.db:
            await utils.send_log("success", "**Database** successfully connected.")
        await super().start(*args, **kwargs)


    async def setup_hook(self):
        """ Load all extensions """
        for filename in os.listdir("./cogs"):
            if filename.endswith(".py"):
                await bot.load_extension(f"cogs.{filename[:-3]}")
                await utils.send_log("info", f"Cog **{filename[:-3]}** successfully loaded.")


    async def on_ready(self):
        """ Run when bot is ready """
        await utils.send_log("info", "Bot is **Up** and **Ready**!")

        try:
            synced = await self.tree.sync()
            for sync in synced:
                await utils.send_log("success", "Command `%s` synced." % sync.name)
            await utils.send_log("info", f"Synced `{len(synced)}` command(s)")
        except Exception as e:
            await utils.send_log("error", e)

    
    async def on_command_error(self, context: commands.Context, exception: commands.CommandError):
        await context.reply(f"Use slash `(/)` commands.\n- Error: `{exception}`")
        await utils.send_log("error", f"**Command Error** - `@{context.author.name}#{context.author.discriminator} ({context.author.id})` Error: `{exception}`")


    async def on_error(self, event: str, *args, **kwargs):
        await utils.send_log("error", f"**Error** - Error: `{event}` Args: `{args}` Kwargs: `{kwargs}`")


    async def close(self):
        """ Close database when bot is down """
        if self.db is not None:
            await self.db.close()
            await utils.send_log("success", "**Database** successfully disconnected!")
        await super().close()

        
intents = discord.Intents.all()
bot = DiscordBot("!", intents)

if __name__ == "__main__":
    bot.run(bot.config["token"])
