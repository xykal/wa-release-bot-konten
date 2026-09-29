"""Komposisi frame video TikTok Eps 2 — 720x1280 @ 60 fps.

Pakai:  python3 render/render.py            → keluaran/tiktok-wa-release-bot-eps2.mp4 (butuh ffmpeg, lihat encode.py)
        python3 render/render.py --cek 2    → gambar 1 frame tiap 2 detik tanpa encode (uji cepat)
        python3 render/render.py --frame 47.5 cek.png
        python3 render/render.py --info     → cetak timeline

Urutan lapisan tiap frame: latar + glow + ikon clay melayang → HP (layar scene + light sweep) → judul kinetik +
ilustrasi asli → outro → stiker meme → konfeti → subtitle karaoke → watermark/footer/progress → efek pasca
(punch-in, guncang, kilat). Semua fungsi murni dari `t` supaya bisa dirender paralel.
"""
import math
import os
import sys
from PIL import Image, ImageChops, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gaya import (W, H, FPS, BRAND, NAMA_PAKET, font, F_BLACK, F_SEMI, F_REG, BG, BG2, GARIS, HIJAU_T, HIJAU_TUA,
                  TEKS, TEKS2, e_out, e_back, prog, mix, lebar, kotak, pil_tembus, tempel, glow)
from aset import logo
from audio import bangun_timeline
from cue import efek_dari_cue
from fx import judul_kinetik, gambar_ilus, gambar_stiker, konfeti, ikon_melayang, efek_pasca
from layar_a import LAYAR_A, SW, SH
from layar_b import LAYAR_B
from naskah import INTRO, OUTRO, ILUS

AKAR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LAYAR = {**LAYAR_A, **LAYAR_B}
SCENES, TOTAL = bangun_timeline()
EFEK = [e for sc in SCENES for e in efek_dari_cue(sc['cue'])]
PX, PY = (W - SW) // 2, 262  # posisi isi layar HP
_cache = {}


def latar():
    if 'latar' not in _cache:
        im = Image.new('RGBA', (W, H), BG + (255,))
        d = ImageDraw.Draw(im)
        for y in range(H):
            d.line([(0, y), (W, y)], fill=mix(BG, (14, 30, 36), y / H))
        _cache['latar'] = im
        _cache['glow'] = glow(520, HIJAU_TUA, 90)
        _cache['glow2'] = glow(360, (20, 60, 90), 70)
        mask = Image.new('L', (SW, SH), 0)
        ImageDraw.Draw(mask).rounded_rectangle((0, 0, SW - 1, SH - 1), radius=28, fill=255)
        _cache['mask'] = mask
        band = pil_tembus((160, SH + 240))
        bd = ImageDraw.Draw(band)
        for x in range(160):
            bd.line([(x, 0), (x, SH + 240)], fill=(255, 255, 255, int(70 * math.sin(math.pi * x / 160) ** 2)))
        _cache['sweep'] = band.rotate(16, resample=Image.BICUBIC, expand=True)
    return _cache['latar'].copy()


def scene_pada(t):
    for i, sc in enumerate(SCENES):
        if t < sc['t1']:
            return i, sc
    return len(SCENES) - 1, SCENES[-1]


def judul_pada(sc, t):
    """Judul aktif + waktu mulainya + waktu ganti berikutnya (buat animasi keluar)."""
    daftar = [(sc['t0'], sc['judul'], 0)] + [(tt, j, m) for tt, j, m in sc['tahap_t']]
    aktif = daftar[0]
    for x in daftar:
        if t >= x[0]:
            aktif = x
    berikut = [x[0] for x in daftar if x[0] > aktif[0]]
    return aktif, (berikut[0] if berikut else sc['t1'])


def gambar_hp(im, t):
    i, sc = scene_pada(t)
    u_masuk = e_back(prog(t, INTRO - 0.2, 0.7))
    dy = (1 - u_masuk) * 900
    if t >= TOTAL - OUTRO:
        dy += e_out(prog(t, TOTAL - OUTRO, 0.4)) * 1100
    ox, oy = PX - 25, PY - 40 + dy
    d = ImageDraw.Draw(im)
    kotak(d, (ox - 4, oy - 4, ox + SW + 54, oy + SH + 84), 52, fill=(0, 0, 0, 110))
    kotak(d, (ox, oy, ox + SW + 50, oy + SH + 80), 48, fill=(24, 32, 38, 255), outline=GARIS + (255,), lebar_garis=3)
    layar = _layar_transisi(sc, i, t)
    u = prog(t, sc['t0'] + 0.1, 0.55)
    if 0 < u < 1:  # light sweep: kilau miring lewat di kaca HP tiap ganti scene
        layar = layar.copy()
        tempel(layar, _cache['sweep'], (-260 + u * (SW + 420), -120))
    im.paste(layar, (PX, int(PY + dy)), _cache['mask'])
    kotak(d, (W / 2 - 50, oy + 14, W / 2 + 50, oy + 30), 8, fill=(0, 0, 0, 255))


