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

Website portofolio pribadi yang memperkenalkan diri saya, bidang yang sedang saya
pelajari, pengalaman, dan proyek yang pernah saya kerjakan. Sejak Tutorial 02, data
yang sebelumnya ditulis langsung di HTML mulai dipindahkan ke basis data dengan
arsitektur Model-View-Template (MVT) Django.

Website terdiri atas tiga halaman:

| Halaman | URL | Isi |
|---|---|---|
| Home | `/` | hero dengan data profil dari context view, Focus Areas, dan Recent Work |
| Experience | `/experience/` | daftar pengalaman dari model `Experience` |
| Projects | `/projects/` | daftar proyek dari model `Project` |

Sejak Tutorial 03 dan Tugas 3, proyek dan experience dapat **ditambah, diubah, dan dihapus**
lewat form, datanya juga tersedia dalam **format JSON**, dan halaman daftarnya dirender dari
JSON tersebut. Semua halaman memakai kerangka `base.html` yang sama.

| Fitur | URL |
|---|---|
| Tambah proyek | `/projects/add/` |
| Ubah dan hapus proyek | `/projects/<id>/edit/`, `/projects/<id>/delete/` |
| Tambah experience | `/experience/add/` |
| Ubah dan hapus experience | `/experience/<id>/edit/`, `/experience/<id>/delete/` |
| Data JSON | `/api/projects/` (mendukung `?title=`), `/api/experience/` |
| Masuk mode pemilik | `/owner/` |

### Mode pemilik

Karena belum ada login, fitur tambah, ubah, dan hapus dikunci dengan environment variable
`OWNER_SECRET`. Pengunjung tidak melihat tombol apa pun, dan membuka URL form secara
langsung menghasilkan halaman **403**. Pemilik membuka `/owner/`, memasukkan kata sandi,
lalu semua tombol muncul sampai ia keluar.

Kalau `OWNER_SECRET` **tidak diatur**, kunci dinonaktifkan dan semua fitur form terbuka.
Ini disengaja supaya asisten dosen yang menjalankan proyek di laptopnya tetap bisa menguji
seluruh fitur tanpa perlu kata sandi.

## Teknologi

- Python 3.13 dan Django 5.2 (LTS, menyesuaikan dukungan PostgreSQL di PWS)
- SQLite untuk pengembangan lokal, PostgreSQL di PWS
- HTML5 semantik, CSS3 (custom properties, Flexbox, CSS Grid, media query,
  pseudo-element), dan Django Template Language
- Google Fonts: Playfair Display, Source Serif 4, dan Libre Baskerville
- Deployment: Pacil Web Service (PWS) dengan Gunicorn dan WhiteNoise

## Struktur Proyek
<pre>
myportofolio/
├── manage.py
├── requirements.txt
├── portofolio/              # konfigurasi Django (settings, urls proyek, wsgi)
├── main/                    # aplikasi utama
│   ├── models.py            # model Experience dan Project
│   ├── forms.py             # ProjectForm dan ExperienceForm (ModelForm)
│   ├── views.py             # halaman, form, endpoint JSON, dan mode pemilik
│   ├── urls.py              # named route aplikasi (namespace "main")
│   ├── owner.py             # kunci mode pemilik (OWNER_SECRET)
│   ├── context_processors.py  # data yang dibutuhkan base.html di semua halaman
│   ├── tests.py             # unit test
│   └── migrations/          # riwayat perubahan skema basis data
├── templates/
│   ├── base.html            # kerangka bersama: head, navbar, footer, pesan
│   ├── index.html           # halaman utama
│   ├── experience.html      # daftar pengalaman
│   ├── projects.html        # daftar proyek dengan pencarian
│   ├── entry_form.html      # satu halaman form untuk tambah dan ubah data
│   ├── owner_login.html     # masuk mode pemilik
│   ├── 403.html             # halaman untuk pengunjung yang bukan pemilik
│   └── components/
│       └── owner_actions.html  # tombol Edit, Delete, dan dialog konfirmasi
└── static/
    ├── css/style.css        # seluruh gaya halaman
    └── img/                 # foto, ilustrasi cat air, ikon, dan gambar proyek
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
#    OWNER_SECRET=          (kosongkan agar semua fitur form terbuka saat dicoba lokal)

