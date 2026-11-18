#!/usr/bin/env python3
"""Short « pro » : plans FIXES (aucun zoom ni déplacement d'image), captures plein cadre,
mises en avant (projecteur), compteurs et cartes animés. Usage : python3 -I short_pro.py <dossier_projet>
Le dossier contient img/, v0.wav..vN.wav et scenes.json (liste de scènes, voir le code de scene_fn)."""
import json, math, os, subprocess, sys, wave
import numpy as np
from functools import lru_cache
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS, SR = 1080, 1920, 30, 44100
BLACK = "/usr/share/fonts/opentype/inter/Inter-Black.otf"
BOLD = "/usr/share/fonts/opentype/inter/Inter-Bold.otf"
GOLD = (255, 196, 40); ICE = (120, 215, 255); RED = (226, 32, 44); WHITE = (250, 250, 250); GREY = (150, 156, 170)
PROJ = os.path.abspath(sys.argv[1])
IMG = os.path.join(PROJ, "img") + "/"
SC = json.load(open(os.path.join(PROJ, "scenes.json")))
PAD = 0.3

DUR = []
for k in range(len(SC)):
    with wave.open(os.path.join(PROJ, f"v{k}.wav")) as w:
        DUR.append(w.getnframes() / w.getframerate())
LEN = [d + PAD + (0.8 if k == len(SC) - 1 else 0) for k, d in enumerate(DUR)]
START = [sum(LEN[:i]) for i in range(len(LEN))]
TOTAL = sum(LEN)


def cl(x, a=0.0, b=1.0): return max(a, min(b, x))
def eo(p): return 1 - (1 - cl(p)) ** 3
def eback(p, s=1.6):
    p = cl(p); return 1 + (s + 1) * (p - 1) ** 3 + s * (p - 1) ** 2
def prog(t, t0, d): return cl((t - t0) / d)


@lru_cache(maxsize=None)
def font(path, size): return ImageFont.truetype(path, size)


@lru_cache(maxsize=None)
def bg():
    im = Image.new("RGB", (W, H)); px = np.zeros((H, W, 3), np.float32)
    yy, xx = np.mgrid[0:H, 0:W]
    t = np.clip(np.hypot((xx - W / 2) / 900, (yy - H * 0.45) / 1200), 0, 1)
    c0 = np.array([22, 28, 48], np.float32); c1 = np.array([6, 7, 12], np.float32)
    px = c0 * (1 - t[..., None]) + c1 * t[..., None]
    return Image.fromarray(px.astype(np.uint8)).convert("RGBA")


def tlayer(s, size, fill, f=BLACK, maxw=1000, stroke=0, letter=0):
    fo = font(f, size)
    while fo.getlength(s) + letter * len(s) > maxw and size > 24:
        size -= 4; fo = font(f, size)
    d0 = ImageDraw.Draw(Image.new("L", (1, 1)))
    bb = d0.textbbox((0, 0), s, font=fo, stroke_width=stroke)
    pad = 24
    L = Image.new("RGBA", (bb[2] - bb[0] + 2 * pad + int(letter * len(s)), bb[3] - bb[1] + 2 * pad), (0, 0, 0, 0))
    d = ImageDraw.Draw(L)
    if letter:
        x = pad
        for ch in s:
            d.text((x - bb[0], pad - bb[1]), ch, font=fo, fill=fill, stroke_width=stroke, stroke_fill=(0, 0, 0, 255)); x += fo.getlength(ch) + letter
    else:
        d.text((pad - bb[0], pad - bb[1]), s, font=fo, fill=fill, stroke_width=stroke, stroke_fill=(0, 0, 0, 255))
    return L


def put(img, L, cx, cy, scale=1.0, alpha=1.0):
    if alpha <= 0.01: return
    if scale != 1.0:
        L = L.resize((max(1, int(L.width * scale)), max(1, int(L.height * scale))), Image.BILINEAR)
    if alpha < 1.0:
        L = L.copy(); L.putalpha(L.split()[3].point(lambda v: int(v * alpha)))
    img.alpha_composite(L, (int(cx - L.width / 2), int(cy - L.height / 2)))


def txt(img, s, size, cx, cy, fill=WHITE, f=BLACK, maxw=1000, stroke=0, p=1.0, pop=True, letter=0):
    L = tlayer(s, size, fill + (255,) if len(fill) == 3 else fill, f, maxw, stroke, letter)
    put(img, L, cx, cy, scale=(0.82 + 0.18 * eback(p)) if pop else 1.0, alpha=cl(p * 3))


