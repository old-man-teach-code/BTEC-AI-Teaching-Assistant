from sqlalchemy.orm import Session
from sqlalchemy import text


def reset_auto_increment(db: Session, table_name: str) -> None:
    """
    Reset auto-increment counter cho bảng để ID tiếp theo bắt đầu từ ID cao nhất hiện có + 1
    
    Hàm này sẽ tìm giá trị ID lớn nhất trong bảng và reset auto-increment để ID tiếp theo
    bắt đầu từ giá trị đó + 1. Nếu bảng không có records nào, auto-increment sẽ được reset về 1.
    
    Args:
        db: Database session
        table_name: Tên bảng cần reset auto-increment
    """
    try:
        # Lấy giá trị ID lớn nhất hiện có
        result = db.execute(text(f"SELECT MAX(id) as max_id FROM {table_name}"))
        max_id = result.fetchone()[0]
        
        # Nếu không có records nào, reset về 1
        if max_id is None:
            max_id = 0
        
        # Reset auto-increment
        db.execute(text(f"ALTER TABLE {table_name} AUTO_INCREMENT = {max_id + 1}"))
        db.commit()
    except Exception as e:
        print(f"Error resetting auto-increment for table {table_name}: {str(e)}")
        db.rollback() 