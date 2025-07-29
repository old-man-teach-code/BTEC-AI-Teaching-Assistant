from sqlalchemy.orm import Session

def seed_data(db: Session):
    """
    Seed dữ liệu mặc định cho database

    Args:
        db: Database session
    """
    # Hiện tại không có dữ liệu mặc định nào cần seed
    # Event types giờ là string tự do, không cần seed

    print("Seeding data completed successfully!")

    # Thêm các loại seed data khác ở đây nếu cần