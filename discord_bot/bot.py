import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import asyncio
import aiohttp
import json
import uvicorn
from api_server import app, set_bot_instance

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
N8N_WEBHOOK_URL = os.getenv("N8N_WEBHOOK_URL")
BACKEND_URL = os.getenv("BACKEND_URL")

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

async def get_user_by_discord_id(discord_user_id: str) -> dict:
    """
    Tìm user trong database bằng discord_user_id
    Returns: user info từ backend hoặc None
    """
    try:
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        # Không cần auth token cho public endpoint
        async with aiohttp.ClientSession() as session:
            # Endpoint public không cần JWT
            endpoint = f"{BACKEND_URL}/users/by-discord/{discord_user_id}"
            
            async with session.get(
                endpoint,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                if response.status == 200:
                    user_data = await response.json()
                    print(f"✅ Found user for Discord ID {discord_user_id}: {user_data.get('name')} (ID: {user_data.get('id')})")
                    return user_data
                elif response.status == 404:
                    print(f"❌ No user found for Discord ID: {discord_user_id}")
                    return None
                else:
                    print(f"❌ Error getting user by Discord ID {discord_user_id}: {response.status}")
                    return None
                    
    except Exception as e:
        print(f"❌ Exception getting user by Discord ID {discord_user_id}: {str(e)}")
        return None

@bot.event
async def on_ready():
    print(f'{bot.user} đã đăng nhập thành công!')
    # Set bot instance cho API server
    set_bot_instance(bot)

@bot.event
async def on_message(message):
    # Bỏ qua tin nhắn từ bot
    if message.author == bot.user:
        return
    
    # Xử lý commands trước
    if message.content.startswith('!'):
        await bot.process_commands(message)
        return
    
    # Bỏ qua tin nhắn trống
    if not message.content.strip():
        return
    
    question = message.content.strip()
    
    # Xác định loại kênh và thông tin người gửi
    is_dm = isinstance(message.channel, discord.DMChannel)
    
    # Tìm user trong database bằng Discord ID
    discord_user_id = str(message.author.id)
    user_from_db = await get_user_by_discord_id(discord_user_id)
    
    # Chuẩn bị dữ liệu request với thông tin từ database
    student_info = {
        "name": message.author.display_name or message.author.name,
        "student_id": str(message.author.id),
        "class": message.channel.name if not is_dm else "Direct Message",
        "discord_id": discord_user_id
    }
    
    # Thêm thông tin từ database nếu tìm thấy
    if user_from_db:
        student_info.update({
            "database_user_id": user_from_db.get("id"),
            "database_name": user_from_db.get("name"),
            "email": user_from_db.get("email"),
            "is_registered_user": True
        })
        print(f"🔍 Found registered user: {user_from_db.get('name')} (DB ID: {user_from_db.get('id')})")
    else:
        student_info["is_registered_user"] = False
        print(f"🔍 User not found in database for Discord ID: {discord_user_id}")
    
    request_data = {
        "question": question,
        "student_info": student_info,
        "channel_info": {
            "channel_id": str(message.channel.id),
            "guild_id": str(message.guild.id) if message.guild else "DM",
            "is_dm": is_dm,
            "channel_name": message.channel.name if not is_dm else "DM"
        },
        "senderId": str(message.author.id) if is_dm else str(message.channel.id)
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
                        if isinstance(result, dict) and result.get('success'):
                            response_data = result.get('response', 'Không có phản hồi')
                            
                            if isinstance(response_data, list) and response_data and 'template_id' in response_data[0]:
                                preview = response_data[0]
                                msg = f"**Template ID:** {preview['template_id']}\n**Nội dung:** {preview['rendered_content']}"
                            else:
                                msg = str(response_data)
                            
                            if is_dm:
                                await message.author.send(msg)
                            else:
                                await message.reply(msg)
                                
                    except json.JSONDecodeError:
                        pass
                else:
                    pass
                        
    except asyncio.TimeoutError:
        pass
            
    except Exception as e:
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
    !userinfo — xem thông tin user từ database
    !kick — kick thành viên
    !ban — ban thành viên
    !roll — quay xúc xắc (ví dụ: !roll 2d6)
    """
    await ctx.send(help_text)

@bot.command(name='userinfo')
async def userinfo_command(ctx, user: discord.Member = None):
    """Xem thông tin user từ database"""
    target_user = user or ctx.author
    discord_user_id = str(target_user.id)
    
    # Tìm user trong database
    user_from_db = await get_user_by_discord_id(discord_user_id)
    
    if user_from_db:
        embed = discord.Embed(
            title="📋 Thông tin User",
            color=0x00ff00,
            description=f"Thông tin của {target_user.display_name}"
        )
        embed.add_field(name="💾 Database ID", value=user_from_db.get("id"), inline=True)
        embed.add_field(name="👤 Tên trong DB", value=user_from_db.get("name"), inline=True)
        embed.add_field(name="📧 Email", value=user_from_db.get("email", "Không có"), inline=True)
        embed.add_field(name="🆔 Discord ID", value=discord_user_id, inline=True)
        embed.add_field(name="📅 Tạo lúc", value=user_from_db.get("created_at", "Không rõ"), inline=True)
        embed.add_field(name="✅ Trạng thái", value="Đã đăng ký", inline=True)
        
        await ctx.reply(embed=embed)
    else:
        embed = discord.Embed(
            title="❌ Không tìm thấy",
            color=0xff0000,
            description=f"User {target_user.display_name} chưa được đăng ký trong hệ thống"
        )
        embed.add_field(name="🆔 Discord ID", value=discord_user_id, inline=True)
        embed.add_field(name="💡 Gợi ý", value="Hãy đăng ký tài khoản trên website để kết nối Discord", inline=False)
        
        await ctx.reply(embed=embed)

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
        uvicorn.run("api_server:app", host="0.0.0.0", port=8080, reload=False)

    t1 = threading.Thread(target=run_discord)
    t2 = threading.Thread(target=run_fastapi)
    t1.start()
    t2.start()
    t1.join()
    t2.join()