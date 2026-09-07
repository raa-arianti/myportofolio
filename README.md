# My Portofolio Website

Website portofolio pribadi yang dibangun dengan Django, HTML5, dan CSS3.
Proyek ini dikembangkan secara bertahap sepanjang mata kuliah **Pemrograman Berbasis
Platform (CSGE602022)**, Fakultas Ilmu Komputer, Universitas Indonesia,
Semester Gasal 2026/2027.

| | |
|---|---|
| **Nama** | Ira Arianti Alawiah |
| **NPM** | 2506551775 |
| **Kelas** | PBP D |

- **Repositori:** https://github.com/raa-arianti/myportofolio
- **Deployment (PWS):** http://ira-arianti-myportofolio.pws.cs.ui.ac.id

---

## Tentang Proyek

Sebuah halaman portofolio satu halaman yang memperkenalkan diri saya, bidang yang
sedang saya pelajari, dan proyek-proyek yang pernah saya kerjakan. Sampai tahap ini
halaman masih sepenuhnya statis, belum menggunakan basis data maupun arsitektur MVT.

Halaman terdiri atas tiga bagian utama:

1. **About Me**, berisi foto, nama, NPM, dan bio singkat.
2. **Focus Areas**, berisi tiga bidang yang sedang saya dalami, disusun sebagai daftar.
3. **Recent Work**, berisi tiga proyek yang pernah saya kerjakan, disusun sebagai kartu.

## Teknologi

- Python 3.13 dan Django 6.1
- HTML5 semantik serta CSS3 (custom properties, Flexbox, CSS Grid, media query)
- Google Fonts: Playfair Display dan Lora
- Deployment: Pacil Web Service (PWS) dengan Gunicorn dan WhiteNoise

## Struktur Proyek
<pre>
myportofolio/
├── manage.py
├── requirements.txt
├── portofolio/              # konfigurasi Django (settings, urls, wsgi)
├── main/                    # aplikasi utama, berisi views.py
├── templates/
│   └── index.html           # seluruh halaman portofolio
└── static/
    ├── css/style.css        # seluruh gaya halaman
    └── img/                 # foto, ikon, dan pratinjau proyek
</pre>

## Menjalankan Secara Lokal

```bash
# 1. Klon repositori
git clone https://github.com/raa-arianti/myportofolio.git
cd myportofolio

# 2. Buat dan aktifkan virtual environment
python -m venv env
env\Scripts\activate          # Windows
# source env/bin/activate     # macOS / Linux

# 3. Pasang dependencies
pip install -r requirements.txt

# 4. Buat berkas .env di root proyek, isi dengan:
#    PRODUCTION=False

# 5. Jalankan migrasi dan server
python manage.py migrate
python manage.py runserver
```

Halaman dapat diakses di http://localhost:8000/

---

## Progres Mingguan

### Tutorial 0, Setup
Membuat repositori Git, memasang Django, dan menginisiasi proyek.

### Tutorial 01, Halaman statis pertama
Menghubungkan view ke template, membangun section "About Me" dengan HTML5 semantik
dan CSS3, lalu men-deploy ke PWS.

### Tugas 1, Perluasan halaman
Mengganti seluruh data contoh dengan data pribadi, mengganti palet dan tipografi
dengan sistem desain sendiri, serta menambahkan dua section baru yaitu **Focus Areas**
dan **Recent Work**, keduanya responsif dengan efek hover tersendiri.

**Rencana iterasi berikutnya:** memperbarui hero, navbar, dan footer agar sesuai
rancangan visual penuh, serta memindahkan data proyek dari HTML ke basis data.

---

## Pertanyaan Reflektif

### Tugas 1

**1. Apakah Anda menggunakan elemen semantik HTML5 seperti `<section>`, `<article>`, atau `<aside>`? Bagaimana elemen tersebut membantu?**

Ya. Saya menggunakan `<header>`, `<nav>`, `<main>`, `<section>`, `<article>`, dan
`<footer>` sebagai kerangka halaman, ditambah `<ul>`/`<li>` serta `<dl>`/`<dt>`/`<dd>`
untuk struktur di dalamnya. Elemen `<aside>` tidak saya pakai karena tidak ada konten
sampingan yang benar-benar terpisah dari alur utama halaman. Memaksakannya justru akan
memberi makna yang keliru.

