"""
make_icon.py
============
Buat icon .ico sederhana untuk News Editor.
Jalankan SEKALI sebelum build.bat jika belum punya file icon.

Requires: Pillow
    pip install Pillow
"""
import subprocess, sys

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "Pillow"])
    from PIL import Image, ImageDraw, ImageFont

import os

def make_icon():
    sizes = [16, 32, 48, 64, 128, 256]
    frames = []

    for size in sizes:
        img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # Background bulat biru
        pad = size // 10
        draw.rounded_rectangle(
            [pad, pad, size-pad, size-pad],
            radius=size//5,
            fill="#2563EB"
        )

        # Teks "N" di tengah
        font_size = int(size * 0.55)
        try:
            fnt = ImageFont.truetype("arial.ttf", font_size)
        except:
            fnt = ImageFont.load_default()

        bbox = draw.textbbox((0,0), "N", font=fnt)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
        draw.text(
            ((size - tw) // 2 - bbox[0],
             (size - th) // 2 - bbox[1]),
            "N", font=fnt, fill="white"
        )
        frames.append(img)

    os.makedirs("assets", exist_ok=True)
    frames[0].save(
        "assets/icon.ico",
        format="ICO",
        sizes=[(s, s) for s in sizes],
        append_images=frames[1:]
    )
    print("✅  assets/icon.ico berhasil dibuat!")


if __name__ == "__main__":
    make_icon()
