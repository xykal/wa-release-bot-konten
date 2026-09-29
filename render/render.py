"""Render video TikTok Eps 2 — 720x1280 @ 60 fps, satu file MP4.

Pakai:  python3 render/render.py            → keluaran/tiktok-wa-release-bot-eps2.mp4
        python3 render/render.py --cek 2    → gambar 1 frame tiap 2 detik tanpa encode (uji cepat)
        python3 render/render.py --frame 47.5 cek.png
        python3 render/render.py --info     → cetak timeline

Frame digambar PIL lalu dipipa ke ffmpeg (rawvideo) per potongan, paralel
sejumlah core, lalu digabung + audio. Kenapa begini: tanpa file PNG perantara
(ribuan frame), memori kecil, dan 4 core runner Actions kepakai semua.
"""
import math
import os
import shutil
import subprocess
import sys
import tempfile
import time
from multiprocessing import Pool
from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gaya import (W, H, FPS, BRAND, NAMA_PAKET, font, F_BLACK, F_SEMI, F_REG, BG, BG2, KARTU, GARIS, HIJAU, HIJAU_T,
                  HIJAU_TUA, TEKS, TEKS2, clamp, e_out, e_back, prog, mix, bungkus, teks_sorot, lebar, kotak,
                  pil_tembus, tempel, glow, perisai, nada)
from audio import bangun_timeline, campur, kapan
from layar_a import LAYAR_A, SW, SH
from layar_b import LAYAR_B
from naskah import OUTRO

AKAR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LAYAR = {**LAYAR_A, **LAYAR_B}
SCENES, TOTAL = bangun_timeline()
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
        _cache['perisai'] = perisai(150)
        _cache['nada'] = nada(130)
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


def gambar_judul(im, teks, t_masuk, t_keluar, t):
    f = font(F_BLACK, 40)
    baris = bungkus(teks, f, W - 80)
    if len(baris) > 2:
        f = font(F_BLACK, 34)
        baris = bungkus(teks, f, W - 80)
    u_in = e_out(prog(t, t_masuk, 0.35))
    u_out = 1 - prog(t, t_keluar - 0.18, 0.18)
    alpha = min(u_in, u_out)
    if alpha <= 0:
        return
    lap = pil_tembus((W, 200))
    d = ImageDraw.Draw(lap)
    y = 20 + (1 - u_in) * 28
    for b in baris:
        # bayangan tipis biar kebaca di atas glow
        teks_sorot(d, W / 2 + 2, y + 2, b, f, warna=(0, 0, 0), sorot=(0, 0, 0))
        y += teks_sorot(d, W / 2, y, b, f)
    tempel(im, lap, (0, 60), alpha)


def gambar_hp(im, t):
    i, sc = scene_pada(t)
    u_masuk = e_back(prog(t, 0.1, 0.7))
    dy = (1 - u_masuk) * 900
    if t >= TOTAL - OUTRO:
        dy += e_out(prog(t, TOTAL - OUTRO, 0.4)) * 1100
    ox, oy = PX - 25, PY - 40 + dy
    d = ImageDraw.Draw(im)
    kotak(d, (ox - 4, oy - 4, ox + SW + 54, oy + SH + 84), 52, fill=(0, 0, 0, 110))
    kotak(d, (ox, oy, ox + SW + 50, oy + SH + 80), 48, fill=(24, 32, 38, 255), outline=GARIS + (255,), lebar_garis=3)
    layar = _layar_transisi(sc, i, t)
    mask = Image.new('L', (SW, SH), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, SW - 1, SH - 1), radius=28, fill=255)
    im.paste(layar, (PX, int(PY + dy)), mask)
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


def gambar_stiker(im, sc, t):
    goyang = math.sin(t * 2.2) * 6
    if sc['layar'] == 'grup':
        u = e_back(prog(t, kapan(sc, 'Ditolak.', 7.0), 0.4))
        if u > 0:
            s = _cache['perisai'].resize((max(1, int(150 * u)), max(1, int(150 * u))))
            tempel(im, s, (W - 150 - 30 + (150 - s.width) / 2, 250 + goyang + (150 - s.height) / 2))
    elif sc['layar'] == 'lagu':
        u = e_back(prog(t, kapan(sc, 'ngirim', 3.0), 0.4))
        if u > 0:
            s = _cache['nada'].resize((max(1, int(130 * u)), max(1, int(130 * u))))
            tempel(im, s, (36 + (130 - s.width) / 2, 240 - goyang + (130 - s.height) / 2))


def gambar_subtitle(im, sc, t):
    f = font(F_SEMI, 25)
    kata = sc['kata']
    if not kata:
        return
    baris, kini, idx = [], [], []
    for k, (w, a, b) in enumerate(kata):
        coba = ' '.join([x for x, _ in kini] + [w])
        if kini and lebar(coba, f) > W - 100:
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
    kotak(d, (28, 0, W - 28, 16 + len(tampil) * 36), 18, fill=(0, 0, 0, 150))
    for n, br in enumerate(tampil):
        y = 8 + n * 36
        teks = ' '.join(w for w, _ in br)
        x = W / 2 - lebar(teks, f) / 2
        for w, k in br:
            warna = HIJAU_T if k == sekarang else (TEKS if k < sekarang else TEKS2)
            d.text((x, y), w, font=f, fill=warna + (255,))
            x += lebar(w + ' ', f)
    tempel(im, lap, (0, 1128), alpha)


