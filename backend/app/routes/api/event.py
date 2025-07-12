from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from dependencies.deps import get_db
from models.event import Event
from models.user import User

router = APIRouter()

@router.get("/today")
def get_today_events(db: Session = Depends(get_db)):
    now = datetime.utcnow()
    start = datetime(now.year, now.month, now.day)
    end = start + timedelta(days=15)
    events = db.query(Event).filter(Event.reminder_time >= start, Event.reminder_time < end).all()
    return [
        {
            "id": e.id,
            "title": e.title,
            "description": e.description,
            "reminder_time": e.reminder_time.isoformat(),
            "user_id": e.user_id,
            "discord_user_id": db.query(User).filter(User.id == e.user_id).first().discord_user_id
        }
        for e in events
    ]
