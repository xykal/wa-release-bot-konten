"""Efek visual: judul kinetik, ilustrasi asli, stiker meme, punch-in, guncang, kilat, konfeti, ikon melayang.

Semua efek dihitung dari waktu absolut `t` (stateless) supaya frame bisa digambar paralel di beberapa proses.
"""
import math
import random
from PIL import Image, ImageDraw
from gaya import (W, H, font, F_BLACK, BG, HIJAU, HIJAU_T, HIJAU_TUA, TEKS, KUNING, BIRU, MERAH, PUTIH,
                  e_out, e_back, prog, lebar, bungkus, pil_tembus, tempel, glow)
from aset import logo, stiker
from cue import STIKER_UKURAN

POS_STIKER = {'ka': (W - 212, 236), 'ki': (22, 236), 'kb': (W - 212, 880), 'kib': (22, 880), 'tengah': (W / 2 - 125, 520)}
# ikon clay dari app, ngambang di sisi kiri/kanan HP (x 0-135 dan 585-720 kosong)
MELAYANG = (('melayang_bintang', 44, 300, 70, 0.0), ('melayang_bulan', 612, 400, 66, 1.1), ('melayang_chat', 30, 610, 74, 2.3),
            ('melayang_kode', 616, 760, 70, 3.1), ('melayang_nada', 44, 950, 66, 4.2), ('melayang_perisai', 606, 1000, 72, 5.0))
_c = {}


def _potong_kata(teks):
    """'Grup ~akun aneh?~' → [('Grup', False), ('akun', True), ('aneh?', True)]"""
    hasil, sorot = [], False
    for kata in teks.split():
        awal = kata.startswith('~'); akhir = '~' in kata[1:]  # 'HP~,' juga nutup sorotan
        if awal:
            sorot = True
        hasil.append((kata.replace('~', ''), sorot))
        if akhir:
            sorot = False
    return hasil


def judul_kinetik(im, teks, t_masuk, t_keluar, t, kiri=False):
    """Judul: tiap kata nge-pop berurutan (overshoot), kata sorotan hijau + garis marker yang tumbuh."""
    u_out = 1 - prog(t, t_keluar - 0.18, 0.18)
    if u_out <= 0 or t < t_masuk:
        return
    kata = _potong_kata(teks)
    maks = 470 if kiri else W - 80
    for ukuran in (40, 34, 30):
        f = font(F_BLACK, ukuran)
        baris = bungkus(' '.join(k for k, _ in kata), f, maks)
        if len(baris) <= (2 if ukuran == 40 else 3):
            break
    lap = pil_tembus((W, 200))
    d = ImageDraw.Draw(lap)
    idx, y = 0, 14
    for b in baris:
        n_kata = len(b.split())
        potongan = kata[idx: idx + n_kata]
        total = lebar(b, f)
        x = 40 if kiri else W / 2 - total / 2
        for k, sorot in potongan:
            s = e_back(prog(t, t_masuk + 0.055 * idx, 0.32), 1.25)  # overshoot kecil biar antar kata nggak nabrak
            w_k = lebar(k, f)
            if s > 0.02:
                fk = font(F_BLACK, max(1, int(ukuran * s)))
                cx, cy = x + w_k / 2, y + ukuran / 2
                px, py = cx - lebar(k, fk) / 2, cy - fk.size / 2
                if sorot:
                    g = e_out(prog(t, t_masuk + 0.055 * idx + 0.18, 0.3))
                    d.rounded_rectangle((x - 4, y + ukuran + 2, x - 4 + (w_k + 8) * g, y + ukuran + 9), 3, fill=HIJAU + (255,))
                d.text((px + 3, py + 4), k, font=fk, fill=(0, 0, 0, 150))
                d.text((px, py), k, font=fk, fill=(HIJAU_T if sorot else TEKS) + (255,))
            x += w_k + lebar(' ', f)
            idx += 1
        y += ukuran + 14
    tempel(im, lap, (0, 62 - (1 - u_out) * 30), u_out)


def gambar_ilus(im, nama, t_masuk, t_keluar, t):
    """Ilustrasi clay asli dari app di pojok kanan atas: pop-in, ngambang pelan, muter dikit."""
    u = e_back(prog(t, t_masuk + 0.12, 0.5)) * (1 - prog(t, t_keluar - 0.2, 0.2))
    if u <= 0.02:
        return
    if 'glow_ilus' not in _c:
        _c['glow_ilus'] = glow(300, HIJAU_TUA, 60)
    ukuran = 150 if nama.startswith('ilus') else 118
    img = logo(nama, ukuran)
    s = max(1, int(img.width * u))
    img = img.resize((s, int(img.height * s / img.width) or 1)).rotate(math.sin(t * 1.3) * 4, resample=Image.BICUBIC, expand=True)
    cx, cy = W - 40 - 75, 74 + 75 + math.sin(t * 1.7) * 6
    tempel(im, _c['glow_ilus'], (cx - 150, cy - 150), 0.7 * u)
    tempel(im, img, (cx - img.width / 2, cy - img.height / 2))


