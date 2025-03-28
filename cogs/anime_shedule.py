from discord.ext import commands, tasks
from discord.ext.pages import Page, Paginator, PageGroup
from discord import Embed, Colour, File
from discord.commands import slash_command, context, Option
import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import timezone, timedelta, time, date

class AnimeShedule(commands.Cog):
    """
    Cog for Anime Shedule
    """
    def __init__(self, bot):
        self.bot = bot
        self.df = pd.DataFrame() # dataframe for the shedule
        self.last_scrape = None

    @commands.Cog.listener()
    async def on_ready(self):
        """
        Start loop on ready and fetch once
        """
        self.fetch_anime_shedule.start() # staert the loop
        self.df, self.last_scrape = scrape() # scrape once, to ensure the df is not empty (if time is already passed)

    @tasks.loop(time=time(hour=0, minute=0,tzinfo=timezone.utc))
    async def fetch_anime_shedule(self):
        """
        Fetch the Anime shedule every week
        """
        if date.today().weekday() == 6: # if sunday fetch data
            self.df, self.last_scrape  = scrape()
        else:
            pass
    
    @slash_command(name="list_shedule", description="List the Anime shedule for the next week")
    async def list_shedule(self, ctx: context.ApplicationContext):
        """
        List the Anime shedule for the next week
        """
        days = {
        'Montag': 1,
        'Dienstag': 2,
        'Mittwoch': 3,
        'Donnerstag': 4,
        'Freitag': 5,
        'Samstag': 6,
        'Sonntag': 7   
        }
        pagegroups = []
        for day in days:
            filtered = self.df[self.df['Day'] == day] # filtered df by day
            pages = [] # 
            embeds = [] # embeds per page
            for index, row in enumerate(filtered.itertuples()):
                embed = Embed(title=f'{row.Title} - EP: {row.Episode}', color=Colour.green())
                embeds.append(embed)
                if (index + 1) % 5 == 0 or index == len(filtered) - 1: 
                    pages.append(Page(embeds=embeds))  
                    embeds = [] # reset embeds for the next page
            pagegroups.append(PageGroup(pages=pages, label=f'{day} - {self.last_scrape + timedelta(days=days[day]-1)}'))       

        paginator = Paginator(pages=pagegroups, show_menu=True, author_check=True, show_disabled=False, menu_placeholder='Tag wählen')
        await paginator.respond(ctx.interaction)

def setup(bot):
    bot.add_cog(AnimeShedule(bot))

def scrape() -> pd.DataFrame | date:
        """
        Scrape the Internet for next weeks Anime shedule
        """
        today = date.today()
        additional_days = days_till_sunday()
        target = today + timedelta(days=(additional_days + 1)) # get the next week monday
        year = target.year
        week = int(target.isocalendar().week)
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
        return df, target

def days_till_sunday() -> int:
    """
    Get the number of days till sunday
    """
    today = date.today()
    if today.weekday() == 6: # if sunday return 7
        return 7
    else:
        return 6 - today.weekday() # return the number of days till sunday