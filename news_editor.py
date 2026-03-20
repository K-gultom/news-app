# ──────────────────────────────────────────────────────────────
#  Auto-install dependencies
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

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, font as tkfont
from tkcalendar import Calendar
import datetime, os, json, re

# ── Tema ──────────────────────────────────────────────────────
BG        = "#F1F5F9"
CARD      = "#FFFFFF"
SIDEBAR   = "#1E293B"
SIDEBAR_H = "#334155"
SIDEBAR_A = "#2563EB"
ACCENT    = "#2563EB"
ACCENT_H  = "#1D4ED8"
TEXT      = "#1E293B"
MUTED     = "#64748B"
BORDER    = "#E2E8F0"
SUCCESS   = "#16A34A"
WARNING   = "#D97706"
DANGER    = "#DC2626"
TB_BG     = "#F8FAFC"   # toolbar background
TB_BTN    = "#FFFFFF"   # toolbar button bg
TB_HOV    = "#E2E8F0"   # toolbar button hover

DEFAULT_KATEGORI = [
    "Umum","Politik","Ekonomi","Teknologi",
    "Olahraga","Kesehatan","Pendidikan","Hiburan","Internasional"
]
KATEGORI_FILE = "kategori.json"

BULAN = ["","Januari","Februari","Maret","April","Mei","Juni",
         "Juli","Agustus","September","Oktober","November","Desember"]

FONT_SIZES = [8, 9, 10, 11, 12, 14, 16, 18, 20, 24, 28, 32, 36, 48]

def format_tanggal(dt):
    return f"{dt.day} {BULAN[dt.month]} {dt.year}"

def parse_meta(html, key):
    m = re.search(rf'<meta\s+name="{key}"\s+content="([^"]*)"', html)
    return m.group(1).strip() if m else ""

def parse_isi(html):
    m = re.search(r'<div class="body-text">(.*?)</div>', html, re.DOTALL)
    if not m: return ""
    txt = m.group(1).strip()
    # Konversi tag HTML → teks biasa untuk ditampilkan di editor
    txt = re.sub(r'<br\s*/?>', '\n', txt)
    txt = re.sub(r'<p>(.*?)</p>', r'\1\n', txt, flags=re.DOTALL)
    txt = re.sub(r'<li>(.*?)</li>', r'• \1\n', txt, flags=re.DOTALL)
    txt = re.sub(r'<ol>(.*?)</ol>', lambda m: m.group(0), txt, flags=re.DOTALL)
    txt = re.sub(r'<[^>]+>', '', txt)
    txt = txt.replace("&lt;","<").replace("&gt;",">").replace("&amp;","&")
    return txt.strip()

def safe_name(name):
    for ch in r'\/:*?"<>|': name = name.replace(ch, "_")
    return name[:60]


