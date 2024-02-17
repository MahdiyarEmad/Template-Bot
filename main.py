import discord, json, time, aiosqlite, os, aiohttp
from discord.ext import commands


class DiscordBot(commands.Bot):
    def __init__(self, command_prefix, intents):
        """ Maintain class """
        super().__init__(command_prefix, intents=intents)
        self.db = None
        with open("config.json") as f:
            self.config = json.load(f)


    def embed(self, *args, **kwargs):
        """ Return a embed with custom embed """
        embed = discord.Embed(*args, **kwargs)
        embed.set_footer(text=self.config["footer"]["text"], icon_url=self.config["footer"]["icon"])
        return embed


    async def start(self, *args, **kwargs):
        """ Start database connection when bot run """
        self.db = await aiosqlite.connect(self.config["database"])
        if self.db:
            await self.send_log("success", "**Database** successfully connected.")
        await super().start(*args, **kwargs)


    async def setup_hook(self):
        """ Load all extensions """
        for filename in os.listdir("./cogs"):
            if filename.endswith(".py"):
                await bot.load_extension(f"cogs.{filename[:-3]}")
                await self.send_log("info", f"Cog **{filename[:-3]}** successfully loaded.")


    async def on_ready(self):
        """ Run when bot is ready """
        await self.send_log("info", "Bot is **Up** and **Ready**!")

        try:
            synced = await self.tree.sync()
            for sync in synced:
                await self.send_log("success", "Command `%s` synced." % sync.name)
            await self.send_log("info", f"Synced `{len(synced)}` command(s)")
        except Exception as e:
            await self.send_log("error", e)

    
    async def on_command_error(self, context: commands.Context, exception: commands.CommandError):
        await context.reply(f"This command has error.\n- Error: `{exception}`")
        await self.send_log("error", f"**Command Error** - `@{context.author.name}#{context.author.discriminator} ({context.author.id})` Error: `{exception}`")


    async def on_error(self, event: str, *args, **kwargs):
        await self.send_log("error", f"**Error** - Error: `{event}`")


    async def close(self):
        """ Close database when bot is down """
        if self.db is not None:
            await self.db.close()
            await self.send_log("success", "**Database** successfully disconnected!")
        await super().close()


    async def send_log(self, type: str, message: str, model: str = "default"):
        """ Advance logging system """
        if type not in ["success", "error", "info", "warning"]:
            raise ValueError("The entered type unknown enter valid type")
        if model not in self.config["webhooks"]:
            raise ValueError("The entered model unknown enter valid model")

        text = message.replace("*", "").replace("`", "")
        print(f"[{type.capitalize()}] {text}")

        async with aiohttp.ClientSession() as session:
            webhook = discord.Webhook.from_url(self.config["webhooks"].get(model), session=session)
            await webhook.send(f"**[{type.capitalize()}]** <t:{round(time.time())}:f> {message}")\
    

        
intents = discord.Intents.all()
bot = DiscordBot("!", intents)

if __name__ == "__main__":
    bot.run(bot.config["token"])