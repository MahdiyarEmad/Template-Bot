import discord
from discord.ext import commands



class GroupCogSystem(commands.GroupCog, name="example"):
    def __init__(self, bot: commands.Bot):
        super().__init__()
        self.bot = bot



async def setup(bot):
    bot.send_log("success", "**Example System** successfully loaded.", "console")
    await bot.add_cog(GroupCogSystem(bot))