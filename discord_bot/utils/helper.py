def format_time(seconds: int) -> str:
    """Chuyển đổi giây thành định dạng thời gian."""
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    return f"{hours}h {minutes}m {seconds}s"

def check_role(member, role_name: str) -> bool:
    """Kiểm tra xem thành viên có vai trò nhất định hay không."""
    return any(role.name == role_name for role in member.roles)
