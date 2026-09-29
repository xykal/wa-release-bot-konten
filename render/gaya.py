"""Palet, font, easing, dan helper gambar yang dipakai semua modul render.

Kenapa dipisah: render.py / layar_*.py cuma mikirin komposisi; semua konstanta
visual ada di satu tempat supaya ganti warna atau font nggak nyebar ke mana-mana.
"""
import os
from PIL import Image, ImageChops, ImageDraw, ImageFont, ImageFilter

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


# ---------- bentuk (anti-alias) ----------
# ImageDraw nggak punya anti-alias buat bentuk. Caranya: mask digambar 3x lalu diperkecil (reduce), lalu
# warna ditempel lewat mask itu ke gambar di balik `draw` (atribut _image, Pillow dipatok 12.3.0 di workflow).
_mask = {}


def _mask_bulat(w, h, r, elips=False):
    k = (w, h, r, elips)
    if k not in _mask:
        if len(_mask) > 4000:
            _mask.clear()
        S = 3
        big = Image.new('L', (w * S, h * S), 0)
        dd = ImageDraw.Draw(big)
        if elips:
            dd.ellipse((0, 0, w * S - 1, h * S - 1), fill=255)
        else:
            dd.rounded_rectangle((0, 0, w * S - 1, h * S - 1), radius=r * S, fill=255)
        _mask[k] = big.reduce(S)
    return _mask[k]


def _rgba(c):
    return tuple(c) if len(c) == 4 else tuple(c) + (255,)


def _isi(im, x0, y0, w, h, warna, mask):
    warna = _rgba(warna)
    lap = Image.new('RGBA', (w, h), warna)
    lap.putalpha(mask if warna[3] == 255 else mask.point(lambda v: v * warna[3] // 255))
    im.alpha_composite(lap, (x0, y0))


def kotak(draw, box, r, fill=None, outline=None, lebar_garis=1):
    """Kotak sudut bulat anti-alias (fallback ke rounded_rectangle biasa kalau gambar bukan RGBA)."""
    im = getattr(draw, '_image', None)
    x0, y0 = int(round(box[0])), int(round(box[1]))
    w, h = int(round(box[2])) - x0, int(round(box[3])) - y0
    if im is None or im.mode != 'RGBA' or w < 2 or h < 2 or x0 < 0 or y0 < 0:
        draw.rounded_rectangle(box, radius=r, fill=fill, outline=outline, width=lebar_garis)
        return
    r = int(min(r, w // 2, h // 2))
    if fill:
        _isi(im, x0, y0, w, h, fill, _mask_bulat(w, h, r))
    if outline:
        g = int(lebar_garis)
        cincin = _mask_bulat(w, h, r).copy()
        if w > 2 * g and h > 2 * g:  # cincin = mask luar dikurangi mask dalam → garis tepi doang, tengah tetap tembus
            dalam = Image.new('L', (w, h), 0)
            dalam.paste(_mask_bulat(w - 2 * g, h - 2 * g, max(0, r - g)), (g, g))
            cincin = ImageChops.subtract(cincin, dalam)
        _isi(im, x0, y0, w, h, outline, cincin)


def bulat(draw, box, fill):
    """Lingkaran/elips anti-alias."""
    im = getattr(draw, '_image', None)
    x0, y0 = int(round(box[0])), int(round(box[1]))
    w, h = int(round(box[2])) - x0, int(round(box[3])) - y0
    if im is None or im.mode != 'RGBA' or w < 2 or h < 2 or x0 < 0 or y0 < 0:
        draw.ellipse(box, fill=fill)
        return
    _isi(im, x0, y0, w, h, fill, _mask_bulat(w, h, 0, elips=True))


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


_ikon = {}


def _sprite_ikon(jenis, r, warna, tebal):
    k = (jenis, r, warna, tebal)
    if k not in _ikon:
        S, m = 3, 2
        uk = (2 * r + 2 * m) * S
        big = pil_tembus((uk, uk))
        dd = ImageDraw.Draw(big)
        c = uk / 2
        dd.ellipse((m * S, m * S, uk - m * S, uk - m * S), fill=warna + (255,))
        rr, tb = r * S, tebal * S
        if jenis == 'centang':
            dd.line([(c - rr * .45, c), (c - rr * .1, c + rr * .38), (c + rr * .5, c - rr * .35)], fill=BG + (255,), width=tb, joint='curve')
        else:
            q = rr * .42
            dd.line([(c - q, c - q), (c + q, c + q)], fill=BG + (255,), width=tb)
            dd.line([(c - q, c + q), (c + q, c - q)], fill=BG + (255,), width=tb)
        _ikon[k] = big.reduce(S)
    return _ikon[k]


def _tempel_ikon(draw, jenis, cx, cy, r, warna, tebal):
    im = getattr(draw, '_image', None)
    sp = _sprite_ikon(jenis, int(r), warna, int(tebal))
    if im is None or im.mode != 'RGBA':
        draw.ellipse((cx - r, cy - r, cx + r, cy + r), fill=warna)
        return
    x, y = int(cx - sp.width / 2), int(cy - sp.height / 2)
    if x >= 0 and y >= 0:
        im.alpha_composite(sp, (x, y))
    else:
        im.paste(sp, (x, y), sp)


def ikon_centang(draw, cx, cy, r, warna=HIJAU_T, tebal=6):
    _tempel_ikon(draw, 'centang', cx, cy, r, warna, tebal)


def ikon_silang(draw, cx, cy, r, warna=MERAH, tebal=6):
    _tempel_ikon(draw, 'silang', cx, cy, r, warna, tebal)
