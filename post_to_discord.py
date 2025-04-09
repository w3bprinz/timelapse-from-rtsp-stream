#!/usr/bin/env python3
import discord
from discord.ext import commands
from datetime import datetime
import pytz
import os
import sys
from dotenv import load_dotenv

# Lade Umgebungsvariablen
load_dotenv('/app/.env')

# Discord Konfiguration aus Umgebungsvariablen
CHANNEL_ID = int(os.getenv('DISCORD_CHANNEL_ID'))
BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')

# Erstelle die intents und aktiviere den Nachrichteninhalt-Intent
intents = discord.Intents.default()
intents.message_content = True

# Erstelle den Bot mit den intents
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    
    # Hole die Datei, die gesendet werden soll
    file_path = sys.argv[1] if len(sys.argv) > 1 else None
    if not file_path or not os.path.exists(file_path):
        print(f'Datei nicht gefunden: {file_path}')
        await bot.close()
        return

    # Erstelle den Nachrichtentext mit dem aktuellen Datum
    tz = pytz.timezone('Europe/Berlin')
    now = datetime.now(tz)
    date_string = now.strftime('%Y-%m-%d %H:%M:%S %Z')
    
    # Bestimme den Nachrichtentext basierend auf der Dateiendung
    if file_path.endswith('.mp4'):
        message_content = f'Timelapse Video vom {date_string}'
    else:
        message_content = f'Screenshot vom {date_string}'

    channel = bot.get_channel(CHANNEL_ID)
    if channel is None:
        print(f'Channel mit ID {CHANNEL_ID} nicht gefunden.')
    else:
        try:
            await channel.send(content=message_content, file=discord.File(file_path))
            print('Nachricht erfolgreich gesendet.')
        except discord.errors.Forbidden as e:
            print(f'Fehler beim Senden der Nachricht: {e}')
    
    await bot.close()

bot.run(BOT_TOKEN)