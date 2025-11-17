from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from pydantic import BaseModel
from dependencies.deps import get_db
from models.event import Event
from models.user import User
from sqlalchemy import and_
import asyncio
import aiohttp
import os

# Environment variables (already loaded in main app)
BACKEND_URL = os.getenv("BACKEND_URL")
DISCORD_BOT_URL = os.getenv("DISCORD_BOT_URL")
DEBUG_MODE = os.getenv("DEBUG_MODE", "false").lower() == "true"

router = APIRouter()

def debug_log(message: str):
    """Log debug message nếu DEBUG_MODE được bật"""
    if DEBUG_MODE:
        print(message)

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

async def get_user_info(owner_id: str, db: Session) -> Dict[str, Any]:
    """
    Hàm helper để lấy user info từ database
    owner_id là ID từ bảng users, cần lấy discord_user_id tương ứng
    """
    try:
        debug_log(f"🔍 Getting user info for owner_id: {owner_id}")
        
        # Truy vấn database trực tiếp thay vì HTTP call
        user = db.query(User).filter(User.id == int(owner_id)).first()
        
        if not user:
            debug_log(f"❌ User not found for owner_id: {owner_id}")
            return None
        
        # Lấy discord_user_id - xử lý field String(64) nullable=True
        discord_user_id_raw = user.discord_user_id
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
            "user_id": user.id,
            "discord_user_id": discord_user_id_value,
            "name": user.name,
            "email": user.email,
            "has_discord_id": discord_user_id_value is not None,
            "raw_discord_user_id": discord_user_id_raw,  # Để debug
        }
                        
    except Exception as e:
        debug_log(f"❌ Error getting user info for owner_id {owner_id}: {str(e)}")
    
    debug_log(f"❌ Could not get user info for owner_id {owner_id}")
    return None

async def send_reminder_to_discord(event, user_id=None, channel_id=None):
    """
    Gửi reminder đến Discord user hoặc channel thông qua Discord Bot API
    """
    try:
        if not DISCORD_BOT_URL:
            debug_log("❌ Discord Bot URL not configured")
            return False
            
        # Format message
        title = event.get('title') if isinstance(event, dict) else getattr(event, 'title', getattr(event, 'name', ''))
        start_time = event.get('start_time') if isinstance(event, dict) else getattr(event, 'start_time', '')
        description = event.get('description') if isinstance(event, dict) else getattr(event, 'description', None)
        msg = f"📅 **Nhắc nhở sự kiện:** {title}\n🕒 Thời gian: {start_time}\n"
        if description:
            msg += f"📝 Mô tả: {description}\n"
        
        # Gửi thông qua Discord Bot API
        target_id = user_id or channel_id
        if target_id:
            async with aiohttp.ClientSession() as session:
                endpoint = f"{DISCORD_BOT_URL}/send_message"
                payload = {
                    "senderId": str(target_id),
                    "output": msg
                }
                
                async with session.post(
                    endpoint,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=15)
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        debug_log(f"✅ Discord message sent successfully: {result}")
                        return True
                    else:
                        debug_log(f"❌ Discord API error: {response.status}")
                        return False
        
        return False
        
    except Exception as e:
        debug_log(f"❌ Error sending Discord reminder: {str(e)}")
        return False

@router.post("/send_reminder")
async def api_send_reminder(request: Request, db: Session = Depends(get_db)):
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
        
        # Lấy thông tin user từ database nếu có owner_id
        user_info = await get_user_info(owner_id, db) if owner_id else None
        debug_log(f"🔍 User info result for owner_id {owner_id}: {user_info}")
        
        # Nếu không có user_id trực tiếp nhưng có user_info, sử dụng discord_user_id
        original_user_id = user_id
        if not user_id and user_info and user_info.get('discord_user_id'):
            user_id = user_info.get('discord_user_id')
            debug_log(f"🔍 Using discord_user_id from database: '{user_id}' (was: '{original_user_id}')")
        
        debug_log(f"🔍 Final user_id for sending: '{user_id}'")
        
        # Gửi reminder
        await send_reminder_to_discord(event, user_id=user_id, channel_id=channel_id)
        
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
