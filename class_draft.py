import discord
from datetime import datetime
from discord.ext import commands
from apscheduler.schedulers.background import BackgroundScheduler

class bot:
    def __init__(self, prefix, intents) -> None:
        self.bot = commands.Bot(command_prefix=prefix, intents=intents)
        # global variables here
        # database here

    def add_schedule(self, job) -> None:
        scheduler = BackgroundScheduler(timezone="Asia/Seoul")
        scheduler.add_job(job, "interval", seconds=5, id="hello_test")
        scheduler.start()

    def run(self,token) -> None:
        self.bot.run(token)

    def initialize(self):
        @self.bot.event
        async def on_ready():
            print(f'{self.bot.user.name} connected')
            await self.bot.change_presence(activity=discord.Game("Study Bot"), status=discord.Status.online)

        @self.bot.command()
        async def hello(ctx):
            await ctx.send('hell0')

intents = discord.Intents.default()
intents.members = True
intents.guilds = True
intents.presences = True

def task_hello():
    print('hello')

discord_bot = bot('!', intents)
discord_bot.add_schedule(task_hello)
discord_bot.initialize()
discord_bot.run(TOKEN)