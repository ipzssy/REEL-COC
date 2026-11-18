# Style de montage n°1 (Clash Center) - à utiliser pour TOUTES les vidéos

Validé par Mikael le 18/11/2026. Références : Hache du Blizzard, Héros, Électro-dragons.

- 1080x1920, 30 fps. Mots qui apparaissent un par un, calés sur la voix (transcrire la voix avec faster-whisper pour avoir les timings).
- Police Luckiest Guy (Luckiest.ttf), contour noir épais, blanc + accents jaune / rose / vert / cyan / rouge. Pop avec rebond.
- Fonds : gameplay de Mikael recadré vertical + flou, herbe verte, violet, noir ("PANIQUE"). Flash blanc à chaque scène.
- Éléments : compteurs animés avec icône, cartes à badge, icônes/héros qui flottent, barre de vie, images de la wiki CoC.
- Voix : clone "Mikael FR 2" (Speko, Cartesia 6562fe43-1b9f-45ad-a13d-50ce23df445b), une phrase par appel, silences coupés (~0,12 s entre phrases).
- Pas de blancs ni de temps morts.
- Fin en boucle : dernière phrase inachevée qui se continue dans la première (ex. "Et n'oublie pas, c'est…" -> "Une des armées les plus simples…"), même fond et même image qu'au début.
- CTA : Discord / lien en bio. JAMAIS de farm automatique, boost d'XP ou bot qui joue.

Code : eng.py (moteur : pop, counter, card, rframe, flash, VidBG/ImgBG, warp des pauses), heroes.py / electro.py / axe_v2.py (scénarios exemples : une liste de Scene(t0, t1, fond, éléments)).
Les chemins (assets r/ h/ e/, clips de gameplay) sont ceux de la session de travail ; à adapter.
