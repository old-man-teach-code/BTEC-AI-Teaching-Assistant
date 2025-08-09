import os
import asyncio
import aiohttp
import json
import discord
from fastapi import FastAPI, Request, HTTPException
from dotenv import load_dotenv
from typing import Dict, Any
import concurrent.futures

load_dotenv()
BACKEND_URL = os.getenv("BACKEND_URL")
DEBUG_MODE = os.getenv("DEBUG_MODE", "false").lower() == "true"

app = FastAPI(title="Discord Bot API", description="API for Discord Bot messaging")

# Global bot reference - sẽ được set từ main bot
bot = None
# Queue để giao tiếp giữa FastAPI và Discord bot
message_queue = asyncio.Queue()
response_futures = {}

def debug_log(message: str):
    """Log debug message nếu DEBUG_MODE được bật"""
    if DEBUG_MODE:
        print(message)

def set_bot_instance(bot_instance):
    """Set bot instance để sử dụng trong API"""
    global bot
    bot = bot_instance
    # Start background task để xử lý message queue
    if bot:
        asyncio.create_task(process_message_queue())

async def process_message_queue():
    """Background task để xử lý message queue"""
    while True:
        try:
            if not message_queue.empty():
                task_data = await message_queue.get()
                task_id = task_data['id']
                action = task_data['action']
                params = task_data['params']
                
                try:
                    if action == 'send_message':
                        result = await _send_message_internal(params['sender_id'], params['output'])
                    elif action == 'debug_user':
                        result = await _debug_user_internal(params['sender_id'])
                    elif action == 'debug_channel':
                        result = await _debug_channel_internal(params['sender_id'])
                    else:
                        result = {"error": f"Unknown action: {action}"}
                    
                    # Set result cho future
                    if task_id in response_futures:
                        response_futures[task_id].set_result(result)
                        del response_futures[task_id]
                        
                except Exception as e:
                    if task_id in response_futures:
                        response_futures[task_id].set_result({"error": str(e)})
                        del response_futures[task_id]
            
            await asyncio.sleep(0.1)  # Tránh busy waiting
        except Exception as e:
            await asyncio.sleep(1)

async def _send_message_internal(sender_id: str, output: str) -> Dict[str, Any]:
    """Internal function để gửi message - chạy trong bot context"""
    try:
        sender_id_int = int(sender_id)
        debug_log(f"🔍 Processing sender_id: {sender_id_int}")
        
        # Thử gửi như user DM trước
        try:
            user = await bot.fetch_user(sender_id_int)
            if user:
                await user.send(str(output))
                debug_log(f"✅ Sent DM to user: {user.name}")
                return {"success": True, "type": "user", "target": str(sender_id), "target_name": user.name}
        except discord.NotFound:
            debug_log(f"User not found: {sender_id}")
        except discord.Forbidden:
            return {"success": False, "error": f"Cannot send DM to user {sender_id} (DMs disabled or blocked)"}
        except Exception as e:
            debug_log(f"Error with user {sender_id}: {str(e)}")
        
        # Thử gửi như channel
        try:
            channel = await bot.fetch_channel(sender_id_int)
            if channel:
                await channel.send(str(output))
                debug_log(f"✅ Sent to channel: {channel.name}")
                return {"success": True, "type": "channel", "target": str(sender_id), "target_name": channel.name}
        except discord.NotFound:
            debug_log(f"Channel not found: {sender_id}")
        except discord.Forbidden:
            return {"success": False, "error": f"No permission to send message to channel {sender_id}"}
        except Exception as e:
            debug_log(f"Error with channel {sender_id}: {str(e)}")
        
        return {"success": False, "error": f"Invalid sender_id or target not found: {sender_id}"}
        
    except Exception as e:
        return {"success": False, "error": str(e)}

