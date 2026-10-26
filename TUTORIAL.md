# 📖 Tutorial & Panduan Penggunaan Web Laboratorium Peralatan Diagnostik

Panduan lengkap mengenai instalasi, konfigurasi database phpMyAdmin, menjalankan aplikasi, serta alur penggunaan fitur untuk Administrator dan Mahasiswa.

---

## 🛠️ 1. Kebutuhan Sistem & Teknologi

- **Bahasa Pemrograman:** Python 3.10+ (Teruji di Python 3.13)
- **Framework Web:** Flask 3.1
- **Database:** MySQL / MariaDB (Terhubung ke phpMyAdmin)
- **Library Pendukung:**
  - `PyMySQL`: Driver koneksi database MySQL tanpa kompilasi C
  - `Pillow`: Validasi dan penanganan berkas gambar
  - `python-dotenv`: Pengelolaan konfigurasi environment
  - `Werkzeug`: Hashing password aman (*scrypt*)

---

## 🚀 2. Panduan Instalasi & Persiapan Proyek

### Langkah 1: Buat dan Aktifkan Virtual Environment
Jalankan perintah berikut di terminal pada folder proyek:
```bash
# Membuat environment python
python3 -m venv .venv

# Mengaktifkan environment (macOS/Linux)
source .venv/bin/activate

# Mengaktifkan environment (Windows)
# .venv\Scripts\activate
```

### Langkah 2: Pasang Ketergantungan Paket
```bash
pip install -r requirements.txt
```

### Langkah 3: Konfigurasi Berkas `.env`
Pastikan berkas `.env` ada di root direktori dengan isi sesuai konfigurasi MySQL phpMyAdmin Anda:
```env
SECRET_KEY=katalog_secret_key_super_secure_2026
DB_HOST=127.0.0.1
DB_PORT=3306
DB_USER=root
DB_PASSWORD=
DB_NAME=db_katalog
FLASK_ENV=development
```
> *Catatan:* Jika Anda menggunakan XAMPP/MAMP tanpa password root, biarkan `DB_PASSWORD` kosong seperti di atas.

---

## 🗄️ 3. Konfigurasi Database & phpMyAdmin

Anda dapat menyiapkan database dengan salah satu dari dua cara berikut:

### Cara A: Otomatis via Terminal (Direkomendasikan)
Cukup jalankan script inisialisasi:
```bash
source .venv/bin/activate
python init_db.py
```
Script ini akan secara otomatis:
1. Membuat database `db_katalog` jika belum ada di MySQL.
2. Mengeksekusi tabel `users`, `mahasiswa`, `katalog`, dan `katalog_gambar`.
3. Menambahkan akun default Admin & Mahasiswa.
4. Memastikan tabel katalog dan berkas unggahan gambar dalam kondisi bersih/kosong (0 data), siap digunakan untuk input data baru oleh Administrator.

