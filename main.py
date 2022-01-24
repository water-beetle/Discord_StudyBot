# import asyncio
import discord
import datetime
# from PIL import Image
import os
# from io import BytesIO
from database_study import DBupdater
from collections import defaultdict
from discord.ext import commands
from apscheduler.schedulers.asyncio import AsyncIOScheduler
# from week_table import week_table
import bot_commands

# Token값 가져오기
# TOKEN = os.environ.get("TOKEN")
TOKEN = "OTMxNDMyMDkyNTMxODM5MDM2.YeEVvA.7rD70QR7p9dN_CDr12gImMhvTWI"

# Intents to get guild member info
intents = discord.Intents.default()
intents.members = True
intents.presences = True

app = commands.Bot(command_prefix='!', intents=intents)
db = DBupdater()

# 상수 모음
ATTEND_TIME = '09:00'

# 전역변수 모음
today_study = {}  # 오늘 공부에 참여한 인원들의 하루 공부시간 저장하는 변수 {이름 : [시작시간, 종료시간, 시작시간, 종료시간...]}
today_rest_time = defaultdict(datetime.timedelta)  # 오늘 휴식한 인원들의 휴식시간 {이름 : 휴식시간}
today_attend = []  # 오늘 출석 여부 변수
embed = discord.Embed(title="출석정보", colour=discord.Colour.purple())  # 출석 정보 출력
count = defaultdict(datetime.timedelta)  # 10분을 얼마나 쉬었는지 체크
today_study_time = defaultdict(datetime.timedelta)  # 유저의 오늘 공부시간
guild_id = 0

# Daily reset task for apscheduler
async def daily_save():
    # 초기화 전 !종료 하지 않은 사용자 있는지 확인 후 처리
    channel = app.get_channel(931431787706597379)
    await channel.send(
            "일일 서버 데이터 저장 및 초기화 작업을 수행할게요!\n"
            "데이터 저장을 위해 !공부 중인 사용자님들을 종료할게요!\n"
            "작업이 완료된 후 다시 <!출석> 후 <!공부>해주세요!"
        )
    for user in today_study:
        if len(today_study[user]) % 2 == 1: # !공부 중인 경우
            await channel.send(f"{user} 님이 공부하고 계시네요!")
            today_study[user].append(datetime.datetime.now())
            for i in range(0, len(today_study[user]), 2):
                start_time = today_study[user][i]
                end_time = today_study[user][i + 1]
                print(start_time, end_time)
                today_study_time[user] += end_time - start_time

            await channel.send(
            f"[{user}] - 공부 끝!\n:alarm_clock:  {today_study[user][0].strftime('%H:%M:%S')} ~ "
            f"{datetime.datetime.now().strftime('%H:%M:%S')}")
            # 오늘 처음 공부 종료를 할 경우
            if db.is_admit_today(user, datetime.date.today()):
                db.update_3(user, today_study_time[user])
            # db에서 오늘 공부한 시간을 가져옴
            else:
                db.update_4(user, db.get_info(user) + today_study_time[user])

            # db의 total_study_time 업데이트
            db.update_5(user, today_study_time[user])

            await channel.send(
                f':book: 공부 시간 : {strfdelta(today_study_time[user], "{hours}시간{minutes}분{seconds}초")}\n'
                f':coffee: 휴식 시간 : {strfdelta(today_rest_time[user], "{hours}시간{minutes}분{seconds}초")}')
            today_rest_time[user] = datetime.timedelta()

            #다음 공부를 위한 변수 초기화
            today_study_time[user] = datetime.timedelta()
            today_rest_time[user] = datetime.timedelta()
            today_study[user] = []
    
    # today_attend 변수 초기화
    global today_attend, embed
    today_attend = []
    embed = discord.Embed(title="출석정보", colour=discord.Colour.purple())
    print('Reset today_attend')

    # 주간 초기화 코드 - attend_info table's total_study_time
    # "UPDATE attend_info SET total_study_time='00:00:00';"
    now_for_reset = datetime.datetime.now().date().strftime("%A")
    if now_for_reset == 'Monday':
        guild = app.get_guild(931431787203284992)
        for user in guild.members:
            if not db.is_admit(user.name):
                db.reset_total_study_time(user.name)

    await channel.send("일간 데이터 저장 및 초기화가 완료되었어요!")

