# Outils communs pour le bot Discord Clash Center (token dans le secret DISCORD_BOT_TOKEN).
import os, requests

TOKEN = os.environ['DISCORD_BOT_TOKEN']
GUILD = '1515604769933099069'          # serveur Clash Center
GENERAL = '1515692264603779155'        # 💬┃général
API = 'https://discord.com/api/v10'
HDR = {'Authorization': f'Bot {TOKEN}', 'User-Agent': 'ClashCenterBot (github, 1.0)'}


def salon(*mots, defaut=GENERAL):
    """Trouve un salon texte dont le nom contient un des mots (ex. 'nouvelles-vid')."""
    try:
        r = requests.get(f'{API}/guilds/{GUILD}/channels', headers=HDR, timeout=30); r.raise_for_status()
        for c in r.json():
            if c.get('type') in (0, 5) and any(m in c['name'].lower() for m in mots):
                return c['id']
    except Exception as e:
        print('Liste des salons impossible :', e)
    return defaut


def poster(canal, payload, fichier=None):
    if fichier:
        with open(fichier, 'rb') as f:
            import json
            r = requests.post(f'{API}/channels/{canal}/messages', headers=HDR, data={'payload_json': json.dumps(payload)},
                              files={'files[0]': ('miniature.jpg', f, 'image/jpeg')}, timeout=60)
    else:
        r = requests.post(f'{API}/channels/{canal}/messages', headers=HDR, json=payload, timeout=60)
    print(r.status_code, r.text[:200])
    r.raise_for_status()
    return r.json()
