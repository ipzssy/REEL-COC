import sys, math
import numpy as np
from PIL import Image, ImageDraw
import eng
from eng import *
S = eng.S; HD = S + "/h/"

def bob(path, a, b, cx, cy, w, rot=0, amp=14, spd=4, ph=0):
    def f(fr, t):
        if not (a <= t < b): return
        k = (t - a) / 0.3; s = ease_out_back(k) if k < 1 else 1.0
        paste_c(fr, load(path, w), cx, cy + amp * math.sin(t * spd + ph), s, rot + 3 * math.sin(t * 3 + ph))
    return f

def hpbar(a, b, cy, w=760, lvl=0.14):
    def f(fr, t):
        if not (a <= t < b): return
        k = (t - a) / 0.3; s = ease_out_back(k) if k < 1 else 1.0
        lay = Image.new("RGBA", (w + 30, 90), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
        d.rounded_rectangle((5, 5, w + 25, 80), 36, fill=(30, 30, 30, 255), outline=(0, 0, 0), width=6)
        pulse = 0.5 + 0.5 * math.sin((t - a) * 9)
        d.rounded_rectangle((14, 14, 14 + int((w - 8) * lvl), 71), 28, fill=(235, int(40 + 40 * pulse), 40))
        paste_c(fr, lay, 540, cy, s)
    return f

def glow(path, a, b, cx, cy, w, col=(255, 120, 255)):
    def f(fr, t):
        if not (a <= t < b): return
        k = (t - a) / 0.3; s = ease_out_back(k) if k < 1 else 1.0
        im = load(path, w)
        gl = Image.new("RGBA", (int(w * 1.5), int(w * 1.5)), (0, 0, 0, 0)); d = ImageDraw.Draw(gl)
        r = int(w * (0.62 + 0.05 * math.sin((t - a) * 6)))
        d.ellipse((gl.width // 2 - r, gl.height // 2 - r, gl.width // 2 + r, gl.height // 2 + r), fill=col + (120,))
        gl = gl.filter(ImageFilter.GaussianBlur(50))
        paste_c(fr, gl, cx, cy, s); paste_c(fr, im, cx, cy + 10 * math.sin(t * 5), s, 4 * math.sin(t * 3))
    return f

def purple():
    y = np.linspace(0, 1, H)[:, None, None]
    top = np.array([70, 30, 140]); bot = np.array([160, 70, 200])
    return Image.fromarray(((top * (1 - y) + bot * y) * np.ones((1, W, 1))).astype(np.uint8)).convert("RGBA")

def build():
    sc = []
    bgA = lambda: VidBG("clip_17h06.mp4", 5, 4.2, blur=3, dim=0.5, zoom=1.0)
    KO = [bob(HD + "bk_ko.png", 0.0, 3.52, 300, 620, 620, -6, ph=0), bob(HD + "aq_ko.png", 0.0, 3.52, 790, 600, 480, 6, ph=2)]
    sc.append(Scene(0, 3.52, bgA(), [
        pop("TES HÉROS", 0.0, 0.22, 1150, 220, WHT, -3),
        pop("MEURENT", 0.22, 0.44, 1150, 230, RED, 2),
        pop("TROP VITE ?", 0.44, 1.14, 1150, 220, YEL, -2),
        pop("LE PROBLÈME", 1.14, 2.72, 1150, 190, WHT, 2),
        pop("LEURS CAPACITÉS", 2.72, 3.52, 1150, 150, YEL, -2),
        *KO]))
    sc.append(Scene(3.52, 6.66, blurred_wall("clip_17h17.mp4", 20, 3.5, 0.5), [
        pop("RÈGLE", 3.52, 3.94, 300, 200, WHT),
        pop("N°1", 3.94, 6.66, 300, 260, RED, -3),
        rframe(HD + "bk_icon.png", 3.7, 6.66, 200, 760, 280, 280, (255, 214, 40)),
        rframe(HD + "aq_icon.png", 3.8, 6.66, 540, 760, 280, 280, (255, 214, 40)),
        rframe(HD + "gw_icon.png", 3.9, 6.66, 880, 760, 280, 280, (255, 214, 40)),
        pop("CAPACITÉ", 4.0, 6.66, 1000, 130, CYA, 0),
        pop("GARDE", 4.64, 5.08, 1150, 220, WHT, 2),
        pop("LA CAPACITÉ", 5.08, 5.7, 1150, 200, YEL, -2),
        pop("MOMENT CRITIQUE", 5.7, 6.66, 1150, 160, RED, 2),
        flash(3.52)]))
    sc.append(Scene(6.66, 10.8, blurred_wall("clip_17h19.mp4", 40, 4.5, 0.5), [
        pop("RÈGLE", 6.66, 7.14, 230, 170, WHT),
        pop("N°2", 7.14, 10.8, 230, 230, RED, -3),
        bob(S + "/proj/../r/Barbarian_King_info_4.png", 7.6, 10.8, 290, 640, 540, 0, 10, 4, 0),
        bob(HD + "aq.png", 7.8, 10.8, 790, 640, 540, 0, 10, 4, 2),
        pop("ILS SE SOIGNENT", 8.26, 8.98, 1080, 150, GRN, -2),
        pop("AVEC LEUR CAPACITÉ", 8.98, 9.54, 1080, 130, WHT, 2),
        hpbar(9.54, 10.8, 1280),
        pop("DANS LE ROUGE", 9.54, 10.8, 1470, 190, RED, -2),
        flash(6.66)]))
    sc.append(Scene(10.8, 14.43, Static(purple(), 10), [
        pop("RÈGLE", 10.8, 11.24, 230, 170, WHT),
        pop("N°3", 11.24, 14.43, 230, 230, YEL, -3),
        glow(HD + "tome_e.png", 11.82, 14.43, 540, 760, 640),
        pop("TOME ÉTERNEL", 11.82, 12.82, 1250, 160, WHT, -2),
        pop("PROTÈGE TES TROUPES", 12.82, 14.43, 1250, 120, CYA, 2),
        bob(HD + "gw_icon.png", 12.4, 14.43, 540, 1480, 300, 0, 10, 5, 1),
        flash(10.8)]))
    sc.append(Scene(14.43, 15.98, VidBG("clip_17h06.mp4", 50, 2.0, blur=2, dim=0.45), [
        pop("LANCE-LE", 14.43, 14.84, 700, 250, YEL, -3),
        pop("SOUS LE FEU", 14.84, 15.98, 1000, 220, ORG, 3),
        glow(HD + "tome_h.png", 14.5, 15.98, 540, 1450, 460, (255, 200, 60)),
        flash(14.43)]))
    sc.append(Scene(15.98, 17.64, Static(grass(), 10), [
        pop("RÉSULTAT", 15.98, 16.5, 250, 200, WHT, -2),
        pop("BIEN PLUS LOIN", 16.5, 17.64, 1560, 170, YEL, 2),
        bob(HD + "aq.png", 16.0, 17.64, 740, 900, 560, 0, 10, 4, 0),
        bob(S + "/r/Barbarian_King_info_4.png", 16.1, 17.64, 330, 900, 540, 0, 10, 4, 2),
        flash(15.98)]))
    sc.append(Scene(17.64, 22.3, blurred_wall("clip_17h25.mp4", 60, 5, 0.5), [
        pop("REINE OU ROI ?", 17.64, 18.3, 230, 170, YEL),
        bob(HD + "aq.png", 17.7, 22.3, 760, 760, 500, 0, 10, 4, 0),
        bob(S + "/r/Barbarian_King_info_4.png", 17.8, 22.3, 320, 760, 480, 0, 10, 4, 2),
        pop("REINE", 17.84, 22.3, 1110, 100, PINK, 0, 760),
        pop("ROI", 17.92, 22.3, 1110, 100, ORG, 0, 320),
        pop("LEQUEL PORTE", 18.3, 18.98, 1330, 150, WHT, -2),
        pop("TES ATTAQUES ?", 18.98, 19.86, 1330, 150, YEL, 2),
        pop("DIS-LE EN COMMENTAIRE", 19.86, 20.92, 1530, 105, WHT, -1),
        pop("REJOINS LE DISCORD", 20.92, 21.8, 1530, 120, CYA, 1),
        pop("LIEN EN BIO", 21.8, 22.3, 1530, 170, YEL, -2),
        flash(17.64)]))
    sc.append(Scene(22.3, 23.85, bgA(), [
        *[bob(a.path if False else p, 22.3, 23.85, cx, cy, w, r, ph=ph) for p, cx, cy, w, r, ph in
          [(HD + "bk_ko.png", 300, 620, 620, -6, 0), (HD + "aq_ko.png", 790, 600, 480, 6, 2)]],
        pop("SINON, VOILÀ", 22.38, 23.0, 1150, 200, WHT, -2),
        pop("CE QUI ARRIVE…", 23.0, 23.85, 1150, 190, RED, 2)]))
    return sc

eng.BUILDS["heroes"] = build
if __name__ == "__main__":
    from multiprocessing import Pool
    eng.CUR["name"] = "heroes"
    n = len(build())
    sel = [int(a) for a in sys.argv[1:]] or list(range(n))
    with Pool(2) as p: p.map(eng.render_scene, sel)
    if len(sys.argv) == 1:
        eng.assemble("heroes", S + "/h/heroes.wav", S + "/h/heroes.mp4")
