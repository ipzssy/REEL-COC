#!/bin/bash
# builds every vNN whose voices are complete and whose output is missing, in order
cd "$(dirname "$(readlink -f "$0")")/.."
declare -A NAME=([02]=guerre [03]=gel [04]=rage [05]=foudre_seisme [06]=heros [07]=electro_dragons [08]=hdv [09]=remparts [10]=lire_base [11]=pourcentage [12]=lanceur_buche [13]=nouvel_hdv [14]=ressources [15]=trophees [16]=bon_clan [17]=pieges [18]=defenses [19]=trois_phases [20]=base_defense)
for n in $(seq -w 2 20); do
  d=v$n; out=out/coc_${n}_${NAME[$n]}.mp4
  [ -f $out ] && continue
  ns=$(python3 -c "import json;print(len(json.load(open('$d/spec.json'))['scenes']))")
  nv=$(ls $d/voice/v*.wav 2>/dev/null | wc -l)
  [ "$nv" -lt "$ns" ] && { echo "skip $d ($nv/$ns voices)"; continue; }
  [ -f $d/.building ] && continue
  touch $d/.building
  engine/build.sh $d ../$out || echo "FAILED $d"
  rm -f $d/.building
done