# 5. Jalankan migrasi dan server
python manage.py migrate
python manage.py runserver

# 6. Jalankan unit test (matikan server dulu dengan Ctrl+C)
python manage.py test main
```

Halaman dapat diakses di http://localhost:8000/

Halaman Experience dan Projects akan menampilkan pesan kosong sampai datanya
ditambahkan lewat tombol **Add project** dan **Add experience**.

Di PWS, `PRODUCTION=True` membuat Django memakai PostgreSQL dari variabel `DB_NAME`,
`DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`, dan `SCHEMA`, sehingga data tidak hilang
setiap kali deploy. `OWNER_SECRET` diatur di Project Environment Variables PWS.

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

### Tutorial 02, Model-View-Template
Membuat model `Experience`, memindahkan data profil dari HTML ke context view, membuat
halaman `/experience/` dengan perulangan dan tampilan kondisi kosong, mengatur routing
lewat `main/urls.py`, dan menulis enam unit test pertama.

### Redesain home page (lanjutan Tugas 1)
Menyelesaikan rencana iterasi dari Tugas 1: navbar berbentuk kapsul, hero dengan gradasi
dan awan cat air, footer dengan lukisan cat air, serta tipografi yang dicocokkan dengan
rancangan Figma. Sekaligus memperbaiki bug CSS responsif Recent Work dari Tugas 1 yang
ternyata tidak pernah aktif, karena aturannya tertulis bersarang di dalam selektor lain.

### Tugas 2, Halaman proyek berbasis model
Menambahkan model `Project`, halaman `/projects/` berisi kartu proyek dari basis data
dengan tampilan kondisi kosong, tautan navbar dengan `{% url %}`, grid kartu responsif
tanpa media query, dan empat unit test baru.

### Tutorial 03, Form dan Data Delivery
Memindahkan head, navbar, dan footer ke `base.html` yang di-extend semua halaman, membuat
form tambah proyek dengan `ModelForm` dan CSRF token, endpoint JSON `/api/projects/` yang
juga dipakai untuk merender halaman proyek setelah di-deserialize, pencarian berdasarkan
judul, serta hapus proyek dengan dialog konfirmasi.

### Tugas 3, Form dan JSON untuk Experience
Menambahkan `ExperienceForm`, halaman tambah dan ubah experience, tombol hapus, dan
endpoint `/api/experience/` yang dipakai untuk merender halaman experience. Sebagai fitur
tambahan: proyek juga bisa diubah, satu halaman form dan satu komponen aksi dipakai bersama,
PWS kini memakai PostgreSQL agar data tidak hilang saat deploy, dan **mode pemilik** membuat
hanya pemilik yang dapat menambah, mengubah, dan menghapus konten.

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

### Tugas 2

**1. Jelaskan alur yang terjadi ketika pengguna membuka halaman portofolio baru, mulai dari permintaan yang diterima proyek hingga data ditampilkan pada browser. Dalam jawabanmu, jelaskan peran `urls.py` proyek, `urls.py` aplikasi, view, model, dan template.**

Saya ambil contoh saat pengguna membuka `/projects/`.

1. **`portofolio/urls.py` (URL proyek)** menerima permintaan pertama kali. Isinya
   `path("", include("main.urls"))`, jadi ia tidak memilih view sama sekali. Tugasnya hanya
   meneruskan permintaan ke aplikasi `main`.
2. **`main/urls.py` (URL aplikasi)** mencocokkan sisa alamat `projects/` dengan
   `path("projects/", show_projects, name="show_projects")`. Nama rute ini yang saya pakai
   di navbar lewat `{% url 'main:show_projects' %}` dan di unit test lewat `reverse()`.
3. **View `show_projects`** memanggil model lewat `Project.objects.all()`.
4. **Model `Project`** menerjemahkan panggilan itu menjadi query SQL ke basis data (SQLite
   di laptop, PostgreSQL di PWS) dan mengembalikan QuerySet. Urutannya sudah ditentukan
   `ordering = ["created_at"]` di `Meta` model, jadi view tidak perlu mengurutkan sendiri.
5. View lalu menyusun **context** berisi `project_list`, `name`, dan `brand_name`, lalu
   memanggil `render()` dengan template `projects.html`.
6. **Template** mengulang `{% for project in project_list %}` untuk membuat satu kartu per
   proyek, atau menjalankan `{% empty %}` kalau datanya kosong. Hasilnya berupa HTML utuh
   yang dikirim sebagai respons.
7. Setelah HTML diterima, browser **meminta lagi** berkas CSS dan setiap gambar kartu ke
   `/static/...`. Permintaan ini dilayani terpisah sebagai berkas statis, tidak melewati
   view.

Yang paling membantu saya memahami alur ini adalah pesan error saat halaman belum
lengkap. Setelah route dan view dibuat tetapi template belum ada, membuka `/projects/`
memunculkan `TemplateDoesNotExist` dari baris `render()` di `views.py`. Artinya
permintaan sudah berhasil melewati kedua `urls.py` dan masuk ke view, dan baru berhenti
di tahap template.

**2. Mengapa data untuk bagian portofolio baru sebaiknya disimpan pada model dan tidak ditulis langsung di dalam template? Jelaskan dampaknya terhadap kemudahan pemeliharaan dan pengembangan aplikasi.**

Proyek saya sendiri menunjukkan perbedaannya dengan jelas. Section **Recent Work** di home
masih berupa tiga blok `<article>` yang saya tulis manual, sedangkan halaman **Projects**
menampilkan enam kartu dari **satu blok HTML** yang diulang oleh `{% for %}`.

Dampaknya terhadap pemeliharaan:

- **Menambah atau mengubah data tidak menyentuh kode tampilan.** Proyek ketujuh cukup satu
  `Project.objects.create(...)`. Dengan cara Recent Work, saya harus menyalin satu
  `<article>` lagi dan berhati-hati agar strukturnya tidak berbeda dari kartu lain.
- **Ada satu sumber kebenaran.** Data yang ditulis di dua tempat pasti suatu saat tidak
  sinkron. Karena itu Recent Work saya rencanakan untuk mengambil data dari model `Project`
  yang sama, bukan ditulis ulang.
- **Tampilan dan data bisa diubah terpisah.** Waktu saya mengatur grid kartu, saya hanya
  menyentuh CSS dan template, tanpa khawatir ada judul proyek yang ikut terhapus.

Dampaknya terhadap pengembangan:

- **Data bisa diurutkan dan disaring.** Rancangan saya punya dropdown filter "All". Dengan
  model, itu cukup menambah satu field kategori dan menyaring QuerySet. Dengan HTML
  statis, filter semacam itu tidak mungkin tanpa JavaScript.
- **Setiap proyek bisa punya halaman detail** berdasarkan `id`-nya, tanpa membuat satu file
  HTML per proyek.
- **Perilakunya bisa diuji.** Unit test saya membuat data palsu, lalu memastikan data itu
  muncul dan pesan kosong muncul saat datanya dihapus. Data yang ditulis mati di HTML
  tidak bisa diuji dengan cara ini.

Di pertanyaan reflektif Tugas 1, saya menulis bahwa langkah berikutnya adalah "Model Django
untuk `Project`". Setelah benar-benar mengerjakannya, perbedaan yang paling terasa adalah
HTML-nya menjadi lebih pendek sementara isinya bertambah dua kali lipat.

**3. Apa perbedaan fungsi `makemigrations` dan `migrate` pada Django? Berikan contoh perubahan model yang mengharuskanmu menjalankan kedua perintah tersebut.**

| | `makemigrations` | `migrate` |
|---|---|---|
| Yang dilakukan | membandingkan `models.py` dengan migrasi terakhir, lalu **menulis berkas instruksi** perubahan | **menjalankan** instruksi itu ke basis data |
| Menyentuh basis data? | tidak | ya |
| Hasilnya | berkas baru di `main/migrations/` | tabel atau kolom berubah, dan Django mencatat migrasi mana yang sudah diterapkan |

Contoh dari Tugas 2: setelah menambahkan `class Project` di `models.py`, `makemigrations`
membuat berkas `main/migrations/0002_project.py` berisi instruksi `Create model Project`.
Pada tahap itu tabelnya belum ada. Baru setelah `migrate`, tabel `Project` benar-benar
dibuat di `db.sqlite3`. Contoh perubahan lain yang juga membutuhkan kedua perintah itu
adalah menambahkan field `category` ke `Project` untuk dropdown filter di rancangan saya.

Dua hal yang saya pelajari dari pemisahan ini:

- **Berkas migrasi wajib di-commit.** `db.sqlite3` tidak ikut ke repositori, jadi PWS
  membuat tabelnya sendiri di PostgreSQL dengan menjalankan migrasi dari berkas yang ada di
  repositori. Tanpa `0002_project.py`, tabel `Project` tidak pernah dibuat di PWS dan
  halaman `/projects/` akan error di sana walaupun lancar di laptop.
- **Menambah data tidak membutuhkan migrasi.** Enam proyek yang saya masukkan lewat
  `python manage.py shell` hanya mengisi tabel yang strukturnya sudah ada, jadi tidak perlu
  `makemigrations` maupun `migrate`.

### Tugas 3

**1. Jelaskan mengapa kita menggunakan ModelForm pada Django alih-alih membuat form HTML secara manual. Selain itu, jelaskan pula mengapa kita diwajibkan menambahkan `{% csrf_token %}` pada form tersebut!**

<!-- JAWABAN IRA -->

**2. Pada Tutorial 03, kita membahas format data JSON dan XML. Mengapa JSON lebih disukai dalam pengembangan aplikasi web modern dibandingkan XML?**

<!-- JAWABAN IRA -->

**3. Jelaskan alur yang terjadi saat kamu menggunakan fungsi view untuk mengembalikan data portofoliomu dalam bentuk JSON. Mengapa kita perlu melakukan proses serialization pada model Django sebelum datanya dikembalikan?**

<!-- JAWABAN IRA -->

---

## Penggunaan AI (AI Disclosure)

Saya **menggunakan bantuan AI** dalam mengerjakan tugas ini, dan berikut rinciannya
selengkap yang saya bisa.

### Tugas 1

#### Tools

**Claude (model Opus 5) melalui Claude Code**, sesi tunggal pada 7 September 2026.

#### Strategi prompting

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

#### Bagian yang dibantu AI

- Menerjemahkan rancangan visual saya menjadi struktur HTML dan aturan CSS.
- Menjelaskan alasan di balik tiap teknik (`grid-template-areas`, `object-fit`,
  `clamp()`, `flex: 1`, satuan `ch`), sehingga saya tidak sekadar menyalin.
- Mengukur perilaku tata letak di berbagai lebar layar untuk menemukan letak breakpoint
  yang tepat.
- Menyusun komentar kode dan draf awal dokumentasi ini.

#### Bagian yang saya kerjakan sendiri

- **Seluruh rancangan visual** (palet, tipografi, tata letak, komposisi tiap section)
  dibuat sebelum AI dilibatkan sama sekali.
- Menyiapkan dan mengekspor seluruh aset gambar.
- Mengetik dan menempel setiap baris kode, lalu mengujinya di browser setelah tiap
  langkah.
- Mengambil keputusan akhir, termasuk keputusan berhenti menambah fitur dan
  memprioritaskan dokumentasi menjelang tenggat.

#### Analisis kritis: keterbatasan AI yang saya temukan

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

#### Perbaikan manual yang saya lakukan

- Mengoreksi warna pink ke `#FFE8EF` setelah memeriksa berkas rancangan saya.
- Mengoreksi struktur kartu proyek menjadi lapisan transparan di atas gambar, setelah
  dua usulan AI sebelumnya keliru.