Bagian yang paling membuat saya berpikir adalah memilih antara `<article>` dan
`<ul>`/`<li>` untuk dua section baru saya, karena keduanya sama-sama berupa kumpulan
tiga item dan secara tampilan bisa dibuat identik. Saya akhirnya membedakannya:

- **Focus Areas** memakai `<ul>`/`<li>`, karena ketiga bidang itu adalah butir-butir
  sejajar dalam satu daftar. Tidak ada satu pun yang masuk akal kalau dicabut dan
  berdiri sendiri di luar konteks daftarnya.
- **Recent Work** memakai `<article>`, karena tiap proyek punya judul, gambar, dan
  deskripsinya sendiri. Satu kartu proyek tetap utuh maknanya kalau dikutip terpisah,
  dan itulah definisi `<article>` menurut spesifikasi HTML.

Manfaat konkret yang saya rasakan ada tiga. Pertama, **aksesibilitas**. Pembaca layar
mengumumkan Focus Areas sebagai "daftar berisi tiga item", sehingga pengguna tahu
seberapa panjang bagian itu sebelum mendengarkannya. Kedua, **penulisan CSS jadi lebih
stabil**. Saya menargetkan elemen berdasarkan maknanya (`.focus-card`, `.work-card`),
bukan posisinya, jadi menambah atau menukar urutan item tidak merusak gaya apa pun.
Ketiga, **kode lebih mudah dibaca ulang**. Membuka HTML saya seminggu kemudian, struktur
halaman langsung terbaca tanpa perlu menelusuri nama kelas satu per satu, sesuatu yang
tidak saya dapat kalau semuanya ditulis sebagai `<div>`.

**2. Tantangan tata letak apa yang Anda temukan saat membuat CSS responsif? Bagaimana Anda mengevaluasi elemen mana yang harus diubah posisinya atau diprioritaskan ukurannya?**

Tantangan terbesar saya bukan membuat kolom menumpuk, melainkan menemukan bahwa **satu
bagian layout punya tinggi tetap sementara bagian lain punya tinggi cair**, dan keduanya
bertabrakan diam-diam.

Di section Recent Work, teks judul dan deskripsi saya letakkan menumpuk di atas gambar
dengan latar pink transparan. Tinggi lapisan teks itu ditentukan oleh panjang teksnya,
jadi angkanya tetap dan tidak ikut mengecil. Sebaliknya tinggi gambar ditentukan oleh
lebar kolom, jadi ikut menyusut saat layar mengecil. Saat saya ukur:

| Lebar layar | Tinggi kartu | Tinggi lapisan teks | Teks menutupi |
|---|---|---|---|
| 1280px | 365px | 106px | 29% |
| 700px | 258px | 106px | **41%** |

Di layar sempit, lapisan teks memanjat naik sampai memotong tombol di dalam gambar.
Masalah ini tidak terlihat sama sekali di layar desktop, dan tidak akan ketahuan kalau
saya hanya mengecilkan jendela browser sekilas tanpa mengukurnya.

Cara saya mengevaluasi: **saya mencari lebar layar tempat tata letak benar-benar mulai
rusak, lalu menaruh breakpoint di situ**, bukan memakai angka standar seperti 768px
begitu saja. Contohnya di Focus Areas, grid tiga kolom saya masih nyaman di 900px, tetapi
pada 640px tiap kolom tinggal sekitar 170px sementara ikonnya sendiri sudah 132px,
sehingga deskripsi pecah menjadi baris-baris pendek. Karena itu breakpoint-nya saya taruh
di **820px**, bukan di 600px yang sudah ada sejak Tutorial 01. Kalau menunggu 600px,
tampilannya sudah rusak jauh sebelum aturannya aktif.

Prinsip prioritas yang saya pakai: **keterbacaan teks selalu menang atas kesetiaan
visual.** Gambar boleh mengecil, kolom boleh runtuh, efek dekoratif boleh hilang, tetapi
teks tidak boleh tertutup atau menyusut sampai sulit dibaca. Karena itu di bawah 600px
saya tidak sekadar menjadikan satu kolom, melainkan **memindahkan lapisan teks keluar
dari atas gambar** dan mengembalikannya ke bawah gambar sebagai blok pink solid. Tiga
tingkat perilaku yang terbentuk:

| Lebar | Kolom | Posisi teks |
|---|---|---|
| di atas 820px | 2 kolom (rasio 1 : 2.44) | menumpuk di atas gambar |
| 600px sampai 820px | 1 kolom | masih menumpuk |
| di bawah 600px | 1 kolom | turun ke bawah gambar |

