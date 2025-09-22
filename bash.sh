#! /bin/bash

rm -f captura_mjpeg.avi

#./server.sh &

# Capturamos un video YUYV RAW y lo convertimos a MJPEG AVI:
ffmpeg -f v4l2 -input_format yuyv422 -framerate 30 -video_size 640x480 \
-i /dev/video0 -c:v mjpeg -q:v 3 captura_mjpeg.avi
# ffmpeg: El programa para capturar y procesar video
# -f v4l2: Usa el dispositivo de Linux (Video4Linux2), estandar para webcams y camaras en Linux, -f es para indicar el formato
# -input_format yuyv422: Fuerza a que se use el formato de entrada YUYV 4:2:2 que produce la cámara (formato raw de video)
# -framerate 30: Captura a 30 cuadros por segundo
# -video_size 640x480: Resolución de captura
# -i /dev/video0: Dispositivo de entrada (la camara conectada al sistema)
# -c:v mjpeg: Codifica a MJPEG en tiempo real (cada frame es una imagen JPEG)
# -q:v: Calidad del video codificado  (de 1 a 31, donde 1 es la mejor)
# captura_mjpeg.avi: Archivo de salida donde se guarda el video capturado

# Convertimos el MJPEG a H.264 y lo enviamos por HLS
ffmpeg -i captura_mjpeg.avi -c:v libx264 -preset ultrafast -tune zerolatency \
-f hls -hls_time 1 -hls_list_size 5 -hls_flags delete_segments+append_list \
./ruta/stream.m3u8
# -i captura_mjpeg.avi: El -i indica el archivo o dispositivo de entrada que FFmpeg debe leer, siempre va seguido del nombre o ruta del archivo o dispositivo
# -c:v libx264: Codifica el video usando el codec H.264
# -preset ultrafast: Usa la codificación mas rápida posible, sacrificando algo de compresión
# -tune zerolatency: Optimiza para minimizar la latencia
# -f hls: Indica que la salida será un stream HLS (HTTP Live Streaming)
# HLS_time 4: Duración de cada segmento HLS en segundos (cada archivo .ts dura 4s)
# hls_list_size 5: El playlist .m3u8 mantendrá referencia a los últimos 5 segmentos 
# -hls_flags delete_segments: Elimina segmentos antiguos de la playlist
# /ruta/stream.m3u8: Ruta y nombre donde se guarda el playlist HLS que lista los segmentos