def gambar_stiker(im, sc, t):
    """Stiker meme dari cue: pop-in overshoot + goyang meredam, keluar mengecil. Bayangan biar 'nempel' di atas layar."""
    for c in sc['cue']:
        if c[0] != 'stiker':
            continue
        t_c, nama, pos, dur = c[1:]
        if not (t_c <= t < t_c + dur):
            continue
        img = stiker(nama, STIKER_UKURAN[pos])
        if img is None:
            continue
        s = e_back(prog(t, t_c, 0.35)) * (1 - e_out(prog(t, t_c + dur - 0.25, 0.25)))
        if s <= 0.02:
            continue
        dt = t - t_c
        sudut = -12 * (1 - e_out(prog(t, t_c, 0.5))) + 5 * math.sin(dt * 9) * math.exp(-dt * 2.5)
        im2 = img.resize((max(1, int(img.width * s)), max(1, int(img.height * s))))
        im2 = im2.rotate(sudut, resample=Image.BICUBIC, expand=True)
        x, y = POS_STIKER[pos]
        uk = STIKER_UKURAN[pos]
        px, py = x + (uk - im2.width) / 2, y + (uk - im2.height) / 2 + math.sin(dt * 2.5) * 5
        bayang = Image.new('RGBA', im2.size, (0, 0, 0, 0))
        bayang.putalpha(im2.getchannel('A').point(lambda v: int(v * 0.45)))
        tempel(im, bayang, (px + 7, py + 9))
        tempel(im, im2, (px, py))


def konfeti(im, sc, t):
    for c in sc['cue']:
        if c[0] != 'konfeti' or not (c[1] <= t < c[1] + 1.6):
            continue
        dt = t - c[1]
        rng = random.Random(int(c[1] * 1000))
        d = ImageDraw.Draw(im)
        for _ in range(54):
            sudut = rng.uniform(-math.pi * 0.95, -math.pi * 0.05)
            v = rng.uniform(320, 760)
            x = c[2] + math.cos(sudut) * v * dt
            y = c[3] + math.sin(sudut) * v * dt + 0.5 * 1000 * dt * dt
            r = rng.uniform(5, 9); putar = rng.uniform(0, 6.28) + dt * rng.uniform(4, 12)
            warna = rng.choice((HIJAU_T, KUNING, BIRU, MERAH, PUTIH))
            a = int(255 * (1 - prog(dt, 1.1, 0.5)))
            pts = [(x + math.cos(putar + k * 1.57) * r * (1.6 if k % 2 else 0.8), y + math.sin(putar + k * 1.57) * r * (1.6 if k % 2 else 0.8)) for k in range(4)]
            d.polygon(pts, fill=warna + (a,))


def ikon_melayang(im, t, alpha=1.0, kecuali=None):
    for nama, x, y, uk, fase in MELAYANG:
        if nama == kecuali:  # ikon yang lagi jadi ilustrasi judul nggak usah dobel
            continue
        img = logo(nama, uk)
        tempel(im, img, (x, y + math.sin(t * 0.9 + fase) * 9), alpha)


def efek_pasca(im, t, efek):
    """Terapkan punch-in (zoom sesaat), guncang, kilat ke frame RGB — semuanya dari tabel EFEK di cue.py."""
    z, gx, gy, kilat = 1.0, 0.0, 0.0, None
    for th, punch, guncang, warna, alpha in efek:
        if not (th <= t < th + 0.45):
            continue
        dt = t - th
        z += punch * (1 - e_out(prog(dt, 0, 0.45)))
        if guncang:
            amp = guncang * (1 - prog(dt, 0, 0.3))
            gx += amp * math.sin(dt * 90); gy += amp * 0.6 * math.cos(dt * 70)
        if warna and dt < 0.15:
            kilat = (warna, alpha * (1 - dt / 0.15))
    if z > 1.001:
        cx, cy = W / 2, 500  # fokus agak atas biar judul nggak kepotong waktu zoom
        x0, y0 = cx * (1 - 1 / z), cy * (1 - 1 / z)
        im = im.crop((int(x0), int(y0), int(x0 + W / z), int(y0 + H / z))).resize((W, H), Image.BILINEAR)
    if abs(gx) + abs(gy) > 0.5:
        dasar = Image.new('RGB', (W, H), BG)
        dasar.paste(im, (int(gx), int(gy)))
        im = dasar
    if kilat:
        k = ('kilat', kilat[0])
        if k not in _c:
            _c[k] = Image.new('RGB', (W, H), kilat[0])
        im = Image.blend(im, _c[k], kilat[1])
    return im
