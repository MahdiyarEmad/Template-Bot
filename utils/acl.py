import json
import discord
from discord.ext import commands
from typing import List, Union


with open("acl.json") as f:
    acl = json.load(f)


def have_role(user: discord.Member, roles: List[int]) -> bool:
    if not isinstance(user, discord.Member):
        return False

    return any([user.get_role(role) for role in roles])


class ACL:
    def __init__(self, bot: commands.Bot = None):
        if bot:
            self.guilds = [bot.get_guild(guild) for guild in acl["guilds"]]
        else:
            self.guilds = [discord.Object(guild) for guild in acl["guilds"]]
        self.guild_ids = acl["guilds"]


    def log_model(self, name: str, *, default: str = "default") -> str:
        """ Log model was returned. """
        return acl["logs"].get(name, default)


    def is_guild(self, target: Union[discord.Interaction, discord.Guild, commands.Context, discord.Member]) -> bool:
        """ Determine if the user is in the guild. """
        if isinstance(target, discord.Interaction):
            return target.guild_id in self.guild_ids
        elif isinstance(target, discord.Member):
            return target.guild.id in self.guild_ids
        elif isinstance(target, discord.Guild):
            return target.id in self.guild_ids
        elif isinstance(target, commands.Context):
            return target.guild.id in self.guild_ids


    def is_console(self, target: Union[discord.Interaction, discord.User, commands.Context, discord.Member]) -> bool:
        """ Determine if the user is an console. """
        if isinstance(target, discord.Interaction):
            return target.user.id in acl["users"]["consoles"] or have_role(target.user, acl["roles"]["consoles"])
        elif isinstance(target, discord.User) or isinstance(target, discord.Member):
            return target.id in acl["users"]["consoles"] or have_role(target, acl["roles"]["consoles"])
        elif isinstance(target, commands.Context):
            return target.author.id in acl["users"]["consoles"] or have_role(target.author, acl["roles"]["consoles"])

    
    def is_admin(self, target: Union[discord.Interaction, discord.User, commands.Context, discord.Member]) -> bool:
        """ Determine if the user is an admin. """
        if isinstance(target, discord.Interaction):
            return self.is_console(target) or target.user.id in acl["users"]["admins"] or have_role(target.user, acl["roles"]["admins"])
        elif isinstance(target, discord.User) or isinstance(target, discord.Member):
            return self.is_console(target) or target.id in acl["users"]["admins"] or have_role(target, acl["roles"]["admins"])
        elif isinstance(target, commands.Context):
            return self.is_console(target) or target.author.id in acl["users"]["admins"] or have_role(target.author, acl["roles"]["admins"])

    
    def is_supporter(self, target: Union[discord.Interaction, discord.User, commands.Context, discord.Member]) -> bool:
        """ Determine if the user is an supporter. """
        if isinstance(target, discord.Interaction):
            return self.is_admin(target) or target.user.id in acl["users"]["supporters"] or have_role(target.user, acl["roles"]["supporters"])
        elif isinstance(target, discord.User) or isinstance(target, discord.Member):
            return self.is_admin(target) or target.id in acl["users"]["supporters"] or have_role(target, acl["roles"]["supporters"])
        elif isinstance(target, commands.Context):
            return self.is_admin(target) or target.author.id in acl["users"]["supporters"] or have_role(target.author, acl["roles"]["supporters"])