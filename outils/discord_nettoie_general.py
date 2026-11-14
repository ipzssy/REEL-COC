# Supprime les annonces de vidéo (🎬) que le bot a postées par erreur dans 💬┃général.
import os, sys, requests
sys.path.insert(0, os.path.dirname(__file__))
from discord_commun import API, HDR, GENERAL
me = requests.get(f'{API}/users/@me', headers=HDR, timeout=30).json()['id']
msgs = requests.get(f'{API}/channels/{GENERAL}/messages?limit=100', headers=HDR, timeout=30).json()
for m in msgs:
    if m['author']['id'] == me and any((e.get('title') or '').startswith('🎬') for e in m.get('embeds', [])):
        r = requests.delete(f"{API}/channels/{GENERAL}/messages/{m['id']}", headers=HDR, timeout=30)
        print('supprimé', m['id'], r.status_code)
