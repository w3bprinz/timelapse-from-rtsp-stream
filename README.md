# RTSP Stream Timelapse Generator

Dieses Projekt erstellt automatisch Timelapse-Videos aus einem RTSP-Stream und sendet diese an einen Discord-Channel.

## Features

- Erstellt Screenshots alle 5 Minuten aus einem RTSP-Stream
- Generiert täglich ein Timelapse-Video aus den Screenshots
- Sendet das Video automatisch an Discord (wenn unter 10MB)
- Automatische Bereinigung alter Screenshots

## Installation

### Voraussetzungen

- Docker
- Unraid (für Container-Installation)

### Konfiguration

1. Klonen Sie das Repository
2. Kopieren Sie `.env.example` zu `.env`
3. Tragen Sie Ihre Konfigurationsdaten in die `.env` Datei ein:
   - RTSP_URL: URL Ihres RTSP-Streams
   - DISCORD_CHANNEL_ID: ID des Discord-Channels
   - DISCORD_BOT_TOKEN: Token Ihres Discord-Bots

### Unraid Installation

1. Gehen Sie zu "Docker" in Unraid
2. Klicken Sie auf "Add Container"
3. Wählen Sie "Custom" als Template
4. Geben Sie die folgenden Informationen ein:
   - Repository: `ihr-username/timelapse-from-rtsp-stream`
   - Name: `timelapse-generator`
   - Ports: Keine erforderlich
   - Volumes:
     - `/path/to/config:/app/config`
     - `/path/to/screenshots:/app/screenshots`
     - `/path/to/timelapse:/app/timelapse`

## Verwendung

Der Container startet automatisch und:

- Erstellt alle 5 Minuten einen Screenshot
- Erstellt täglich um Mitternacht ein Timelapse-Video
- Sendet das Video an Discord (wenn unter 10MB)
- Löscht die Screenshots nach der Video-Erstellung

## Sicherheit

- Sensible Daten werden über Umgebungsvariablen verwaltet
- Keine hartcodierten Zugangsdaten im Code
- Sichere Speicherung der Konfiguration

## Lizenz

MIT
