"""Layar HP scene 05-09: lagu, caption, lapor + tidur, GitHub, CTA."""
import math
from gaya import (font, F_BLACK, F_SEMI, F_REG, BG, KARTU, GARIS, HIJAU, HIJAU_T, HIJAU_TUA, GELEMBUNG, TEKS, TEKS2,
                  MERAH, KUNING, PUTIH, kotak, e_back, ikon_centang, chip, lebar, bungkus)
from audio import kapan
from layar_a import SW, kanvas, bar_atas, gelembung_teks, gelembung, pop, kartu


def _voice_note(d, y, t, t_mulai, judul, artis, trend=False, muncul=1.0):
    """Gelembung voice note ala WA: tombol play, gelombang yang goyang, durasi, lalu caption."""
    if muncul <= 0:
        return y
    lb, tinggi = SW - 40, 170 if trend else 150
    x0 = 14
    if muncul < 1:
        s = e_back(muncul)
        cx, cy = x0 + lb / 2, y + tinggi / 2
        kotak(d, (cx - lb * s / 2, cy - tinggi * s / 2, cx + lb * s / 2, cy + tinggi * s / 2), 12, fill=KARTU)
        return y + tinggi + 8
    kotak(d, (x0, y, x0 + lb, y + tinggi), 12, fill=KARTU)
    d.ellipse((x0 + 14, y + 14, x0 + 58, y + 58), fill=HIJAU_T)
    d.polygon([(x0 + 31, y + 25), (x0 + 31, y + 47), (x0 + 49, y + 36)], fill=BG)
    maju = (t - t_mulai) / 60.0 % 1.0
    for i in range(34):
        x = x0 + 72 + i * 8
        h = 6 + 16 * abs(math.sin(i * 0.9 + t * 6)) * (0.5 + 0.5 * math.sin(i * 0.37))
        warna = HIJAU_T if i / 34 <= maju else GARIS
        d.rounded_rectangle((x, y + 36 - h / 2, x + 4, y + 36 + h / 2), radius=2, fill=warna)
    d.text((x0 + 72, y + 62), f'0:{int(maju * 60):02d} / 1:00', font=font(F_REG, 11), fill=TEKS2)
    d.text((x0 + 14, y + 92), judul, font=font(F_SEMI, 15), fill=TEKS)
    d.text((x0 + 14, y + 114), artis, font=font(F_REG, 13), fill=TEKS2)
    if trend:
        d.text((x0 + 14, y + 138), 'lagi rame diputer di Indonesia minggu ini', font=font(F_REG, 11), fill=HIJAU_T)
    return y + tinggi + 8


# ---------- 05 lagu ----------
def layar_lagu(sc, t, mode):
    im, d = kanvas()
    bar_atas(d, 'Channel Kamu', '2.104 pengikut')
    t_vn = kapan(sc, 'ngirim', 3.0)
    d.text((SW / 2 - 24, 102), 'Kemarin', font=font(F_REG, 11), fill=TEKS2)
    y = _voice_note(d, 120, t, sc['t0'] - 37, 'Kangen', 'Dewa 19', muncul=1.0)
    d.text((SW / 2 - 28, y + 2), 'Hari ini', font=font(F_REG, 11), fill=TEKS2)
    y = gelembung_teks(d, y + 20, 'Katanya udah move on. Terus kenapa lagu ini masih di-repeat?', lebar_maks=SW - 40, muncul=pop(t, t_vn - 0.3))
    y = _voice_note(d, y, t, t_vn, 'Risalah Hati', 'Dewa 19', trend=False, muncul=pop(t, t_vn))
    if mode >= 1:
        t_m = sc['tahap_t'][0][0]
        u = pop(t, t_m)
        if u > 0:
            s = e_back(u)
            kartu(d, (30, 580, SW - 30, 580 + 150 * s))
            if u >= 1:
                d.text((48, 596), '148', font=font(F_BLACK, 40), fill=HIJAU_T)
                d.text((150, 608), 'lagu lawas & 2000-an', font=font(F_SEMI, 15), fill=TEKS)
                d.text((150, 632), 'jiwang Malaysia, pop, indie', font=font(F_REG, 12), fill=TEKS2)
                v = pop(t, kapan(sc, 'trend', 10.0))
                if v > 0:
                    chip(d, 48, 672, '+ chart trend minggu ini', font(F_SEMI, 13), fill=HIJAU_TUA, warna=HIJAU_T)
    return im


# ---------- 06 caption: gaya-gaya ----------
GAYA_CONTOH = (('galau,', 'galau', 'Nggak semua yang lewat harus dilupain. Sebagian cukup diputer ulang.'),
               ('motivasi,', 'motivasi', 'Nggak apa-apa jalan pelan. Yang penting nggak balik ke orang yang sama.'),
               ('nyindir,', 'nyindir', 'Santai, aku nggak nunggu kamu berubah. Aku nunggu diriku berhenti berharap.'),
               ('ayat.', 'ayat', 'Maka, sesungguhnya beserta kesulitan ada kemudahan. — QS. Al-Insyirah: 5'))


