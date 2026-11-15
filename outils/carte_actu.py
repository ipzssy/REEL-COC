# Cartes illustrées 1280x720 pour les annonces du salon actu (fond violet/orange, titre doré, image du wiki Clash of Clans).
import os, re, math, requests
from PIL import Image, ImageDraw, ImageFont, ImageFilter

UA = {'User-Agent': 'Mozilla/5.0'}
WD = os.environ.get('CC_WD', '/tmp/cc_cartes'); os.makedirs(WD, exist_ok=True)
FONT = WD + '/lg.ttf'
W, H = 1280, 720

def _police():
    if not os.path.exists(FONT):
        try:
            open(FONT, 'wb').write(requests.get('https://github.com/google/fonts/raw/main/apache/luckiestguy/LuckiestGuy-Regular.ttf', headers=UA, timeout=60).content)
        except Exception:
            return None
    return FONT

def _f(taille):
    p = _police()
    try:
        return ImageFont.truetype(p, taille) if p else ImageFont.truetype('DejaVuSans-Bold.ttf', taille)
    except Exception:
        return ImageFont.load_default()

def wiki(nom):
    """Image du wiki Clash of Clans, rognée sur la partie visible. None si introuvable."""
    try:
        p = WD + '/' + re.sub(r'[^A-Za-z0-9._-]', '_', nom)
        if not os.path.exists(p):
            r = requests.get('https://clashofclans.fandom.com/api.php', params={'action': 'query', 'titles': 'File:' + nom, 'prop': 'imageinfo', 'iiprop': 'url', 'format': 'json'}, headers=UA, timeout=30)
            u = list(r.json()['query']['pages'].values())[0]['imageinfo'][0]['url']
            open(p, 'wb').write(requests.get(u, headers=UA, timeout=90).content)
        im = Image.open(p).convert('RGBA')
        bb = im.split()[3].point(lambda v: 255 if v > 20 else 0).getbbox()
        return im.crop(bb) if bb else im
    except Exception as e:
        print('Image wiki indisponible :', nom, e)
        return None

def _fond():
    bg = Image.new('RGB', (W, H)); px = bg.load()
    for y in range(H):
        for x in range(W):
            t = min(max((x / W) * 0.55 + (y / H) * 0.45, 0), 1)
            px[x, y] = (int(55 + 200 * t), int(15 + 115 * t), int(105 - 80 * t))
    bg = bg.convert('RGBA'); cx, cy = W * 0.74, H * 0.5
    rayons = Image.new('L', (W, H), 0); d = ImageDraw.Draw(rayons)
    for i in range(18):
        a = i * math.pi * 2 / 18
        d.polygon([(cx, cy), (cx + 2500 * math.cos(a), cy + 2500 * math.sin(a)), (cx + 2500 * math.cos(a + 0.07), cy + 2500 * math.sin(a + 0.07))], fill=45)
    bg.paste((255, 235, 170, 255), (0, 0), rayons.filter(ImageFilter.GaussianBlur(4)))
    return bg

def _texte(bg, s, taille, x, y, couleur, trait=9):
    d = ImageDraw.Draw(bg); d.text((x, y), s, font=_f(taille), fill=couleur, stroke_width=trait, stroke_fill=(15, 8, 25))

def _lignes(s, taille, largeur):
    d = ImageDraw.Draw(Image.new('RGB', (10, 10))); f = _f(taille); res, cur = [], ''
    for mot in s.split():
        t = (cur + ' ' + mot).strip()
        if d.textlength(t, font=f) <= largeur or not cur:
            cur = t
        else:
            res.append(cur); cur = mot
    return res + [cur]

def carte(chemin, etiquette, titre, sous_titre='', images=()):
    bg = _fond()
    # images à droite, jamais agrandies de plus de 1.1x (pas de flou)
    zone_x, zone_w = 730, 500
    imgs = [i for i in (wiki(n) for n in images) if i is not None]
    if imgs:
        h_case = 560 // len(imgs)
        for k, im in enumerate(imgs):
            s = min(zone_w / im.width, (h_case - 10) / im.height, 1.1)
            im = im.resize((max(int(im.width * s), 1), max(int(im.height * s), 1)), Image.LANCZOS)
            a = im.split()[3]
            glow = Image.new('RGBA', im.size, (255, 240, 180, 0)); glow.putalpha(a.filter(ImageFilter.MaxFilter(11)).filter(ImageFilter.GaussianBlur(20)).point(lambda v: int(v * .8)))
            ombre = Image.new('RGBA', im.size, (0, 0, 0, 0)); ombre.putalpha(a.filter(ImageFilter.GaussianBlur(12)).point(lambda v: int(v * .5)))
            x = zone_x + (zone_w - im.width) // 2; y = 80 + k * h_case + (h_case - im.height) // 2
            bg.alpha_composite(glow, (x, y)); bg.alpha_composite(ombre, (x + 8, y + 14)); bg.alpha_composite(im, (x, y))
    # texte à gauche
    _texte(bg, etiquette.upper(), 34, 60, 54, (255, 255, 255), 6)
    largeur = 610 if imgs else 1100
    taille = 96
    while True:
        L = _lignes(titre.upper(), taille, largeur)
        if (len(L) <= 3 and taille * 1.1 * len(L) <= 380) or taille <= 50:
            break
        taille -= 6
    y = 130
    for l in L:
        _texte(bg, l, taille, 60, y, (255, 205, 45), 12); y += int(taille * 1.12)
    if sous_titre:
        _texte(bg, sous_titre, 44, 60, min(y + 24, H - 110), (255, 255, 255), 8)
    bg.convert('RGB').save(chemin, 'JPEG', quality=92)
    return chemin
