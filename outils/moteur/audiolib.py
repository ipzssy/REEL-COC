import math, wave
import numpy as np
from tl import *

SR = 44100
N = int(round(TOTAL * SR))
rng = np.random.default_rng(3)
two_pi = 2 * math.pi


def tt(dur):
    return np.arange(int(dur * SR)) / SR


def put(arr, t0, sig, gain=1.0):
    i = int(round(t0 * SR))
    if i >= len(arr) or i < 0:
        return
    j = min(len(arr), i + len(sig))
    arr[i:j] += sig[: j - i] * gain


def lowpass_sweep(x, f0, f1):
    n = len(x)
    out = np.zeros(n)
    y = 0.0
    for k in range(n):
        fc = f0 + (f1 - f0) * (k / n)
        a = 1 - math.exp(-two_pi * fc / SR)
        y += a * (x[k] - y)
        out[k] = y
    return out


# ------------------------------------------------------------ instruments
def kick():
    t = tt(0.32)
    ph = two_pi * (48 * t + 110 * (1 - np.exp(-35 * t)) / 35)
    return np.sin(ph) * np.exp(-t * 8) + 0.25 * np.exp(-t * 400) * rng.standard_normal(len(t))


def clap():
    t = tt(0.22)
    n = rng.standard_normal(len(t))
    n = np.concatenate([[0], np.diff(n)])
    return n * np.exp(-t * 20) * 0.45 + np.sin(two_pi * 190 * t) * np.exp(-t * 35) * 0.25


def hat(v=1.0):
    t = tt(0.07)
    n = rng.standard_normal(len(t))
    n = np.concatenate([[0], np.diff(n)])
    return n * np.exp(-t * 90) * 0.22 * v


def bass(f):
    t = tt(0.42)
    s = sum(np.sin(two_pi * f * h * t) / h for h in range(1, 6))
    return s * np.exp(-t * 5.5) * 0.30


def pluck(f):
    t = tt(0.30)
    return (np.sin(two_pi * f * t) + 0.45 * np.sin(two_pi * 2 * f * t)) * np.exp(-t * 13) * 0.17


def pad(freqs, dur):
    t = tt(dur)
    env = np.sin(np.pi * np.clip(t / dur, 0, 1)) ** 0.7
    s = sum(np.sin(two_pi * f * t) + 0.3 * np.sin(two_pi * 2 * f * t) for f in freqs)
    return s * env * 0.045


# ------------------------------------------------------------ sfx
def sfx_boom():
    t = tt(1.2)
    ph = two_pi * (36 * t + 70 * (1 - np.exp(-6 * t)) / 6)
    s = np.sin(ph) * np.exp(-t * 3.2)
    n = lowpass_sweep(rng.standard_normal(int(0.25 * SR)), 3000, 300) * np.exp(-tt(0.25) * 14)
    s[: len(n)] += n * 0.8
    return s * 0.9


def sfx_whoosh(dur=0.4):
    x = rng.standard_normal(int(dur * SR))
    y = lowpass_sweep(x, 400, 5500)
    env = np.sin(np.pi * np.linspace(0, 1, len(y))) ** 2
    return y * env * 1.6


def sfx_riser(dur):
    n = int(dur * SR)
    x = rng.standard_normal(n)
    y = lowpass_sweep(x, 250, 9000)
    k = np.linspace(0, 1, n)
    env = k ** 2.2
    t = tt(dur)
    tone = np.sin(two_pi * (220 * t + 700 * t * t / dur))
    return (y * 1.5 + tone * 0.25) * env * 0.8


def sfx_pop():
    t = tt(0.12)
    ph = two_pi * (520 * t + 360 * (1 - np.exp(-30 * t)) / 30)
    return np.sin(ph) * np.exp(-t * 32) * 0.7


def sfx_buzz():
    out = np.zeros(int(0.5 * SR))
    for off in (0.0, 0.16):
        t = tt(0.13)
        s = sum(np.sin(two_pi * 95 * h * t) / h for h in range(1, 9)) * np.exp(-t * 9) * 0.5
        put(out, off, s)
    return out


def sfx_ding():
    t = tt(1.1)
    s = (np.sin(two_pi * 988 * t) + 0.65 * np.sin(two_pi * 1319 * t) + 0.3 * np.sin(two_pi * 2637 * t)) * np.exp(-t * 4.2)
    return s * 0.42


def sfx_alert():
    return sfx_buzz() * 0.8 + np.pad(sfx_boom()[: int(0.5 * SR)], (0, 0)) * 0.3


