"""
generate_list.py
================
- Lokal  : python generate_list.py
- Actions: otomatis setiap git push ke main
"""
import os, json, sys, time, datetime

FOLDER   = os.path.dirname(os.path.abspath(__file__))
OUT_FILE = os.path.join(FOLDER, "file-list.json")
SKIP     = {"index.html"}

def scan():
    return sorted(f for f in os.listdir(FOLDER)
                  if f.lower().endswith(".html") and f not in SKIP)

def generate():
    files = scan()
    with open(OUT_FILE, "w", encoding="utf-8") as fp:
        json.dump(files, fp, ensure_ascii=False, indent=2)
    now = datetime.datetime.now().strftime("%H:%M:%S")
    print(f"[{now}] file-list.json → {len(files)} berita")
    for f in files: print(f"  • {f}")

def watch():
    print("Mode WATCH — Ctrl+C untuk berhenti.\n")
    last = None
    while True:
        cur = scan()
        if cur != last: generate(); last = cur
        time.sleep(2)

if __name__ == "__main__":
    if "--watch" in sys.argv or "-w" in sys.argv:
        try: watch()
        except KeyboardInterrupt: print("\nDihentikan.")
    else:
        generate()
