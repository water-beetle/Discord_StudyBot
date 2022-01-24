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
        guild_id = 0

        # database here
        self.db = database.DBupdater()

        # constant variable
        self.ATTEND_TIME = '09:00'


    def add_schedule(self) -> None:
        self.scheduler = AsyncIOScheduler(timezone="Asia/Seoul")
        self.scheduler.add_job(bot_commands.daily_save, "interval", args=[self], minutes=1, id="daily_save")
        self.scheduler.start()

    def run(self, token) -> None:
        super().run(token)

    # Daily reset task for apscheduler
    async def daily_save(self):
        # 초기화 전 !종료 하지 않은 사용자 있는지 확인 후 처리
        channel = self.get_channel(931431787706597379)
        await channel.send(
            "일일 서버 데이터 저장 및 초기화 작업을 수행할게요!\n"
            "데이터 저장을 위해 !공부 중인 사용자님들을 종료할게요!\n"
            "작업이 완료된 후 다시 <!출석> 후 <!공부>해주세요!"
        )
        for user in self.today_study:
            if len(self.today_study[user]) % 2 == 1:  # !공부 중인 경우
                await channel.send(f"{user} 님이 공부하고 계시네요!")
                self.today_study[user].append(datetime.datetime.now())
                for i in range(0, len(self.today_study[user]), 2):
                    start_time = self.today_study[user][i]
                    end_time = self.today_study[user][i + 1]
                    print(start_time, end_time)
                    self.today_study_time[user] += end_time - start_time

                await channel.send(
                    f"[{user}] - 공부 끝!\n:alarm_clock:  {self.today_study[user][0].strftime('%H:%M:%S')} ~ "
                    f"{datetime.datetime.now().strftime('%H:%M:%S')}")
                # 오늘 처음 공부 종료를 할 경우
                if self.db.is_admit_today(user, datetime.date.today()):
                    self.db.update_3(user, self.today_study_time[user])
                # db에서 오늘 공부한 시간을 가져옴
                else:
                    self.db.update_4(user, self.db.get_info(user) + self.today_study_time[user])

                # db의 total_study_time 업데이트
                self.db.update_5(user, self.today_study_time[user])

                await channel.send(
                    f':book: 공부 시간 : {strfdelta(self.today_study_time[user], "{hours}시간{minutes}분{seconds}초")}\n'
                    f':coffee: 휴식 시간 : {strfdelta(self.today_rest_time[user], "{hours}시간{minutes}분{seconds}초")}')
                self.today_rest_time[user] = datetime.timedelta()

                # 다음 공부를 위한 변수 초기화
                self.today_study_time[user] = datetime.timedelta()
                self.today_rest_time[user] = datetime.timedelta()
                self.today_study[user] = []

        # today_attend 변수 초기화
        self.today_attend = []
        self.embed = discord.Embed(title="출석정보", colour=discord.Colour.purple())
        print('Reset today_attend')

        # 주간 초기화 코드 - attend_info table's total_study_time
        # "UPDATE attend_info SET total_study_time='00:00:00';"
        now_for_reset = datetime.datetime.now().date().strftime("%A")
        if now_for_reset == 'Monday':
            guild = self.get_guild(931431787203284992)
            for user in guild.members:
                if not self.db.is_admit(user.name):
                    self.db.reset_total_study_time(user.name)

        await channel.send("일간 데이터 저장 및 초기화가 완료되었어요!")

    def initialize(self):
        @self.event
        async def on_ready():
            print(f'{self.user.name} connected')
            await self.change_presence(activity=discord.Game("Study Bot"), status=discord.Status.online)

        # auto_save & get guild_id feature
        @self.event
        async def on_member_update(before, after):
            global guild_id
            guild_id = after.guild.id
            print(guild_id)

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
