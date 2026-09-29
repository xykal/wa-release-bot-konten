"""Encode: frame dari render.frame() dipipa ke ffmpeg (rawvideo) per potongan, paralel sejumlah core,
lalu digabung + audio. Kenapa begini: tanpa file PNG perantara (ribuan frame), memori kecil,
dan 4 core runner Actions kepakai semua. CLI-nya dipanggil lewat render/render.py.
"""
import os
import shutil
import subprocess
import tempfile
import time
from multiprocessing import Pool

import render
from audio import campur
from gaya import W, H, FPS


def ffmpeg():
    return shutil.which('ffmpeg') or 'ffmpeg'


def render_bagian(arg):
    a, b, out = arg
    cmd = [ffmpeg(), '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS),
           '-i', '-', '-an', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '19', '-pix_fmt', 'yuv420p', '-g', '120', out]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for n in range(a, b):
        p.stdin.write(render.frame(n / FPS).tobytes())
    p.stdin.close()
    if p.wait() != 0:
        raise RuntimeError(f'ffmpeg gagal di bagian {a}-{b}')
    return out


def render_penuh(keluar):
    os.makedirs(os.path.dirname(keluar), exist_ok=True)
    tmp = tempfile.mkdtemp(prefix='render-')
    n_frame = int(render.TOTAL * FPS)
    n_proses = max(1, min(os.cpu_count() or 1, 8))
    batas = [round(n_frame * k / n_proses) for k in range(n_proses + 1)]
    tugas = [(batas[k], batas[k + 1], os.path.join(tmp, f'bag{k:02d}.mp4')) for k in range(n_proses)]
    mulai = time.time()
    render.latar()
    with Pool(n_proses) as pool:
        bagian = pool.map(render_bagian, tugas)
    print(f'video {n_frame} frame selesai {time.time() - mulai:.0f} dtk, {n_proses} proses')
    daftar = os.path.join(tmp, 'daftar.txt')
    with open(daftar, 'w') as f:
        f.writelines(f"file '{b}'\n" for b in bagian)
    video = os.path.join(tmp, 'video.mp4')
    subprocess.run([ffmpeg(), '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', daftar, '-c', 'copy', video], check=True)
    audio = os.path.join(tmp, 'audio.wav')
    campur(render.SCENES, render.TOTAL, audio)
    subprocess.run([ffmpeg(), '-v', 'error', '-y', '-i', video, '-i', audio, '-c:v', 'copy', '-c:a', 'aac', '-b:a', '160k',
                    '-ar', '48000', '-movflags', '+faststart', '-shortest', keluar], check=True)
    shutil.rmtree(tmp, ignore_errors=True)
    print(f'selesai: {keluar} ({os.path.getsize(keluar) / 1e6:.1f} MB, {render.TOTAL:.1f} dtk)')


def info():
    print(f'total {render.TOTAL:.2f} dtk, {int(render.TOTAL * FPS)} frame @ {FPS} fps, {W}x{H}')
    for sc in render.SCENES:
        n_s = sum(1 for c in sc['cue'] if c[0] == 'stiker'); n_f = sum(1 for c in sc['cue'] if c[0] == 'sfx')
        print(f"  {sc['vo']} {sc['t0']:6.2f}-{sc['t1']:6.2f}  vo {sc['dur_vo']:5.2f}  {sc['layar']:8s} sfx {n_f:2d} stiker {n_s}")


def main(arg):
    if arg[:1] == ['--info']:
        info()
    elif arg[:1] == ['--frame']:
        render.frame(float(arg[1])).save(arg[2] if len(arg) > 2 else 'frame.png')
    elif arg[:1] == ['--cek']:
        langkah = float(arg[1]) if len(arg) > 1 else 2.0
        mulai, n, t = time.time(), 0, 0.0
        while t < render.TOTAL:
            render.frame(t); n += 1; t += langkah
        print(f'cek {n} frame ok, rata-rata {(time.time() - mulai) / n * 1000:.0f} ms/frame')
    else:
        render_penuh(os.path.join(render.AKAR, 'keluaran', 'tiktok-wa-release-bot-eps2.mp4'))