def rect(img, box, fill=None, outline=None, width=0, radius=0, alpha=1.0):
    L = Image.new("RGBA", img.size, (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    d.rounded_rectangle(box, radius=radius, fill=(fill + (int(255 * alpha),)) if fill else None,
                        outline=(outline + (int(255 * alpha),)) if outline else None, width=width)
    img.alpha_composite(L)


@lru_cache(maxsize=None)
def pic(name, width):
    im = Image.open(IMG + name).convert("RGBA")
    return im.resize((width, int(im.height * width / im.width)), Image.LANCZOS)


def place_pic(img, name, y, p=1.0, width=W, x=0):
    im = pic(name, width)
    if p < 1.0:
        im = im.copy(); im.putalpha(im.split()[3].point(lambda v: int(v * cl(p))))
    img.alpha_composite(im, (x, y)); return im.height


def wipe_pic(img, name, y, p, width=W):
    im = pic(name, width); w = int(im.width * eo(p))
    if w > 0: img.alpha_composite(im.crop((0, 0, w, im.height)), (0, y))
    return im.height


def spotlight(img, y0, h, boxes, p):
    """assombrit l'image sauf les boîtes, contour or. Pas de mouvement : seulement fondu."""
    L = Image.new("RGBA", img.size, (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    d.rectangle((0, y0, W, y0 + h), fill=(0, 0, 0, int(150 * eo(p))))
    for (x1, y1, x2, y2) in boxes:
        d.rounded_rectangle((x1, y1, x2, y2), radius=14, fill=(0, 0, 0, 0))
    img.alpha_composite(L)
    for (x1, y1, x2, y2) in boxes:
        pulse = 0.75 + 0.25 * math.sin(p * 40)
        rect(img, (x1, y1, x2, y2), outline=GOLD, width=6, radius=14, alpha=eo(p) * pulse)


def bar(img, t):
    rect(img, (0, 0, W, 10), fill=(40, 44, 58))
    rect(img, (0, 0, int(W * t / TOTAL), 10), fill=GOLD)


def header(img, p):
    txt(img, "CLASH CENTER", 34, W / 2, 78, GREY, BOLD, p=p, pop=False, letter=8)


def captions(img, text, lt, dur):
    words = text.split()
    wts = [len(w) + 2 for w in words]; tot = sum(wts); acc = 0; idx = len(words) - 1
    for i, w in enumerate(wts):
        acc += w
        if lt < dur * acc / tot: idx = i; break
    grp = idx // 4 * 4; chunk = words[grp:grp + 4]
    sizes = 76
    f = font(BLACK, sizes)
    total = sum(f.getlength(w + " ") for w in chunk)
    while total > 980 and sizes > 40:
        sizes -= 4; f = font(BLACK, sizes); total = sum(f.getlength(w + " ") for w in chunk)
    x = (W - total) / 2; y = 1640
    rect(img, (0, y - 70, W, y + 110), fill=(0, 0, 0), alpha=0.35)
    d = ImageDraw.Draw(img)
    for j, w in enumerate(chunk):
        col = GOLD if grp + j == idx else WHITE
        d.text((x, y), w, font=f, fill=col, stroke_width=7, stroke_fill=(0, 0, 0)); x += f.getlength(w + " ")


# ------------------------------------------------------------------ scènes
def s_hook(img, lt):
    base = pic("s0.png", 1080)
    # fond flou
    bgb = pic("s0.png", 1700).crop((300, 0, 1380, 956)).filter(ImageFilter.GaussianBlur(26)).convert("RGBA")
    dark = Image.new("RGBA", bgb.size, (0, 0, 0, 150)); bgb.alpha_composite(dark)
    img.alpha_composite(bgb, (0, 200))
    on = int(lt * 8) % 2 == 0 if lt < 0.6 else True
    rect(img, (0, 250, W, 370), fill=RED if on else (120, 14, 22))
    txt(img, "ATTENTION", 120, W / 2, 310, WHITE, BLACK, p=prog(lt, 0.0, 0.25), maxw=900, letter=6)
    txt(img, "NOUVEL", 150, W / 2, 500, WHITE, BLACK, p=prog(lt, 0.35, 0.3))
    txt(img, "ÉQUIPEMENT", 150, W / 2, 660, GOLD, BLACK, p=prog(lt, 0.6, 0.3), maxw=1000)
    rect(img, (0, 770, W, 776), fill=GOLD)
    place_pic(img, "s0.png", 776, p=prog(lt, 0.2, 0.3))
    rect(img, (0, 776 + 607, W, 776 + 613), fill=GOLD)
    txt(img, "LÉGENDAIRE", 110, W / 2, 1480, ICE, BLACK, p=prog(lt, 1.6, 0.3), letter=10)


def s_axe(img, lt):
    txt(img, "ROI DES BARBARES", 40, W / 2, 230, GREY, BOLD, p=prog(lt, 0, 0.3), pop=False, letter=6)
    txt(img, "HACHE DU", 130, W / 2, 360, WHITE, BLACK, p=prog(lt, 0.1, 0.3))
    txt(img, "BLIZZARD", 170, W / 2, 530, ICE, BLACK, p=prog(lt, 0.35, 0.3))
    # icône sur halo
    halo = Image.new("RGBA", (900, 900), (0, 0, 0, 0)); ImageDraw.Draw(halo).ellipse((100, 100, 800, 800), fill=(90, 190, 255, 120))
    halo = halo.filter(ImageFilter.GaussianBlur(90)); put(img, halo, W / 2, 1000, alpha=eo(prog(lt, 0.4, 0.5)))
    ic = pic("s3.png", 520); put(img, ic, W / 2, 1000, alpha=prog(lt, 0.4, 0.4))
    # échelle des raretés
    labels = [("COMMUN", GREY), ("ÉPIQUE", (190, 110, 255)), ("LÉGENDAIRE", GOLD)]
    for i, (s, c) in enumerate(labels):
        p = prog(lt, 1.2 + i * 0.5, 0.3)
        txt(img, s, 44 if i < 2 else 58, 190 + i * 350, 1380, c, BLACK, p=p, maxw=330)
        if i < 2: txt(img, ">", 50, 365 + i * 350, 1380, GREY, BLACK, p=p, pop=False)
    rect(img, (W / 2 + 260 - 200, 1425, W / 2 + 260 + 200 + 40, 1432), fill=GOLD, alpha=eo(prog(lt, 2.2, 0.3)))
    txt(img, "NOUVELLE RARETÉ", 42, W / 2, 1480, WHITE, BOLD, p=prog(lt, 2.6, 0.3), pop=False, letter=6)


def s_free(img, lt):
    txt(img, "GRATUIT", 190, W / 2, 290, GOLD, BLACK, p=prog(lt, 0.0, 0.3))
    txt(img, "ÉVÉNEMENT DE CRAFT", 66, W / 2, 470, WHITE, BLACK, p=prog(lt, 0.3, 0.3), maxw=1000)
    y0 = 560; hgt = place_pic(img, "s2.png", y0, p=prog(lt, 0.2, 0.3))
    k = W / 2048.0
    boxes = []
    for (a, b) in [(910, 185), (910, 528)]:
        boxes.append((int(a * 1.02 * k) - 4, y0 + int(b * 1.02 * k) - 6, int((a + 175) * 1.02 * k) + 4, y0 + int((b + 175) * 1.02 * k) + 6))
    p = prog(lt, 1.1, 0.5)
    if p > 0: spotlight(img, y0, hgt, boxes, p)
    txt(img, "DÈS L'HÔTEL DE VILLE", 54, W / 2, 1200, GREY, BOLD, p=prog(lt, 2.0, 0.3), pop=False, maxw=900)
    n = int(1 + 7 * eo(prog(lt, 2.0, 0.8)))
    txt(img, f"HDV {n}", 200, W / 2, 1400, WHITE, BLACK, p=prog(lt, 2.0, 0.2), pop=False)


def s_later(img, lt):
    txt(img, "TU RATES", 110, W / 2, 330, WHITE, BLACK, p=prog(lt, 0.0, 0.3))
    txt(img, "L'ÉVÉNEMENT ?", 110, W / 2, 470, GOLD, BLACK, p=prog(lt, 0.15, 0.3))
    items = [("01", "CHEZ LE MARCHAND"), ("02", "ÉVÉNEMENTS D'ÉQUIPEMENT"), ("03", "ET D'AUTRES SOURCES")]
    for i, (n, s) in enumerate(items):
        p = prog(lt, 1.0 + i * 0.9, 0.35); y = 760 + i * 230
        rect(img, (70, y - 85, W - 70, y + 85), fill=(28, 34, 56), outline=GOLD if i < 2 else (70, 76, 96), width=4, radius=26, alpha=eo(p))
        txt(img, n, 80, 170, y, GOLD if i < 2 else GREY, BLACK, p=p, pop=False)
        txt(img, s, 52, 620, y, WHITE if i < 2 else GREY, BLACK, p=p, pop=False, maxw=720)
    txt(img, "PAS DE PANIQUE", 70, W / 2, 1500, ICE, BLACK, p=prog(lt, 3.6, 0.3), letter=6)


def s_pass(img, lt):
    txt(img, "CRAFT PASS", 130, W / 2, 330, WHITE, BLACK, p=prog(lt, 0.0, 0.3))
    txt(img, "OPTIONNEL", 70, W / 2, 470, GREY, BOLD, p=prog(lt, 0.3, 0.3), pop=False, letter=10)
    v = 9.99 * eo(prog(lt, 0.4, 1.0))
    txt(img, f"{v:.2f}".replace(".", ",") + " $", 230, W / 2, 800, GOLD, BLACK, p=prog(lt, 0.4, 0.2), pop=False)
    for i, s in enumerate(["HACHE DÉJÀ NIVEAU 15", "PAS OBLIGATOIRE"]):
        p = prog(lt, 2.4 + i * 1.6, 0.35); y = 1150 + i * 200
        rect(img, (90, y - 80, W - 90, y + 80), fill=(28, 34, 56), outline=ICE if i == 0 else GOLD, width=4, radius=26, alpha=eo(p))
        txt(img, s, 58, W / 2, y, WHITE, BLACK, p=p, pop=False, maxw=860)


def s_level(img, lt):
    txt(img, "NIVEAU MAX", 100, W / 2, 250, WHITE, BLACK, p=prog(lt, 0.0, 0.3))
    n = int(1 + 32 * eo(prog(lt, 0.3, 1.4)))
    txt(img, str(n), 260, W / 2, 470, GOLD, BLACK, p=prog(lt, 0.3, 0.2), pop=False)
    y0 = 640; wipe_pic(img, "s1.png", y0, prog(lt, 0.4, 1.2))
    for i, (a, b) in enumerate([("HDV 16", "NIVEAUX 28 À 30"), ("HDV 18", "NIVEAUX 31 À 33")]):
        p = prog(lt, 2.2 + i * 1.8, 0.35); y = 1290 + i * 150
        rect(img, (90, y - 60, W - 90, y + 60), fill=(28, 34, 56), outline=GOLD, width=4, radius=22, alpha=eo(p))
        txt(img, a, 56, 290, y, GOLD, BLACK, p=p, pop=False, maxw=300)
        txt(img, b, 52, 700, y, WHITE, BLACK, p=p, pop=False, maxw=520)


def s_cost(img, lt):
    txt(img, "COÛT MAXIMUM", 96, W / 2, 280, WHITE, BLACK, p=prog(lt, 0.0, 0.3))
    txt(img, "HACHE DU BLIZZARD, NIVEAU 33", 40, W / 2, 400, GREY, BOLD, p=prog(lt, 0.2, 0.3), pop=False, letter=3, maxw=1000)
    rows = [("BRILLANT", 79760, (255, 205, 70), 1.0), ("LUMINEUX", 5100, (110, 230, 140), 2.3), ("ÉTOILÉ", 705, (255, 140, 60), 3.5)]
    for i, (name, val, col, t0) in enumerate(rows):
        p = prog(lt, t0, 0.35); y = 700 + i * 300
        rect(img, (70, y - 120, W - 70, y + 120), fill=(26, 32, 52), outline=col, width=5, radius=30, alpha=eo(p))
        v = int(val * eo(prog(lt, t0 + 0.1, 0.9)))
        s = f"{v:,}".replace(",", " ")
        txt(img, s, 140, W / 2, y - 20, col, BLACK, p=p, pop=False, maxw=900)
        txt(img, "MINERAI " + name, 44, W / 2, y + 80, WHITE, BOLD, p=p, pop=False, letter=4, maxw=900)


def s_advice(img, lt):
    txt(img, "GARDE TON", 120, W / 2, 270, WHITE, BLACK, p=prog(lt, 0.0, 0.3))
    txt(img, "MINERAI", 170, W / 2, 440, GOLD, BLACK, p=prog(lt, 0.2, 0.3))
    y0 = 620; wipe_pic(img, "s4.png", y0, prog(lt, 0.4, 1.0))
    txt(img, "AVANT D'AMÉLIORER UN ÉPIQUE", 52, W / 2, 1410, WHITE, BLACK, p=prog(lt, 1.6, 0.3), pop=False, maxw=1000)
    txt(img, "TU POURRAIS LE REGRETTER", 56, W / 2, 1500, RED, BLACK, p=prog(lt, 2.8, 0.3), maxw=1000)


def s_cta(img, lt):
    txt(img, "TON CHOIX ?", 150, W / 2, 320, WHITE, BLACK, p=prog(lt, 0.0, 0.3))
    for i, (letter, s, col) in enumerate([("A", "JE CRAFTE LA HACHE", ICE), ("B", "JE CONTINUE MES ÉPIQUES", (190, 110, 255))]):
        p = prog(lt, 0.5 + i * 0.4, 0.35); y = 760 + i * 330
        sc = 0.9 + 0.1 * eback(p)
        L = Image.new("RGBA", (940, 270), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
        d.rounded_rectangle((0, 0, 939, 269), radius=40, fill=(28, 34, 56, 255), outline=col + (255,), width=6)
        d.ellipse((40, 55, 200, 215), fill=col + (255,))
        d.text((120, 135), letter, font=font(BLACK, 120), fill=(10, 12, 20), anchor="mm")
        d.text((250, 135), s, font=font(BLACK, 42), fill=WHITE, anchor="lm")
        put(img, L, W / 2, y, scale=sc, alpha=eo(p))
    txt(img, "RÉPONDS EN COMMENTAIRE", 56, W / 2, 1360, GOLD, BLACK, p=prog(lt, 1.4, 0.3), pop=False)
    p = prog(lt, 2.8, 0.4)
    rect(img, (110, 1440, W - 110, 1560), fill=GOLD, radius=60, alpha=eo(p))
    txt(img, "DISCORD · LIEN EN BIO", 54, W / 2, 1500, (12, 12, 18), BLACK, p=p, pop=False, maxw=800)


FN = {"hook": s_hook, "axe": s_axe, "free": s_free, "later": s_later, "pass": s_pass, "level": s_level,
      "cost": s_cost, "advice": s_advice, "cta": s_cta}


def scene_at(t):
    for i in range(len(START) - 1, -1, -1):
        if t >= START[i]: return i, t - START[i]
    return 0, t


def frame(t):
    i, lt = scene_at(t)
    img = bg().copy()
    FN[SC[i]["fn"]](img, lt)
    header(img, prog(t, 0, 0.3)); bar(img, t)
    if SC[i]["fn"] != "cta": captions(img, SC[i]["text"], lt, DUR[i])
    return img


def audio():
    n = int(TOTAL * SR) + SR
    mix = np.zeros(n, np.float32)
    for i in range(len(SC)):
        with wave.open(os.path.join(PROJ, f"v{i}.wav")) as w:
            a = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
        s = int(START[i] * SR); mix[s:s + len(a)] += a * 0.95
        # tic de coupe discret
        tt = np.arange(int(0.12 * SR)) / SR
        mix[s:s + len(tt)] += (np.sin(2 * np.pi * 180 * tt) * np.exp(-tt * 30) * 0.28).astype(np.float32)
    # impact d'ouverture
    tt = np.arange(int(0.9 * SR)) / SR
    boom = np.sin(2 * np.pi * (70 - 30 * tt) * tt) * np.exp(-tt * 4) * 0.55
    rng = np.random.default_rng(1); nz = rng.standard_normal(len(tt)) * np.exp(-tt * 9) * 0.12
    mix[:len(tt)] += (boom + nz).astype(np.float32)
    # nappe grave discrète
    t2 = np.arange(n) / SR
    mix += (np.sin(2 * np.pi * 55 * t2) * 0.03 + np.sin(2 * np.pi * 82.4 * t2) * 0.02).astype(np.float32)
    mix = np.clip(mix, -0.98, 0.98)
    p = os.path.join(PROJ, "mix.wav")
    with wave.open(p, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((mix * 32767).astype(np.int16).tobytes())
    return p


def render():
    out = os.path.join(PROJ, "short_pro.mp4"); ap = audio()
    nf = int(TOTAL * FPS)
    pr = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                           "-i", ap, "-c:v", "libx264", "-preset", "fast", "-crf", "17", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k",
                           "-shortest", "-movflags", "+faststart", out], stdin=subprocess.PIPE)
    for k in range(nf):
        pr.stdin.write(frame(k / FPS).convert("RGB").tobytes())
    pr.stdin.close(); pr.wait(); print("ok", out, round(TOTAL, 2))


if __name__ == "__main__":
    if len(sys.argv) > 2 and sys.argv[2] == "still":
        for t in map(float, sys.argv[3:]):
            frame(t).convert("RGB").save(os.path.join(PROJ, f"still_{t}.png"))
    else:
        render()
