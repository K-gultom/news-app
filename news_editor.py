import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import datetime
import os
import subprocess
import sys

BG        = "#F5F6FA"
CARD      = "#FFFFFF"
ACCENT    = "#2563EB"
ACCENT_H  = "#1D4ED8"
TEXT      = "#1E293B"
MUTED     = "#64748B"
BORDER    = "#E2E8F0"
SUCCESS   = "#16A34A"

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

def format_tanggal(dt_str):
    try:
        dt = datetime.datetime.strptime(dt_str, "%d/%m/%Y")
        bulan = ["","Januari","Februari","Maret","April","Mei","Juni",
                 "Juli","Agustus","September","Oktober","November","Desember"]
        return f"{dt.day} {bulan[dt.month]} {dt.year}"
    except:
        return dt_str


class NewsEditor(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("News Editor")
        self.geometry("720x720")
        self.resizable(True, True)
        self.configure(bg=BG)
        self.minsize(600, 600)
        self._build_ui()

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
        canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"))

        pad = 28
        self._field("Judul Berita *",  "entry_judul",   pad)
        self._field("Nama Author *",   "entry_author",  pad)
        self._field("Tanggal Berita *","entry_tanggal", pad, placeholder="DD/MM/YYYY")
        self._field("Isi Berita *",    "text_isi",      pad, is_text=True)

        # ── Format ──
        fmt_frame = tk.Frame(self.body, bg=BG)
        fmt_frame.pack(fill="x", padx=pad, pady=(4, 0))
        tk.Label(fmt_frame, text="Format simpan", bg=BG, fg=MUTED,
                 font=("Segoe UI", 10)).pack(anchor="w")
        self.fmt_var = tk.StringVar(value="html")
        rf = tk.Frame(fmt_frame, bg=BG)
        rf.pack(anchor="w", pady=4)
        for val, lbl in [("html","HTML (.html)"),("txt","Teks biasa (.txt)"),("keduanya","Keduanya")]:
            tk.Radiobutton(rf, text=lbl, variable=self.fmt_var, value=val,
                           bg=BG, fg=TEXT, activebackground=BG,
                           font=("Segoe UI", 10), selectcolor=CARD).pack(side="left", padx=(0,16))

        # ── Auto-generate toggle ──
        self.auto_gen = tk.BooleanVar(value=True)
        ag_frame = tk.Frame(self.body, bg=BG)
        ag_frame.pack(fill="x", padx=pad, pady=(8, 0))
        tk.Checkbutton(ag_frame, text="Otomatis perbarui file-list.json (untuk index.html)",
                       variable=self.auto_gen, bg=BG, fg=MUTED,
                       activebackground=BG, selectcolor=CARD,
                       font=("Segoe UI", 10)).pack(anchor="w")

        # ── Tombol ──
        btn_row = tk.Frame(self.body, bg=BG)
        btn_row.pack(fill="x", padx=pad, pady=20)
        self._btn(btn_row, "🗑  Bersihkan",    self._clear, BORDER,  MUTED).pack(side="left")
        self._btn(btn_row, "💾  Simpan Berita", self._save,  ACCENT, "white", bold=True).pack(side="right")

        self.status = tk.Label(self, text="Siap.", bg=BORDER, fg=MUTED,
                               font=("Segoe UI", 9), anchor="w", padx=12)
        self.status.pack(fill="x", side="bottom")

        self.entry_tanggal.insert(0, datetime.date.today().strftime("%d/%m/%Y"))

    def _field(self, label, attr, pad, is_text=False, placeholder=""):
        frame = tk.Frame(self.body, bg=BG)
        frame.pack(fill="x", padx=pad, pady=(14, 0))
        tk.Label(frame, text=label, bg=BG, fg=MUTED, font=("Segoe UI", 10)).pack(anchor="w")
        wrapper = tk.Frame(frame, bg=BORDER, bd=0)
        wrapper.pack(fill="x", pady=4)
        if is_text:
            widget = tk.Text(wrapper, height=9, font=("Segoe UI", 11), bg=CARD, fg=TEXT,
                             relief="flat", bd=8, wrap="word", insertbackground=ACCENT)
            widget.pack(fill="both", expand=True)
        else:
            widget = tk.Entry(wrapper, font=("Segoe UI", 11), bg=CARD, fg=TEXT,
                              relief="flat", bd=8, insertbackground=ACCENT)
            widget.pack(fill="x")
            if placeholder:
                widget.insert(0, placeholder); widget.config(fg=MUTED)
                def on_fi(e, w=widget):
                    if w.get() == placeholder: w.delete(0,"end"); w.config(fg=TEXT)
                def on_fo(e, w=widget, p=placeholder):
                    if not w.get(): w.insert(0,p); w.config(fg=MUTED)
                widget.bind("<FocusIn>", on_fi); widget.bind("<FocusOut>", on_fo)
        setattr(self, attr, widget)

    def _btn(self, parent, text, cmd, bg, fg, bold=False):
        return tk.Button(parent, text=text, command=cmd, bg=bg, fg=fg,
                         activebackground=ACCENT_H, activeforeground="white",
                         relief="flat", bd=0,
                         font=("Segoe UI", 10, "bold" if bold else "normal"),
                         padx=18, pady=8, cursor="hand2")

    def _get_values(self):
        judul   = self.entry_judul.get().strip()
        author  = self.entry_author.get().strip()
        tanggal = self.entry_tanggal.get().strip()
        isi     = self.text_isi.get("1.0", "end").strip()
        if tanggal in ("DD/MM/YYYY", ""): tanggal = datetime.date.today().strftime("%d/%m/%Y")
        return judul, author, tanggal, isi

    def _validate(self, judul, author, tanggal, isi):
        for val, name in [(judul,"Judul"),(author,"Author"),(isi,"Isi berita")]:
            if not val:
                messagebox.showwarning("Peringatan", f"{name} tidak boleh kosong.")
                return False
        return True

    def _save(self):
        judul, author, tanggal, isi = self._get_values()
        if not self._validate(judul, author, tanggal, isi): return

        fmt = self.fmt_var.get()
        saved_folder = None

        if fmt == "html":
            path = filedialog.asksaveasfilename(
                defaultextension=".html", filetypes=[("HTML file","*.html")],
                initialfile=self._safe_name(judul)+".html", title="Simpan sebagai HTML")
            if path:
                self._write_html(path, judul, author, tanggal, isi)
                saved_folder = os.path.dirname(path)
                self._set_status(f"✅  Disimpan: {os.path.basename(path)}", SUCCESS)

        elif fmt == "txt":
            path = filedialog.asksaveasfilename(
                defaultextension=".txt", filetypes=[("Text file","*.txt")],
                initialfile=self._safe_name(judul)+".txt", title="Simpan sebagai TXT")
            if path:
                self._write_txt(path, judul, author, tanggal, isi)
                self._set_status(f"✅  Disimpan: {os.path.basename(path)}", SUCCESS)

        else:
            folder = filedialog.askdirectory(title="Pilih folder untuk menyimpan kedua file")
            if folder:
                base = os.path.join(folder, self._safe_name(judul))
                self._write_html(base+".html", judul, author, tanggal, isi)
                self._write_txt(base+".txt", judul, author, tanggal, isi)
                saved_folder = folder
                self._set_status(f"✅  Disimpan: {self._safe_name(judul)}.html & .txt", SUCCESS)

        # ── Auto generate file-list.json ──
        if saved_folder and self.auto_gen.get():
            gen_script = os.path.join(saved_folder, "generate_list.py")
            if os.path.isfile(gen_script):
                try:
                    subprocess.run([sys.executable, gen_script], cwd=saved_folder, check=True)
                    self._set_status(self.status.cget("text") + "  |  📋 file-list.json diperbarui", SUCCESS)
                except Exception as e:
                    self._set_status(f"⚠️  file-list.json gagal diperbarui: {e}", "#D97706")
            else:
                self._set_status(self.status.cget("text") + "  |  ℹ️  generate_list.py tidak ada di folder tujuan", MUTED)

    def _write_html(self, path, judul, author, tanggal, isi):
        tgl_fmt = format_tanggal(tanggal)
        html = HTML_TEMPLATE.format(
            judul=judul, author=author, tanggal_fmt=tgl_fmt,
            isi=isi.replace("<","&lt;").replace(">","&gt;"),
            tahun=datetime.date.today().year)
        with open(path, "w", encoding="utf-8") as f: f.write(html)

    def _write_txt(self, path, judul, author, tanggal, isi):
        tgl_fmt = format_tanggal(tanggal)
        div = "=" * 60
        with open(path, "w", encoding="utf-8") as f:
            f.write(f"{div}\nJUDUL   : {judul}\nAUTHOR  : {author}\nTANGGAL : {tgl_fmt}\n{div}\n\n{isi}\n\n{div}\nDibuat dengan News Editor\n")

    def _clear(self):
        if messagebox.askyesno("Bersihkan Form", "Yakin ingin mengosongkan semua field?"):
            for w in [self.entry_judul, self.entry_author]: w.delete(0,"end")
            self.entry_tanggal.delete(0,"end")
            self.entry_tanggal.insert(0, datetime.date.today().strftime("%d/%m/%Y"))
            self.text_isi.delete("1.0","end")
            self._set_status("Form dikosongkan.", MUTED)

    def _safe_name(self, name):
        for ch in r'\/:*?"<>|': name = name.replace(ch,"_")
        return name[:60]

    def _set_status(self, msg, color=MUTED):
        self.status.config(text=msg, fg=color)


if __name__ == "__main__":
    NewsEditor().mainloop()
