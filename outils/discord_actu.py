# Poste les nouvelles vidéos officielles Clash of Clans (YouTube) dans le salon actu.
import os, sys, datetime, requests, xml.etree.ElementTree as ET
sys.path.insert(0, os.path.dirname(__file__))
from discord_commun import salon, poster

FEED = 'https://www.youtube.com/feeds/videos.xml?channel_id=UCD1Em4q90ZUK2R5HKesszJg'  # chaîne officielle Clash of Clans
FENETRE = datetime.timedelta(hours=int(os.environ.get('FENETRE_H', '3')))
ns = {'a': 'http://www.w3.org/2005/Atom', 'm': 'http://search.yahoo.com/mrss/', 'yt': 'http://www.youtube.com/xml/schemas/2015'}
try:
    root = ET.fromstring(requests.get(FEED, timeout=30).content)
except Exception as e:
    print('Flux indisponible :', e); raise SystemExit(0)
now = datetime.datetime.now(datetime.timezone.utc)
nouveaux = []
for e in root.findall('a:entry', ns):
    pub = datetime.datetime.fromisoformat(e.find('a:published', ns).text.replace('Z', '+00:00'))
    if now - pub <= FENETRE:
        nouveaux.append((pub, e.find('a:title', ns).text, e.find('a:link', ns).get('href'),
                         e.find('m:group/m:thumbnail', ns).get('url')))
if not nouveaux:
    print('Pas de nouveauté'); raise SystemExit(0)
canal = os.environ.get('DISCORD_CHANNEL_ID') or salon('actu')
for pub, titre, lien, img in sorted(nouveaux)[-int(os.environ.get('MAX_POSTS', '3')):]:
    poster(canal, {'embeds': [{'title': '📰 ' + titre, 'url': lien, 'color': 0xF5B000,
                               'description': "Nouvelle vidéo officielle de **Clash of Clans** ! Ton avis en dessous 👇",
                               'image': {'url': img}, 'footer': {'text': 'Actu Clash • source : chaîne officielle Clash of Clans'}}],
                   'allowed_mentions': {'parse': []}})
