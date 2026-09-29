"""Timeline + audio: VO dari vo/*.wav, waktu per kata, SFX & musik sintetis.

Semua SFX dan musik latar dibuat dari numpy (sinus, noise, envelope) supaya
tidak ada satu pun aset audio pihak ketiga di repo ini — pelajaran dari audit
repo produk (SFX meme tanpa lisensi). Kualitasnya sederhana, tapi bersih.
"""
import math
import os
import wave
import numpy as np
from naskah import SCENES, JEDA_AWAL, JEDA_AKHIR, OUTRO, KARAKTER_PER_DETIK

AKAR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SR = 24000


def baca_wav(path):
    w = wave.open(path)
    a = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
    if w.getnchannels() == 2:
        a = a.reshape(-1, 2).mean(axis=1)
    sr = w.getframerate()
    if sr != SR:
        a = np.interp(np.arange(0, len(a), sr / SR), np.arange(len(a)), a).astype(np.float32)
    return a


def _bersih(k):
    return k.strip('.,?!:;"\'()').lower()


def waktu_kata(a, teks):
    """Taksir waktu tiap kata dari energi sinyal: bagian bicara dipetakan ke kata
    sebanding panjang hurufnya. Bukan ASR, tapi cukup buat sorotan karaoke."""
    kata = teks.split()
    dur = len(a) / SR
    fr = SR // 100
    if len(a) < fr * 5:
        return _rata(kata, 0, dur)
    rms = np.sqrt(np.convolve(a ** 2, np.ones(fr) / fr, 'same')[::fr])
    bicara = rms >= max(0.01, rms.max() * 0.06)
    idx = np.nonzero(bicara)[0]
    if len(idx) < 5:
        return _rata(kata, 0, dur)
    t = [k / 100 for k in range(idx[0], idx[-1] + 1)]
    bobot = [len(_bersih(k)) + 1.6 + (1.2 if k[-1] in '.,?!' else 0) for k in kata]
    tot, acc, hasil, n = sum(bobot), 0.0, [], len(t)
    for k, b in zip(kata, bobot):
        i0 = int(acc / tot * (n - 1))
        acc += b
        i1 = int(acc / tot * (n - 1))
        hasil.append((k, t[i0], t[min(i1, n - 1)] + 0.01))
    return hasil


def _rata(kata, mulai, dur):
    n = max(1, len(kata))
    return [(k, mulai + i * dur / n, mulai + (i + 1) * dur / n) for i, k in enumerate(kata)]


def bangun_timeline():
    """Balikin (scenes, total). Tiap scene dapat: t0, t_vo, t1, kata (absolut), tahap_t, cue."""
    hasil, kursor = [], 0.0
    for s in SCENES:
        path = os.path.join(AKAR, 'vo', s['vo'] + '.wav')
        if os.path.exists(path):
            a = baca_wav(path)
        else:
            a = np.zeros(int(len(s['teks']) / KARAKTER_PER_DETIK * SR), np.float32)
        dur = len(a) / SR
        t_vo = kursor + JEDA_AWAL
        kata = [(k, t_vo + x, t_vo + y) for k, x, y in waktu_kata(a, s['teks'])]
        tahap_t = []
        for pemicu, judul, mode in s.get('tahap', []):
            cocok = [x for k, x, _ in kata if _bersih(k) == _bersih(pemicu)]
            tahap_t.append((cocok[0] if cocok else t_vo + dur * 0.6, judul, mode))
        sc = dict(s, t0=kursor, t_vo=t_vo, dur_vo=dur, t1=t_vo + dur + JEDA_AKHIR, kata=kata, tahap_t=tahap_t, sinyal=a)
        sc['cue'] = _cue_scene(sc)
        hasil.append(sc)
        kursor = sc['t1']
    return hasil, kursor + OUTRO


def kapan(sc, pemicu, cadangan=0.5):
    """Waktu absolut kata `pemicu` diucapkan (kemunculan pertama)."""
    for k, x, _ in sc['kata']:
        if _bersih(k) == _bersih(pemicu):
            return x
    return sc['t_vo'] + cadangan


def _cue_scene(sc):
    """Cue SFX per scene — sinkron dengan yang digambar layar_*.py (pakai fungsi `kapan` yang sama)."""
    c = [(sc['t0'] + 0.05, 'whoosh')]
    c += [(t, 'pop') for t, _, _ in sc['tahap_t']]
    m = sc['layar']
    if m == 'masalah':
        c += [(sc['t_vo'] + d, 'pop') for d in (0.5, 1.1, 1.7)]
    elif m == 'pairing':
        awal = kapan(sc, 'masukin', 2.0)
        c += [(awal + 0.45 + i * 0.13, 'klik') for i in range(8)] + [(kapan(sc, 'Selesai!', 8.0), 'ding')]
    elif m == 'rilis':
        c += [(kapan(sc, 'posting', 3.0), 'whoosh'), (kapan(sc, 'channel.', 4.0) + 0.1, 'ding')]
    elif m == 'grup':
        c += [(kapan(sc, 'Ditolak.', 7.0), 'buzz'), (kapan(sc, 'Kamu', 9.0), 'ding')]
    elif m == 'lagu':
        c += [(kapan(sc, 'ngirim', 3.0), 'pop')]
    elif m == 'caption':
        c += [(kapan(sc, k, 2 + i), 'pop') for i, k in enumerate(('galau,', 'motivasi,', 'nyindir,', 'ayat.'))]
    elif m == 'lapor':
        c += [(kapan(sc, 'lapor', 3.0), 'ding'), (kapan(sc, 'tidur.', 7.0), 'zzz')]
    elif m == 'github':
        c += [(kapan(sc, 'gratis,', 2.0), 'sparkle')]
    elif m == 'cta':
        c += [(kapan(sc, 'Follow,', 5.0), 'sparkle')]
    return c


