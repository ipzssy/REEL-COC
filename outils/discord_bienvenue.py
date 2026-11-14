# Message de bienvenue avec bannière pour chaque nouveau membre de Clash Center.
# Tourne toutes les ~10 min via GitHub Actions. Nécessite « Server Members Intent » activé sur le bot.
import os, sys, io, json, requests
sys.path.insert(0, os.path.dirname(__file__))
from discord_commun import API, HDR, GUILD, salon
exec(open(os.path.join(os.path.dirname(__file__), 'miniatures.py'), encoding='utf-8').read())
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps

ETAT = os.environ.get('ETAT_FILE') or os.path.join(os.path.dirname(__file__), '..', 'etat', 'bienvenue.json')
DRY = os.environ.get('DRY_RUN') == '1'
etat = json.load(open(ETAT))

def fond():
    p = os.path.join(WD, 'fond_bienvenue2.jpg')
    if not os.path.exists(p):
        b = Image.open(build_banner(False)).convert('RGB').resize((1100, 619), Image.LANCZOS)
        b.crop((0, 60, 1100, 560)).save(p, quality=92)
    return Image.open(p).convert('RGBA')

def texte(img, s, size, y, fill, stroke=8):
    d = ImageDraw.Draw(img); f = ImageFont.truetype(FONT, size)
    while d.textlength(s, font=f) > 1000 and size > 24:
        size -= 4; f = ImageFont.truetype(FONT, size)
    d.text(((1100 - d.textlength(s, font=f)) / 2, y), s, font=f, fill=fill, stroke_width=stroke, stroke_fill=(30, 8, 45))

def carte(membre, rang):
    u = membre['user']; nom = membre.get('nick') or u.get('global_name') or u['username']
    img = fond(); ov = Image.new('L', img.size, 0); ImageDraw.Draw(ov).ellipse((150, -40, 950, 540), fill=150)
    sh = Image.new('RGBA', img.size, (20, 6, 40, 255)); sh.putalpha(ov.filter(ImageFilter.GaussianBlur(70))); img.alpha_composite(sh)
    if u.get('avatar'):
        url = f"https://cdn.discordapp.com/avatars/{u['id']}/{u['avatar']}.png?size=256"
    else:
        url = f"https://cdn.discordapp.com/embed/avatars/{(int(u['id']) >> 22) % 6}.png"
    av = Image.open(io.BytesIO(requests.get(url, timeout=30).content)).convert('RGBA').resize((190, 190), Image.LANCZOS)
    m = Image.new('L', (190, 190), 0); ImageDraw.Draw(m).ellipse((0, 0, 189, 189), fill=255); av.putalpha(m)
    ring = Image.new('RGBA', (214, 214), (0, 0, 0, 0)); rd = ImageDraw.Draw(ring)
    rd.ellipse((0, 0, 213, 213), fill=(255, 196, 40, 255)); rd.ellipse((6, 6, 207, 207), fill=(150, 45, 210, 255))
    glow = ring.copy().filter(ImageFilter.GaussianBlur(14))
    img.alpha_composite(glow, (443, 18)); img.alpha_composite(ring, (443, 18)); img.alpha_composite(av, (455, 30))
    texte(img, 'BIENVENUE', 92, 238, (255, 205, 60))
    texte(img, nom.upper(), 56, 340, (255, 255, 255))
    texte(img, f'Tu es le {rang}e membre de Clash Center !', 34, 425, (230, 200, 255), 6)
    p = os.path.join(WD, f"bienvenue_{u['id']}.png"); img.convert('RGB').save(p, quality=92)
    return p, nom

if DRY:
    g = requests.get(f'{API}/guilds/{GUILD}', headers=HDR, timeout=30).json()
    owner = requests.get(f"{API}/guilds/{GUILD}/members/{g['owner_id']}", headers=HDR, timeout=30).json()
    p, _ = carte(owner, 221); print('test :', p)
    d = os.path.dirname(ETAT); Image.open(p).convert('RGB').save(os.path.join(d, 'test_bienvenue.jpg'), quality=90)
    raise SystemExit(0)

r = requests.get(f'{API}/guilds/{GUILD}/members?limit=1000', headers=HDR, timeout=30)
if r.status_code == 403:
    print("Active « Server Members Intent » dans le Developer Portal (onglet Bot)."); raise SystemExit(0)
r.raise_for_status()
membres = sorted([m for m in r.json() if not m['user'].get('bot')], key=lambda m: m['joined_at'])
if etat['dernier'] is None:  # premier lancement : on ne souhaite pas la bienvenue à tout le monde
    etat['dernier'] = membres[-1]['joined_at'] if membres else ''
    json.dump(etat, open(ETAT, 'w')); print('Initialisé'); raise SystemExit(0)
nouveaux = [m for m in membres if m['joined_at'] > etat['dernier']]
total = requests.get(f'{API}/guilds/{GUILD}?with_counts=true', headers=HDR, timeout=30).json().get('approximate_member_count', len(membres))
canal = os.environ.get('DISCORD_CHANNEL_ID') or salon('bienvenue')
me = requests.get(f'{API}/users/@me', headers=HDR, timeout=30).json()['id']
for i, m in enumerate(nouveaux):
    p, nom = carte(m, total - len(nouveaux) + 1 + i)
    payload = {'content': f"👋 Bienvenue <@{m['user']['id']}> sur **Clash Center** ! Lis le 📜┃règlement, présente-toi dans 💬┃général et file voir nos vidéos dans 📢┃nouvelles-vidéos 🔥",
               'allowed_mentions': {'users': [m['user']['id']]}}
    for essai in range(2):
        with open(p, 'rb') as f:
            rr = requests.post(f'{API}/channels/{canal}/messages', headers=HDR, data={'payload_json': json.dumps(payload)},
                               files={'files[0]': ('bienvenue.png', f, 'image/png')}, timeout=60)
        print(nom, rr.status_code, rr.text[:150])
        if rr.status_code == 403 and essai == 0:  # se donne le droit d'écrire dans le salon
            requests.put(f'{API}/channels/{canal}/permissions/{me}', headers=HDR, timeout=30,
                         json={'type': 1, 'allow': str(1024 | 2048 | 16384 | 32768 | 65536), 'deny': '0'})
            continue
        break
    etat['dernier'] = m['joined_at']
json.dump(etat, open(ETAT, 'w'))
