import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import asyncio
import aiohttp
import json
from fastapi import FastAPI, Request
import uvicorn

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
N8N_WEBHOOK_URL = os.getenv("N8N_WEBHOOK_URL")
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

app = FastAPI()

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

async def send_reminder(event, user_id=None, channel_id=None):
    # Format message
    title = event.get('title') if isinstance(event, dict) else getattr(event, 'title', getattr(event, 'name', ''))
    start_time = event.get('start_time') if isinstance(event, dict) else getattr(event, 'start_time', '')
    description = event.get('description') if isinstance(event, dict) else getattr(event, 'description', None)
    msg = f"📅 **Nhắc nhở sự kiện:** {title}\n🕒 Thời gian: {start_time}\n"
    if description:
        msg += f"📝 Mô tả: {description}\n"
    # Gửi DM nếu có user_id
    if user_id:
        try:
            user = await bot.fetch_user(int(user_id))
            if user:
                await user.send(msg)
        except Exception:
            pass
    # Gửi vào channel nếu có channel_id
    elif channel_id:
        try:
            channel = await bot.fetch_channel(int(channel_id))
            if channel:
                await channel.send(msg)
        except Exception:
            pass

@app.post("/send_reminder")
async def api_send_reminder(request: Request):
    data = await request.json()
    
    # Hàm helper để lấy user info từ backend
    async def get_user_info(owner_id):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{BACKEND_URL}/discord/users/{owner_id}",
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status == 200:
                        user_data = await response.json()
                        return {
                            "discord_user_id": user_data.get("discord_user_id"),
                            "name": user_data.get("name"),
                            "email": user_data.get("email")
                        }
        except Exception:
            pass
        return None
    
    async def process_event(event):
        user_id = event.get('user_id') or event.get('discord_id')
        channel_id = event.get('channel_id')
        owner_id = event.get('owner_id')
        
        await send_reminder(event, user_id=user_id, channel_id=channel_id)
        user_info = await get_user_info(owner_id) if owner_id else None
        
        return {
            "success": True,
            "description": event.get('description'),
            "start_time": event.get('start_time') or event.get('Start'),
            "end_time": event.get('end_time') or event.get('End'),
            "discord_user_id": user_info.get("discord_user_id") if user_info else None,
            "owner_id": owner_id
        }
    
    # Xử lý list hoặc single event
    if isinstance(data, list):
        results = [await process_event(event) for event in data]
        return {"results": results, "count": len(data)}
    
    return await process_event(data)

@bot.event
async def on_ready():
    pass

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
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
    !hello — chào bot  
    !ping — kiểm tra phản hồi  
    !help — xem menu trợ giúp
    !kick — kick thành viên
    !ban — ban thành viên
    !roll — quay xúc xắc (ví dụ: !roll 2d6)

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