- Menghentikan penambahan fitur dan mengalihkan sisa waktu ke dokumentasi.

Kesimpulan saya: AI sangat membantu untuk menjelaskan konsep dan mempercepat penulisan
kode, tetapi ia bekerja dari tebakan atas apa yang saya maksud. Yang menjaga hasil akhir
tetap benar adalah saya sendiri, dengan menguji tiap langkah, membandingkannya dengan
rancangan asli, dan berani mengatakan bahwa sesuatu belum sesuai alih-alih menerima
hasil yang kelihatannya sudah rapi.

### Tugas 2 dan redesain home page

#### Tools

**Claude (model Opus 5) melalui Claude Code** di aplikasi desktop, dalam satu percakapan
berkelanjutan pada 9, 14, dan 16 September 2026. Percakapan ini mencakup Tutorial 02,
redesain home page, dan Tugas 2.

#### Strategi prompting

Saya memakai aturan kerja yang sama dengan Tugas 1: AI tidak boleh mengubah berkas
proyek, saya yang mengetik setiap potongan kode, dan pekerjaan dibagi per section
dengan tahap analisis, HTML, CSS, lalu responsif. Saya juga meminta AI **memeriksa
hasil pekerjaan saya setelah tiap langkah**, bukan hanya memberi kode, sehingga setiap
tahap ditutup dengan pengecekan berkas, unit test, atau pengukuran halaman di browser.