async def _debug_user_internal(sender_id: str) -> Dict[str, Any]:
    """Internal function để debug user"""
    try:
        sender_id_int = int(sender_id)
        user = await bot.fetch_user(sender_id_int)
        return {
            "found": True,
            "name": user.name,
            "display_name": user.display_name,
            "bot": user.bot
        }
    except discord.NotFound:
        return {"found": False, "error": "User not found"}
    except Exception as e:
        return {"found": False, "error": str(e)}

async def _debug_channel_internal(sender_id: str) -> Dict[str, Any]:
    """Internal function để debug channel"""
    try:
        sender_id_int = int(sender_id)
        channel = await bot.fetch_channel(sender_id_int)
        return {
            "found": True,
            "name": channel.name,
            "type": str(channel.type),
            "guild": channel.guild.name if hasattr(channel, 'guild') and channel.guild else None
        }
    except discord.NotFound:
        return {"found": False, "error": "Channel not found"}
    except Exception as e:
        return {"found": False, "error": str(e)}

async def send_reminder(event, user_id=None, channel_id=None):
    """
    Gửi reminder đến Discord user hoặc channel
    """
    if not bot:
        raise HTTPException(status_code=500, detail="Bot instance not available")
    
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
            user = await asyncio.wait_for(bot.fetch_user(int(user_id)), timeout=10.0)
            if user:
                await asyncio.wait_for(user.send(msg), timeout=10.0)
        except Exception as e:
            pass
    # Gửi vào channel nếu có channel_id
    elif channel_id:
        try:
            channel = await asyncio.wait_for(bot.fetch_channel(int(channel_id)), timeout=10.0)
            if channel:
                await asyncio.wait_for(channel.send(msg), timeout=10.0)
        except Exception as e:
            pass

async def send_message_to_discord(sender_id: str, output: str) -> Dict[str, Any]:
    """
    Hàm helper để gửi tin nhắn đến Discord sử dụng queue system
    """
    if not bot or not bot.is_ready():
        return {"success": False, "error": "Bot not ready"}
    
    try:
        # Tạo unique task ID
        import uuid
        task_id = str(uuid.uuid4())
        
        # Tạo future để chờ kết quả
        future = asyncio.Future()
        response_futures[task_id] = future
        
        # Thêm task vào queue
        task_data = {
            'id': task_id,
            'action': 'send_message',
            'params': {'sender_id': sender_id, 'output': output}
        }
        await message_queue.put(task_data)
        
        # Chờ kết quả với timeout
        try:
            result = await asyncio.wait_for(future, timeout=15.0)
            return result
        except asyncio.TimeoutError:
            # Cleanup future nếu timeout
            if task_id in response_futures:
                del response_futures[task_id]
            return {"success": False, "error": "Timeout processing message"}
            
    except Exception as e:
        return {"success": False, "error": str(e)}

