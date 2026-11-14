# Générateur de miniatures, vidéos TikTok avec couverture et bannière (style « TOUT SAVOIR »).
# Prévu pour tourner dans le workbench Composio : exec(requests.get(RAW).text)
import os, re, math, random, json, subprocess, sys, requests
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops

UA = {'User-Agent': 'Mozilla/5.0'}
WD = os.environ.get('CC_WD', '/home/user/cc')
os.makedirs(WD, exist_ok=True)
FONT = WD + '/lg.ttf'
if not os.path.exists(FONT):
    open(FONT, 'wb').write(requests.get('https://github.com/google/fonts/raw/main/apache/luckiestguy/LuckiestGuy-Regular.ttf', headers=UA, timeout=60).content)


def dl(name):
    p = WD + '/' + re.sub(r"[^A-Za-z0-9._-]", '_', name)
    if not os.path.exists(p):
        r = requests.get('https://clashofclans.fandom.com/api.php', params={'action': 'query', 'titles': 'File:' + name, 'prop': 'imageinfo', 'iiprop': 'url', 'format': 'json'}, headers=UA, timeout=30)
        u = list(r.json()['query']['pages'].values())[0]['imageinfo'][0]['url']
        open(p, 'wb').write(requests.get(u, headers=UA, timeout=90).content)
    im = Image.open(p).convert('RGBA')
    return im.crop(im.split()[3].point(lambda v: 255 if v > 20 else 0).getbbox())


W, H = 1080, 1920


def base():
    cx, cy = W / 2, H * 0.53
    bg = Image.new('RGB', (W, H)); px = bg.load()
    for y in range(H):
        for x in range(W):
            t = min(math.hypot(x - cx, (y - cy) * 0.8) / 950, 1)
            px[x, y] = (int(215 - 110 * t), int(240 - 85 * t), int(80 - 45 * t))
    bg = bg.convert('RGBA'); ray = Image.new('L', (W, H), 0); rd = ImageDraw.Draw(ray)
    for i in range(22):
        a = i * math.pi * 2 / 22; a2 = a + 0.08
        rd.polygon([(cx, cy), (cx + 3000 * math.cos(a), cy + 3000 * math.sin(a)), (cx + 3000 * math.cos(a2), cy + 3000 * math.sin(a2))], fill=60)
    bg.paste((255, 255, 210, 255), (0, 0), ray.filter(ImageFilter.GaussianBlur(5)))
    return bg


def place(bg, im, maxw, maxh, x, y, rot=0):
    s = min(maxw / im.width, maxh / im.height, 1.1)  # jamais plus de 1.1x : pas de flou
    im = im.resize((int(im.width * s), int(im.height * s)), Image.LANCZOS)
    if rot:
        im = im.rotate(rot, resample=Image.BICUBIC, expand=True)
    a = im.split()[3]
    glow = Image.new('RGBA', im.size, (255, 255, 190, 0)); glow.putalpha(a.filter(ImageFilter.MaxFilter(15)).filter(ImageFilter.GaussianBlur(28)).point(lambda v: int(v * 0.85)))
    sh = Image.new('RGBA', im.size, (0, 0, 0, 0)); sh.putalpha(a.filter(ImageFilter.GaussianBlur(18)).point(lambda v: int(v * 0.5)))
    x = int(x - im.width / 2); y = int(y - im.height / 2)
    bg.alpha_composite(glow, (x, y)); bg.alpha_composite(sh, (x + 14, y + 26)); bg.alpha_composite(im, (x, y))


