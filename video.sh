#!/bin/bash

# Habilitar control de señales
trap cleanup INT

cleanup() {
    echo "Cerrando procesos..."
    # Mata todos los procesos hijos
    pkill -P $$
    # También mata ffmpeg específicamente si sigue vivo
    pkill ffmpeg
    # También mata el servidor http
    pkill -f "python3 -m http.server"
    # También mata el ngrok
    pkill -f "ngrok"
    echo "Limpieza completa."
    exit 0
}

ngrok http 8080 &

sleep 2

python3 update_dynamo.py

python3 -m http.server 8080 &

OUTPUT_DIR="alexa_dash"
cd ..
rm -rf "$OUTPUT_DIR"
mkdir -p "$OUTPUT_DIR"
cd "$OUTPUT_DIR"

# Lanzar ffmpeg en background
ffmpeg -f v4l2 \
  -input_format yuyv422 \
  -framerate 25 \
  -video_size 960x540 \
  -i /dev/video0 \
  -f lavfi -i anullsrc=channel_layout=stereo:sample_rate=44100 \
  -c:v libx264 \
  -preset ultrafast \
  -tune zerolatency \
  -profile:v baseline \
  -level 3.1 \
  -pix_fmt yuv420p \
  -c:a aac \
  -b:a 64k \
  -f dash \
  -window_size 5 \
  -extra_window_size 3 \
  -seg_duration 4 \
  -remove_at_exit 1 \
  stream.mpd 2> ffmpeg.log &
FFMPEG_PID=$!

echo "DASH generado"

HTTP_PID=$!

# Esperar a que uno reciba Ctrl+C
wait $FFMPEG_PID
wait $HTTP_PID