# ══════════════════════════════════════════════════════════════
#  RichTextEditor — Text widget + toolbar formatting
# ══════════════════════════════════════════════════════════════
class RichTextEditor(tk.Frame):
    """
    Frame berisi toolbar formatting + tk.Text widget.
    Mendukung: Bold, Italic, Underline, Strikethrough,
               Font family, Font size, Align (L/C/R),
               Bullet list, Numbered list, warna teks.
    """

    FONTS = ["Georgia", "Segoe UI", "Arial", "Times New Roman",
             "Courier New", "Calibri", "Verdana", "Tahoma"]

    def __init__(self, master, height=14, **kw):
        super().__init__(master, bg=BORDER)
        self._height = height
        self._build()

    # ── Build UI ─────────────────────────────────────────────
    def _build(self):
        # ── Toolbar ──
        tb = tk.Frame(self, bg=TB_BG,
                      highlightbackground=BORDER, highlightthickness=1)
        tb.pack(fill="x")

        # Grup 1: Font family + size
        g1 = tk.Frame(tb, bg=TB_BG); g1.pack(side="left", padx=(6,0), pady=4)

        self._font_var = tk.StringVar(value="Georgia")
        fcb = ttk.Combobox(g1, textvariable=self._font_var,
                           values=self.FONTS, width=13,
                           font=("Segoe UI", 9), state="readonly")
        fcb.pack(side="left", padx=(0,4), ipady=3)
        fcb.bind("<<ComboboxSelected>>", lambda e: self._apply_font())

        self._size_var = tk.StringVar(value="11")
        scb = ttk.Combobox(g1, textvariable=self._size_var,
                           values=[str(s) for s in FONT_SIZES], width=4,
                           font=("Segoe UI", 9), state="readonly")
        scb.pack(side="left", padx=(0,6), ipady=3)
        scb.bind("<<ComboboxSelected>>", lambda e: self._apply_font())

        self._sep(tb)

        # Grup 2: Bold / Italic / Underline / Strikethrough
        g2 = tk.Frame(tb, bg=TB_BG); g2.pack(side="left", pady=4)
        self._bold_on      = tk.BooleanVar()
        self._italic_on    = tk.BooleanVar()
        self._under_on     = tk.BooleanVar()
        self._strike_on    = tk.BooleanVar()

        self._tb_toggle(g2, "B",  self._bold_on,   self._toggle_bold,   bold=True)
        self._tb_toggle(g2, "I",  self._italic_on,  self._toggle_italic, italic=True)
        self._tb_toggle(g2, "U",  self._under_on,   self._toggle_under)
        self._tb_toggle(g2, "S̶",  self._strike_on,  self._toggle_strike)

        self._sep(tb)

        # Grup 3: Alignment
        g3 = tk.Frame(tb, bg=TB_BG); g3.pack(side="left", pady=4)
        self._tb_btn(g3, "⬤≡",  self._align_left,   tip="Rata Kiri")
        self._tb_btn(g3, "≡≡",   self._align_center, tip="Rata Tengah")
        self._tb_btn(g3, "≡⬤",  self._align_right,  tip="Rata Kanan")

        self._sep(tb)

        # Grup 4: List
        g4 = tk.Frame(tb, bg=TB_BG); g4.pack(side="left", pady=4)
        self._tb_btn(g4, "• —",  self._insert_bullet,   tip="Bullet List")
        self._tb_btn(g4, "1. —", self._insert_numbered, tip="Numbered List")

        self._sep(tb)

        # Grup 5: Warna teks
        g5 = tk.Frame(tb, bg=TB_BG); g5.pack(side="left", pady=4)
        for label, color in [("A", "#1E293B"), ("A", "#2563EB"),
                              ("A", "#DC2626"), ("A", "#16A34A"),
                              ("A", "#D97706")]:
            c = color
            btn = tk.Button(g5, text=label, bg=TB_BTN,
                            fg=c, relief="flat",
                            font=("Georgia", 11, "bold"),
                            padx=6, pady=3, cursor="hand2",
                            activebackground=TB_HOV,
                            command=lambda col=c: self._apply_color(col))
            btn.pack(side="left", padx=1)

        self._sep(tb)

        # Grup 6: Clear formatting
        self._tb_btn(tb, "✕ fmt", self._clear_fmt, tip="Hapus Formatting")

        # ── Text area ──
        txt_frame = tk.Frame(self, bg=CARD)
        txt_frame.pack(fill="both", expand=True)

        self.text = tk.Text(txt_frame, height=self._height,
                            font=("Georgia", 11),
                            bg=CARD, fg=TEXT,
                            relief="flat", bd=10,
                            wrap="word",
                            insertbackground=ACCENT,
                            undo=True)
        vsb = ttk.Scrollbar(txt_frame, command=self.text.yview)
        self.text.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        self.text.pack(fill="both", expand=True)

        # Binding: update toolbar state saat cursor bergerak
        self.text.bind("<<CursorMoved>>", self._update_toolbar_state)
        self.text.bind("<ButtonRelease-1>", self._update_toolbar_state)
        self.text.bind("<KeyRelease>", self._update_toolbar_state)

        # Tag pool untuk font size & family (dibuat on-demand)
        self._font_tags = {}    # key: (family, size, bold, italic, under, strike)
        self._color_tags = {}   # key: hex color

        # Base tags
        self.text.tag_configure("bold",      font=("Georgia", 11, "bold"))
        self.text.tag_configure("italic",    font=("Georgia", 11, "italic"))
        self.text.tag_configure("bolditalic",font=("Georgia", 11, "bold italic"))
        self.text.tag_configure("underline", underline=True)
        self.text.tag_configure("strike",    overstrike=True)
        self.text.tag_configure("align_left",   justify="left")
        self.text.tag_configure("align_center", justify="center")
        self.text.tag_configure("align_right",  justify="right")

    # ── Toolbar helpers ───────────────────────────────────────
    def _sep(self, parent):
        tk.Frame(parent, bg=BORDER, width=1,
                 height=22).pack(side="left", padx=5, pady=4)

    def _tb_btn(self, parent, label, cmd, tip="", bold=False):
        b = tk.Button(parent, text=label, bg=TB_BTN, fg=TEXT,
                      relief="flat", font=("Segoe UI", 9, "bold" if bold else "normal"),
                      padx=7, pady=3, cursor="hand2",
                      activebackground=TB_HOV,
                      command=cmd)
        b.pack(side="left", padx=1)
        return b

    def _tb_toggle(self, parent, label, var, cmd,
                   bold=False, italic=False):
        style = "bold" if bold else ("italic" if italic else "normal")
        b = tk.Checkbutton(parent, text=label, variable=var,
                           bg=TB_BTN, fg=TEXT,
                           selectcolor=ACCENT,
                           activebackground=TB_HOV,
                           font=("Segoe UI", 10, style),
                           relief="flat", padx=6, pady=3,
                           cursor="hand2",
                           indicatoron=False,
                           command=cmd)
        b.pack(side="left", padx=1)
        return b

    # ── Format actions ────────────────────────────────────────
    def _sel(self):
        """Return (start, end) selection atau None jika tidak ada."""
        try:
            return self.text.index("sel.first"), self.text.index("sel.last")
        except tk.TclError:
            return None

    def _toggle_tag(self, tag):
        sel = self._sel()
        if not sel: return
        s, e = sel
        existing = self.text.tag_names(s)
        if tag in existing:
            self.text.tag_remove(tag, s, e)
        else:
            self.text.tag_add(tag, s, e)

    def _toggle_bold(self):
        sel = self._sel()
        if not sel: self._bold_on.set(not self._bold_on.get()); return
        s, e = sel
        tags = self.text.tag_names(s)
        if "bold" in tags:
            self.text.tag_remove("bold", s, e)
            self.text.tag_remove("bolditalic", s, e)
        else:
            self.text.tag_add("bold", s, e)
            if "italic" in tags:
                self.text.tag_remove("italic", s, e)
                self.text.tag_add("bolditalic", s, e)

    def _toggle_italic(self):
        sel = self._sel()
        if not sel: self._italic_on.set(not self._italic_on.get()); return
        s, e = sel
        tags = self.text.tag_names(s)
        if "italic" in tags:
            self.text.tag_remove("italic", s, e)
            self.text.tag_remove("bolditalic", s, e)
        else:
            self.text.tag_add("italic", s, e)
            if "bold" in tags:
                self.text.tag_remove("bold", s, e)
                self.text.tag_add("bolditalic", s, e)

    def _toggle_under(self):
        self._toggle_tag("underline")

    def _toggle_strike(self):
        self._toggle_tag("strike")

    def _apply_font(self):
        sel = self._sel()
        if not sel: return
        s, e = sel
        family = self._font_var.get()
        size   = int(self._size_var.get())
        key = (family, size)
        if key not in self._font_tags:
            tag = f"font_{family.replace(' ','_')}_{size}"
            self.text.tag_configure(tag, font=(family, size))
            self._font_tags[key] = tag
        # Hapus tag font lama di seleksi
        for t in list(self._font_tags.values()):
            self.text.tag_remove(t, s, e)
        self.text.tag_add(self._font_tags[key], s, e)

    def _apply_color(self, color):
        sel = self._sel()
        if not sel: return
        s, e = sel
        if color not in self._color_tags:
            tag = f"color_{color.replace('#','')}"
            self.text.tag_configure(tag, foreground=color)
            self._color_tags[color] = tag
        for t in list(self._color_tags.values()):
            self.text.tag_remove(t, s, e)
        self.text.tag_add(self._color_tags[color], s, e)

    def _align_left(self):
        self._set_align("align_left")

    def _align_center(self):
        self._set_align("align_center")

    def _align_right(self):
        self._set_align("align_right")

    def _set_align(self, tag):
        try:
            s = self.text.index("sel.first linestart")
            e = self.text.index("sel.last lineend")
        except tk.TclError:
            s = self.text.index("insert linestart")
            e = self.text.index("insert lineend")
        for t in ("align_left","align_center","align_right"):
            self.text.tag_remove(t, s, e)
        self.text.tag_add(tag, s, e)

    def _insert_bullet(self):
        sel = self._sel()
        if sel:
            s_line = self.text.index(f"{sel[0]} linestart")
            e_line = self.text.index(f"{sel[1]} lineend")
            lines = self.text.get(s_line, e_line).splitlines()
            self.text.delete(s_line, e_line)
            result = "\n".join(
                (l if l.startswith("• ") else f"• {l}") for l in lines)
            self.text.insert(s_line, result)
        else:
            pos = self.text.index("insert")
            line_start = self.text.index(f"{pos} linestart")
            line_text  = self.text.get(line_start, f"{pos} lineend")
            if not line_text.startswith("• "):
                self.text.insert(line_start, "• ")

    def _insert_numbered(self):
        sel = self._sel()
        if sel:
            s_line = self.text.index(f"{sel[0]} linestart")
            e_line = self.text.index(f"{sel[1]} lineend")
            lines  = self.text.get(s_line, e_line).splitlines()
            self.text.delete(s_line, e_line)
            result = "\n".join(
                (l if re.match(r'^\d+\.\s', l) else f"{i+1}. {l}")
                for i, l in enumerate(lines))
            self.text.insert(s_line, result)
        else:
            pos   = self.text.index("insert")
            ls    = self.text.index(f"{pos} linestart")
            ltxt  = self.text.get(ls, f"{pos} lineend")
            if not re.match(r'^\d+\.\s', ltxt):
                self.text.insert(ls, "1. ")

    def _clear_fmt(self):
        sel = self._sel()
        if not sel: return
        s, e = sel
        for tag in (list(self._font_tags.values()) +
                    list(self._color_tags.values()) +
                    ["bold","italic","bolditalic","underline","strike",
                     "align_left","align_center","align_right"]):
            self.text.tag_remove(tag, s, e)

    def _update_toolbar_state(self, event=None):
        """Sinkronkan state tombol toggle dengan posisi kursor."""
        try:
            idx = self.text.index("insert")
            tags = self.text.tag_names(idx)
            self._bold_on.set("bold"   in tags or "bolditalic" in tags)
            self._italic_on.set("italic" in tags or "bolditalic" in tags)
            self._under_on.set("underline" in tags)
            self._strike_on.set("strike" in tags)
            # Sinkron font
            for (fam, sz), tag in self._font_tags.items():
                if tag in tags:
                    self._font_var.set(fam)
                    self._size_var.set(str(sz))
                    break
        except:
            pass

    # ── Konversi ke HTML ──────────────────────────────────────
    def get_html(self):
        """Konversi isi editor beserta formatting → HTML string."""
        content = self.text.get("1.0", "end-1c")
        if not content.strip():
            return ""

        # Kumpulkan semua range tag
        segments = self._get_tagged_segments()
        html_parts = []
        prev_align = None
        i = 0
        chars = list(content)

        while i < len(chars):
            ch = chars[i]
            # Cari semua tag aktif di posisi ini
            tags_here = segments.get(i, set())

            # Align → wrap paragraf
            align = None
            if "align_center" in tags_here: align = "center"
            elif "align_right"  in tags_here: align = "right"
            else: align = "left"

            # Buka div align jika berubah
            if align != prev_align:
                if prev_align is not None:
                    html_parts.append("</div>")
                style = f"text-align:{align}" if align != "left" else ""
                html_parts.append(f'<div style="{style}">' if style else "<div>")
                prev_align = align

            # Format inline
            open_tags, close_tags = [], []
            if "bold"       in tags_here or "bolditalic" in tags_here:
                open_tags.append("<strong>"); close_tags.insert(0,"</strong>")
            if "italic"     in tags_here or "bolditalic" in tags_here:
                open_tags.append("<em>"); close_tags.insert(0,"</em>")
            if "underline"  in tags_here:
                open_tags.append("<u>"); close_tags.insert(0,"</u>")
            if "strike"     in tags_here:
                open_tags.append("<s>"); close_tags.insert(0,"</s>")

            # Warna
            color_tag = next((t for t in tags_here
                              if t.startswith("color_")), None)
            if color_tag:
                col = "#" + color_tag[6:]
                open_tags.append(f'<span style="color:{col}">')
                close_tags.insert(0,"</span>")

            # Font custom
            font_tag = next((t for t in tags_here
                             if t.startswith("font_")), None)
            if font_tag:
                for (fam,sz), tag in self._font_tags.items():
                    if tag == font_tag:
                        open_tags.append(
                            f'<span style="font-family:{fam};font-size:{sz}pt">')
                        close_tags.insert(0,"</span>")
                        break

            escaped = (ch.replace("&","&amp;")
                         .replace("<","&lt;")
                         .replace(">","&gt;"))
            if ch == "\n":
                html_parts.append("".join(close_tags) + "<br>" + "".join(open_tags))
            else:
                html_parts.append("".join(open_tags) + escaped + "".join(close_tags))
            i += 1

        if prev_align is not None:
            html_parts.append("</div>")

        return "".join(html_parts)

    def _get_tagged_segments(self):
        """Return dict {char_index: set_of_tags}."""
        content = self.text.get("1.0", "end-1c")
        seg = {}
        all_tags = (["bold","italic","bolditalic","underline","strike",
                     "align_left","align_center","align_right"] +
                    list(self._font_tags.values()) +
                    list(self._color_tags.values()))
        for tag in all_tags:
            ranges = self.text.tag_ranges(tag)
            for j in range(0, len(ranges), 2):
                start = self.text.count("1.0", ranges[j], "chars")[0]
                end   = self.text.count("1.0", ranges[j+1], "chars")[0]
                for k in range(start, end):
                    seg.setdefault(k, set()).add(tag)
        return seg

    # ── Proxy get/insert/delete untuk kompatibilitas ──────────
    def get(self, *a, **kw):
        return self.text.get(*a, **kw)

    def insert(self, *a, **kw):
        return self.text.insert(*a, **kw)

    def delete(self, *a, **kw):
        return self.text.delete(*a, **kw)

    def focus_set(self):
        self.text.focus_set()


