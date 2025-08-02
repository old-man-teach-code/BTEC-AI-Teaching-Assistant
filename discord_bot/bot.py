import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import asyncio
import aiohttp
import json
# Thêm FastAPI
from fastapi import FastAPI
import uvicorn

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
N8N_WEBHOOK_URL = os.getenv("N8N_WEBHOOK_URL")

# Khởi tạo FastAPI
app = FastAPI()

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

@bot.event
async def on_ready():
    pass

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    # Xử lý commands trước
    if message.content.startswith('!'):
        await bot.process_commands(message)
        return
    
    question = message.content.strip()
    request_data = {
        "question": question,
        "student_info": {
            "name": message.author.display_name or message.author.name,
            "student_id": str(message.author.id),
            "class": message.channel.name,
            "discord_id": str(message.author.id)
        },
        "channel_info": {
            "channel_id": str(message.channel.id),
            "guild_id": str(message.guild.id) if message.guild else "DM"
        }
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                N8N_WEBHOOK_URL,
                json=request_data,
                headers={"Content-Type": "application/json"},
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                if response.status == 200:
                    try:
                        result = await response.json()
                        # Nếu kết quả là template preview
                        if isinstance(result, dict) and result.get('success'):
                            response_data = result.get('response', 'Không có phản hồi')
                            # Nếu response_data là list và có trường template_id, rendered_content
                            if isinstance(response_data, list) and response_data and 'template_id' in response_data[0]:
                                preview = response_data[0]
                                msg = f"**Template ID:** {preview['template_id']}\n**Nội dung:** {preview['rendered_content']}"
                                # Nếu là DM thì gửi về DM, nếu là channel thì gửi về channel
                                if isinstance(message.channel, discord.DMChannel):
                                    await message.author.send(msg)
                                else:
                                    await message.channel.send(msg)
                            else:
                                # Mặc định gửi về channel hoặc reply
                                await message.reply(str(response_data))
                    except json.JSONDecodeError:
                        pass
                else:
                    pass
    except asyncio.TimeoutError:
        pass
    except Exception:
        pass
    
@bot.command(name='hello')
async def hello_command(ctx):
    """Chào bot"""
    await ctx.reply(f"Xin chào {ctx.author.display_name}! 👋")

@bot.command(name='ping')
async def ping_command(ctx):
    """Kiểm tra phản hồi"""
    latency = round(bot.latency * 1000)
    await ctx.reply(f"🏓 Pong! Độ trễ: {latency}ms")

@bot.command(name='help')
async def help_command(ctx):
    """Xem menu trợ giúp"""
    help_text = """**🤖 Trợ lý giảng viên - Lệnh hỗ trợ:**

    **📋 Lệnh có sẵn:**
    `!hello` — chào bot  
    `!ping` — kiểm tra phản hồi  
    `!help` — xem menu trợ giúp
    `!kick` — kick thành viên
    `!ban` — ban thành viên
    `!roll` — quay xúc xắc (ví dụ: !roll 2d6)

    **🎯 AI Assistant:**
    Gửi bất kỳ tin nhắn nào để AI trả lời
    VD: "Khi nào deadline bài tập?"
    """
    await ctx.send(help_text)

# Load các phần mở rộng nếu có
initial_extensions = [
    "cogs.moderation",
    "cogs.fun",
    "cogs.utility"
]

async def main():
    for ext in initial_extensions:
        try:
            await bot.load_extension(ext)
        except Exception:
            pass

    try:
        await bot.start(TOKEN)
    except discord.LoginFailure:
        pass
    except Exception:
        pass

if __name__ == "__main__":
    import threading

    def run_discord():
        asyncio.run(main())

    def run_fastapi():
        uvicorn.run("bot:app", host="0.0.0.0", port=8080)

    t1 = threading.Thread(target=run_discord)
    t2 = threading.Thread(target=run_fastapi)
    t1.start()
    t2.start()
    t1.join()
    t2.join()

