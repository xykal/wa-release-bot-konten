"""Naskah Eps 2 — satu sumber untuk VO, judul, layar HP, dan cue SFX.

`teks` HARUS sama persis dengan yang dibacakan di vo/<vo>.wav, karena waktu
per kata buat subtitle karaoke dihitung dari file suaranya (lihat audio.py).
`tahap` = daftar (kata_pemicu, judul, mode_layar): begitu narator sampai di
kata itu, judul dan layar ganti. Kata pemicu dicocokkan tanpa tanda baca.
"""

SCENES = [
    dict(vo='00', layar='masalah',
         judul='Grup kemasukan *akun aneh?*',
         tahap=[('Channel-nya', 'Channel *sepi?*', 1), ('Rilis', 'Rilis *lupa diumumin?*', 2), ('Tenang', 'Ada *satu bot* buat semuanya', 3)],
         teks='Grup WhatsApp kamu sering kemasukan akun aneh? Channel-nya sepi? Rilis aplikasi lupa diumumin? Tenang, ada satu bot yang ngurus semuanya.'),
    dict(vo='01', layar='beranda',
         judul='Kenalin, *WA Release Bot*',
         tahap=[('Nggak', 'Jalan *dari HP*, tanpa server', 1)],
         teks='Kenalin, WA Release Bot. Bot bikinan Kall yang jalan langsung dari HP Android. Nggak perlu server, nggak perlu laptop, nggak perlu Termux.'),
    dict(vo='02', layar='pairing',
         judul='Nyambung pakai *kode pairing*',
         tahap=[('Selesai', '*Selesai.* Bot siap kerja', 1)],
         teks='Nyambunginnya gampang. Buka aplikasinya, masukin kode pairing, persis kayak nambah perangkat WhatsApp biasa. Selesai! Botnya langsung siap kerja.'),
    dict(vo='03', layar='rilis',
         judul='Rilis GitHub *auto ke channel*',
         tahap=[('Rapi', 'Post-nya *rapi*: catatan + file', 1)],
         teks='Tiap kamu rilis versi baru di GitHub, bot langsung posting ke channel. Rapi banget: apa yang baru, file yang bisa diunduh, sampai ukurannya.'),
    dict(vo='04', layar='grup',
         judul='Penjaga grup *otomatis*',
         tahap=[('Yang', 'Pernah keluar? *Ditolak.*', 1), ('Kamu', 'Grup aman *tanpa dipantau*', 2)],
         teks='Buat grup, ada penjaga otomatis. Permintaan gabung dicek satu-satu. Yang dulu udah keluar, atau pernah di-kick? Ditolak. Kamu nggak perlu mantengin lagi.'),
    dict(vo='05', layar='lagu',
         judul='Tiap hari *ada lagu*',
         tahap=[('Ada', '*148 lagu* + yang lagi trend', 1)],
         teks='Channel kamu nggak bakal sepi. Tiap hari bot ngirim potongan lagu enam puluh detik, dalam bentuk voice note. Ada seratus empat puluh delapan lagu, plus yang lagi trend minggu ini.'),
    dict(vo='06', layar='caption',
         judul='Caption-nya *kena banget*',
         tahap=[('Yang', 'Contoh gaya *sok bijak*', 1)],
         teks='Caption-nya kena banget. Kadang galau, kadang motivasi, kadang nyindir, kadang ayat. Yang ini contohnya: Katanya udah move on. Terus kenapa lagu ini masih di-repeat?'),
    dict(vo='07', layar='lapor',
         judul='Gagal? *Lapor sendiri*',
         tahap=[('Dan', 'Selesai kerja? *Tidur.*', 1)],
         teks='Kalau kirimnya gagal tiga kali, bot lapor ke chat kamu sendiri. Dan di antara pengecekan, botnya tidur. Baterai aman, kuota aman.'),
    dict(vo='08', layar='github',
         judul='*Open source*, gratis',
         tahap=[('Kodenya', 'Kode + APK: *komentar pin*', 1)],
         teks='Semuanya open source, gratis, dan bisa kamu pasang sendiri. Kodenya ada di GitHub, link-nya di komentar yang di-pin.'),
    dict(vo='09', layar='cta',
         judul='Fitur apa lagi? *Tulis di komen*',
         tahap=[('Follow', '*Follow* buat episode berikutnya', 1)],
         teks='Menurut kamu, fitur apa lagi yang harus ditambahin? Tulis di komen ya. Follow, biar nggak ketinggalan episode berikutnya!'),
]

# Jeda sebelum VO mulai di tiap scene, jeda setelah VO habis, dan outro (logo + CTA diam).
JEDA_AWAL, JEDA_AKHIR, OUTRO = 0.35, 0.45, 1.6

# Kalau file VO belum ada (klip belum dibuat), durasi ditaksir dari panjang teks.
KARAKTER_PER_DETIK = 13.5

CAPTION_TIKTOK = (
    'Satu bot buat grup, channel, dan rilis aplikasi kamu. Jalan dari HP, tanpa server. '
    'Fitur apa lagi yang harus ditambahin? Tulis di komen.\n\n'
    '#botwhatsapp #whatsapp #androiddeveloper #bikinaplikasi #coding #programmer #teknologi #opensource #fyp #xyverse'
)
