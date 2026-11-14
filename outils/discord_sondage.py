# Poste un sondage Discord (un tous les 2 jours) dans 💬┃général.
import os, sys, datetime
sys.path.insert(0, os.path.dirname(__file__))
from discord_commun import GENERAL, poster

SONDAGES = [
    ("Tu es HDV combien en ce moment ? 🏰", ["HDV 13 ou moins", "HDV 14 - 15", "HDV 16 - 17", "HDV 18 - 19"]),
    ("Quelle vidéo tu veux demain ? 🎬", ["Astuce d'attaque", "Nouveautés du jeu", "Ordre d'amélioration", "Défense / base"]),
    ("Ton sort préféré ? ✨", ["Rage", "Gel", "Foudre", "Invisibilité"]),
    ("Le héros que tu montes en premier ? 👑", ["Roi des barbares", "Reine des archers", "Grand gardien", "Championne royale"]),
    ("Tu attaques comment en guerre ? ⚔️", ["Dès le début", "Au milieu", "À la dernière minute", "Je participe pas 😅"]),
    ("Tu joues combien de temps par jour ? ⏱️", ["Moins de 30 min", "30 min - 1 h", "1 - 2 h", "Plus de 2 h"]),
    ("L'armée qui te fait gagner le plus ? 🐉", ["Électro-dragons", "Cochons", "Ballons", "Sorcières / autre"]),
]
jour = datetime.date.today().toordinal() // 2
q, reps = SONDAGES[jour % len(SONDAGES)]
poster(os.environ.get('DISCORD_CHANNEL_ID') or GENERAL, {
    'content': '📊 **Sondage du jour** — réponds et dis-nous pourquoi en dessous 👇',
    'poll': {'question': {'text': q}, 'answers': [{'poll_media': {'text': r}} for r in reps],
             'duration': 48, 'allow_multiselect': False},
    'allowed_mentions': {'parse': []},
})
