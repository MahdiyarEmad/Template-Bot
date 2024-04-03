from typing import Coroutine
import discord, json
from discord import app_commands
from discord.ext import commands


with open("config/help.json") as f:
    config = json.load(f)


class Help(commands.Cog):
    def __init__(self, bot: commands.Bot):
        super().__init__()
        self.bot = bot


    def cog_unload(self):
        with open('config/help.json', 'w') as f:
            json.dump(config, f, indent=4)

    
    @app_commands.command(name="help", description="List all available command(s)")
    async def help(self, interaction: discord.Interaction):
        command_list = self.bot.tree.get_commands()
        text = ""

        for command in command_list:
            text += "- `/%s` - %s\n" % (command.name, command.description)

        embed = discord.Embed(title="Command List", colour=discord.Colour.blurple(), description=text)
        embed.set_footer(text=config["footer"]["text"], icon_url=config["footer"]["icon_url"])
        await interaction.response.send_message(embed=embed, ephemeral=True)



async def setup(bot):
    await bot.add_cog(Help(bot))