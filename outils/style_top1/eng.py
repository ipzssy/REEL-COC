import os, sys, json, math, subprocess, random
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from functools import lru_cache
from multiprocessing import Pool

R = os.path.dirname(os.path.abspath(__file__))
S = os.path.dirname(R)
W, H, FPS = 1080, 1920, 30
FONT = R + "/Luckiest.ttf"
YEL = (255, 214, 40); WHT = (255, 255, 255); PINK = (255, 90, 170); GRN = (90, 230, 80)
RED = (235, 30, 30); CYA = (80, 200, 255); ORG = (255, 150, 30)

def ease_out_back(x):
    x = max(0, min(1, x)); c1 = 2.2; c3 = c1 + 1
    return 1 + c3 * (x - 1) ** 3 + c1 * (x - 1) ** 2

@lru_cache(None)
def fnt(sz): return ImageFont.truetype(FONT, int(sz))

@lru_cache(None)
def load(p, w=None):
    im = Image.open(p).convert("RGBA")
    if w: im = im.resize((int(w), int(im.height * w / im.width)), Image.LANCZOS)
    return im

@lru_cache(None)
def text_layer(txt, sz, fill, strokew):
    f = fnt(sz); st = int(sz * strokew)
    b = ImageDraw.Draw(Image.new("L", (4, 4))).textbbox((0, 0), txt, font=f, stroke_width=st)
    w, h = b[2] - b[0] + 20, b[3] - b[1] + 20
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.text((10 - b[0] + 0, 14 - b[1] + 6), txt, font=f, fill=(0, 0, 0, 255), stroke_width=st, stroke_fill=(0, 0, 0, 255))
    d.text((10 - b[0], 10 - b[1]), txt, font=f, fill=fill + (255,), stroke_width=st, stroke_fill=(0, 0, 0, 255))
    return im

def fit_size(txt, sz, maxw=960):
    w = ImageDraw.Draw(Image.new("L", (4, 4))).textlength(txt, font=fnt(sz))
    return sz if w <= maxw else sz * maxw / w

def paste_c(frame, layer, cx, cy, s=1.0, rot=0, alpha=1.0):
    if s != 1.0:
        layer = layer.resize((max(1, int(layer.width * s)), max(1, int(layer.height * s))), Image.BILINEAR)
    if rot: layer = layer.rotate(rot, expand=True, resample=Image.BILINEAR)
    if alpha < 1:
        a = layer.getchannel("A").point(lambda v: int(v * alpha)); layer = layer.copy(); layer.putalpha(a)
    frame.paste(layer, (int(cx - layer.width / 2), int(cy - layer.height / 2)), layer)

class Scene:
    def __init__(s, t0, t1, bg, items, name=""):
        s.t0, s.t1, s.bg, s.items, s.name = t0, t1, bg, items, name

# ---------- items ----------
def pop(txt, a, b, cy, sz, col=WHT, rot=0, cx=540, stroke=0.13, maxw=960):
    def f(fr, t):
        if not (a <= t < b): return
        k = (t - a) / 0.22; s = ease_out_back(k) if k < 1 else 1.0
        z = fit_size(txt, sz, maxw)
        paste_c(fr, text_layer(txt, int(z), col, stroke), cx, cy, s * (1 + 0.012 * math.sin(t * 9)), rot)
    return f

def image(path, a, b, cx, cy, w, rot=0, shadow=True, pulse=0.0):
    def f(fr, t):
        if not (a <= t < b): return
        k = (t - a) / 0.28; s = ease_out_back(k) if k < 1 else 1.0
        s *= 1 + pulse * math.sin((t - a) * 6)
        im = load(path, w)
        paste_c(fr, im, cx, cy, s, rot)
    return f

def fmt(n): return f"{n:,}".replace(",", " ")

