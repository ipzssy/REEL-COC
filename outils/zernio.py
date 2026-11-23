"""Client minimal pour l'API Zernio (publication TikTok planifiée).

La clé se lit dans la variable d'environnement ZERNIO_API_KEY, ou dans le
fichier .env du projet (ignoré par Git). Elle n'est jamais écrite dans le code.

Usage en ligne de commande (lecture seule, ne publie rien) :
    python3 outils/zernio.py comptes
"""
import json
import os
import sys
import urllib.request

BASE = "https://zernio.com/api/v1"
RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _cle():
    cle = os.environ.get("ZERNIO_API_KEY")
    if cle:
        return cle
    chemin = os.path.join(RACINE, ".env")
    if os.path.exists(chemin):
        with open(chemin, encoding="utf-8") as f:
            for ligne in f:
                if ligne.startswith("ZERNIO_API_KEY="):
                    return ligne.split("=", 1)[1].strip()
    raise RuntimeError("ZERNIO_API_KEY introuvable (variable d'environnement ou .env)")


def _requete(methode, chemin, corps=None):
    donnees = json.dumps(corps).encode("utf-8") if corps is not None else None
    req = urllib.request.Request(
        BASE + chemin,
        data=donnees,
        method=methode,
        headers={
            "Authorization": "Bearer " + _cle(),
            "Content-Type": "application/json",
        },
    )
    with urllib.request.urlopen(req, timeout=60) as rep:
        return json.loads(rep.read().decode("utf-8") or "{}")


def lister_comptes(profil_id=None):
    """Retourne les comptes connectés (id, platform, ...). Lecture seule."""
    chemin = "/accounts" + (f"?profileId={profil_id}" if profil_id else "")
    return _requete("GET", chemin)


def creer_profil(nom, description=""):
    """Crée un profil (ex. « Clash Center »)."""
    return _requete("POST", "/profiles", {"name": nom, "description": description})


def lien_connexion_tiktok(profil_id, redirection=None):
    """Retourne authUrl à ouvrir par le propriétaire du compte TikTok."""
    chemin = f"/connect/tiktok?profileId={profil_id}"
    if redirection:
        chemin += "&redirect_url=" + redirection
    return _requete("GET", chemin)


def televerser_video(nom_fichier, contenu_type="video/mp4"):
    """Demande une URL présignée. Retourne uploadUrl et publicUrl.

    L'envoi du fichier se fait ensuite avec un PUT vers uploadUrl.
    """
    return _requete(
        "POST",
        "/media/presign",
        {"filename": nom_fichier, "contentType": contenu_type},
    )


def programmer_post_tiktok(profil_id, compte_id, texte, url_video, date_iso, fuseau="Europe/Paris"):
    """Programme une vidéo TikTok. Ne s'exécute que si on l'appelle explicitement."""
    corps = {
        "content": texte,
        "scheduledFor": date_iso,
        "timezone": fuseau,
        "platforms": [{"platform": "tiktok", "accountId": compte_id}],
        "profileId": profil_id,
        "mediaItems": [{"type": "video", "url": url_video}],
        "tiktokSettings": {
            "privacy_level": "PUBLIC_TO_EVERYONE",
            "allow_comment": True,
            "allow_duet": True,
            "allow_stitch": True,
            "commercial_content_type": "none",
            "content_preview_confirmed": True,
            "express_consent_given": True,
            "media_type": "video",
            "video_made_with_ai": False,
        },
    }
    return _requete("POST", "/posts", corps)


if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == "comptes":
        print(json.dumps(lister_comptes(), indent=2, ensure_ascii=False))
    else:
        print("Usage : python3 outils/zernio.py comptes")
