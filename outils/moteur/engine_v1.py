"""Generic motion-design reel engine (style of reel_coc_v12). Run with cwd = video folder (spec.json + voice/)."""
import subprocess, os, sys, math, re, json
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from tl import *

W, H = 1080, 1920
BLACKF = "/usr/share/fonts/opentype/inter/InterDisplay-Black.otf"
BOLDF = "/usr/share/fonts/opentype/inter/Inter-Bold.otf"
XBF = "/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf"
WHITE = (245, 245, 245); RED = (236, 38, 56); GREY = (95, 95, 100); BG = (11, 11, 14); PAPER = (250, 250, 248); INK = (10, 10, 10)
BANK = os.path.join(HERE, "..", "..", "banque")
SC = SPEC["scenes"]
TXT = [s["text"] for s in SC]
STOP = {"le", "la", "les", "de", "des", "du", "un", "une", "et", "ou", "à", "au", "aux", "en", "tu", "te", "ta", "ton", "tes",
        "ce", "ces", "c'est", "qui", "que", "pour", "sur", "pas", "ne", "se", "sa", "son", "ses", "est", "il", "ils", "elle",
        "elles", "on", "mais", "dans", "avec", "par", "plus", "si", "lui", "leur", "leurs", "toi", "moi", "y", "a", "d'un", "d'une"}
KEY = set()
for s in SC:
    for k in ("stamp",):
        if s.get(k): KEY.add(s[k][0])
    for tg in s.get("tags", []) + s.get("flow", []):
        KEY.add(tg[0])
    for k in ("qword", "cword"):
        if s.get(k): KEY.add(s[k])
KEY |= {"erreur", "solution", "résultat", "commentaire", "clash", "clans"}

_fc = {}
def F(path, sz):
    k = (path, sz)
    if k not in _fc: _fc[k] = ImageFont.truetype(path, sz)
    return _fc[k]

def norm(w):
    return re.sub(r"[^\wéèêàâùûôîçœ'%-]", "", w.lower())

def is_key(w):
    n = norm(w)
    return any(n.startswith(k.lower()) or n.split("'")[-1].startswith(k.lower()) for k in KEY)

# ------------------------------------------------------------------ timing
def chunks(text):
    out, cur = [], []
    for w in text.split():
        if w in (":", "?", "!", "%"):
            if w != ":": cur[-1] += (" " + w if w in "?!%" else w)
            continue
        if cur and (len(cur) >= 3 or len(" ".join(cur + [w])) > 20):
            out.append(cur); cur = []
        cur.append(w)
    if cur: out.append(cur)
    return out

_wt = {}
def word_times(i):
    if i in _wt: return _wt[i]
    ws = [w for c in chunks(TXT[i]) for w in c]
    L = [len(w) + 2 for w in ws]; tot = sum(L); t = LEAD; out = []
    for w, l in zip(ws, L):
        d = VD[i] * l / tot; out.append((t, t + d, w)); t += d
    _wt[i] = out
    return out

def wt(i, word):
    word = word.lower()
    for a, b, w in word_times(i):
        n = norm(w)
        if n.startswith(word) or n.split("'")[-1].startswith(word):
            return a
    print(f"[warn] scene {i}: word '{word}' not found", file=sys.stderr)
    return LEAD + 0.5

# ------------------------------------------------------------------ easing
def cl(x, a=0.0, b=1.0): return max(a, min(b, x))
def eo(p): p = cl(p); return 1 - (1 - p) ** 3
def eback(p, s=1.8):
    p = cl(p); p -= 1; return p * p * ((s + 1) * p + s) + 1
def prog(t, t0, d): return cl((t - t0) / d)

