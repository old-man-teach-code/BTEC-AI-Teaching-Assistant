from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()

class NotifyDiscordRequest(BaseModel):
    discord_user_id: str
    title: str
    reminder_time: str
    description: str = ""

@router.post("/notify")
def notify_discord(req: NotifyDiscordRequest):
    print(f"[Notify Discord] To {req.discord_user_id}: {req.title} at {req.reminder_time} - {req.description}")
    return {"success": True}
