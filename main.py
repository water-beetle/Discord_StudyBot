from class_draft import StudyBot
import os

# Token값 가져오기
# TOKEN = os.environ.get("TOKEN")

TOKEN = "..."

discord_bot = StudyBot('!')

for filename in os.listdir("Cogs"):
    if filename.endswith(".py"):
        discord_bot.load_extension(f"Cogs.{filename[:-3]}")

discord_bot.initialize()
discord_bot.add_schedule()
discord_bot.run(TOKEN)