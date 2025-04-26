# Timelapse Generator mit Discord Integration

Dieses Projekt erstellt Timelapses aus einem RTSP-Stream und integriert einen Discord Bot für Benachrichtigungen und Bildverwaltung.

## Features

- Automatische Screenshot-Erstellung aus RTSP-Stream
- Discord Bot Integration:
  - `/image last` - Zeigt das letzte aufgenommene Bild (nur im Daily Channel verfügbar)
  - `/purge` - Löscht alle Nachrichten in einem Channel (nur für Bot-Owner)
  - Automatische Daily Posts (8:00 und 20:00 Uhr)
  - Status Rotation mit verschiedenen Aktivitäten
- Automatische Bildkomprimierung für Discord-Uploads
- Detailliertes Logging

## Installation

1. Repository klonen:

```bash
git clone https://github.com/w3bprinz/timelapse-from-rtsp-stream.git
cd timelapse-from-rtsp-stream
```

2. `.env` Datei erstellen:

```env
DISCORD_BOT_TOKEN=dein_bot_token
DISCORD_TIMELAPSE_CHANNEL_ID=dein_channel_id
DISCORD_DAILY_CHANNEL_ID=daily_channel_id
```

3. Docker Image bauen:

```bash
docker build -t ghcr.io/w3bprinz/timelapse-from-rtsp-stream:latest .
```

4. Container starten:

```bash
docker run -d \
  --name timelapse-generator \
  -v /pfad/zu/.env:/app/.env \
  ghcr.io/w3bprinz/timelapse-from-rtsp-stream:latest
```

## Discord Bot Einrichtung

1. Erstelle einen neuen Bot im [Discord Developer Portal](https://discord.com/developers/applications)
2. Aktiviere die folgenden Intents:
   - Message Content Intent
   - Server Members Intent
3. Lade den Bot mit den folgenden Berechtigungen ein:
   - `bot`
   - `applications.commands`
4. Benötigte Bot-Berechtigungen:
   - Nachrichten senden
   - Dateien anhängen
   - Nachrichten verwalten (für purge)

## Logs

Die Logs des Bots werden in `/var/log/discord_bot.log` gespeichert und sind auch in der Unraid-Konsole sichtbar.

## Entwicklung

- Python 3.9+
- discord.py 2.0+
- FFmpeg für Bildkomprimierung

Siehe [CHANGELOG.md](CHANGELOG.md) für die Versionshistorie.

## Lizenz

MIT License - siehe [LICENSE](LICENSE) für Details.
