# Crée le salon privé 🎞️┃sneak-peek (staff) : le propriétaire y dépose les vidéos/photos sneak peek, le bot les lit.
import os, sys, requests
sys.path.insert(0, os.path.dirname(__file__))
from discord_commun import API, HDR, GUILD

VOIR, ECRIRE, LIENS, FICHIERS, HISTO, SLASH = 1024, 2048, 16384, 32768, 65536, 1 << 31
NOM = '🎞️┃sneak-peek'
me = requests.get(f'{API}/users/@me', headers=HDR, timeout=30).json()['id']
g = requests.get(f'{API}/guilds/{GUILD}', headers=HDR, timeout=30).json()
chans = requests.get(f'{API}/guilds/{GUILD}/channels', headers=HDR, timeout=30).json()
staff = next((c['id'] for c in chans if c['type'] == 4 and 'staff' in c['name'].lower()), None)
for c in chans:
    if 'sneak-peek' in c['name']:
        print('Déjà là :', c['name'], c['id'], 'catégorie', c.get('parent_id'))
        if staff and c.get('parent_id') != staff:
            r = requests.patch(f"{API}/channels/{c['id']}", headers=HDR, timeout=30, json={'parent_id': staff})
            print('Déplacé dans staff', r.status_code)
        sys.exit(0)

def ow(i, t, allow, deny=0):
    return {'id': i, 'type': t, 'allow': str(allow), 'deny': str(deny)}

ows = [ow(GUILD, 0, 0, VOIR),
       ow(me, 1, VOIR | ECRIRE | LIENS | FICHIERS | HISTO),
       ow(g['owner_id'], 1, VOIR | ECRIRE | LIENS | FICHIERS | HISTO | SLASH)]
r = requests.post(f'{API}/guilds/{GUILD}/channels', headers=HDR, timeout=30,
                  json={'name': NOM, 'type': 0, 'parent_id': staff, 'permission_overwrites': ows,
                        'topic': 'Privé : vidéos et photos sneak peek pour les prochaines vidéos Clash Center.'})
print(r.status_code, r.text[:200])
r.raise_for_status()
