import discord
import os
from dotenv import load_dotenv

# Set up
load_dotenv()
intents = discord.Intents.default()
intents.messages = True
intents.polls = True
bot = discord.Bot(intents=intents, debug_guilds=[1145030840401793104])


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')



if __name__ == '__main__':
    for file in os.listdir('cogs'):
        if file.endswith('.py'):
            bot.load_extension(f'cogs.{file[:-3]}')

    bot.run(os.getenv('TOKEN'))