def _layar_transisi(sc, i, t):
    """Geser kiri antar scene selama 0.35 dtk: layar lama keluar, layar baru masuk."""
    _, _, mode = judul_pada(sc, t)[0]
    baru = LAYAR[sc['layar']](sc, t, mode)
    u = prog(t, sc['t0'], 0.35)
    if i == 0 or u >= 1:
        return baru
    lama_sc = SCENES[i - 1]
    lama = LAYAR[lama_sc['layar']](lama_sc, lama_sc['t1'] - 0.01, judul_pada(lama_sc, lama_sc['t1'] - 0.01)[0][2])
    geser = int(e_out(u) * SW)
    out = Image.new('RGBA', (SW, SH), BG2 + (255,))
    out.paste(lama, (-geser, 0))
    out.paste(baru, (SW - geser, 0))
    return out


def gambar_subtitle(im, sc, t):
    """Karaoke 2 baris: kata aktif hijau + sedikit membesar, kata lewat putih, kata belum abu."""
    f = font(F_SEMI, 27)
    kata = sc['kata']
    if not kata:
        return
    baris, kini = [], []
    for k, (w, a, b) in enumerate(kata):
        coba = ' '.join([x for x, _ in kini] + [w])
        if kini and lebar(coba, f) > W - 96:
            baris.append(kini)
            kini = []
        kini.append((w, k))
    if kini:
        baris.append(kini)
    sekarang = max([k for k, (w, a, b) in enumerate(kata) if a <= t] or [-1])
    baris_kini = next((n for n, br in enumerate(baris) if any(k == sekarang for _, k in br)), 0)
    hal = baris_kini // 2
    tampil = baris[hal * 2: hal * 2 + 2]
    alpha = e_out(prog(t, sc['t0'] + 0.1, 0.3)) * (1 - prog(t, sc['t1'] - 0.15, 0.15))
    lap = pil_tembus((W, 130))
    d = ImageDraw.Draw(lap)
    kotak(d, (24, 0, W - 24, 18 + len(tampil) * 40), 20, fill=(0, 0, 0, 165))
    for n, br in enumerate(tampil):
        y = 9 + n * 40
        teks = ' '.join(w for w, _ in br)
        x = W / 2 - lebar(teks, f) / 2
        for w, k in br:
            if k == sekarang:
                pop = 1 + 0.16 * (1 - e_out(prog(t, kata[k][1], 0.16)))
                fk = font(F_SEMI, int(27 * pop))
                d.text((x + (lebar(w, f) - lebar(w, fk)) / 2 + 2, y - (fk.size - 27) / 2 + 2), w, font=fk, fill=(0, 0, 0, 200))
                d.text((x + (lebar(w, f) - lebar(w, fk)) / 2, y - (fk.size - 27) / 2), w, font=fk, fill=HIJAU_T + (255,))
            else:
                d.text((x, y), w, font=f, fill=(TEKS if k < sekarang else TEKS2) + (255,))
            x += lebar(w + ' ', f)
    tempel(im, lap, (0, 1122), alpha)


def gambar_intro(im, t):
    """Logo XyVerse asli (lockup utuh) nge-pop di tengah, kilau lewat, tagline masuk; lalu naik & pudar pas HP masuk."""
    u_out = 1 - prog(t, INTRO - 0.15, 0.35)
    if u_out <= 0:
        return
    lap = pil_tembus((W, H))
    d = ImageDraw.Draw(lap)
    d.rectangle((0, 0, W, H), fill=BG + (255,))
    tempel(lap, _cache['glow'], (W / 2 - 260, 560 - 260), 0.9 * e_out(prog(t, 0.0, 0.6)))
    s = e_back(prog(t, 0.05, 0.55))
    if s > 0.02:
        wm = logo('xyverse_logo', 460).copy()
        u_k = prog(t, 0.7, 0.45)
        if 0 < u_k < 1:  # kilau: band putih miring digeser, dimask pakai alpha wordmark
            kilau = pil_tembus(wm.size)
            x = -120 + u_k * (wm.width + 240)
            ImageDraw.Draw(kilau).polygon([(x, 0), (x + 90, 0), (x + 40, wm.height), (x - 50, wm.height)], fill=(255, 255, 255, 170))
            kilau.putalpha(ImageChops.multiply(kilau.getchannel('A'), wm.getchannel('A')))
            wm.alpha_composite(kilau)
        m = wm.resize((max(1, int(wm.width * s)), max(1, int(wm.height * s))))
        tempel(lap, m, (W / 2 - m.width / 2, 560 - m.height / 2))
    u_t = e_out(prog(t, 0.6, 0.3))
    if u_t > 0:
        f = font(F_SEMI, 22)
        s2 = 'WA Release Bot  ·  Eps 2'
        d.text((W / 2 - lebar(s2, f) / 2, 650 + (1 - u_t) * 20), s2, font=f, fill=TEKS2 + (int(255 * u_t),))
    tempel(im, lap, (0, -(1 - u_out) * 60), u_out)


