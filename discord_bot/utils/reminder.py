import discord

async def send_reminder(bot, discord_user_id, event):
    """
    Gửi nhắc nhở qua Discord DM hoặc channel.
    """
    user = await bot.fetch_user(discord_user_id)
    if user:
        msg = f"Nhắc nhở: Sự kiện '{event['title']}' lúc {event['reminder_time']}\nChi tiết: {event.get('description','')}"
        try:
            await user.send(msg)
        except Exception as e:
            print(f"Không thể gửi DM cho user {discord_user_id}: {e}")
    else:
        print(f"Không tìm thấy Discord user với ID {discord_user_id}")
