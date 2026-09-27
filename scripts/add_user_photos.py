"""Attach user-supplied photos to catalog varieties by FILE NAME.

Usage:
    python3 add_user_photos.py [photo_dir]          # default: user_photos/
    python3 add_user_photos.py --drive <folderId>   # download a Drive folder first (gws CLI)

Rules
- File name (without extension) = variety name, e.g. "Alocasia venom.jpg",
  "anthurium_carla_x_bvep.png". Case, _ - and punctuation are ignored;
  trailing copies like " (1)" are dropped.
- Exact normalised match first, then a unique "all words contained" match.
- User photos override v22 and Wikimedia reference photos.
- Files that match nothing, or match several varieties, are listed and skipped.
- Generic names (WhatsApp Image ..., photo_2026-..., IMG_1234) are skipped:
  rename them to the variety name first.
"""
import json, os, re, sys, subprocess
from PIL import Image, ImageOps

WS = "/home/user/workspace"
src = f"{WS}/merge_v22.py"
code = open(src).read()
ns = {}
exec(code[: code.index("KNOWN =")], ns)          # reuse pretty()/key() from the merge script
key = ns["key"]

args = sys.argv[1:]
photo_dir = f"{WS}/user_photos"
if args[:1] == ["--drive"]:
    folder = args[1]
    os.makedirs(photo_dir, exist_ok=True)
    out = subprocess.run(["gws", "drive", "files", "list", "--params", json.dumps({
        "q": f'"{folder}" in parents and mimeType contains "image/" and trashed=false',
        "pageSize": 500, "fields": "files(id,name)"})], capture_output=True, text=True).stdout
    for f in json.loads(out).get("files", []):
        subprocess.run(["gws", "drive", "files", "get", "--params",
                        json.dumps({"fileId": f["id"], "alt": "media"}),
                        "--output", os.path.join(photo_dir, f["name"])], capture_output=True)
elif args:
    photo_dir = args[0]

GENERIC = re.compile(r"^(whatsapp image|photo_\d|img[_-]?\d|image\d|screenshot|dsc\d|pxl_)", re.I)
OUT = f"{WS}/user_photos_proc"
os.makedirs(OUT, exist_ok=True)

cat = json.load(open(f"{WS}/data_clean.json"))
adds = json.load(open(f"{WS}/additions_v22.json"))
targets = [("cat", p) for k, p, r in cat if k == "ITEM"] + [("add", a) for a in adds]
tkeys = [(key(t["name"]), kind, t) for kind, t in targets]

log = {"matched": [], "skipped": []}
files = sorted(f for f in os.listdir(photo_dir) if f.lower().endswith((".jpg", ".jpeg", ".png", ".webp", ".heic")))
for fn in files:
    stem = os.path.splitext(fn)[0]
    if GENERIC.match(stem):
        log["skipped"].append((fn, "generic file name - rename to the variety name"))
        continue
    name = re.sub(r"\s*\(\d+\)$", "", re.sub(r"[_\-]+", " ", stem)).strip()
    k = key(name)
    hits = [t for t in tkeys if t[0] == k]
    if not hits:
        kw = set(k.split())
        hits = [t for t in tkeys if kw and kw <= set(t[0].split())]
    if len(hits) != 1:
        log["skipped"].append((fn, "no match" if not hits else "ambiguous: " + " | ".join(h[2]["name"] for h in hits[:5])))
        continue
    _, kind, t = hits[0]
    im = ImageOps.exif_transpose(Image.open(os.path.join(photo_dir, fn))).convert("RGB")
    im.thumbnail((1200, 1200))
    dst = os.path.join(OUT, re.sub(r"[^a-z0-9]+", "_", t["name"].lower()).strip("_") + ".jpg")
    im.save(dst, quality=88)
    if kind == "add":
        t["img"] = os.path.relpath(dst, WS)      # build.py prefixes WS for additions
    else:
        t["img"] = dst
    t.pop("ref", None)
    t["photo_source"] = "user"
    log["matched"].append((fn, t["name"]))

json.dump(cat, open(f"{WS}/data_clean.json", "w"), ensure_ascii=False, indent=1)
json.dump(adds, open(f"{WS}/additions_v22.json", "w"), ensure_ascii=False, indent=1)
json.dump(log, open(f"{WS}/user_photos_log.json", "w"), ensure_ascii=False, indent=1)
print(f"matched {len(log['matched'])}, skipped {len(log['skipped'])}")
for a, b in log["matched"]:
    print("  +", a, "->", b)
for a, b in log["skipped"]:
    print("  -", a, ":", b)
