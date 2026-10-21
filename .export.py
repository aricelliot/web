import os, json, glob
from PIL import Image, ImageOps

ROOT = r"E:\github\web"
SRC = os.path.join(ROOT, "照片素材")
OUT = os.path.join(ROOT, "photos")
CATS = [("nian", "年"), ("xizang", "西藏"), ("guizhou", "贵州"), ("qinghai", "青海")]
PER = 15

TIERS = [
    ("wall", 320, 76),
    ("grid", 640, 78),
    ("view", 1400, 80),
    ("full", 2200, 85),
]

for name, _, _ in TIERS:
    os.makedirs(os.path.join(OUT, name), exist_ok=True)
os.makedirs(os.path.join(OUT, "hero"), exist_ok=True)

def year_of(im):
    ex = im.getexif()
    raw = ex.get(36867) or ex.get(306) or ""
    y = str(raw)[:4]
    try:
        n = int(y)
        if 1990 < n < 2035:
            return n
    except Exception:
        pass
    return None

def tone(im):
    small = im.convert("RGB").resize((1, 1), Image.LANCZOS)
    r, g, b = small.getpixel((0, 0))
    return "#%02x%02x%02x" % (r, g, b)

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

    for i, fi in enumerate(idx):
        name = files[fi]
        src = os.path.join(SRC, cn, name)
        im = ImageOps.exif_transpose(Image.open(src)).convert("RGB")
        w, h = im.size
        k = "%s-%02d" % (key, i + 1)

        for tier, maxw, q in TIERS:
            t = im.copy()
            t.thumbnail((maxw, maxw), Image.LANCZOS)
            t.save(os.path.join(OUT, tier, k + ".jpg"), "JPEG", quality=q,
                   optimize=True, progressive=True)

        manifest.append({
            "key": k,
            "cat": cn,
            "ar": round(w / h, 4),
            "w": w,
            "h": h,
            "year": year_of(im),
            "c": tone(im),
        })
        print(k, cn, name, manifest[-1]["year"], manifest[-1]["c"])

json.dump(manifest, open(os.path.join(OUT, "manifest.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print("TOTAL", len(manifest))

# 开场 hero：1600 宽，只出一张
hero_src = os.path.join(SRC, "年", "DSC_3819.jpg")
hi = ImageOps.exif_transpose(Image.open(hero_src)).convert("RGB")
hi.thumbnail((1600, 1600), Image.LANCZOS)
hi.save(os.path.join(OUT, "hero", "nian-14-1600.jpg"), "JPEG", quality=74,
        optimize=True, progressive=True)
# og 图 1200x630
og = ImageOps.fit(ImageOps.exif_transpose(Image.open(hero_src)).convert("RGB"), (1200, 630), Image.LANCZOS)
os.makedirs(os.path.join(OUT, "og"), exist_ok=True)
og.save(os.path.join(OUT, "og", "og-1200x630.jpg"), "JPEG", quality=80, optimize=True, progressive=True)
print("hero + og done")
