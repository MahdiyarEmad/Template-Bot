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
            await self.send_log("info", f"Synced `{len(synced)}` command(s)")
        except Exception as e:
            await self.send_log("error", e)


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
        payload = {"content": f"**[{type.capitalize()}]** <t:{round(time.time())}:f> {message}"}
        
        async with aiohttp.ClientSession() as session:
            try:
                await session.post(self.config["webhooks"][model], json=payload)
            except Exception as e:
                print(e)
                return False
            else:
                return True

        
intents = discord.Intents.all()
bot = DiscordBot("!", intents)

if __name__ == "__main__":
    bot.run(bot.config["token"])