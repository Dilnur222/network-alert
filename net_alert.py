import json
import time
import subprocess
import requests
import platform
import os
import sys
from datetime import datetime
from dotenv import load_dotenv

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))

TOKEN = os.getenv("TELEGRAM_TOKEN", "ВАШ_TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "ВАШ_CHAT_ID")
CHECK_INTERVAL = 5   # 5 секунд для быстрой демонстрации
LOG_FILE = os.path.join(BASE_DIR, "alerts.log")

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": message}
    try:
        requests.post(url, data=data)
    except Exception as e:
        print(f"Ошибка при отправке в Telegram: {e}")

def ping(ip):
    # Определяем параметр для команды ping в зависимости от ОС 
    # (В Windows используется -n, а в Linux/Mac -c)
    param = "-n" if platform.system().lower() == "windows" else "-c"
    
    result = subprocess.run(
        ["ping", param, "1", ip],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    return result.returncode == 0

def log_event(text):
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} — {text}\n")

def load_devices():
    devices_path = os.path.join(BASE_DIR, "devices.json")
    try:
        with open(devices_path, "r", encoding="utf-8") as f:
            return json.load(f)["devices"]
    except FileNotFoundError:
        print("Файл devices.json не найден!")
        return []
    except json.JSONDecodeError:
        print("Ошибка чтения файла devices.json. Проверьте формат.")
        return []

def main():
    devices = load_devices()
    if not devices:
        return

    print("Запуск системы мониторинга...")
    if TOKEN == "ВАШ_TELEGRAM_TOKEN" or CHAT_ID == "ВАШ_CHAT_ID":
         print("⚠️ ВНИМАНИЕ: Не настроены TOKEN и CHAT_ID. Сообщения в Telegram отправляться не будут!\n")
    
    while True:
        for d in devices:
            name = d["name"]
            ip = d["ip"]

            if not ping(ip):
                msg = f"⚠️ ALERT: {name} ({ip}) недоступен!"
                print(msg)
                log_event(msg)
                
                # Отправляем сообщение в Telegram только если токены заполнены
                if TOKEN != "ВАШ_TELEGRAM_TOKEN" and CHAT_ID != "ВАШ_CHAT_ID":
                    send_telegram(msg)
            else:
                print(f"✅ {name} ({ip}) доступен")

        print("-" * 30)
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()