Satu hal lain yang saya syukuri: `grid-template-areas` yang dipakai di hero sejak
Tutorial 01 memungkinkan saya mengatur urutan tampil di layar sempit (nama, lalu foto,
lalu bio) berbeda dari urutan di HTML, tanpa mengubah markup sedikit pun. Itu membuat
saya sadar bahwa urutan dokumen dan urutan tampilan adalah dua hal yang bisa dipisahkan.

**3. Batasan apa yang Anda rasakan pada static web murni? Fungsionalitas dinamis apa yang ingin Anda tambahkan berikutnya?**

Batasan yang paling saya rasakan adalah **tidak adanya pemisahan antara data dan
tampilan**. Ketiga proyek di Recent Work ditulis langsung sebagai markup: judul,
deskripsi, dan nama berkas gambarnya menempel di dalam HTML. Akibatnya:

- Menambah proyek keempat berarti menyalin blok `<article>` secara manual, lalu
  memeriksa ulang penempatannya di grid. Ini melanggar prinsip DRY, karena ada tiga blok
  yang hampir identik dan berbeda hanya isinya.
- Tidak ada satu sumber kebenaran. Kalau saya ingin mengganti judul sebuah proyek,
  saya harus mencarinya di dalam HTML, bukan mengubah satu baris data.
- Setiap perubahan konten sekecil apa pun menuntut commit dan deploy ulang. Untuk
  memperbaiki satu salah ketik pun, saya harus melalui seluruh alur Git.
- Konten tidak bisa disaring, diurutkan, atau dicari. Kalau nanti proyeknya ada 15,
  pengunjung harus menggulir semuanya.

Fungsionalitas dinamis yang paling ingin saya siapkan berikutnya, berurutan:

1. **Model Django untuk `Project` dan `FocusArea`.** Data pindah ke basis data, dan
   template cukup melakukan perulangan `{% for %}` atas satu blok markup. Tiga blok
   `<article>` yang berulang akan menyusut menjadi satu.
2. **Django Admin** untuk mengelola isi portofolio tanpa menyentuh kode sama sekali.
   Ini yang paling mengubah cara kerja saya sehari-hari.
3. **Halaman detail proyek** dengan URL dinamis, sehingga tiap proyek punya alamatnya
   sendiri dan bisa dibagikan terpisah. Menariknya, ini sekaligus membuktikan pilihan
   `<article>` saya di pertanyaan pertama: konten yang memang berdiri sendiri secara
   semantik ternyata juga yang paling masuk akal untuk diberi halaman sendiri.
4. **Formulir kontak** yang benar-benar mengirim pesan, melibatkan penanganan POST,
   CSRF token, dan validasi, hal-hal yang mustahil dilakukan dengan HTML dan CSS saja.

---

## Penggunaan AI (AI Disclosure)

Saya **menggunakan bantuan AI** dalam mengerjakan tugas ini, dan berikut rinciannya
selengkap yang saya bisa.

### Tools

**Claude (model Opus 5) melalui Claude Code**, sesi tunggal pada 7 September 2026.

### Strategi prompting

Saya tidak meminta AI membuatkan seluruh website. Sebelum mulai, saya menetapkan aturan
kerja eksplisit lewat prompt berikut:

> I have an existing Django portfolio project based on Tutorial 01. I want to continue
> and improve this existing project based on my own design reference.
>
> **Workflow rules:** (1) Do not modify any files directly. (2) Do not create, delete,
> overwrite, or automatically edit files. (3) Do not use automated file-editing tools.
> (4) I will manually copy and paste every code change myself. (5) Work incrementally,
> one section at a time. (6) Before moving to the next section, wait for my confirmation.
> (7) Never give me the entire website code at once. (8) Always inspect the existing code
> before suggesting changes. (9) Preserve my existing structure and functionality unless
> a change is necessary. (10) Do not redesign my website. Follow my provided design
> reference.
>
> **For every section:** STEP A, analysis (identify relevant existing HTML/CSS, explain
> what needs to change, and in which file). STEP B, HTML only, explain where to paste,
> wait for my confirmation. STEP C, CSS, after I confirm the HTML works. STEP D,
> responsive CSS last.

