import asyncio
import discord
import datetime
from PIL import Image
import os
from io import BytesIO
from database_study import DBupdater
from collections import defaultdict
from discord.ext import commands
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from week_table import week_table

# Token값 가져오기
TOKEN = os.environ.get("TOKEN")


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

# Daily reset task for apscheduler
async def daily_save():
    # 초기화 전 !종료 하지 않은 사용자 있는지 확인 후 처리
    channel = app.get_channel(931413535605551127)
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
        guild = app.get_guild(931413535605551124)
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


# on_ready event
@app.event
async def on_ready():
    print(f'{app.user.name} 연결성공')
    # app.loop.create_task(task())
    await app.change_presence(status=discord.Status.online, activity=None)


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
    # 등록된 사용자가 아닐 경우
    if db.is_admit(ctx.author.name):
        db.update(ctx.author.name)
        await ctx.send(f"[{ctx.author.name}] - 등록 완료")
    # 등록된 사용자인 경우
    else:
        await ctx.send(f"[{ctx.author.name}] - 이미 동록된 사용자입니다")


# 목표시간 설정
@app.command()
async def 목표시간(ctx, time):
    # 등록된 사용자가 아닐 경우
    if db.is_admit(ctx.author.name):
        await ctx.send(f"'!등록'을 먼저 입력해주세요")
    # 등록된 사용자인 경우
    else:
        db.update_2(ctx.author.name, datetime.timedelta(hours=int(time)))
        await ctx.send(f"[{ctx.author.name}] - 목표시간 {time}시간 설정")


# [attend_time] 변경 필요
@app.command()
async def 출석(ctx):
    if db.is_admit(ctx.author.name):
        await ctx.send(f"'!등록'을 먼저 입력해주세요")
        return;

    if (ctx.author.name in today_attend):
        await ctx.send("이미 출석했습니다")
    else:
        attend_time = datetime.datetime.now().strftime("%H:%M")
        # 지각인 경우
        if (attend_time > ATTEND_TIME):
            embed.add_field(name=ctx.author.name, value=attend_time + '\n\n:red_square: 지각')
        # 지각이 아닌 경우
        else:
            embed.add_field(name=ctx.author.name, value=attend_time + '\n\n:green_square: 출석')

        today_attend.append(ctx.author.name)
        today_study[ctx.author.name] = []
        await ctx.send(embed=embed)


@app.command()
async def 시작(ctx):
    if db.is_admit(ctx.author.name):
        await ctx.send(f"'!등록'을 먼저 입력해주세요")
        return;
    # 출석체크 여부
    if ctx.author.name in today_attend:
        today_study[ctx.author.name].append(datetime.datetime.now())
        await ctx.send(f"[{ctx.author.name}] - {today_study[ctx.author.name][-1].strftime('%H:%M')} 시작")
    else:
        await ctx.send("출석체크 부탁드립니다")


@app.command()
async def 휴식(ctx):
    if db.is_admit(ctx.author.name):
        await ctx.send(f"'!등록'을 먼저 입력해주세요")
        return;

    # 출석체크 여부
    if ctx.author.name not in today_attend:
        await ctx.send("출석체크 부탁드립니다")
    # 시작여부 확인
    elif len(today_study[ctx.author.name]) % 2 == 0:
        await ctx.send("!시작을 먼저 입력해주세요")
    else:
        # 공부 종료시간 입력
        today_study[ctx.author.name].append(datetime.datetime.now())

        # wait_for 함수 handler
        def check(message):
            return message.content == "!휴식끝" and message.author == ctx.author

        # 기본 10분 휴식, 10분지나면 mention 후 다시 10분 휴식
        async def wait_user():
            try:
                rest_time = (datetime.datetime.now() + datetime.timedelta(minutes=10))
                await ctx.send(f"[{ctx.author.name}] - 10분 휴식\n {rest_time.strftime('%H:%M')}분 까지 '!휴식끝'을 입력해주세요")
                msg = await app.wait_for('message', timeout=600.0, check=check)
            except asyncio.TimeoutError:
                count[ctx.author.name] += datetime.timedelta(minutes=10)
                await ctx.send(f'{ctx.author.mention} 10분 지났습니다...')
                await wait_user()
            else:
                total_rest_time = datetime.datetime.now() + datetime.timedelta(minutes=10) - rest_time + count[
                    ctx.author.name]
                # today_rest_time에 사용자 휴식시간을 더해줌
                today_rest_time[ctx.author.name] += total_rest_time
                await ctx.send(
                    f'[{ctx.author.name}] - 휴식 끝 \n 휴식시간 - {strfdelta(total_rest_time, "{minutes}분{seconds}초")}')
                # 공부 시작시간 입력
                today_study[ctx.author.name].append(datetime.datetime.now())
                # 휴식 count 초기화
                count[ctx.author.name] = datetime.timedelta()

        await wait_user()


