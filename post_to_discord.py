#!/usr/bin/env python3
import sys
import os
import asyncio
from datetime import datetime, time
import pytz
from dotenv import load_dotenv
import subprocess
import logging
import discord
from discord.ext import commands, tasks
import glob

# Grundlegende Logging-Konfiguration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Erstelle Logger für dieses Modul
logger = logging.getLogger()

# Füge den Python-Pfad hinzu
sys.path.append('/usr/local/lib/python3.9/site-packages')

# Lade Umgebungsvariablen
env_file = '/app/.env'
if not os.path.exists(env_file):
    logger.error(f"Fehler: .env Datei nicht gefunden unter {env_file}")
    sys.exit(1)

load_dotenv(env_file)

# Hole die Umgebungsvariablen
DISCORD_BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')
DISCORD_TIMELAPSE_CHANNEL_ID = os.getenv('DISCORD_TIMELAPSE_CHANNEL_ID')
DISCORD_DAILY_CHANNEL_ID = os.getenv('DISCORD_DAILY_CHANNEL_ID')
DISCORD_GUILD_IDS = os.getenv('DISCORD_GUILD_IDS', '').split(',')  # Komma-separierte Liste von Guild IDs

# Überprüfe, ob alle erforderlichen Umgebungsvariablen vorhanden sind
if not DISCORD_BOT_TOKEN:
    logger.error("Fehler: DISCORD_BOT_TOKEN nicht gesetzt")
    sys.exit(1)
if not DISCORD_TIMELAPSE_CHANNEL_ID:
    logger.error("Fehler: DISCORD_TIMELAPSE_CHANNEL_ID nicht gesetzt")
    sys.exit(1)
if not DISCORD_DAILY_CHANNEL_ID:
    logger.error("Fehler: DISCORD_DAILY_CHANNEL_ID nicht gesetzt")
    sys.exit(1)
if not DISCORD_GUILD_IDS:
    logger.error("Fehler: DISCORD_GUILD_IDS nicht gesetzt")
    sys.exit(1)

# Konvertiere Guild IDs zu Integers
try:
    DISCORD_GUILD_IDS = [int(guild_id.strip()) for guild_id in DISCORD_GUILD_IDS if guild_id.strip()]
except ValueError as e:
    logger.error(f"Fehler: Ungültige Guild ID in DISCORD_GUILD_IDS: {str(e)}")
    sys.exit(1)

logger.info(f"Bot Token: {'*' * len(DISCORD_BOT_TOKEN)}")
logger.info(f"Timelapse Channel ID: {DISCORD_TIMELAPSE_CHANNEL_ID}")
logger.info(f"Daily Channel ID: {DISCORD_DAILY_CHANNEL_ID}")
logger.info(f"Guild IDs: {DISCORD_GUILD_IDS}")

# Erstelle den Bot mit den intents
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Füge die guild_ids als Attribut zum Bot hinzu
bot.guild_ids = DISCORD_GUILD_IDS

@bot.event
async def on_ready():
    logger.info(f'Bot ist eingeloggt als {bot.user.name}')
    try:
        # Warte kurz, damit die Cogs vollständig geladen sind
        await asyncio.sleep(1)
        
        # Entferne zuerst alle bestehenden Commands
        bot.tree.clear_commands(guild=None)
        logger.info("Alle bestehenden Commands wurden entfernt")
        
        # Synchronisiere zuerst für die spezifischen Guilds
        for guild_id in DISCORD_GUILD_IDS:
            try:
                # Entferne die Commands für diese Guild
                bot.tree.clear_commands(guild=discord.Object(id=guild_id))
                
                # Synchronisiere die Commands für diese Guild
                synced = await bot.tree.sync(guild=discord.Object(id=guild_id))
                logger.info(f"Synchronisierte {len(synced)} Commands für Guild {guild_id}")
                
                # Debug: Zeige die synchronisierten Commands
                for cmd in synced:
                    logger.info(f"- {cmd.name} (Guild {guild_id})")
            except Exception as e:
                logger.error(f"Fehler beim Synchronisieren der Commands für Guild {guild_id}: {e}")
        
        # Dann synchronisiere global
        try:
            synced = await bot.tree.sync()
            logger.info(f"Synchronisierte {len(synced)} Commands global")
            
            # Debug: Zeige die synchronisierten Commands
            for cmd in synced:
                logger.info(f"- {cmd.name}")
        except Exception as e:
            logger.error(f"Fehler beim globalen Synchronisieren der Commands: {e}")
    except Exception as e:
        logger.error(f"Fehler beim Synchronisieren der Befehle: {e}")

    # Starte die Tasks
    change_status.start()
    check_daily_post.start()

