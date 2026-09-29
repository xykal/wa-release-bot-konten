"""Cue per scene: SFX, stiker meme, konfeti — semuanya dikunci ke KATA yang diucapkan narator.

Format cue: ('sfx', t, nama, potong) | ('stiker', t, nama, posisi, dur) | ('konfeti', t, cx, cy).
Nama SFX bisa sintetis (pop, klik, ding, buzz, whoosh, sparkle, zzz — lihat audio.py) atau nama file di
aset/manifest.json (myinstants). `potong` = durasi maksimum SFX file (yang panjang dipotong + fade).
Efek visual (punch-in, guncang, kilat) diturunkan dari SFX-nya lewat tabel EFEK, jadi gambar & suara pasti sinkron.
"""

STIKER_UKURAN = {'ka': 190, 'ki': 190, 'kb': 190, 'kib': 190, 'tengah': 250}

# nama sfx → (punch zoom, guncang px, warna kilat atau None, alpha kilat)
EFEK = {
    'vine-boom': (0.10, 12, None, 0), 'buzz': (0.0, 8, None, 0), 'record-scratch': (0.0, 6, None, 0),
    'ding': (0.06, 0, (255, 255, 255), 0.30), 'family-feud-good-answer': (0.08, 0, (255, 255, 255), 0.35),
    'discord-notification': (0.05, 0, None, 0), 'cartoon-bonk': (0.08, 4, None, 0), 'whoosh': (0.04, 0, None, 0),
    'emergency-meeting': (0.0, 4, (241, 92, 109), 0.30), 'windows-10-error-sound': (0.0, 5, (241, 92, 109), 0.25),
    'tuturu_1': (0.0, 0, (37, 211, 102), 0.20), 'yeay': (0.06, 0, (255, 255, 255), 0.25),
}


def _bersih(k):
    return k.strip('.,?!:;"\'()').lower()


def kapan(sc, pemicu, cadangan=0.5):
    """Waktu absolut kata `pemicu` diucapkan (kemunculan pertama); fallback t_vo + cadangan."""
    for k, x, _ in sc['kata']:
        if _bersih(k) == _bersih(pemicu):
            return x
    return sc['t_vo'] + cadangan


def S(t, nama, potong=2.0):
    return ('sfx', t, nama, potong)


def K(t, nama, posisi='ka', dur=2.6):
    return ('stiker', t, nama, posisi, dur)


