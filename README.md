# Timelapse from RTSP Stream

Ein Docker-basiertes System zur Erstellung von Timelapse-Videos aus einem RTSP-Stream mit automatischer Veröffentlichung in Discord.

## Features

- Automatische Screenshots in regelmäßigen Abständen
- Erstellung von Timelapse-Videos
- Automatische Veröffentlichung in Discord
- Spezielle Posts um 8:00 und 20:00 Uhr
- Discord-Bot mit Befehlen und Status-Rotation
- Automatische Bildverkleinerung für Discord

## Voraussetzungen

- Docker
- RTSP-Stream URL
- Discord Bot Token
- Discord Channel IDs

## Installation

1. Klone das Repository:

```bash
git clone https://github.com/w3bprinz/timelapse-from-rtsp-stream.git
cd timelapse-from-rtsp-stream
```

2. Erstelle eine `.env` Datei basierend auf `.env.example`:

```bash
cp .env.example .env
```

3. Bearbeite die `.env` Datei mit deinen Einstellungen:

```env
# RTSP Stream URL
RTSP_URL=rtsp://your-stream-url

# Discord Konfiguration
DISCORD_BOT_TOKEN=your_bot_token
DISCORD_CHANNEL_ID=your_channel_id
DISCORD_DAILY_CHANNEL_ID=your_daily_channel_id

# Verzeichnisse
SCREENSHOT_DIR=/app/screenshots
TIMELAPSE_DIR=/app/timelapse

# Video Einstellungen
MAX_VIDEO_SIZE_MB=50
```

4. Starte den Container:

```bash
docker build -t timelapse-rtsp .
docker run -d --name timelapse-rtsp -v $(pwd)/.env:/app/.env timelapse-rtsp
```

## Discord Bot Befehle

Der Bot unterstützt folgende Befehle:

- `!last` - Sendet das letzte aufgenommene Bild in den Kanal

Der Bot zeigt auch einen rotierenden Status mit folgenden Meldungen:

- 🌱 Pflanzenwachstum überwachen
- 📸 Screenshots aufnehmen
- ⏱️ Timelapse erstellen
- 🌿 Daily Weed Pictures
- 📊 Wachstumsstatistiken

## Automatische Posts

- Screenshots werden alle 5 Minuten erstellt
- Timelapse-Videos werden täglich erstellt
- Spezielle Posts werden um 8:00 und 20:00 Uhr im Daily Channel veröffentlicht
- Alle Bilder werden automatisch verkleinert, falls sie größer als 10MB sind

## Logs

Die Logs des Containers können mit folgendem Befehl eingesehen werden:

```bash
docker logs timelapse-rtsp
```

Die Discord-Bot Logs befinden sich in:

```bash
docker exec timelapse-rtsp cat /var/log/discord_bot.log
```

## Lizenz

MIT