# ══════════════════════════════════════════════════════════════
#  DatePickerPopup
# ══════════════════════════════════════════════════════════════
class DatePickerPopup(tk.Toplevel):
    def __init__(self, parent, current_date, callback):
        super().__init__(parent)
        self.title("Pilih Tanggal")
        self.resizable(False, False)
        self.configure(bg=BG)
        self.grab_set()
        tk.Label(self, text="📅  Pilih Tanggal Berita", bg=BG, fg=TEXT,
                 font=("Segoe UI",11,"bold"), anchor="w").pack(fill="x", padx=16, pady=(14,6))
        cal = Calendar(self, selectmode="day",
                       year=current_date.year, month=current_date.month,
                       day=current_date.day, date_pattern="dd/mm/yyyy",
                       background="#1E3A5F", foreground="white",
                       headersbackground="#163251", headersforeground="white",
                       selectbackground=ACCENT, selectforeground="white",
                       normalbackground=CARD, normalforeground=TEXT,
                       weekendbackground="#F8FAFC", weekendforeground="#DC2626",
                       othermonthbackground="#F1F5F9", othermonthforeground="#94A3B8",
                       bordercolor=BORDER, font=("Segoe UI",10))
        cal.pack(padx=16, pady=4)
        br = tk.Frame(self, bg=BG); br.pack(fill="x", padx=16, pady=12)
        tk.Button(br, text="Batal", command=self.destroy,
                  bg=BORDER, fg=MUTED, relief="flat",
                  font=("Segoe UI",10), padx=14, pady=6, cursor="hand2").pack(side="left")
        tk.Button(br, text="✔  Pilih",
                  command=lambda: self._pick(cal, callback),
                  bg=ACCENT, fg="white", relief="flat",
                  activebackground=ACCENT_H, activeforeground="white",
                  font=("Segoe UI",10,"bold"), padx=14, pady=6,
                  cursor="hand2").pack(side="right")
        self.update_idletasks()
        px = parent.winfo_rootx()+(parent.winfo_width()-self.winfo_width())//2
        py = parent.winfo_rooty()+(parent.winfo_height()-self.winfo_height())//2
        self.geometry(f"+{px}+{py}")

    def _pick(self, cal, callback):
        d,m,y = cal.get_date().split("/")
        self.destroy()
        callback(datetime.date(int(y),int(m),int(d)))


