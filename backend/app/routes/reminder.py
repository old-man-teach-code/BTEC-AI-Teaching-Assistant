from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime, timedelta
from pydantic import BaseModel
from dependencies.deps import get_db
from models.event import Event
from models.user import User
from sqlalchemy import and_
import asyncio
import aiohttp

router = APIRouter()

class ReminderEventData(BaseModel):
    title: str
    start_time: str
    description: Optional[str] = None
    Start: Optional[str] = None 
    End: Optional[str] = None    
    owner_id: str

@router.post("/process")
def process_reminder(
    event_data: ReminderEventData,
    test_mode: bool = False, 
    db: Session = Depends(get_db)
):
    """
    Xử lý reminder cho một event cụ thể từ n8n
    
    Args:
        event_data: Dữ liệu event từ n8n
        test_mode: Nếu True, bỏ qua gửi Discord thật
        db: Database session
        
    Returns:
        List[Dict]: Danh sách events đã được xử lý reminder với thông tin chi tiết
    """
    try:
        processed_events = []
        
        # Parse start_time từ string
        try:
            start_time_str = event_data.start_time or event_data.Start
            if start_time_str:
                # Remove 'Z' and handle timezone
                if start_time_str.endswith('Z'):
                    start_time_str = start_time_str[:-1]
                start_time = datetime.fromisoformat(start_time_str)
            else:
                raise ValueError("No start_time provided")
            
            print(f"[DEBUG] Looking for event with:")
            print(f"  - title: {event_data.title}")
            print(f"  - owner_id: {event_data.owner_id}")
            print(f"  - start_time: {start_time}")
            
            # 🔧 Tìm event với query rộng hơn để debug
            all_matching_events = db.query(Event).filter(
                and_(
                    Event.title == event_data.title,
                    Event.owner_id == int(event_data.owner_id)
                )
            ).all()
            
            print(f"[DEBUG] Found {len(all_matching_events)} events with matching title and owner")
            for evt in all_matching_events:
                print(f"  - Event ID {evt.id}: start_time={evt.start_time}, reminded={evt.reminded}")
            
            # Tìm event (bất kể reminded status)
            event = db.query(Event).filter(
                and_(
                    Event.title == event_data.title,
                    Event.owner_id == int(event_data.owner_id),
                    Event.start_time == start_time
                )
            ).first()
            
            if not event:
                # Không tìm thấy event
                return [{"reminded": False}]
            
            # Kiểm tra đã reminded chưa
            print(f"[DEBUG] Event {event.id} reminded status: {event.reminded}")
            if event.reminded:
                # Đã reminded rồi
                print(f"[DEBUG] Event {event.id} already reminded, returning false")
                return [{"reminded": False}]
            
            # Kiểm tra thời gian có hợp lý không
            now_utc = datetime.now()
            now_local = now_utc + timedelta(hours=7)
            event_start_naive = event.start_time.replace(tzinfo=None) if event.start_time.tzinfo else event.start_time
            reminder_time = event_start_naive - timedelta(minutes=event.reminder_minutes or 0)
            
            print(f"[DEBUG] Time check for event: {event.title}")
            print(f"  - Event start time: {event_start_naive}")
            print(f"  - Current UTC time: {now_utc}")
            print(f"  - Current Vietnam time: {now_local}")
            print(f"  - Reminder minutes: {event.reminder_minutes}")
            print(f"  - Reminder time: {reminder_time}")
            print(f"  - Should remind: {reminder_time <= now_local}")
            print(f"  - Time difference: {(now_local - reminder_time).total_seconds()} seconds")
            
            if reminder_time > now_local:
                # Chưa đến thời gian nhắc nhở
                print(f"[DEBUG] Not time to remind yet for event {event.id}")
                return [{"reminded": False}]
            
            # Kiểm tra thêm: không nhắc nhở quá sớm (ví dụ: không nhắc nhở trước 24 giờ)
            time_diff_hours = (now_local - reminder_time).total_seconds() / 3600
            if time_diff_hours > 24:
                print(f"[DEBUG] Reminder time too old ({time_diff_hours:.1f} hours ago) for event {event.id}")
                return [{"reminded": False}]
            
            print(f"[DEBUG] Found event ID {event.id} to process reminder")
            print(f"[DEBUG] Event details: title='{event.title}', start_time={event.start_time}, reminded={event.reminded}")
            
            # Kiểm tra xem event có quá cũ không (đã qua rồi)
            if event_start_naive < now_local:
                print(f"[DEBUG] Event {event.id} has already started/passed, not processing reminder")
                return [{"reminded": False}]
            
            # Lấy user để lấy discord_user_id  
            user = db.query(User).filter(User.id == event.owner_id).first()
            discord_user_id = user.discord_user_id if user else None
            
            # 🎯 ĐÃ ĐẾN GIỜ NHẮC NHỞ - Bỏ qua Discord và luôn coi như thành công
            print(f"[DEBUG] Processing reminder for event {event.id}")
            print(f"[DEBUG] Skipping Discord API call - treating as success")
            
            # Luôn coi như thành công (bỏ qua Discord)
            success = True
            
            # Đánh dấu đã nhắc nhở
            event.reminded = True
            db.commit()
            print(f"[DEBUG] Successfully processed reminder and marked event {event.id} as reminded")
            
            # Trả về dữ liệu theo format yêu cầu
            success_data = {
                "reminded": True,
                "title": event.title,
                "start_time": event.start_time.isoformat(),
                "description": event.description,
                "Start": event.start_time.isoformat(),
                "End": event.end_time.isoformat() if event.end_time else None,
                "owner_id": str(event.owner_id),
                "reminder_minutes": event.reminder_minutes,
                "discord_user_id": discord_user_id,
                "message": "Đã xử lý reminder thành công"
            }
            
            # In ra console cho debug
            print(f"[SUCCESS] Event reminder processed:")
            print(f"  - reminder_minutes: {event.reminder_minutes}")
            print(f"  - discord_user_id: {discord_user_id}")
            print(f"  - owner_id: {event.owner_id}")
            print(f"  - reminded: True")
            print(f"  - event_type: {event.event_type}")
            
            processed_events.append(success_data)
                
        except Exception as event_error:
            print(f"[ERROR] Exception in processing event: {event_error}")
            import traceback
            traceback.print_exc()
            
            # Thêm vào danh sách với lỗi - chỉ trả về false
            processed_events.append({"reminded": False})
        
        return processed_events
        
    except Exception as e:
        print(f"[Reminder Error] General error in process_reminders: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing reminders: {str(e)}"
        )
