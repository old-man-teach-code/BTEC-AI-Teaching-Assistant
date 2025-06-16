import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

# Load biến môi trường từ file .env
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# Khởi tạo intents - rất quan trọng!
intents = discord.Intents.default()
intents.message_content = True  # Để bot nhận nội dung message

# Khởi tạo bot với intents
bot = commands.Bot(command_prefix="!", intents=intents)

# Danh sách các cogs (module) sẽ được load
initial_extensions = [
    "cogs.moderation",
    "cogs.fun",
    "cogs.utility"
]

if __name__ == "__main__":
    for extension in initial_extensions:
        bot.load_extension(extension)
    bot.run(TOKEN)