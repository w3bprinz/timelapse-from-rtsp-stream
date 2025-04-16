#!/bin/bash

# Lade Umgebungsvariablen
source /app/.env

# Erstelle Verzeichnisse, falls sie nicht existieren
mkdir -p "$SCREENSHOT_DIR"
mkdir -p "$TIMELAPSE_DIR"

# Funktion zum Posten in Discord
post_to_discord() {
    local file_path="$1"
    local message="$2"
    local channel_id="$3"
    
    # Führe das Discord-Script aus
    DISCORD_CHANNEL_ID="$channel_id" python3 /app/post_to_discord.py "$file_path" "$message"
    
    if [ $? -ne 0 ]; then
        echo "Fehler beim Posten in Discord"
        return 1
    fi
    return 0
}

# Funktion zum Überprüfen, ob es sich um einen speziellen Zeitpunkt handelt
is_special_time() {
    local current_time=$(date +"%H:%M")
    [ "$current_time" = "08:00" ] || [ "$current_time" = "20:00" ]
}

# Funktion zum Erstellen eines Screenshots
create_screenshot() {
    local timestamp=$(date +"%Y-%m-%d_%H-%M-%S")
    local output_file="/app/screenshots/screenshot_${timestamp}.png"
    
    # Erstelle Screenshot mit ffmpeg
    ffmpeg -y -i "$RTSP_URL" -frames:v 1 -update 1 "$output_file" 2>/dev/null
    
    if [ ! -f "$output_file" ] || [ ! -s "$output_file" ]; then
        echo "Fehler beim Erstellen des Screenshots"
        return 1
    fi
    
    # Prüfe, ob es sich um eine spezielle Uhrzeit handelt (8:00 oder 20:00)
    if is_special_time; then
        local current_time=$(date +"%Y-%m-%d %H:%M:%S")
        local message="Daily Weed Picture: $current_time"
        post_to_discord "$output_file" "$message" "$DISCORD_DAILY_CHANNEL_ID"
    fi
    
    return 0
}

# Erstelle ein Timelapse-Video
create_timelapse() {
    local date=$(date +%Y%m%d)
    local output_file="$TIMELAPSE_DIR/timelapse_${date}.mp4"
    
    # Erstelle das Timelapse-Video mit höherer Qualität
    ffmpeg -y \
        -framerate 12 \
        -pattern_type glob \
        -i "$SCREENSHOT_DIR/*.png" \
        -c:v libx264 \
        -preset slow \
        -crf 18 \
        -pix_fmt yuv420p \
        -movflags +faststart \
        "$output_file"
    
    # Überprüfe die Dateigröße
    local size_mb=$(du -m "$output_file" | cut -f1)
    if [ "$size_mb" -le "$MAX_VIDEO_SIZE_MB" ]; then
        # Sende das Video an Discord
        post_to_discord "$output_file" "Timelapse Video vom $(date +"%Y-%m-%d")" "$DISCORD_CHANNEL_ID"
    else
        echo "Video ist zu groß ($size_mb MB) und wird nicht gesendet"
    fi
    
    # Lösche alle Screenshots
    rm -f "$SCREENSHOT_DIR"/*.png
}

# Hauptlogik
if [ "$1" = "screenshot" ]; then
    create_screenshot
elif [ "$1" = "timelapse" ]; then
    create_timelapse
fi