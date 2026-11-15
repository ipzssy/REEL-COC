# Liste le contenu du salon privé sneak-peek (messages, pièces jointes) pour vérifier que le bot y a accès.
import os, sys, requests
sys.path.insert(0, os.path.dirname(__file__))
from discord_commun import API, HDR, GUILD

chans = requests.get(f'{API}/guilds/{GUILD}/channels', headers=HDR, timeout=30).json()
c = next((c for c in chans if 'sneak-peek' in c['name']), None)
if not c:
    sys.exit('Salon introuvable')
r = requests.get(f"{API}/channels/{c['id']}/messages?limit=20", headers=HDR, timeout=30)
print('Lecture', r.status_code)
r.raise_for_status()
for m in r.json():
    pj = [f"{a['filename']} ({a.get('content_type')}, {a['size']//1024} Ko)" for a in m.get('attachments', [])]
    print('MSG', m['id'], m['timestamp'][:19], 'texte=', repr(m['content'][:80]), 'fichiers=', pj)
print('FIN')
