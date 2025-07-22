from sqlalchemy.orm import Session
from models.event_type import EventType
from crud.event_type import seed_default_event_types

def seed_data(db: Session):
    """
    Seed dữ liệu mặc định cho database
    
    Args:
        db: Database session
    """
    # Seed event types mặc định
    seed_default_event_types(db)
    
    print("Seeding data completed successfully!")
    
    # Thêm các loại seed data khác ở đây nếu cần 