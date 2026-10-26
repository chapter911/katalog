# 📊 Flowchart Sistem Aplikasi Web Laboratorium Peralatan Diagnostik

Dokumen ini memuat diagram alur proses (*flowchart*) menyeluruh untuk aplikasi Web Laboratorium Peralatan Diagnostik berbasis Python Flask dan MySQL (phpMyAdmin), sesuai aturan pembaruan dokumentasi berkala.

---

## 1. Diagram Arsitektur & Hak Akses (Role-Based Access)

```mermaid
graph TD
    User([Pengguna / Tamu]) --> Landing[Akses Halaman Utama /]
    Landing --> AuthCheck{Apakah Sudah Login?}
    
    AuthCheck -- Belum --> LoginGate[Halaman Login /login]
    AuthCheck -- Sudah --> CheckRole{Cek Peran / Role}

    LoginGate --> SubmitLogin[Input Identifier + Password]
    SubmitLogin --> ValidCred{Kredensial Valid?}
    
    ValidCred -- Tidak --> ErrLogin[Tampilkan Peringatan Error<br/>Anti-Duplikasi Notifikasi] --> LoginGate
    ValidCred -- Ya --> SetSession[Simpan Session User & Role] --> CheckRole

    CheckRole -- Role: Mahasiswa --> MhsPortal[Area Mahasiswa]
    CheckRole -- Role: Admin --> AdminPortal[Area Administrator]

    subgraph "Hak Akses Mahasiswa"
        MhsPortal --> MhsKatalogList[Melihat Daftar Katalog]
        MhsPortal --> MhsKatalogSearch[Mencari Item Katalog]
        MhsKatalogList --> ClickCard[Klik Langsung Kartu Katalog]
        ClickCard --> MhsKatalogDetail[Melihat Detail Item & Galeri Foto]
        MhsPortal --> MhsUpdatePass[Ubah Password Akun Sendiri]
        MhsPortal -. Akses Ditolak .-> BlockAdmin[403 / Redirect ke Katalog]
    end

    subgraph "Hak Akses Administrator"
        AdminPortal --> AdminKatalog[Kelola Katalog Item]
        AdminPortal --> AdminMhs[Kelola Data Mahasiswa]
        
        AdminKatalog --> AddItem[Input Item Baru: 1-5 Foto + Pilih Thumbnail]
        AdminKatalog --> EditItem[Edit Item: Tambah/Hapus Foto, Ganti Thumbnail]
        AdminKatalog --> DelItem[Hapus Item & Berkas Fisik]

        AdminMhs --> ListMhs[Daftar & Pencarian Mahasiswa]
        AdminMhs --> AddMhs[Tambah Mahasiswa Baru dengan NIM]
        AdminMhs --> EditMhs[Ubah Profil / Reset Password Mahasiswa]
        AdminMhs --> DelMhs[Hapus Mahasiswa & Akun Pengguna]
    end
```

---

## 2. Alur Autentikasi Pengguna (Login & Logout)

```mermaid
flowchart TD
    Start([Mulai]) --> OpenLogin[Buka Halaman /login]
    OpenLogin --> FillForm[Isi Username/NIM & Password]
    FillForm --> ClickLogin[Klik Tombol Masuk]
    
    ClickLogin --> QueryDB[(Query users WHERE username = ? OR nim = ?)]
    QueryDB --> UserExists{Pengguna Ditemukan?}
    
    UserExists -- Tidak --> ShowErr[Flash Error: Username/NIM atau password salah]
    ShowErr --> OpenLogin
    
    UserExists -- Ya --> CheckHash{Verifikasi Password Hash}
    CheckHash -- Salah --> ShowErr
    CheckHash -- Benar --> CreateSession[Set session: user_id, user_role, user_name, identifier]
    
    CreateSession --> FlashWelcome[Flash: Selamat Datang!]
    FlashWelcome --> RedirectTarget{Ada Parameter ?next?}
    RedirectTarget -- Ya --> GoNext[Redirect ke Target URL]
    RedirectTarget -- Tidak --> GoKatalog[Redirect ke /katalog]

    GoKatalog --> LogoutAction{Pengguna Klik Logout?}
    GoNext --> LogoutAction
    LogoutAction -- Ya --> ClearSession[Hapus Session] --> FlashLogout[Flash: Berhasil Logout] --> OpenLogin
```

---

## 3. Alur Pengelolaan Katalog (Input/Edit 1-5 Gambar & Thumbnail)

> **Catatan Status Awal:** Saat aplikasi baru diinisialisasi atau dimulai, tabel `katalog` dan `katalog_gambar` berada dalam kondisi **benar-benar kosong (0 data)** dan direktori `static/uploads/katalog/` bersih, menampilkan pesan *"Katalog Masih Kosong"*.

