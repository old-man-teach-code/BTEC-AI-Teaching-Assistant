import datetime
from sqlalchemy.orm import Session
from models.event import Event  # Giả sử đã có model Event
from models.user import User
from core.config import settings

def check_reminders(db: Session):
    """
    Kiểm tra các sự kiện sắp đến hạn nhắc nhở và gửi thông báo.
    """
    now = datetime.datetime.utcnow()
    in_15_min = now + datetime.timedelta(minutes=15)
    events = db.query(Event).filter(
        Event.reminder_time >= now,
        Event.reminder_time <= in_15_min,
        Event.reminded == False
    ).all()
    for event in events:
        user = db.query(User).filter(User.id == event.user_id).first()
        print(f"[Reminder] Event '{event.title}' for user {user.email} at {event.reminder_time}")
        event.reminded = True
        db.add(event)
    db.commit()
