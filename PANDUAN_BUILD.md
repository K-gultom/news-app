# 🛠️ Panduan Build News Editor → Windows Installer

## Struktur folder yang dibutuhkan

```
📁 project/
 ├── news_editor.py          ← file utama aplikasi
 ├── generate_list.py        ← script portal berita
 ├── index.html              ← halaman portal berita
 ├── file-list.json          ← daftar berita
 ├── build.bat               ← script build otomatis
 ├── installer.iss           ← script Inno Setup
 ├── make_icon.py            ← buat icon .ico
 └── assets/
      └── icon.ico           ← icon aplikasi
```

---

## Langkah 1 — Install tools yang dibutuhkan

### A. Python 3.10+
Download dari https://python.org
> ⚠️ Centang "Add Python to PATH" saat install!

### B. Inno Setup 6
Download dari https://jrsoftware.org/isdl.php
Install seperti biasa, pilih lokasi default.

---

## Langkah 2 — Buat icon (sekali saja)

Buka Command Prompt di folder project, jalankan:
```
python make_icon.py
```
Akan membuat file `assets\icon.ico`.

> Atau ganti dengan icon .ico milikmu sendiri,
> simpan di `assets\icon.ico`

---

## Langkah 3 — Build .exe dengan PyInstaller

Double-click file `build.bat`
atau jalankan di Command Prompt:
```
build.bat
```

Proses ini akan:
1. Install PyInstaller otomatis
2. Compile news_editor.py → folder `dist\NewsEditor\`
3. Menyalin file pendukung ke folder dist

⏱️ Estimasi waktu: 1–3 menit

Hasil: `dist\NewsEditor\NewsEditor.exe`

---

## Langkah 4 — Buat Installer dengan Inno Setup

1. Buka **Inno Setup Compiler**
2. Klik **File → Open** → pilih `installer.iss`
3. Klik **Build → Compile** (atau tekan F9)

⏱️ Estimasi waktu: 30 detik – 2 menit

Hasil: `installer_output\NewsEditor_Setup_v3.0.exe`

---

## Langkah 5 — Distribusikan!

File `NewsEditor_Setup_v3.0.exe` siap dibagikan.
Pengguna cukup double-click → install → langsung bisa pakai.

---

## Troubleshooting

| Masalah | Solusi |
|---|---|
| `python tidak ditemukan` | Reinstall Python, centang "Add to PATH" |
| `ModuleNotFoundError: tkcalendar` | Jalankan: `pip install tkcalendar` |
| `ModuleNotFoundError: babel` | Jalankan: `pip install babel` |
| Icon tidak muncul | Pastikan `assets\icon.ico` ada, atau hapus baris `--icon` di build.bat |
| Antivirus memblokir .exe | False positive — wajar untuk exe hasil PyInstaller. Tambahkan ke whitelist. |
| Installer.iss error "file not found" | Pastikan sudah jalankan `build.bat` dulu sebelum compile Inno Setup |

---

## Ukuran output yang diharapkan

| File | Estimasi ukuran |
|---|---|
| `dist\NewsEditor\` (folder) | ~35–60 MB |
| `NewsEditor_Setup_v3.0.exe` | ~20–35 MB (setelah kompresi) |

---

## Update versi

Saat ada update `news_editor.py`:
1. Jalankan `build.bat` lagi
2. Compile ulang `installer.iss` di Inno Setup
3. Ganti nomor versi di `installer.iss` baris `#define AppVersion`
