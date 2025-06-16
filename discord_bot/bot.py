import json, asyncio, discord, httpx
from fastapi import FastAPI, Request
from contextlib import asynccontextmanager
from datetime import datetime
from pydantic import BaseModel
from typing import Set, List, Union

DISCORD_BOT_TOKEN = 'YOUR_DISCORD_BOT_TOKEN'
N8N_WEBHOOK_URL = 'https://n8n-se06303.tino.page/webhook/b4974b3d-91a8-44e2-98a0-d1b8e8aff908'
SENT_MESSAGES_FILE = "sent_messages.json"

intents = discord.Intents.default()
intents.message_content = intents.messages = intents.guilds = intents.dm_messages = True
bot = discord.Client(intents=intents)

def load_sent_messages() -> Set[str]:
    try:
        with open(SENT_MESSAGES_FILE, "r") as f:
            return set(json.load(f))
    except: return set()

def save_sent_messages(messages: Set[str]):
    with open(SENT_MESSAGES_FILE, "w") as f:
        json.dump(list(messages), f)

sent_messages = load_sent_messages()

@bot.event
async def on_ready(): ...

@bot.event
async def on_message(msg):
    if msg.author.bot: return
    await asyncio.sleep(0.5)

    valid_ext = ('.png', '.jpg', '.jpeg', '.pdf', '.doc', '.docx', '.csv')
    filtered = [a for a in msg.attachments if a.filename.lower().endswith(valid_ext)]
    urls = sorted((a.url for a in filtered), key=len)[:3]
    names = [a.filename.lower() for a in filtered]

    payload = {
        'timestamp': datetime.utcnow().isoformat(),
        'username': msg.author.name,
        'user_id': str(msg.author.id),
        'channel': str(msg.channel),
        'channel_id': str(getattr(msg.channel, 'id', 'unknown')),
        'content': msg.content,
        'channel_type': 'DM' if isinstance(msg.channel, discord.DMChannel) else 'Guild Channel',
        'attachment_urls': urls,
        'attachment_filenames': names,
    }

    try:
        async with httpx.AsyncClient() as client:
            await client.post(N8N_WEBHOOK_URL, json=payload)
    except: ...

@asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.create_task(bot.start(DISCORD_BOT_TOKEN))
    yield
    if not task.done():
        task.cancel()
        try: await task
        except asyncio.CancelledError: ...

app = FastAPI(lifespan=lifespan)

@app.get("/")
async def root():
    return {"message": "FastAPI + Discord bot đang chạy"}

@app.post("/webhook/response")
async def webhook_response(request: Request):
    data = await request.json()
    content, cid, uid, ctype = map(data.get, ("content", "channel_id", "user_id", "channel_type"))
    if not content:
        return {"error": "Thiếu nội dung"}

    if ctype == "Guild Channel" and cid:
        if channel := bot.get_channel(int(cid)):
            await channel.send(content)
            return {"status": f"Đã gửi đến channel {cid}"}
        return {"error": "Không tìm thấy channel"}

    if ctype == "DM" and uid:
        if user := await bot.fetch_user(int(uid)):
            await user.send(content)
            return {"status": f"Đã gửi tin nhắn riêng đến user {uid}"}
        return {"error": "Không tìm thấy user"}

    return {"error": "Kiểu kênh không hợp lệ hoặc thiếu ID"}

class WebhookPayload(BaseModel):
    Issent: bool
    message: str
    id: Union[str, int]
    users: str
    channel_ids: Union[str, List[str]]
    allChannelIDs: List[str] = []

@app.post("/webhook/notification")
async def webhook_handler(request: Request):
    global sent_messages
    data = await request.json()

    message = data.get("message", "Thông báo từ giáo viên").strip()
    channel_ids = data.get("channel_ids", [])
    all_channel_ids = data.get("allChannelIDs", [])
    attachments = "\n".join(filter(None, [data.get(f"AttachmentURL{i}") for i in range(1, 4)]))
    discord_message = f"📢 **Teacher**: @everyone {message}\n{attachments}"

    results = {"channels": {"sent": [], "failed": [], "skipped": []}}

    def is_sent(key): return key in sent_messages
    def mark_sent(key): sent_messages.add(key)

    if isinstance(channel_ids, str):
        try: channel_ids = json.loads(channel_ids)
        except: channel_ids = [channel_ids]
    elif not isinstance(channel_ids, list):
        channel_ids = []

    if all_channel_ids == ["1377893907861602357"]:  # send_to_all
        for guild in bot.guilds:
            for ch in guild.text_channels:
                key = f"{discord_message}|{ch.id}"
                if is_sent(key):
                    results["channels"]["skipped"].append((guild.name, ch.name)); continue
                try:
                    await ch.send(discord_message)
                    results["channels"]["sent"].append((guild.name, ch.name))
                    mark_sent(key)
                except:
                    results["channels"]["failed"].append((guild.name, ch.name))
    else:
        for ch_id in all_channel_ids:
            try: ch_id_int = int(ch_id)
            except ValueError: continue
            key = f"{discord_message}|{ch_id_int}"
            if is_sent(key):
                results["channels"]["skipped"].append(("Unknown Guild", str(ch_id_int))); continue
            if channel := bot.get_channel(ch_id_int):
                try:
                    await channel.send(discord_message)
                    results["channels"]["sent"].append((channel.guild.name, channel.name))
                    mark_sent(key)
                except:
                    results["channels"]["failed"].append((channel.guild.name, channel.name))
            else:
                results["channels"]["failed"].append(("Unknown Guild", str(ch_id_int)))

    save_sent_messages(sent_messages)
    return {"success": True, "results": results}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("bot:app", host="0.0.0.0", port=8060)
