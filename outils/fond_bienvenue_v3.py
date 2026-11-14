# Fond de bienvenue v3 : fond original + logo Clash Center + cadre doré (centre laissé libre pour ProBot).
import os, io, requests
os.environ.setdefault('CC_WD', '/tmp/cc')
exec(open(os.path.join(os.path.dirname(__file__), 'miniatures.py'), encoding='utf-8').read())
from PIL import Image, ImageDraw, ImageFont, ImageFilter
LOGO = 'https://yt3.ggpht.com/HfhMapCy3951t2YDGMb8spBCGU6oMEnkd05_nooffoba3cpbTrmk3wW0bskWpS2pIjBsmWHYDnU=s800-c-k-c0x00ffffff-no-rj'
W, H = 1100, 500
bg = Image.open(build_banner(False, personnages=False)).convert('RGB').resize((1100, 619), Image.LANCZOS).crop((0, 60, 1100, 560)).convert('RGBA')
# vignette violette sur les bords
v = Image.new('L', (W, H), 255); ImageDraw.Draw(v).ellipse((-120, -160, W + 120, H + 160), fill=0)
sh = Image.new('RGBA', (W, H), (40, 10, 70, 255)); sh.putalpha(v.filter(ImageFilter.GaussianBlur(60)).point(lambda x: int(x * 0.75))); bg.alpha_composite(sh)
# logo rond avec halo, à gauche et à droite
logo = Image.open(io.BytesIO(requests.get(LOGO, timeout=30).content)).convert('RGBA').resize((150, 150), Image.LANCZOS)
m = Image.new('L', (150, 150), 0); ImageDraw.Draw(m).ellipse((0, 0, 149, 149), fill=255); logo.putalpha(m)
ring = Image.new('RGBA', (170, 170), (0, 0, 0, 0)); rd = ImageDraw.Draw(ring)
rd.ellipse((0, 0, 169, 169), fill=(255, 196, 40, 255)); rd.ellipse((5, 5, 164, 164), fill=(120, 40, 180, 255))
for x in (60, W - 230):
    glow = Image.new('RGBA', (230, 230), (0, 0, 0, 0)); ImageDraw.Draw(glow).ellipse((20, 20, 210, 210), fill=(190, 90, 255, 200))
    bg.alpha_composite(glow.filter(ImageFilter.GaussianBlur(22)), (x - 30, 135))
    bg.alpha_composite(ring, (x, 165)); bg.alpha_composite(logo, (x + 10, 175))
# cadre doré
d = ImageDraw.Draw(bg)
d.rounded_rectangle((8, 8, W - 9, H - 9), radius=28, outline=(255, 196, 40, 255), width=6)
d.rounded_rectangle((18, 18, W - 19, H - 19), radius=22, outline=(170, 70, 230, 255), width=3)
# petit titre en haut
f = ImageFont.truetype(FONT, 34); t = 'CLASH CENTER'
d.text(((W - d.textlength(t, font=f)) / 2, 30), t, font=f, fill=(255, 210, 70), stroke_width=5, stroke_fill=(40, 10, 60))
out = os.environ.get('OUT', 'fond_bienvenue_v3_1100x500.jpg'); bg.convert('RGB').save(out, quality=93); print(out)
