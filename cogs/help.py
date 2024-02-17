import discord, json
from discord import app_commands
from discord.ext import commands


with open("config/help.json") as f:
    config = json.load(f)



class Help(commands.Cog):
    def __init__(self, bot: commands.Bot):
        super().__init__()
        self.bot = bot

    
    @app_commands.command(name="help", description="List all available command(s)")
    async def help(self, interaction: discord.Interaction):
        text = ""

        for group in config:
            text += "**%s**\n" % group["name"]
            for command in group["commands"]:
                text += "- `/%s` - %s\n" % (command["name"], command["description"])

        embed = discord.Embed(title="Command List", colour=discord.Colour.blurple(), description=text)
        await interaction.response.send_message(embed=embed, ephemeral=True)



async def setup(bot):
    await bot.add_cog(Help(bot))