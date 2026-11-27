# FitBeat

PWA de sport : programme hebdomadaire, chrono de séance avec calories brûlées, musique intégrée, repas et calories estimés par IA, coach IA.

## Lancer

```bash
cd app-sport
ANTHROPIC_API_KEY=sk-ant-... node server.js   # MODEL=claude-sonnet-5-5 pour changer de modèle
```

Ouvrir http://localhost:3000. Sans clé, tout fonctionne sauf l'analyse de repas et le coach.

## Calculs

- Calories brûlées = MET × poids (kg) × durée (h). Les MET du programme sont des valeurs approchées du Compendium of Physical Activities.
- Cible quotidienne = métabolisme de base (Mifflin-St Jeor) × facteur d'activité ± ajustement d'objectif.
- Calories des repas : estimation IA à partir du texte, erreur typique de 20 % ou plus.

## Musique

Le beat WebAudio fonctionne sans fichier. Pour de vrais morceaux, ajouter des mp3 libres de droits dans `public/music/` et les déclarer dans `public/music/playlist.json`.
