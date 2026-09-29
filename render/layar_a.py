"""Layar HP scene 00-04 + helper tampilan ala WhatsApp yang dipakai layar_b.py juga.

Semua digambar ulang tiap frame di kanvas SW x SH (isi layar HP), lalu render.py
menempelkannya ke mockup HP. Waktu `t` selalu absolut (detik dari awal video).
"""
from PIL import Image, ImageDraw
from gaya import (font, F_BLACK, F_SEMI, F_REG, BG, BG2, KARTU, GARIS, HIJAU, HIJAU_T, HIJAU_TUA, GELEMBUNG,
                  TEKS, TEKS2, MERAH, KUNING, PUTIH, kotak, bungkus, prog, e_out, e_back, ikon_centang,
                  ikon_silang, chip, lebar)
from audio import kapan

SW, SH = 400, 760
_wallpaper = {}


def kanvas():
    # Wallpaper titik-titik ala WA (dibikin sekali) supaya layar kosong nggak kelihatan mati.
    if 'w' not in _wallpaper:
        im = Image.new('RGBA', (SW, SH), BG2 + (255,))
        d = ImageDraw.Draw(im)
        for y in range(100, SH, 26):
            for x in range(8 + (y // 26 % 2) * 13, SW, 26):
                d.ellipse((x, y, x + 3, y + 3), fill=(24, 36, 43, 255))
        _wallpaper['w'] = im
    im = _wallpaper['w'].copy()
    return im, ImageDraw.Draw(im)


def bar_atas(d, judul, sub='', warna=HIJAU_TUA):
    d.rectangle((0, 0, SW, 30), fill=BG)
    d.text((18, 7), '12.00', font=font(F_SEMI, 14), fill=TEKS)
    d.rectangle((0, 30, SW, 92), fill=warna)
    d.ellipse((16, 42, 54, 80), fill=KARTU)
    d.text((66, 40 if sub else 50), judul, font=font(F_SEMI, 18), fill=PUTIH)
    if sub:
        d.text((66, 64), sub, font=font(F_REG, 13), fill=(200, 230, 220))


def gelembung(d, y, baris, f, masuk=True, lebar_maks=300, waktu='12.00', warna=None, muncul=1.0):
    """Gelembung chat; `baris` sudah dipecah. Balikin y bawah. `muncul` 0..1 = animasi pop."""
    if muncul <= 0:
        return y
    tinggi = len(baris) * (f.size + 5) + 26
    lb = max([lebar(b, f) for b in baris] + [60]) + 28
    lb = min(lb, lebar_maks)
    x0 = 14 if masuk else SW - 14 - lb
    if muncul < 1:
        s = e_back(muncul)
        cx, cy = x0 + lb / 2, y + tinggi / 2
        lb2, t2 = lb * s, tinggi * s
        kotak(d, (cx - lb2 / 2, cy - t2 / 2, cx + lb2 / 2, cy + t2 / 2), 12, fill=warna or (KARTU if masuk else GELEMBUNG))
        return y + tinggi + 8
    kotak(d, (x0, y, x0 + lb, y + tinggi), 12, fill=warna or (KARTU if masuk else GELEMBUNG))
    yy = y + 10
    for b in baris:
        d.text((x0 + 14, yy), b, font=f, fill=TEKS)
        yy += f.size + 5
    d.text((x0 + lb - 44, y + tinggi - 18), waktu, font=font(F_REG, 10), fill=TEKS2)
    return y + tinggi + 8


def gelembung_teks(d, y, teks, masuk=True, ukuran=14, muncul=1.0, lebar_maks=300, warna=None, waktu='12.00'):
    f = font(F_REG, ukuran)
    return gelembung(d, y, bungkus(teks, f, lebar_maks - 30), f, masuk, lebar_maks, waktu, warna, muncul)


def pop(t, t_mulai, dur=0.28):
    return prog(t, t_mulai, dur)


def kartu(d, box, judul=None):
    kotak(d, box, 14, fill=KARTU)
    if judul:
        d.text((box[0] + 16, box[1] + 12), judul, font=font(F_SEMI, 14), fill=TEKS2)


# ---------- 00 masalah: grup spam → channel sepi → rilis nganggur ----------
def layar_masalah(sc, t, mode):
    im, d = kanvas()
    if mode == 0:
        bar_atas(d, 'Grup Alumni 2019', '128 anggota, 3 baru bergabung')
        y = 104
        y = gelembung_teks(d, y, '+62 812-3xxx-xxxx bergabung lewat tautan', ukuran=12, warna=BG, muncul=pop(t, sc['t_vo'] + 0.3))
        y = gelembung_teks(d, y, 'Kak, ada info kerja gaji 15jt, minat? Klik link di bio', muncul=pop(t, sc['t_vo'] + 0.5))
        y = gelembung_teks(d, y, '+62 857-9xxx-xxxx bergabung lewat tautan', ukuran=12, warna=BG, muncul=pop(t, sc['t_vo'] + 0.9))
        y = gelembung_teks(d, y, 'PROMO!!! gabung grup sebelah, hadiah tiap hari', muncul=pop(t, sc['t_vo'] + 1.1))
        y = gelembung_teks(d, y, 'Halo semuanya... siapa ini yang masukin?', masuk=False, muncul=pop(t, sc['t_vo'] + 1.7))
        if pop(t, sc['t_vo'] + 2.2) >= 1:
            ikon_silang(d, SW - 50, y + 40, 26)
            d.text((60, y + 30), 'admin lagi tidur, spam masuk terus', font=font(F_REG, 13), fill=MERAH)
    elif mode == 1:
        bar_atas(d, 'Channel Kamu', '2.104 pengikut')
        kartu(d, (30, 300, SW - 30, 430))
        d.text((SW / 2 - lebar('Belum ada update', font(F_SEMI, 18)) / 2, 330), 'Belum ada update', font=font(F_SEMI, 18), fill=TEKS)
        d.text((SW / 2 - lebar('terakhir posting 3 minggu lalu', font(F_REG, 13)) / 2, 366), 'terakhir posting 3 minggu lalu', font=font(F_REG, 13), fill=TEKS2)
        k = int((t * 2) % 4)
        d.text((SW / 2 - 30, 400), 'sepi' + '.' * k, font=font(F_REG, 13), fill=TEKS2)
    elif mode == 2:
        bar_atas(d, 'GitHub', 'xykal/wa-release-bot', warna=(36, 41, 47))
        kartu(d, (16, 110, SW - 16, 250))
        d.text((32, 126), 'Release', font=font(F_REG, 13), fill=TEKS2)
        d.text((32, 148), 'v2.0.0', font=font(F_BLACK, 26), fill=TEKS)
        chip(d, 32, 196, 'Latest', font(F_SEMI, 12), fill=HIJAU_TUA, warna=HIJAU_T)
        chip(d, 110, 196, 'published 2 hari lalu', font(F_SEMI, 12))
        kartu(d, (16, 270, SW - 16, 350))
        d.text((32, 292), 'Diumumin ke channel?', font=font(F_SEMI, 15), fill=TEKS)
        d.text((32, 316), 'belum. kelupaan lagi.', font=font(F_REG, 14), fill=MERAH)
    else:
        bar_atas(d, 'WA Release Bot', 'satu bot, tiga kerjaan')
        for i, (nama, ket) in enumerate((('Jaga grup', 'tolak akun yang pernah keluar'), ('Isi channel', 'lagu + caption tiap hari'), ('Umumin rilis', 'GitHub → channel, otomatis'))):
            u = pop(t, sc['tahap_t'][2][0] + 0.15 * i)
            if u <= 0:
                continue
            y = 120 + i * 120
            kartu(d, (16, y, SW - 16, y + 100))
            ikon_centang(d, 50, y + 50, 20)
            d.text((84, y + 26), nama, font=font(F_SEMI, 17), fill=TEKS)
            d.text((84, y + 54), ket, font=font(F_REG, 13), fill=TEKS2)
    return im


# ---------- 01 beranda app ----------
def layar_beranda(sc, t, mode):
    im, d = kanvas()
    bar_atas(d, 'WA Release Bot', 'tersambung · bot lagi tidur')
    kartu(d, (16, 108, SW - 16, 212))
    ikon_centang(d, 50, 160, 22)
    d.text((84, 132), 'Tersambung', font=font(F_SEMI, 17), fill=TEKS)
    d.text((84, 160), 'perangkat tertaut: HP ini', font=font(F_REG, 13), fill=TEKS2)
    d.text((84, 180), 'cek berikutnya 14 menit lagi', font=font(F_REG, 13), fill=TEKS2)
    kartu(d, (16, 228, SW - 16, 372), 'Repo yang dipantau')
    d.text((32, 262), 'xykal/wa-release-bot', font=font(F_SEMI, 16), fill=TEKS)
    d.text((32, 288), 'target: Channel Kamu', font=font(F_REG, 13), fill=TEKS2)
    d.text((32, 308), 'rilis terakhir: v1.7.0', font=font(F_REG, 13), fill=TEKS2)
    chip(d, 32, 334, 'Cek sekarang', font(F_SEMI, 13), fill=HIJAU, warna=PUTIH)
    if mode >= 1:
        t_m = sc['tahap_t'][0][0]
        for i, (teks, tm) in enumerate((('server', t_m), ('laptop', kapan(sc, 'laptop,', 8.0)), ('Termux', kapan(sc, 'Termux.', 9.0)))):
            u = pop(t, tm)
            if u <= 0:
                continue
            y = 400 + i * 74
            s = e_back(u)
            lb = 300 * s
            kotak(d, (SW / 2 - lb / 2, y, SW / 2 + lb / 2, y + 58), 14, fill=KARTU)
            if u >= 1:
                ikon_silang(d, 56, y + 29, 18)
                d.text((88, y + 17), 'nggak perlu ' + teks, font=font(F_SEMI, 17), fill=TEKS)
    d.text((32, 700), 'Node.js jalan di dalam APK-nya', font=font(F_REG, 13), fill=TEKS2)
    d.text((32, 720), 'bukan Termux, bukan VPS', font=font(F_REG, 13), fill=TEKS2)
    return im


# ---------- 02 pairing ----------
def layar_pairing(sc, t, mode):
    im, d = kanvas()
    bar_atas(d, 'Tautkan perangkat', 'WA Release Bot')
    kartu(d, (16, 110, SW - 16, 300), 'Nomor WhatsApp kamu')
    d.text((32, 146), '+62 812 •••• ••••', font=font(F_SEMI, 20), fill=TEKS)
    chip(d, 32, 190, 'Minta kode pairing', font(F_SEMI, 13), fill=HIJAU, warna=PUTIH)
    awal = kapan(sc, 'masukin', 2.0) + 0.45
    kode = 'XYKL-7A2B'
    n = min(len(kode), int(max(0, t - awal) / 0.13) + (1 if t >= awal else 0))
    if n:
        d.text((32, 236), kode[:n] + ('|' if int(t * 3) % 2 and n < len(kode) else ''), font=font(F_BLACK, 26), fill=HIJAU_T)
    kartu(d, (16, 320, SW - 16, 520), 'Di HP kamu: WhatsApp')
    for i, langkah in enumerate(('Perangkat tertaut', 'Tautkan perangkat', 'Tautkan dengan nomor telepon', 'Masukkan kode')):
        y = 354 + i * 38
        aktif = t >= awal - 1.6 + i * 0.4
        d.ellipse((34, y + 4, 50, y + 20), fill=HIJAU_T if aktif else GARIS)
        d.text((62, y), langkah, font=font(F_REG, 14), fill=TEKS if aktif else TEKS2)
    if mode >= 1:
        u = pop(t, sc['tahap_t'][0][0], 0.4)
        s = e_back(u)
        cy = 620
        r = 44 * s
        d.ellipse((SW / 2 - r, cy - r, SW / 2 + r, cy + r), fill=HIJAU_T)
        if u >= 1:
            ikon_centang(d, SW / 2, cy, 44)
            f = font(F_SEMI, 18)
            d.text((SW / 2 - lebar('Tersambung', f) / 2, 680), 'Tersambung', font=f, fill=TEKS)
            d.text((SW / 2 - lebar('bot siap kerja', font(F_REG, 13)) / 2, 706), 'bot siap kerja', font=font(F_REG, 13), fill=TEKS2)
    return im


# ---------- 03 rilis GitHub → post channel ----------
POST_RILIS = ['wa-release-bot v1.7.0 udah rilis!', 'Baru aja mendarat dari GitHub, masih anget.', '',
              'Apa yang baru:', '- Lapor otomatis kalau kirim gagal 3x', '- Caption lagu: 5 gaya baru', '- 148 lagu di daftar', '',
              'File:', '- app-arm64.apk (26,0 MB)', '- engine-bundle.zip (1,1 MB)', '', 'github.com/xykal/wa-release-bot']


def layar_rilis(sc, t, mode):
    im, d = kanvas()
    t_kirim = kapan(sc, 'posting', 3.0)
    if t < t_kirim + 0.35:
        bar_atas(d, 'GitHub', 'xykal/wa-release-bot', warna=(36, 41, 47))
        u = prog(t, t_kirim, 0.35)
        dy = -e_out(u) * 700
        kartu(d, (16, 120 + dy, SW - 16, 300 + dy))
        d.text((32, 136 + dy), 'Release · baru saja', font=font(F_REG, 13), fill=TEKS2)
        d.text((32, 160 + dy), 'v1.7.0', font=font(F_BLACK, 30), fill=TEKS)
        chip(d, 32, 214 + dy, 'Latest', font(F_SEMI, 12), fill=HIJAU_TUA, warna=HIJAU_T)
        chip(d, 110, 214 + dy, '2 assets', font(F_SEMI, 12))
        d.text((32, 258 + dy), 'bot kebangun, ambil catatan rilis...', font=font(F_REG, 13), fill=HIJAU_T)
    else:
        bar_atas(d, 'Channel Kamu', '2.104 pengikut')
        u = pop(t, t_kirim + 0.35, 0.35)
        f = font(F_REG, 13)
        y = gelembung(d, 108, POST_RILIS, f, masuk=True, lebar_maks=SW - 40, muncul=u)
        if u >= 1:
            # sorot bagian yang lagi diomongin narator
            sorot = {'Rapi': (4, 7), 'file': (9, 11), 'ukurannya.': (10, 11)}
            for kata, (a, b) in sorot.items():
                if t >= kapan(sc, kata, 99):
                    y0 = 108 + 10 + a * (f.size + 5)
                    y1 = 108 + 10 + b * (f.size + 5) + 2
                    d.rounded_rectangle((22, y0 - 2, SW - 30, y1), radius=6, outline=HIJAU_T, width=2)
            d.text((24, y + 6), 'Terkirim · dilihat 1.980', font=font(F_REG, 12), fill=TEKS2)
    return im


# ---------- 04 penjaga grup ----------
def layar_grup(sc, t, mode):
    im, d = kanvas()
    bar_atas(d, 'Grup Alumni 2019', 'permintaan bergabung')
    t_cek = kapan(sc, 'Permintaan', 2.0)
    t_tolak = kapan(sc, 'Ditolak.', 7.0)
    orang = (('+62 812-3xxx-xxxx', 'pernah keluar 12 Mei', False), ('Dina Prasetyo', 'diundang anggota', True),
             ('+62 857-9xxx-xxxx', 'pernah di-kick', False), ('Rafi', 'lewat tautan', True))
    for i, (nama, ket, ok) in enumerate(orang):
        y = 110 + i * 96
        u = pop(t, t_cek + i * 0.25)
        if u <= 0:
            continue
        kartu(d, (16, y, SW - 16, y + 84))
        d.ellipse((30, y + 20, 74, y + 64), fill=GARIS)
        d.text((88, y + 20), nama, font=font(F_SEMI, 15), fill=TEKS)
        d.text((88, y + 44), ket, font=font(F_REG, 13), fill=TEKS2)
        if t >= t_cek + 1.2 + i * 0.25 and t < t_tolak + i * 0.18:
            k = int((t * 3) % 3) + 1
            d.text((SW - 110, y + 32), 'ngecek' + '.' * k, font=font(F_REG, 12), fill=KUNING)
        elif t >= t_tolak + i * 0.18:
            if ok:
                ikon_centang(d, SW - 60, y + 42, 18)
            else:
                ikon_silang(d, SW - 60, y + 42, 18)
                d.text((SW - 170, y + 34), 'DITOLAK', font=font(F_BLACK, 13), fill=MERAH)
    if mode >= 2:
        u = pop(t, sc['tahap_t'][1][0])
        if u > 0:
            kotak(d, (30, 560, SW - 30, 640), 14, fill=HIJAU_TUA)
            d.text((48, 576), 'Grup aman.', font=font(F_SEMI, 17), fill=PUTIH)
            d.text((48, 602), 'dicek tiap beberapa menit, tanpa kamu buka HP', font=font(F_REG, 12), fill=(200, 230, 220))
    return im


LAYAR_A = dict(masalah=layar_masalah, beranda=layar_beranda, pairing=layar_pairing, rilis=layar_rilis, grup=layar_grup)
