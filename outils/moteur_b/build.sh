#!/bin/bash
# usage: build.sh <video_dir> <out_name>
set -e
E=$(dirname "$(readlink -f "$0")")
OUT="$2"; cd "$1"
python3 -I $E/engine.py events
python3 -I $E/audio.py > /dev/null
N=$(python3 -c "import json;print(len(json.load(open('spec.json'))['scenes']))")
for w in 0 1 2; do python3 -I $E/engine.py render $(seq $w 3 $((N-1))) & done; wait
for i in $(seq 0 $((N-1))); do test -f shots/s$i.mp4 || { echo "missing shot $i"; exit 1; }; done
(for f in $(ls shots/s*.mp4 | sort -V); do echo "file '$(basename $f)'"; done) > shots/list.txt
ffmpeg -y -loglevel error -f concat -safe 0 -i shots/list.txt -c copy video_only.mp4
M=$(ffmpeg -hide_banner -i audio_raw.wav -af loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json -f null - 2>&1 | python3 -c "
import sys,json
s=sys.stdin.read(); j=json.loads(s[s.rindex('{'):s.rindex('}')+1]); print(j['input_i'],j['input_tp'],j['input_lra'],j['input_thresh'],j['target_offset'])")
set -- $M
ffmpeg -y -loglevel error -i audio_raw.wav -af "loudnorm=I=-14:TP=-1.5:LRA=11:measured_I=$1:measured_TP=$2:measured_LRA=$3:measured_thresh=$4:offset=$5:linear=true" -ar 48000 audio_final.wav
ffmpeg -y -loglevel error -i video_only.mp4 -i audio_final.wav -c:v copy -c:a aac -b:a 192k -shortest "$OUT.part.mp4"
mv "$OUT.part.mp4" "$OUT"
echo "done $OUT $(ffprobe -v error -show_entries format=duration -of csv=p=0 $OUT)"