def bangun_cue(sc):
    k = lambda kata, cadangan=1.0: kapan(sc, kata, cadangan)  # noqa: E731 — biar tabel di bawah pendek
    v = sc['t_vo']
    c = [S(sc['t0'] + 0.05, 'whoosh')] + [S(t, 'pop') for t, _, _ in sc['tahap_t']]
    m = sc['layar']
    if m == 'masalah':
        c += [S(v + d, 'pop') for d in (0.5, 1.1, 1.7)]
        c += [S(k('aneh?', 2.5), 'vine-boom'), K(k('aneh?', 2.5), 'doraemon_masalah', 'ka'),
              S(k('sepi?', 4.5), 'awkward-cricket-sound-effect', 1.6), K(k('sepi?', 4.5), 'read_aja', 'ki'),
              S(k('lupa', 6.5), 'windows-10-error-sound', 1.2), K(k('lupa', 6.5), 'jackjack_marah', 'kb'),
              S(k('Tenang,', 8.0), 'family-feud-good-answer'), S(k('satu', 8.6), 'ding')]
    elif m == 'beranda':
        c += [S(k('Kenalin,', 0.2), 'tuturu_1'), S(k('Android.', 5.5), 'mantappu', 1.5),
              S(k('Nggak', 6.5), 'fahhhhh'), K(k('Nggak', 6.5), 'pepe_capek', 'ka', 3.2),
              S(k('Termux.', 9.5), 'emotional-damage-meme', 1.6)]
    elif m == 'pairing':
        awal = k('masukin', 2.0)
        c += [S(awal + 0.45 + i * 0.13, 'klik') for i in range(8)]
        c += [S(k('Nyambunginnya', 0.2), 'anjayhaha', 1.7), K(k('Nyambunginnya', 0.2), 'jaka_sembung', 'ka', 3.0),
              S(k('Selesai!', 8.0), 'family-feud-good-answer'), S(k('Selesai!', 8.0) + 0.15, 'yeay'),
              ('konfeti', k('Selesai!', 8.0), 360, 620), S(k('kerja.', 9.8), 'discord-notification')]
    elif m == 'rilis':
        c += [S(k('posting', 3.0), 'whoosh'), S(k('channel.', 4.0) + 0.1, 'discord-notification'),
              S(k('Rapi', 5.0), 'original-sheesh', 1.6), K(k('Rapi', 5.0) + 0.3, 'mau_tium', 'kb'),
              S(k('ukurannya.', 9.5), 'ding')]
    elif m == 'grup':
        c += [S(k('Permintaan', 2.5), 'emergency-meeting', 1.4), K(k('Permintaan', 2.5), 'plonga_plongo', 'ki', 2.4),
              S(k('Ditolak.', 7.0), 'buzz'), S(k('Ditolak.', 7.0) + 0.05, 'vine-boom'),
              K(k('Ditolak.', 7.0) + 0.05, 'pemaaf', 'tengah', 2.2),
              S(k('Kamu', 9.0), 'respek', 1.5), K(k('Kamu', 9.0), 'gk_tau_gk_liat', 'ka', 3.0)]
    elif m == 'lagu':
        c += [S(k('sepi.', 1.5), 'cartoon-bonk'), K(k('sepi.', 1.5), 'sabar_menanti', 'ka'),
              S(k('ngirim', 3.0), 'pop'), S(k('ngirim', 3.0), 'sparkle-sound-effect', 1.2),
              K(k('voice', 6.0), 'sakitin_lagi', 'kb', 2.8), S(k('Ada', 7.5), 'omgwow', 1.6), S(k('trend', 10.0), 'ding')]
    elif m == 'caption':
        c += [S(k('galau,', 2.0), 'pop'), S(k('galau,', 2.0), 'sad-violin', 1.5), K(k('galau,', 2.0), 'kalo_suka_bilang', 'ki', 2.4),
              S(k('motivasi,', 3.0), 'pop'), S(k('motivasi,', 3.0), 'kids-saying-yay-sound-effect_3', 1.0),
              S(k('nyindir,', 4.0), 'pop'), S(k('nyindir,', 4.0), 'tapi-boong-hahaha', 1.5), K(k('nyindir,', 4.0), 'alergi_buaya', 'ka', 2.6),
              S(k('ayat.', 5.0), 'pop'), S(k('di-repeat?', 10.0), 'vine-boom'), K(k('di-repeat?', 10.0), 'pedih_sekali', 'tengah', 2.4),
              S(k('di-repeat?', 10.0) + 0.4, 'ngakak-laugh-annoying', 1.8)]
    elif m == 'lapor':
        g = k('gagal', 1.5)
        c += [S(g, 'windows-10-error-sound', 1.0), S(g + 0.5, 'cartoon-bonk'), S(g + 1.0, 'cartoon-bonk'),
              S(k('lapor', 3.0), 'discord-notification'), K(k('lapor', 3.0), 'sambil_nangis', 'ka', 2.8),
              S(k('tidur.', 7.0), 'zzz'), K(k('tidur.', 7.0), 'baru_bangun', 'kb', 3.0), S(k('Baterai', 8.5), 'ding')]
    elif m == 'github':
        c += [S(k('gratis,', 2.0), 'record-scratch'), K(k('gratis,', 2.0), 'bayar', 'ka', 3.0), S(k('gratis,', 2.0) + 0.6, 'sparkle'),
              S(k('Kodenya', 5.0), 'discord-notification'), S(k('di-pin.', 8.0), 'ding')]
    elif m == 'cta':
        c += [S(v + d, 'pop') for d in (0.6, 1.4, 2.2)]
        c += [S(k('Follow,', 5.0), 'rizz-sound-effect'), K(k('Follow,', 5.0), 'permisi_seumur_hidup', 'ka', 3.2),
              S(k('Follow,', 5.0) + 0.3, 'yeay'), ('konfeti', k('Follow,', 5.0), 360, 640),
              S(k('berikutnya!', 8.0), 'sparkle'), K(sc['t1'] + 0.25, 'maaciii', 'kb', 2.4),
              S(sc['t1'] + 0.25, 'sparkle-sound-effect', 1.5)]
    return c


def efek_dari_cue(cue):
    """Daftar (t, punch, guncang, warna, alpha) buat fx.py — diturunkan dari SFX yang punya entri EFEK."""
    return [(x[1],) + EFEK[x[2]] for x in cue if x[0] == 'sfx' and x[2] in EFEK]
