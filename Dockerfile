FROM python:3.9-slim

# Installiere Abhängigkeiten
RUN apt-get update && apt-get install -y \
    ffmpeg \
    cron \
    && rm -rf /var/lib/apt/lists/*

# Setze die Zeitzone
ENV TZ=Europe/Berlin
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Erstelle Verzeichnisse
RUN mkdir -p /app/screenshots /app/timelapse /var/log && \
    touch /var/log/discord_bot.log && \
    chmod 666 /var/log/discord_bot.log

# Kopiere die Python-Abhängigkeiten
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r /app/requirements.txt

# Kopiere die Skripte
COPY screenshot_script.sh /app/
COPY post_to_discord.py /app/
COPY cogs /app/cogs/

# Setze Arbeitsverzeichnis
WORKDIR /app

# Mache die Skripte ausführbar
RUN chmod +x /app/screenshot_script.sh

# Erstelle Cron-Jobs
RUN echo "*/5 * * * * /app/screenshot_script.sh >> /var/log/screenshot.log 2>&1" > /etc/cron.d/timelapse_cron && \
    echo "@reboot /usr/local/bin/python3 /app/post_to_discord.py >> /var/log/discord_bot.log 2>&1" >> /etc/cron.d/timelapse_cron && \
    chmod 0644 /etc/cron.d/timelapse_cron

# Starte Cron im Vordergrund
CMD ["cron", "-f"]