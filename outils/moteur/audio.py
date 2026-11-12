import sys, wave, json, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
TR = 2 ** (((json.load(open("spec.json")).get("n", 0) % 5) - 2) / 12)
import numpy as np
from audiolib import *
music = np.zeros(N); beat = BEAT; step = beat / 4
CH0 = [(55.00,[220.00,261.63,329.63,440.00]),(43.65,[174.61,220.00,261.63,349.23]),(65.41,[261.63,329.63,392.00,523.25]),(49.00,[196.00,246.94,293.66,392.00])]
CH = [(r * TR, [x * TR for x in tn]) for r, tn in CH0]
ARP = [0,1,2,3,2,1,2,1,0,1,2,3,2,1,3,2]
for s in range(int(TOTAL / step) + 1):
    t0 = s * step; root, tones = CH[int(t0 // (4 * beat)) % 4]; pos = s % 16
    if pos % 4 == 0: put(music, t0, kick(), 0.85)
    if pos in (4, 12): put(music, t0, clap(), 0.8)
    if pos % 4 == 2: put(music, t0, hat(1.0), 1.0)
    if pos % 2 == 1: put(music, t0, hat(0.5), 1.0)
    if pos % 2 == 0: put(music, t0, bass(root if pos % 8 != 6 else root * 2), 1.0)
    put(music, t0, pluck(tones[ARP[pos]]), 1.0)
    if pos == 0: put(music, t0, pad(tones[:3], 4 * beat), 1.0)
gain = np.ones(N)
for i, sc in enumerate(json.load(open('spec.json'))['scenes']):
    if sc.get('result'):
        a = int((STARTS[i] - 0.4) * SR); gain[a:int(STARTS[i] * SR)] = 0
k = int(0.03 * SR); music *= np.convolve(gain, np.ones(k) / k, mode="same")
music = music / np.max(np.abs(music)) * 10 ** (-18 / 20)
sfx = np.zeros(N)
tab = {"boom": (sfx_boom, 0.9), "whoosh": (sfx_whoosh, 0.4), "pop": (sfx_pop, 0.6), "buzz": (sfx_buzz, 0.6),
       "ding": (sfx_ding, 0.8), "stamp": (sfx_boom, 1.0)}
for t0, kind in json.load(open("events.json")):
    fn, g = tab[kind]
    put(sfx, max(0, t0 - (0.12 if kind == "whoosh" else 0)), fn(), g)
    if kind == "stamp": put(sfx, t0, sfx_pop(), 0.8)
put(sfx, 0.0, sfx_alert(), 0.6)
sfx = sfx / np.max(np.abs(sfx)) * 10 ** (-10 / 20)
voice = np.zeros(N); duck = np.ones(N)
for i in range(NSHOTS):
    with wave.open(f"voice/v{i}.wav") as w:
        assert w.getframerate() == SR
        x = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float64) / 32768
    x = x / np.max(np.abs(x)) * 10 ** (-6 / 20); t0 = STARTS[i] + LEAD
    put(voice, t0, x, 1.0)
    duck[max(0, int((t0 - 0.03) * SR)):min(N, int((t0 + len(x) / SR + 0.1) * SR))] = 0.4
k = int(0.08 * SR); duck = np.convolve(duck, np.ones(k) / k, mode="same")
mix = music * duck + sfx * (0.55 + 0.45 * duck) + voice
f = int(0.03 * SR); mix[:f] *= np.linspace(0, 1, f); mix[-f:] *= np.linspace(1, 0, f)
mix = mix / max(1.0, np.max(np.abs(mix)) / 0.89)
pcm = (mix * 32767).astype(np.int16)
with wave.open("audio_raw.wav", "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(np.repeat(pcm[:, None], 2, axis=1).tobytes())
print("audio", len(pcm) / SR)
