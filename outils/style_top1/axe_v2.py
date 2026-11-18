import json, subprocess, numpy as np, sys
import eng
from eng import *
S = eng.S
words = json.load(open(R + "/words.json"))
eng.KNOTS[:] = make_knots(words, shrink=0.1, thr=0.2)
last = words[-1][2]  # 39.4
eng.KNOTS.append((last + 0.3, eng.g(last) + 0.3))
def build():
    sc = eng.build_axe()
    sc[-1].t1 = last + 0.1
    t0 = last + 0.1
    bg = VidBG("clip_17h06.mp4", 22, 2.0, blur=2, dim=0.45, zoom=1.0)
    sc.append(Scene(t0, t0 + 1.3, bg, [
        pop("ET SI TU AS", t0, t0 + 0.5, 960, 190, WHT, -3),
        pop("RATÉ", t0 + 0.5, t0 + 0.85, 960, 260, YEL, 3),
        pop("LE DÉBUT…", t0 + 0.85, t0 + 1.3, 960, 230, WHT, -2),
    ], "loop"))
    return sc
eng.BUILDS["axe"] = build
def audio():
    def rd(p):
        return np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-i", p, "-ar", "44100", "-ac", "1", "-f", "s16le", "-"], capture_output=True).stdout, np.int16)
    v = rd(S + "/cp/voice_mix.wav"); sr = 44100
    parts = []
    k = eng.KNOTS
    for (o0, n0), (o1, n1) in zip(k, k[1:]):
        if abs((o1 - o0) - (n1 - n0)) < 1e-6:
            parts.append(v[int(o0 * sr):int(o1 * sr)])
        else:
            seg = v[int(o0 * sr):int(o0 * sr + (n1 - n0) * sr)]  # tail of speech, then short pad
            parts.append(seg * 0 if False else v[int(o0 * sr):int(o0 * sr + (n1 - n0) * sr)])
    # cut up to last word end + 0.1
    a = np.concatenate(parts)[: int(eng.g(last) * sr)]
    a = np.concatenate([a, np.zeros(int(0.1 * sr), np.int16), rd(S + "/h/t8.wav")])
    import wave
    w = wave.open(S + "/r/axe_v2.wav", "wb"); w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr); w.writeframes(a.tobytes()); w.close()
    return len(a) / sr
if __name__ == "__main__":
    n = len(eng.BUILDS["axe"]())
    from multiprocessing import Pool
    eng.CUR["name"] = "axe"
    with Pool(2) as p: p.map(eng.render_scene, range(n))
    d = audio(); print("audio", d)
    eng.assemble("axe", S + "/r/axe_v2.wav", S + "/r/refait_v2.mp4")