async def get_user_info(owner_id: str, auth_token: str = None) -> Dict[str, Any]:
    """
    Hàm helper để lấy user info từ backend
    owner_id là ID từ bảng users, cần lấy discord_user_id tương ứng
    auth_token: Bearer token từ request header
    """
    try:
        debug_log(f"🔍 Getting user info for owner_id: {owner_id}")
        debug_log(f"🔍 Backend URL: {BACKEND_URL}")
        
        # Tạo headers với authentication
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        # Sử dụng token từ request header hoặc fallback sang env
        token_to_use = auth_token or os.getenv("ADMIN_TOKEN") or os.getenv("API_TOKEN")
        if token_to_use:
            headers["Authorization"] = f"Bearer {token_to_use}"
            debug_log(f"🔍 Using authentication token")
        
        async with aiohttp.ClientSession() as session:
            # Endpoint chính xác từ logs: /api/users/{id}
            endpoint = f"{BACKEND_URL}/api/users/{owner_id}"
            
            try:
                debug_log(f"🔍 Trying authenticated endpoint: {endpoint}")
                async with session.get(
                    endpoint,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    debug_log(f"🔍 Response status: {response.status}")
                    
                    if response.status == 200:
                        user_data = await response.json()
                        debug_log(f"🔍 User data received: {user_data}")
                        debug_log(f"🔍 Raw discord_user_id value: {user_data.get('discord_user_id')}")
                        debug_log(f"🔍 Type of discord_user_id: {type(user_data.get('discord_user_id'))}")
                        
                        # Lấy discord_user_id - xử lý field String(64) nullable=True
                        discord_user_id_raw = user_data.get('discord_user_id')
                        discord_user_id_value = None
                        
                        debug_log(f"🔍 Raw discord_user_id: '{discord_user_id_raw}' (type: {type(discord_user_id_raw)})")
                        
                        if discord_user_id_raw is not None:
                            # Database field là String(64), có thể chứa string hoặc null
                            if isinstance(discord_user_id_raw, str):
                                # Kiểm tra string không rỗng và không phải "null"
                                stripped = discord_user_id_raw.strip()
                                if stripped and stripped.lower() != "null" and stripped != "":
                                    discord_user_id_value = stripped
                                    debug_log(f"🔍 String discord_user_id: '{discord_user_id_value}'")
                            elif isinstance(discord_user_id_raw, (int, float)):
                                # Chuyển number thành string
                                discord_user_id_value = str(int(discord_user_id_raw))
                                debug_log(f"🔍 Number to string discord_user_id: '{discord_user_id_value}'")
                        
                        debug_log(f"🔍 Final processed discord_user_id: '{discord_user_id_value}'")
                        
                        return {
                            "user_id": user_data.get("id"),
                            "discord_user_id": discord_user_id_value,
                            "name": user_data.get("name"),
                            "email": user_data.get("email"),
                            "has_discord_id": discord_user_id_value is not None,
                            "raw_discord_user_id": discord_user_id_raw,  # Để debug
                            "raw_data": user_data  # Thêm raw data để debug
                        }
                    else:
                        response_text = await response.text()
                        debug_log(f"❌ Error response: {response_text}")
                        
            except Exception as e:
                debug_log(f"❌ Error with endpoint {endpoint}: {str(e)}")
                    
    except Exception as e:
        debug_log(f"❌ Error getting user info for owner_id {owner_id}: {str(e)}")
    
    debug_log(f"❌ Could not get user info for owner_id {owner_id}")
    return None

@app.post("/send_reminder")
async def api_send_reminder(request: Request):
    """
    API endpoint để gửi reminder
    Body: Event data hoặc list of events
    """
    data = await request.json()
    
    # Lấy Authorization token từ header
    auth_header = request.headers.get("Authorization")
    auth_token = None
    if auth_header and auth_header.startswith("Bearer "):
        auth_token = auth_header.replace("Bearer ", "")
        debug_log(f"🔍 Received auth token from request header")
    
    async def process_event(event):
        user_id = event.get('user_id') or event.get('discord_id')
        channel_id = event.get('channel_id')
        owner_id = event.get('owner_id')
        
        # Lấy thông tin user từ backend nếu có owner_id, sử dụng token từ request
        user_info = await get_user_info(owner_id, auth_token) if owner_id else None
        debug_log(f"🔍 User info result for owner_id {owner_id}: {user_info}")
        
        # Nếu không có user_id trực tiếp nhưng có user_info, sử dụng discord_user_id
        original_user_id = user_id
        if not user_id and user_info and user_info.get('discord_user_id'):
            user_id = user_info.get('discord_user_id')
            debug_log(f"🔍 Using discord_user_id from database: '{user_id}' (was: '{original_user_id}')")
        
        debug_log(f"🔍 Final user_id for sending: '{user_id}'")
        
        # Gửi reminder
        await send_reminder(event, user_id=user_id, channel_id=channel_id)
        
        # Debug các giá trị trước khi return
        final_discord_user_id = user_info.get("discord_user_id") if user_info else user_id
        debug_log(f"🔍 Final discord_user_id: '{final_discord_user_id}'")
        debug_log(f"🔍 User name: {user_info.get('name') if user_info else None}")
        debug_log(f"🔍 Has discord_id in database: {user_info.get('has_discord_id', False) if user_info else False}")
        
        return {
            "success": True,
            "description": event.get('description'),
            "start_time": event.get('start_time') or event.get('Start'),
            "end_time": event.get('end_time') or event.get('End'),
            "discord_user_id": final_discord_user_id,
            "owner_id": owner_id,
            "user_name": user_info.get("name") if user_info else None,
            "has_discord_id_in_db": user_info.get('has_discord_id', False) if user_info else False,
            "raw_discord_user_id": user_info.get("raw_discord_user_id") if user_info else None
        }
    
    # Xử lý list hoặc single event
    if isinstance(data, list):
        results = [await process_event(event) for event in data]
        return {"results": results, "count": len(data)}
    
    return await process_event(data)

@app.post("/send_message")
async def api_send_message(request: Request):
    """
    API endpoint để gửi tin nhắn đến Discord
    Body: {
        "senderId": "123456789",  // Discord user ID hoặc channel ID
        "output": "Nội dung tin nhắn"
    }
    """
    try:
        data = await request.json()
        sender_id = data.get("senderId")
        output = data.get("output")
        
        if not sender_id:
            raise HTTPException(status_code=400, detail="Missing senderId")
        
        if not output:
            raise HTTPException(status_code=400, detail="Missing output")
        
        result = await send_message_to_discord(sender_id, output)
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "bot_connected": bot is not None and bot.is_ready() if bot else False,
        "bot_user": str(bot.user) if bot and bot.user else None,
        "bot_guilds": len(bot.guilds) if bot else 0
    }

