import discord, json, requests, time, aiosqlite, os
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
            self.send_log("success", "**Database** successfully connected.", "console")
        await super().start(*args, **kwargs)


    async def setup_hook(self):
        """ Load all extensions """
        for filename in os.listdir("./cogs"):
            if filename.endswith(".py"):
                await bot.load_extension(f"cogs.{filename[:-3]}")


    async def on_ready(self):
        """ Run when bot is ready """
        self.send_log("success", "Bot is **Up** and **Ready**!")

        try:
            synced = await self.tree.sync()
            self.send_log("success", f"Synced `{len(synced)}` command(s)")
        except Exception as e:
            self.send_log("error", e)


    async def close(self):
        """ Close database when bot is down """
        if self.db is not None:
            await self.db.close()
            self.send_log("warning", "**Database** successfully disconnected!")
        await super().close()


    def send_log(self, type: str, message: str, model: str = "default"):
        """ Advance logging system """
        if type not in ["success", "error", "info", "warning"]:
            type = "unknown"
        if model not in self.config["webhooks"]:
            model = "default"

        text = message.replace("*", "").replace("`", "")
        print(f"[{type.capitalize()}] {text}")
        payload = {"content": f"**[{type.capitalize()}]** <t:{round(time.time())}:f> {message}"}
        try:
            requests.post(self.config["log_webhooks"][model], json=payload)
        except Exception:
            return False
        else:
            return True
        
intents = discord.Intents.all()
bot = DiscordBot("!", intents)

if __name__ == "__main__":
    bot.run(bot.config["token"])