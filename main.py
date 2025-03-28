import discord
import ezcord
import os
from dotenv import load_dotenv

# Set up
load_dotenv()
intents = discord.Intents.default()
intents.messages = True
intents.polls = True
bot = ezcord.Bot(intents=intents, debug_guilds=[1145030840401793104])

if __name__ == '__main__':
    bot.load_cogs('cogs')
    bot.run(os.getenv('TOKEN'))