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
    local temp_file="$SCREENSHOT_DIR/temp_${timestamp}.png"
    
    # Versuche bis zu 3 Mal, ein gutes Bild zu bekommen
    for i in {1..3}; do
        echo "Versuch $i: Erstelle Screenshot..."
        
        # Warte 1 Sekunde, um den Stream zu stabilisieren
        sleep 1
        
        # Erstelle Screenshot mit verbesserten Parametern
        ffmpeg -y \
            -rtsp_transport tcp \
            -analyzeduration 10000000 \
            -probesize 5000000 \
            -i "$RTSP_URL" \
            -frames:v 1 \
            -vf "format=rgb24,setpts=PTS-STARTPTS" \
            -compression_level 9 \
            -update 1 \
            "$temp_file"
        
        # Überprüfe, ob das Bild gültig ist
        if [ -f "$temp_file" ] && [ -s "$temp_file" ]; then
            # Überprüfe die Bildqualität
            local image_info=$(ffprobe -v error -select_streams v:0 -show_entries stream=width,height -of csv=p=0 "$temp_file")
            if [ ! -z "$image_info" ]; then
                mv "$temp_file" "$output_file"
                echo "Screenshot erfolgreich erstellt: $output_file"
                return 0
            fi
        fi
        
        # Warte 2 Sekunden vor dem nächsten Versuch
        sleep 2
    done
    
    # Lösche temporäre Datei, falls vorhanden
    rm -f "$temp_file"
    echo "Fehler: Konnte keinen gültigen Screenshot erstellen"
    return 1
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