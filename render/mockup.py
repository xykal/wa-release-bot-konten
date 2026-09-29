"""Mockup HP statis buat landing page (web/ di repo produk).

Pakai layar yang sama dengan video (layar_*.py) pada detik terakhir tiap scene,
dipasang ke bingkai HP tipis yang sama, disimpan WebP transparan:

  EPS2_POTONGAN=penuh python3 render/mockup.py [dir_keluar]   -> keluaran/mockup/<layar>.webp

Kenapa dari renderer, bukan screenshot: tampilannya sudah konsisten dengan
video, tidak ada data pribadi (nomor, nama grup asli), dan bisa dirender ulang
kapan saja tanpa HP. Di web diberi label "ilustrasi".
"""
import os
import sys

from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import render  # noqa: E402  (memuat SCENES + cache bingkai)
from gaya import bulat  # noqa: E402

# layar -> nama file; urutan = urutan tampil di web
PILIH = ['beranda', 'rilis', 'grup', 'lagu', 'kerja', 'stack', 'caption', 'lapor']


def mockup(nama):
    sc = next(s for s in render.SCENES if s['layar'] == nama)
    t = sc['t1'] - 0.01
    mode = render.judul_pada(sc, t)[0][2]
    layar = render.LAYAR[nama](sc, t, mode)
    hp = render._cache['hp'].copy()
    x, y = render.TEPI + render.PAD, render.ATAS + render.PAD
    hp.paste(layar, (x, y), render._cache['mask'])
    d = ImageDraw.Draw(hp)
    cx = x + render.SW / 2
    bulat(d, (cx - 7, y + 9, cx + 7, y + 23), (4, 6, 8))  # kamera punch-hole, sama dengan video
    return hp


def main(arg):
    keluar = arg[0] if arg else os.path.join(render.AKAR, 'keluaran', 'mockup')
    os.makedirs(keluar, exist_ok=True)
    render.frame(0.0)  # isi _cache (bingkai, mask)
    for nama in PILIH:
        im = mockup(nama)
        path = os.path.join(keluar, f'{nama}.webp')
        im.save(path, 'WEBP', quality=84, method=6)
        print(f'{path} {im.size[0]}x{im.size[1]} {os.path.getsize(path) // 1024} KB')


if __name__ == '__main__':
    main(sys.argv[1:])