```mermaid
flowchart TD
    InitCheck([Katalog Dibuka]) --> HasData{Ada Data Katalog?}
    HasData -- Tidak (0 Item) --> ShowEmpty[Tampilkan 'Katalog Masih Kosong' + Tombol Tambah Item Pertama]
    HasData -- Ada Item --> ShowGrid[Tampilkan Grid Kartu Katalog]

    ShowEmpty --> AdminInput([Admin Buka Form Tambah Katalog])
    AdminInput --> FormFill[Input Judul & Deskripsi]
    FormFill --> UploadPhotos[Pilih Berkas Foto: Dropzone / File Picker]
    
    UploadPhotos --> CheckFiles[Validasi File di Browser & Server]
    CheckFiles --> CountValid{Total Foto Antara 1 s/d 5?}
    
    CountValid -- Kurang dari 1 --> WarnMin[Peringatan: Minimal 1 foto wajib diunggah] --> UploadPhotos
    CountValid -- Lebih dari 5 --> WarnMax[Peringatan: Maksimal 5 foto diizinkan] --> UploadPhotos
    
    CountValid -- Valid --> SelectThumbnail[Klik 'Jadikan Thumbnail Utama' pada salah satu foto]
    SelectThumbnail --> SubmitForm[Klik Tombol Simpan]
    
    SubmitForm --> ServerProc[Server: Simpan File ke static/uploads/katalog/ dengan UUID unik]
    ServerProc --> InsertDB[(Insert/Update tabel katalog & tabel katalog_gambar)]
    InsertDB --> SetFlag[Tandai is_thumbnail = 1 untuk foto terpilih]
    SetFlag --> SuccessNotif[Tampilkan Notifikasi Berhasil]
    SuccessNotif --> RedirectDetail[Redirect ke Detail Item /katalog/:id]
    RedirectDetail --> End([Selesai])
```

---

## 4. Mekanisme Anti-Duplikasi Notifikasi (Rule #1)

```mermaid
flowchart LR
    EventTrigger[Event Aksi Backend / Flash] --> SessionFlash[Flask get_flashed_messages]
    SessionFlash --> RenderHTML[Render ke DOM Container #notification-wrapper]
    RenderHTML --> JSCheck[JavaScript: initNotifications]
    
    JSCheck --> LoopAlerts{Loop Tiap Alert}
    LoopAlerts --> CheckSet{Pernah Ditampilkan di Set seenMessages?}
    
    CheckSet -- Ya (Duplikat) --> RemoveDuplicate[Hapus Elemen dari DOM Segera]
    CheckSet -- Belum (Unik) --> AddSet[Tambahkan Teks ke seenMessages]
    
    AddSet --> AutoDismiss[Timer 5 Detik: Fade Out & Hapus]
    AddSet --> ManualClose[Klik Tombol Silang: Tutup Alert]
```

---

## 5. Alur Pemrosesan Tampilan Thumbnail & Pratinjau Gambar (Fit & Pas)

```mermaid
flowchart TD
    ImgData[Data Gambar Katalog: file_path] --> AspectBox[Container Box 16:10 / 4:3]
    AspectBox --> StyleGrad[Background Canvas: Radial Gradient #1e293b -> #0b1120]
    StyleGrad --> FitMode[Aturan object-fit: contain & padding]
    FitMode --> CheckRatio{Rasio Gambar}
    
    CheckRatio -- Banner / Melebar --> FitW[Ditampilkan 100% Lebar Proporsional, Tidak Terpotong Sisi]
    CheckRatio -- Logo / Kotak / Vertikal --> FitH[Ditampilkan 100% Tinggi Proporsional, Tidak Terpotong Atas/Bawah]
    
    FitW --> RenderDone[Tampilan Kartu Rapi & Bersih Tanpa Badge Jumlah Foto]
    FitH --> RenderDone
```

---

## 6. Alur Interaksi Klik Kartu Katalog (Direct Card Click Navigation)

```mermaid
flowchart TD
    UserHover[Pengguna Arahkan Kursor / Hover ke Kartu Katalog] --> VisualFeedback[Efek Naik & Border Glow + Kursor Pointer]
    VisualFeedback --> UserClick{Pengguna Melakukan Klik}
    
    UserClick -- Klik Tombol Edit / Hapus (Admin) --> ActionBtn[Jalankan Aksi Admin Tanpa Buka Detail: stopPropagation]
    UserClick -- Klik Area Kartu Mana Saja --> DirectNav[Navigasi Langsung ke /katalog/:id]
    
    DirectNav --> OpenDetail[Halaman Detail Terbuka Seketika]
```