# ------------------------------------------------------------------ background
def make_bg():
    im = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(im, "RGBA")
    hor = 1020; vx = W / 2
    for k in range(-14, 15):
        x = vx + k * 150
        d.line([(vx + k * 18, hor), (x + (x - vx) * 2.2, H)], fill=(255, 255, 255, 16), width=2)
    for j in range(1, 16):
        y = hor + (H - hor) * (j / 15) ** 1.8
        d.line([(0, y), (W, y)], fill=(255, 255, 255, 14), width=2)
    for j in range(0, 12):
        d.line([(0, j * 90), (W, j * 90)], fill=(255, 255, 255, 5), width=1)
    v = Image.new("L", (W, H), 0); ImageDraw.Draw(v).ellipse([-300, -200, W + 300, H + 200], fill=255)
    v = v.filter(ImageFilter.GaussianBlur(220))
    return Image.composite(im, Image.new("RGB", (W, H), (0, 0, 0)), v)
BGIM = make_bg()

# ------------------------------------------------------------------ elements
_tc = {}
def title(text, sz, col=WHITE, squeeze=0.74, shadow=True, maxw=980):
    k = (text, sz, col, squeeze, maxw)
    if k in _tc: return _tc[k]
    f = F(BLACKF, sz); bb = f.getbbox(text)
    w, h = bb[2] - bb[0] + 20, bb[3] - bb[1] + 30
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    if shadow: d.text((10 - bb[0] + 6, 10 - bb[1] + 10), text, font=f, fill=(0, 0, 0, 170))
    d.text((10 - bb[0], 10 - bb[1]), text, font=f, fill=col + (255,))
    nw = int(w * squeeze); nh = h
    if nw > maxw: nh = int(h * maxw / nw); nw = maxw
    im = im.resize((max(1, nw), max(1, nh)), Image.LANCZOS)
    _tc[k] = im
    return im

def paste_c(dst, im, cx, cy, scale=1.0, alpha=1.0, rot=0.0):
    if alpha <= 0.01 or scale <= 0.01: return
    if scale != 1.0:
        im = im.resize((max(1, int(im.width * scale)), max(1, int(im.height * scale))), Image.BILINEAR)
    if rot: im = im.rotate(rot, resample=Image.BICUBIC, expand=True)
    if alpha < 1.0:
        a = im.getchannel("A").point(lambda v: int(v * alpha)); im = im.copy(); im.putalpha(a)
    dst.paste(im, (int(cx - im.width / 2), int(cy - im.height / 2)), im)