Alasan saya menyusun aturan seperti itu: kalau AI boleh menulis berkas sendiri, saya
akan berakhir memiliki kode yang tidak saya pahami. Dengan mengetik ulang setiap
potongan dan mengujinya sebelum lanjut, saya tahu persis apa yang masuk ke proyek saya
dan kenapa. Larangan "jangan redesign" saya tambahkan karena rancangan visualnya sudah
saya buat sendiri lebih dulu, dan saya ingin AI mengikutinya, bukan menggantinya.

### Bagian yang dibantu AI

- Menerjemahkan rancangan visual saya menjadi struktur HTML dan aturan CSS.
- Menjelaskan alasan di balik tiap teknik (`grid-template-areas`, `object-fit`,
  `clamp()`, `flex: 1`, satuan `ch`), sehingga saya tidak sekadar menyalin.
- Mengukur perilaku tata letak di berbagai lebar layar untuk menemukan letak breakpoint
  yang tepat.
- Menyusun komentar kode dan draf awal dokumentasi ini.

### Bagian yang saya kerjakan sendiri

- **Seluruh rancangan visual** (palet, tipografi, tata letak, komposisi tiap section)
  dibuat sebelum AI dilibatkan sama sekali.
- Menyiapkan dan mengekspor seluruh aset gambar.
- Mengetik dan menempel setiap baris kode, lalu mengujinya di browser setelah tiap
  langkah.
- Mengambil keputusan akhir, termasuk keputusan berhenti menambah fitur dan
  memprioritaskan dokumentasi menjelang tenggat.

### Analisis kritis: keterbatasan AI yang saya temukan

Bagian ini yang menurut saya paling berharga dari proses kerja tadi.

**1. AI salah membaca rancangan saya dua kali berturut-turut, dengan sangat percaya
diri.** Pada section Recent Work, AI mula-mula menyimpulkan gambar proyek ditampilkan
utuh dengan teks di bawahnya. Setelah saya bilang hasilnya tidak sesuai, AI justru
memperbaiki ke arah yang salah, yaitu memotong gambar dengan `object-fit: cover`,
lengkap dengan tabel perhitungan piksel yang terlihat meyakinkan. Padahal rancangan saya
tidak memotong apa pun. Teksnya berada di **lapisan pink beropasitas 75% di atas
gambar**, dan struktur baru menjadi benar setelah saya menyebutkan hal itu secara
eksplisit. Pelajarannya: AI tidak bisa melihat maksud dari sebuah gambar rancangan.
Ia menebak, dan tebakannya bisa salah tanpa terdengar ragu sedikit pun. Perhitungan yang
rapi tidak menjamin premisnya benar.

**2. Warna yang diambil AI dari mockup meleset.** AI menebak pink saya `#f9dce5`
berdasarkan tangkapan layar. Nilai sebenarnya dari berkas rancangan saya adalah
`#FFE8EF`. Saya periksa dan koreksi sendiri. Warna yang dicomot dari gambar terkompresi
tidak bisa dipercaya sebagai nilai final.

**3. Font di proyek ini masih berupa tebakan AI yang belum saya verifikasi.** AI
menanyakan font yang saya pakai, saya belum sempat mengeceknya, dan AI melanjutkan
dengan asumsi Playfair Display dan Lora sambil menyatakan terbuka bahwa itu asumsi. Saya
mencatat ini sebagai utang yang belum lunas, bukan sebagai keputusan desain.

**4. AI juga salah menduga isi berkas aset saya.** Melihat mockup, AI menyimpulkan latar
hero berupa kolase tegel bunga. Setelah berkasnya dibuka, isinya ternyata gradasi polos.
Ini menegaskan pola yang sama, bahwa kesimpulan dari gambar perlu diverifikasi ke sumber
aslinya.

### Perbaikan manual yang saya lakukan

- Mengoreksi warna pink ke `#FFE8EF` setelah memeriksa berkas rancangan saya.
- Mengoreksi struktur kartu proyek menjadi lapisan transparan di atas gambar, setelah
  dua usulan AI sebelumnya keliru.
- Menghentikan penambahan fitur dan mengalihkan sisa waktu ke dokumentasi.

Kesimpulan saya: AI sangat membantu untuk menjelaskan konsep dan mempercepat penulisan
kode, tetapi ia bekerja dari tebakan atas apa yang saya maksud. Yang menjaga hasil akhir
tetap benar adalah saya sendiri, dengan menguji tiap langkah, membandingkannya dengan
rancangan asli, dan berani mengatakan bahwa sesuatu belum sesuai alih-alih menerima
hasil yang kelihatannya sudah rapi.