# 📰 Portal Berita

Portal berita statis yang di-deploy otomatis ke **GitHub Pages** menggunakan **GitHub Actions**.

---

## 🗂️ Struktur Folder

```
portal-berita/
├── .github/
│   └── workflows/
│       └── deploy.yml       ← GitHub Actions (otomatis)
├── index.html               ← Halaman listview berita
├── generate_list.py         ← Generate file-list.json
├── news_editor.py           ← Aplikasi desktop pembuat berita
├── file-list.json           ← Daftar berita (auto-generate)
└── berita-*.html            ← File berita kamu
```

---

## 🚀 Cara Setup (Sekali Saja)

### 1. Buat repo baru di GitHub
Buka https://github.com/new, buat repo nama misalnya `portal-berita`. Centang **Public**.

### 2. Upload semua file ke repo

```bash
git init
git add .
git commit -m "first commit"
git branch -M main
git remote add origin https://github.com/USERNAME/portal-berita.git
git push -u origin main
```

### 3. Aktifkan GitHub Pages
1. Buka repo → **Settings** → **Pages**
2. Source: **"Deploy from a branch"**
3. Branch: **gh-pages**, folder: **/ (root)**
4. Klik **Save**

> Branch `gh-pages` dibuat otomatis oleh Actions saat pertama push.

### 4. Tunggu Actions selesai
Buka tab **Actions** → tunggu workflow hijau ✅

Portal kamu live di:
```
https://USERNAME.github.io/portal-berita/
```

---

## ✍️ Cara Tambah Berita Baru

1. Jalankan `news_editor.py`, buat berita, simpan `.html` ke folder repo
2. Push ke GitHub:
   ```bash
   git add .
   git commit -m "tambah berita baru"
   git push
   ```
3. Actions otomatis generate `file-list.json` dan deploy ulang ✅

---

## 🛠️ Jalankan Lokal

```bash
python generate_list.py
python -m http.server 8000
# buka http://localhost:8000
```

---

## ❓ Troubleshooting

| Masalah | Solusi |
|---|---|
| Actions gagal | Tab Actions → klik workflow merah → lihat log |
| Halaman tidak update | Tunggu 1-2 menit atau Ctrl+Shift+R |
| Berita tidak muncul | Cek isi `file-list.json` |
