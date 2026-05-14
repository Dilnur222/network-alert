import json
import time
import subprocess
import requests
import platform
from datetime import datetime

TOKEN = "ВАШ_TELEGRAM_TOKEN"
CHAT_ID = "ВАШ_CHAT_ID"
CHECK_INTERVAL = 300   # 5 минут (можно поменять на 5-10 секунд для демонстрации)
LOG_FILE = "alerts.log"

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
    try:
        with open("devices.json", "r", encoding="utf-8") as f:
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
