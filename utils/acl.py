import discord, json
from .client import DiscordBot


with open("acl.json") as f:
    acl = json.load(f)


class ACL:
    def __init__(self, bot: DiscordBot = None):
        if bot:
            self.guilds = [bot.get_guild(guild) for guild in acl["guilds"]]
        else:
            self.guilds = [discord.Object(guild) for guild in acl["guilds"]]
        self.guild_ids = acl["guilds"]