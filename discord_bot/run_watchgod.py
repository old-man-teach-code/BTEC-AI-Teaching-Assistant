from watchgod import run_process
import signal
import sys
import os

def run_bot():
    # Đảm bảo kill process con cũ trước khi chạy mới
    if sys.platform == "win32":
        os.system('taskkill /F /IM python.exe /T >nul 2>&1')
    else:
        os.system('pkill -f bot.py')
    os.system('python bot.py')

if __name__ == "__main__":
    run_process('.', run_bot)