def layar_caption(sc, t, mode):
    im, d = kanvas()
    bar_atas(d, 'Channel Kamu', 'caption dari AI, dicek gayanya')
    y = 104
    for kata, label, contoh in GAYA_CONTOH:
        u = pop(t, kapan(sc, kata, 3.0))
        if u <= 0:
            break
        f = font(F_REG, 13)
        baris = bungkus(contoh, f, SW - 150)
        y_atas = y
        y = gelembung(d, y, baris, f, masuk=True, lebar_maks=SW - 120, muncul=u)
        if u >= 1:
            lb = min(max([lebar(b, f) for b in baris] + [60]) + 28, SW - 120)
            chip(d, 14 + lb + 8, y_atas + 6, label, font(F_SEMI, 11), fill=HIJAU_TUA, warna=HIJAU_T)
    if mode >= 1:
        t_m = sc['tahap_t'][0][0]
        teks = 'Katanya udah move on. Terus kenapa lagu ini masih di-repeat?'
        n = min(len(teks), int(max(0, t - t_m - 0.2) / 0.045))
        if n > 0:
            f = font(F_SEMI, 15)
            baris = bungkus(teks[:n] + ('|' if n < len(teks) and int(t * 4) % 2 else ''), f, SW - 90)
            kotak(d, (14, 520, SW - 14, 520 + len(baris) * 22 + 46), 12, fill=GELEMBUNG)
            for i, b in enumerate(baris):
                d.text((28, 532 + i * 22), b, font=f, fill=TEKS)
            chip(d, 28, 520 + len(baris) * 22 + 16, 'sok bijak', font(F_SEMI, 11), fill=BG, warna=HIJAU_T)
    return im


# ---------- 07 lapor ke chat sendiri + tidur ----------
def layar_lapor(sc, t, mode):
    im, d = kanvas()
    if mode == 0:
        bar_atas(d, 'Kamu (Anda)', 'pesan ke diri sendiri')
        t_l = kapan(sc, 'lapor', 3.0)
        for i, (lbl, tm) in enumerate((('Percobaan 1: gagal (timeout)', t_l - 1.6), ('Percobaan 2: gagal (timeout)', t_l - 1.1), ('Percobaan 3: gagal (timeout)', t_l - 0.6))):
            u = pop(t, tm)
            if u > 0:
                kotak(d, (40, 110 + i * 34, SW - 40, 138 + i * 34), 8, fill=KARTU)
                d.text((54, 116 + i * 34), lbl, font=font(F_REG, 12), fill=MERAH)
        y = 230
        y = gelembung_teks(d, y, 'Bot gagal kirim rilis v1.7.0 ke Channel Kamu (3x). Error terakhir: Timed Out. '
                                 'Aku nggak bakal spam ulang. Kalau mau coba lagi, tekan "Cek sekarang".',
                           masuk=False, lebar_maks=SW - 50, muncul=pop(t, t_l), waktu='12.03')
        if pop(t, t_l + 0.4) >= 1:
            d.text((SW - 200, y + 4), 'cuma kamu yang lihat', font=font(F_REG, 11), fill=TEKS2)
    else:
        bar_atas(d, 'WA Release Bot', 'bot lagi tidur')
        t_m = sc['tahap_t'][0][0]
        u = pop(t, t_m, 0.5)
        cy = 330
        r = 70 * e_back(u)
        d.ellipse((SW / 2 - r, cy - r, SW / 2 + r, cy + r), fill=KUNING)
        d.ellipse((SW / 2 - r * 0.75 + r * 0.55, cy - r * 0.95, SW / 2 + r * 0.75 + r * 0.55, cy + r * 0.55), fill=(17, 27, 33))
        if u >= 1:
            for i in range(3):
                w = (t - t_m) * 1.2 - i * 0.5
                if w > 0:
                    f = font(F_BLACK, 18 + i * 8)
                    d.text((SW / 2 + 60 + i * 26, cy - 80 - (w % 1.5) * 40 - i * 20), 'z', font=f, fill=HIJAU_T)
            for i, (lbl, nilai) in enumerate((('CPU', 'nol, proses berhenti'), ('Baterai', 'aman, tanpa layanan latar 24 jam'), ('Kuota', 'satu request kecil per cek'))):
                v = pop(t, t_m + 0.6 + i * 0.3)
                if v > 0:
                    y = 470 + i * 78
                    kartu(d, (16, y, SW - 16, y + 66))
                    ikon_centang(d, 46, y + 33, 16)
                    d.text((76, y + 14), lbl, font=font(F_SEMI, 15), fill=TEKS)
                    d.text((76, y + 38), nilai, font=font(F_REG, 12), fill=TEKS2)
    return im


