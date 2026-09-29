"""Layar HP scene teknis: 02b stack (apa yang ada di dalam APK) dan 02c cara kerja (siklus 15 menit).

Fakta dari repo produk: Kotlin (UI, foreground service, jadwal), Node.js 18.20.4 via nodejs-mobile,
Baileys 6.7.24 (WhatsApp Web protocol, kode pairing), cek rilis tiap 15 menit (default), cek grup tiap 5 menit,
lagu + caption dari Cloudflare Worker yang manggil Groq.
"""
import math
from gaya import (font, F_BLACK, F_SEMI, F_REG, BG, BG2, KARTU, GARIS, HIJAU, HIJAU_T, HIJAU_TUA, TEKS, TEKS2,
                  KUNING, PUTIH, kotak, bulat, e_back, prog, lebar, chip)
from audio import kapan
from layar_a import SW, kanvas, bar_atas, pop, kartu


def _blok(d, box, judul, ket, u, warna=KARTU, sorot=False):
    """Blok diagram yang nge-pop dari tengah; garis tepi hijau kalau disorot."""
    if u <= 0:
        return
    s = e_back(u)
    cx, cy = (box[0] + box[2]) / 2, (box[1] + box[3]) / 2
    w, h = (box[2] - box[0]) * s, (box[3] - box[1]) * s
    kotak(d, (cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2), 14, fill=warna, outline=HIJAU_T if sorot else None, lebar_garis=2)
    if u >= 1:
        d.text((box[0] + 18, box[1] + 12), judul, font=font(F_SEMI, 17), fill=TEKS)
        d.text((box[0] + 18, box[1] + 38), ket, font=font(F_REG, 12), fill=TEKS2)


def _panah(d, x, y0, y1, u):
    """Panah vertikal yang tumbuh dari y0 ke y1."""
    if u <= 0:
        return
    y = y0 + (y1 - y0) * u
    d.line([(x, y0), (x, y)], fill=HIJAU_T, width=3)
    if u >= 1:
        d.polygon([(x - 7, y1 - 9), (x + 7, y1 - 9), (x, y1)], fill=HIJAU_T)


def layar_stack(sc, t, mode):
    im, d = kanvas()
    bar_atas(d, 'WA Release Bot', 'apa yang ada di dalam APK-nya')
    t_apk, t_node, t_bai = kapan(sc, 'APK-nya', 2.5), kapan(sc, 'Node.js', 3.5), kapan(sc, 'Baileys', 6.0)
    t_wa, t_kt = kapan(sc, 'WhatsApp,', 7.5), kapan(sc, 'Kotlin', 9.0)
    u = pop(t, t_apk, 0.35)
    if u > 0:  # wadah APK
        s = e_back(u)
        kotak(d, (200 - 184 * s, 320 - 212 * s, 200 + 184 * s, 320 + 212 * s), 22, fill=BG, outline=HIJAU, lebar_garis=3)
        if u >= 1:
            chip(d, 28, 96, 'wa-release-bot.apk', font(F_SEMI, 12), fill=HIJAU, warna=PUTIH)
            d.text((SW - 168, 116), 'satu file, tanpa server', font=font(F_REG, 11), fill=TEKS2)
    _blok(d, (40, 138, SW - 40, 208), 'Kotlin', 'UI, foreground service, jadwal cek', pop(t, t_kt), sorot=t >= t_kt)
    _panah(d, 200, 208, 236, pop(t, t_kt + 0.25))
    _blok(d, (40, 238, SW - 40, 308), 'Node.js 18 beneran', 'nodejs-mobile: libnode.so ikut di APK', pop(t, t_node), sorot=t_node <= t < t_bai)
    _panah(d, 200, 308, 336, pop(t, t_node + 0.35))
    _blok(d, (40, 338, SW - 40, 408), 'Baileys 6.7', 'protokol WhatsApp Web, kode pairing', pop(t, t_bai), sorot=t_bai <= t < t_kt)
    if pop(t, t_node + 0.5) >= 1:
        chip(d, 40, 428, 'bukan Termux', font(F_SEMI, 11), fill=KARTU, warna=KUNING)
        chip(d, 150, 428, 'bukan VPS', font(F_SEMI, 11), fill=KARTU, warna=KUNING)
        chip(d, 242, 428, 'bukan laptop', font(F_SEMI, 11), fill=KARTU, warna=KUNING)
    u = pop(t, t_wa, 0.4)
    if u > 0:  # garis putus-putus jalan dari Baileys ke WhatsApp = koneksi hidup
        s = e_back(u)
        for i in range(12):
            y = 462 + (i * 14 + t * 40) % 166
            if y + 7 <= 630:
                d.line([(200, y), (200, y + 7)], fill=HIJAU_T, width=3)
        kotak(d, (200 - 90 * s, 660 - 26 * s, 200 + 90 * s, 660 + 26 * s), 26, fill=HIJAU)
        if u >= 1:
            f = font(F_SEMI, 16)
            d.text((200 - lebar('WhatsApp', f) / 2, 649), 'WhatsApp', font=f, fill=PUTIH)
            d.text((SW / 2 - lebar('nyambung kayak perangkat tertaut biasa', font(F_REG, 11)) / 2, 700),
                   'nyambung kayak perangkat tertaut biasa', font=font(F_REG, 11), fill=TEKS2)
    return im


