#!/bin/bash
# usage: voices.sh <video_dir> <blobid0> <blobid1> ...
T=/root/.claude/projects/-home-claude/c50337cd-a37e-5624-b8c7-997e105991c5/tool-results
d=$1; shift; i=0
for b in "$@"; do
  ffmpeg -y -loglevel error -i $T/mcp-Speko-blob-*-$b.wav -af "silenceremove=start_periods=1:start_threshold=-45dB,areverse,silenceremove=start_periods=1:start_threshold=-45dB,areverse" -ar 44100 -ac 1 -sample_fmt s16 $d/voice/v$i.wav
  i=$((i+1))
done
echo "$d: $i voices"
