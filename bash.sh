#! /bin/bash

# Limpiamos la carpeta ruta
OUTPUT_DIR="alexa_dash"
rm -rf "$OUTPUT_DIR"
mkdir -p "$OUTPUT_DIR"
cd "$OUTPUT_DIR"

# Capturamos directamente desde la cámara y generamos HLS en un solo paso
ffmpeg -f v4l2 -input_format yuyv422 -framerate 25 -video_size 960x540 \
	-i /dev/video0 -f lavfi -i anullsrc=channel_layout=stereo:sample_rate=44100 \
	 -c:v libx264 -preset ultrafast -tune zerolatency \
	-profile:v baseline -level 3.1 -pix_fmt yuv420p -c:a aac -b:a 64k \
	-f dash -window_size 5 -extra_window_size 3 -seg_duration 4 -remove_at_exit 1 \
	stream.mpd 2> ffmpeg.log &

python3 -m http.server 8080
