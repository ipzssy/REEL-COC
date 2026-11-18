import sys, math
import numpy as np
from PIL import Image, ImageDraw
import eng
from eng import *
from heroes import bob, glow, purple
S = eng.S; E = S + "/e/"
def row(path, a, b, cy, n, w, gap):
    its = []
    for i in range(n):
        x0 = 540 - (n - 1) * gap / 2 + i * gap
        its.append(bob(path, a + 0.12 * i, b, x0, cy + (30 if i % 2 else 0), w, 0, 12, 5, i))
    return its
def shake(txt, a, b, cy, sz, col):
    def f(fr, t):
        if a <= t < b:
            pop(txt, a, b, cy + int(10 * math.sin(t * 60)), sz, col, -3)(fr, t)
    return f
def bgA(ss=70): return VidBG("clip_17h06.mp4", ss, 4.2, blur=3, dim=0.5, zoom=1.0)
def build():
    T = [0, 3.6, 6.55, 9.97, 12.75, 15.05, 18.21, 23.73, 24.85]
    sc = []
    sc.append(Scene(T[0], T[1], bgA(), [
        bob(E + "ed_info.png", 0, T[1], 540, 560, 800, 0, 18, 3),
        pop("UNE DES ARMÉES", 0.0, 0.54, 1250, 150, WHT, -2),
        pop("LES PLUS SIMPLES", 0.54, 1.14, 1250, 150, YEL, 2),
        pop("POUR GAGNER", 1.14, 1.76, 1250, 190, WHT, -2),
        pop("ÉLECTRO-DRAGONS", 1.76, 2.58, 1250, 140, CYA, 2),
        pop("VOICI COMMENT", 2.58, 3.3, 1250, 160, WHT, -2),
        pop("LES JOUER", 3.3, T[1], 1250, 230, YEL, 2)]))
    sc.append(Scene(T[1], T[2], blurred_wall("clip_17h19.mp4", 30, 3.3, 0.5), [
        pop("RÈGLE", T[1], 4.06, 230, 170, WHT), pop("N°1", 4.06, T[2], 230, 230, CYA, -3),
        *row(E + "ed10.png", 3.9, T[2], 640, 3, 330, 330),
        *row(E + "ed10.png", 4.1, T[2], 940, 3, 330, 330),
        pop("EN LIGNE", 4.64, 5.4, 1350, 230, WHT, -2),
        pop("UN SEUL CÔTÉ", 5.4, T[2], 1350, 170, YEL, 2), flash(T[1])]))
    sc.append(Scene(T[2], T[3], blurred_wall("clip_17h25.mp4", 90, 3.6, 0.5), [
        pop("RÈGLE", T[2], 7.3, 230, 170, WHT), pop("N°2", 7.3, T[3], 230, 230, CYA, -3),
        bob(E + "ed2.png", 6.8, T[3], 330, 680, 700, 0, 14, 4),
        *[bob(E + "ad15.png", 7.4 + 0.12 * i, T[3], 700 + 100 * i, 760 + 30 * (i % 2), 230, 0, 6, 4, i) for i in range(3)],
        bob(E + "lightning.png", 7.4, T[3], 540, 1060, 240, 0, 12, 6),
        pop("L'ÉCLAIR REBONDIT", 7.48, 8.84, 1330, 120, CYA, -2),
        pop("ZONES SERRÉES", 8.84, T[3], 1330, 170, YEL, 2), flash(T[2])]))
    sc.append(Scene(T[3], T[4], Static(purple(), 10), [
        pop("RÈGLE", T[3], 10.76, 230, 170, WHT), pop("N°3", 10.76, T[4], 230, 230, PINK, -3),
        glow(E + "rage.png", 10.98, T[4], 540, 800, 620, (255, 90, 255)),
        pop("LA RAGE", 10.98, 11.56, 1330, 220, PINK, -2),
        pop("AU CŒUR DE LA BASE", 11.56, T[4], 1330, 120, WHT, 2), flash(T[3])]))
    sc.append(Scene(T[4], T[5], bgA(40), [
        shake("ATTENTION", T[4], 13.44, 330, 230, RED),
        bob(E + "ad15.png", 13.0, T[5], 540, 820, 420, 0, 12, 4),
        pop("ILS SONT LENTS", 13.44, 14.06, 1300, 150, ORG, -2),
        pop("FACE AUX DÉFENSES AÉRIENNES", 14.06, T[5], 1300, 100, WHT, 2), flash(T[4])]))
    sc.append(Scene(T[5], T[6], bgA(85), [
        pop("RÉSULTAT", T[5], 15.74, 260, 210, WHT, -2),
        bob(E + "ed_info.png", 15.2, T[6], 540, 760, 760, 0, 16, 4),
        pop("LA BASE SE VIDE", 15.74, 16.46, 1300, 150, GRN, 2),
        pop("BÂTIMENT APRÈS BÂTIMENT", 16.46, T[6], 1300, 100, YEL, -2), flash(T[5])]))
    sc.append(Scene(T[6], T[7], blurred_wall("clip_17h17.mp4", 50, 5.6, 0.5), [
        bob(E + "ed_info.png", 18.3, T[7], 300, 620, 500, 0, 12, 4, 0),
        bob(E + "dragon_info.png", 18.5, T[7], 790, 620, 440, 0, 12, 4, 2),
        pop("ÉLECTRO", 18.24, T[7], 1000, 90, CYA, 0, 300), pop("DRAGONS", 18.82, T[7], 1000, 90, ORG, 0, 790),
        pop("ÉLECTRO OU DRAGONS ?", 18.24, 19.88, 1230, 105, YEL, -1),
        pop("TU JOUES QUOI ?", 19.88, 20.78, 1230, 150, WHT, 2),
        pop("DIS-LE EN COMMENTAIRE", 20.78, 21.9, 1480, 105, WHT, -1),
        pop("REJOINS LE DISCORD", 21.9, 23.0, 1480, 125, CYA, 1),
        pop("LIEN EN BIO", 23.0, T[7], 1480, 170, YEL, -2), flash(T[6])]))
    sc.append(Scene(T[7], T[8], bgA(), [
        bob(E + "ed_info.png", T[7], T[8], 540, 560, 800, 0, 18, 3),
        pop("ET N'OUBLIE PAS,", T[7], 24.5, 1250, 150, WHT, -2),
        pop("C'EST…", 24.5, T[8], 1250, 230, YEL, 2)]))
    return sc
eng.BUILDS["electro"] = build
if __name__ == "__main__":
    from multiprocessing import Pool
    eng.CUR["name"] = "electro"
    n = len(build())
    sel = [int(a) for a in sys.argv[1:]] or list(range(n))
    with Pool(2) as p: p.map(eng.render_scene, sel)
    if len(sys.argv) == 1: eng.assemble("electro", S + "/e/electro.wav", S + "/e/electro.mp4")