# today_rest_time 초기화 필요
@app.command()
async def 종료(ctx):
    if db.is_admit(ctx.author.name):
        await ctx.send(f"'!등록'을 먼저 입력해주세요")
        return;
    # 출석체크 확인
    if ctx.author.name not in today_attend:
        await ctx.send("출석체크 부탁드립니다")
    # 시작여부 확인
    elif len(today_study[ctx.author.name]) % 2 == 0:
        await ctx.send("!시작을 먼저 입력해주세요")
    # db 업데이트 및 공부시간 출력
    else:
        today_study[ctx.author.name].append(datetime.datetime.now())
        for i in range(0, len(today_study[ctx.author.name]), 2):
            start_time = today_study[ctx.author.name][i]
            end_time = today_study[ctx.author.name][i + 1]
            print(start_time, end_time)
            today_study_time[ctx.author.name] += end_time - start_time

        display = discord.Embed(title = "공부 기록", colur = discord.Colour.magenta())
        out = f":alarm_clock:  {today_study[ctx.author.name][0].strftime('%H:%M:%S')} ~ {datetime.datetime.now().strftime('%H:%M:%S')}\n "
        # 오늘 처음 공부 종료를 할 경우
        if db.is_admit_today(ctx.author.name, datetime.date.today()):
            db.update_3(ctx.author.name, today_study_time[ctx.author.name])
        # db에서 오늘 공부한 시간을 가져옴
        else:
            db.update_4(ctx.author.name, db.get_info(ctx.author.name) + today_study_time[ctx.author.name])

        # db의 total_study_time 업데이트
        db.update_5(ctx.author.name, today_study_time[ctx.author.name])

        out += f':book: 공부 시간 : {strfdelta(today_study_time[ctx.author.name], "{hours}시간{minutes}분{seconds}초")}\n :coffee: 휴식 시간 : {strfdelta(today_rest_time[ctx.author.name], "{hours}시간{minutes}분{seconds}초")}'
        display.add_field(name = f"[{ctx.author.name}] - 공부 끝!\n", value = out)

        await ctx.send(embed = display)

        # 다음 공부를 위한 변수 초기화
        today_study_time[ctx.author.name] = datetime.timedelta()
        today_rest_time[ctx.author.name] = datetime.timedelta()
        today_study[ctx.author.name] = []


# 일주일 랭킹표
@app.command()
async def 랭킹(ctx):
    ranking_dict = {}
    ranking_db = db.get_ranking()
    ranking_display = ""
    ranking_table = discord.Embed(title="랭킹", colour=discord.Colour.purple())
    out = ""

    # 1, 2, 3위를 기록하기 위한 count변수
    rank_count = 0

    for data in ranking_db:
        ranking_dict[data[0]] = strfdelta(data[1], "{hours}시간{minutes}분{seconds}초")

    # 정렬
    ranking_dict = sorted(ranking_dict.items(), key=lambda x: x[1])

    # 출력 내용
    for key, value in ranking_dict:
        rank_count += 1
        if (rank_count == 1):
            out += ":one: "
        elif (rank_count == 2):
            out += ":two: "
        elif (rank_count == 3):
            out += ":three: "

        out += f"{key} : {value}"

        if (rank_count == 1):
            out += ":crown:\n"
        else:
            out += "\n"

    ranking_table.add_field(name="순위표", value=out)

    await ctx.send(embed=ranking_table)


@app.command()
async def 기록(ctx):
    week_table_class = week_table(ctx.author.name)
    week_table_class.add_data()

    with BytesIO() as image_binary:
        week_table_class.im.save(image_binary, "png")
        image_binary.seek(0)
        week_table_img = discord.File(fp=image_binary, filename="week_table.png")
        await ctx.send(file=week_table_img)





app.run(TOKEN)
