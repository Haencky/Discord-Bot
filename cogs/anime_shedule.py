from discord.ext import commands
from discord.commands import slash_command, context
import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime

class AnimeShedule(commands.Cog):
    """
    Cog for Anime Shedule
    """
    def __init__(self, bot):
        self.bot = bot

    @slash_command(name='anime-info', description='Get the anime shedule for the week')
    async def anime_shedule(self, ctx: context.ApplicationContext):
        df  = self.scrape()
        await ctx.respond(f'Hallo {ctx.author.mention}!')
    
    def scrape(self) -> pd.DataFrame:
        today = datetime.today()
        year = today.year
        week = int(today.isocalendar().week) + 1
        days = {
            'Montag': 'timetable-column odd Monday',
            'Dienstag': 'timetable-column even Tuesday',
            'Mittwoch': 'timetable-column odd Wednesday',
            'Donnerstag': 'timetable-column even Thursday',
            'Freitag': 'timetable-column odd Friday',
            'Samstag': 'timetable-column even Saturday',
            'Sonntag': 'timetable-column odd Sunday'   
        }
        url = f'https://animeschedule.net/?year={year}&week={week}'

        d, titles, times, episode_c = [], [], [], []

        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')

        def get_day(day: str) -> list:
            day_soup = soup.find('div', {'class': f'{days[day]}'})
            for i in day_soup.find_all('div', {'class': 'timetable-column-show unaired'}):
                d.append(day)
                titles.append(i.find('h2', {'class': 'show-title-bar'}).text)
                episode_c.append(i.find('span', {'class': 'show-episode'}).text)
                times.append("".join(i.find('time', {'class': 'show-air-time'}).text.split()))
        
        for day in days.keys():
            get_day(day)

        dict_for_df = {
            'Day': d,
            'Title': titles,
            'Episode': episode_c,
            'Time': times
        }
        df = pd.DataFrame(dict_for_df)
        print(df)
        return df



def setup(bot):
    bot.add_cog(AnimeShedule(bot))