"""Aset gambar/suara buat render.

Dua jenis:
- aset/logo/*.webp  : aset ASLI dari repo produk (logo XyVerse, ilustrasi clay, ikon melayang). Ikut di repo.
- aset/manifest.json: stiker meme + SFX myinstants pihak ketiga. TIDAK disimpan di repo (lisensinya bukan punya kita,
  lihat THIRD_PARTY_NOTICES.md) — diunduh saat render ke aset/cache/ lalu dicek sha256 supaya isinya nggak berubah diam-diam.

Pakai:  python3 render/aset.py --unduh     → isi aset/cache (dipanggil workflow, cache-nya di-restore actions/cache)
        python3 render/aset.py --cek       → laporan aset mana yang ada / hilang
"""
import hashlib
import json
import os
import shutil
import subprocess
import sys
import urllib.request
import wave
import numpy as np
from PIL import Image

AKAR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIR_LOGO = os.path.join(AKAR, 'aset', 'logo')
DIR_CACHE = os.path.join(AKAR, 'aset', 'cache')
MANIFEST = os.path.join(AKAR, 'aset', 'manifest.json')
SR = 24000
UA = 'Mozilla/5.0 (X11; Linux x86_64) wa-release-bot-konten/render'
_c = {}


def manifest():
    if 'm' not in _c:
        with open(MANIFEST) as f:
            _c['m'] = json.load(f)
    return _c['m']


def _sha(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for blok in iter(lambda: f.read(1 << 16), b''):
            h.update(blok)
    return h.hexdigest()


def _target(jenis, item):
    ext = 'mp3' if jenis == 'sfx' else 'webp'
    return os.path.join(DIR_CACHE, jenis, f"{item['nama']}.{ext}")


def unduh_semua():
    """Unduh semua item manifest yang belum ada / hash-nya beda. Balikin daftar yang gagal."""
    gagal = []
    for jenis in ('sfx', 'stiker'):
        for item in manifest()[jenis]:
            tujuan = _target(jenis, item)
            if os.path.exists(tujuan) and _sha(tujuan) == item['sha256']:
                continue
            os.makedirs(os.path.dirname(tujuan), exist_ok=True)
            try:
                req = urllib.request.Request(item['url'], headers={'User-Agent': UA})
                with urllib.request.urlopen(req, timeout=30) as r, open(tujuan + '.part', 'wb') as f:
                    shutil.copyfileobj(r, f)
                if _sha(tujuan + '.part') != item['sha256']:
                    os.remove(tujuan + '.part')
                    raise ValueError('sha256 beda dari manifest')
                os.replace(tujuan + '.part', tujuan)
                print(f'unduh ok  {jenis}/{item["nama"]}')
            except Exception as e:  # satu aset gagal jangan matiin render: scene-nya jalan tanpa aset itu
                gagal.append((jenis, item['nama'], str(e)[:80]))
                print(f'unduh GAGAL {jenis}/{item["nama"]}: {str(e)[:80]}')
    return gagal


def cek():
    hilang = [(j, i['nama']) for j in ('sfx', 'stiker') for i in manifest()[j] if not os.path.exists(_target(j, i))]
    ada = sum(len(manifest()[j]) for j in ('sfx', 'stiker')) - len(hilang)
    print(f'aset pihak ketiga: {ada} ada, {len(hilang)} hilang', *(f'\n  hilang: {j}/{n}' for j, n in hilang))
    return hilang


# ---------- gambar ----------
def logo(nama, lebar=None):
    """Aset asli (aset/logo/<nama>.webp) sebagai RGBA, opsional di-resize ke lebar tertentu (di-cache)."""
    k = ('logo', nama, lebar)
    if k not in _c:
        im = Image.open(os.path.join(DIR_LOGO, nama + '.webp')).convert('RGBA')
        if lebar:
            im = im.resize((int(lebar), max(1, int(im.height * lebar / im.width))), Image.LANCZOS)
        _c[k] = im
    return _c[k]


def stiker(nama, ukuran=190):
    """Stiker meme dari cache; None kalau belum diunduh (render lokal tanpa internet tetap jalan)."""
    k = ('stiker', nama, ukuran)
    if k not in _c:
        path = os.path.join(DIR_CACHE, 'stiker', nama + '.webp')
        if not os.path.exists(path):
            _c[k] = None
        else:
            im = Image.open(path).convert('RGBA')
            im.thumbnail((ukuran, ukuran), Image.LANCZOS)
            _c[k] = im
    return _c[k]


# ---------- suara ----------
def _baca_wav(path):
    w = wave.open(path)
    a = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
    if w.getnchannels() == 2:
        a = a.reshape(-1, 2).mean(axis=1)
    sr = w.getframerate()
    if sr != SR:
        a = np.interp(np.arange(0, len(a), sr / SR), np.arange(len(a)), a).astype(np.float32)
    return a


def sfx(nama):
    """SFX myinstants sebagai float32 mono 24 kHz, atau None kalau file/decoder nggak ada.
    Decode lewat ffmpeg (ada di runner); fallback soundfile kalau kebetulan terpasang lokal."""
    k = ('sfx', nama)
    if k in _c:
        return _c[k]
    mp3 = os.path.join(DIR_CACHE, 'sfx', nama + '.mp3')
    wav = mp3[:-4] + '.wav'
    hasil = None
    if os.path.exists(wav):
        hasil = _baca_wav(wav)
    elif os.path.exists(mp3):
        if shutil.which('ffmpeg'):
            r = subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', mp3, '-ac', '1', '-ar', str(SR), wav], capture_output=True)
            if r.returncode == 0:
                hasil = _baca_wav(wav)
        else:
            try:
                import soundfile
                a, sr = soundfile.read(mp3, dtype='float32')
                if a.ndim == 2:
                    a = a.mean(axis=1)
                hasil = np.interp(np.arange(0, len(a), sr / SR), np.arange(len(a)), a).astype(np.float32) if sr != SR else a
            except Exception:
                hasil = None
    _c[k] = hasil
    return hasil


if __name__ == '__main__':
    if sys.argv[1:] == ['--unduh']:
        g = unduh_semua()
        cek()
        sys.exit(1 if len(g) > 8 else 0)  # toleransi beberapa gagal (situs meme suka rewel), tapi jangan semua
    else:
        cek()
