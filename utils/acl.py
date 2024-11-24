import json
import discord
from discord.ext import commands
from typing import List


with open("acl.json") as f:
    acl = json.load(f)


def have_role(user: discord.Member, roles: List[int]) -> bool:
    return any([user.get_role(role) for role in roles])


class ACL:
    def __init__(self, bot: commands.Bot = None):
        if bot:
            self.guilds = [bot.get_guild(guild) for guild in acl["guilds"]]
        else:
            self.guilds = [discord.Object(guild) for guild in acl["guilds"]]
        self.guild_ids = acl["guilds"]


    def log_model(self, name: str, *, default: str = "default") -> str:
        return acl["logs"].get(name, default)


    def is_console(self, interaction: discord.Interaction) -> bool:
        """ Determine if the user is an console. """
        return interaction.user.id in acl["users"]["consoles"] or have_role(interaction.user, acl["roles"]["consoles"])

    
    def is_admin(self, interaction: discord.Interaction) -> bool:
        """ Determine if the user is an admin. """
        return self.is_console(interaction) or interaction.user.id in acl["users"]["admins"] or have_role(interaction.user, acl["roles"]["admins"])

    
    def is_supporter(self, interaction: discord.Interaction) -> bool:
        """ Determine if the user is an supporter. """
        return self.is_admin(interaction) or interaction.user.id in acl["users"]["supporters"] or have_role(interaction.user, acl["roles"]["supporters"])