# ---------- 08 GitHub / open source ----------
def layar_github(sc, t, mode):
    im, d = kanvas()
    bar_atas(d, 'GitHub', 'xykal/wa-release-bot', warna=(36, 41, 47))
    kartu(d, (16, 110, SW - 16, 330))
    d.text((32, 128), 'xykal / wa-release-bot', font=font(F_SEMI, 17), fill=TEKS)
    d.text((32, 156), 'Bot WhatsApp: rilis GitHub → channel, penjaga', font=font(F_REG, 12), fill=TEKS2)
    d.text((32, 174), 'grup, lagu harian. Jalan dari Android.', font=font(F_REG, 12), fill=TEKS2)
    x = 32
    for lbl, tm in (('Gratis', kapan(sc, 'gratis,', 2.0)), ('Source-available', kapan(sc, 'open', 1.0)), ('Pasang sendiri', kapan(sc, 'pasang', 4.0))):
        if t >= tm:
            x += chip(d, x, 210, lbl, font(F_SEMI, 12), fill=HIJAU_TUA, warna=HIJAU_T) + 8
    d.text((32, 256), 'Kotlin · Node.js · Baileys · Cloudflare Workers', font=font(F_REG, 12), fill=TEKS2)
    d.text((32, 280), 'CI: build APK, CodeQL, audit dependensi', font=font(F_REG, 12), fill=TEKS2)
    if mode >= 1:
        u = pop(t, sc['tahap_t'][0][0])
        if u > 0:
            s = e_back(u)
            kotak(d, (SW / 2 - 170 * s, 380, SW / 2 + 170 * s, 380 + 190 * s), 14, fill=KARTU)
            if u >= 1:
                d.text((48, 396), 'Komentar yang di-pin', font=font(F_SEMI, 14), fill=TEKS2)
                d.text((48, 424), 'Link kode + APK', font=font(F_BLACK, 20), fill=HIJAU_T)
                d.text((48, 460), 'github.com/xykal/wa-release-bot', font=font(F_REG, 13), fill=TEKS)
                d.text((48, 484), 'Releases → app-arm64.apk', font=font(F_REG, 13), fill=TEKS)
                chip(d, 48, 520, 'Lihat komentar', font(F_SEMI, 13), fill=HIJAU, warna=PUTIH)
    return im


# ---------- 09 CTA ----------
def layar_cta(sc, t, mode):
    im, d = kanvas()
    bar_atas(d, 'Komentar', '1.204 komentar')
    komen = (('rizky_dev', 'bisa buat status WA juga nggak?'), ('nadia.p', 'mau versi iPhone dong'), ('kall (pembuat)', 'noted, masuk daftar'))
    y = 110
    for i, (nama, isi) in enumerate(komen):
        u = pop(t, sc['t_vo'] + 0.4 + i * 0.5)
        if u <= 0:
            break
        kartu(d, (16, y, SW - 16, y + 70))
        d.ellipse((30, y + 17, 66, y + 53), fill=HIJAU_TUA if 'kall' in nama else GARIS)
        d.text((80, y + 14), nama, font=font(F_SEMI, 13), fill=HIJAU_T if 'kall' in nama else TEKS2)
        d.text((80, y + 36), isi, font=font(F_REG, 14), fill=TEKS)
        y += 82
    t_k = kapan(sc, 'Tulis', 4.0)
    teks = 'Fitur apa lagi?'
    n = min(len(teks), int(max(0, t - t_k) / 0.08))
    kotak(d, (16, 560, SW - 16, 620), 30, fill=KARTU, outline=HIJAU_T if n else GARIS, lebar_garis=2)
    d.text((36, 578), (teks[:n] or 'Tambahkan komentar...') + ('|' if n and n < len(teks) and int(t * 4) % 2 else ''), font=font(F_REG, 15), fill=TEKS if n else TEKS2)
    if mode >= 1:
        t_f = sc['tahap_t'][0][0]
        u = pop(t, t_f, 0.4)
        if u > 0:
            denyut = 1 + 0.05 * math.sin((t - t_f) * 6)
            lb = 200 * e_back(u) * denyut
            kotak(d, (SW / 2 - lb / 2, 650, SW / 2 + lb / 2, 710), 30, fill=MERAH)
            if u >= 1:
                f = font(F_BLACK, 20)
                d.text((SW / 2 - lebar('Follow', f) / 2, 667), 'Follow', font=f, fill=PUTIH)
    return im


LAYAR_B = dict(lagu=layar_lagu, caption=layar_caption, lapor=layar_lapor, github=layar_github, cta=layar_cta)
