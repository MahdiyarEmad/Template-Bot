import discord, utils

PREFIX = "!"
INTENTS = discord.Intents.all()
DEBUG_MODE = False

bot = utils.DiscordBot(PREFIX, INTENTS, debug=DEBUG_MODE)

if __name__ == "__main__":
    bot.run(bot.config["token"])
