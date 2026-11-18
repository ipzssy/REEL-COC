#!/usr/bin/env python3
"""Short TH19 v4 : grammaire de la référence coc_03_gel_viral (1080x1920, 60 fps).
Plans coupés toutes les ~2 s avec zoom, sous-titres mot par mot (mot actif dans une pastille violette),
étiquettes en gros titres, cadre arrondi, tampon cercle violet, jauges + « TON AVIS ? », SFX à chaque coupe."""
import math, subprocess, wave
import numpy as np
from functools import lru_cache
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS, SR = 1080, 1920, 60, 44100
BLACKF = "/usr/share/fonts/opentype/inter/Inter-Black.otf"
BOLDF = "/usr/share/fonts/opentype/inter/Inter-Bold.otf"
REPO = "/home/claude/reel-coc"
BG = (11, 11, 14); WHITE = (250, 250, 250); PURPLE = (165, 90, 255); GREY = (150, 150, 158)
RED = (236, 38, 56); GREEN = (80, 220, 120); INK = (10, 10, 10); PAPER = (250, 250, 248)

import json, os, sys
PROJ = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else os.getcwd()
SPEC = json.load(open(os.path.join(PROJ, "spec.json")))
PURPLE = tuple(SPEC.get("accent", PURPLE))
HEADER = SPEC.get("header", "CLASH OF CLANS")
OUTNAME = os.path.join(PROJ, SPEC.get("out", "short.mp4"))
MIXNAME = os.path.join(PROJ, "mix.wav")
SN = os.path.join(PROJ, "img") + "/"
SCENES = []
for k, s in enumerate(SPEC["scenes"]):
    SCENES.append(dict(v=k, label=s.get("label"), big=[(t, PURPLE if c == "accent" else WHITE) for t, c in s.get("big", [])],
                       stamp=(s["stamp"], PURPLE, 0.55) if s.get("stamp") else None, gauge=bool(s.get("gauge")), glabels=s.get("gauge_labels", ["OFFICIEL", "FUITE"]),
                       sub=s["text"], images=s.get("images", [])))
PAD = 0.3
SHOT = 2.2          # un plan toutes les ~2 s
GAUGE_EXTRA = 3.0   # temps supplémentaire pour les jauges

DUR = []
for s in SCENES:
    with wave.open(os.path.join(PROJ, f"v{s['v']}.wav")) as w:
        DUR.append(w.getnframes() / w.getframerate())
LEN = [d + PAD + (GAUGE_EXTRA if s.get("gauge") else 0) for d, s in zip(DUR, SCENES)]
START = [sum(LEN[:i]) for i in range(len(LEN))]
TOTAL = sum(LEN)


