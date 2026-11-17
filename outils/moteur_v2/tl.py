import wave, json, os
FPS = 60
BPM = 120
BEAT = 60.0 / BPM
LEAD = 0.25
SPEC = json.load(open("spec.json"))
NSHOTS = len(SPEC["scenes"])
VD = []
for i in range(NSHOTS):
    with wave.open(f"voice/v{i}.wav") as w:
        VD.append(w.getnframes() / w.getframerate())
SCENES = [round(LEAD + VD[i] + (1.7 if i == NSHOTS - 1 else 0.35), 3) for i in range(NSHOTS)]
STARTS = [sum(SCENES[:i]) for i in range(NSHOTS)]
TOTAL = sum(SCENES)
