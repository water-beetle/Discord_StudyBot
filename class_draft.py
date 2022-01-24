import discord
from datetime import datetime
from discord.ext import commands
from apscheduler.schedulers.background import BackgroundScheduler

class StudyBot(commands.Bot):
    def __init__(self, prefix, intents) -> None:
        super().__init__(command_prefix=prefix, intents=intents)
        # global variables here
        # database here

    def add_schedule(self, job) -> None:
        scheduler = BackgroundScheduler(timezone="Asia/Seoul")
        scheduler.add_job(job, "interval", seconds=5, id="hello_test")
        scheduler.start()

    def run(self,token) -> None:
        super().run(token)

    def initialize(self):
        @self.event
        async def on_ready():
            print(f'{self.user.name} connected')
            await self.change_presence(activity=discord.Game("Study Bot"), status=discord.Status.online)

        @self.command()
        async def name(ctx):
            await ctx.send('hell0')

intents = discord.Intents.default()
intents.members = True
intents.guilds = True
intents.presences = True

def task_hello():
    print('hello')

discord_bot = StudyBot('!', intents)
discord_bot.add_schedule(task_hello)
discord_bot.initialize()
discord_bot.run(TOKEN)