# ══════════════════════════════════════════════════════════════
#  Build HTML output
# ══════════════════════════════════════════════════════════════
def build_html(judul, author, tgl_fmt, kategori, isi_html, tahun):
    return f"""<!DOCTYPE html>
<html lang="id">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width,initial-scale=1.0"/>
  <meta name="judul"    content="{judul}"/>
  <meta name="author"   content="{author}"/>
  <meta name="tanggal"  content="{tgl_fmt}"/>
  <meta name="kategori" content="{kategori}"/>
  <title>{judul}</title>
  <style>
    *{{box-sizing:border-box;margin:0;padding:0}}
    body{{font-family:'Georgia',serif;background:#F8FAFC;color:#1E293B;line-height:1.8}}
    header{{background:#1E3A5F;color:white;padding:16px 0;text-align:center;font-size:13px;letter-spacing:2px;text-transform:uppercase}}
    header a{{color:rgba(255,255,255,.6);text-decoration:none;font-size:12px;margin-left:20px}}
    header a:hover{{color:white}}
    .container{{max-width:760px;margin:48px auto;padding:0 24px}}
    .category{{font-size:12px;font-weight:700;color:#2563EB;text-transform:uppercase;letter-spacing:1.5px;margin-bottom:12px}}
    h1{{font-size:2rem;font-weight:700;color:#0F172A;line-height:1.3;margin-bottom:16px}}
    .meta{{display:flex;gap:20px;font-size:13px;color:#64748B;border-top:1px solid #E2E8F0;border-bottom:1px solid #E2E8F0;padding:10px 0;margin-bottom:28px}}
    .body-text{{font-size:1.05rem;color:#334155;line-height:1.85}}
    .body-text div{{margin-bottom:0.6em}}
    footer{{text-align:center;font-size:12px;color:#94A3B8;margin:60px 0 24px}}
  </style>
</head>
<body>
  <header>Portal Berita <a href="index.html">← Kembali ke daftar berita</a></header>
  <div class="container">
    <div class="category">{kategori}</div>
    <h1>{judul}</h1>
    <div class="meta"><span>✍ {author}</span><span>📅 {tgl_fmt}</span></div>
    <div class="body-text">{isi_html}</div>
  </div>
  <footer>© {tahun} Portal Berita — Dibuat dengan News Editor</footer>
</body>
</html>"""


