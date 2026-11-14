# Paramètres pro du serveur Clash Center + bannière originale (sans personnages du jeu).
import os, sys, io, base64, requests
sys.path.insert(0, os.path.dirname(__file__))
from discord_commun import API, HDR, GUILD, salon
exec(open(os.path.join(os.path.dirname(__file__), 'miniatures.py'), encoding='utf-8').read())
from PIL import Image

reglement = salon('reglement', 'règlement', defaut=None)
staff = salon('staff-discussion', defaut=None)
params = {
    'description': "🏆 La communauté Clash of Clans 100 % française : astuces, actus HDV 19, sondages, recherche de clan et une vidéo chaque jour à 19h !",
    'preferred_locale': 'fr',
    'default_message_notifications': 1,   # mentions seulement : pas de spam de notifications
    'explicit_content_filter': 2,         # filtre les images choquantes pour tous
    'verification_level': 1,              # e-mail vérifié : bloque les comptes jetables sans gêner les vrais
    'system_channel_flags': 1 | 4 | 8,    # pas de messages d'arrivée Discord en double (ProBot s'en charge), pas d'astuces, pas de stickers
}
if reglement: params['rules_channel_id'] = reglement
if staff: params['public_updates_channel_id'] = staff
r = requests.patch(f'{API}/guilds/{GUILD}', headers=HDR, timeout=30, json=params)
print('paramètres', r.status_code, r.text[:300])

b = Image.open(build_banner(True, personnages=False)).convert('RGB').resize((960, 540), Image.LANCZOS)
buf = io.BytesIO(); b.save(buf, 'JPEG', quality=90)
uri = 'data:image/jpeg;base64,' + base64.b64encode(buf.getvalue()).decode()
for champ in ('banner', 'splash'):
    r = requests.patch(f'{API}/guilds/{GUILD}', headers=HDR, timeout=60, json={champ: uri})
    print(champ, r.status_code, r.text[:200])
g = requests.get(f'{API}/guilds/{GUILD}', headers=HDR, timeout=30).json()
print('niveau boost', g.get('premium_tier'), 'boosts', g.get('premium_subscription_count'), 'features', g.get('features'))
