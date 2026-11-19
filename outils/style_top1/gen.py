import sys, re, json, math, subprocess, difflib, wave
import numpy as np
from PIL import Image, ImageDraw
import eng
from eng import *
from heroes import bob, glow, purple
S = eng.S
A = {"king": S+"/r/Barbarian_King_info_4.png", "queen": S+"/h/aq.png", "th18": S+"/r/Town_Hall18_info1.png", "th16": S+"/r/Town_Hall16.png",
 "th19": S+"/a/th19.png", "ad": S+"/e/ad15.png", "eagle": S+"/a/eagle.png", "rage": S+"/e/rage.png", "lightning": S+"/e/lightning.png",
 "tome": S+"/h/tome_e.png", "ed": S+"/e/ed_info.png", "dragon": S+"/e/dragon_info.png", "logl": S+"/a/logl.png", "wallb": S+"/a/wallb.png",
 "giant_bomb": S+"/a/giant_bomb.png", "air_bomb": S+"/a/air_bomb.png", "spring": S+"/a/spring.png", "air_mine": S+"/a/air_mine.png",
 "bomb": S+"/a/bomb.png", "hog": S+"/a/hog.png", "healer": S+"/a/healer.png", "lab15": S+"/a/lab15.png", "army_camp12": S+"/a/army_camp12.png",
 "clan_castle": S+"/a/clan_castle.png", "builder": S+"/a/builder.png", "gold": S+"/a/gold.png", "resources": S+"/a/resources.png",
 "bk_ko": S+"/h/bk_ko.png", "aq_ko": S+"/h/aq_ko.png", "wall16": S+"/a/wall16.png", "trophy": S+"/a/trophy.png"}
C = {"w": WHT, "y": YEL, "r": RED, "g": GRN, "c": CYA, "p": PINK, "o": ORG}
def tok(s): return re.findall(r"\w+", s.lower())

def img_auto(key, a, b, cx, cy, maxw, maxh, ph=0):
    p = A[key]
    def f(fr, t):
        if not (a <= t < b): return
        im = load(p); w = min(maxw, maxh * im.width / im.height)
        bob(p, a, b, cx, cy, w, 0, 12, 4, ph)(fr, t)
    return f
