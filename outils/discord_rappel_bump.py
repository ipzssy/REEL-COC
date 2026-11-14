# Rappel toutes les 2 h dans 🔼┃bump pour que le propriétaire tape /bump (DISBOARD).
import os, sys, requests
sys.path.insert(0, os.path.dirname(__file__))
from discord_commun import API, HDR, GUILD, salon, poster
owner = requests.get(f'{API}/guilds/{GUILD}', headers=HDR, timeout=30).json()['owner_id']
canal = salon('bump', defaut=None)
if not canal:
    print('Salon bump introuvable'); raise SystemExit(0)
poster(canal, {'content': f"⏰ <@{owner}> c'est l'heure du **/bump** ! Tape `/bump` ici pour remonter Clash Center sur DISBOARD 🚀",
               'allowed_mentions': {'users': [owner]}})