@app.get("/debug/{sender_id}")
async def debug_sender_id(sender_id: str):
    """Debug endpoint để kiểm tra sender_id sử dụng queue system"""
    if not bot or not bot.is_ready():
        return {"error": "Bot not ready"}
    
    try:
        sender_id_int = int(sender_id)
    except ValueError:
        return {"error": f"Invalid sender_id format: {sender_id}"}
    
    result = {
        "sender_id": sender_id,
        "bot_ready": bot.is_ready(),
        "user_check": None,
        "channel_check": None
    }
    
    # Check user using queue
    try:
        import uuid
        task_id = str(uuid.uuid4())
        future = asyncio.Future()
        response_futures[task_id] = future
        
        task_data = {
            'id': task_id,
            'action': 'debug_user',
            'params': {'sender_id': sender_id}
        }
        await message_queue.put(task_data)
        
        user_result = await asyncio.wait_for(future, timeout=10.0)
        result["user_check"] = user_result
        
    except asyncio.TimeoutError:
        result["user_check"] = {"found": False, "error": "Timeout checking user"}
    except Exception as e:
        result["user_check"] = {"found": False, "error": str(e)}
    
    # Check channel using queue
    try:
        import uuid
        task_id = str(uuid.uuid4())
        future = asyncio.Future()
        response_futures[task_id] = future
        
        task_data = {
            'id': task_id,
            'action': 'debug_channel',
            'params': {'sender_id': sender_id}
        }
        await message_queue.put(task_data)
        
        channel_result = await asyncio.wait_for(future, timeout=10.0)
        result["channel_check"] = channel_result
        
    except asyncio.TimeoutError:
        result["channel_check"] = {"found": False, "error": "Timeout checking channel"}
    except Exception as e:
        result["channel_check"] = {"found": False, "error": str(e)}
    
    return result


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Discord Bot API Server",
        "endpoints": [
            "/send_message - POST: Gửi tin nhắn đến Discord",
            "/send_reminder - POST: Gửi reminder",
            "/guilds - GET: Lấy tất cả servers/guilds",
            "/guilds/{guild_id}/channels - GET: Lấy channels trong guild",
            "/health - GET: Kiểm tra trạng thái",
            "/debug/{sender_id} - GET: Debug user/channel",
            "/docs - GET: API documentation"
        ]
    }
