import os
from discord.ext import commands
from dotenv import load_dotenv

# Load token từ .env để bảo mật
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# Khởi tạo bot với prefix, intents mặc định
bot = commands.Bot(command_prefix="!", intents=None)

# Danh sách các cogs cần load
initial_extensions = [
    "cogs.moderation",
    "cogs.fun",
    "cogs.utility"
]

if __name__ == "__main__":
    for extension in initial_extensions:
        bot.load_extension(extension)
    bot.run(TOKEN)