---

## 7. Alur Pembaruan Kata Sandi Mandiri (Update Password Flow)

```mermaid
flowchart TD
    UserNav([Pengguna Klik Nama / Akun di Navbar]) --> DropdownMenu[Muncul Menu Dropdown: Ubah Password & Logout]
    DropdownMenu -- Pilih '🔑 Ubah Password' --> OpenForm[Buka Halaman /update-password]
    DropdownMenu -- Pilih '🚪 Logout' --> DoLogout[Hapus Session & Redirect ke Login]
    
    OpenForm --> InputFields[Input: Password Saat Ini, Password Baru & Konfirmasi]
    InputFields --> SubmitPass[Klik 'Simpan Password Baru']
    
    SubmitPass --> ValFields{Semua Field Terisi & Panjang Baru >= 6?}
    ValFields -- Tidak --> WarnField[Flash Error Validasi Input] --> OpenForm
    
    ValFields -- Ya --> MatchPass{Password Baru == Konfirmasi?}
    MatchPass -- Tidak Cocok --> WarnMismatch[Flash Error: Konfirmasi password tidak cocok] --> OpenForm
    
    MatchPass -- Cocok --> CheckCurrent[(Verifikasi Password Lama ke Database)]
    CheckCurrent --> CurrentValid{Password Lama Sesuai?}
    CurrentValid -- Salah --> WarnWrongOld[Flash Error: Password saat ini salah] --> OpenForm
    
    CurrentValid -- Benar --> HashNew[Generate Hash Baru dengan Werkzeug Scrypt]
    HashNew --> UpdateDB[(UPDATE users SET password_hash = ? WHERE id = ?)]
    UpdateDB --> FlashSuccess[Flash Sukses: Password berhasil diperbarui!]
    FlashSuccess --> RedirectHome[Redirect ke /katalog]
    RedirectHome --> SelesaiPass([Selesai])
```

---

## 8. Alur Pratinjau Perbesar Gambar (Lightbox Modal Image Zoom)

```mermaid
flowchart TD
    UserDetail[Pengguna Berada di Halaman Detail Item /katalog/:id] --> HoverImg[Arahkan Kursor ke Gambar Utama]
    HoverImg --> ShowZoomBadge[Muncul Badge '🔍 Klik untuk perbesar' & Kursor Zoom-In]
    ShowZoomBadge --> UserClickImg[Pengguna Klik Gambar Utama]
    
    UserClickImg --> OpenLightbox[Buka Lightbox Modal Fullscreen dengan Efek Blur Backdrop]
    OpenLightbox --> RenderLargeImg[Tampilkan Gambar dalam Resolusi Penuh & Pas Proporsional]
    
    RenderLargeImg --> UserActions{Interaksi Pengguna di Modal}
    
    UserActions -- Klik Tombol Silang (X) / Klik Backdrop / Tekan Esc --> CloseModal[Tutup Lightbox & Kembalikan Scroll Halaman]
    UserActions -- Klik Panah Kanan / Tekan ArrowRight --> NextImg[Beralih ke Foto Selanjutnya & Sinkronkan Thumbnail]
    UserActions -- Klik Panah Kiri / Tekan ArrowLeft --> PrevImg[Beralih ke Foto Sebelumnya & Sinkronkan Thumbnail]
    
    NextImg --> RenderLargeImg
    PrevImg --> RenderLargeImg
```

---

## 9. Diagram Alur Deployment Shared Hosting (cPanel Phusion Passenger)

```mermaid
flowchart TD
    StartDeploy([Mulai Deployment]) --> StepDB[1. cPanel: Buat Database & User via MySQL Wizard + All Privileges]
    StepDB --> StepImport[2. phpMyAdmin: Import schema.sql ke Database]
    StepImport --> StepPythonApp[3. Setup Python App: Tentukan Path & passenger_wsgi.py]
    StepPythonApp --> StepUpload[4. File Manager: Unggah Berkas Proyek]
    StepUpload --> StepEnv[5. Buat .env dengan DB_NAME & DB_USER lengkap pakai prefix cPanel]
    StepEnv --> StepDeps[6. Install Dependencies: via 'Run Pip Install' cPanel atau Terminal: bootstrap get-pip jika pip belum ada]
    StepDeps --> StepInit[7. Terminal: Jalankan init_db.py untuk Akun Default]
    StepInit --> StepRestart[8. Klik Restart Python App di cPanel]
    StepRestart --> Live([Aplikasi Live & Berjalan di Domain!])
```