def tag(text, bgc, fg, sz=50, padx=26, pady=12, maxw=980):
    k = ("tag", text, bgc, fg, sz)
    if k in _tc: return _tc[k]
    while sz > 26 and F(XBF, sz).getlength(text) + 2 * padx > maxw: sz -= 2
    f = F(XBF, sz); bb = f.getbbox(text)
    w, h = bb[2] - bb[0] + 2 * padx, bb[3] - bb[1] + 2 * pady
    im = Image.new("RGBA", (w + 12, h + 12), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rectangle([8, 10, w + 8, h + 10], fill=(0, 0, 0, 150))
    d.rectangle([0, 0, w, h], fill=bgc + (255,))
    d.text((padx - bb[0], pady - bb[1]), text, font=f, fill=fg + (255,))
    _tc[k] = im
    return im

def stamp(text, sz=140):
    k = ("stamp", text, sz)
    if k in _tc: return _tc[k]
    t = title(text, sz, RED, 0.72, shadow=False, maxw=600)
    pad = 34
    im = Image.new("RGBA", (t.width + 2 * pad, t.height + 2 * pad - 10), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rectangle([4, 4, im.width - 5, im.height - 5], outline=RED + (255,), width=12)
    im.paste(t, (pad, pad - 10), t)
    rng = np.random.default_rng(len(text))
    a = np.array(im.getchannel("A")).astype(np.float32)
    im.putalpha(Image.fromarray((a * (rng.random(a.shape) > 0.10) * 0.95).astype(np.uint8)))
    _tc[k] = im
    return im

def card(frame, caption=None, style="polaroid"):
    fw, fh = frame.size
    if style == "polaroid":
        b, bb = 20, (96 if caption else 20)
        im = Image.new("RGBA", (fw + 2 * b + 14, fh + b + bb + 14), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        d.rectangle([10, 12, fw + 2 * b + 10, fh + b + bb + 12], fill=(0, 0, 0, 140))
        d.rectangle([0, 0, fw + 2 * b, fh + b + bb], fill=PAPER + (255,))
        im.paste(frame, (b, b))
        if caption:
            d.text(((fw + 2 * b) / 2, fh + b + bb / 2 + 2), caption, font=F(XBF, 46), fill=(15, 15, 15, 255), anchor="mm")
    else:
        foot = 120
        im = Image.new("RGBA", (fw + 14, fh + foot + 14), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        d.rectangle([10, 12, fw + 10, fh + foot + 12], fill=(0, 0, 0, 150))
        d.rectangle([0, 0, fw, fh + foot], fill=(24, 24, 28, 255))
        im.paste(frame, (0, 0))
        d.rectangle([0, fh, fw, fh + 6], fill=(60, 60, 64, 255))
        d.rectangle([0, fh, int(fw * 0.62), fh + 6], fill=RED + (255,))
        d.rounded_rectangle([18, 16, 150, 58], radius=8, fill=RED + (255,))
        d.text((84, 37), "● REPLAY", font=F(XBF, 24), fill=(255, 255, 255, 255), anchor="mm")
        d.text((24, fh + 30), caption or "Clash of Clans", font=F(XBF, 40), fill=(240, 240, 240, 255))
        d.text((24, fh + 80), "Clash of Clans · attaque", font=F(BOLDF, 26), fill=(150, 150, 155, 255))
    return im

def gauge(frac, w=150, h=420):
    im = Image.new("RGBA", (w + 200, h + 170), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    x0 = 100
    d.rounded_rectangle([x0, 0, x0 + w, h], radius=18, fill=(30, 30, 34, 255), outline=(55, 55, 60, 255), width=3)
    fh = int((h - 12) * cl(frac))
    if fh > 0: d.rounded_rectangle([x0 + 6, h - 6 - fh, x0 + w - 6, h - 6], radius=12, fill=(245, 245, 245, 255))
    d.text((x0 + w / 2, h + 55), "?", font=F(BLACKF, 64), fill=WHITE + (255,), anchor="mm")
    return im

def shake_at(t, t0, amp=20, dur=0.28):
    dd = t - t0
    if 0 <= dd < dur:
        k = (1 - dd / dur)
        return [amp * k * math.sin(dd * 90), amp * 0.75 * k * math.cos(dd * 70)]
    return [0.0, 0.0]

# ------------------------------------------------------------------ subtitles
def subtitles(img, i, t):
    wts = word_times(i); groups = []; k = 0
    for c in chunks(TXT[i]):
        groups.append(wts[k:k + len(c)]); k += len(c)
    g = None
    for gi, grp in enumerate(groups):
        end = groups[gi + 1][0][0] if gi + 1 < len(groups) else SCENES[i]
        if grp[0][0] - 0.05 <= t < end: g = grp
    if g is None: return
    sz = 54
    while True:
        f = F(XBF, sz); sp = f.getlength(" ")
        widths = [f.getlength(w) for _, _, w in g]; tw = sum(widths) + sp * (len(g) - 1)
        if tw < 980 or sz <= 36: break
        sz -= 2
    x = (W - tw) / 2; d = ImageDraw.Draw(img)
    for (a, b, w), wl in zip(g, widths):
        col = (RED if is_key(w) else WHITE) if t >= a else GREY
        d.text((x + 3, 1516), w, font=f, fill=(0, 0, 0), anchor="lm")
        d.text((x, 1512), w, font=f, fill=col, anchor="lm")
        x += wl + sp

# ------------------------------------------------------------------ video source
CLIPS = {"A1": "attaque_01_nettoyage_finale", "A2": "attaque_02_attaque_entiere_th15", "H1": "capacites_heros_01_invisibilite",
         "T1": "troupes_01_super_dragons_masse", "T2": "troupes_02_groupes_separes", "D1": "defenses_01_tirs_croises",
         "E1": "ecran_fin_01_3_etoiles", "HV1": "hotel_de_ville_01_effondrement", "HV2": "hotel_de_ville_02_effondrement",
         "R1": "remparts_01_explosion", "S1": "sorts_01_tremblement_de_terre", "S2": "sorts_02_lanceur_de_bucher",
         "S3": "sorts_03_rage", "S4": "sorts_04_gel", "S5": "sorts_05_foudre_tremblement", "V1": "village_01_vue_ensemble"}

class Clip:
    def __init__(self, key, ss, dur, w=960, h=540, crop=None):
        vf = (crop + "," if crop else "") + f"scale={w}:{h}:flags=lanczos,unsharp=5:5:0.4"
        self.w, self.h = w, h
        self.p = subprocess.Popen(["ffmpeg", "-loglevel", "quiet", "-ss", str(ss), "-t", str(dur + 0.5),
                                   "-i", os.path.join(BANK, CLIPS[key] + ".mp4"), "-vf", vf, "-r", "30", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                                  stdout=subprocess.PIPE)
        self.idx = -1; self.cur = Image.new("RGB", (w, h), (0, 0, 0))
    def get(self, t):
        want = int(t * 30)
        while self.idx < want:
            raw = self.p.stdout.read(self.w * self.h * 3)
            if len(raw) < self.w * self.h * 3: break
            self.cur = Image.frombytes("RGB", (self.w, self.h), raw); self.idx += 1
        return self.cur
    def close(self):
        try: self.p.stdout.close(); self.p.kill()
        except Exception: pass

def setup(i):
    s = SC[i]; D = SCENES[i]
    if s["kind"] == "hook": return Clip(s["clip"], s["ss"], D, 540, 960, "crop=608:1080:560:0")
    if s["kind"] == "versus": return None
    return Clip(s["clip"], s["ss"], D, 960 if s.get("card") == "video" else 800, 540 if s.get("card") == "video" else 450)

# ------------------------------------------------------------------ scenes
def draw_head(img, t, main, sub, big):
    p = prog(t, 0.0, 0.28)
    if big:
        paste_c(img, title(main, 250), W / 2, 300 + 40 * (1 - eo(p)), scale=1.25 - 0.25 * eo(p), alpha=p)
        if sub:
            q = prog(t, 0.18, 0.25)
            paste_c(img, title(sub, 155, RED), W / 2, 495, scale=1.3 - 0.3 * eo(q), alpha=q)
    else:
        paste_c(img, title(main, 170), W / 2, 250 + 40 * (1 - eo(p)), scale=1.25 - 0.25 * eo(p), alpha=p)

def draw_scene(i, t, clip, img):
    s = SC[i]; kind = s["kind"]; sh = [0.0, 0.0]
    def addsh(v):
        sh[0] += v[0]; sh[1] += v[1]
    if kind == "hook":
        q = prog(t, 0.2, 0.22)
        paste_c(img, title(s.get("top", "CLASH OF CLANS"), 120), W / 2, 210, alpha=q, scale=1.15 - 0.15 * eo(q))
        p = prog(t, 0.0, 0.35)
        fr = clip.get(t)
        ph = Image.new("RGBA", (600, 1030), (0, 0, 0, 0)); d = ImageDraw.Draw(ph)
        d.rounded_rectangle([0, 0, 599, 1029], radius=70, fill=(28, 28, 32, 255), outline=(70, 70, 76, 255), width=6)
        ph.paste(fr, (30, 40))
        d.rounded_rectangle([230, 52, 370, 86], radius=17, fill=(0, 0, 0, 255))
        paste_c(img, ph, W / 2, 880 + 120 * (1 - eo(p)), scale=(0.82 + 0.18 * eback(p)) * 0.86, alpha=p)
        w0, txt = s["stamp"]; ts = wt(i, w0)
        if t >= ts:
            q = prog(t, ts, 0.14)
            paste_c(img, stamp(txt), W / 2, 900, scale=2.0 - eo(q), rot=12, alpha=min(1, 2 * q)); addsh(shake_at(t, ts, 22))
        if s.get("tag"):
            w1, txt1 = s["tag"]; tt_ = wt(i, w1)
            if t >= tt_:
                q = prog(t, tt_, 0.18)
                paste_c(img, tag(txt1, PAPER, INK, 50), W / 2 + 60, 1350, scale=1.3 - 0.3 * eo(q), rot=-3, alpha=q)
        addsh(shake_at(t, 0.0, 26, 0.3))
    elif kind == "std":
        main, sub = s["head"]; big = bool(sub)
        draw_head(img, t, main, sub, big)
        fr = clip.get(t); style = s.get("card", "polaroid")
        c = card(fr, s.get("cap"), style)
        tags = s.get("tags", []); flow = s.get("flow", [])
        p = prog(t, 0.45 if big else 0.25, 0.35)
        if big:
            if tags or flow:
                paste_c(img, c, W / 2, 930 + 250 * (1 - eo(p)), scale=0.8 if style == "video" else 0.9, alpha=p, rot=0 if style == "video" else 3)
                ty = [1320, 1415]
            else:
                if style == "polaroid":
                    paste_c(img, c, W / 2 + 480 * (1 - eo(p)), 1040, rot=5 - 3 * eo(p), alpha=p)
                else:
                    paste_c(img, c, W / 2, 1040 + 200 * (1 - eo(p)), scale=0.9 + 0.1 * eo(p), alpha=p)
                ty = []
            sy = 1010
        else:
            paste_c(img, c, W / 2, 760 + 150 * (1 - eo(p)), scale=(0.92 + 0.08 * eo(p)) if style == "video" else 1.0, alpha=p, rot=0 if style == "video" else -2)
            ty = [1190, 1282, 1374]; sy = 1250
        if s.get("result"): addsh(shake_at(t, 0.0, 24, 0.3))
        for k, tg in enumerate(tags[:len(ty)]):
            w0, txt = tg[0], tg[1]; red = len(tg) < 3 or tg[2] == "r"
            t0 = wt(i, w0)
            if t >= t0:
                q = prog(t, t0, 0.16)
                paste_c(img, tag(txt, RED if red else PAPER, WHITE if red else INK, 50), W / 2, ty[k], scale=1.25 - 0.25 * eo(q), alpha=q)
        if flow:
            ys = [1190, 1370] if not big else [1300, 1440]
            for k, (w0, txt) in enumerate(flow[:2]):
                t0 = wt(i, w0)
                if t >= t0:
                    q = prog(t, t0, 0.18)
                    paste_c(img, tag(txt, RED if k == 0 else PAPER, WHITE if k == 0 else INK, 50), W / 2, ys[k], scale=1.3 - 0.3 * eo(q), alpha=q)
            t1 = wt(i, flow[1][0]) - 0.35
            if t >= t1:
                q = eo(prog(t, t1, 0.3)); d = ImageDraw.Draw(img)
                y0 = ys[0] + 40; y1 = y0 + (ys[1] - ys[0] - 80) * q
                d.line([(W / 2, y0), (W / 2, y1)], fill=WHITE, width=9)
                if q > 0.9: d.polygon([(W / 2, y1 + 6), (W / 2 - 20, y1 - 22), (W / 2 + 20, y1 - 22)], fill=WHITE)
        if s.get("stamp"):
            w0, txt = s["stamp"]; t0 = wt(i, w0)
            if t >= t0:
                q = prog(t, t0, 0.14)
                yy = sy if not (big and (tags or flow)) else 930
                paste_c(img, stamp(txt, 130), W / 2 + 60, yy, scale=2 - eo(q), rot=-10 if i % 2 else 9, alpha=min(1, 2 * q))
                addsh(shake_at(t, t0, 18, 0.25))
    elif kind == "versus":
        (n1, n2), (s1, s2) = s["names"], s["subs"]
        ta = wt(i, s["w1"]); tb = wt(i, s["w2"])
        for k, (tk, name, sub, cx) in enumerate([(ta, n1, s1, W / 2 - 230), (tb, n2, s2, W / 2 + 230)]):
            if t >= tk - 0.15:
                q = prog(t, tk - 0.15, 0.25)
                paste_c(img, title(name, 120, maxw=440), cx, 250, alpha=q, scale=1.2 - 0.2 * eo(q))
                if sub: paste_c(img, title(sub, 64, (150, 150, 155), maxw=440), cx, 345, alpha=q)
                fill = 0.15 + 0.75 * (0.5 + 0.5 * math.sin(t * (5 + 2 * k) + k))
                paste_c(img, gauge(fill * eo(q)), cx, 690, alpha=q)
        tq = wt(i, s["qword"])
        if t >= tq:
            q = prog(t, tq, 0.2)
            paste_c(img, title("?", 330, RED), W / 2, 690, scale=1.6 - 0.6 * eback(q), alpha=q)
        tc = wt(i, s["cword"]) - 0.4
        if t >= tc:
            q = prog(t, tc, 0.2)
            paste_c(img, title("TON AVIS ?", 170), W / 2, 1090, alpha=q, scale=1.2 - 0.2 * eo(q))
            paste_c(img, tag("EN COMMENTAIRE", RED, WHITE, 54), W / 2, 1240, alpha=q, scale=1.25 - 0.25 * eo(q))
            paste_c(img, tag("DISCORD : LIEN EN BIO", PAPER, INK, 40), W / 2, 1345, alpha=prog(t, tc + 0.4, 0.25))
    return sh

def scene_events(i):
    s = SC[i]; E = []
    def ev(t, k): E.append((round(STARTS[i] + t, 3), k))
    ev(0.0, "whoosh")
    if s["kind"] == "hook":
        ev(0.0, "boom"); ev(wt(i, s["stamp"][0]), "stamp")
        if s.get("tag"): ev(wt(i, s["tag"][0]), "pop")
    elif s["kind"] == "std":
        main = s["head"][0]
        if main.startswith("ERREUR") or main.startswith("PIÈGE"): ev(0.05, "buzz")
        elif s.get("result"): ev(0.0, "boom")
        else: ev(0.05, "ding")
        if s.get("stamp"): ev(wt(i, s["stamp"][0]), "stamp")
        for tg in s.get("tags", [])[:3] + s.get("flow", [])[:2]: ev(wt(i, tg[0]), "pop")
    else:
        ev(wt(i, s["w1"]), "pop"); ev(wt(i, s["w2"]), "pop"); ev(wt(i, s["qword"]), "boom"); ev(wt(i, s["cword"]) - 0.4, "ding")
    return E

def frame(i, t, clip):
    img = BGIM.copy()
    dx, dy = draw_scene(i, t, clip, img)
    subtitles(img, i, t)
    z = 1.0 + 0.035 * t / SCENES[i]
    vw, vh = W / z, H / z
    x0 = (W - vw) / 2 + dx; y0 = (H - vh) / 2 + dy
    return img.transform((W, H), Image.EXTENT, (x0, y0, x0 + vw, y0 + vh), Image.BILINEAR)

def render(i):
    nf = int(round(SCENES[i] * FPS)); clip = setup(i)
    os.makedirs("shots", exist_ok=True)
    out = f"shots/s{i}.mp4"
    enc = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                            "-c:v", "libx264", "-preset", "veryfast", "-b:v", "11M", "-maxrate", "12M", "-minrate", "10M", "-bufsize", "24M",
                            "-g", "60", "-pix_fmt", "yuv420p", out + ".part.mp4"], stdin=subprocess.PIPE)
    for k in range(nf):
        enc.stdin.write(frame(i, k / FPS, clip).tobytes())
    enc.stdin.close(); enc.wait()
    if clip: clip.close()
    assert enc.returncode == 0
    os.rename(out + ".part.mp4", out)

if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "sheet":  # one still per scene at the busiest moment (near the end)
        ims = []
        for i in range(NSHOTS):
            c = setup(i); ims.append(frame(i, SCENES[i] * 0.85, c).resize((270, 480))); c and c.close()
        sh = Image.new("RGB", (270 * min(5, NSHOTS), 480 * ((NSHOTS + 4) // 5)))
        for k, im in enumerate(ims): sh.paste(im, ((k % 5) * 270, (k // 5) * 480))
        sh.save("sheet.png")
    elif cmd == "events":
        E = []
        for i in range(NSHOTS): E += scene_events(i)
        json.dump(sorted(E), open("events.json", "w"))
    elif cmd == "render":
        for i in [int(x) for x in sys.argv[2:]] or range(NSHOTS):
            render(i)
