import sys, os
sys.path.insert(0, os.getcwd())
from mg import *
from PIL import ImageDraw as D2
FLUO = (255, 214, 0)
def fit(im, mw=860):
    return im if im.width <= mw else im.resize((mw, int(im.height * mw / im.width)), Image.LANCZOS)
img = BGIM.copy()
fr = Clip("troupes_01_super_dragons_masse", 9.5, 1, 880, 495).get(0.2)
paste_c(img, title("CLASH OF CLANS", 92, (200, 200, 205)), 515, 215)
paste_c(img, tag("3 ERREURS", RED, WHITE, 54), 515, 320, rot=-2)
paste_c(img, fit(title("POURQUOI TU", 150, WHITE)), 515, 470)
paste_c(img, fit(title("RATES", 270, FLUO)), 515, 650)
paste_c(img, fit(title("TES ATTAQUES ?", 150, WHITE)), 515, 835)
paste_c(img, card(fr, "tout au même endroit"), 505, 1150, rot=-3, scale=0.78)
paste_c(img, stamp("À ÉVITER", 110), 680, 1010, rot=10)
paste_c(img, fit(tag("QUI TE COÛTENT DES ÉTOILES", FLUO, (10, 10, 10), 62)), 515, 1455, rot=-1)
img.save("miniature_01.jpg", quality=93)
z = img.copy(); d = D2.Draw(z, "RGBA")
d.rectangle([0, 1540, 1080, 1920], fill=(255, 0, 0, 90)); d.rectangle([950, 760, 1080, 1540], fill=(255, 0, 0, 90))
z.resize((540, 960)).save("miniature_01_zones.png")
