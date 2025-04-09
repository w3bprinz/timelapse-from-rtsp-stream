#!/bin/bash

# Lade Umgebungsvariablen
source /app/.env

# Erstelle Verzeichnisse, falls sie nicht existieren
mkdir -p "$SCREENSHOT_DIR"
mkdir -p "$TIMELAPSE_DIR"

# Erstelle einen Screenshot
create_screenshot() {
    local timestamp=$(date +%Y%m%d_%H%M%S)
    local output_file="$SCREENSHOT_DIR/screenshot_${timestamp}.png"
    
    ffmpeg -y -rtsp_transport tcp -analyzeduration 10000000 -probesize 5000000 -i "$RTSP_URL" \
        -frames:v 1 \
        -update 1 "$output_file"
    
    echo "Screenshot erstellt: $output_file"
}

# Erstelle ein Timelapse-Video
create_timelapse() {
    local date=$(date +%Y%m%d)
    local output_file="$TIMELAPSE_DIR/timelapse_${date}.mp4"
    
    # Erstelle das Timelapse-Video
    ffmpeg -y -framerate 12 -pattern_type glob -i "$SCREENSHOT_DIR/*.png" \
        -c:v libx264 -pix_fmt yuv420p "$output_file"
    
    # Überprüfe die Dateigröße
    local size_mb=$(du -m "$output_file" | cut -f1)
    if [ "$size_mb" -le "$MAX_VIDEO_SIZE_MB" ]; then
        # Sende das Video an Discord
        python3 /app/post_to_discord.py "$output_file"
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