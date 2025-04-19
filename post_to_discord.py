#!/usr/bin/env python3
import sys
import os
import asyncio
from datetime import datetime, time
import pytz
from dotenv import load_dotenv

# Füge den Python-Pfad hinzu
sys.path.append('/usr/local/lib/python3.9/site-packages')

import discord
from discord.ext import commands, tasks
import glob
import os

# Lade Umgebungsvariablen
env_file = '/app/.env'
if not os.path.exists(env_file):
    print(f"Fehler: .env Datei nicht gefunden unter {env_file}")
    sys.exit(1)

load_dotenv(env_file)

# Hole die Umgebungsvariablen
DISCORD_BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')
DISCORD_CHANNEL_ID = os.getenv('DISCORD_CHANNEL_ID')
DISCORD_DAILY_CHANNEL_ID = os.getenv('DISCORD_DAILY_CHANNEL_ID')

# Überprüfe, ob alle erforderlichen Umgebungsvariablen vorhanden sind
if not DISCORD_BOT_TOKEN:
    print("Fehler: DISCORD_BOT_TOKEN nicht gesetzt")
    sys.exit(1)
if not DISCORD_CHANNEL_ID:
    print("Fehler: DISCORD_CHANNEL_ID nicht gesetzt")
    sys.exit(1)
if not DISCORD_DAILY_CHANNEL_ID:
    print("Fehler: DISCORD_DAILY_CHANNEL_ID nicht gesetzt")
    sys.exit(1)

print(f"Bot Token: {'*' * len(DISCORD_BOT_TOKEN)}")
print(f"Channel ID: {DISCORD_CHANNEL_ID}")
print(f"Daily Channel ID: {DISCORD_DAILY_CHANNEL_ID}")

# Erstelle den Bot mit den intents
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Status-Rotation
status_messages = [
    "🌱 Pflanzenwachstum überwachen",
    "📸 Screenshots aufnehmen",
    "⏱️ Timelapse erstellen",
    "🌿 Daily Weed Pictures",
    "📊 Wachstumsstatistiken"
]

@tasks.loop(seconds=30)
async def change_status():
    """Ändert den Bot-Status alle 30 Sekunden"""
    current_status = status_messages.pop(0)
    status_messages.append(current_status)
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=current_status))

@tasks.loop(seconds=60)
async def check_daily_post():
    """Überprüft jede Minute, ob es Zeit für einen Daily Post ist"""
    berlin_tz = pytz.timezone('Europe/Berlin')
    current_time = datetime.now(berlin_tz).time()
    
    # Definiere die Zeiten für die Daily Posts
    post_times = [time(8, 0), time(20, 0)]
    
    if current_time in post_times:
        try:
            # Finde das neueste Bild
            screenshot_dir = "/app/screenshots"
            list_of_files = glob.glob(f"{screenshot_dir}/screenshot_*.png")
            if not list_of_files:
                print("Keine Screenshots für Daily Post gefunden")
                return

            latest_file = max(list_of_files, key=os.path.getctime)
            current_time_str = datetime.now(berlin_tz).strftime("%Y-%m-%d %H:%M:%S")
            message = f"Daily Weed Picture: {current_time_str}"
            
            # Sende das Bild in den Daily Channel
            channel = bot.get_channel(int(DISCORD_DAILY_CHANNEL_ID))
            if channel:
                with open(latest_file, 'rb') as f:
                    await channel.send(content=message, file=discord.File(f))
                print(f"Daily Post erfolgreich gesendet: {latest_file}")
        except Exception as e:
            print(f"Fehler beim Senden des Daily Posts: {str(e)}")

@bot.command(name='last')
async def last_image(ctx):
    """Sendet das letzte aufgenommene Bild in den Kanal"""
    try:
        # Finde das neueste Bild im Screenshot-Verzeichnis
        screenshot_dir = "/app/screenshots"
        list_of_files = glob.glob(f"{screenshot_dir}/screenshot_*.png")
        if not list_of_files:
            await ctx.send("Keine Screenshots gefunden.")
            return

        latest_file = max(list_of_files, key=os.path.getctime)
        
        # Sende das Bild
        with open(latest_file, 'rb') as f:
            await ctx.send(file=discord.File(f))
        print(f"Letztes Bild erfolgreich an Discord gesendet: {latest_file}")
    except Exception as e:
        await ctx.send(f"Fehler beim Senden des Bildes: {str(e)}")
        print(f"Fehler beim Senden des letzten Bildes: {str(e)}")

@bot.event
async def on_ready():
    print(f'Bot ist eingeloggt als {bot.user.name}')
    # Starte die Status-Rotation und den Daily Post Check
    change_status.start()
    check_daily_post.start()

# Wenn das Skript direkt ausgeführt wird (nicht als Modul)
if __name__ == "__main__":
    # Wenn Argumente übergeben wurden, handelt es sich um einen direkten Aufruf zum Senden eines Bildes
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        message = sys.argv[2] if len(sys.argv) > 2 else f"Screenshot vom {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

        if not os.path.exists(file_path):
            print(f"Fehler: Datei {file_path} existiert nicht")
            sys.exit(1)

        # Erstelle einen temporären Client für den direkten Aufruf
        client = discord.Client(intents=discord.Intents.default())

        @client.event
        async def on_ready():
            try:
                channel = client.get_channel(int(DISCORD_CHANNEL_ID))
                if not channel:
                    print(f"Fehler: Kanal mit ID {DISCORD_CHANNEL_ID} nicht gefunden")
                    await client.close()
                    return

                with open(file_path, 'rb') as f:
                    await channel.send(content=message, file=discord.File(f))
                print(f"Erfolgreich an Discord gesendet: {file_path}")
            except Exception as e:
                print(f"Fehler beim Senden an Discord: {str(e)}")
            finally:
                await client.close()

        client.run(DISCORD_BOT_TOKEN)
    else:
        # Starte den Bot für Befehle und automatische Posts
        bot.run(DISCORD_BOT_TOKEN)