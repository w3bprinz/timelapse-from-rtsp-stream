FROM python:3.9-slim

# Setze Python auf unbuffered
ENV PYTHONUNBUFFERED=1

# Installiere Abhängigkeiten
RUN apt-get update && apt-get install -y \
    ffmpeg \
    cron \
    && rm -rf /var/lib/apt/lists/*

# Setze die Zeitzone
ENV TZ=Europe/Berlin
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Erstelle Verzeichnisse und setze Berechtigungen
RUN mkdir -p /app/screenshots /app/timelapse /var/log && \
    touch /var/log/discord_bot.log /var/log/screenshot.log && \
    chmod 666 /var/log/discord_bot.log /var/log/screenshot.log && \
    chown -R root:root /app

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

# Kopiere und konfiguriere den Cron-Job
COPY crontab /etc/cron.d/timelapse_cron
RUN chmod 0644 /etc/cron.d/timelapse_cron && \
    echo "" >> /etc/cron.d/timelapse_cron && \
    crontab /etc/cron.d/timelapse_cron

# Erstelle Start-Skript
RUN echo '#!/bin/bash\n\
# Starte den Discord Bot im Hintergrund\n\
python3 /app/post_to_discord.py &\n\
\n\
# Starte den Cron-Dienst\n\
cron -f' > /app/start.sh && \
    chmod +x /app/start.sh

# Starte beide Dienste
CMD ["/app/start.sh"]