# Initialize Scheduler
scheduler = AsyncIOScheduler(timezone="Asia/Seoul")
scheduler.add_job(daily_save, "cron", hour=5, minute=0, id="daily_save")
scheduler.start()

# Add Custom Help Command
app.remove_command("help")


@app.group(invoke_without_command=True)
async def help(ctx):
    em = discord.Embed(title="Help", description="!help <명령어> 를 통해 더 자세한 정보를 확인해 보세요.")
    em.add_field(name="명령어", value="등록, 목표시간, 출석, 시작, 휴식, 종료")
    await ctx.send(embed=em)


@help.command()
async def 등록(ctx):
    em = discord.Embed(title="등록", description="디스코드 이름으로  사용자를 등록합니다.", color=ctx.author.color)
    em.add_field(name="사용법", value="!등록")
    await ctx.send(embed=em)


@help.command()
async def 목표시간(ctx):
    em = discord.Embed(title="목표시간", description="디스코드 이름으로  사용자를 등록합니다.", color=ctx.author.color)
    em.add_field(name="사용법", value="!등록")
    await ctx.send(embed=em)


@help.command()
async def 출석(ctx):
    em = discord.Embed(title="출석", description="디스코드 이름으로  사용자를 등록합니다.", color=ctx.author.color)
    em.add_field(name="사용법", value="!등록")
    await ctx.send(embed=em)


@help.command()
async def 시작(ctx):
    em = discord.Embed(title="시작", description="디스코드 이름으로  사용자를 등록합니다.", color=ctx.author.color)
    em.add_field(name="사용법", value="!등록")
    await ctx.send(embed=em)


@help.command()
async def 휴식(ctx):
    em = discord.Embed(title="휴식", description="디스코드 이름으로  사용자를 등록합니다.", color=ctx.author.color)
    em.add_field(name="사용법", value="!등록")
    await ctx.send(embed=em)


@help.command()
async def 종료(ctx):
    em = discord.Embed(title="종료", description="디스코드 이름으로  사용자를 등록합니다.", color=ctx.author.color)
    em.add_field(name="사용법", value="!등록")
    await ctx.send(embed=em)


# App events
@app.event
async def on_ready():
    print(f'{app.user.name} 연결성공')
    # app.loop.create_task(task())
    await app.change_presence(status=discord.Status.online, activity=None)

# auto_save & get guild_id feature
@app.event
async def on_member_update(before, after):
    global guild_id
    guild_id = after.guild.id
    print(guild_id)

##############
###기타 함수###
##############
def strfdelta(tdelta, fmt):
    d = {}
    d["hours"], rem = divmod(tdelta.seconds, 3600)
    d["minutes"], d["seconds"] = divmod(rem, 60)
    return fmt.format(**d)


######################
### 명령어 처리 함수 ###
######################

# db에 사용자 등록
@app.command()
async def 등록(ctx):
    await bot_commands._등록(ctx, db)


# 목표시간 설정
@app.command()
async def 목표시간(ctx, time):
    await bot_commands._목표시간(ctx, time, db)

# 출석
@app.command()
async def 출석(ctx):
    await bot_commands._출석(ctx, db, embed, today_attend, today_study, ATTEND_TIME)

# 시작
@app.command()
async def 시작(ctx):
    await bot_commands._시작(ctx, db, today_attend, today_study)

# 휴식
@app.command()
async def 휴식(ctx):
    await bot_commands._휴식(ctx, db, today_attend, today_study, count, today_rest_time, app)

# today_rest_time 초기화 필요
@app.command()
async def 종료(ctx):
    await bot_commands._종료(ctx, db, today_attend, today_study, today_study_time, today_rest_time)

# 일주일 랭킹표
@app.command()
async def 랭킹(ctx):
    await bot_commands._랭킹(ctx, db)

# record
@app.command()
async def 기록(ctx):
    await bot_commands._기록(ctx)

app.run(TOKEN)
