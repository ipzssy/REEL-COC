# Salon 📰┃actu-clash : événements du jeu, annonces officielles Supercell, fuites (étiquetées non officielles).
# Tout est posté par le bot Clash Center. Anti-doublon : on relit les derniers messages du salon (tags dans les footers).
import os, re, sys, json, datetime, html, requests
from zoneinfo import ZoneInfo
sys.path.insert(0, os.path.dirname(__file__))
from discord_commun import API, HDR, GUILD, salon, poster

SNEAK_ID_DEPART = 1571397676342313041     # les fuites déposées avant ce message ne sont jamais republiées
PROPRIO = '649405632532971524'
BLOG = 'https://supercell.com/en/games/clashofclans/blog/'
BLOG_DEPUIS = datetime.date(2026, 11, 15)  # pas de rattrapage des anciens articles
OR, VIOLET = 0xF5B000, 0x9B59B6
MAX = {'evt': 3, 'blog': 3, 'leak': 4}

D = datetime.date
EVENEMENTS = [  # slug, nom, début, fin, texte (source : saison de novembre 2026 « Clash of Titans »)
    ('wastelands', 'Retour des cosmétiques Wastelands', D(2026, 11, 15), D(2026, 11, 30),
     "Les skins de héros et le décor **Wastelands** reviennent dans la boutique ! **5 skins et 1 décor** purement cosmétiques pour changer le look de ton village."),
    ('treasure-hunt', 'Chasse au trésor', D(2026, 11, 16), D(2026, 11, 23),
     "La **Chasse au trésor** démarre aujourd'hui et dure jusqu'au **23 novembre**, pour les Hôtels de ville 3 à 17. Pense à faire tes attaques chaque jour pour ne rien rater !"),
    ('snackable', 'Snackable Troops', D(2026, 11, 20), D(2026, 11, 26),
     "Les **Snackable Troops** arrivent du **20 au 26 novembre** : des troupes de renfort à usage unique pour booster tes attaques. À utiliser au bon moment !"),
    ('clan-games', 'Jeux de clan', D(2026, 11, 22), D(2026, 11, 28),
     "Les **Jeux de clan** commencent aujourd'hui et durent jusqu'au **28 novembre**. Pendant les 4 premiers jours, des troupes de renfort sont disponibles. Rassemble ton clan !"),
    ('fully-forged', 'Fully Forged Challenge', D(2026, 11, 24), D(2026, 12, 1),
     "Le **Fully Forged Challenge** débute aujourd'hui, jusqu'au **1er décembre** : attaque avec des héros construits à partir de pièces de machines de siège."),
]

canal = salon('actu')
sneak = salon('sneak-peek', defaut=None)
recent = requests.get(f'{API}/channels/{canal}/messages?limit=100', headers=HDR, timeout=30).json()
vus = set()
for m in recent:
    for e in m.get('embeds', []):
        vus.add((e.get('footer') or {}).get('text', ''))
        if e.get('url'):
            vus.add(e['url'])
def deja(tag):
    return any(tag in v for v in vus if v)

aujourdhui = datetime.datetime.now(ZoneInfo('Europe/Paris')).date()
n = 0
# A) événements du jeu : le jour du début (ou le lendemain si manqué), jamais s'ils sont finis
for slug, nom, debut, fin, texte in EVENEMENTS:
    if n >= MAX['evt']:
        break
    if debut <= aujourdhui <= min(fin, debut + datetime.timedelta(days=1)) and not deja('evt:' + slug):
        poster(canal, {'embeds': [{'title': '🗓️ Nouvel événement : ' + nom, 'description': texte, 'color': OR,
                                   'footer': {'text': 'Actu Clash • evt:' + slug}}], 'allowed_mentions': {'parse': []}})
        n += 1

# B) annonces officielles du blog Supercell (titre et résumé d'origine, en anglais)
UA = {'User-Agent': 'Mozilla/5.0 (compatible; ClashCenterBot)'}
def meta(page, nom):
    m = re.search(r'<meta[^>]+(?:property|name)=["\']%s["\'][^>]+content=["\']([^"\']*)' % re.escape(nom), page, re.I) or \
        re.search(r'<meta[^>]+content=["\']([^"\']*)["\'][^>]+(?:property|name)=["\']%s["\']' % re.escape(nom), page, re.I)
    return html.unescape(m.group(1)).strip() if m else ''
n = 0
try:
    liste = requests.get(BLOG, headers=UA, timeout=30).text
    liens = list(dict.fromkeys(re.findall(r'/en/games/clashofclans/blog/news/[a-z0-9\-]+/?', liste)))[:8]
    for lien in liens:
        url = 'https://supercell.com' + lien.rstrip('/') + '/'
        if n >= MAX['blog'] or deja(url) or deja(url.rstrip('/')):
            continue
        page = requests.get(url, headers=UA, timeout=30).text
        d = (meta(page, 'article:published_time') or (re.search(r'"datePublished"\s*:\s*"([^"]+)', page) or [None, ''])[1])[:10]
        if not d or datetime.date.fromisoformat(d) < BLOG_DEPUIS:
            continue
        titre, desc, img = meta(page, 'og:title'), meta(page, 'og:description'), meta(page, 'og:image')
        if not titre:
            continue
        emb = {'title': '📰 ' + titre[:240], 'url': url, 'color': OR,
               'description': (desc[:600] + '\n\n' if desc else '') + '🔗 Article officiel de Supercell (en anglais)',
               'footer': {'text': 'Actu Clash • source : blog officiel Supercell'}}
        if img:
            emb['image'] = {'url': img}
        poster(canal, {'embeds': [emb], 'allowed_mentions': {'parse': []}})
        n += 1
except Exception as e:
    print('Blog indisponible :', e)

# C) fuites déposées par Mikael dans le salon privé sneak-peek : étiquette « non officiel » puis transfert natif
n = 0
if sneak:
    msgs = requests.get(f'{API}/channels/{sneak}/messages?limit=20', headers=HDR, timeout=30).json()
    for m in sorted(msgs, key=lambda x: int(x['id'])):
        if n >= MAX['leak']:
            break
        if int(m['id']) <= SNEAK_ID_DEPART or m['author']['id'] != PROPRIO or deja('ref:' + m['id']):
            continue
        poster(canal, {'embeds': [{'title': '👻 Fuite / Sneak Peek', 'color': VIOLET,
                                   'description': "Information **non officielle**, venue de fuites de la communauté : à prendre avec précaution tant que Supercell ne l'a pas confirmée.",
                                   'footer': {'text': 'Actu Clash • ref:' + m['id']}}], 'allowed_mentions': {'parse': []}})
        r = requests.post(f'{API}/channels/{canal}/messages', headers=HDR, timeout=60,
                          json={'message_reference': {'type': 1, 'message_id': m['id'], 'channel_id': sneak}})
        print('transfert', m['id'], r.status_code, r.text[:150])
        n += 1
print('Terminé')
