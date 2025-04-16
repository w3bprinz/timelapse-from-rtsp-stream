#!/usr/bin/env python3
import discord
from discord.ext import commands
from datetime import datetime
import pytz
import os
import sys
from dotenv import load_dotenv

# Lade Umgebungsvariablen
env_file = os.getenv('DISCORD_ENV', '/app/.env')
load_dotenv(env_file)

# Hole die Umgebungsvariablen
DISCORD_BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')
DISCORD_CHANNEL_ID = os.getenv('DISCORD_CHANNEL_ID')

# Überprüfe, ob alle erforderlichen Umgebungsvariablen vorhanden sind
if not DISCORD_BOT_TOKEN or not DISCORD_CHANNEL_ID:
    print("Fehler: DISCORD_BOT_TOKEN oder DISCORD_CHANNEL_ID nicht gesetzt")
    sys.exit(1)

# Hole den Dateipfad und die Nachricht aus den Kommandozeilenargumenten
if len(sys.argv) < 2:
    print("Fehler: Kein Dateipfad angegeben")
    sys.exit(1)

file_path = sys.argv[1]
message = sys.argv[2] if len(sys.argv) > 2 else f"Screenshot vom {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

# Überprüfe, ob die Datei existiert
if not os.path.exists(file_path):
    print(f"Fehler: Datei {file_path} existiert nicht")
    sys.exit(1)

# Erstelle den Discord Client
client = discord.Client(intents=discord.Intents.default())

@client.event
async def on_ready():
    try:
        # Hole den Kanal
        channel = client.get_channel(int(DISCORD_CHANNEL_ID))
        if not channel:
            print(f"Fehler: Kanal mit ID {DISCORD_CHANNEL_ID} nicht gefunden")
            await client.close()
            return

        # Sende die Nachricht und die Datei
        with open(file_path, 'rb') as f:
            await channel.send(content=message, file=discord.File(f))
        print(f"Erfolgreich an Discord gesendet: {file_path}")
    except Exception as e:
        print(f"Fehler beim Senden an Discord: {str(e)}")
    finally:
        await client.close()

# Starte den Client
client.run(DISCORD_BOT_TOKEN)