def star(a, b, cx, cy, sz=420):
    def f(fr, t):
        if not (a <= t < b): return
        k = (t - a) / 0.3; s = ease_out_back(k) if k < 1 else 1.0
        lay = Image.new("RGBA", (sz, sz), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
        pts = []
        for i in range(10):
            r = sz * 0.46 if i % 2 == 0 else sz * 0.2; an = -math.pi / 2 + i * math.pi / 5
            pts.append((sz / 2 + r * math.cos(an), sz / 2 + r * math.sin(an) + 8))
        d.polygon(pts, fill=(255, 200, 30), outline=(110, 60, 0)); d.line(pts + [pts[0]], fill=(110, 60, 0), width=14)
        paste_c(fr, lay, cx, cy, s, 6 * math.sin(t * 4))
    return f
def clock(a, b, cx, cy, sz=420):
    def f(fr, t):
        if not (a <= t < b): return
        k = (t - a) / 0.3; s = ease_out_back(k) if k < 1 else 1.0
        lay = Image.new("RGBA", (sz, sz), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
        d.ellipse((10, 10, sz - 10, sz - 10), fill=(250, 245, 230), outline=(30, 30, 30), width=18)
        c = sz / 2; ang = (t - a) * 2 * math.pi
        d.line((c, c, c + 150 * math.sin(ang), c - 150 * math.cos(ang)), fill=(220, 30, 30), width=14)
        d.line((c, c, c + 90 * math.sin(ang / 12), c - 90 * math.cos(ang / 12)), fill=(30, 30, 30), width=18)
        paste_c(fr, lay, cx, cy, s)
    return f
def bigtxt(txt, a, b, cy, sz, col):
    return pop(txt, a, b, cy, sz, col, -3)
def shake(txt, a, b, cy, sz, col):
    def f(fr, t):
        if a <= t < b: pop(txt, a, b, cy + int(8 * math.sin(t * 60)), sz, col, -3)(fr, t)
    return f

BG = {}
def mkbg(kind):
    if kind == "grass": return Static(grass(), 10)
    if kind == "purple": return Static(purple(), 10)
    if kind == "black": return Static(black())
    if kind == "sky": return Static(sky(), 14)
    k, clip, ss = kind.split(":"); ss = float(ss)
    if k == "b": return VidBG(clip, ss, 12, blur=3, dim=0.5, zoom=1.0)
    return blurred_wall(clip, ss, 12, 0.5)


TINTS = [(40, 110, 220), (150, 60, 210), (230, 130, 30), (30, 170, 170)]
class BlurBG:
    def __init__(s, path, tint, ph=0):
        s.ph = ph
        W2, H2 = 1320, 2340
        base = Image.new("RGBA", (W2, H2), tint + (255,))
        if path:
            im = load(path); sc = max(W2 / im.width, H2 / im.height) * 1.0
            r = im.resize((max(1, int(im.width * sc)), max(1, int(im.height * sc))), Image.BICUBIC)
            base.alpha_composite(r, ((W2 - r.width) // 2, (H2 - r.height) // 2)) if r.width <= W2 and r.height <= H2 else base.paste(r.crop(((r.width - W2) // 2, (r.height - H2) // 2, (r.width - W2) // 2 + W2, (r.height - H2) // 2 + H2)), (0, 0))
            base = base.filter(ImageFilter.GaussianBlur(22))
        ov = Image.new("RGBA", (W2, H2), tuple(int(c * 0.55) for c in tint) + (255,))
        base = Image.blend(base, ov, 0.35 if path else 1.0)
        arr = np.array(base).astype(np.float32)
        yy = np.linspace(0.0, 1.0, H2)[:, None, None]
        arr[..., :3] *= 0.8 * (0.55 + 0.55 * (1 - abs(yy - 0.45)))  # soft vignette
        # soft light band
        s.arr = np.clip(arr, 0, 255).astype(np.uint8)
        s.W2, s.H2 = W2, H2
    def get(s, i, n):
        dx = int(70 * math.sin(i / 45 + s.ph)); dy = int(70 * math.cos(i / 60 + s.ph))
        x = (s.W2 - W) // 2 + dx; y = (s.H2 - H) // 2 + dy
        return Image.fromarray(s.arr[y:y + H, x:x + W]).convert("RGBA")


class ClipWin:
    def __init__(s, clip, ss, a, b, cx, cy, w=980, h=520):
        s.clip, s.ss, s.a, s.b, s.cx, s.cy, s.w, s.h = clip, ss, a, b, cx, cy, w, h
        s.p = None; s.last = None
        m = Image.new("L", (w, h), 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, w - 1, h - 1), 36, fill=255); s.mask = m
        o = Image.new("RGBA", (w + 24, h + 24), (0, 0, 0, 0)); d = ImageDraw.Draw(o)
        d.rounded_rectangle((0, 0, w + 23, h + 23), 44, fill=(0, 0, 0, 255))
        d.rounded_rectangle((6, 6, w + 17, h + 17), 40, outline=(255, 255, 255, 255), width=8)
        s.frame = o
    def __call__(s, fr, t):
        if not (s.a <= t < s.b): return
        if s.p is None:
            s.p = subprocess.Popen(["ffmpeg", "-v", "error", "-ss", str(s.ss), "-i", R + "/" + s.clip, "-vf",
                f"scale={s.w}:{s.h}:force_original_aspect_ratio=increase,crop={s.w}:{s.h},fps={FPS}", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
        buf = s.p.stdout.read(s.w * s.h * 3)
        if len(buf) == s.w * s.h * 3: s.last = Image.fromarray(np.frombuffer(buf, np.uint8).reshape(s.h, s.w, 3))
        if s.last is None: return
        k = min(1.0, (t - s.a) / 0.2); sc_ = 0.92 + 0.08 * k
        lay = Image.new("RGBA", s.frame.size, (0, 0, 0, 0)); lay.alpha_composite(s.frame)
        lay.paste(s.last, (12, 12), s.mask)
        paste_c(fr, lay, s.cx, s.cy, sc_)

def align(script_toks, words):
    """times (start,end) for each script token using difflib against whisper words"""
    wt = [tok(w[0]) for w in words]; wtl = []; idx = []
    for i, t in enumerate(wt):
        for x in t: wtl.append(x); idx.append(i)
    sm = difflib.SequenceMatcher(None, script_toks, wtl, autojunk=False)
    T = [None] * len(script_toks)
    for blk in sm.get_matching_blocks():
        for k in range(blk.size): T[blk.a + k] = idx[blk.b + k]
    # interpolate
    n = len(T); known = [i for i in range(n) if T[i] is not None]
    if not known: raise SystemExit("no alignment")
    out = []
    for i in range(n):
        if T[i] is None:
            lo = max([k for k in known if k < i], default=None); hi = min([k for k in known if k > i], default=None)
            if lo is None: T[i] = T[hi]
            elif hi is None: T[i] = T[lo]
            else: T[i] = T[lo] + (T[hi] - T[lo]) * (i - lo) / (hi - lo)
    res = []
    for i in range(n):
        j = T[i]; a = int(math.floor(j)); fr = j - a
        s0 = words[a][1]; e0 = words[a][2]
        res.append(s0 + fr * (words[min(a + 1, len(words) - 1)][1] - s0) if fr else s0)
    # enforce monotonic
    for i in range(1, n): res[i] = max(res[i], res[i-1])
    return res

def build_video(spec, workdir):
    """spec: dict(id, scenes[], loop) ; workdir has voice.wav + words.json"""
    words = json.load(open(workdir + "/words.json"))
    scenes = spec["scenes"]; loop = spec["loop"]
    all_say = [s["say"] for s in scenes] + [loop["say"]]
    toks = []; owner = []
    for si, sy in enumerate(all_say):
        for t in tok(sy): toks.append(t); owner.append(si)
    times = align(toks, words)
    # scene start/end
    starts = []; pos = 0
    for si in range(len(all_say)):
        starts.append(times[owner.index(si)])
    vend = words[-1][2]
    out = []
    for si, sc in enumerate(scenes + [loop]):
        a = starts[si] if si else 0.0
        b = starts[si + 1] if si + 1 < len(starts) else vend + 0.1
        islast = si == len(scenes)
        base = scenes[0] if islast else sc
        # token positions inside scene
        sidx = [i for i, o in enumerate(owner) if o == si]
        stoks = [toks[i] for i in sidx]; stimes = [times[i] for i in sidx]
        items = [flash(a)] if si else []
        imgs = scenes[0].get("imgs", []) if islast else sc.get("imgs", [])
        head = None if islast else sc.get("head")
        yimg = 740 if head else 640
        cinfo = (scenes[0] if islast else sc).get("clip")
        n = len(imgs)
        pos_ = {1: [540], 2: [300, 790], 3: [200, 540, 880]}.get(n, [])
        mw, mh = {1: (760, 700), 2: (480, 620), 3: (320, 420)}.get(n, (400, 400))
        for k, im in enumerate(imgs):
            if im == "star": items.append(star(a, b, 540, yimg))
            elif im == "clock": items.append(clock(a, b, 540, yimg))
            elif im.startswith("big:"):
                tx, col = im[4:].rsplit("|", 1); items.append(bigtxt(tx, a, b, yimg, 330, C[col]))
            else: items.append(img_auto(im, a + 0.05 * k, b, pos_[k], yimg, mw, mh, k))
        if head:
            w1, w2, col = (head + ("r",))[:3] if len(head) == 2 else head
            tw = stimes[min(2, len(stimes) - 1)] if w2 else b
            items.append(pop(w1, a, tw if w2 else b, 230, 190, WHT))
            if w2: items.append(pop(w2, tw, b, 230, 240, C[col], -3))
        lines = loop["lines"] if islast else sc["lines"]
        cur = 0; li = []
        for (at, txt, col, *sz) in lines:
            want = tok(at)[0]; j = cur
            while j < len(stoks) and stoks[j] != want: j += 1
            if j >= len(stoks): j = min(cur, len(stoks) - 1)
            li.append((stimes[j], txt, col, sz[0] if sz else 150)); cur = j + 1
        li[0] = (a if li[0][0] - a < 0.5 else li[0][0], *li[0][1:])
        for k, (t0, txt, col, z) in enumerate(li):
            t1 = li[k + 1][0] if k + 1 < len(li) else b
            if t1 <= t0: t1 = t0 + 0.3
            items.append(pop(txt, t0, t1, 1350, int(z * 1.3), C[col], (-2 if k % 2 else 2)))
        bgk = (scenes[0]["bg"] if islast else sc["bg"])
        h1 = (head[0] if head else "")
        if si == len(scenes) - 1: tint = (120, 50, 200)
        elif h1 in ("ERREUR", "ATTENTION"): tint = (190, 40, 40)
        elif h1 == "RÉSULTAT": tint = (40, 160, 70)
        else: tint = TINTS[si % len(TINTS)]
        mainimg = next((A[k] for k in imgs if k in A), None)
        if mainimg and len(imgs) > 1 and si % 2: mainimg = A[[k for k in imgs if k in A][-1]]
        if cinfo:
            bgo = eng.VidBG(cinfo[0], cinfo[1], (b - a) * 1.3 + 1, dim=0.42, zoom=1.0, cropx=0.5)
        elif (si == 0 or islast) and bgk.startswith("b:") and spec.get("battle", False):
            bgo = mkbg(bgk)
        else:
            bgo = BlurBG(mainimg, tint, ph=si)
        out.append(Scene(a, b, bgo, items, f"s{si}"))
    return out, words

def make_audio(workdir, words, out_wav, end_orig, tail_wav=None):
    sr = 44100
    v = np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-i", workdir + "/voice.wav", "-ar", "44100", "-ac", "1", "-f", "s16le", "-"], capture_output=True).stdout, np.int16)
    k = eng.KNOTS
    parts = []
    for (o0, n0), (o1, n1) in zip(k, k[1:]):
        parts.append(v[int(o0 * sr):int(o0 * sr + (n1 - n0) * sr)])
    last_o, last_n = k[-1]
    parts.append(v[int(last_o * sr):int(end_orig * sr)])
    a = np.concatenate(parts)
    w = wave.open(out_wav, "wb"); w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr); w.writeframes(a.tobytes()); w.close()
    return len(a) / sr

def run(vid, spec, wd):
    from multiprocessing import Pool
    scenes, words = build_video(spec, wd)
    eng.KNOTS[:] = make_knots([(w[0], w[1], w[2]) for w in words], shrink=0.1, thr=0.2)
    end = words[-1][2] + 0.1
    eng.KNOTS.append((end, eng.g(words[-1][2]) + 0.1)) if False else None
    # extend knots to end
    last = eng.KNOTS[-1]
    eng.KNOTS.append((end + 0.5, last[1] + (end + 0.5 - last[0])))
    eng.BUILDS[vid] = lambda: build_video(spec, wd)[0]
    eng.CUR["name"] = vid
    n = len(scenes)
    with Pool(2) as p: p.map(eng.render_scene, range(n))
    dur = make_audio(wd, words, f"{wd}/{vid}.wav", end)
    eng.assemble(vid, f"{wd}/{vid}.wav", f"{wd}/{vid}.mp4")
    return dur
