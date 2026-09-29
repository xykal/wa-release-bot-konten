"""Palet, font, easing, dan helper gambar yang dipakai semua modul render.

Kenapa dipisah: render.py / layar_*.py cuma mikirin komposisi; semua konstanta
visual ada di satu tempat supaya ganti warna atau font nggak nyebar ke mana-mana.
"""
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

AKAR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W, H, FPS = 720, 1280, 60
BRAND = 'XyVerse Technology Global'
NAMA_PAKET = 'wa-release-bot'

_FONT = os.path.join(AKAR, 'fonts')
F_BLACK = os.path.join(_FONT, 'font_logo_judul_hero__archivo-expanded-black.ttf')
F_SEMI = os.path.join(_FONT, 'font_subjudul_tombol__archivo-semibold.ttf')
F_REG = os.path.join(_FONT, 'font_body_footer__archivo-regular.ttf')

# Palet gelap ala WhatsApp (sama dengan tema app-nya, biar nyambung sama screenshot asli).
BG = (11, 20, 26); BG2 = (17, 27, 33); KARTU = (32, 44, 51); GARIS = (42, 57, 66)
HIJAU = (0, 168, 132); HIJAU_T = (37, 211, 102); HIJAU_TUA = (0, 92, 75); GELEMBUNG = (0, 92, 75)
TEKS = (233, 237, 239); TEKS2 = (134, 150, 160); MERAH = (241, 92, 109); KUNING = (255, 196, 0)
BIRU = (83, 189, 235); PUTIH = (255, 255, 255)

_fc = {}


def font(path, size):
    k = (path, int(size))
    if k not in _fc:
        _fc[k] = ImageFont.truetype(path, int(size))
    return _fc[k]


# ---------- easing ----------
def clamp(x, a=0.0, b=1.0):
    return a if x < a else b if x > b else x


def e_out(x):
    x = clamp(x)
    return 1 - (1 - x) ** 3


def e_io(x):
    x = clamp(x)
    return 4 * x ** 3 if x < .5 else 1 - (-2 * x + 2) ** 3 / 2


def e_back(x, s=1.7):
    x = clamp(x) - 1
    return x * x * ((s + 1) * x + s) + 1


def prog(t, a, dur):
    return clamp((t - a) / dur) if dur > 0 else 1.0


def mix(c1, c2, u):
    return tuple(int(c1[i] + (c2[i] - c1[i]) * u) for i in range(3))


# ---------- teks ----------
def lebar(teks, f):
    return f.getlength(teks)


def bungkus(teks, f, maks):
    """Pecah kalimat jadi baris-baris yang muat di `maks` px."""
    baris, kini = [], ''
    for kata in teks.split():
        coba = (kini + ' ' + kata).strip()
        if lebar(coba, f) <= maks or not kini:
            kini = coba
        else:
            baris.append(kini)
            kini = kata
    if kini:
        baris.append(kini)
    return baris


def teks_sorot(draw, x, y, teks, f, warna=TEKS, sorot=HIJAU_T, tengah=True):
    """Tulis satu baris; kata di antara *bintang* diwarnai `sorot`. Balikin tinggi baris."""
    potongan, tebal, buf = [], False, ''
    for ch in teks:
        if ch == '*':
            if buf:
                potongan.append((buf, tebal))
            buf, tebal = '', not tebal
        else:
            buf += ch
    if buf:
        potongan.append((buf, tebal))
    total = sum(lebar(p, f) for p, _ in potongan)
    cx = x - total / 2 if tengah else x
    for p, tb in potongan:
        draw.text((cx, y), p, font=f, fill=sorot if tb else warna)
        cx += lebar(p, f)
    return f.size + 6


def bayangan_teks(draw, xy, teks, f, fill, bayang=(0, 0, 0), jarak=3):
    draw.text((xy[0] + jarak, xy[1] + jarak), teks, font=f, fill=bayang)
    draw.text(xy, teks, font=f, fill=fill)


# ---------- bentuk ----------
def kotak(draw, box, r, fill=None, outline=None, lebar_garis=1):
    draw.rounded_rectangle(box, radius=r, fill=fill, outline=outline, width=lebar_garis)


def pil_tembus(ukuran):
    return Image.new('RGBA', ukuran, (0, 0, 0, 0))


def tempel(im, lapisan, pos=(0, 0), alpha=1.0):
    """Tempel lapisan RGBA ke `im` dengan opacity. Dipakai buat fade-in/out apa pun."""
    if alpha <= 0:
        return
    if alpha < 1:
        a = lapisan.getchannel('A').point(lambda v: int(v * alpha))
        lapisan = lapisan.copy()
        lapisan.putalpha(a)
    im.alpha_composite(lapisan, dest=(int(pos[0]), int(pos[1])))


def glow(ukuran, warna, radius=60):
    """Bulatan cahaya lembut; dibikin sekali lalu di-cache pemanggil (blur itu mahal)."""
    im = pil_tembus((ukuran, ukuran))
    d = ImageDraw.Draw(im)
    d.ellipse((radius, radius, ukuran - radius, ukuran - radius), fill=warna + (255,))
    return im.filter(ImageFilter.GaussianBlur(radius))


def stempel(im, pos, teks, warna, sudut=-12, skala=1.0, alpha=1.0):
    """Cap miring ala 'DITOLAK' / 'TERKIRIM': kotak garis tebal + teks, muncul dengan efek jatuh."""
    f = font(F_BLACK, 30 * skala)
    lb = lebar(teks, f) + 40
    lap = pil_tembus((int(lb) + 20, int(f.size) + 44))
    d = ImageDraw.Draw(lap)
    kotak(d, (10, 10, lb + 10, f.size + 34), 8, outline=warna + (255,), lebar_garis=5)
    d.text((30, 20), teks, font=f, fill=warna + (255,))
    lap = lap.rotate(sudut, resample=Image.BICUBIC, expand=True)
    tempel(im, lap, (pos[0] - lap.width / 2, pos[1] - lap.height / 2), alpha)


def chip(draw, x, y, teks, f, fill=KARTU, warna=TEKS, pad=14):
    lb = lebar(teks, f) + pad * 2
    kotak(draw, (x, y, x + lb, y + f.size + pad), (f.size + pad) // 2, fill=fill)
    draw.text((x + pad, y + pad / 2 - 1), teks, font=f, fill=warna)
    return lb


def ikon_centang(draw, cx, cy, r, warna=HIJAU_T, tebal=6):
    draw.ellipse((cx - r, cy - r, cx + r, cy + r), fill=warna)
    draw.line([(cx - r * .45, cy), (cx - r * .1, cy + r * .38), (cx + r * .5, cy - r * .35)], fill=BG, width=tebal, joint='curve')


def ikon_silang(draw, cx, cy, r, warna=MERAH, tebal=6):
    draw.ellipse((cx - r, cy - r, cx + r, cy + r), fill=warna)
    k = r * .42
    draw.line([(cx - k, cy - k), (cx + k, cy + k)], fill=BG, width=tebal)
    draw.line([(cx - k, cy + k), (cx + k, cy - k)], fill=BG, width=tebal)
