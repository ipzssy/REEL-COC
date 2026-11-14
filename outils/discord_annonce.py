# Annonce la vidéo du jour sur Discord avec le bot de Mikael (token dans le secret DISCORD_BOT_TOKEN).
import os, json, datetime, requests
from zoneinfo import ZoneInfo

TOKEN = os.environ['DISCORD_BOT_TOKEN']
CHANNEL = os.environ.get('DISCORD_CHANNEL_ID') or '1515692264603779155'  # 💬┃général par défaut
SLOT = os.environ.get('SLOT', '19h')
API = 'https://discord.com/api/v10'
H = {'Authorization': f'Bot {TOKEN}', 'User-Agent': 'ClashCenterBot (github, 1.0)'}

today = datetime.datetime.now(ZoneInfo('Europe/Paris')).date().isoformat()
plan = requests.get('https://raw.githubusercontent.com/ipzssy/REEL-COC/main/planning_tiktok.json', timeout=30).json()
entries = [e for e in plan if e['date'] == today and e['slot'] == SLOT]
if not entries:
    print('Rien à annoncer aujourd\'hui'); raise SystemExit(0)
e = entries[0]

exec(open(os.path.join(os.path.dirname(__file__), 'miniatures.py'), encoding='utf-8').read())
thumb = build_thumb(key_for(e))

titre = e['title'].split('#')[0].strip()
embed = {
    'title': '🎬 ' + titre,
    'description': ("Nouvelle vidéo dispo sur toutes nos plateformes ! 🔥\n\n"
                    "📺 **YouTube** : https://youtube.com/@clashcenterfr/shorts\n"
                    "🎵 **TikTok** : https://www.tiktok.com/@clash_center0\n"
                    "📸 **Instagram** : https://www.instagram.com/clashcenter2026\n\n"
                    "Like, commente et dis-nous ce que tu en penses 👇"),
    'color': 0x8E2DE2,
    'image': {'url': 'attachment://miniature.jpg'},
    'footer': {'text': 'Clash Center • 1 vidéo par jour à 19h'},
}
payload = {'embeds': [embed], 'allowed_mentions': {'parse': []}}
with open(thumb, 'rb') as f:
    r = requests.post(f'{API}/channels/{CHANNEL}/messages', headers=H,
                      data={'payload_json': json.dumps(payload)},
                      files={'files[0]': ('miniature.jpg', f, 'image/jpeg')}, timeout=60)
print(r.status_code, r.text[:300])
r.raise_for_status()