def word(bg, s, size, y, top, bot, angle=2, stroke=26):
    d = ImageDraw.Draw(bg)
    while True:
        f = ImageFont.truetype(FONT, size); bb = d.textbbox((0, 0), s, font=f)
        if bb[2] - bb[0] <= 980 or size < 60:
            break
        size -= 10
    pad = 90; L = Image.new('RGBA', (bb[2] - bb[0] + 2 * pad, bb[3] + 2 * pad), (0, 0, 0, 0))
    mk = Image.new('L', L.size, 0); ImageDraw.Draw(mk).text((pad - bb[0], pad), s, font=f, fill=255)
    o = mk.filter(ImageFilter.MaxFilter(stroke + 1))
    for k in range(20, 0, -2):
        L.paste((10, 10, 10, 255), (0, 0), ImageChops.offset(o, 0, k))
    L.paste((10, 10, 10, 255), (0, 0), o)
    g = Image.new('RGBA', L.size); gd = ImageDraw.Draw(g)
    for yy in range(L.height):
        t = min(max((yy - pad - bb[1]) / max(bb[3] - bb[1], 1), 0), 1)
        gd.line((0, yy, L.width, yy), fill=tuple(int(top[i] + (bot[i] - top[i]) * t) for i in range(3)) + (255,))
    L.paste(g, (0, 0), mk)
    L = L.rotate(angle, resample=Image.BICUBIC, expand=True)
    bg.alpha_composite(L, ((W - L.width) // 2, y))


Y = ((255, 250, 160), (255, 185, 15)); WT = ((255, 255, 255), (215, 215, 215)); R = ((255, 120, 110), (205, 25, 35))
# clé: (haut1, haut2, [(image, maxw, maxh, x, y, rotation)], (bas1, couleur), bas2)
SPECS = {
    'hdv19': ('TOUT', 'SAVOIR', [('Town Hall19.png', 1000, 900, 540, 1040, 0)], ('HDV19', WT), None),
    'preuve': ('HDV19', 'LA PREUVE', [('Town Hall19.png', 900, 820, 540, 1000, 0)], ('ÇA ARRIVE', R), 'TRÈS BIENTÔT'),
    'hammerjam': ('HAMMER', 'JAM', [('Hammer of Building.png', 430, 430, 830, 760, -20), ("Builder's Apprentice info.png", 760, 820, 470, 1040, 0)], ('-50%', R), 'FINIT DEMAIN'),
    '05': ('SANS', "L'ATTAQUER", [('Air Defense17.png', 600, 800, 540, 1000, 0)], ('FOUDRE', R), '+ SÉISME'),
    '06': ('TES HÉROS', 'MEURENT ?', [('Barbarian King info 4.png', 900, 860, 540, 1010, 0)], ('CAPACITÉS', R), 'LE SECRET'),
    '07': ('ARMÉE', 'FACILE', [('Electro Dragon info 3.png', 900, 860, 540, 1010, 0)], ('3 ÉTOILES', R), 'ÉLECTRO-DRAGONS'),
    '08': ('TON HDV', 'TIENT ?', [('Town Hall18 info1.png', 900, 820, 540, 1000, 0)], ('VOICI', R), 'POURQUOI'),
    '09': ('TU OUBLIES', 'ÇA', [('Wall19 beta.png', 390, 500, 340, 1000, 0), ('Wall19 beta.png', 390, 500, 740, 1000, 0)], ('LES REMPARTS', R), 'ERREUR N°1'),
    '10': ('10', 'SECONDES', [('Archer Queen info 3.png', 900, 860, 540, 1010, 0)], ('AVANT', R), "D'ATTAQUER"),
    '11': ('BLOQUÉ', 'À 90% ?', [('Barbarian-xx.png', 950, 820, 540, 1000, 0)], ('+10%', R), 'FACILE'),
    '12': ('SOUS-', 'ESTIMÉ', [('Log Launcher info.png', 980, 820, 540, 1000, 0)], ('LANCE-BÛCHES', R), 'TESTE-LE'),
    '13': ('NOUVEL', 'HDV ?', [('Town Hall19.png', 900, 820, 540, 1000, 0)], ("N'AMÉLIORE", R), 'PAS ÇA'),
    '14': ('PLUS DE', 'RESSOURCES', [('Elixir Cart info.png', 880, 820, 540, 1010, 0)], ('3 ASTUCES', R), 'FACILES'),
    '15': ('TROPHÉES', 'PERDUS ?', [('Trophy prev.png', 950, 820, 540, 1000, 0)], ('3 RAISONS', R), 'À CORRIGER'),
    '16': ('CLAN', 'MORT ?', [('Clan Castle14.png', 880, 820, 540, 1000, 0)], ('CHANGE', R), 'DE CLAN'),
    '17': ('ATTENTION', 'PIÈGE !', [('Archer Queen info 5.png', 760, 800, 460, 1030, 0), ('Giant Bomb info.png', 270, 270, 850, 1280, 0)], ('BOMBE', R), 'GÉANTE'),
    '18': ('DÉTRUIS', 'EN 1ER', [('Inferno Tower10 Multi.png', 520, 820, 330, 1010, 0), ('Scattershot7.png', 520, 560, 770, 1080, 0)], ('CES DÉFENSES', R), 'TOUT DE SUITE'),
    '19': ('3 PHASES', '3 ÉTOILES', [('Barbarian King info 2.png', 900, 860, 540, 1010, 0)], ('NE RATE', R), 'PAS ÇA'),
    '20': ('BASE', 'RASÉE ?', [('Eagle Artillery Level1 info.png', 770, 700, 540, 1000, 0)], ('3 ERREURS', R), 'À ÉVITER'),
}


def key_for(entry):
    v = entry['video']; m = re.search(r'coc_(\d\d)_', v)
    if m:
        return m.group(1)
    return 'preuve' if 'preuve' in v else 'hammerjam' if 'hammerjam' in v else 'hdv19'


def build_thumb(k):
    t1, t2, imgs, (b1, c1), b2 = SPECS[k]
    bg = base()
    for (n, mw, mh, x, y, rot) in imgs:
        place(bg, dl(n), mw, mh, x, y, rot)
    word(bg, t1, 290, -10, *Y); word(bg, t2, 290, 250, *WT)
    if b2:
        word(bg, b1, 260, 1350, *c1); word(bg, b2, 130, 1630, *WT, stroke=20)
    else:
        word(bg, b1, 290, 1380, *c1)
    p = f'{WD}/mini_{k}.jpg'; bg.convert('RGB').save(p, quality=92)
    return p


def ffmpeg():
    try:
        import imageio_ffmpeg
    except ImportError:
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-q', 'imageio-ffmpeg'], capture_output=True)
        import imageio_ffmpeg
    return imageio_ffmpeg.get_ffmpeg_exe()


def _info(FF, p):
    s = subprocess.run([FF, '-i', p], capture_output=True, text=True).stderr
    w, h = map(int, re.search(r'Video:.*?, (\d{3,4})x(\d{3,4})', s).groups())
    fps = re.search(r'([\d.]+) fps', s).group(1)
    m = re.search(r'Audio:.*?(\d{4,5}) Hz', s); sr = m.group(1) if m else '48000'
    d = re.search(r'Duration: (\d+):(\d+):([\d.]+)', s).groups()
    return w, h, fps, sr, int(d[0]) * 3600 + int(d[1]) * 60 + float(d[2])


def build_tiktok(k, video_url):
    """Vidéo + miniature 0,5 s à la fin. Renvoie (chemin, cover_ms)."""
    FF = ffmpeg(); thumb = build_thumb(k)
    src = f'{WD}/src_{k}.mp4'
    if not os.path.exists(src):
        open(src, 'wb').write(requests.get(video_url, timeout=180).content)
    w, h, fps, sr, _ = _info(FF, src); dst = f'{WD}/tiktok_{k}.mp4'
    fc = (f"[1:v]scale={w}:{h}:force_original_aspect_ratio=decrease,pad={w}:{h}:(ow-iw)/2:(oh-ih)/2,setsar=1,fps={fps},format=yuv420p[t];"
          f"[0:v]setsar=1,fps={fps},format=yuv420p[v0];[0:a]aresample={sr},aformat=channel_layouts=stereo[a0];[v0][a0][t][2:a]concat=n=2:v=1:a=1[v][a]")
    subprocess.run([FF, '-y', '-v', 'error', '-i', src, '-loop', '1', '-t', '0.5', '-i', thumb, '-f', 'lavfi', '-t', '0.5', '-i', f'anullsrc=r={sr}:cl=stereo',
                    '-filter_complex', fc, '-map', '[v]', '-map', '[a]', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '18', '-c:a', 'aac', '-b:a', '192k',
                    '-movflags', '+faststart', dst], check=True, capture_output=True)
    return dst, int((_info(FF, dst)[4] - 0.25) * 1000)


def put_banner(bg, im, w, cx, cy, rot=0, flip=False):
    s = min(w / im.width, 1.0); im = im.resize((int(im.width * s), int(im.height * s)), Image.LANCZOS)
    if flip:
        im = im.transpose(Image.FLIP_LEFT_RIGHT)
    if rot:
        im = im.rotate(rot, resample=Image.BICUBIC, expand=True)
    sh = Image.new('RGBA', im.size, (20, 10, 40, 0)); sh.putalpha(im.split()[3].filter(ImageFilter.GaussianBlur(16)).point(lambda v: int(v * 0.45)))
    x = int(cx - im.width / 2); y = int(cy - im.height / 2); bg.alpha_composite(sh, (x + 18, y + 28)); bg.alpha_composite(im, (x, y))


def build_banner(avec_texte=True):
    random.seed(11)
    BW, BH = 2560, 1440; CX, CY = 1280, 720
    bg = Image.new('RGB', (BW, BH)); d = ImageDraw.Draw(bg)
    for y in range(BH):
        t = y / BH; c1 = (60, 20, 110); c2 = (255, 140, 40)
        d.line((0, y, BW, y), fill=tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3)))
    bg = bg.convert('RGBA')
    ray = Image.new('L', (BW, BH), 0); rd = ImageDraw.Draw(ray)
    for i in range(36):
        a = i * math.pi * 2 / 36; a2 = a + 0.05
        rd.polygon([(CX, CY), (CX + 4000 * math.cos(a), CY + 4000 * math.sin(a)), (CX + 4000 * math.cos(a2), CY + 4000 * math.sin(a2))], fill=55)
    bg.paste((255, 220, 150, 255), (0, 0), ray.filter(ImageFilter.GaussianBlur(8)))
    gl = Image.new('L', (BW, BH), 0); ImageDraw.Draw(gl).ellipse((CX - 850, CY - 420, CX + 850, CY + 420), fill=230)
    bg.paste((255, 200, 90, 255), (0, 0), gl.filter(ImageFilter.GaussianBlur(150)))

    def smoke(n, yr, rr, col, alpha, blur):
        m = Image.new('L', (BW, BH), 0); md = ImageDraw.Draw(m)
        for i in range(n):
            x = random.randint(-200, BW + 200); y = random.randint(*yr); r = random.randint(*rr)
            md.ellipse((x - r, y - r * 0.6, x + r, y + r * 0.6), fill=alpha)
        L = Image.new('RGBA', (BW, BH), col + (255,)); L.putalpha(m.filter(ImageFilter.GaussianBlur(blur))); return L
    bg.alpha_composite(smoke(25, (900, 1500), (150, 320), (90, 40, 110), 170, 40))

    def bolt(x0, y0, x1, y1, width):
        pts = [(x0, y0)] + [(x0 + (x1 - x0) * i / 9 + random.randint(-60, 60), y0 + (y1 - y0) * i / 9 + random.randint(-40, 40)) for i in range(1, 9)] + [(x1, y1)]
        L = Image.new('RGBA', (BW, BH), (0, 0, 0, 0)); ImageDraw.Draw(L).line(pts, fill=(200, 120, 255, 255), width=width * 3, joint='curve')
        L = L.filter(ImageFilter.GaussianBlur(14)); ImageDraw.Draw(L).line(pts, fill=(255, 240, 255, 255), width=width, joint='curve'); return L
    for (a, b, c, e) in [(CX - 1100, CY - 480, CX - 300, CY + 60), (CX + 1100, CY - 460, CX + 320, CY + 40), (CX - 900, CY + 520, CX - 250, CY + 60), (CX + 950, CY + 500, CX + 260, CY + 80)]:
        bg.alpha_composite(bolt(a, b, c, e, 10))
    put_banner(bg, dl('Balloon 6.png'), 560, 360, 330, rot=12)
    put_banner(bg, dl('P.E.K.K.A info.png'), 640, 520, 980)
    put_banner(bg, dl('Hog Rider15.png'), 620, 2120, 1000, rot=-4, flip=True)
    put_banner(bg, dl('Dragon infobox2.png'), 560, 2210, 330, rot=-8, flip=True)
    db = Image.new('RGBA', (BW, BH), (0, 0, 0, 0)); dd = ImageDraw.Draw(db)
    for i in range(70):
        x = random.choice([random.randint(0, 850), random.randint(1710, BW)]); y = random.randint(0, BH); s = random.randint(10, 34)
        ang = random.random() * math.pi
        dd.polygon([(x + s * math.cos(ang + k * 2.1), y + s * 0.7 * math.sin(ang + k * 2.1)) for k in range(3)], fill=random.choice([(120, 70, 40, 255), (90, 90, 100, 255), (150, 100, 60, 255), (60, 40, 30, 255)]))
    bg.alpha_composite(db)
    bg.alpha_composite(smoke(60, (1250, 1560), (160, 320), (255, 245, 235), 255, 30))
    if not avec_texte:
        p = WD + '/banniere_fond.jpg'; bg.convert('RGB').save(p, quality=90)
        return p
    size, y = 260, CY - 215; dd = ImageDraw.Draw(bg); s = 'CLASH CENTER'
    f = ImageFont.truetype(FONT, size); bb = dd.textbbox((0, 0), s, font=f)
    while bb[2] - bb[0] > 1480:
        size -= 8; f = ImageFont.truetype(FONT, size); bb = dd.textbbox((0, 0), s, font=f)
    x = CX - (bb[2] - bb[0]) / 2 - bb[0]
    mk = Image.new('L', (BW, BH), 0); ImageDraw.Draw(mk).text((x, y), s, font=f, fill=255)
    L = Image.new('RGBA', (BW, BH), (0, 0, 0, 0)); L.paste((190, 70, 255, 255), (0, 0), mk.filter(ImageFilter.MaxFilter(61)).filter(ImageFilter.GaussianBlur(25)))
    o = mk.filter(ImageFilter.MaxFilter(37))
    for k in range(28, 0, -2):
        L.paste((45, 10, 70, 255), (0, 0), ImageChops.offset(o, 0, k))
    L.paste((110, 30, 170, 255), (0, 0), o); L.paste((30, 8, 45, 255), (0, 0), mk.filter(ImageFilter.MaxFilter(17)))
    for k in range(12, 0, -1):
        L.paste((180, 80, 10, 255), (0, 0), ImageChops.offset(mk, 0, k))
    g = Image.new('RGBA', (BW, BH)); gd = ImageDraw.Draw(g)
    for yy in range(BH):
        t = min(max((yy - y - bb[1]) / (bb[3] - bb[1]), 0), 1); gd.line((0, yy, BW, yy), fill=(255, int(245 - 110 * t), int(140 - 130 * t), 255))
    L.paste(g, (0, 0), mk)
    hi = Image.new('L', (BW, BH), 0); ImageDraw.Draw(hi).rectangle((0, 0, BW, int(y + bb[1] + (bb[3] - bb[1]) * 0.4)), fill=95)
    L.paste((255, 255, 240, 255), (0, 0), ImageChops.multiply(hi, mk)); bg.alpha_composite(L)
    band = Image.new('RGBA', (1300, 120), (0, 0, 0, 0)); bd = ImageDraw.Draw(band)
    bd.polygon([(30, 0), (1300, 0), (1270, 120), (0, 120)], fill=(30, 8, 45, 255)); bd.polygon([(40, 8), (1288, 8), (1260, 112), (12, 112)], fill=(150, 45, 210, 255))
    f3 = ImageFont.truetype(FONT, 58); s3 = 'ASTUCES • ACTUS • 1 VIDÉO PAR JOUR'
    bd.text(((1300 - bd.textlength(s3, font=f3)) / 2, 30), s3, font=f3, fill=(255, 255, 255), stroke_width=5, stroke_fill=(30, 8, 45))
    band = band.rotate(2, resample=Image.BICUBIC, expand=True); bg.alpha_composite(band, (CX - band.width // 2, CY + 95))
    f4 = ImageFont.truetype(FONT, 48); dd = ImageDraw.Draw(bg); s4 = '@CLASHCENTERFR'
    dd.text((CX - dd.textlength(s4, font=f4) / 2, CY + 240), s4, font=f4, fill=(255, 230, 120), stroke_width=7, stroke_fill=(30, 8, 45))
    p = WD + '/banniere.jpg'; bg.convert('RGB').save(p, quality=90)
    return p