def cl(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def eo(p):
    p = cl(p); return 1 - (1 - p) ** 3


def eback(p, s=1.8):
    p = cl(p); return 1 + (s + 1) * (p - 1) ** 3 + s * (p - 1) ** 2


def prog(t, t0, d):
    return cl((t - t0) / d)


@lru_cache(maxsize=None)
def text_img(s, size, col, font=BLACKF, maxw=980):
    while True:
        f = ImageFont.truetype(font, size)
        bb = f.getbbox(s); w = bb[2] - bb[0]
        if w <= maxw or size <= 40:
            break
        size -= 6
    pad = 14
    im = Image.new("RGBA", (w + pad * 2 + 12, size + pad * 2 + 20), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.text((pad + 10, pad + 10), s, font=f, fill=(0, 0, 0, 200))
    d.text((pad + 4, pad + 4), s, font=f, fill=col + (255,))
    return im


@lru_cache(maxsize=None)
def tag_img(s, bgc, fgc, size=56):
    f = ImageFont.truetype(BOLDF, size)
    bb = f.getbbox(s); tw = bb[2] - bb[0]; th = bb[3] - bb[1]
    im = Image.new("RGBA", (tw + 70, th + 46), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, tw + 69, th + 45], radius=18, fill=bgc + (255,))
    d.text((35 - bb[0], 23 - bb[1]), s, font=f, fill=fgc + (255,))
    return im


@lru_cache(maxsize=None)
def stamp_img(s, col):
    f = ImageFont.truetype(BLACKF, 50)
    bb = f.getbbox(s); tw = bb[2] - bb[0]; th = bb[3] - bb[1]
    d_ = max(tw, th) + 120
    im = Image.new("RGBA", (d_, d_), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.ellipse([10, 10, d_ - 10, d_ - 10], outline=col + (255,), width=10)
    d.text(((d_ - tw) / 2 - bb[0], (d_ - th) / 2 - bb[1]), s, font=f, fill=col + (255,))
    return im


def put(img, layer, cx, cy, scale=1.0, alpha=1.0, rot=0.0):
    l = layer
    if scale != 1.0:
        l = l.resize((max(1, int(l.width * scale)), max(1, int(l.height * scale))), Image.BILINEAR)
    if rot:
        l = l.rotate(rot, resample=Image.BICUBIC, expand=True)
    if alpha < 1.0:
        a = l.getchannel("A").point(lambda v: int(v * max(0.0, alpha)))
        l = l.copy(); l.putalpha(a)
    img.alpha_composite(l, (int(cx - l.width / 2), int(cy - l.height / 2)))


CW, CH = 920, 760
@lru_cache(maxsize=None)
def source(name):
    return Image.open(SN+name).convert("RGB")

def shot(name, f0, f1, z0, z1, p):
    """Plan net (aucun flou) : cadre CWxCH, pan de f0 vers f1 et zoom z0 vers z1."""
    im = source(name)
    sc = max(CW / im.width, CH / im.height)
    z = z0 + (z1 - z0) * p
    vw, vh = CW / (sc * z), CH / (sc * z)
    fx = f0[0] + (f1[0] - f0[0]) * p; fy = f0[1] + (f1[1] - f0[1]) * p
    x0 = min(max(fx * im.width - vw / 2, 0), im.width - vw)
    y0 = min(max(fy * im.height - vh / 2, 0), im.height - vh)
    return im.resize((int(im.width*sc*z)+1, int(im.height*sc*z)+1), Image.LANCZOS).crop(
        (int(x0*sc*z), int(y0*sc*z), int(x0*sc*z)+CW, int(y0*sc*z)+CH)).convert("RGBA")

# plans automatiques : alterne images, focus et zooms pour changer d'angle à chaque coupe
FOCI = [((.3,.5),(.6,.5),1.0,1.3),((.5,.3),(.5,.6),1.1,1.6),((.8,.4),(.55,.6),1.2,1.7),((.5,.8),(.4,.7),1.0,1.5),
        ((.2,.7),(.4,.5),1.3,1.8),((.7,.3),(.6,.5),1.1,1.5)]
SHOTS = {}
for _i, _s in enumerate(SCENES):
    imgs = _s["images"] or []
    SHOTS[_i] = [(imgs[(_i + n) % len(imgs)],) + FOCI[(_i * 2 + n) % len(FOCI)] for n in range(4)] if imgs else []

# ----- fond sombre violet
def make_bg():
    base = Image.new("RGBA", (W, H), (12, 10, 18, 255))
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(glow).ellipse([-200, 500, W + 200, 1500], fill=(165, 90, 255, 60))
    base.alpha_composite(glow.filter(ImageFilter.GaussianBlur(220)))
    return base


BG_IMG = make_bg()


def sub_layer(sub, lt, dur):
    """Sous-titres mot par mot : le mot en cours passe dans une pastille violette."""
    words = sub.split()
    weights = [len(w) + 2 for w in words]
    tot = sum(weights)
    f = ImageFont.truetype(BOLDF, 64)
    lines, cur = [], []
    for w in words:
        if f.getbbox(" ".join(cur + [w]))[2] > 940 and cur:
            lines.append(cur); cur = []
        cur.append(w)
    if cur: lines.append(cur)
    im = Image.new("RGBA", (W, 440), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    spans, acc = [], 0.0
    for wt in weights:
        dw = dur * wt / tot
        spans.append((acc, acc + dw)); acc += dw
    y, idx = 20, 0
    space = f.getbbox(" ")[2]
    for line in lines:
        widths = [f.getbbox(w)[2] for w in line]
        total_w = sum(widths) + space * (len(line) - 1)
        x = (W - total_w) / 2
        for w, ww in zip(line, widths):
            a, b = spans[idx]
            if a <= lt < b:
                d.rounded_rectangle([x - 12, y - 6, x + ww + 12, y + 74], radius=16, fill=PURPLE + (255,))
                col = WHITE
            elif lt >= b:
                col = WHITE
            else:
                col = (165, 165, 172)
            d.text((x + 3, y + 3), w, font=f, fill=(0, 0, 0, 200))
            d.text((x, y), w, font=f, fill=col + (255,))
            x += ww + space; idx += 1
        y += 84
    return im


def gauge_frame(img, lt, t_start, labels=("OFFICIEL", "FUITE")):
    """Jauges OFFICIEL / FUITE, « ? » violet, « TON AVIS ? » — style référence."""
    p = prog(lt, t_start, 0.6)
    for k, (label, cx, phase) in enumerate([(labels[0], 330, 0.0), (labels[1], 750, 1.3)]):
        fill = 0.25 + 0.6 * (0.5 + 0.5 * math.sin(lt * (4 + 2 * k) + phase)) if lt > t_start + 0.6 else 0.0
        fill = fill * eo(p)
        top, bot = 560, 1160
        d = ImageDraw.Draw(img)
        d.rounded_rectangle([cx - 80, top, cx + 80, bot], radius=28, fill=(30, 30, 38, 255), outline=(70, 70, 80, 255), width=4)
        h = int((bot - top - 24) * fill)
        if h > 0:
            d.rounded_rectangle([cx - 64, bot - 12 - h, cx + 64, bot - 12], radius=20, fill=WHITE + (255,))
        put(img, text_img(label, 64, WHITE, maxw=440), cx, top - 60, alpha=p)
    q = prog(lt, t_start + 0.3, 0.3)
    put(img, text_img("?", 260, PURPLE), 540, 860, scale=1.6 - 0.6 * eback(q), alpha=q)
    r = prog(lt, t_start + 1.2, 0.4)
    put(img, text_img("TON AVIS ?", 150, WHITE), 540, 1290, scale=1.2 - 0.2 * eo(r), alpha=r)
    put(img, tag_img("EN COMMENTAIRE", PURPLE, WHITE, 52), 540, 1430, alpha=prog(lt, t_start + 1.6, 0.3))
    return img


def scene_at(t):
    for i in range(len(START)):
        if START[i] <= t < START[i] + LEN[i]:
            return i, t - START[i]
    return len(START) - 1, LEN[-1]


def frame(t):
    i, lt = scene_at(t)
    s = SCENES[i]
    img = BG_IMG.copy()
    # en-tête permanent
    put(img, text_img(HEADER, 62, WHITE, font=BOLDF, maxw=900), W / 2, 150, alpha=prog(t, 0.0, 0.25))
    dur = DUR[i]
    if s.get("gauge"):
        gauge_frame(img, lt, 0.0, s["glabels"])
    else:
        # plans : une coupe toutes les ~SHOT secondes, chaque plan zoome de 100 % à 115 %
        n_shots = max(1, round(dur / SHOT))
        k = min(int(lt / (dur / n_shots)), n_shots - 1)
        seg = dur / n_shots
        local = lt - k * seg
        zoom = 1.0 + 0.15 * cl(local / seg)
        lst = SHOTS[i]
        if lst:
            nm, f0, f1, z0, z1 = lst[k % len(lst)]
            card = shot(nm, f0, f1, z0, z1, cl(local / seg))
        else:
            card = Image.new("RGBA", (CW, CH), (25, 22, 34, 255))
        cx, cy = 540, 640
        img.alpha_composite(Image.new("RGBA", (W, H), (0, 0, 0, 0)))
        # cadre arrondi violet
        frame_l = Image.new("RGBA", (940, 780), (0, 0, 0, 0))
        fd = ImageDraw.Draw(frame_l)
        fd.rounded_rectangle([0, 0, 939, 779], radius=40, fill=(25, 22, 34, 255), outline=PURPLE + (255,), width=6)
        frame_l.paste(card, (20, 20), card)
        put(img, frame_l, cx, cy, scale=0.94 + 0.06 * eback(prog(local, 0.0, 0.2)))
        # étiquette au-dessus du cadre
        if s.get("label"):
            put(img, tag_img(s["label"], PURPLE, WHITE, 68), cx, 255, scale=1.2 - 0.2 * eo(prog(lt, 0.0, 0.2)),
                alpha=prog(lt, 0.0, 0.15))
        # gros mots en bas du cadre
        ys = 1130 if len(s["big"]) <= 2 else 1115
        for m, (txt, col) in enumerate(s["big"]):
            p = prog(lt, 0.25 + m * 0.35, 0.22)
            if p > 0:
                put(img, text_img(txt, 120 if len(txt) > 12 else 150, col), cx, ys + m * 110,
                    scale=0.7 + 0.3 * eback(p), alpha=eo(p))
        # tampon
        if s.get("stamp"):
            label, col, at = s["stamp"]
            p = prog(lt, at * dur, 0.15)
            if p > 0:
                put(img, stamp_img(label, col), 790, 450, scale=2.0 - eo(p) if p < 1 else 1.0,
                    alpha=min(1.0, 2 * p), rot=-12)
        # légende du cadre
        put(img, tag_img("Clash of Clans · TH19", (30, 26, 40), GREY, 36), cx, 1290 + 1000 - 1000 + 0, alpha=0.0)
        # sous-titres
        img.alpha_composite(sub_layer(s["sub"], lt, dur), (0, 1440))
        # flash à chaque coupe
        cut_t = [k2 * (dur / n_shots) for k2 in range(n_shots)]
        for ct in cut_t:
            if 0 <= lt - ct < 0.08:
                img.alpha_composite(Image.new("RGBA", (W, H), (255, 255, 255, int(120 * (1 - (lt - ct) / 0.08)))))
    return img.convert("RGB")


def audio():
    N = int(TOTAL * SR) + SR
    voice = np.zeros(N); music = np.zeros(N); sfx = np.zeros(N)
    rng = np.random.default_rng(7)
    for i, s in enumerate(SCENES):
        with wave.open(os.path.join(PROJ, f"v{s['v']}.wav")) as w:
            x = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float64) / 32768
        a = int((START[i] + 0.12) * SR)
        voice[a:a + len(x)] += x * 0.95
    beat = 0.5
    tt = np.arange(int(0.5 * SR)) / SR
    kick = np.sin(2 * np.pi * (55 + 90 * np.exp(-tt * 40)) * tt) * np.exp(-tt * 9)
    hat_n = rng.standard_normal(int(0.06 * SR)) * np.exp(-np.arange(int(0.06 * SR)) / SR * 90)
    k = 0
    while k * beat < TOTAL:
        a = int(k * beat * SR)
        music[a:a + len(kick)] += kick * 0.55
        if k % 2 == 1:
            music[a:a + len(hat_n)] += hat_n * 0.12
        k += 1
    chords = [(220.0, 261.63, 329.63), (174.61, 220.0, 261.63), (261.63, 329.63, 392.0), (196.0, 246.94, 293.66)]
    c = 0
    while c * 2.0 < TOTAL:
        a = int(c * 2.0 * SR); L = int(2.0 * SR)
        tp = np.arange(L) / SR
        env = np.minimum(1, tp / 0.25) * np.exp(-np.maximum(0, tp - 1.2) * 3)
        pad = sum(np.sin(2 * np.pi * f * tp) for f in chords[c % 4]) / 3
        L2 = min(L, len(music) - a)
        music[a:a + L2] += (pad * env)[:L2] * 0.35
        c += 1
    # SFX : whoosh + pop à chaque coupe de plan, pop à chaque mot-clé
    wl = int(0.3 * SR)
    wn = rng.standard_normal(wl) * np.hanning(wl)
    wn = np.convolve(wn, np.ones(40) / 40, mode="same")
    pl = int(0.09 * SR); pt = np.arange(pl) / SR
    pop = np.sin(2 * np.pi * 880 * pt) * np.exp(-pt * 45)
    for i, s in enumerate(SCENES):
        dur = DUR[i]
        if s.get("gauge"):
            n_shots = 1
        else:
            n_shots = max(1, round(dur / SHOT))
        for k2 in range(n_shots):
            a = int((START[i] + k2 * (dur / n_shots)) * SR)
            sfx[a:a + wl] += wn * 0.3
        for m in range(len(s["big"])):
            a = int((START[i] + 0.25 + m * 0.35) * SR)
            sfx[a:a + pl] += pop * 0.5
    mix = voice + music * 0.3 + sfx
    mix = mix / max(1.0, np.max(np.abs(mix)) / 0.92)
    pcm = (mix * 32767).astype(np.int16)
    with wave.open(MIXNAME, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes(np.repeat(pcm[:, None], 2, axis=1).tobytes())


def _chunk(args):
    a, b, part = args
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
           "-c:v", "libx264", "-preset", "veryfast", "-crf", "19", "-pix_fmt", "yuv420p", part]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for fi in range(a, b):
        p.stdin.write(frame(fi / FPS).tobytes())
    p.stdin.close(); p.wait()
    return part


def render():
    from multiprocessing import Pool
    total = int(TOTAL * FPS) + 1
    n = 4
    step = -(-total // n)
    jobs = [(k * step, min(total, (k + 1) * step), os.path.join(PROJ, f"part{k}.mp4")) for k in range(n) if k * step < total]
    with Pool(2) as pool:
        parts = pool.map(_chunk, jobs)
    lst = os.path.join(PROJ, "parts.txt")
    open(lst, "w").write("".join(f"file '{p}'\n" for p in parts))
    subprocess.check_call(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst, "-i", MIXNAME,
                           "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", OUTNAME])
    for p in parts: os.remove(p)
    print("frames", total, "duree", round(TOTAL, 2), OUTNAME)


if __name__ == "__main__":
    audio()
    render()
