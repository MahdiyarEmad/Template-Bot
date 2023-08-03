import discord
from discord.ext import commands



class ExampleSystem(commands.Cog):
    def __init__(self, bot: commands.Bot):
        super().__init__()
        self.bot = bot



async def setup(bot):
    bot.send_log("success", "**Example System** successfully loaded.", "console")
    await bot.add_cog(ExampleSystem(bot))