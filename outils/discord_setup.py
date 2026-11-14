# Crée (si absents) les salons 📢┃nouvelles-vidéos et 📰┃actu-clash avec le bot Clash Center.
import os, sys, requests
sys.path.insert(0, os.path.dirname(__file__))
from discord_commun import API, HDR, GUILD

perms = requests.get(f'{API}/guilds/{GUILD}/members/' + requests.get(f'{API}/users/@me', headers=HDR, timeout=30).json()['id'], headers=HDR, timeout=30).json()
print('roles du bot :', perms.get('roles'))
me = requests.get(f'{API}/users/@me', headers=HDR, timeout=30).json()['id']
chans = requests.get(f'{API}/guilds/{GUILD}/channels', headers=HDR, timeout=30).json()
cat = next((c['id'] for c in chans if c['type'] == 4 and 'INFORMATIONS' in c['name']), None)
noms = {c['name'] for c in chans}
lecture_seule = [{'id': GUILD, 'type': 0, 'allow': '1024', 'deny': '2048'},
                 {'id': me, 'type': 1, 'allow': '562949953539072', 'deny': '0'}]
for nom, sujet in [('📢┃nouvelles-vidéos', 'Chaque jour à 19h : la nouvelle vidéo Clash Center (YouTube, TikTok, Instagram).'),
                   ('📰┃actu-clash', 'Les dernières nouveautés officielles de Clash of Clans, postées automatiquement.')]:
    if nom in noms:
        print('Déjà là :', nom); continue
    r = requests.post(f'{API}/guilds/{GUILD}/channels', headers=HDR, timeout=30,
                      json={'name': nom, 'type': 0, 'topic': sujet, 'parent_id': cat, 'permission_overwrites': lecture_seule})
    print(nom, r.status_code, r.text[:200])
    if r.status_code == 403:  # pas le droit de gérer les permissions : on crée le salon simple
        r = requests.post(f'{API}/guilds/{GUILD}/channels', headers=HDR, timeout=30,
                          json={'name': nom, 'type': 0, 'topic': sujet, 'parent_id': cat})
        print(nom, '(sans permissions)', r.status_code, r.text[:200])
    if r.status_code == 403:
        r = requests.post(f'{API}/guilds/{GUILD}/channels', headers=HDR, timeout=30, json={'name': nom, 'type': 0, 'topic': sujet})
        print(nom, '(hors catégorie)', r.status_code, r.text[:200])
    r.raise_for_status()
