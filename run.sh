python3 main.py && ffplay -f f64le -ar 48000 hello.bin -showmode 0 -autoexit > /dev/null 2>&1 && \
ffmpeg -f f64le -ar 48000 -i hello.bin song.wav