# ══════════════════════════════════════════════════════════════
#  NewsEditor — Aplikasi Utama
# ══════════════════════════════════════════════════════════════
class NewsEditor(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("News Editor")
        self.geometry("1080x720")
        self.minsize(900, 620)
        self.configure(bg=BG)
        self._sel_date    = datetime.date.today()
        self._edit_path   = None
        self._repo_folder = None
        self._kategori    = self._load_kategori()
        self._all_berita  = []
        self._build_layout()
        self._show_page("tulis")

    # ── Kategori ─────────────────────────────────────────────
    def _load_kategori(self):
        if os.path.isfile(KATEGORI_FILE):
            try:
                d = json.loads(open(KATEGORI_FILE, encoding="utf-8").read())
                if isinstance(d, list) and d: return d
            except: pass
        return list(DEFAULT_KATEGORI)

    def _save_kategori(self):
        with open(KATEGORI_FILE, "w", encoding="utf-8") as f:
            json.dump(self._kategori, f, ensure_ascii=False, indent=2)

    # ── Layout ───────────────────────────────────────────────
    def _build_layout(self):
        self.sidebar = tk.Frame(self, bg=SIDEBAR, width=210)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        logo_f = tk.Frame(self.sidebar, bg=SIDEBAR, height=62)
        logo_f.pack(fill="x"); logo_f.pack_propagate(False)
        tk.Label(logo_f, text="📰  News Editor", bg=SIDEBAR, fg="white",
                 font=("Segoe UI",13,"bold")).pack(side="left", padx=18, pady=18)
        tk.Frame(self.sidebar, bg="#334155", height=1).pack(fill="x")

        self._nav_btns = {}
        for key, lbl in [("tulis",    "✏   Tulis Berita"),
                          ("kelola",   "📂  Kelola Berita"),
                          ("kategori", "🏷   Kategori"),
                          ("sync",     "☁   Sync Server")]:
            b = tk.Button(self.sidebar, text=lbl, anchor="w",
                          bg=SIDEBAR, fg="#CBD5E1",
                          activebackground=SIDEBAR_H, activeforeground="white",
                          relief="flat", bd=0, font=("Segoe UI",10),
                          padx=20, pady=13, cursor="hand2",
                          command=lambda k=key: self._show_page(k))
            b.pack(fill="x")
            self._nav_btns[key] = b

        tk.Label(self.sidebar, text="v3.0", bg=SIDEBAR, fg="#475569",
                 font=("Segoe UI",8)).pack(side="bottom", pady=8)

        self.content = tk.Frame(self, bg=BG)
        self.content.pack(side="left", fill="both", expand=True)

        self.status_bar = tk.Label(self, text="Siap.", bg=BORDER, fg=MUTED,
                                   font=("Segoe UI",9), anchor="w", padx=12)
        self.status_bar.pack(fill="x", side="bottom")

    def _show_page(self, key):
        for k, b in self._nav_btns.items():
            b.config(bg=SIDEBAR_A if k==key else SIDEBAR,
                     fg="white" if k==key else "#CBD5E1")
        for w in self.content.winfo_children():
            w.destroy()
        {"tulis":    self._page_tulis,
         "kelola":   self._page_kelola,
         "kategori": self._page_kategori,
         "sync":     self._page_sync}[key]()

    # ── Helper UI ────────────────────────────────────────────
    def _page_header(self, title):
        hdr = tk.Frame(self.content, bg=CARD, height=56)
        hdr.pack(fill="x"); hdr.pack_propagate(False)
        tk.Label(hdr, text=title, bg=CARD, fg=TEXT,
                 font=("Segoe UI",14,"bold")).pack(side="left", padx=24, pady=14)
        tk.Frame(self.content, bg=BORDER, height=1).pack(fill="x")
        return hdr

    def _scrollbody(self, pad_x=32):
        c = tk.Canvas(self.content, bg=BG, highlightthickness=0)
        sb = ttk.Scrollbar(self.content, orient="vertical", command=c.yview)
        c.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y"); c.pack(fill="both", expand=True)
        body = tk.Frame(c, bg=BG)
        wid = c.create_window((0,0), window=body, anchor="nw")
        c.bind("<Configure>", lambda e: c.itemconfig(wid, width=e.width))
        body.bind("<Configure>", lambda e: c.configure(scrollregion=c.bbox("all")))
        c.bind_all("<MouseWheel>",
            lambda e: c.yview_scroll(int(-1*(e.delta/120)), "units"))
        return body, pad_x

    def _lbl(self, p, text, pad, top=14):
        tk.Label(p, text=text, bg=BG, fg=MUTED,
                 font=("Segoe UI",10)).pack(anchor="w", padx=pad, pady=(top,0))

    def _entry(self, p, pad):
        w = tk.Frame(p, bg=BORDER); w.pack(fill="x", padx=pad, pady=4)
        e = tk.Entry(w, font=("Segoe UI",11), bg=CARD, fg=TEXT,
                     relief="flat", bd=8, insertbackground=ACCENT)
        e.pack(fill="x"); return e

    # ══════════════════════════════════════════════════════════
    #  PAGE: TULIS
    # ══════════════════════════════════════════════════════════
    def _page_tulis(self, prefill=None):
        self._edit_path = prefill["path"] if prefill else None
        title = "✏   Edit Berita" if prefill else "✏   Tulis Berita Baru"
        hdr = self._page_header(title)
        if prefill:
            tk.Label(hdr, text=os.path.basename(prefill["path"]),
                     bg=CARD, fg=MUTED, font=("Segoe UI",9)).pack(side="left", pady=14)

        body, pad = self._scrollbody(32)

        # Judul
        self._lbl(body, "Judul Berita *", pad, 20)
        self.e_judul = self._entry(body, pad)
        if prefill: self.e_judul.insert(0, prefill.get("judul",""))

        # Author + Kategori
        row2 = tk.Frame(body, bg=BG); row2.pack(fill="x", padx=pad, pady=(14,0))
        row2.columnconfigure(0, weight=1); row2.columnconfigure(1, weight=1)

        lf = tk.Frame(row2, bg=BG); lf.grid(row=0, column=0, sticky="ew", padx=(0,8))
        tk.Label(lf, text="Nama Author *", bg=BG, fg=MUTED,
                 font=("Segoe UI",10)).pack(anchor="w")
        wa = tk.Frame(lf, bg=BORDER); wa.pack(fill="x", pady=4)
        self.e_author = tk.Entry(wa, font=("Segoe UI",11), bg=CARD, fg=TEXT,
                                  relief="flat", bd=8, insertbackground=ACCENT)
        self.e_author.pack(fill="x")
        if prefill: self.e_author.insert(0, prefill.get("author",""))

        rf = tk.Frame(row2, bg=BG); rf.grid(row=0, column=1, sticky="ew", padx=(8,0))
        tk.Label(rf, text="Kategori *", bg=BG, fg=MUTED,
                 font=("Segoe UI",10)).pack(anchor="w")
        wk = tk.Frame(rf, bg=BORDER); wk.pack(fill="x", pady=4)
        self.cmb_kat = ttk.Combobox(wk, values=self._kategori,
                                     font=("Segoe UI",11), state="readonly")
        self.cmb_kat.pack(fill="x", ipady=5)
        def_kat = prefill.get("kategori","Umum") if prefill else "Umum"
        self.cmb_kat.set(def_kat if def_kat in self._kategori else self._kategori[0])

        # Tanggal
        self._lbl(body, "Tanggal Berita *", pad, 14)
        self._sel_date = datetime.date.today()
        if prefill and prefill.get("tanggal"):
            try:
                p = prefill["tanggal"].split()
                self._sel_date = datetime.date(int(p[2]), BULAN.index(p[1]), int(p[0]))
            except: pass
        trow = tk.Frame(body, bg=BG); trow.pack(fill="x", padx=pad, pady=4)
        wtgl = tk.Frame(trow, bg=BORDER); wtgl.pack(side="left", fill="x", expand=True)
        self.lbl_tgl = tk.Label(wtgl, text=format_tanggal(self._sel_date),
                                 bg=CARD, fg=TEXT, font=("Segoe UI",11),
                                 anchor="w", padx=10, pady=9)
        self.lbl_tgl.pack(fill="x")
        tk.Button(trow, text="📅  Pilih",
                  command=lambda: DatePickerPopup(self, self._sel_date, self._on_date),
                  bg=ACCENT, fg="white", activebackground=ACCENT_H, activeforeground="white",
                  relief="flat", bd=0, font=("Segoe UI",10),
                  padx=14, pady=8, cursor="hand2").pack(side="left", padx=(8,0))

        # ── Isi Berita (Rich Text Editor) ──
        self._lbl(body, "Isi Berita *", pad, 14)
        editor_wrap = tk.Frame(body, bg=BG)
        editor_wrap.pack(fill="x", padx=pad, pady=4)
        self.e_isi = RichTextEditor(editor_wrap, height=14)
        self.e_isi.pack(fill="both", expand=True)
        if prefill and prefill.get("isi"):
            self.e_isi.insert("1.0", prefill.get("isi",""))

        # Auto gen
        self.auto_gen = tk.BooleanVar(value=True)
        ag = tk.Frame(body, bg=BG); ag.pack(fill="x", padx=pad, pady=(10,0))
        tk.Checkbutton(ag, text="Otomatis perbarui file-list.json setelah simpan",
                       variable=self.auto_gen, bg=BG, fg=MUTED,
                       activebackground=BG, selectcolor=CARD,
                       font=("Segoe UI",10)).pack(anchor="w")

        # Tombol
        br = tk.Frame(body, bg=BG); br.pack(fill="x", padx=pad, pady=(14,28))
        lbl_cancel = "✖  Batal Edit" if prefill else "🗑  Bersihkan"
        tk.Button(br, text=lbl_cancel,
                  command=lambda: self._show_page("tulis"),
                  bg=BORDER, fg=MUTED, relief="flat",
                  font=("Segoe UI",10), padx=16, pady=8,
                  cursor="hand2").pack(side="left")

        lbl_save = "💾  Simpan Perubahan" if prefill else "💾  Simpan Berita"
        tk.Button(br, text=lbl_save, command=self._save_berita,
                  bg=ACCENT, fg="white", activebackground=ACCENT_H, activeforeground="white",
                  relief="flat", bd=0, font=("Segoe UI",10,"bold"),
                  padx=18, pady=8, cursor="hand2").pack(side="right")

    def _on_date(self, d):
        self._sel_date = d
        self.lbl_tgl.config(text=format_tanggal(d))

    def _save_berita(self):
        judul  = self.e_judul.get().strip()
        author = self.e_author.get().strip()
        kat    = self.cmb_kat.get().strip()
        isi_html = self.e_isi.get_html()

        for v, n in [(judul,"Judul"),(author,"Author"),
                     (isi_html,"Isi berita"),(kat,"Kategori")]:
            if not v:
                messagebox.showwarning("Peringatan", f"{n} tidak boleh kosong.")
                return

        tgl_fmt = format_tanggal(self._sel_date)
        html = build_html(judul, author, tgl_fmt, kat,
                          isi_html, datetime.date.today().year)

        if self._edit_path:
            path = self._edit_path
            with open(path, "w", encoding="utf-8") as f: f.write(html)
            self._set_status(f"✅  Diperbarui: {os.path.basename(path)}", SUCCESS)
        else:
            path = filedialog.asksaveasfilename(
                defaultextension=".html", filetypes=[("HTML","*.html")],
                initialfile=safe_name(judul)+".html", title="Simpan Berita")
            if not path: return
            with open(path, "w", encoding="utf-8") as f: f.write(html)
            self._set_status(f"✅  Disimpan: {os.path.basename(path)}", SUCCESS)

        if self.auto_gen.get():
            self._run_gen(os.path.dirname(path))

        self._edit_path = None
        self.after(200, lambda: self._show_page("tulis"))

    def _run_gen(self, folder):
        g = os.path.join(folder, "generate_list.py")
        if os.path.isfile(g):
            try: subprocess.run([sys.executable, g], cwd=folder, check=True, capture_output=True)
            except: pass

    # ══════════════════════════════════════════════════════════
    #  PAGE: KELOLA
    # ══════════════════════════════════════════════════════════
    def _page_kelola(self):
        hdr = self._page_header("📂  Kelola Berita")
        tk.Button(hdr, text="📁  Pilih Folder", command=self._pilih_folder,
                  bg=ACCENT, fg="white", relief="flat",
                  activebackground=ACCENT_H, activeforeground="white",
                  font=("Segoe UI",10), padx=14, pady=6,
                  cursor="hand2").pack(side="right", padx=16, pady=14)

        self.lbl_folder = tk.Label(self.content,
            text=f"Folder: {self._repo_folder or '— belum dipilih —'}",
            bg=BG, fg=MUTED, font=("Segoe UI",9), anchor="w")
        self.lbl_folder.pack(fill="x", padx=20, pady=(10,4))

        sf = tk.Frame(self.content, bg=BG); sf.pack(fill="x", padx=20, pady=(0,10))
        ws = tk.Frame(sf, bg=BORDER); ws.pack(side="left", fill="x", expand=True)
        self.e_search = tk.Entry(ws, font=("Segoe UI",11), bg=CARD, fg=MUTED,
                                  relief="flat", bd=8, insertbackground=ACCENT)
        self.e_search.insert(0,"🔍  Cari judul, author, atau kategori...")
        self.e_search.pack(fill="x")
        self.e_search.bind("<FocusIn>", lambda e: (
            self.e_search.delete(0,"end"), self.e_search.config(fg=TEXT))
            if self.e_search.get().startswith("🔍") else None)
        self.e_search.bind("<KeyRelease>", lambda e: self._filter_list())

        kf = tk.Frame(sf, bg=BG); kf.pack(side="left", padx=(8,0))
        self.cmb_filter = ttk.Combobox(kf, values=["Semua"]+self._kategori,
                                        font=("Segoe UI",10), state="readonly", width=14)
        self.cmb_filter.set("Semua"); self.cmb_filter.pack(ipady=5)
        self.cmb_filter.bind("<<ComboboxSelected>>", lambda e: self._filter_list())

        lw = tk.Frame(self.content, bg=BG)
        lw.pack(fill="both", expand=True, padx=20, pady=(0,16))
        lc = tk.Canvas(lw, bg=BG, highlightthickness=0)
        lsb = ttk.Scrollbar(lw, orient="vertical", command=lc.yview)
        lc.configure(yscrollcommand=lsb.set)
        lsb.pack(side="right", fill="y"); lc.pack(fill="both", expand=True)
        self.list_body = tk.Frame(lc, bg=BG)
        wid = lc.create_window((0,0), window=self.list_body, anchor="nw")
        lc.bind("<Configure>", lambda e: lc.itemconfig(wid, width=e.width))
        self.list_body.bind("<Configure>",
            lambda e: lc.configure(scrollregion=lc.bbox("all")))
        lc.bind_all("<MouseWheel>",
            lambda e: lc.yview_scroll(int(-1*(e.delta/120)),"units"))

        if self._repo_folder:
            self._load_list()
        else:
            tk.Label(self.list_body,
                     text="Klik '📁 Pilih Folder' untuk memilih folder repo berita.",
                     bg=BG, fg=MUTED, font=("Segoe UI",11)).pack(pady=60)

    def _pilih_folder(self):
        f = filedialog.askdirectory(title="Pilih folder repo berita")
        if not f: return
        self._repo_folder = f
        self._show_page("kelola")

    def _load_list(self):
        files = sorted(f for f in os.listdir(self._repo_folder)
                       if f.lower().endswith(".html") and f != "index.html")
        self._all_berita = []
        for fname in files:
            fpath = os.path.join(self._repo_folder, fname)
            try:
                raw = open(fpath, encoding="utf-8").read()
                self._all_berita.append({
                    "path":     fpath, "file": fname,
                    "judul":    parse_meta(raw,"judul")    or fname,
                    "author":   parse_meta(raw,"author")   or "—",
                    "tanggal":  parse_meta(raw,"tanggal")  or "—",
                    "kategori": parse_meta(raw,"kategori") or "Umum",
                    "isi":      parse_isi(raw),
                })
            except: pass
        n = len(self._all_berita)
        self.lbl_folder.config(
            text=f"Folder: {self._repo_folder}  ({n} berita ditemukan)")
        self._render_list(self._all_berita)

    def _filter_list(self):
        q   = self.e_search.get().lower().strip()
        kat = self.cmb_filter.get()
        res = self._all_berita
        if not q.startswith("🔍") and q:
            res = [b for b in res if q in b["judul"].lower()
                   or q in b["author"].lower() or q in b["kategori"].lower()]
        if kat and kat != "Semua":
            res = [b for b in res if b["kategori"] == kat]
        self._render_list(res)

    def _render_list(self, items):
        for w in self.list_body.winfo_children(): w.destroy()
        if not items:
            tk.Label(self.list_body, text="Tidak ada berita ditemukan.",
                     bg=BG, fg=MUTED, font=("Segoe UI",11)).pack(pady=60)
            return
        for i, b in enumerate(items):
            row = tk.Frame(self.list_body, bg=CARD,
                           highlightbackground=BORDER, highlightthickness=1)
            row.pack(fill="x", pady=(0,2))
            tk.Label(row, text=f"{i+1:02d}", bg=CARD, fg="#CBD5E1",
                     font=("Segoe UI",10,"bold"), width=4).pack(side="left", padx=(12,4))
            info = tk.Frame(row, bg=CARD)
            info.pack(side="left", fill="x", expand=True, pady=10)
            tk.Label(info, text=b["kategori"], bg="#EFF6FF", fg=ACCENT,
                     font=("Segoe UI",8,"bold"), padx=6, pady=1).pack(anchor="w")
            tk.Label(info, text=b["judul"], bg=CARD, fg=TEXT,
                     font=("Segoe UI",11,"bold"), anchor="w").pack(fill="x")
            tk.Label(info,
                     text=f"✍ {b['author']}   📅 {b['tanggal']}   📄 {b['file']}",
                     bg=CARD, fg=MUTED, font=("Segoe UI",9), anchor="w").pack(fill="x")
            act = tk.Frame(row, bg=CARD); act.pack(side="right", padx=12)
            tk.Button(act, text="✏  Edit",
                      command=lambda bd=b: self._do_edit(bd),
                      bg="#EFF6FF", fg=ACCENT, relief="flat",
                      font=("Segoe UI",9), padx=10, pady=5,
                      cursor="hand2").pack(side="left", padx=(0,6))
            tk.Button(act, text="🗑  Hapus",
                      command=lambda bd=b: self._do_hapus(bd),
                      bg="#FEF2F2", fg=DANGER, relief="flat",
                      font=("Segoe UI",9), padx=10, pady=5,
                      cursor="hand2").pack(side="left")

    def _do_edit(self, bdata):
        for w in self.content.winfo_children(): w.destroy()
        for k, b in self._nav_btns.items():
            b.config(bg=SIDEBAR_A if k=="tulis" else SIDEBAR,
                     fg="white" if k=="tulis" else "#CBD5E1")
        self._page_tulis(prefill=bdata)

    def _do_hapus(self, bdata):
        if not messagebox.askyesno("Hapus Berita",
            f"Yakin menghapus:\n\n\"{bdata['judul']}\"\n\n"
            f"File: {bdata['file']}\n\nTindakan ini tidak bisa dibatalkan!"):
            return
        try:
            os.remove(bdata["path"])
            self._run_gen(self._repo_folder)
            self._set_status(f"🗑  Dihapus: {bdata['file']}", WARNING)
            self._load_list()
            self._filter_list()
        except Exception as e:
            messagebox.showerror("Gagal", f"Tidak bisa menghapus:\n{e}")

    # ══════════════════════════════════════════════════════════
    #  PAGE: KATEGORI
    # ══════════════════════════════════════════════════════════
    def _page_kategori(self):
        self._page_header("🏷   Manajemen Kategori")
        body, pad = self._scrollbody(32)

        card = tk.Frame(body, bg=CARD,
                        highlightbackground=BORDER, highlightthickness=1)
        card.pack(fill="x", pady=(0,20))
        inn = tk.Frame(card, bg=CARD); inn.pack(fill="x", padx=20, pady=16)
        tk.Label(inn, text="Tambah Kategori Baru", bg=CARD, fg=TEXT,
                 font=("Segoe UI",11,"bold")).pack(anchor="w", pady=(0,10))
        ir = tk.Frame(inn, bg=CARD); ir.pack(fill="x")
        wi = tk.Frame(ir, bg=BORDER); wi.pack(side="left", fill="x", expand=True)
        self.e_kat_baru = tk.Entry(wi, font=("Segoe UI",11), bg=CARD, fg=TEXT,
                                    relief="flat", bd=8, insertbackground=ACCENT)
        self.e_kat_baru.pack(fill="x")
        self.e_kat_baru.bind("<Return>", lambda e: self._tambah_kat())
        tk.Button(ir, text="➕  Tambah", command=self._tambah_kat,
                  bg=ACCENT, fg="white", relief="flat",
                  activebackground=ACCENT_H, activeforeground="white",
                  font=("Segoe UI",10), padx=14, pady=8,
                  cursor="hand2").pack(side="left", padx=(8,0))
        tk.Button(ir, text="↺  Reset Default", command=self._reset_kat,
                  bg=BORDER, fg=MUTED, relief="flat",
                  font=("Segoe UI",10), padx=14, pady=8,
                  cursor="hand2").pack(side="left", padx=(8,0))

        tk.Label(body, text=f"Kategori aktif ({len(self._kategori)})",
                 bg=BG, fg=MUTED, font=("Segoe UI",10)).pack(
                     anchor="w", padx=pad, pady=(0,8))
        self.kat_frame = tk.Frame(body, bg=BG)
        self.kat_frame.pack(fill="x", padx=pad)
        self._render_kat()

    def _render_kat(self):
        for w in self.kat_frame.winfo_children(): w.destroy()
        cols = 3
        row_f = None
        for i, kat in enumerate(self._kategori):
            if i % cols == 0:
                row_f = tk.Frame(self.kat_frame, bg=BG)
                row_f.pack(fill="x", pady=(0,8))
                for c in range(cols):
                    row_f.columnconfigure(c, weight=1, uniform="col")
            c = tk.Frame(row_f, bg=CARD,
                         highlightbackground=BORDER, highlightthickness=1)
            c.grid(row=0, column=i%cols, sticky="ew",
                   padx=(0,8) if i%cols < cols-1 else 0)
            tk.Label(c, text=kat, bg=CARD, fg=TEXT,
                     font=("Segoe UI",10), anchor="w",
                     padx=12, pady=10).pack(side="left", fill="x", expand=True)
            is_def = kat in DEFAULT_KATEGORI
            db = tk.Button(c, text="✕",
                           command=lambda k=kat: self._hapus_kat(k),
                           bg=CARD, fg="#F87171" if not is_def else "#CBD5E1",
                           relief="flat", font=("Segoe UI",10),
                           padx=8, pady=8,
                           cursor="hand2" if not is_def else "")
            db.pack(side="right")
            if is_def: db.config(state="disabled")

    def _tambah_kat(self):
        nama = self.e_kat_baru.get().strip().title()
        if not nama:
            messagebox.showwarning("Kosong","Nama kategori tidak boleh kosong.")
            return
        if nama in self._kategori:
            messagebox.showwarning("Duplikat", f"Kategori '{nama}' sudah ada.")
            return
        self._kategori.append(nama)
        self._save_kategori()
        self.e_kat_baru.delete(0,"end")
        self._render_kat()
        self._set_status(f"✅  Kategori '{nama}' ditambahkan.", SUCCESS)

    def _hapus_kat(self, nama):
        if nama in DEFAULT_KATEGORI:
            messagebox.showinfo("Info","Kategori bawaan tidak bisa dihapus.")
            return
        if not messagebox.askyesno("Hapus", f"Hapus kategori '{nama}'?"): return
        self._kategori.remove(nama)
        self._save_kategori()
        self._render_kat()
        self._set_status(f"🗑  Kategori '{nama}' dihapus.", WARNING)

    def _reset_kat(self):
        if messagebox.askyesno("Reset",
            "Reset ke kategori bawaan?\nKategori tambahan akan hilang."):
            self._kategori = list(DEFAULT_KATEGORI)
            self._save_kategori()
            self._render_kat()
            self._set_status("↺  Kategori direset ke default.", MUTED)

    # ══════════════════════════════════════════════════════════
    #  PAGE: SYNC
    # ══════════════════════════════════════════════════════════
    def _page_sync(self):
        self._page_header("☁   Sync Server")
        body, pad = self._scrollbody(32)

        fc = tk.Frame(body, bg=CARD,
                      highlightbackground=BORDER, highlightthickness=1)
        fc.pack(fill="x", pady=(0,16))
        fi = tk.Frame(fc, bg=CARD); fi.pack(fill="x", padx=20, pady=16)
        tk.Label(fi, text="Folder Repo Git", bg=CARD, fg=TEXT,
                 font=("Segoe UI",11,"bold")).pack(anchor="w", pady=(0,8))
        fr = tk.Frame(fi, bg=CARD); fr.pack(fill="x")
        wf = tk.Frame(fr, bg=BORDER); wf.pack(side="left", fill="x", expand=True)
        self.lbl_sfolder = tk.Label(wf,
            text=self._repo_folder or "— belum dipilih —",
            bg=CARD, fg=TEXT if self._repo_folder else MUTED,
            font=("Segoe UI",10), anchor="w", padx=10, pady=9)
        self.lbl_sfolder.pack(fill="x")
        tk.Button(fr, text="📁  Pilih", command=self._pilih_sync_folder,
                  bg=BORDER, fg=TEXT, relief="flat",
                  font=("Segoe UI",10), padx=14, pady=8,
                  cursor="hand2").pack(side="left", padx=(8,0))

        ic = tk.Frame(body, bg=CARD,
                      highlightbackground=BORDER, highlightthickness=1)
        ic.pack(fill="x", pady=(0,20))
        ii = tk.Frame(ic, bg=CARD); ii.pack(fill="x", padx=20, pady=14)
        tk.Label(ii, text="Perintah yang akan dijalankan:",
                 bg=CARD, fg=MUTED, font=("Segoe UI",9)).pack(anchor="w", pady=(0,6))
        for s in ["1.  git add .",
                  "2.  git commit -m 'commit berita terbaru <tanggal>'",
                  "3.  git pull  (resolve conflict otomatis jika ada)",
                  "4.  git push"]:
            tk.Label(ii, text=s, bg=CARD, fg=TEXT,
                     font=("Consolas",10)).pack(anchor="w")

        tk.Button(body, text="☁  Mulai Sync Sekarang",
                  command=self._mulai_sync,
                  bg="#0F766E", fg="white",
                  activebackground="#0D5C55", activeforeground="white",
                  relief="flat", bd=0, font=("Segoe UI",11,"bold"),
                  pady=13, cursor="hand2").pack(fill="x")

    def _pilih_sync_folder(self):
        f = filedialog.askdirectory(title="Pilih folder repo Git")
        if not f: return
        self._repo_folder = f
        self.lbl_sfolder.config(text=f, fg=TEXT)

    def _mulai_sync(self):
        if not self._repo_folder:
            messagebox.showwarning("Belum Dipilih",
                "Pilih folder repo Git terlebih dahulu.")
            return
        if not os.path.isdir(os.path.join(self._repo_folder, ".git")):
            messagebox.showerror("Bukan Git Repo",
                f"Folder ini bukan repositori Git:\n{self._repo_folder}")
            return
        msg = f"commit berita terbaru {datetime.datetime.now().strftime('%d %B %Y %H:%M')}"
        self._git_window(self._repo_folder, msg)

    def _git_window(self, folder, commit_msg):
        win = tk.Toplevel(self)
        win.title("Sync Server")
        win.geometry("620x460")
        win.configure(bg=BG)
        win.resizable(True, True)
        win.grab_set()

        tk.Label(win, text="☁  Sync Server", bg=BG, fg=TEXT,
                 font=("Segoe UI",13,"bold"), anchor="w").pack(
                     fill="x", padx=20, pady=(16,2))
        tk.Label(win, text=folder, bg=BG, fg=MUTED,
                 font=("Segoe UI",9), anchor="w").pack(
                     fill="x", padx=20, pady=(0,10))

        lf = tk.Frame(win, bg="#0F172A"); lf.pack(fill="both", expand=True, padx=20)
        log = tk.Text(lf, bg="#0F172A", fg="#94A3B8", font=("Consolas",10),
                      relief="flat", bd=10, state="disabled", wrap="word")
        lsb = ttk.Scrollbar(lf, command=log.yview)
        log.configure(yscrollcommand=lsb.set)
        lsb.pack(side="right", fill="y"); log.pack(fill="both", expand=True)
        for tag, col in [("cmd","#60A5FA"),("ok","#4ADE80"),
                         ("warn","#FCD34D"),("err","#F87171"),("out","#CBD5E1")]:
            log.tag_config(tag, foreground=col)

        cd_lbl = tk.Label(win, text="", bg=BG, fg=MUTED, font=("Segoe UI",9))
        cd_lbl.pack(pady=(8,0))
        close_btn = tk.Button(win, text="Tutup", state="disabled",
                              bg=BORDER, fg=MUTED, relief="flat",
                              font=("Segoe UI",10), padx=16, pady=7,
                              cursor="hand2", command=win.destroy)
        close_btn.pack(pady=(4,12))

        def ap(text, tag="out"):
            log.configure(state="normal")
            log.insert("end", text, tag)
            log.see("end")
            log.configure(state="disabled")
            win.update()

        def run_cmd(lbl, cmd, rc1=False):
            ap(f"\n$ {lbl}\n", "cmd")
            try:
                r = subprocess.run(cmd, cwd=folder, stdout=subprocess.PIPE,
                                   stderr=subprocess.STDOUT, text=True)
                if r.stdout.strip(): ap(r.stdout.strip()+"\n", "out")
                if r.returncode == 0:
                    ap("✔  OK\n", "ok"); return True, 0
                elif rc1 and r.returncode == 1:
                    ap("ℹ  Tidak ada perubahan untuk di-commit.\n", "warn")
                    return True, 1
                else:
                    ap(f"✖  Gagal (exit {r.returncode})\n", "err")
                    return False, r.returncode
            except FileNotFoundError:
                ap("✖  Git tidak ditemukan di PATH.\n", "err"); return False, -1
            except Exception as e:
                ap(f"✖  Error: {e}\n", "err"); return False, -1

        def get_conflicts():
            r = subprocess.run(["git","diff","--name-only","--diff-filter=U"],
                               cwd=folder, stdout=subprocess.PIPE,
                               stderr=subprocess.DEVNULL, text=True)
            return r.stdout.strip()

        def run_all():
            ap("\n─── Tahap 1: Simpan perubahan lokal ───\n","cmd")
            ok,_ = run_cmd("git add .", ["git","add","."])
            if not ok: return done(False)
            ok,_ = run_cmd(f'git commit -m "{commit_msg}"',
                           ["git","commit","-m",commit_msg], rc1=True)
            if not ok: return done(False)

            ap("\n─── Tahap 2: Pull dari server ───\n","cmd")
            ok,_ = run_cmd("git pull",["git","pull"])
            if not ok:
                konflik = get_conflicts()
                if konflik:
                    ap(f"\n⚠️  Conflict pada:\n{konflik}\n","warn")
                    ap("→  Resolve otomatis (ambil versi lokal)...\n","warn")
                    for fn in konflik.splitlines():
                        fn = fn.strip()
                        if fn:
                            ok2,_ = run_cmd(f"git checkout --ours {fn}",
                                            ["git","checkout","--ours",fn])
                            if not ok2: return done(False)
                    ok,_ = run_cmd("git add .",["git","add","."])
                    if not ok: return done(False)
                    ok,_ = run_cmd('git commit -m "merge: resolve conflict"',
                                   ["git","commit","-m","merge: resolve conflict"],
                                   rc1=True)
                    if not ok: return done(False)
                else: return done(False)

            ap("\n─── Tahap 3: Push ke server ───\n","cmd")
            ok,_ = run_cmd("git push",["git","push"])
            if not ok: return done(False)
            done(True)

        def done(success):
            if success:
                ap("\n✅  Sync selesai! Semua perubahan berhasil dipush.\n","ok")
                self._set_status("✅  Sync server selesai.", SUCCESS)
                def tick(n):
                    if not win.winfo_exists(): return
                    if n <= 0: win.destroy()
                    else:
                        cd_lbl.config(text=f"Menutup dalam {n} detik...")
                        win.after(1000, lambda: tick(n-1))
                tick(3)
            else:
                ap("\n⚠️  Sync gagal. Periksa log di atas.\n","err")
                self._set_status("⚠️  Sync server gagal.", WARNING)
                close_btn.configure(state="normal", bg=ACCENT, fg="white",
                                    activebackground=ACCENT_H, activeforeground="white")

        win.after(150, run_all)

    # ── Helpers ──────────────────────────────────────────────
    def _set_status(self, msg, color=MUTED):
        self.status_bar.config(text=msg, fg=color)


if __name__ == "__main__":
    NewsEditor().mainloop()
