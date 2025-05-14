import os
import requests
import time
from datetime import datetime
import pytz

# Konfigurasi
TIMEZONE = pytz.timezone("Asia/Jakarta")
WEBSITES = [
    {"name": "SGM", "url": "https://www.generasimaju.co.id/"},
    {"name": "NUTRICLUB", "url": "https://www.nutriclub.co.id/"},
    {"name": "BEBECLUB", "url": "https://www.bebeclub.co.id/"}
]

def send_telegram(message):
    """Kirim notifikasi ke Telegram"""
    requests.post(
        f"https://api.telegram.org/bot{os.getenv('BOT_MONITORING')}/sendMessage",
        json={
            "chat_id": os.getenv("CHAT_ID_MONITORING"),
            "text": message,
            "parse_mode": "Markdown"
        }
    )

def check_site(site):
    """Cek status website"""
    try:
        start_time = time.time()
        response = requests.get(site["url"], timeout=10)
        response_time = time.time() - start_time
        
        if response.status_code == 200:
            return f"🟢 UP | {response_time:.2f}s"
        else:
            return f"🔴 DOWN ({response.status_code}) | {response_time:.2f}s"
    except Exception as e:
        return f"⚠️ ERROR: {str(e)}"

def main():
    # Kirim notifikasi mulai monitoring
    send_telegram("🚀 **Memulai Monitoring 3 Website**\n" + 
                  "\n".join([f"- {site['name']}: `{site['url']}`" for site in WEBSITES]))
    
    last_statuses = {site["name"]: None for site in WEBSITES}

    while True:
        current_time = datetime.now(TIMEZONE).strftime("%d-%m-%Y %H:%M:%S")
        messages = []

        for site in WEBSITES:
            status = check_site(site)
            
            # Kirim notifikasi hanya jika status berubah
            if status != last_statuses[site["name"]]:
                messages.append(
                    f"**{site['name']}**\n"
                    f"URL: `{site['url']}`\n"
                    f"Status: {status}\n"
                    f"Waktu: `{current_time}`"
                )
                last_statuses[site["name"]] = status

        if messages:
            send_telegram("\n\n".join(messages))

        time.sleep(int(os.getenv("CHECK_INTERVAL", 60)))

if __name__ == "__main__":
    main()