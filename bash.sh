#! /bin/bash

# Limpiamos la carpeta ruta
rm -f ruta/*

# Capturamos directamente desde la cámara y generamos HLS en un solo paso
ffmpeg -f v4l2 -input_format yuyv422 -framerate 30 -video_size 640x480 \
	-i /dev/video0 -f lavfi -i anullsrc=channel_layout=stereo:sample_rate=44100 \
	 -c:v libx264 -preset ultrafast -tune zerolatency \
	-f hls -hls_time 1 -hls_list_size 5 -hls_flags delete_segments+append_list \
	-hls_segment_filename "./ruta/segment%03d.ts" ./ruta/stream.m3u8

