import discord, json
from discord import app_commands
from discord.ext import commands


with open("config/example.json") as f:
    config = json.load(f)



class ExampleSystem(commands.Cog):
    def __init__(self, bot: commands.Bot):
        super().__init__()
        self.bot = bot



async def setup(bot):
    await bot.add_cog(ExampleSystem(bot))