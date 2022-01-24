import datetime
import asyncio
import discord
from week_table import week_table
from io import BytesIO

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

async def inside(db, today_study, today_study_time, today_rest_time, user, channel):
    today_study[user].append(datetime.datetime.now())
    for i in range(0, len(today_study[user]), 2):
        start_time = today_study[user][i]
        end_time = today_study[user][i + 1]
        print(start_time, end_time)
        today_study_time[user] += end_time - start_time

    await channel.send(
        f"[{user}] - 공부 끝!\n:alarm_clock:  {today_study[user][0].strftime('%H:%M:%S')} ~ "
        f"{datetime.datetime.now().strftime('%H:%M:%S')}"
    )
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
        f':coffee: 휴식 시간 : {strfdelta(today_rest_time[user], "{hours}시간{minutes}분{seconds}초")}'
    )
    today_rest_time[user] = datetime.timedelta()

    #다음 공부를 위한 변수 초기화
    today_study_time[user] = datetime.timedelta()
    today_rest_time[user] = datetime.timedelta()
    today_study[user] = []

# Daily reset task for apscheduler
async def daily_save(app, today_study, today_study_time, today_rest_time, db):
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
            await inside(db, today_study, today_study_time, today_rest_time, user, channel)
    
    # today_attend 변수 초기화 - 문제 발생 부분! 수정 필요
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

# db에 사용자 등록
async def _등록(ctx, db):
    # 등록된 사용자가 아닐 경우
    if db.is_admit(ctx.author.name):
        db.update(ctx.author.name)
        await ctx.send(f"[{ctx.author.name}] - 등록 완료")
    # 등록된 사용자인 경우
    else:
        await ctx.send(f"[{ctx.author.name}] - 이미 동록된 사용자입니다")

async def _목표시간(ctx, time, db):
    # 등록된 사용자가 아닐 경우
    if db.is_admit(ctx.author.name):
        await ctx.send(f"'!등록'을 먼저 입력해주세요")
    # 등록된 사용자인 경우
    else:
        db.update_2(ctx.author.name, datetime.timedelta(hours=int(time)))
        await ctx.send(f"[{ctx.author.name}] - 목표시간 {time}시간 설정")

# attend_time 변경 필요
async def _출석(ctx, db, embed, today_attend, today_study, ATTEND_TIME):
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

# 시작
async def _시작(ctx, db, today_attend, today_study):
    if db.is_admit(ctx.author.name):
        await ctx.send(f"'!등록'을 먼저 입력해주세요")
        return;
    # 출석체크 여부
    if ctx.author.name in today_attend:
        today_study[ctx.author.name].append(datetime.datetime.now())
        await ctx.send(f"[{ctx.author.name}] - {today_study[ctx.author.name][-1].strftime('%H:%M')} 시작")
    else:
        await ctx.send("출석체크 부탁드립니다")

# 휴식
async def _휴식(ctx, db, today_attend, today_study, count, today_rest_time, app):
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
async def _종료(ctx, db, today_attend, today_study, today_study_time, today_rest_time):
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
        await inside(db, today_study, today_study_time, today_rest_time, ctx.author.name, ctx.channel)


# 일주일 랭킹표
async def _랭킹(ctx, db):
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
    ranking_dict = sorted(ranking_dict.items(), key=lambda x: x[1], reverse=True)

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


async def _기록(ctx):
    week_table_class = week_table(ctx.author.name)
    week_table_class.add_data()

    with BytesIO() as image_binary:
        week_table_class.im.save(image_binary, "png")
        image_binary.seek(0)
        week_table_img = discord.File(fp=image_binary, filename="week_table.png")
        await ctx.send(file=week_table_img)