def gambar_outro(im, t):
    u = e_out(prog(t, TOTAL - OUTRO, 0.5))
    if u <= 0:
        return
    lap = pil_tembus((W, H))
    d = ImageDraw.Draw(lap)
    kotak(d, (0, 0, W, H), 0, fill=BG + (int(238 * u),))
    tempel(lap, _cache['glow'], (W / 2 - 260, 420 - 260), 0.8)
    wm = logo('xyverse_logo', 440)
    s = e_back(prog(t, TOTAL - OUTRO + 0.1, 0.5))
    m = wm.resize((max(1, int(wm.width * s)), max(1, int(wm.height * s))))
    tempel(lap, m, (W / 2 - m.width / 2, 440 - m.height / 2 + (1 - u) * 40))
    f = font(F_BLACK, 40)
    d.text((W / 2 - lebar('WA Release Bot', f) / 2, 560 + (1 - u) * 40), 'WA Release Bot', font=f, fill=TEKS + (255,))
    f2 = font(F_SEMI, 22)
    for n, s in enumerate(('Kode + APK: komentar yang di-pin', 'Fitur apa lagi? Tulis di komen')):
        d.text((W / 2 - lebar(s, f2) / 2, 640 + n * 36), s, font=f2, fill=(HIJAU_T if n == 0 else TEKS2) + (255,))
    tempel(im, lap, (0, 0), u)


def gambar_bingkai(im, t):
    """Watermark atas (mark asli + nama), footer brand, progress bar."""
    d = ImageDraw.Draw(im)
    a = e_out(prog(t, INTRO - 0.1, 0.4))
    if a > 0:
        tempel(im, logo('xyverse_mark', 30), (28, 22), a)
        f = font(F_SEMI, 15)
        d.text((68, 28), 'WA Release Bot  ·  Eps 2', font=f, fill=TEKS2 + (int(255 * a),))
        d.text((W - 28 - lebar('@xykal', f), 28), '@xykal', font=f, fill=TEKS2 + (int(255 * a),))
    f = font(F_REG, 14)
    kaki = f'{NAMA_PAKET} · {BRAND}'
    d.text((W / 2 - lebar(kaki, f) / 2, 1246), kaki, font=f, fill=TEKS2)
    d.rectangle((0, H - 6, W, H), fill=GARIS)
    d.rectangle((0, H - 6, int(W * t / TOTAL), H), fill=HIJAU_T)


def frame(t):
    im = latar()
    tempel(im, _cache['glow'], (W / 2 - 260 + math.sin(t * 0.5) * 30, 380 + math.cos(t * 0.4) * 30), 0.55)
    tempel(im, _cache['glow2'], (-40 + math.sin(t * 0.3) * 20, 900), 0.6)
    ikon_melayang(im, t, e_out(prog(t, INTRO - 0.2, 0.6)))
    i, sc = scene_pada(t)
    gambar_hp(im, t)
    if t < TOTAL - OUTRO + 0.2:
        (t_j, judul, _), t_next = judul_pada(sc, t)
        t_akhir = min(t_next, TOTAL - OUTRO)
        ilus = ILUS.get(sc['layar'])
        judul_kinetik(im, judul, t_j, t_akhir, t, kiri=bool(ilus))
        if ilus:
            gambar_ilus(im, ilus, sc['t0'], min(sc['t1'], TOTAL - OUTRO), t)
    gambar_outro(im, t)
    gambar_stiker(im, sc, t)
    konfeti(im, sc, t)
    if t < TOTAL - OUTRO + 0.2:
        gambar_subtitle(im, sc, t)
    gambar_intro(im, t)
    gambar_bingkai(im, t)
    return efek_pasca(im.convert('RGB'), t, EFEK)


if __name__ == '__main__':
    from encode import main
    main(sys.argv[1:])
