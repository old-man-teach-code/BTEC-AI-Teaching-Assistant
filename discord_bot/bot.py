import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import asyncio

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
N8N_WEBHOOK_URL = os.getenv("N8N_WEBHOOK_URL")

intents = discord.Intents.default()
intents.message_content = True 
bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

@bot.event
async def on_ready():
    print(f"Bot đã online với tên: {bot.user}")

@bot.event
async def on_message(message):
    print(f"Nhận message: {message.content} từ {message.author}")
    if message.author == bot.user:
        return  
    if not message.content.startswith('!'):
        return
    if message.content.startswith('!ping'):
        await message.channel.send("Pong!")
    elif message.content.startswith('!help'):
        help_text = "Các lệnh cơ bản:\n!ping - reply Pong!\n!help - list các commands\n!kick - kick thành viên\n!ban - ban thành viên"
        await message.channel.send(help_text)
    await bot.process_commands(message)

initial_extensions = [
    "cogs.moderation",
    "cogs.fun",
    "cogs.utility"
]

async def main():
    for ext in initial_extensions:
        try:
            await bot.load_extension(ext)
            print(f"Đã load extension: {ext}")
        except Exception as e:
            print(f"Không thể load extension {ext}: {e}")
    await bot.start(TOKEN)

if __name__ == "__main__":
    asyncio.run(main())