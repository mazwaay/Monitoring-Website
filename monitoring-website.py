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
CHECK_INTERVAL = 60  # detik

def send_telegram(message):
    """Kirim notifikasi ke Telegram"""
    try:
        response = requests.post(
            f"https://api.telegram.org/bot{os.getenv('BOT_MONITORING')}/sendMessage",
            json={
                "chat_id": os.getenv("CHAT_ID_MONITORING"),
                "text": message,
                "parse_mode": "Markdown"
            },
            timeout=10
        )
        if response.status_code != 200:
            print(f"Gagal mengirim Telegram: {response.text}")
    except Exception as e:
        print(f"Error Telegram: {str(e)}")

def check_site(site):
    """Cek status website"""
    try:
        start_time = time.time()
        response = requests.get(site["url"], timeout=10)
        response_time = time.time() - start_time
        
        if response.status_code == 200:
            return {"status": "UP", "response_time": response_time}
        else:
            return {"status": "DOWN", "code": response.status_code, "response_time": response_time}
    except requests.exceptions.Timeout:
        return {"status": "ERROR", "message": "Timeout (10s)"}
    except Exception as e:
        return {"status": "ERROR", "message": str(e)}

def main():
    # Kirim notifikasi mulai monitoring
    send_telegram(
        "🚀 **Memulai Monitoring Website**\n" + 
        "\n".join([f"- {site['name']}: `{site['url']}`" for site in WEBSITES])
    )

    last_statuses = {site["name"]: None for site in WEBSITES}

    while True:
        current_time = datetime.now(TIMEZONE).strftime("%d-%m-%Y %H:%M:%S")
        
        for site in WEBSITES:
            result = check_site(site)
            current_status = result["status"]
            
            # Hanya kirim notifikasi jika status berubah
            if last_statuses[site["name"]] is not None and current_status != last_statuses[site["name"]]:
                emoji = "🟢" if current_status == "UP" else "🔴"
                
                if current_status == "UP":
                    message = (
                        f"{emoji} **{site['name']} KEMBALI NORMAL**\n"
                        f"URL: `{site['url']}`\n"
                        f"Response: {result['response_time']:.2f}s\n"
                        f"Waktu: `{current_time}`"
                    )
                elif current_status == "DOWN":
                    message = (
                        f"{emoji} **{site['name']} DOWN**\n"
                        f"URL: `{site['url']}`\n"
                        f"Status Code: {result['code']}\n"
                        f"Waktu: `{current_time}`"
                    )
                else:  # ERROR
                    message = (
                        f"⚠️ **{site['name']} ERROR**\n"
                        f"URL: `{site['url']}`\n"
                        f"Error: {result['message']}\n"
                        f"Waktu: `{current_time}`"
                    )
                
                send_telegram(message)
            
            # Update status terakhir
            last_statuses[site["name"]] = current_status

        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()