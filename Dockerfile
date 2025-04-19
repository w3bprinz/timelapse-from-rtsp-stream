FROM python:3.9-slim

# Installiere ffmpeg und andere Abhängigkeiten
RUN apt-get update && \
    apt-get install -y ffmpeg cron tzdata && \
    pip install discord.py pytz python-dotenv && \
    rm -rf /var/lib/apt/lists/*

# Setze die Zeitzone auf Berlin
ENV TZ=Europe/Berlin
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Erstelle Arbeitsverzeichnis
WORKDIR /app

# Erstelle notwendige Verzeichnisse
RUN mkdir -p /app/screenshots /app/timelapse

# Kopiere die Skripte in das Arbeitsverzeichnis
COPY screenshot_script.sh /app/screenshot_script.sh
COPY post_to_discord.py /app/post_to_discord.py
COPY .env.example /app/.env

# Setze Berechtigungen für das Skript
RUN chmod +x /app/screenshot_script.sh

# Kopiere und konfiguriere den Cron-Job
COPY crontab /etc/cron.d/timelapse_cron
RUN chmod 0644 /etc/cron.d/timelapse_cron && \
    echo "" >> /etc/cron.d/timelapse_cron && \
    echo "@reboot /usr/local/bin/python3 /app/post_to_discord.py >> /var/log/discord_bot.log 2>&1" >> /etc/cron.d/timelapse_cron && \
    crontab /etc/cron.d/timelapse_cron

# Starte den Cron-Dienst
CMD ["cron", "-f"]