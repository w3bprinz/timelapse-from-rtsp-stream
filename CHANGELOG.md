# Changelog

Alle wichtigen Änderungen an diesem Projekt werden in dieser Datei dokumentiert.

Das Format basiert auf [Keep a Changelog](https://keepachangelog.com/de/1.0.0/),
und dieses Projekt folgt [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2024-04-25

### Hinzugefügt

- Neuer Discord Bot mit Slash Commands
- `/image last` Command zum Anzeigen des letzten Screenshots (nur im Daily Channel verfügbar)
- `/purge` Command zum Löschen aller Nachrichten in einem Channel (nur für Bot-Owner)
- Automatische Daily Posts mit Screenshots (8:00 und 20:00 Uhr)
- Logging in `/var/log/discord_bot.log`
- Bot Status Rotation mit verschiedenen Aktivitäten

### Geändert

- Verbesserte Codestruktur mit separaten Cogs für Commands
- Optimierte Bildkomprimierung für Discord-Uploads
- Channel-IDs werden jetzt aus der `.env` Datei gelesen

## [1.0.0] - 2024-04-24

### Hinzugefügt

- Erste Version des Timelapse Generators
- RTSP Stream Aufnahme
- Screenshot-Erstellung
- Basis-Dockerfile für Container-Deployment