def gambar_outro(im, t):
    u = e_out(prog(t, TOTAL - OUTRO, 0.5))
    if u <= 0:
        return
    lap = pil_tembus((W, H))
    d = ImageDraw.Draw(lap)
    kotak(d, (0, 0, W, H), 0, fill=BG + (int(235 * u),))
    ik = _cache['perisai']
    lap.alpha_composite(ik, (int(W / 2 - ik.width / 2), int(360 + (1 - u) * 40)))
    f = font(F_BLACK, 44)
    d.text((W / 2 - lebar('WA Release Bot', f) / 2, 540 + (1 - u) * 40), 'WA Release Bot', font=f, fill=TEKS + (255,))
    f2 = font(F_SEMI, 22)
    for n, s in enumerate(('Kode + APK: komentar yang di-pin', 'Fitur apa lagi? Tulis di komen')):
        d.text((W / 2 - lebar(s, f2) / 2, 620 + n * 36), s, font=f2, fill=(HIJAU_T if n == 0 else TEKS2) + (255,))
    tempel(im, lap, (0, 0), u)


def frame(t):
    im = latar()
    g = _cache['glow']
    tempel(im, g, (W / 2 - 260 + math.sin(t * 0.5) * 30, 380 + math.cos(t * 0.4) * 30), 0.55)
    tempel(im, _cache['glow2'], (-40 + math.sin(t * 0.3) * 20, 900), 0.6)
    i, sc = scene_pada(t)
    gambar_hp(im, t)
    if t < TOTAL - OUTRO + 0.2:
        (t_j, judul, _), t_next = judul_pada(sc, t)
        gambar_judul(im, judul, t_j, min(t_next, TOTAL - OUTRO), t)
        gambar_stiker(im, sc, t)
        gambar_subtitle(im, sc, t)
    gambar_outro(im, t)
    d = ImageDraw.Draw(im)
    f = font(F_REG, 14)
    kaki = f'{NAMA_PAKET} · {BRAND}'
    d.text((W / 2 - lebar(kaki, f) / 2, 1246), kaki, font=f, fill=TEKS2)
    d.rectangle((0, H - 6, W, H), fill=GARIS)
    d.rectangle((0, H - 6, int(W * t / TOTAL), H), fill=HIJAU_T)
    return im.convert('RGB')


# ---------- encode ----------
def ffmpeg():
    return shutil.which('ffmpeg') or 'ffmpeg'


def render_bagian(arg):
    a, b, out = arg
    cmd = [ffmpeg(), '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS),
           '-i', '-', '-an', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '19', '-pix_fmt', 'yuv420p', '-g', '120', out]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for n in range(a, b):
        p.stdin.write(frame(n / FPS).tobytes())
    p.stdin.close()
    if p.wait() != 0:
        raise RuntimeError(f'ffmpeg gagal di bagian {a}-{b}')
    return out


def render_penuh(keluar):
    os.makedirs(os.path.dirname(keluar), exist_ok=True)
    tmp = tempfile.mkdtemp(prefix='render-')
    n_frame = int(TOTAL * FPS)
    n_proses = max(1, min(os.cpu_count() or 1, 8))
    batas = [round(n_frame * k / n_proses) for k in range(n_proses + 1)]
    tugas = [(batas[k], batas[k + 1], os.path.join(tmp, f'bag{k:02d}.mp4')) for k in range(n_proses)]
    mulai = time.time()
    latar()
    with Pool(n_proses) as pool:
        bagian = pool.map(render_bagian, tugas)
    print(f'video {n_frame} frame selesai {time.time() - mulai:.0f} dtk, {n_proses} proses')
    daftar = os.path.join(tmp, 'daftar.txt')
    with open(daftar, 'w') as f:
        f.writelines(f"file '{b}'\n" for b in bagian)
    video = os.path.join(tmp, 'video.mp4')
    subprocess.run([ffmpeg(), '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', daftar, '-c', 'copy', video], check=True)
    audio = os.path.join(tmp, 'audio.wav')
    campur(SCENES, TOTAL, audio)
    subprocess.run([ffmpeg(), '-v', 'error', '-y', '-i', video, '-i', audio, '-c:v', 'copy', '-c:a', 'aac', '-b:a', '160k',
                    '-ar', '48000', '-movflags', '+faststart', '-shortest', keluar], check=True)
    shutil.rmtree(tmp, ignore_errors=True)
    print(f'selesai: {keluar} ({os.path.getsize(keluar) / 1e6:.1f} MB, {TOTAL:.1f} dtk)')


def info():
    print(f'total {TOTAL:.2f} dtk, {int(TOTAL * FPS)} frame @ {FPS} fps, {W}x{H}')
    for sc in SCENES:
        print(f"  {sc['vo']} {sc['t0']:6.2f}-{sc['t1']:6.2f}  vo {sc['dur_vo']:5.2f}  {sc['layar']:8s} cue {len(sc['cue'])}")


if __name__ == '__main__':
    arg = sys.argv[1:]
    if arg[:1] == ['--info']:
        info()
    elif arg[:1] == ['--frame']:
        frame(float(arg[1])).save(arg[2] if len(arg) > 2 else 'frame.png')
    elif arg[:1] == ['--cek']:
        langkah = float(arg[1]) if len(arg) > 1 else 2.0
        mulai, n, t = time.time(), 0, 0.0
        while t < TOTAL:
            frame(t); n += 1; t += langkah
        print(f'cek {n} frame ok, rata-rata {(time.time() - mulai) / n * 1000:.0f} ms/frame')
    else:
        render_penuh(os.path.join(AKAR, 'keluaran', 'tiktok-wa-release-bot-eps2.mp4'))
