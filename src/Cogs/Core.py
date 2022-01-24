import discord
from discord.ext import commands

class Core(commands.Cog):

    def __init__(self, app):
        self.app = app

    @commands.group(invoke_without_command=True)
    async def help(self, ctx, func = None):
        em = discord.Embed(title="Help", description="!help <명령어> 를 통해 더 자세한 정보를 확인해 보세요.")
        em.add_field(name="명령어", value="등록, 목표시간, 출석, 시작, 휴식, 휴식끝, 종료, 기록, 랭킹")
        await ctx.send(embed=em)

    @help.command()
    async def 등록(self, ctx):
        em = discord.Embed(title="등록", description="디스코드 이름으로  사용자를 등록합니다.", color=ctx.author.color)
        em.add_field(name="사용법", value="!등록")
        await ctx.send(embed=em)

    @help.command()
    async def 출석(self, ctx):
        em = discord.Embed(title="출석", description="현재 시각을 기준으로 공부를 하기 위해 출석을 합니다.", color=ctx.author.color)
        em.add_field(name="사용법", value="!출석")
        await ctx.send(embed=em)

    @help.command()
    async def 시작(self, ctx):
        em = discord.Embed(title="시작", description="현재 시각을 기준으로 공부를 시작합니다", color=ctx.author.color)
        em.add_field(name="사용법", value="!시작")
        await ctx.send(embed=em)

    @help.command()
    async def 휴식(self, ctx):
        em = discord.Embed(title="휴식", description="현재 시각을 기준으로 10분 휴식을 시작합니다.", color=ctx.author.color)
        em.add_field(name="사용법", value="!휴식")
        await ctx.send(embed=em)

    @help.command()
    async def 휴식끝(self, ctx):
        em = discord.Embed(title="휴식끝", description="현재 시각을 기준으로 휴식을 종료하고 공부를 시작합니다.", color=ctx.author.color)
        em.add_field(name="사용법", value="!휴식끝")
        await ctx.send(embed=em)

    @help.command()
    async def 목표시간(self, ctx):
        em = discord.Embed(title="목표시간", description="하루 공부 목표시간을 시간 단위로 설정합니다", color=ctx.author.color)
        em.add_field(name="사용법", value="!목표시간 5")
        await ctx.send(embed=em)

    @help.command()
    async def 종료(self, ctx):
        em = discord.Embed(title="종료", description="현재 시각을 기준으로 공부를 종료합니다", color=ctx.author.color)
        em.add_field(name="사용법", value="!종료")
        await ctx.send(embed=em)

    @help.command()
    async def 기록(self, ctx):
        em = discord.Embed(title="기록", description="이번주의 요일별 공부시간과 목표시간 달성여부를 보여줍니다,", color=ctx.author.color)
        em.add_field(name="사용법", value="!기록")
        await ctx.send(embed=em)

    @help.command()
    async def 랭킹(self, ctx):
        em = discord.Embed(title="랭킹", description="일주일간 등록된 사용자들의 공부시간 순위을 보여줍니다.", color=ctx.author.color)
        em.add_field(name="사용법", value="!랭킹")
        await ctx.send(embed=em)

def setup(app):
     app.add_cog(Core(app))