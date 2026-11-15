# Affiche le lien d'invitation permanent du serveur (crée un lien sans expiration sur le salon de bienvenue si aucun n'existe).
import os, sys, requests
sys.path.insert(0, os.path.dirname(__file__))
from discord_commun import API, HDR, GUILD, salon

r = requests.get(f'{API}/guilds/{GUILD}/invites', headers=HDR, timeout=30)
print('INVITES', r.status_code)
if r.ok:
    for i in r.json():
        print('LIEN', f"https://discord.gg/{i['code']}", 'expire' if i.get('max_age') else 'permanent', 'max_uses', i.get('max_uses'), 'utilisations', i.get('uses'), 'salon', (i.get('channel') or {}).get('name'))
    if not any(not i.get('max_age') and not i.get('max_uses') for i in r.json()):
        c = salon('bienvenue', 'invitation', 'reglement')
        r2 = requests.post(f'{API}/channels/{c}/invites', headers=HDR, json={'max_age': 0, 'max_uses': 0, 'unique': False}, timeout=30)
        print('CREE', r2.status_code, 'LIEN', f"https://discord.gg/{r2.json().get('code')}" if r2.ok else r2.text[:200])
