import datetime
import asyncio
from backend.app.models.event import Event  # Giả sử Event là SQLAlchemy model
from backend.app.models.user import User
from backend.app.database.session import SessionLocal
import aiohttp

def get_upcoming_reminders(session):
    now = datetime.datetime.now()
    in_15_min = now + datetime.timedelta(minutes=15)
    return session.query(Event).filter(
        Event.reminder_time != None,
        Event.reminded == False,
        Event.reminder_time >= now,
        Event.reminder_time <= in_15_min
    ).all()

def mark_as_reminded(session, event):
    event.reminded = True
    session.commit()


async def send_discord_reminder(event, discord_user_id=None, channel_id=None):
    """
    Gửi notification thật tới Discord bot qua API /send_reminder
    """
    BOT_API_URL = "http://localhost:8080/send_reminder"
    payload = {
        "title": event.title,
        "start_time": str(event.start_time),
        "description": event.description,
    }
    if discord_user_id:
        payload["user_id"] = discord_user_id
    if channel_id:
        payload["channel_id"] = channel_id
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(BOT_API_URL, json=payload, timeout=10) as resp:
                if resp.status == 200:
                    print(f"[Reminder] Đã gửi notification Discord cho user {discord_user_id} hoặc channel {channel_id}")
                else:
                    print(f"[Reminder] Lỗi gửi notification Discord: {resp.status}")
    except Exception as e:
        print(f"[Reminder] Exception gửi notification Discord: {e}")


async def check_reminders():
    """
    Chạy mỗi phút: lấy event sắp nhắc, gửi notification Discord, đánh dấu đã nhắc
    """
    while True:
        session = SessionLocal()
        try:
            events = get_upcoming_reminders(session)
            for event in events:
                # Lấy user để lấy discord_user_id
                user = session.query(User).filter(User.id == event.owner_id).first()
                discord_user_id = user.discord_user_id if user and hasattr(user, 'discord_user_id') else None
                # Gửi notification thật (DM nếu có user, hoặc gửi vào channel nếu có channel_id trong event)
                channel_id = getattr(event, 'channel_id', None)
                await send_discord_reminder(event, discord_user_id=discord_user_id, channel_id=channel_id)
                mark_as_reminded(session, event)
        except Exception as e:
            print(f"[Reminder Error] {e}")
        finally:
            session.close()
        await asyncio.sleep(60)


# Hàm này để chạy riêng khi cần
if __name__ == "__main__":
    asyncio.run(check_reminders())
