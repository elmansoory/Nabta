"""Import names, photos and prices from BanrakTonmai Garden (Shopify store).

- reads https://www.banraktonmaigarden.com/products.json (all pages) -> brt/products.json
- cleans names, extracts pack size ("Set of 10 Plants" -> pkg 10); price is per listing (per set)
- downloads the first product photo (700 px) -> brt/img/
- writes brt/items.json
- fills photos for catalog / v22 varieties that still have no photo (or only a Wikimedia reference)

Run after merge_v22.py and before add_user_photos.py / build_catalog.py.
Pass --offline to reuse brt/products.json and already downloaded images.
"""
import json, re, os, io, sys, time, urllib.request, concurrent.futures as cf
from PIL import Image

WS = "/home/user/workspace"
BASE = "https://www.banraktonmaigarden.com"
UA = {"User-Agent": "Mozilla/5.0"}
RATE = 52
os.makedirs(f"{WS}/brt/img", exist_ok=True)

if "--offline" not in sys.argv:
    allp = []
    for page in range(1, 30):
        d = json.loads(urllib.request.urlopen(urllib.request.Request(
            f"{BASE}/products.json?limit=250&page={page}", headers=UA), timeout=60).read())
        if not d["products"]:
            break
        allp += d["products"]
        time.sleep(1)
    json.dump(allp, open(f"{WS}/brt/products.json", "w"))
P = json.load(open(f"{WS}/brt/products.json"))

GENERA = ("aglaonema alocasia anthurium begonia epipremnum homalomena hoya monstera oxalis philodendron "
          "piper rhaphidophora scindapsus spathiphyllum syngonium thaumatophyllum zamioculcas").split()


def parse(t):
    t = (t.replace("“", "'").replace("”", "'").replace("‘", "'").replace("’", "'")
          .replace('"', "'").replace("—", "-").replace("–", "-"))
    pkg = 1
    m = re.search(r"set\s*(?:of\s*)?(\d+)\s*(?:pcs|plants?)?", t, re.I) or re.search(r"\((\d+)\s*plants?\)", t, re.I)
    if m:
        pkg = int(m.group(1))
    s = re.sub(r"[-]?\s*\(?\s*(wholesale\s*)?(bundle\s*)?\(?\s*set\s*(of\s*)?\d+\s*(pcs|plants?)?\s*\)?(\s*\((big|small|medium)\s*size\))?", "", t, flags=re.I)
    s = re.sub(r"\(\s*\d+\s*plants?\s*\)", "", s, flags=re.I)
    s = re.sub(r"-?\s*wholesale( bundle)?", "", s, flags=re.I)
    s = re.sub(r"\(exact plant shown\)", "", s, flags=re.I)
    s = re.sub(r"-\s*rare top cut.*$", " (top cut)", s, flags=re.I)
    s = re.sub(r"^rare\s+", "", s, flags=re.I)
    s = re.sub(r"-?\s*rare\s+(cutting|collector's plant|actual plant)", r" \1", s, flags=re.I)
    s = re.sub(r"\s*\brooted\b", "", s, flags=re.I)
    s = re.sub(r"top cut\s+(\d[\d\-]*)\s*leaves", r"top cut, \1 leaves", s, flags=re.I)
    s = re.sub(r"\bfrom tissue culture\b|\bfrom TC\b", "TC", s, flags=re.I)
    s = re.sub(r"\(\s*\)", "", s)
    s = re.sub(r"\bVariegated\b", "Variegata", s, flags=re.I)
    s = re.sub(r"\b(Variegata)(\s+Variegata)+", r"\1", s, flags=re.I)
    s = re.sub(r"(\w)\(", r"\1 (", s); s = re.sub(r"\(\s+", "(", s); s = re.sub(r"\s+\)", ")", s)
    s = re.sub(r"\s+", " ", s).strip(" -|")
    if s.count("'") % 2:
        s = re.sub(r"'$", "", s)
    return s[:1].upper() + s[1:], pkg


items = []
for p in P:
    if not p["images"]:
        continue
    name, pkg = parse(p["title"])
    low = name.lower()
    v = p["variants"][0]
    usd = float(v["price"])
    src = p["images"][0]["src"]
    items.append({"name": name, "title": p["title"],
                  "genus": next((g for g in GENERA if g in low), "Other").title(),
                  "pkg": pkg, "usd": usd, "egp": round(usd * RATE),
                  "available": any(x["available"] for x in p["variants"]),
                  "url": f"{BASE}/products/{p['handle']}",
                  "src": src + ("&" if "?" in src else "?") + "width=700",
                  "img": f"brt/img/{p['handle'][:70]}-{p['id']}.jpg"})


def dl(it):
    fn = f"{WS}/{it['img']}"
    if os.path.exists(fn):
        return
    try:
        raw = urllib.request.urlopen(urllib.request.Request(it["src"], headers=UA), timeout=60).read()
        im = Image.open(io.BytesIO(raw)).convert("RGB"); im.thumbnail((700, 700)); im.save(fn, quality=86)
    except Exception as e:
        print("photo failed:", it["name"], e); it["img"] = None


with cf.ThreadPoolExecutor(8) as ex:
    list(ex.map(dl, items))
json.dump(items, open(f"{WS}/brt/items.json", "w"), ensure_ascii=False, indent=1)
print("BanrakTonmai items:", len(items))

# ---- fill missing / reference-only photos in the existing catalog -------------------------------
FILL = {  # catalog or v22 name -> BanrakTonmai cleaned name
    "Alocasia venom": "Alocasia venom",
    "Philodendron 'Green Congo' variegata": "Philodendron green Congo Variegata",
    "Alocasia regal shield": "Alocasia Regal shields",
}
byname = {i["name"]: i for i in items}
adds = json.load(open(f"{WS}/additions_v22.json"))
cat = json.load(open(f"{WS}/data_clean.json"))
filled = []
for a in adds:
    b = byname.get(FILL.get(a["name"], ""))
    if b and b["img"] and (not a.get("img") or a.get("ref")):
        a["img"] = b["img"]; a.pop("ref", None); a["photo_source"] = "banraktonmai"; filled.append(a["name"])
for k, p, r in cat:
    if k != "ITEM":
        continue
    b = byname.get(FILL.get(p["name"], ""))
    if b and b["img"] and not p.get("img"):
        p["img"] = f"{WS}/{b['img']}"; p["photo_source"] = "banraktonmai"; filled.append(p["name"])
json.dump(adds, open(f"{WS}/additions_v22.json", "w"), ensure_ascii=False, indent=1)
json.dump(cat, open(f"{WS}/data_clean.json", "w"), ensure_ascii=False, indent=1)

cred = json.load(open(f"{WS}/photo_credits.json"))
for n in filled:
    cred.pop(n, None)
json.dump(cred, open(f"{WS}/photo_credits.json", "w"), ensure_ascii=False, indent=1)
print("photos filled from BanrakTonmai:", filled)