# ---------- sintesis SFX ----------
def _env(n, serang=0.005, lepas=0.15):
    t = np.arange(n) / SR
    return np.minimum(t / serang, 1.0) * np.exp(-t / lepas)


def _sfx(nama, rng):
    if nama == 'pop':
        n = int(0.09 * SR); t = np.arange(n) / SR
        f = 520 * np.exp(-t * 18) + 160
        return 0.6 * np.sin(2 * np.pi * np.cumsum(f) / SR) * _env(n, 0.002, 0.03)
    if nama == 'klik':
        n = int(0.03 * SR)
        return 0.35 * rng.standard_normal(n) * _env(n, 0.001, 0.006)
    if nama == 'ding':
        n = int(0.7 * SR); t = np.arange(n) / SR
        return 0.45 * (np.sin(2 * np.pi * 1318 * t) + 0.4 * np.sin(2 * np.pi * 2637 * t)) * _env(n, 0.003, 0.22)
    if nama == 'buzz':
        n = int(0.22 * SR); t = np.arange(n) / SR
        return 0.4 * np.sign(np.sin(2 * np.pi * 110 * t)) * (0.6 + 0.4 * np.sin(2 * np.pi * 30 * t)) * _env(n, 0.004, 0.12)
    if nama == 'whoosh':
        n = int(0.32 * SR)
        x = rng.standard_normal(n)
        y = np.zeros(n, np.float32); lp = 0.0
        for i in range(n):
            a = 0.02 + 0.25 * (i / n)
            lp += a * (x[i] - lp)
            y[i] = lp
        return 2.2 * y * np.sin(np.linspace(0, math.pi, n)) ** 2
    if nama == 'sparkle':
        y = np.zeros(int(0.6 * SR), np.float32)
        for i, f in enumerate((1568, 1976, 2349, 3136)):
            n = int(0.25 * SR); t = np.arange(n) / SR
            s = int(i * 0.07 * SR)
            y[s:s + n] += 0.3 * np.sin(2 * np.pi * f * t) * _env(n, 0.002, 0.09)
        return y
    if nama == 'zzz':
        n = int(0.9 * SR); t = np.arange(n) / SR
        return 0.25 * np.sin(2 * np.pi * 330 * t * (1 - 0.15 * t)) * np.sin(2 * np.pi * 3 * t) ** 2 * _env(n, 0.05, 0.6)
    return np.zeros(1, np.float32)


def musik(total, rng):
    """Pad lo-fi pelan: progresi Am–F–C–G, sinus ditumpuk + sedikit detune, dilembutkan."""
    n = int(total * SR)
    y = np.zeros(n, np.float32)
    akor = [(220.0, 261.6, 329.6), (174.6, 220.0, 261.6), (130.8, 164.8, 196.0), (196.0, 246.9, 293.7)]
    bar = 60 / 76 * 4
    t = np.arange(n) / SR
    for i in range(int(total / bar) + 1):
        a, b = int(i * bar * SR), min(n, int((i + 1) * bar * SR))
        if a >= n:
            break
        tt = t[a:b] - t[a]
        env = np.minimum(tt / 0.6, 1.0) * np.minimum((bar - tt) / 0.8, 1.0)
        seg = np.zeros(b - a, np.float32)
        for f in akor[i % 4]:
            for det in (0.997, 1.0, 1.004):
                seg += np.sin(2 * np.pi * f * det * tt + rng.uniform(0, 6.28)) / 9
            seg += 0.15 * np.sin(2 * np.pi * f / 2 * tt) / 3
        y[a:b] += seg * np.clip(env, 0, 1)
    lp, out = 0.0, np.zeros(n, np.float32)
    for i in range(n):
        lp += 0.08 * (y[i] - lp)
        out[i] = lp
    return out


def campur(scenes, total, path_keluar, dengan_musik=True):
    """VO + SFX + musik (di-duck waktu narator ngomong) → WAV mono 24 kHz."""
    n = int(total * SR)
    vo = np.zeros(n, np.float32)
    for sc in scenes:
        a = sc['sinyal']; s = int(sc['t_vo'] * SR)
        vo[s:s + len(a)] += a[:max(0, n - s)]
    rng = np.random.default_rng(7)
    sfx = np.zeros(n, np.float32)
    for sc in scenes:
        for t, nama in sc['cue']:
            y = _sfx(nama, rng).astype(np.float32); s = int(t * SR)
            if 0 <= s < n:
                sfx[s:s + len(y)] += y[:n - s]
    out = vo * 0.95 + sfx * 0.5
    if dengan_musik:
        m = musik(total, rng)
        fr = SR // 20
        blok = np.sqrt((np.pad(vo, (0, (-len(vo)) % fr)) ** 2).reshape(-1, fr).mean(axis=1))
        blok = np.maximum(blok, np.concatenate(([0], blok[:-1])) * 0.85)  # lepas pelan, biar nggak kedip
        amp = np.repeat(blok, fr)[:n]
        duck = 1.0 - 0.65 * np.clip(amp / 0.05, 0, 1)
        out += m * 0.10 * duck
    out = np.tanh(out * 1.1) * 0.92
    w = wave.open(path_keluar, 'wb')
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((out * 32767).astype(np.int16).tobytes())
    w.close()