async def load_cogs():
    cogs_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cogs')
    if not os.path.exists(cogs_dir):
        logger.error(f"FEHLER: Verzeichnis {cogs_dir} existiert nicht!")
        return

    for filename in os.listdir(cogs_dir):
        if filename.endswith('.py') and not filename.startswith('__'):
            try:
                # Lade die Cog
                await bot.load_extension(f'cogs.{filename[:-3]}')
                logger.info(f"Erfolgreich geladen: cogs.{filename[:-3]}")
                
                # Warte kurz, damit die Commands registriert werden können
                await asyncio.sleep(0.5)
            except Exception as e:
                logger.error(f"Fehler beim Laden von cogs.{filename[:-3]}: {str(e)}")
                logger.error(f"Details: {e.__class__.__name__}: {str(e)}")

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
                logger.warning("Keine Screenshots für Daily Post gefunden")
                return

            latest_file = max(list_of_files, key=os.path.getctime)
            current_time_str = datetime.now(berlin_tz).strftime("%Y-%m-%d %H:%M:%S")
            message = f"Daily Weed Picture: {current_time_str}"
            
            # Verkleinere das Bild, falls nötig
            resized_file = resize_image(latest_file)
            if not resized_file:
                logger.error("Fehler beim Verkleinern des Bildes für Daily Post")
                return
            
            # Sende das Bild in den Daily Channel
            channel = bot.get_channel(int(DISCORD_DAILY_CHANNEL_ID))
            if channel:
                with open(resized_file, 'rb') as f:
                    await channel.send(content=message, file=discord.File(f))
                logger.info(f"Daily Post erfolgreich gesendet: {resized_file}")
                
                # Lösche die temporäre Datei, falls eine erstellt wurde
                if resized_file != latest_file:
                    os.remove(resized_file)
        except Exception as e:
            logger.error(f"Fehler beim Senden des Daily Posts: {str(e)}")

def resize_image(input_file):
    """Verkleinert ein Bild, falls es größer als 10MB ist"""
    max_size_mb = 10
    size_mb = int(subprocess.check_output(['du', '-m', input_file]).split()[0].decode('utf-8'))
    
    if size_mb > max_size_mb:
        logger.info(f"Bild ist zu groß ({size_mb} MB), verkleinere es...")
        # Behalte die ursprüngliche Dateiendung bei
        file_ext = os.path.splitext(input_file)[1]
        temp_file = f"{os.path.splitext(input_file)[0]}_resized{file_ext}"
        
        # Verkleinere das Bild mit ffmpeg
        subprocess.run([
            'ffmpeg', '-y',
            '-i', input_file,
            '-frames:v', '1',
            '-update', '1',
            '-vf', "scale='min(1920,iw)':'min(1080,ih)':force_original_aspect_ratio=decrease",
            '-compression_level', '9',
            temp_file
        ], check=True)
        
        if os.path.exists(temp_file) and os.path.getsize(temp_file) > 0:
            return temp_file
        else:
            logger.error("Fehler beim Verkleinern des Bildes")
            return None
    return input_file

async def main():
    # Lade zuerst die Cogs
    await load_cogs()
    
    # Starte den Bot
    await bot.start(DISCORD_BOT_TOKEN)

# Wenn das Skript direkt ausgeführt wird (nicht als Modul)
if __name__ == "__main__":
    # Wenn Argumente übergeben wurden, handelt es sich um einen direkten Aufruf zum Senden eines Bildes
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        message = sys.argv[2] if len(sys.argv) > 2 else f"Screenshot vom {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

        if not os.path.exists(file_path):
            logger.error(f"Fehler: Datei {file_path} existiert nicht")
            sys.exit(1)

        # Verkleinere das Bild, falls nötig
        resized_file = resize_image(file_path)
        if not resized_file:
            logger.error("Fehler beim Verkleinern des Bildes")
            sys.exit(1)

        # Erstelle einen temporären Client für den direkten Aufruf
        client = discord.Client(intents=discord.Intents.default())

        @client.event
        async def on_ready():
            try:
                channel = client.get_channel(int(DISCORD_TIMELAPSE_CHANNEL_ID))
                if not channel:
                    logger.error(f"Fehler: Kanal mit ID {DISCORD_TIMELAPSE_CHANNEL_ID} nicht gefunden")
                    await client.close()
                    return

                with open(resized_file, 'rb') as f:
                    await channel.send(content=message, file=discord.File(f))
                logger.info(f"Erfolgreich an Discord gesendet: {resized_file}")
                
                # Lösche die temporäre Datei, falls eine erstellt wurde
                if resized_file != file_path:
                    os.remove(resized_file)
            except Exception as e:
                logger.error(f"Fehler beim Senden an Discord: {str(e)}")
            finally:
                await client.close()

        client.run(DISCORD_BOT_TOKEN)
    else:
        # Starte den Bot für Befehle und automatische Posts
        asyncio.run(main())