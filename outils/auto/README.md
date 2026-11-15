# Short automatique (veille → vidéo → validation de Mikael)

Moteur : `python3 -I outils/auto/short_auto.py <dossier_projet>` (1080x1920, 60 fps, environ 1 min de rendu par minute de vidéo).

Le dossier projet contient :
- `spec.json`
- `img/` : images nettes du jeu (jpg ou png)
- `v0.wav`, `v1.wav`, ... : une voix par scène (voix clonée de Mikael, mono 44100 Hz, silences rognés)

## spec.json
```json
{"out": "short.mp4", "accent": [165, 90, 255], "header": "CLASH OF CLANS",
 "scenes": [
  {"text": "phrase lue par la voix (sert aussi aux sous-titres)",
   "label": "ÉTIQUETTE", "big": [["MOT", "white"], ["MOT2", "accent"]],
   "stamp": "À CONFIRMER", "images": ["a.jpg", "b.png"]},
  {"text": "Rejoins le Discord, lien en bio.", "gauge": true}
 ]}
```
- 7 à 10 scènes, 30 à 60 s au total. Première scène = accroche. Dernière scène = `gauge: true` (jauges + « TON AVIS ? »).
- `big` : 1 à 3 gros mots (2 maximum conseillé), `white` ou `accent`.
- `stamp` : `À CONFIRMER`, `PROBABLE`, `FUITE`, `OFFICIEL`... pour tout ce qui n'est pas confirmé.

## Voix
Speko `audio_synthesize` : clone « Mikael FR » (voice id `bf98b054-1a25-4d96-8c5c-ff4920ebf14b`), contrainte `allowedProviders` tts `["cartesia"]`, `sampleRate` 24000. Un appel par scène, puis :
`ffmpeg -i brut.wav -af "silenceremove=start_periods=1:start_threshold=-45dB,areverse,silenceremove=start_periods=1:start_threshold=-45dB,areverse" -ar 44100 -ac 1 -sample_fmt s16 vN.wav`

## Miniature
Uniquement via `outils/miniatures.py` (`build_thumb`). Jamais d'images du dossier `thumbs/` ou `miniatures/`.

## Règles
Ne jamais parler du bot, de farm, de boost d'XP, d'« auto » ni d'Upgrade+. CTA autorisé : « rejoindre le Discord, lien en bio ». Les fuites ne sont jamais présentées comme officielles.
