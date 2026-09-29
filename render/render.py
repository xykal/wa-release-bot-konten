"""Komposisi frame video TikTok Eps 2 — 720x1280 @ 60 fps.

Pakai:  python3 render/render.py            → keluaran/tiktok-wa-release-bot-eps2.mp4 (butuh ffmpeg, lihat encode.py)
        python3 render/render.py --cek 2    → gambar 1 frame tiap 2 detik tanpa encode (uji cepat)
        python3 render/render.py --frame 47.5 cek.png
        python3 render/render.py --info     → cetak timeline

Urutan lapisan tiap frame: latar + glow + ikon clay melayang → HP (bingkai tipis anti-alias, layar scene, light
sweep) → judul kinetik + ilustrasi asli → outro → stiker meme → konfeti → subtitle karaoke → sting logo (scene 01)
→ watermark/footer/progress → efek pasca (punch-in, guncang, kilat). Semua fungsi murni dari `t` supaya bisa paralel.
"""
import math
import os
import sys
from PIL import Image, ImageChops, ImageDraw, ImageFilter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gaya import (W, H, FPS, BRAND, NAMA_PAKET, font, F_BLACK, F_SEMI, F_REG, BG, BG2, GARIS, HIJAU_T, HIJAU_TUA,
                  TEKS, TEKS2, e_out, e_io, e_back, prog, mix, lebar, kotak, bulat, pil_tembus, tempel, glow)
from aset import logo
from audio import bangun_timeline
from cue import efek_dari_cue, kapan
from fx import judul_kinetik, gambar_ilus, gambar_stiker, konfeti, ikon_melayang, efek_pasca
from layar_a import LAYAR_A, SW, SH
from layar_b import LAYAR_B
from naskah import INTRO, OUTRO, ILUS

AKAR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LAYAR = {**LAYAR_A, **LAYAR_B}
SCENES, TOTAL = bangun_timeline()
EFEK = [e for sc in SCENES for e in efek_dari_cue(sc['cue'])]
PX, PY = (W - SW) // 2, 262  # posisi isi layar HP
TEPI, ATAS, PAD = 10, 14, 70  # bezel tipis kiri/kanan, atas/bawah; PAD = ruang bayangan di lapisan bingkai
T_STING = kapan(SCENES[1], 'Kenalin,', 0.3)  # logo XyVerse nongol pas "Kenalin"
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
        S = 4
        mask = Image.new('L', (SW * S, SH * S), 0)
        ImageDraw.Draw(mask).rounded_rectangle((0, 0, SW * S - 1, SH * S - 1), radius=34 * S, fill=255)
        _cache['mask'] = mask.reduce(S)
        band = pil_tembus((64, SH + 240))
        bd = ImageDraw.Draw(band)
        for x in range(64):
            bd.line([(x, 0), (x, SH + 240)], fill=(255, 255, 255, int(85 * math.sin(math.pi * x / 64) ** 2)))
        _cache['sweep'] = band.rotate(16, resample=Image.BICUBIC, expand=True)
        _cache['hp'] = _bingkai_hp()
    return _cache['latar'].copy()


def _bingkai_hp():
    """Bingkai HP tipis: digambar 4x lalu diperkecil (anti-alias), rim terang tipis, tombol samping, bayangan lembut."""
    S = 4
    w, h = SW + 2 * TEPI, SH + 2 * ATAS
    big = pil_tembus(((w + 2 * PAD) * S, (h + 2 * PAD) * S))
    d = ImageDraw.Draw(big)
    p = PAD * S
    d.rounded_rectangle((p - 3 * S, (PAD + 130) * S, p, (PAD + 172) * S), radius=2 * S, fill=(74, 82, 90, 255))  # volume
    d.rounded_rectangle((p - 3 * S, (PAD + 184) * S, p, (PAD + 226) * S), radius=2 * S, fill=(74, 82, 90, 255))
    d.rounded_rectangle((p + w * S, (PAD + 150) * S, p + (w + 3) * S, (PAD + 212) * S), radius=2 * S, fill=(74, 82, 90, 255))  # power
    d.rounded_rectangle((p, p, p + w * S, p + h * S), radius=44 * S, fill=(70, 78, 86, 255))  # rim
    d.rounded_rectangle((p + 2 * S, p + 2 * S, p + (w - 2) * S, p + (h - 2) * S), radius=42 * S, fill=(12, 16, 20, 255))  # bezel
    kecil = big.reduce(S)
    bayang = pil_tembus(kecil.size)
    ImageDraw.Draw(bayang).rounded_rectangle((PAD + 6, PAD + 26, PAD + w + 6, PAD + h + 26), radius=44, fill=(0, 0, 0, 170))
    bayang = bayang.filter(ImageFilter.GaussianBlur(26))
    bayang.alpha_composite(kecil)
    return bayang


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
    u_masuk = e_back(prog(t, INTRO + 0.05, 0.75), 1.2)
    dy = (1 - u_masuk) * 900
    if t >= TOTAL - OUTRO:
        dy += e_out(prog(t, TOTAL - OUTRO, 0.4)) * 1100
    im.alpha_composite(_cache['hp'], (PX - TEPI - PAD, int(PY - ATAS - PAD + dy)))
    layar = _layar_transisi(sc, i, t)
    u = prog(t, sc['t0'] + 0.15, 0.45)
    if 0 < u < 1:  # light sweep: garis kilau tipis miring lewat di kaca HP tiap ganti scene
        layar = layar.copy()
        tempel(layar, _cache['sweep'], (-300 + u * (SW + 380), -120))
    im.paste(layar, (PX, int(PY + dy)), _cache['mask'])
    d = ImageDraw.Draw(im)
    bulat(d, (W / 2 - 7, PY + dy + 9, W / 2 + 7, PY + dy + 23), (4, 6, 8))  # kamera punch-hole


