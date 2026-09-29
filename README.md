# wa-release-bot-konten

Render pipeline for the TikTok episodes of [WA Release Bot](https://github.com/xykal/wa-release-bot).
Kept separate from the product repo on purpose: media, voice-over and marketing scripts do not
belong in the APK repo (see the product repo's `docs/KONTEN-TIKTOK.md`).

Pipeline render video TikTok untuk [WA Release Bot](https://github.com/xykal/wa-release-bot).
Sengaja dipisah dari repo produk: media, VO, dan naskah promosi tidak ikut repo APK.

## How it works / Cara kerja

- `render/naskah.py` — the script: titles, phone screen per scene, VO text.
- `vo/NN.wav` — AI voice-over, one file per scene. Word timing for the karaoke subtitle is
  estimated from the audio energy (`render/audio.py`), so the text in `naskah.py` must match
  the audio word for word.
- `render/cue.py` — per-scene cues (meme SFX, WhatsApp meme stickers, confetti) locked to spoken words;
  `render/fx.py` — kinetic titles, punch-in zoom, shake, flash, floating clay icons from the app.
- `render/aset.py` + `aset/manifest.json` — third-party stickers/SFX are NOT committed: downloaded at
  render time and verified by sha256 (`python3 render/aset.py --unduh`). `aset/logo/` = original app assets.
- `render/render.py` — draws every frame with Pillow (720x1280, 60 fps), pipes them to ffmpeg
  in parallel chunks (`render/encode.py`), then muxes the mix (VO + SFX + soft synthesized pad).
- `.github/workflows/render.yml` — renders on GitHub Actions, two cuts of the same script and
  voice-over (`POTONGAN` in `render/naskah.py`): `tiktok-wa-release-bot-eps2` (full, ~2:30) and
  `tiktok-wa-release-bot-eps2-pendek` (short, ~1:13, for FYP), one MP4 artifact each. Runs on
  every push to `main` that touches render files, or manually via *Run workflow*.
  Locally: `EPS2_POTONGAN=pendek python3 render/render.py`.

Local checks without ffmpeg / cek lokal tanpa ffmpeg:

```bash
python3 render/aset.py --unduh           # fetch stickers + SFX into aset/cache (gitignored)
python3 render/render.py --info          # timeline
python3 render/render.py --cek 2         # draw one frame every 2 s, catch errors
python3 render/render.py --frame 51 f.png
```

## Episode 2

Script, TikTok caption, pinned comment and upload notes: [`skrip.md`](skrip.md).

## License / Lisensi

Same personal-use license as the product repo (`LICENSE`). Fonts: Archivo, SIL OFL 1.1.
All SFX, music and artwork are generated in code; no third-party media (`THIRD_PARTY_NOTICES.md`).

---

Built by xykal — XyVerse Technology Global  
Dibuat oleh xykal — XyVerse Technology Global
