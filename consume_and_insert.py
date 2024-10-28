#Används inte längre!!

import json
import os
from azure.storage.queue import QueueClient
import pyodbc
from datetime import datetime
from dotenv import load_dotenv

# Ladda miljövariabler från .env-filen
load_dotenv()

# Hämta variabler från miljövariabler (os.getenv)
AQ_CONNECTION_STRING = os.getenv("AQ_CONNECTION_STRING")
DB_USERNAME = os.getenv("DB_USERNAME")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_USER_NAME = os.getenv("DB_USER_NAME")
SERVER_NAME = os.getenv("SERVER_NAME")
DRIVER_S = os.getenv("DRIVER_S")

# Azure Queue Storage anslutningsinformation
connection_string = AQ_CONNECTION_STRING
queue_name = DB_USERNAME  # Ersätt med ditt faktiska könamn

# Azure SQL Database anslutningsinformation
server = SERVER_NAME
database = DB_USER_NAME
username = DB_USERNAME  # Använd variabeln från .env-filen
password = DB_PASSWORD
driver = DRIVER_S

# Skapa anslutning till Queue Storage
queue_client = QueueClient.from_connection_string(connection_string, queue_name)

# Skapa anslutning till SQL Database
conn_str = f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}'
conn = pyodbc.connect(conn_str)
cursor = conn.cursor()

# Hämta meddelanden från kön
messages = queue_client.receive_messages()

for message in messages:
    # Extrahera JSON-data från meddelandet
    data = json.loads(message.content)
    
    # Extrahera värden från JSON-data
    timestamp = datetime.strptime(data['timestamp'], "%Y-%m-%d %H:%M:%S")
    os_info = data['os']
    cpu_usage = data['cpu_usage']
    memory_usage = data['memory_usage']
    disk_usage = data['disk_usage']
    battery = data['battery']
    
    # Infoga data i databasen
    cursor.execute("""
    INSERT INTO SystemInfo (timestamp, os, cpu_usage, memory_usage, disk_usage, battery)
    VALUES (?, ?, ?, ?, ?, ?)
    """, timestamp, os_info, cpu_usage, memory_usage, disk_usage, battery)
    
    # Ta bort meddelandet från kön efter att det har bearbetats
    queue_client.delete_message(message)

# Commit ändringar och stäng anslutningar
conn.commit()
cursor.close()
conn.close()

#skriptet lyckades föra över data från json in i min sql data tabell på försök nr.2, den körs var 10onde sekund o försöker skicka data från kön!!!