def _layar_transisi(sc, i, t):
    """Ganti scene 0.4 dtk: layar lama geser kiri + pudar, layar baru masuk dari kanan sambil membesar 0.94→1."""
    _, _, mode = judul_pada(sc, t)[0]
    baru = LAYAR[sc['layar']](sc, t, mode)
    u = prog(t, sc['t0'], 0.4)
    if i == 0 or u >= 1:
        return baru
    e = e_io(u)
    lama_sc = SCENES[i - 1]
    lama = LAYAR[lama_sc['layar']](lama_sc, lama_sc['t1'] - 0.01, judul_pada(lama_sc, lama_sc['t1'] - 0.01)[0][2])
    out = Image.new('RGBA', (SW, SH), BG2 + (255,))
    tempel(out, lama, (-e * SW * 0.35, 0), 1 - e)
    s = 0.94 + 0.06 * e
    b = baru.resize((int(SW * s), int(SH * s)))
    tempel(out, b, ((1 - e) * SW * 0.6 + (SW - b.width) / 2, (SH - b.height) / 2), min(1.0, e * 1.4))
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


def gambar_sting(im, t):
    """Logo XyVerse asli nge-pop di atas HP pas "Kenalin", kilau lewat, lalu terbang mengecil ke pojok jadi watermark."""
    if not (T_STING <= t < T_STING + 2.1):
        return
    dt = t - T_STING
    u_in = e_back(prog(dt, 0, 0.5), 1.4)
    u_go = e_io(prog(dt, 1.6, 0.5))
    lap = pil_tembus((W, H))
    kotak(ImageDraw.Draw(lap), (0, 0, W, H), 0, fill=(0, 0, 0, int(140 * u_in * (1 - u_go))))
    tempel(lap, _cache['glow'], (W / 2 - 260, 640 - 260), 0.9 * u_in * (1 - u_go))
    wm = logo('xyverse_logo', 460).copy()
    u_k = prog(dt, 0.55, 0.5)
    if 0 < u_k < 1:
        kilau = pil_tembus(wm.size)
        x = -120 + u_k * (wm.width + 240)
        ImageDraw.Draw(kilau).polygon([(x, 0), (x + 90, 0), (x + 40, wm.height), (x - 50, wm.height)], fill=(255, 255, 255, 170))
        kilau.putalpha(ImageChops.multiply(kilau.getchannel('A'), wm.getchannel('A')))
        wm.alpha_composite(kilau)
    lebar_akhir = 110
    lb = max(2, int((460 * u_in) * (1 - u_go) + lebar_akhir * u_go))
    m = wm.resize((lb, max(1, int(wm.height * lb / wm.width))))
    cx = W / 2 * (1 - u_go) + (28 + lebar_akhir / 2) * u_go
    cy = 640 * (1 - u_go) + (24 + m.height / 2) * u_go
    tempel(lap, m, (cx - m.width / 2, cy - m.height / 2))
    tempel(im, lap, (0, 0))


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
    """Watermark (lockup XyVerse kecil, muncul setelah sting), footer brand, progress bar."""
    d = ImageDraw.Draw(im)
    if t >= T_STING + 2.1:
        tempel(im, logo('xyverse_logo', 110), (28, 24))
        f = font(F_SEMI, 15)
        d.text((W - 28 - lebar('@xykal', f), 28), '@xykal', font=f, fill=TEKS2 + (255,))
    f = font(F_REG, 14)
    kaki = f'{NAMA_PAKET} · {BRAND}'
    d.text((W / 2 - lebar(kaki, f) / 2, 1246), kaki, font=f, fill=TEKS2)
    d.rectangle((0, H - 6, W, H), fill=GARIS)
    d.rectangle((0, H - 6, int(W * t / TOTAL), H), fill=HIJAU_T)


def frame(t):
    im = latar()
    tempel(im, _cache['glow'], (W / 2 - 260 + math.sin(t * 0.5) * 30, 380 + math.cos(t * 0.4) * 30), 0.55)
    tempel(im, _cache['glow2'], (-40 + math.sin(t * 0.3) * 20, 900), 0.6)
    ikon_melayang(im, t, e_out(prog(t, INTRO + 0.3, 0.6)))
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
    gambar_sting(im, t)
    gambar_bingkai(im, t)
    return efek_pasca(im.convert('RGB'), t, EFEK)


if __name__ == '__main__':
    from encode import main
    main(sys.argv[1:])