SIMPUL = (('bangun:', 'Bangun', -90), ('GitHub,', 'Cek rilis GitHub', 0), ('gabung,', 'Cek grup', 90), ('harian,', 'Kirim lagu', 135), ('tidur', 'Tidur', 180))


def layar_kerja(sc, t, mode):
    im, d = kanvas()
    bar_atas(d, 'WA Release Bot', 'siklus tiap 15 menit')
    cx, cy, r = 200, 330, 118
    bulat(d, (cx - r - 5, cy - r - 5, cx + r + 5, cy + r + 5), GARIS)
    bulat(d, (cx - r + 5, cy - r + 5, cx + r - 5, cy + r - 5), BG2)
    t0 = kapan(sc, 'bangun:', 3.0)
    u_arc = prog(t, t0, 6.5)
    if u_arc > 0:  # busur hijau + titik yang muter = bot lagi jalan siklusnya
        d.arc((cx - r, cy - r, cx + r, cy + r), -90, -90 + 360 * u_arc, fill=HIJAU_T, width=10)
        a = math.radians(-90 + 360 * u_arc)
        bulat(d, (cx + r * math.cos(a) - 11, cy + r * math.sin(a) - 11, cx + r * math.cos(a) + 11, cy + r * math.sin(a) + 11), PUTIH)
    f = font(F_BLACK, 22)
    d.text((cx - lebar('15 menit', f) / 2, cy - 24), '15 menit', font=f, fill=TEKS)
    d.text((cx - lebar('sekali putaran', font(F_REG, 12)) / 2, cy + 6), 'sekali putaran', font=font(F_REG, 12), fill=TEKS2)
    for kata, label, sudut in SIMPUL:
        u = pop(t, kapan(sc, kata, 3.0))
        if u <= 0:
            continue
        a = math.radians(sudut)
        px, py = cx + (r + 34) * math.cos(a), cy + (r + 34) * math.sin(a)
        fl = font(F_SEMI, 13)
        w = lebar(label, fl) + 24
        s = e_back(u)
        px = min(max(px, w / 2 + 6), SW - w / 2 - 6)
        kotak(d, (px - w / 2 * s, py - 15 * s, px + w / 2 * s, py + 15 * s), 15, fill=HIJAU_TUA if kata != 'tidur' else KARTU)
        if u >= 1:
            d.text((px - w / 2 + 12, py - 8), label, font=fl, fill=TEKS)
    if mode >= 1:
        u = pop(t, sc['tahap_t'][0][0])
        if u > 0:
            kartu(d, (16, 520, SW - 16, 640), 'Lagu + caption')
            if u >= 1:
                d.text((32, 552), 'Cloudflare Worker  ->  Groq AI  ->  bot', font=font(F_SEMI, 14), fill=TEKS)
                d.text((32, 576), '148 lagu, 11 gaya caption, dicek batasnya per HP', font=font(F_REG, 12), fill=TEKS2)
                chip(d, 32, 600, 'galau', font(F_SEMI, 11), fill=BG, warna=HIJAU_T)
                chip(d, 96, 600, 'nyindir', font(F_SEMI, 11), fill=BG, warna=HIJAU_T)
                chip(d, 170, 600, 'ayat', font(F_SEMI, 11), fill=BG, warna=HIJAU_T)
                chip(d, 226, 600, 'motivasi', font(F_SEMI, 11), fill=BG, warna=HIJAU_T)
    d.text((32, 690), 'HP kamu nggak perlu nyala layarnya.', font=font(F_REG, 13), fill=TEKS2)
    d.text((32, 710), 'Selesai kerja, bot balik tidur: hemat baterai + kuota.', font=font(F_REG, 13), fill=TEKS2)
    return im


LAYAR_C = dict(stack=layar_stack, kerja=layar_kerja)
