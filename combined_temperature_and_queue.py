import psutil
import platform
import json
from datetime import datetime
from azure.storage.queue import QueueClient
import os
from dotenv import load_dotenv

# Ladda miljövariabler från .env-filen
load_dotenv()

# Hämta variabler från miljövariabler
AQ_CONNECTION_STRING = os.getenv("AQ_CONNECTION_STRING")
DB_USERNAME = os.getenv("DB_USERNAME")

# Azure Queue Storage anslutningsinformation
connection_string = AQ_CONNECTION_STRING
queue_name = DB_USERNAME

# Skapa anslutning till Queue Storage
queue_client = QueueClient.from_connection_string(connection_string, queue_name)

def get_system_info():
    # Hämta systeminformation
    cpu_usage = psutil.cpu_percent()
    memory_usage = psutil.virtual_memory().percent
    disk_usage = psutil.disk_usage('/').percent
    os_info = platform.system() + " " + platform.release()
    
    # Hämta batteriinformation om tillgänglig
    battery = psutil.sensors_battery()
    battery_info = f"{battery.percent}% {'Charging' if battery.power_plugged else 'Discharging'}" if battery else "N/A"

    # Skapa data dictionary
    data = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "os": os_info,
        "cpu_usage": cpu_usage,
        "memory_usage": memory_usage,
        "disk_usage": disk_usage,
        "battery": battery_info
    }
    
    return data

def send_to_queue(data):
    # Konvertera data till JSON-sträng
    message = json.dumps(data)
    
    # Skicka meddelandet till kön
    queue_client.send_message(message)
    print(f"Meddelande skickat till kön: {message}")

if __name__ == "__main__":
    system_info = get_system_info()
    send_to_queue(system_info)
