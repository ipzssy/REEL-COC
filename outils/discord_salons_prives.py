# Crée les salons privés 📤┃départs (visible seulement par le propriétaire + ProBot) et 🔼┃bump (propriétaire + DISBOARD).
import os, sys, requests
sys.path.insert(0, os.path.dirname(__file__))
from discord_commun import API, HDR, GUILD

PROBOT, DISBOARD = '282859044593598464', '302050872383242240'
VOIR, ECRIRE, LIENS, FICHIERS, HISTO, SLASH = 1024, 2048, 16384, 32768, 65536, 1 << 31
me = requests.get(f'{API}/users/@me', headers=HDR, timeout=30).json()['id']
g = requests.get(f'{API}/guilds/{GUILD}', headers=HDR, timeout=30).json()
chans = requests.get(f'{API}/guilds/{GUILD}/channels', headers=HDR, timeout=30).json()
noms = {c['name']: c['id'] for c in chans}
staff = next((c['id'] for c in chans if c['type'] == 4 and 'STAFF' in c['name']), None)

def ow(i, t, allow, deny=0):
    return {'id': i, 'type': t, 'allow': str(allow), 'deny': str(deny)}

for nom, sujet, autre in [('📤┃départs', 'Membres qui quittent le serveur (privé).', PROBOT),
                          ('🔼┃bump', 'Faire /bump avec DISBOARD (privé).', DISBOARD)]:
    if nom in noms:
        print('Déjà là :', nom, noms[nom]); continue
    base = [ow(GUILD, 0, 0, VOIR), ow(me, 1, VOIR | ECRIRE | LIENS | HISTO), ow(g['owner_id'], 1, VOIR | ECRIRE | HISTO | SLASH)]
    for ows in (base + [ow(autre, 1, VOIR | ECRIRE | LIENS | FICHIERS | HISTO | SLASH)], base):
        r = requests.post(f'{API}/guilds/{GUILD}/channels', headers=HDR, timeout=30,
                          json={'name': nom, 'type': 0, 'topic': sujet, 'parent_id': staff, 'permission_overwrites': ows})
        print(nom, r.status_code, r.text[:160])
        if r.ok:
            break