Satu pengecualian saya berikan secara eksplisit di akhir: AI boleh langsung menyunting
`README.md` untuk memperbarui bagian dokumentasi yang sudah basi dan menyusun draf
bagian AI disclosure ini. Atas permintaan saya, AI juga menyusun draf jawaban
pertanyaan reflektif Tugas 2 berdasarkan kode proyek saya. Draf itu saya baca,
sunting, dan pastikan saya pahami sebelum saya masukkan ke README.

#### Bagian yang dibantu AI

- Menjelaskan konsep dan menyusun potongan kode untuk model `Project`, view, route,
  template, unit test, serta CSS navbar, footer, hero, dan halaman proyek.
- Memeriksa berkas saya setelah tiap langkah, termasuk menemukan blok footer yang tidak
  sengaja tertempel di tengah hero dan menimpa sebagian markup-nya.
- Mengukur tata letak di beberapa lebar layar langsung di browser untuk menentukan
  breakpoint hero di 960px, dan menguji CSS serta unit test lebih dulu (lewat gaya
  sementara di browser dan salinan proyek terpisah) sebelum kodenya diberikan kepada saya.
- Mengukur piksel transparan pada `footer.png` dan `awan.png` untuk menentukan posisi
  lukisan footer dan pita awan di hero.
- Menemukan bug CSS dari Tugas 1: aturan responsif Recent Work tertulis bersarang di dalam
  `.focus` dan `.hero-grid`, sehingga dibaca sebagai selektor keturunan dan tidak pernah
  cocok dengan elemen apa pun.