def counter(icon, val, a, b, cy, sz=150, col=WHT, dur=0.55):
    def f(fr, t):
        if not (a <= t < b): return
        k = (t - a) / 0.25; s = ease_out_back(k) if k < 1 else 1.0
        v = int(val * min(1, (t - a) / dur) ** 0.6)
        txt = fmt(v)
        tl = text_layer(txt, sz, col, 0.1); ic = load(R + "/" + icon, 150)
        tw = tl.width + ic.width + 14
        lay = Image.new("RGBA", (tw, max(tl.height, ic.height)), (0, 0, 0, 0))
        lay.paste(ic, (0, (lay.height - ic.height) // 2), ic)
        lay.paste(tl, (ic.width + 14, (lay.height - tl.height) // 2), tl)
        paste_c(fr, lay, 540, cy, s if lay.width * s < 1040 else 1040 / lay.width)
    return f

def flash(a, d=0.12):
    def f(fr, t):
        if a <= t < a + d:
            ov = Image.new("RGBA", (W, H), (255, 255, 255, int(150 * (1 - (t - a) / d)))); fr.alpha_composite(ov)
    return f

def card(level, a, b, cx, cy, w=380, tilt=0, col=(120, 50, 200)):
    def f(fr, t):
        if not (a <= t < b): return
        k = (t - a) / 0.3; s = ease_out_back(k) if k < 1 else 1.0
        h = int(w * 1.25)
        lay = Image.new("RGBA", (w + 40, h + 40), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
        d.rounded_rectangle((20, 24, w + 20, h + 24), 36, fill=(0, 0, 0, 150))
        d.rounded_rectangle((12, 12, w + 12, h + 12), 36, fill=col, outline=(255, 215, 90), width=8)
        d.rounded_rectangle((34, 34, w - 10, h - 10), 26, fill=tuple(int(c * 0.55) for c in col))
        ic = load(S + "/proj/img/axe_cut.png", w - 60)
        lay.paste(ic, (30 + 0, 60), ic)
        d.ellipse((w - 120, -6, w + 30, 144), fill=(255, 190, 40), outline=(90, 40, 0), width=7)
        tl = text_layer(str(level), 78 if level > 9 else 90, WHT, 0.1)
        lay.paste(tl, (w - 45 - tl.width // 2, 69 - tl.height // 2), tl)
        paste_c(fr, lay, cx, cy, s, tilt)
    return f

def shield(a, b, cx, cy, sz=330):
    def f(fr, t):
        if not (a <= t < b): return
        k = (t - a) / 0.3; s = ease_out_back(k) if k < 1 else 1.0
        lay = Image.new("RGBA", (sz, int(sz * 1.2)), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
        pts = [(sz * .5, 6), (sz - 10, sz * .16), (sz - 22, sz * .7), (sz * .5, sz * 1.14), (22, sz * .7), (10, sz * .16)]
        d.polygon(pts, fill=(120, 70, 10), outline=(70, 35, 0))
        pts2 = [(sz * .5, 24), (sz - 34, sz * .2), (sz - 44, sz * .67), (sz * .5, sz * 1.04), (44, sz * .67), (34, sz * .2)]
        d.polygon(pts2, fill=(255, 200, 40))
        d.ellipse((sz * .22, sz * .22, sz * .78, sz * .78), fill=(255, 245, 210), outline=(150, 90, 0), width=8)
        ang = (t - a) * 2 * math.pi * 1.0
        c = (sz * .5, sz * .5)
        d.line((c[0], c[1], c[0] + 70 * math.sin(ang), c[1] - 70 * math.cos(ang)), fill=(60, 30, 0), width=10)
        d.line((c[0], c[1], c[0] + 44 * math.sin(ang / 12), c[1] - 44 * math.cos(ang / 12)), fill=(60, 30, 0), width=13)
        paste_c(fr, lay, cx, cy, s, math.sin(t * 5) * 4)
    return f

def rframe(path, a, b, cx, cy, w, hgt=None, border=(110, 230, 90), rad=44):
    def f(fr, t):
        if not (a <= t < b): return
        k = (t - a) / 0.3; s = ease_out_back(k) if k < 1 else 1.0
        im = load(path, w - 24); hh = hgt or im.height + 24
        lay = Image.new("RGBA", (w + 30, hh + 30), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
        d.rounded_rectangle((15, 15, w + 15, hh + 15), rad, fill=(20, 30, 20, 255), outline=border, width=12)
        lay.paste(im, (27, 27 + (hh - 24 - im.height) // 2), im)
        paste_c(fr, lay, cx, cy, s)
    return f

def stamp(txt, a, b, cy, sz=70, col=(255, 190, 40)):
    def f(fr, t):
        if a <= t < b:
            paste_c(fr, text_layer(txt, sz, col, 0.1), 540, cy, 1, -4)
    return f

def header(txt="CLASH CENTER"):
    def f(fr, t):
        paste_c(fr, text_layer(txt, 46, (255, 255, 255), 0.12), 540, 90, 1)
    return f

# ---------- backgrounds ----------
def grass():
    rnd = np.random.RandomState(3)
    base = np.zeros((H, W, 3), np.float32); base[:] = (70, 165, 45)
    n = rnd.rand(H // 8, W // 8).astype(np.float32)
    n = np.array(Image.fromarray((n * 255).astype(np.uint8)).resize((W, H), Image.BICUBIC)).astype(np.float32) / 255
    base += (n[..., None] - .5) * 55
    yy = (np.arange(H)[:, None] // 90 % 2) * 12
    base += yy[..., None]
    return Image.fromarray(np.clip(base, 0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(2)).convert("RGBA")

def sky():
    y = np.linspace(0, 1, H)[:, None, None]
    top = np.array([40, 110, 220]); bot = np.array([170, 220, 255])
    arr = (top * (1 - y) + bot * y) * np.ones((1, W, 1))
    return Image.fromarray(arr.astype(np.uint8)).convert("RGBA")

def black(): return Image.new("RGBA", (W, H), (0, 0, 0, 255))

class VidBG:
    """stream cropped portrait frames from a gameplay clip via ffmpeg"""
    def __init__(s, clip, ss, dur, blur=0, dim=0.55, zoom=1.0, cropx=0.5):
        s.args = (clip, ss, dur, blur, dim, zoom, cropx); s.p = None; s.i = -1; s.fr = None
    def start(s):
        clip, ss, dur, blur, dim, zoom, cropx = s.args
        pr = json.loads(subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v", "-show_entries", "stream=width,height", "-of", "json", R + "/" + clip], capture_output=True, text=True).stdout)["streams"][0]
        vw, vh = pr["width"], pr["height"]
        cw = int(vh * 9 / 16 / zoom); ch = int(vh / zoom)
        x = int((vw - cw) * cropx)
        vf = f"crop={cw}:{ch}:{x}:{int((vh-ch)/2)},scale={W}:{H}:flags=lanczos" + (f",gblur=sigma={blur}" if blur else "")
        s.p = subprocess.Popen(["ffmpeg", "-v", "error", "-ss", str(ss), "-t", str(dur + 1), "-i", R + "/" + clip, "-vf", vf, "-r", str(FPS),
                                "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
    def get(s, i):
        if s.p is None: s.start()
        while s.i < i:
            buf = s.p.stdout.read(W * H * 3)
            if len(buf) < W * H * 3: break
            s.fr = np.frombuffer(buf, np.uint8).reshape(H, W, 3); s.i += 1
        a = s.fr.astype(np.float32) * (1 - s.args[4])
        return Image.fromarray(a.astype(np.uint8)).convert("RGBA")

class ImgBG:
    """zoomed, blurred still (e.g. cinematic)"""
    def __init__(s, path, blur=0, dim=0.0, z0=1.0, z1=1.12, fit="cover", fy=0.5):
        s.path, s.blur, s.dim, s.z0, s.z1, s.fy = path, blur, dim, z0, z1, fy
    def get(s, i, n):
        im = load(s.path); k = i / max(1, n)
        z = s.z0 + (s.z1 - s.z0) * k
        sc = max(W / im.width, H / im.height) * z
        r = im.resize((int(im.width * sc), int(im.height * sc)), Image.BILINEAR)
        x = (r.width - W) // 2; y = int((r.height - H) * s.fy)
        o = r.crop((x, y, x + W, y + H))
        if s.blur: o = o.filter(ImageFilter.GaussianBlur(s.blur))
        if s.dim: o = Image.blend(o, Image.new("RGBA", o.size, (0, 0, 0, 255)), s.dim)
        return o

class Static:
    def __init__(s, im, drift=0): s.im, s.drift = im, drift
    def get(s, i, n):
        if not s.drift: return s.im.copy()
        dx = int(math.sin(i / 20) * s.drift)
        return Image.fromarray(np.roll(np.array(s.im), dx, axis=1))

def blurred_wall(clip, ss, dur, dim=0.5):
    return VidBG(clip, ss, dur, blur=14, dim=dim, zoom=1.0, cropx=0.5)

# ---------- scene definitions ----------
I = S + "/proj/img/"
def build_axe():
    sc = []
    # 0: intro, battle
    sc.append(Scene(0, 3.9, VidBG("clip_17h06.mp4", 22, 4.2, blur=2, dim=0.45, zoom=1.0), [
        pop("UN NOUVEL", 0.0, 0.36, 1050, 200, WHT, -3),
        pop("ÉQUIPEMENT", 0.36, 0.7, 1050, 190, YEL, 2),
        pop("LÉGENDAIRE", 0.7, 1.14, 1050, 190, WHT, -2),
        pop("ARRIVE SUR", 1.14, 1.52, 1050, 190, WHT, 2),
        pop("CLASH OF CLANS", 1.52, 2.44, 1050, 175, YEL, -2),
        pop("UNE TOUTE NOUVELLE", 2.44, 3.04, 1350, 130, WHT, 0),
        pop("RARETÉ", 3.04, 3.9, 1350, 230, YEL, -3),
        rframe(R + "/Barbarian_King_info_4.png", 2.3, 3.9, 540, 500, 440, hgt=440),
    ], "intro"))
    # 1: barbarian king / axe
    sc.append(Scene(3.9, 6.4, Static(sky(), 14), [
        image(R + "/Barbarian_King_info_4.png", 3.9, 6.4, 540, 1180, 880),
        rframe(I + "axe_cut.png", 4.5, 6.4, 540, 540, 420, 420),
        pop("COMMENÇONS PAR", 3.9, 4.62, 250, 120, WHT),
        pop("LA HACHE DU BLIZZARD", 4.62, 5.66, 250, 110, CYA),
        pop("ROI DES BARBARES", 5.66, 6.4, 250, 130, YEL),
        flash(3.9),
    ], "king"))
    # 2: craft event
    sc.append(Scene(6.4, 11.5, ImgBG(I + "craft_event.png", blur=0, dim=0.15, z0=1.25, z1=1.7, fy=0.5), [
        pop("ÉVÉNEMENT", 7.2, 7.58, 260, 150, WHT),
        pop("DE CRAFT", 7.58, 8.3, 260, 170, YEL),
        pop("OU DIRECT", 8.3, 9.02, 260, 150, WHT),
        pop("NIVEAU 15", 9.02, 9.74, 260, 190, YEL),
        pop("AVEC LE", 9.74, 10.06, 260, 150, WHT),
        pop("PASSE PAYANT", 10.06, 11.5, 260, 150, YEL),
        shield(9.74, 11.5, 540, 1500),
        flash(6.4),
    ], "craft"))
    # 3a: cinematic + level 33
    sc.append(Scene(11.5, 13.5, ImgBG(I + "axe_scene.png", dim=0.1, z0=1.1, z1=1.3), [
        pop("LES LÉGENDAIRES", 11.66, 12.78, 1500, 130, WHT),
        pop("NIVEAU 33", 12.78, 13.5, 1500, 230, YEL),
        flash(11.5),
    ], "cine"))
    # 3b: grass 28-30 TH16
    gr = grass()
    sc.append(Scene(13.5, 16.4, Static(gr, 10), [
        pop("NIVEAUX", 13.58, 13.8, 420, 190, WHT, -2),
        pop("28 À 30", 13.8, 14.66, 420, 260, YEL, 2),
        pop("DÉBLOQUÉS", 14.66, 15.08, 1060, 150, WHT),
        pop("HDV 16", 15.08, 16.4, 1060, 210, YEL),
        image(R + "/Town_Hall16.png", 15.1, 16.4, 540, 1500, 560),
        flash(13.5),
    ], "g1"))
    # 3c: 31-33 TH18
    sc.append(Scene(16.4, 19.2, Static(gr, 10), [
        pop("ET LES NIVEAUX", 16.5, 16.86, 420, 130, WHT),
        pop("31 À 33", 16.86, 17.8, 420, 260, YEL, -2),
        pop("DÉBLOQUÉS", 17.8, 18.5, 1060, 150, WHT),
        pop("HDV 18", 18.5, 19.2, 1060, 210, YEL),
        image(R + "/Town_Hall18_info1.png", 18.0, 19.2, 540, 1520, 640),
        flash(16.4),
    ], "g2"))
    # 4: costs
    sc.append(Scene(19.2, 25.7, blurred_wall("clip_17h17.mp4", 30, 6.5, 0.45), [
        card(33, 19.3, 25.7, 540, 560, 400),
        pop("POUR TOUT MAXER", 19.3, 20.7, 1000, 120, WHT),
        counter("Shiny_Ore.png", 79760, 20.78, 25.7, 1060, 160, WHT),
        counter("Glowy_Ore.png", 5100, 23.34, 25.7, 1290, 160, WHT),
        counter("Starry_Ore.png", 705, 24.74, 25.7, 1520, 160, YEL),
        flash(19.2),
    ], "cost"))
    # 5a: PANIC
    sc.append(Scene(25.7, 26.76, Static(black()), [
        pop("PAS DE", 25.7, 26.04, 760, 170, WHT),
        pop("PANIQUE", 26.04, 26.76, 960, 250, RED, -4),
    ], "panic"))
    # 5b: cheaper
    sc.append(Scene(26.76, 30.7, blurred_wall("clip_17h19.mp4", 40, 4.2, 0.5), [
        card(1, 26.9, 30.7, 300, 520, 320, -6, (140, 60, 210)),
        card(27, 27.2, 30.7, 780, 520, 320, 6, (140, 60, 210)),
        pop("NIVEAUX 1 À 27", 26.86, 27.94, 920, 120, WHT),
        pop("MOINS CHER", 27.94, 28.28, 1080, 190, GRN),
        pop("LUMINEUX", 28.28, 28.66, 1280, 190, PINK),
        pop("ÉTOILÉS", 28.66, 29.02, 1280, 190, YEL),
        pop("QUE LES", 29.02, 29.22, 1480, 140, WHT),
        pop("ÉPIQUES", 29.22, 30.7, 1480, 220, PINK),
        flash(26.76),
    ], "cheaper"))
    # 6: future epics
    sc.append(Scene(30.7, 37.2, blurred_wall("clip_17h25.mp4", 60, 6.6, 0.5), [
        image(R + "/Barbarian_King_info_4.png", 30.7, 37.2, 540, 560, 600),
        pop("TOUS LES FUTURS", 30.84, 31.62, 1020, 110, WHT),
        pop("ÉPIQUES", 31.62, 31.98, 1020, 200, PINK),
        pop("COÛTENT PAREIL", 31.98, 32.68, 1020, 140, YEL),
        counter("Starry_Ore.png", 430, 32.68, 37.2, 1300, 170, YEL),
        counter("Glowy_Ore.png", 3550, 34.48, 37.2, 1520, 170, WHT),
        stamp("À CONFIRMER", 34.48, 37.2, 1740, 60),
        flash(30.7),
    ], "future"))
    # 7: outro, one word at a time
    words = [("LES", 37.34, 37.62, WHT, 260), ("ANCIENS", 37.62, 37.94, WHT, 240), ("ÉPIQUES", 37.94, 38.14, PINK, 240),
             ("SERONT", 38.14, 38.42, WHT, 240), ("AUSSI", 38.42, 38.66, WHT, 260), ("MOINS", 38.66, 38.92, GRN, 260),
             ("CHERS", 38.92, 39.08, GRN, 260), ("AVEC LE", 39.08, 39.28, WHT, 230), ("TEMPS", 39.28, 39.8, YEL, 380)]
    items = [pop("LES", 37.2, 37.62, 960, 260)] if False else []
    items += [pop(t, a if i else 37.2, b, 960, z, c, (-3 if i % 2 else 3)) for i, (t, a, b, c, z) in enumerate(words)]
    sc.append(Scene(37.2, 39.7, VidBG("clip_17h06.mp4", 60, 3.0, blur=3, dim=0.5, zoom=1.0, cropx=0.3), items, "outro"))
    return sc


KNOTS = [(0.0, 0.0)]
def g(t):
    k = KNOTS
    if t <= k[0][0]: return t
    for (o0, n0), (o1, n1) in zip(k, k[1:]):
        if t <= o1: return n0 + (t - o0) * (n1 - n0) / max(1e-9, o1 - o0)
    return k[-1][1] + (t - k[-1][0])
def ginv(tn):
    k = KNOTS
    for (o0, n0), (o1, n1) in zip(k, k[1:]):
        if tn <= n1: return o0 + (tn - n0) * (o1 - o0) / max(1e-9, n1 - n0)
    return k[-1][0] + (tn - k[-1][1])

def make_knots(words, shrink=0.14, thr=0.3, end=None):
    """words: [(w,start,end)] original times -> knots compressing pauses"""
    k = [(0.0, 0.0)]; new = 0.0; prev_o = 0.0
    for i in range(1, len(words)):
        e, s = words[i-1][2], words[i][1]
        if s - e > thr:
            new += e - prev_o; k.append((e, new)); new += shrink; k.append((s, new)); prev_o = s
    return k

BUILDS = {"axe": build_axe}
CUR = {"name": "axe"}

def render_scene(idx):
    scn = BUILDS[CUR["name"]]()[idx]
    ta, tb = g(scn.t0), g(scn.t1)
    n = int(round((tb - ta) * FPS))
    out = f"{R}/{CUR['name']}_sc_{idx}.mp4"
    p = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
    for i in range(n):
        t = ginv(ta + i / FPS)
        t = max(scn.t0, min(scn.t1 - 1e-4, t))
        bg = scn.bg
        fr = bg.get(i) if isinstance(bg, VidBG) else bg.get(i, n)
        fr = fr.convert("RGBA")
        for it in scn.items: it(fr, t)
        p.stdin.write(fr.convert("RGB").tobytes())
    p.stdin.close(); p.wait()
    return idx

def assemble(name, audio_wav, outmp4):
    n = len(BUILDS[name]())
    with open(f"{R}/{name}_list.txt", "w") as f:
        for i in range(n): f.write(f"file '{name}_sc_{i}.mp4'\n")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", f"{R}/{name}_list.txt", "-i", audio_wav,
                    "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", outmp4], check=True)