### Cara B: Manual via Antarmuka Web phpMyAdmin
1. Buka browser dan akses phpMyAdmin (biasanya di `http://localhost/phpmyadmin` atau `http://127.0.0.1:8080`).
2. Buat database baru bernama `db_katalog`.
3. Pilih database `db_katalog`, lalu buka menu **Import**.
4. Pilih berkas [schema.sql](file:///Users/agung_kesuma/katalog/schema.sql) dan klik **Go / Kirim**.

---

## 🔑 4. Informasi Akun Pengujian (Kredensial Default)

Aplikasi telah dilengkapi dengan akun siap pakai untuk pengujian:

| Role | Tipe Login | Username / NIM | Password | Hak Akses |
| :--- | :--- | :--- | :--- | :--- |
| **Administrator** | Username | `admin` | `admin123` | Akses Penuh: Kelola Katalog (CRUD, Thumbnail), Kelola Mahasiswa (CRUD) |
| **Mahasiswa 1** | NIM | `2024001` | `mhs123` | Melihat Daftar Katalog, Pencarian, & Detail Item |
| **Mahasiswa 2** | NIM | `2024002` | `mhs123` | Melihat Daftar Katalog, Pencarian, & Detail Item |

*(Tersedia tombol auto-fill pada halaman login untuk mengisi kredensial dengan satu klik)*

---

## 💻 5. Menjalankan Aplikasi

Jalankan server aplikasi Flask:
```bash
source .venv/bin/activate
python app.py
```
Buka peramban (browser) di alamat:
👉 **`http://127.0.0.1:5000`**

---

## 🌟 6. Panduan Fitur & Cara Penggunaan

### A. Halaman Login (`/login`)
- **Admin**: Masukkan `admin` pada kolom Username/NIM dan kata sandi `admin123`.
- **Mahasiswa**: Masukkan `2024001` pada kolom Username/NIM dan kata sandi `mhs123`.
- Terdapat ikon mata untuk melihat/sembunyikan password.

### B. Daftar Item Katalog (`/katalog`)
- Dapat diakses oleh **Admin** maupun **Mahasiswa**.
- Dilengkapi **kolom pencarian cerdas** berdasarkan judul atau deskripsi item.
- Setiap kartu menampilkan:
  - Foto **Thumbnail Utama** yang dipilih admin dengan format pas (*contain fit*). Gambar, logo, maupun spanduk beresolusi apa pun akan tampil utuh dan simetris di dalam bingkai tanpa terpotong (*no crop*).
  - Judul dan cuplikan deskripsi item secara bersih dan minimalis tanpa lencana jumlah foto.
  - **Navigasi Langsung Sekali Klik:** Pengguna tidak perlu mencari atau menekan tombol khusus; cukup **klik langsung di mana saja pada kartu item** tersebut untuk langsung membuka halaman detail lengkapnya.
  - Untuk Administrator: Terdapat tombol cepat **Edit** dan **Hapus** pada kartu tanpa memicu pembukaan detail (*stopPropagation*).

### C. Detail Item Katalog (`/katalog/<id>`)
- Menampilkan foto utama berukuran besar dengan mode pas proporsional (*contain*) berlatar kanvas gradien elegan, memastikan foto tidak terpotong.
- **Fitur Perbesar Gambar (Zoom Lightbox):** Klik langsung pada area foto utama (muncul tanda *🔍 Klik untuk perbesar*) untuk membuka tampilan gambar layar penuh (*fullscreen lightbox modal*) beresolusi tinggi dengan latar belakang gelap buram (*backdrop blur*).
- **Navigasi Gambar di Modal:**
  - Klik tombol panah kiri / kanan (atau tekan tombol panah keyboard `←` / `→`) untuk beralih antar foto aset.
  - Tekan tombol silang `&times;`, klik di luar area gambar, atau tekan tombol `Esc` pada keyboard untuk menutup tampilan perbesar.
- Menampilkan deretan thumbnail foto mini di bawahnya. Klik pada salah satu foto mini untuk mengganti tampilan foto utama secara instan.
- Informasi lengkap spesifikasi dan waktu registrasi aset.

### D. Input Item Katalog Baru (`/admin/katalog/create`) *(Khusus Admin)*
- **Judul**: Judul item/aset.
- **Deskripsi**: Deskripsi lengkap.
- **Unggah Foto (Min 1, Maks 5)**:
  - Klik atau seret file gambar ke kotak unggahan.
  - Pratinjau langsung muncul seketika di layar.
  - Setiap foto memiliki tombol **"Jadikan Thumbnail"**. Klik tombol ini pada foto yang ingin dijadikan gambar sampul utama. Foto thumbnail akan ditandai dengan border emas dan label bintang ⭐.
  - Terdapat tombol silang merah di sudut foto jika ingin membatalkan/menghapus foto sebelum disimpan.

### E. Edit Item Katalog (`/admin/katalog/<id>/edit`) *(Khusus Admin)*
- Mengubah judul dan deskripsi yang sudah ada.
- Menghapus foto lama dengan menekan tombol silang merah (status foto menjadi pudar dan siap dihapus saat form disimpan).
- Menambah foto baru hingga batas maksimal 5 foto.
- Mengubah pilihan foto thumbnail utama antara foto lama maupun foto yang baru diunggah.

### F. Kelola Mahasiswa (`/admin/mahasiswa`) *(Khusus Admin)*
- Melihat tabel seluruh mahasiswa terdaftar beserta NIM, Jurusan, Angkatan, dan Email.
- Fitur pencarian mahasiswa berdasarkan NIM, nama, atau jurusan.
- Menambah mahasiswa baru (`/admin/mahasiswa/create`): Membuat data profil sekaligus akun login pengguna baru.
- Mengedit mahasiswa (`/admin/mahasiswa/<id>/edit`): Mengubah data dan mereset kata sandi login jika diperlukan.
- Menghapus mahasiswa: Menghapus data identitas dan akun login secara permanen.

### G. Menu Dropdown Pengguna & Ubah Password (`/update-password`) *(Semua Pengguna)*
- **Menu Dropdown Terpadu:** Tombol ubah kata sandi dan logout kini terintegrasi rapi di dalam **menu dropdown pada nama akun pengguna** di pojok kanan atas navbar.
- Klik pada nama akun/badge Anda untuk membuka menu dropdown yang berisi:
  1. **🔑 Ubah Password:** Membuka form pembaruan kata sandi mandiri.
  2. **🚪 Logout Keluar:** Mengakhiri sesi dan keluar dari sistem secara aman.
- Input data yang dibutuhkan pada form Ubah Password:
  1. **Password Saat Ini:** Untuk memverifikasi keaslian pemilik akun sebelum perubahan disetujui.
  2. **Password Baru:** Kata sandi baru yang diinginkan (minimal 6 karakter).
  3. **Konfirmasi Password Baru:** Pengulangan kata sandi baru untuk mencegah kesalahan pengetikan (*typo*).
- Dilengkapi tombol ikon mata (👁️) di setiap kolom untuk melihat/menyembunyikan teks kata sandi.
- Setelah berhasil, pengguna dapat langsung menggunakan kata sandi baru tersebut pada sesi login berikutnya.

---

## 🛡️ 7. Kepatuhan Aturan & Keamanan

1. **Anti-Duplikasi Notifikasi:** Sistem pesan flash backend dan toast frontend memiliki proteksi `seenMessages` otomatis sehingga tidak akan ada notifikasi ganda yang muncul di layar.
2. **Keamanan Role-Based:** Pengguna dengan role Mahasiswa yang mencoba mengakses URL administratif (`/admin/...`) secara otomatis ditolak dan dialihkan dengan notifikasi peringatan.
3. **Penyimpanan Berkas Rapi:** Berkas gambar disimpan dengan penamaan unik UUID di `static/uploads/katalog/`, dan dihapus dari penyimpanan lokal ketika item atau foto bersangkutan dihapus dari database.

---

## 🌐 8. Panduan Deployment di Shared Hosting (cPanel / CloudLinux Passenger)

Aplikasi berbasis Flask ini dapat dijalankan pada layanan **Shared Hosting** yang menyediakan fitur **"Setup Python App"** (didukung oleh CloudLinux Phusion Passenger).

### Berkas Khusus Shared Hosting:
- Proyek telah dilengkapi berkas [passenger_wsgi.py](file:///Users/agung_kesuma/katalog/passenger_wsgi.py) di root direktori sebagai jembatan *entrypoint* antara web server Apache/LiteSpeed hosting dengan aplikasi Flask Anda.

---

### Langkah demi Langkah Deployment:

#### 1. Persiapan Database di cPanel
1. Masuk ke dashboard **cPanel** hosting Anda.
2. Buka menu **MySQL Database Wizard**:
   - Buat database baru (misal: `u1234567_db_katalog`).
   - Buat pengguna MySQL baru (misal: `u1234567_userkatalog`) dan password aman.
   - Tetapkan hak akses **All Privileges** pengguna ke database tersebut.
3. Buka menu **phpMyAdmin** di cPanel:
   - Pilih database yang baru dibuat.
   - Masuk ke tab **Import**, pilih berkas [schema.sql](file:///Users/agung_kesuma/katalog/schema.sql) dari komputer Anda, lalu klik **Go / Kirim** untuk membuat seluruh tabel.

#### 2. Konfigurasi "Setup Python App" di cPanel
1. Buka menu **Setup Python App** di cPanel.
2. Klik tombol **Create Application**:
   - **Python Version:** Pilih versi terbaru yang tersedia (disarankan `3.10`, `3.11`, atau `3.12`).
   - **Application root:** Tentukan path folder proyek Anda (misal: `katalog` atau `aplikasi_diagnostik`).
   - **Application URL:** Pilih domain atau subdomain Anda (misal: `diagnostik.domainanda.com`).
   - **Application startup file:** Ketik `passenger_wsgi.py`.
   - **Application Entry point:** Ketik `application`.
3. Klik tombol **CREATE** di pojok kanan atas.

#### 3. Mengunggah Berkas Proyek
1. Buka menu **File Manager** di cPanel.
2. Masuk ke folder *Application root* yang telah ditentukan (misal: `/home/username/katalog`).
3. Unggah seluruh berkas proyek Anda **kecuali** folder `.venv` dan folder `do_not_upload`:
   - `app.py`, `config.py`, `db.py`, `auth_helpers.py`, `init_db.py`, `passenger_wsgi.py`, `requirements.txt`
   - Folder `routes/`, `templates/`, `static/`
4. Buat berkas **`.env`** di folder root tersebut dan sesuaikan dengan kredensial database cPanel Anda:
   ```env
   SECRET_KEY=kunci_rahasia_produksi_yang_sangat_panjang_dan_acak_2026
   DB_HOST=localhost
   DB_PORT=3306
   DB_USER=u1234567_userkatalog
   DB_PASSWORD=PasswordDatabaseAndaYangAman!
   DB_NAME=u1234567_db_katalog
   FLASK_ENV=production
   ```

#### 4. Memasang Dependencies (Package Python)

Terdapat dua cara mudah untuk memasang package pada cPanel:

##### Cara 1: Langsung melalui Tombol di GUI cPanel (Paling Mudah & Rekomendasi)
1. Buka menu **Setup Python App** di cPanel dan klik aplikasi Anda.
2. Gulir ke bawah ke bagian **Configuration files**.
3. Di kotak teks input, ketik: `requirements.txt` lalu klik tombol **Add**.
4. Setelah muncul di daftar, klik tombol **Run Pip Install**.
5. Tunggu proses instalasi selesai (ditandai dengan notifikasi sukses berwarna hijau).

> ⚠️ **Jika Muncul Pesan Error:**
> `Error File (.../3.10/bin/pip): [Errno 2] No such file or directory: '.../bin/pip'`
> Ini terjadi karena virtual environment di CloudLinux cPanel belum terpasang binary `pip`.
> **Solusi Cepat:** Buka **Terminal** cPanel dan jalankan perintah berikut untuk menginstal `pip` ke virtualenv:
> ```bash
> # 1. Pasang pip ke dalam virtualenv aplikasi
> curl -sS https://bootstrap.pypa.io/get-pip.py | /home/agun9011/virtualenv/public_html/diagnostik.agungj.com/3.10/bin/python3
> 
> # 2. Pastikan symlink pip tersedia
> ln -s /home/agun9011/virtualenv/public_html/diagnostik.agungj.com/3.10/bin/pip3 /home/agun9011/virtualenv/public_html/diagnostik.agungj.com/3.10/bin/pip 2>/dev/null
> ```
> Setelah itu, Anda bisa klik ulang tombol **Run Pip Install** di cPanel GUI atau langsung instal via terminal.

##### Cara 2: Melalui Terminal cPanel
1. Buka menu **Terminal** di cPanel.
2. Jalankan perintah instalasi menggunakan binary Python lengkap virtualenv Anda:
   ```bash
   /home/agun9011/virtualenv/public_html/diagnostik.agungj.com/3.10/bin/python3 -m pip install -r /home/agun9011/public_html/diagnostik.agungj.com/requirements.txt
   ```
> 💡 **Solusi alternatif jika virtualenv rusak total:**
> Anda cukup hapus aplikasi dari **Setup Python App** (klik tombol tempat sampah), lalu buat ulang (*Create Application*) dengan memilih Python 3.10. cPanel akan men-generate ulang virtual environment yang bersih.

#### 5. Inisialisasi Akun Admin Awal di Server
Masih di jendela Terminal cPanel, jalankan:
```bash
/home/agun9011/virtualenv/public_html/diagnostik.agungj.com/3.10/bin/python3 init_db.py
```
> Perintah ini akan mendaftarkan akun default Admin (`admin` / `admin123`) serta akun mahasiswa awal ke database MySQL hosting Anda dengan tabel katalog tetap bersih (0 data).

> ⚠️ **Jika Muncul Error `OperationalError: (1044, "Access denied for user 'agun9011_...' to database 'db_katalog'")`:**
> 1. **Nama Database di `.env` Harus Pakai Prefix cPanel**:
>    Di cPanel shared hosting, nama database selalu diawali username cPanel.
>    Pastikan di file `.env` di server tertulis:
>    ```env
>    DB_NAME=agun9011_db_katalog   # (BUKAN db_katalog)
>    DB_USER=agun9011_db_katalog
>    ```
> 2. **Hubungkan User ke Database di cPanel**:
>    Buka **cPanel > MySQL Databases** -> scroll ke **Add User to Database** (Tambahkan Pengguna ke Basis Data):
>    - User: `agun9011_db_katalog`
>    - Database: `agun9011_db_katalog`
>    - Klik **Add**, centang kotak **ALL PRIVILEGES**, lalu klik **Make Changes**.
> 3. **Perbarui file `init_db.py` dan `schema.sql` di server**:
>    Pastikan file `init_db.py` dan `schema.sql` terbaru telah diunggah ke server (agar tidak mengeksekusi `CREATE DATABASE db_katalog` yang dilarang di shared hosting).

#### 6. Pengaturan Berkas Statis & Izin Folder
1. Pastikan folder `static/uploads/katalog/` memiliki izin akses tulis (*permission `755`*).
2. Jika server web Apache/LiteSpeed di cPanel membutuhkan *rewrite rule* untuk folder `static`, tambahkan kode berikut di berkas `.htaccess` di dalam `public_html` (atau folder subdomain Anda):
   ```apache
   RewriteEngine On
   RewriteRule ^static/(.*)$ /home/username/katalog/static/$1 [L]
   ```
   *(Sebagian besar hosting CloudLinux Passenger telah menangani berkas statis Flask secara otomatis).*

#### 7. Restart Aplikasi
1. Buka menu **Setup Python App** di cPanel.
2. Klik tombol **Restart** di samping nama aplikasi Anda.
3. Buka domain atau subdomain Anda di peramban web:
   👉 Aplikasi Laboratorium Peralatan Diagnostik Anda kini telah aktif (*Live*) di Shared Hosting!

