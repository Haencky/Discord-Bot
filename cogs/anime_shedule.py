from discord.ext import commands, tasks
from discord.ext.pages import Page, Paginator
from discord import Embed, Colour, File
from discord.commands import slash_command, context
import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime, timezone, timedelta, time

class AnimeShedule(commands.Cog):
    """
    Cog for Anime Shedule
    """
    def __init__(self, bot):
        self.bot = bot
        self.df = pd.DataFrame() # dataframe for the shedule

    @commands.Cog.listener()
    async def on_ready(self):
         """
         Start loop on ready and fetch once
         """
         self.fetch_anime_shedule.start() # staert the loop
         self.df = scrape() # scrape once, to ensure the df is not empty (if time is already passed)

    @tasks.loop(time=time(hour=0, minute=0,tzinfo=timezone.utc))
    async def fetch_anime_shedule(self):
        """
        Fetch the Anime shedule every week
        """
        if datetime.today().weekday() == 6: # if sunday fetch data
            self.df  = scrape()
        else:
             pass
    
def setup(bot):
    bot.add_cog(AnimeShedule(bot))


def scrape() -> pd.DataFrame:
        """"
        Scrape the Internet for next weeks Anime shedule
        """
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
        print(f"{today}: Scraped {len(df)} entries")
        return df