- Memperbarui bagian README yang basi dan menyusun draf bagian AI disclosure ini.
- Menyusun draf jawaban pertanyaan reflektif Tugas 2 dengan contoh dari kode proyek saya.

#### Bagian yang saya kerjakan sendiri

- Seluruh rancangan visual di Figma, termasuk halaman All Project, serta mengekspor
  keenam gambar kartu proyek dengan ukuran seragam.
- Mengetik dan menempel seluruh kode aplikasi, menjalankan migrasi, mengisi data lewat
  shell, menjalankan test, commit, merge, dan deploy.
- Memeriksa tampilan di browser setelah tiap langkah dan memutuskan kapan hasilnya sudah
  sesuai rancangan.
- Menyunting draf jawaban pertanyaan reflektif Tugas 2 dan memastikan setiap
  penjelasannya cocok dengan kode yang saya ketik sendiri.
- Menentukan prioritas, misalnya menyelesaikan home page lebih dulu karena tugas-tugas
  berikutnya dibangun di atasnya, serta menunda pencocokan font dan warna ke sesi lain.

#### Keterbatasan AI yang saya temukan

**1. Salah hitung, lalu salah membaca maksud rancangan di footer.** Ruang di bawah teks
footer awalnya dihitung dari tinggi semak di sisi kiri lukisan, padahal teks berada tepat
di atas menara di tengah. Ketika menara itu menembus teks, AI menganggapnya kesalahan dan
menjauhkan teks dari menara, sehingga muncul ruang kosong besar. Padahal menara yang
menembus teks copyright memang konsep rancangan saya. Setelah saya jelaskan, AI mengukur
ulang rancangan dan mengganti pendekatannya menjadi jarak atas dalam persen.

**2. Detail rancangan terlewat dari tangkapan layar yang kecil.** Kepala pada foto hero
sengaja menyembul melewati tepi atas kartu, tetapi hal ini baru disadari AI setelah saya
mengirim tangkapan layar Figma yang lebih dekat. Kalau tidak, kartunya akan dibuat
memotong foto.

