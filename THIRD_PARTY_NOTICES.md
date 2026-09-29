# Third-party notices / Catatan pihak ketiga

| Aset | Sumber | Lisensi | Catatan |
|---|---|---|---|
| `fonts/font_*archivo*.ttf` | Archivo — The Archivo Project Authors (Omnibus-Type) | SIL Open Font License 1.1 (`fonts/OFL-Archivo.txt`) | Self-hosted, tidak diubah. |
| `vo/*.wav` | Suara narator dibuat dengan text-to-speech AI dari naskah `render/naskah.py` | Dibuat untuk proyek ini | Video wajib diberi label "Konten yang dibuat AI" saat upload. |
| SFX (pop, klik, ding, buzz, whoosh, sparkle, zzz) | Disintesis dari numpy di `render/audio.py` | Bagian dari repo ini | Tidak ada file audio pihak ketiga. |
| Musik latar | Pad sintetis di `render/audio.py` (`musik()`) | Bagian dari repo ini | Bukan lagu berhak cipta. |
| Ikon perisai, not musik, ilustrasi layar HP | Digambar dengan Pillow di `render/gaya.py`, `render/layar_*.py` | Bagian dari repo ini | Tidak memakai stiker/pack pihak ketiga. |

Tidak ada dependensi runtime dari CDN. Dependensi build: Pillow dan numpy (dipatok versinya di workflow).
