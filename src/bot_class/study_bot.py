import discord
from datetime import datetime
from discord.ext import commands
from functions import bot_commands
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from . import database
from collections import defaultdict
import datetime


def strfdelta(tdelta, fmt):
    d = {}
    d["hours"], rem = divmod(tdelta.seconds, 3600)
    d["minutes"], d["seconds"] = divmod(rem, 60)
    return fmt.format(**d)


class StudyBot(commands.Bot):
    def __init__(self, prefix) -> None:
        intents = discord.Intents.default()
        intents.messages = True
        intents.members = True
        intents.presences = True
        super().__init__(command_prefix=prefix, intents=intents)
        self.remove_command("help")

        # global variables here
        self.today_study = {}  # 오늘 공부에 참여한 인원들의 하루 공부시간 저장하는 변수 {이름 : [시작시간, 종료시간, 시작시간, 종료시간...]}
        self.today_rest_time = defaultdict(datetime.timedelta)  # 오늘 휴식한 인원들의 휴식시간 {이름 : 휴식시간}
        self.today_attend = []  # 오늘 출석 여부 변수
        self.embed = discord.Embed(title="출석정보", colour=discord.Colour.purple())  # 출석 정보 출력
        self.count = defaultdict(datetime.timedelta)  # 10분을 얼마나 쉬었는지 체크
        self.today_study_time = defaultdict(datetime.timedelta)  # 유저의 오늘 공부시간
        self.scheduler = AsyncIOScheduler(timezone="Asia/Seoul")
        self.guild_id = 0
        self.scheduler_added = False

        # database here
        self.db = database.DBupdater()

        # constant variable
        self.ATTEND_TIME = '09:00'


    # def add_schedule(self) -> None:
    #     self.scheduler = AsyncIOScheduler(timezone="Asia/Seoul")
    #     self.scheduler.add_job(bot_commands.daily_save, "interval", args=[self, self.guild_id], minutes=1, id="daily_save")
    #     self.scheduler.start()

    def run(self, token) -> None:
        super().run(token)

    def initialize(self):
        @self.event
        async def on_ready():
            print(f'{self.user.name} connected')
            await self.change_presence(activity=discord.Game("Study Bot"), status=discord.Status.online)
        
        @self.event
        async def on_guild_join(guild):
            self.guild_id = guild.id
            if self.guild_id:
                if not self.scheduler_added:
                    self.scheduler.add_job(bot_commands.daily_save, "cron", args=[self, self.guild_id], hour=4, minute=0, id="daily_save")
                    self.scheduler.start()
                    self.scheduler_added = True
            
            channel = guild.text_channels[0]
            await channel.send("도움말은 !help")

        ######################
        ### 명령어 처리 함수 ###
        ######################

        # db에 사용자 등록
        @self.command()
        async def 등록(ctx):
            await bot_commands._등록(ctx, self.db)

        # 목표시간 설정
        @self.command()
        async def 목표시간(ctx, time):
            await bot_commands._목표시간(ctx, time, self.db)

        # 출석
        @self.command()
        async def 출석(ctx):
            await bot_commands._출석(ctx, self.db, self.embed, self.today_attend, self.today_study, self.ATTEND_TIME)

        # 시작
        @self.command()
        async def 시작(ctx):
            await bot_commands._시작(ctx, self.db, self.today_attend, self.today_study)

        # 휴식
        @self.command()
        async def 휴식(ctx):
            await bot_commands._휴식(ctx, self.db, self.today_attend, self.today_study, self.count, self.today_rest_time,
                                   self)

        # today_rest_time 초기화 필요
        @self.command()
        async def 종료(ctx):
            await bot_commands._종료(ctx, self.db, self.today_attend, self.today_study, self.today_study_time, self.today_rest_time)

        # 일주일 랭킹표
        @self.command()
        async def 랭킹(ctx):
            await bot_commands._랭킹(ctx, self.db)

        # record
        @self.command()
        async def 기록(ctx):
            await bot_commands._기록(ctx)


'''


# Initialize Scheduler
scheduler = AsyncIOScheduler(timezone="Asia/Seoul")
scheduler.add_job(daily_save, "cron", hour=5, minute=0, id="daily_save")
scheduler.start()'''
