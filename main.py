from class_draft import StudyBot

# Token값 가져오기
# TOKEN = os.environ.get("TOKEN")

TOKEN = "..."

discord_bot = StudyBot('!')
discord_bot.initialize()
discord_bot.add_schedule()
discord_bot.run(TOKEN)



'''# Add Custom Help Command
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
    await ctx.send(embed=em)'''


