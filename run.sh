python3 src/main.py $1 && ffplay -f f64le -ar 48000 main.bin -showmode 0 -autoexit > /dev/null 2>&1 && \
ffmpeg -f f64le -ar 48000 -i main.bin song.wav