**3. Beberapa nilai masih asumsi dan belum diverifikasi ke Figma.** Font untuk navbar,
subjudul section, deskripsi kartu, dan footer, serta warna kartu foto (`#f3f1f1`), masih
berupa asumsi. Warna kartu sengaja ditaruh sebagai token dengan komentar "SEMENTARA" agar
mudah diganti. Deskripsi kartu proyek juga masih sans-serif, padahal di rancangan tampak
serif. Saya mencatat ini sebagai pekerjaan yang belum selesai, bukan keputusan desain.

### Tutorial 03 dan Tugas 3

#### Tools

**Claude (model Opus 5) melalui Claude Code** di aplikasi desktop, 16 September 2026, dalam
percakapan yang sama dengan Tutorial 02 dan Tugas 2.

#### Strategi prompting

Berbeda dari tugas sebelumnya, untuk Tutorial 03 dan Tugas 3 saya **secara eksplisit
mengizinkan AI mengubah kode dan membuat commit langsung**, satu commit per tahap, karena
Tutorial 03 berbatas waktu malam itu juga dan jadwal saya beberapa hari setelahnya penuh.
Sebagai gantinya saya meminta setiap tahap diverifikasi dengan unit test dan pengecekan di
browser sebelum di-commit, dan saya yang menjalankan push, merge, dan deploy.

Saya juga mengarahkan desain fiturnya sendiri. Setelah melihat bahwa siapa pun bisa
menambah dan menghapus konten di PWS, saya meminta agar pengunjung hanya melihat data,
sedangkan tombol tambah, ubah, dan hapus hanya bisa dipakai oleh saya. Permintaan ini yang
menjadi fitur mode pemilik.

#### Bagian yang dikerjakan AI

- Menulis kode Tutorial 03 (kecuali `base.html`, yang saya buat sendiri) dan Tugas 3:
  `forms.py`, view dan route untuk form, endpoint JSON, pencarian, hapus dengan dialog
  konfirmasi, ubah data, serta CSS tombol, form, dan dialog.
- Menemukan bahwa `settings.py` tidak pernah membaca variabel basis data, sehingga PWS
  selama ini memakai SQLite yang dibuat ulang setiap deploy, lalu mengubahnya agar memakai
  PostgreSQL saat `PRODUCTION=True`.
- Merancang dan menulis mode pemilik (`owner.py`, context processor, halaman `/owner/`,
  halaman 403) sesuai permintaan saya.
- Menulis 24 unit test baru, sehingga total menjadi 34 test.
- Memperbarui README dan menyusun draf bagian AI disclosure ini.

#### Bagian yang saya kerjakan sendiri

- Membuat branch Tutorial 03 dan `base.html`, lalu memutuskan menyerahkan sisa pengerjaan
  kepada AI karena tenggat.
- Menentukan perilaku mode pemilik: data tampil untuk semua orang, tetapi hanya saya yang
  boleh mengubahnya.
- Memeriksa Project Environment Variables di PWS, mengatur `OWNER_SECRET`, menjalankan push,
  merge, dan deploy, serta mengisi ulang data portofolio di PWS lewat form.
- Menulis jawaban pertanyaan reflektif Tugas 3.

#### Keterbatasan AI yang saya temukan

**1. AI tidak sengaja menghapus data asli saya.** Saat menguji fitur hapus, AI menjalankan
percobaan langsung ke basis data lokal saya dengan asumsi perubahannya bisa dibatalkan
lewat savepoint. Asumsi itu salah, karena shell Django berjalan dalam mode autocommit, dan
proyek RumputSehatEWS benar-benar terhapus. AI menyadarinya dari jumlah data yang berubah,
memulihkan data yang sama di urutan semula, dan sejak itu hanya menguji perubahan data di
basis data test Django. Pelajaran bagi saya: pengujian yang mengubah data tidak boleh
dijalankan ke basis data yang berisi data asli.

**2. Masalah konfigurasi yang lebih besar baru terlihat ketika dicari alasannya.** Selama
Tugas 1 dan Tugas 2, tidak ada yang menyadari bahwa PWS tidak memakai PostgreSQL. Hal ini
baru ketahuan ketika saya meminta agar data tampil permanen di PWS, dan AI membaca ulang
`settings.py` untuk mencari tahu kenapa data di sana selalu kosong.
