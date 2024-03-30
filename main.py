import discord, json, time, aiosqlite, os, aiohttp
from pymongo.mongo_client import MongoClient
from discord.ext import commands


class DiscordBot(commands.Bot):
    def __init__(self, command_prefix, intents):
        """ Maintain class """
        super().__init__(command_prefix, intents=intents)
        self.db = None
        with open("test.json") as f:
            self.config = json.load(f)


    async def get_api(self, api):
        """ Helps to get api """
        async with aiohttp.ClientSession() as session:
            async with session.get(api) as response:
                try:
                    response.raise_for_status()
                except Exception:
                    return False
                else:
                    return await response.json()


    async def start(self, *args, **kwargs):
        """ Start database connection when bot run """
        # client = MongoClient(self.config["mongodb"]["uri"])
        # try:
        #     client.admin.command('ping')
        #     await self.send_log("success", "Pinged your deployment. You successfully connected to **MongoDB**!")
        #     self.mongodb = client.get_database(self.config["mongodb"]["database"])
        # except Exception as e:
        #     await self.send_log("error", f"Error: `{e}`")

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
        await context.reply(f"Use slash `(/)` commands.\n- Error: `{exception}`")
        await self.send_log("error", f"**Command Error** - `@{context.author.name}#{context.author.discriminator} ({context.author.id})` Error: `{exception}`")


    async def on_error(self, event: str, *args, **kwargs):
        await self.send_log("error", f"**Error** - Error: `{event}` Args: `{args}` Kwargs: `{kwargs}`")


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

        text = str(message).replace("*", "").replace("`", "")
        print(f"[{type.capitalize()}] {text}")

        async with aiohttp.ClientSession() as session:
            webhook = discord.Webhook.from_url(self.config["webhooks"].get(model), session=session)
            await webhook.send(f"**[{type.capitalize()}]** <t:{round(time.time())}:f> {message}")
    

        
intents = discord.Intents.all()
bot = DiscordBot("!", intents)

if __name__ == "__main__":
    bot.run(bot.config["token"])