import os, json, shutil
from PIL import Image, ImageOps
Image.MAX_IMAGE_PIXELS = 400_000_000

ROOT = r"E:\github\web"
SRC = os.path.join(ROOT, "照片素材")
OUT = os.path.join(ROOT, "photos")
CATS = [("nian", "年"), ("xizang", "西藏"), ("guizhou", "贵州"), ("qinghai", "青海")]
PER = 15

for sub in ("thumb", "full"):
    p = os.path.join(OUT, sub)
    if os.path.isdir(p):
        shutil.rmtree(p)
    os.makedirs(p, exist_ok=True)

manifest = []
for key, cn in CATS:
    files = []
    for f in sorted(os.listdir(os.path.join(SRC, cn))):
        if not f.lower().endswith((".jpg", ".jpeg", ".png")):
            continue
        try:
            w0, h0 = Image.open(os.path.join(SRC, cn, f)).size
        except Exception:
            continue
        if 0.4 < w0 / h0 < 3.2:
            files.append(f)
    n = len(files)
    idx = [round(i * (n - 1) / (PER - 1)) for i in range(PER)] if n >= PER else list(range(n))
    picked = [files[i] for i in idx]
    for i, name in enumerate(picked):
        src = os.path.join(SRC, cn, name)
        im = ImageOps.exif_transpose(Image.open(src)).convert("RGB")
        w, h = im.size
        k = f"{key}-{i+1:02d}"

        t = im.copy()
        t.thumbnail((1000, 1000), Image.LANCZOS)
        t.save(os.path.join(OUT, "thumb", k + ".jpg"), "JPEG", quality=80, optimize=True, progressive=True)

        f = im.copy()
        f.thumbnail((2200, 2200), Image.LANCZOS)
        f.save(os.path.join(OUT, "full", k + ".jpg"), "JPEG", quality=85, optimize=True, progressive=True)

        manifest.append({"key": k, "cat": cn, "ar": round(w / h, 4), "w": w, "h": h})
        print(k, cn, f"{w}x{h}", name)

json.dump(manifest, open(os.path.join(OUT, "manifest.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("TOTAL", len(manifest))
