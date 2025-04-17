#!/bin/bash

# Lade Umgebungsvariablen
source /app/.env

# Erstelle Verzeichnisse, falls sie nicht existieren
mkdir -p "$SCREENSHOT_DIR"
mkdir -p "$TIMELAPSE_DIR"

# Funktion zum Verkleinern eines Bildes
resize_image() {
    local input_file="$1"
    local max_size_mb=8  # Reduziert auf 8MB für mehr Sicherheit
    local size_mb=$(du -m "$input_file" | cut -f1)
    
    if [ "$size_mb" -gt "$max_size_mb" ]; then
        echo "Bild ist zu groß ($size_mb MB), verkleinere es..."
        local temp_file="${input_file%.*}_resized.${input_file##*.}"
        
        # Verkleinere das Bild mit ffmpeg
        ffmpeg -y -i "$input_file" \
            -vf "scale='min(1280,iw)':'min(720,ih)':force_original_aspect_ratio=decrease" \
            -compression_level 9 \
            -q:v 2 \
            "$temp_file"
        
        # Überprüfe, ob die Verkleinerung erfolgreich war
        if [ -f "$temp_file" ] && [ -s "$temp_file" ]; then
            mv "$temp_file" "$input_file"
            echo "Bild erfolgreich verkleinert"
        else
            echo "Fehler beim Verkleinern des Bildes"
            return 1
        fi
    fi
    return 0
}

# Funktion zum Posten in Discord
post_to_discord() {
    local file_path="$1"
    local message="$2"
    local channel_id="$3"
    
    # Verkleinere das Bild, falls nötig
    if [[ "$file_path" == *.png ]] || [[ "$file_path" == *.jpg ]] || [[ "$file_path" == *.jpeg ]]; then
        resize_image "$file_path"
        if [ $? -ne 0 ]; then
            echo "Fehler beim Verkleinern des Bildes"
            return 1
        fi
    fi
    
    # Führe das Discord-Script mit vollem Python-Pfad aus
    PYTHONPATH=/app DISCORD_CHANNEL_ID="$channel_id" /usr/local/bin/python3 /app/post_to_discord.py "$file_path" "$message"
    
    if [ $? -ne 0 ]; then
        echo "Fehler beim Posten in Discord"
        return 1
    fi
    return 0
}

# Funktion zum Überprüfen, ob es sich um einen speziellen Zeitpunkt handelt
is_special_time() {
    local current_time=$(date +"%H:%M")
    [ "$current_time" = "09:10" ] || [ "$current_time" = "20:00" ]
}

# Funktion zum Erstellen eines Screenshots
create_screenshot() {
    local timestamp=$(date +"%Y-%m-%d_%H-%M-%S")
    local output_file="/app/screenshots/screenshot_${timestamp}.png"
    local temp_file="/app/screenshots/temp_${timestamp}.png"
    
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
                
                # Prüfe, ob es sich um eine spezielle Uhrzeit handelt (8:00 oder 20:00)
                if is_special_time; then
                    local current_time=$(date +"%Y-%m-%d %H:%M:%S")
                    local message="Daily Weed Picture: $current_time"
                    post_to_discord "$output_file" "$message" "$DISCORD_DAILY_CHANNEL_ID"
                fi
                
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