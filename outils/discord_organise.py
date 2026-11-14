# Range le serveur Clash Center : catégories claires, salons privés en bas dans STAFF. Ne touche pas aux tickets.
import os, sys, unicodedata, requests
sys.path.insert(0, os.path.dirname(__file__))
from discord_commun import API, HDR, GUILD

def norm(s):
    s = unicodedata.normalize('NFKD', unicodedata.normalize('NFKC', s))
    return ''.join(c for c in s if not unicodedata.combining(c)).lower()

chans = requests.get(f'{API}/guilds/{GUILD}/channels', headers=HDR, timeout=30).json()
cats = {c['id']: c for c in chans if c['type'] == 4}
def cat(*mots):
    return next((i for i, c in cats.items() if any(m in norm(c['name']) for m in mots)), None)

VOIR, ECRIRE = 1024, 2048
def creer_cat(nom, lecture_seule):
    ows = [{'id': GUILD, 'type': 0, 'allow': str(VOIR), 'deny': str(ECRIRE if lecture_seule else 0)}]
    r = requests.post(f'{API}/guilds/{GUILD}/channels', headers=HDR, timeout=30, json={'name': nom, 'type': 4, 'permission_overwrites': ows})
    print('catégorie créée', nom, r.status_code); r.raise_for_status(); return r.json()['id']

c_info = cat('informations', 'bienvenue')
c_clash = cat('clash center') or creer_cat('━━ 📢 𝗖𝗟𝗔𝗦𝗛 𝗖𝗘𝗡𝗧𝗘𝗥 ━━', True)
c_comm = cat('communaute')
c_shop = cat('boutique') or creer_cat('━━ 🛒 𝗕𝗢𝗨𝗧𝗜𝗤𝗨𝗘 ━━', False)
c_supp = cat('support')
c_staff = cat('staff')

PLAN = [  # (catégorie, [(mot-clé, type ou None)])
    (c_info, [('bienvenue', 0), ('reglement', 0), ('invitation', 0)]),
    (c_clash, [('nouvelles-vid', 0), ('actu-clash', 0), ('presentation-bot', 0)]),
    (c_comm, [('general', 0), ('request-clan', 0), ('communaute-bot', 0), ('salon-general', 2)]),
    (c_shop, [('offres-speciales', 0), ('upgrade-rempart', 0), ('sell-compte', 0), ('avis-clients', 0)]),
    (c_supp, [('contacte-ipzssy', 0)]),
    (c_staff, [('staff-discussion', 0), ('staff-vocal', 2), ('analytics', 0), ('logs-moderation', 0), ('logs-ticket', 0),
               ('logs-join', 0), ('departs', 0), ('bump', 0), ('fichier-bot', 0), ('montage-video', 0)]),
]
maj, vus = [], set()
for pos, (cid, liste) in enumerate(PLAN):
    maj.append({'id': cid, 'position': pos})
    for i, (mot, typ) in enumerate(liste):
        ch = next((c for c in chans if c['type'] in (0, 2, 5) and c['id'] not in vus and mot in norm(c['name'])
                   and (typ is None or c['type'] == typ) and not ('salon-general' in norm(c['name']) and mot == 'general')), None)
        if not ch:
            print('introuvable :', mot); continue
        vus.add(ch['id'])
        if ch.get('parent_id') != cid:  # un déplacement à la fois (permissions du salon conservées)
            rr = requests.patch(f"{API}/channels/{ch['id']}", headers=HDR, timeout=30, json={'parent_id': cid})
            print('déplacé', norm(ch['name']), rr.status_code)
            import time; time.sleep(0.6)
        maj.append({'id': ch['id'], 'position': i})
r = requests.patch(f'{API}/guilds/{GUILD}/channels', headers=HDR, timeout=30, json=maj)
print('rangement', r.status_code, r.text[:200]); r.raise_for_status()
for c in requests.get(f'{API}/guilds/{GUILD}/channels', headers=HDR, timeout=30).json():
    if c['type'] == 4:
        print('==', c['position'], c['name'])
