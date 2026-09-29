# Naskah Eps 2 — "Satu bot buat grup, channel, dan rilis"

Format: 720x1280, 60 fps, satu file `tiktok-wa-release-bot-eps2.mp4`. Durasi mengikuti
panjang VO (lihat `python3 render/render.py --info`), sekitar 1 menit 55 detik.
Narator satu suara (AI, perempuan, Bahasa Indonesia santai) untuk semua scene —
tidak ada suara lain, termasuk saat menyebut nama pembuat.

Sumber kebenaran naskah = `render/naskah.py` (teks VO harus sama persis dengan file
`vo/NN.wav`, karena waktu per kata buat karaoke dihitung dari suaranya).

| # | Judul di layar | Layar HP | VO |
|---|---|---|---|
| 00 | Grup kemasukan akun aneh? → Channel sepi? → Rilis lupa diumumin? → Ada satu bot | grup spam, channel kosong, rilis GitHub nganggur, 3 kartu solusi | Grup WhatsApp kamu sering kemasukan akun aneh? Channel-nya sepi? Rilis aplikasi lupa diumumin? Tenang, ada satu bot yang ngurus semuanya. |
| 01 | Kenalin, WA Release Bot → Jalan dari HP, tanpa server | beranda app: tersambung, repo dipantau, coret server/laptop/Termux | Kenalin, WA Release Bot. Bot bikinan Kall yang jalan langsung dari HP Android. Nggak perlu server, nggak perlu laptop, nggak perlu Termux. |
| 02 | Nyambung pakai kode pairing → Selesai. Bot siap kerja | kode pairing diketik, langkah di WA, centang tersambung | Nyambunginnya gampang. Buka aplikasinya, masukin kode pairing, persis kayak nambah perangkat WhatsApp biasa. Selesai! Botnya langsung siap kerja. |
| 03 | Rilis GitHub auto ke channel → Post-nya rapi: catatan + file | kartu release terbang, post channel format baru (apa yang baru, file + ukuran) | Tiap kamu rilis versi baru di GitHub, bot langsung posting ke channel. Rapi banget: apa yang baru, file yang bisa diunduh, sampai ukurannya. |
| 04 | Penjaga grup otomatis → Pernah keluar? Ditolak. → Grup aman tanpa dipantau | daftar permintaan gabung, "ngecek...", DITOLAK / centang, stiker perisai | Buat grup, ada penjaga otomatis. Permintaan gabung dicek satu-satu. Yang dulu udah keluar, atau pernah di-kick? Ditolak. Kamu nggak perlu mantengin lagi. |
| 05 | Tiap hari ada lagu → 148 lagu + yang lagi trend | voice note kemarin & hari ini, kartu 148 lagu, chip trend, stiker not | Channel kamu nggak bakal sepi. Tiap hari bot ngirim potongan lagu enam puluh detik, dalam bentuk voice note. Ada seratus empat puluh delapan lagu, plus yang lagi trend minggu ini. |
| 06 | Caption-nya kena banget → Contoh gaya sok bijak | 4 gelembung gaya (galau, motivasi, nyindir, ayat), contoh diketik | Caption-nya kena banget. Kadang galau, kadang motivasi, kadang nyindir, kadang ayat. Yang ini contohnya: Katanya udah move on. Terus kenapa lagu ini masih di-repeat? |
| 07 | Gagal? Lapor sendiri → Selesai kerja? Tidur. | 3 percobaan gagal, laporan ke chat "Anda", bulan + zzz, CPU/baterai/kuota | Kalau kirimnya gagal tiga kali, bot lapor ke chat kamu sendiri. Dan di antara pengecekan, botnya tidur. Baterai aman, kuota aman. |
| 08 | Open source, gratis → Kode + APK: komentar pin | kartu repo GitHub, chip gratis/source-available/pasang sendiri, kartu komentar pin | Semuanya open source, gratis, dan bisa kamu pasang sendiri. Kodenya ada di GitHub, link-nya di komentar yang di-pin. |
| 09 | Fitur apa lagi? Tulis di komen → Follow buat episode berikutnya | komentar masuk, kolom komentar diketik, tombol Follow | Menurut kamu, fitur apa lagi yang harus ditambahin? Tulis di komen ya. Follow, biar nggak ketinggalan episode berikutnya! |

Outro 1,6 detik: perisai + "WA Release Bot" + "Kode + APK: komentar yang di-pin".

## Caption TikTok (copy-paste)

Satu bot buat grup, channel, dan rilis aplikasi kamu. Jalan dari HP, tanpa server.
Fitur apa lagi yang harus ditambahin? Tulis di komen.

#botwhatsapp #whatsapp #androiddeveloper #bikinaplikasi #coding #programmer #teknologi #opensource #fyp #xyverse

## Komentar yang di-pin (tulis sendiri setelah upload)

Kode + APK: github.com/xykal/wa-release-bot (menu Releases, file app-arm64.apk).
Eps 3: cara pasangnya langkah demi langkah, atau fitur lain? Vote di balasan.

## Catatan upload

1. Nyalakan label "Konten yang dibuat AI" (suaranya AI). Jangan tulis "link di bio"/"download" di caption; arahkan ke komentar pin.
2. Video sudah ada musik latar pelan (sintetis, bebas lisensi). Kalau mau pasang sound yang lagi ramai, set volume sound tambahan 10-15% supaya narasi tetap jelas.
3. Sampul: ambil frame di detik 3-4 (judul "Grup kemasukan akun aneh?") atau detik 51 (stempel DITOLAK + perisai).
4. Jam posting yang biasanya ramai: 11.00-13.00 atau 19.00-21.00 WIB.
5. Balas komentar pakai video balasan; itu bahan Eps 3.
6. Jangan hapus lalu upload ulang video yang sama; kalau sepi, bikin versi hook beda.

## Batas panjang TikTok

TikTok menerima video sampai 10 menit (upload dari aplikasi), jadi 1 menit bukan batas.
Yang jadi tantangan di video panjang cuma retensi: hook 3 detik pertama dan pergantian
layar tiap 3-5 detik, itu yang dijaga render ini.
