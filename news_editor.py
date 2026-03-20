# ──────────────────────────────────────────────────────────────
#  Auto-install tkcalendar jika belum ada
# ──────────────────────────────────────────────────────────────
import sys, subprocess

def _ensure(pkg, import_name=None):
    import_name = import_name or pkg
    try:
        __import__(import_name)
    except ImportError:
        print(f"[News Editor] Menginstall {pkg} ...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", pkg],
                              stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

_ensure("tkcalendar")

# ──────────────────────────────────────────────────────────────
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkcalendar import Calendar
import datetime
import os

BG       = "#F5F6FA"
CARD     = "#FFFFFF"
ACCENT   = "#2563EB"
ACCENT_H = "#1D4ED8"
TEXT     = "#1E293B"
MUTED    = "#64748B"
BORDER   = "#E2E8F0"
SUCCESS  = "#16A34A"
WARNING  = "#D97706"

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="id">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <meta name="judul"   content="{judul}"/>
  <meta name="author"  content="{author}"/>
  <meta name="tanggal" content="{tanggal_fmt}"/>
  <title>{judul}</title>
  <style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: 'Georgia', serif;
      background: #F8FAFC;
      color: #1E293B;
      line-height: 1.7;
    }}
    header {{
      background: #1E3A5F;
      color: white;
      padding: 16px 0;
      text-align: center;
      font-size: 13px;
      letter-spacing: 2px;
      text-transform: uppercase;
    }}
    header a {{
      color: rgba(255,255,255,0.6);
      text-decoration: none;
      font-size: 12px;
      margin-left: 20px;
    }}
    header a:hover {{ color: white; }}
    .container {{
      max-width: 760px;
      margin: 48px auto;
      padding: 0 24px;
    }}
    .category {{
      font-size: 12px;
      font-weight: 700;
      color: #2563EB;
      text-transform: uppercase;
      letter-spacing: 1.5px;
      margin-bottom: 12px;
    }}
    h1 {{
      font-size: 2rem;
      font-weight: 700;
      color: #0F172A;
      line-height: 1.3;
      margin-bottom: 16px;
    }}
    .meta {{
      display: flex;
      gap: 20px;
      font-size: 13px;
      color: #64748B;
      border-top: 1px solid #E2E8F0;
      border-bottom: 1px solid #E2E8F0;
      padding: 10px 0;
      margin-bottom: 28px;
    }}
    .body-text {{
      font-size: 1.05rem;
      color: #334155;
      white-space: pre-wrap;
    }}
    footer {{
      text-align: center;
      font-size: 12px;
      color: #94A3B8;
      margin: 60px 0 24px;
    }}
  </style>
</head>
<body>
  <header>
    Portal Berita
    <a href="index.html">← Kembali ke daftar berita</a>
  </header>
  <div class="container">
    <div class="category">Berita</div>
    <h1>{judul}</h1>
    <div class="meta">
      <span>✍ {author}</span>
      <span>📅 {tanggal_fmt}</span>
    </div>
    <div class="body-text">{isi}</div>
  </div>
  <footer>© {tahun} Portal Berita — Dibuat dengan News Editor</footer>
