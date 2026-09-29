# Third-party notices / Catatan pihak ketiga

## Ikut di repo ini

| Aset | Sumber | Lisensi | Catatan |
|---|---|---|---|
| `fonts/font_*archivo*.ttf` | Archivo — The Archivo Project Authors (Omnibus-Type) | SIL Open Font License 1.1 (`fonts/OFL-Archivo.txt`) | Self-hosted, tidak diubah. |
| `vo/*.wav` | Suara narator dibuat dengan text-to-speech AI dari naskah `render/naskah.py` | Dibuat untuk proyek ini | Video wajib diberi label "Konten yang dibuat AI" saat upload. |
| `aset/logo/*.webp` | Logo XyVerse, ilustrasi clay, ikon melayang — disalin dari repo produk `xykal/wa-release-bot` (`app/src/main/res/drawable-nodpi/`) | Milik xykal — XyVerse Technology Global | Aset asli app-nya, dipakai apa adanya. |
| SFX sintetis (pop, klik, ding, buzz, whoosh, sparkle, zzz), musik latar | numpy di `render/audio.py` | Bagian dari repo ini | — |
| Tampilan layar HP | Digambar dengan Pillow di `render/layar_*.py` | Bagian dari repo ini | Mockup, bukan screenshot. |

## TIDAK ikut di repo — diunduh saat render (`aset/manifest.json`, `render/aset.py --unduh`)

| Aset | Sumber | Status hak cipta | Catatan |
|---|---|---|---|
| 27 SFX meme (vine boom, anjay, emotional damage, sad violin, dll.) | myinstants.com (`/media/sounds/<nama>.mp3`) | Tidak jelas / bukan milik kami; myinstants adalah agregat unggahan pengguna | Hanya dipakai di video, bukan didistribusikan ulang lewat repo. sha256 dipatok supaya isi tidak berubah diam-diam. |
| 19 stiker pack "Meme receh indo" (publisher: luissela) | getstickerpack.com/stickers/meme-receh-indo (CDN `s3.getstickerpack.com`) | Halaman pack menyatakan "These stickers are property of Luissela"; gambar di dalamnya meme dari berbagai sumber | Sama: hanya dipakai di video. |

Keputusan memakai SFX/stiker meme di video ada di penerbit video (xykal); repo ini sengaja tidak menyimpan
salinannya. Kalau ada klaim, cukup hapus entri di `aset/manifest.json` dan cue-nya di `render/cue.py`, lalu render ulang.

Tidak ada dependensi runtime dari CDN. Dependensi build: Pillow dan numpy (dipatok versinya di workflow).