</body>
</html>
"""

BULAN = ["","Januari","Februari","Maret","April","Mei","Juni",
         "Juli","Agustus","September","Oktober","November","Desember"]

def format_tanggal(dt: datetime.date) -> str:
    return f"{dt.day} {BULAN[dt.month]} {dt.year}"


# ──────────────────────────────────────────────────────────────
#  Widget kalender popup
# ──────────────────────────────────────────────────────────────
class DatePickerPopup(tk.Toplevel):
    """Popup kalender. Memanggil callback(date) saat tanggal dipilih."""

    def __init__(self, parent, current_date: datetime.date, callback):
        super().__init__(parent)
        self.title("Pilih Tanggal")
        self.resizable(False, False)
        self.configure(bg=BG)
        self.grab_set()
        self.callback = callback

        # Judul
        tk.Label(self, text="📅  Pilih Tanggal Berita",
                 bg=BG, fg=TEXT, font=("Segoe UI", 11, "bold"),
                 anchor="w").pack(fill="x", padx=16, pady=(14, 6))

        # Kalender
        cal = Calendar(
            self,
            selectmode="day",
            year=current_date.year,
            month=current_date.month,
            day=current_date.day,
            date_pattern="dd/mm/yyyy",
            locale="id_ID",
            background="#1E3A5F",
            foreground="white",
            headersbackground="#163251",
            headersforeground="white",
            selectbackground=ACCENT,
            selectforeground="white",
            normalbackground=CARD,
            normalforeground=TEXT,
            weekendbackground="#F8FAFC",
            weekendforeground="#DC2626",
            othermonthbackground="#F1F5F9",
            othermonthforeground="#94A3B8",
            bordercolor=BORDER,
            font=("Segoe UI", 10),
        )
        cal.pack(padx=16, pady=4)

        # Tombol
        btn_row = tk.Frame(self, bg=BG)
        btn_row.pack(fill="x", padx=16, pady=12)

        tk.Button(btn_row, text="Batal",
                  command=self.destroy,
                  bg=BORDER, fg=MUTED, relief="flat",
                  font=("Segoe UI", 10), padx=14, pady=6,
                  cursor="hand2").pack(side="left")

        tk.Button(btn_row, text="✔  Pilih Tanggal",
                  command=lambda: self._pick(cal),
                  bg=ACCENT, fg="white", relief="flat",
                  activebackground=ACCENT_H, activeforeground="white",
                  font=("Segoe UI", 10, "bold"), padx=14, pady=6,
                  cursor="hand2").pack(side="right")

        # Tengahkan popup
        self.update_idletasks()
        px = parent.winfo_rootx() + (parent.winfo_width()  - self.winfo_width())  // 2
        py = parent.winfo_rooty() + (parent.winfo_height() - self.winfo_height()) // 2
        self.geometry(f"+{px}+{py}")

    def _pick(self, cal):
        raw = cal.get_date()          # "DD/MM/YYYY"
        d, m, y = raw.split("/")
        picked = datetime.date(int(y), int(m), int(d))
        self.destroy()
        self.callback(picked)


# ──────────────────────────────────────────────────────────────
#  Aplikasi utama
# ──────────────────────────────────────────────────────────────
class NewsEditor(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("News Editor")
        self.geometry("720x660")
        self.resizable(True, True)
        self.configure(bg=BG)
        self.minsize(600, 560)
        self._selected_date = datetime.date.today()
        self._build_ui()

    # ── UI ────────────────────────────────────────────────────
    def _build_ui(self):
        hbar = tk.Frame(self, bg=ACCENT, height=52)
        hbar.pack(fill="x")
        hbar.pack_propagate(False)
        tk.Label(hbar, text="📰  News Editor", bg=ACCENT, fg="white",
                 font=("Segoe UI", 15, "bold")).pack(side="left", padx=20)

        canvas = tk.Canvas(self, bg=BG, highlightthickness=0)
        sb = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        canvas.pack(fill="both", expand=True)

        self.body = tk.Frame(canvas, bg=BG)
        win_id = canvas.create_window((0, 0), window=self.body, anchor="nw")

        def _resize(e): canvas.itemconfig(win_id, width=e.width)
        canvas.bind("<Configure>", _resize)
        self.body.bind("<Configure>", lambda e: canvas.configure(
            scrollregion=canvas.bbox("all")))
        canvas.bind_all("<MouseWheel>",
            lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"))

        pad = 28
        self._field("Judul Berita *", "entry_judul", pad)
        self._field("Nama Author *",  "entry_author", pad)
        self._date_field(pad)
        self._field("Isi Berita *",   "text_isi", pad, is_text=True)

        # Auto-generate toggle
        self.auto_gen = tk.BooleanVar(value=True)
        ag_frame = tk.Frame(self.body, bg=BG)
        ag_frame.pack(fill="x", padx=pad, pady=(12, 0))
        tk.Checkbutton(ag_frame,
                       text="Otomatis perbarui file-list.json setelah simpan",
                       variable=self.auto_gen, bg=BG, fg=MUTED,
                       activebackground=BG, selectcolor=CARD,
                       font=("Segoe UI", 10)).pack(anchor="w")

        # Tombol
        btn_row = tk.Frame(self.body, bg=BG)
        btn_row.pack(fill="x", padx=pad, pady=(16, 20))
        self._btn(btn_row, "🗑  Bersihkan",
                  self._clear, BORDER, MUTED).pack(side="left")
        self._btn(btn_row, "☁  Sync Server",
                  self._sync_server, "#0F766E", "white").pack(side="right", padx=(8, 0))
        self._btn(btn_row, "💾  Simpan Berita",
                  self._save, ACCENT, "white", bold=True).pack(side="right")

        self.status = tk.Label(self, text="Siap.", bg=BORDER, fg=MUTED,
                               font=("Segoe UI", 9), anchor="w", padx=12)
        self.status.pack(fill="x", side="bottom")

    def _field(self, label, attr, pad, is_text=False):
        frame = tk.Frame(self.body, bg=BG)
        frame.pack(fill="x", padx=pad, pady=(14, 0))
        tk.Label(frame, text=label, bg=BG, fg=MUTED,
                 font=("Segoe UI", 10)).pack(anchor="w")
        wrapper = tk.Frame(frame, bg=BORDER, bd=0)
        wrapper.pack(fill="x", pady=4)
        if is_text:
            widget = tk.Text(wrapper, height=9, font=("Segoe UI", 11),
                             bg=CARD, fg=TEXT, relief="flat", bd=8,
                             wrap="word", insertbackground=ACCENT)
            widget.pack(fill="both", expand=True)
        else:
            widget = tk.Entry(wrapper, font=("Segoe UI", 11),
                              bg=CARD, fg=TEXT, relief="flat", bd=8,
                              insertbackground=ACCENT)
            widget.pack(fill="x")
        setattr(self, attr, widget)

    def _date_field(self, pad):
        """Field tanggal dengan tombol kalender."""
        frame = tk.Frame(self.body, bg=BG)
        frame.pack(fill="x", padx=pad, pady=(14, 0))
        tk.Label(frame, text="Tanggal Berita *", bg=BG, fg=MUTED,
                 font=("Segoe UI", 10)).pack(anchor="w")

        row = tk.Frame(frame, bg=BG)
        row.pack(fill="x", pady=4)

        # Tampilan tanggal (read-only)
        display_wrap = tk.Frame(row, bg=BORDER)
        display_wrap.pack(side="left", fill="x", expand=True)
        self.lbl_tanggal = tk.Label(
            display_wrap,
            text=format_tanggal(self._selected_date),
            bg=CARD, fg=TEXT,
            font=("Segoe UI", 11),
            anchor="w", padx=10, pady=9)
        self.lbl_tanggal.pack(fill="x")

        # Tombol buka kalender
        tk.Button(row, text="📅  Pilih",
                  command=self._open_calendar,
                  bg=ACCENT, fg="white",
                  activebackground=ACCENT_H, activeforeground="white",
                  relief="flat", bd=0,
                  font=("Segoe UI", 10), padx=14, pady=8,
                  cursor="hand2").pack(side="left", padx=(8, 0))

    def _open_calendar(self):
        DatePickerPopup(self, self._selected_date, self._on_date_selected)

    def _on_date_selected(self, date: datetime.date):
        self._selected_date = date
        self.lbl_tanggal.config(text=format_tanggal(date))

    def _btn(self, parent, text, cmd, bg, fg, bold=False):
        return tk.Button(parent, text=text, command=cmd,
                         bg=bg, fg=fg,
                         activebackground=ACCENT_H, activeforeground="white",
                         relief="flat", bd=0,
                         font=("Segoe UI", 10, "bold" if bold else "normal"),
                         padx=18, pady=8, cursor="hand2")

    # ── Logika ────────────────────────────────────────────────
    def _get_values(self):
        judul  = self.entry_judul.get().strip()
        author = self.entry_author.get().strip()
        isi    = self.text_isi.get("1.0", "end").strip()
        return judul, author, self._selected_date, isi

    def _validate(self, judul, author, isi):
        for val, name in [(judul,"Judul"),(author,"Author"),(isi,"Isi berita")]:
            if not val:
                messagebox.showwarning("Peringatan", f"{name} tidak boleh kosong.")
                return False
        return True

    def _reset_form(self):
        for w in [self.entry_judul, self.entry_author]:
            w.delete(0, "end")
        self._selected_date = datetime.date.today()
        self.lbl_tanggal.config(text=format_tanggal(self._selected_date))
        self.text_isi.delete("1.0", "end")

    # ── Simpan ────────────────────────────────────────────────
    def _save(self):
        judul, author, tanggal, isi = self._get_values()
        if not self._validate(judul, author, isi):
            return

        path = filedialog.asksaveasfilename(
            defaultextension=".html",
            filetypes=[("HTML file", "*.html")],
            initialfile=self._safe_name(judul) + ".html",
            title="Simpan Berita sebagai HTML")
        if not path:
            return

        self._write_html(path, judul, author, tanggal, isi)
        saved_folder = os.path.dirname(path)
        msg = f"✅  Disimpan: {os.path.basename(path)}"

        if self.auto_gen.get():
            gen_script = os.path.join(saved_folder, "generate_list.py")
            if os.path.isfile(gen_script):
                try:
                    subprocess.run([sys.executable, gen_script],
                                   cwd=saved_folder, check=True,
                                   capture_output=True)
                    msg += "  |  📋 file-list.json diperbarui"
                except Exception as e:
                    self._set_status(f"⚠️  file-list.json gagal: {e}", WARNING)
                    return
            else:
                msg += "  |  ℹ️  generate_list.py tidak ditemukan"

        self._set_status(msg, SUCCESS)
        self._reset_form()

    def _write_html(self, path, judul, author, tanggal: datetime.date, isi):
        tgl_fmt = format_tanggal(tanggal)
        html = HTML_TEMPLATE.format(
            judul=judul, author=author, tanggal_fmt=tgl_fmt,
            isi=isi.replace("<","&lt;").replace(">","&gt;"),
            tahun=datetime.date.today().year)
        with open(path, "w", encoding="utf-8") as f:
            f.write(html)

    # ── Sync Server ───────────────────────────────────────────
    def _sync_server(self):
        folder = filedialog.askdirectory(title="Pilih folder repo Git untuk di-sync")
        if not folder:
            return
        if not os.path.isdir(os.path.join(folder, ".git")):
            messagebox.showerror("Bukan Git Repo",
                f"Folder ini bukan repositori Git:\n{folder}\n\n"
                "Pastikan folder sudah di-init dengan git.")
            return

        tanggal_commit = datetime.datetime.now().strftime("%d %B %Y %H:%M")
        commit_msg = f"commit berita terbaru {tanggal_commit}"
        self._run_git_window(folder, commit_msg)

    def _run_git_window(self, folder, commit_msg):
        win = tk.Toplevel(self)
        win.title("Sync Server")
        win.geometry("600x440")
        win.configure(bg=BG)
        win.resizable(True, True)
        win.grab_set()

        tk.Label(win, text="☁  Sync Server", bg=BG, fg=TEXT,
                 font=("Segoe UI", 13, "bold"), anchor="w").pack(
                     fill="x", padx=20, pady=(16, 2))
        tk.Label(win, text=folder, bg=BG, fg=MUTED,
                 font=("Segoe UI", 9), anchor="w").pack(
                     fill="x", padx=20, pady=(0, 10))

        log_frame = tk.Frame(win, bg="#0F172A")
        log_frame.pack(fill="both", expand=True, padx=20)

        log = tk.Text(log_frame, bg="#0F172A", fg="#94A3B8",
                      font=("Consolas", 10), relief="flat",
                      bd=10, state="disabled", wrap="word")
        log_sb = ttk.Scrollbar(log_frame, command=log.yview)
        log.configure(yscrollcommand=log_sb.set)
        log_sb.pack(side="right", fill="y")
        log.pack(fill="both", expand=True)

        log.tag_config("cmd",    foreground="#60A5FA")
        log.tag_config("ok",     foreground="#4ADE80")
        log.tag_config("warn",   foreground="#FCD34D")
        log.tag_config("err",    foreground="#F87171")
        log.tag_config("output", foreground="#CBD5E1")

        countdown_lbl = tk.Label(win, text="", bg=BG, fg=MUTED,
                                 font=("Segoe UI", 9))
        countdown_lbl.pack(pady=(8, 0))

        close_btn = tk.Button(win, text="Tutup", state="disabled",
                              bg=BORDER, fg=MUTED, relief="flat",
                              font=("Segoe UI", 10), padx=16, pady=7,
                              cursor="hand2", command=win.destroy)
        close_btn.pack(pady=(4, 12))

        def append(text, tag="output"):
            log.configure(state="normal")
            log.insert("end", text, tag)
            log.see("end")
            log.configure(state="disabled")
            win.update()

        def run(cmd_label, cmd, allow_rc1=False):
            """Jalankan satu perintah git. Kembalikan (success, returncode)."""
            append(f"\n$ {cmd_label}\n", "cmd")
            try:
                result = subprocess.run(cmd, cwd=folder,
                                        stdout=subprocess.PIPE,
                                        stderr=subprocess.STDOUT,
                                        text=True)
                if result.stdout.strip():
                    append(result.stdout.strip() + "\n", "output")
                if result.returncode == 0:
                    append("✔  OK\n", "ok")
                    return True, 0
                elif allow_rc1 and result.returncode == 1:
                    append("ℹ  Tidak ada perubahan untuk di-commit.\n", "warn")
                    return True, 1
                else:
                    append(f"✖  Gagal (exit {result.returncode})\n", "err")
                    return False, result.returncode
            except FileNotFoundError:
                append("✖  Git tidak ditemukan. Pastikan Git terinstall dan ada di PATH.\n", "err")
                return False, -1
            except Exception as e:
                append(f"✖  Error: {e}\n", "err")
                return False, -1

        def has_conflict(folder):
            """Cek apakah ada file yang sedang konflik."""
            result = subprocess.run(["git", "diff", "--name-only", "--diff-filter=U"],
                                    cwd=folder, stdout=subprocess.PIPE,
                                    stderr=subprocess.DEVNULL, text=True)
            return result.stdout.strip()

        def run_all():
            # ── Tahap 1: simpan perubahan lokal dulu ──
            append("\n─── Tahap 1: Simpan perubahan lokal ───\n", "cmd")
            ok, _ = run("git add .", ["git", "add", "."])
            if not ok: return _finish(False)

            ok, rc = run(f'git commit -m "{commit_msg}"',
                         ["git", "commit", "-m", commit_msg], allow_rc1=True)
            if not ok: return _finish(False)

            # ── Tahap 2: pull dari remote ──
            append("\n─── Tahap 2: Pull dari server ───\n", "cmd")
            ok, _ = run("git pull", ["git", "pull"])

            if not ok:
                # Cek apakah penyebabnya adalah merge conflict
                konflik = has_conflict(folder)
                if konflik:
                    append(f"\n⚠️  Conflict terdeteksi pada file:\n{konflik}\n", "warn")
                    append("→  Menyelesaikan conflict otomatis (ambil versi lokal)...\n", "warn")

                    # Ambil versi lokal untuk semua file yang konflik
                    for f in konflik.splitlines():
                        f = f.strip()
                        if f:
                            ok2, _ = run(f"git checkout --ours {f}",
                                         ["git", "checkout", "--ours", f])
                            if not ok2: return _finish(False)

                    # Add ulang file yang sudah di-resolve
                    ok, _ = run("git add .", ["git", "add", "."])
                    if not ok: return _finish(False)

                    # Commit hasil merge
                    ok, _ = run(f'git commit -m "merge: resolve conflict {commit_msg}"',
                                ["git", "commit", "-m",
                                 f"merge: resolve conflict {commit_msg}"], allow_rc1=True)
                    if not ok: return _finish(False)
                else:
                    return _finish(False)

            # ── Tahap 3: push ke remote ──
            append("\n─── Tahap 3: Push ke server ───\n", "cmd")
            ok, _ = run("git push", ["git", "push"])
            if not ok: return _finish(False)

            _finish(True)

        def _finish(success):
            if success:
                append("\n✅  Sync selesai! Semua perubahan berhasil dipush.\n", "ok")
                self._set_status("✅  Sync server selesai.", SUCCESS)

                # Countdown 3 detik lalu tutup otomatis
                def _tick(n):
                    if not win.winfo_exists():
                        return
                    if n <= 0:
                        win.destroy()
                    else:
                        countdown_lbl.config(text=f"Window akan tertutup dalam {n} detik...")
                        win.after(1000, lambda: _tick(n - 1))
                _tick(3)
            else:
                append("\n⚠️  Sync berhenti karena ada error. Periksa log di atas.\n", "err")
                self._set_status("⚠️  Sync server gagal. Lihat log.", WARNING)
                # Biarkan terbuka, aktifkan tombol Tutup
                close_btn.configure(state="normal", bg=ACCENT, fg="white",
                                    activebackground=ACCENT_H, activeforeground="white")

        win.after(150, run_all)

    # ── Bersihkan manual ──────────────────────────────────────
    def _clear(self):
        if messagebox.askyesno("Bersihkan Form",
                               "Yakin ingin mengosongkan semua field?"):
            self._reset_form()
            self._set_status("Form dikosongkan.", MUTED)

    # ── Helpers ───────────────────────────────────────────────
    def _safe_name(self, name):
        for ch in r'\/:*?"<>|':
            name = name.replace(ch, "_")
        return name[:60]

    def _set_status(self, msg, color=MUTED):
        self.status.config(text=msg, fg=color)


if __name__ == "__main__":
    NewsEditor().mainloop()