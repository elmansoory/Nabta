"""Merge 'The Plants Price 22' PDF price list into the catalog data.

- fills USD/EGP for catalog items whose name matches an entry in the new list
- produces additions_v22.json for varieties not present in the photo catalog
  (duplicate listings collapsed into a min-max price range)
"""
import json, re, collections

RATE = 52
cat = json.load(open("/home/user/workspace/data_clean.json"))
pl = json.load(open("/home/user/workspace/pricelist.json"))

GEN = [("anthurium", ["a .", "a.", "anthrium", "anthurim"]), ("philodendron", ["phillo", "philo", "philo.", "p.", "phillodendron", "philodendrom"]),
       ("scindapsus", ["sc."]), ("aglaonema", ["aglonema"]), ("syngonium", ["sygnioum", "syngonuim"])]
SPELL = {"clari nervium": "clarinervium", "clarinerveium": "clarinervium", "cristalinum": "crystallinum",
         "cuculata": "cucullata", "culculata": "cucullata", "betwing": "bat wing", "plaaminggiana": "plumbea",
         "doryaki": "dorayaki", "sulamjana": "sulanjana", "wenti": "wentii", "variegated": "variegata",
         "luxry": "luxurians", "victhi": "veitchii", "warocqueanum": "warocqueanum", "orhchid": "Orchid", "comfetti": "Confetti",
         "hybird": "hybrid", "pepromia": "Peperomia", "silverdrragon": "Silver Dragon",
         "luxuryan": "luxurians", "veitchiii": "veitchii", "waroq": "warocqueanum",
         "paraisoverde": "Paraiso Verde", "bigonia": "Begonia", "blody": "bloody",
         "epicia": "Episcia", "homalomena": "Homalomena", "burlemarx": "Burle Marx",
         "silverdragon": "Silver Dragon", "regalshield": "regal shield", "golden bon": "golden bone"}


def pretty(name):
    s = re.sub(r"\s+", " ", name).strip()
    s = s.replace("’", "'").replace("“", "'").replace("”", "'").replace("×", "x")
    low = s.lower()
    for full, abbrs in GEN:
        if low.startswith(full):
            continue
        for a in sorted(abbrs, key=len, reverse=True):
            if low.startswith(a):
                s = full.title() + " " + s[len(a):].lstrip(". ")
                low = s.lower()
                break
    for a, b in SPELL.items():
        s = re.sub(a, b, s, flags=re.I)
    # balance stray opening quote: Alocasia 'Bambino -> Alocasia 'Bambino'
    s = re.sub(r"\s*\d+\s*\$\s*$", "", s)
    s = re.sub(r"(\D)(\d+)\$$", r"\1", s)
    if s.count("'") % 2 == 1:
        s += "'"
    s = s[:1].upper() + s[1:]
    return s


def key(name):
    s = pretty(name).lower()
    s = re.sub(r"[^a-z0-9 ]", " ", s)
    stop = {"sp", "spp", "the", "var"}
    return " ".join(sorted(set(w for w in s.split() if w not in stop)))


KNOWN = """aglaonema alocasia anthurium ardisia begonia caladium calathea carica cercestis ceropegia
christia cocos colocasia cordyline ctenanthe curcuma dieffenbachia dionaea dracaena drimiopsis
echeveria epipremnum euphorbia ficus graptophyllum homalomena hoya labisia maranta monstera musa
peperomia philodendron pilea plinia radermachera rhaphidophora schismatoglottis scindapsus
sonerila spathiphyllum syngonium tacca thaumatophyllum xanthosoma zamioculcas""".split()


RECLASS = {
    "anthurium": ["black emerald", "bloody night", "carla original", "clarinervium", "crystallinum",
                  "docblok", "dorayaki", "kos rc", "luxurians", "michelle", "papi x", "purple tiger",
                  "red ghost", "red tiger", "rvdp", "veitchii", "warocqueanum", "zara michelle"],
    "philodendron": ["gigas", "paraiso verde", "pink princess", "burle marx"],
    "alocasia": ["golden bone", "golden bonee", "silver dragon"],
    "syngonium": ["milk confetti"],
    "tradescantia": ["zebrina"],
    "jewel orchid": ["jewel"],
    "musa": ["banana"],
    "ceropegia": ["string of heart"],
    "episcia": ["episcia"],
    "aquatic plants": ["lotus", "water lily"],
}


def guess_genus(name):
    words = [re.sub(r"[^a-z]", "", w.lower()) for w in name.split()]
    for w in words:
        if w in KNOWN:
            return w.title()
    if "moss" in words or "terrarium" in words:
        return "Terrarium & moss"
    low = name.lower()
    for g, keys in RECLASS.items():
        if any(k in low for k in keys):
            return g.title() if g != "jewel orchid" else "Jewel orchid"
    return "Other / hybrids"


catkeys = collections.defaultdict(list)
for k, p, r in cat:
    if k == "ITEM":
        catkeys[key(p["name"])].append(p)

groups = collections.OrderedDict()
for n, pkg, u in pl:
    groups.setdefault(key(n), {"name": pretty(n), "pkg": pkg, "prices": []})
    if u:
        groups[key(n)]["prices"].append(u)

filled, additions = 0, []
for k, g in groups.items():
    prices = sorted(set(g["prices"]))
    if k in catkeys:
        for p in catkeys[k]:
            if not p.get("usd") and prices:
                p["usd"] = prices[0]
                p["egp"] = prices[0] * RATE
                p["source"] = "v22"
                filled += 1
    else:
        gname = guess_genus(g["name"])
        nm = g["name"]
        first = gname.split()[0].lower()
        if first not in nm.lower() and gname not in ("Other / hybrids", "Terrarium & moss", "Aquatic Plants", "Jewel orchid"):
            nm = gname.split()[0] + " " + nm[0].lower() + nm[1:]
        additions.append({"srckey": k, "name": nm, "genus": gname,
                          "pkg": g["pkg"], "lo": prices[0] if prices else None,
                          "hi": prices[-1] if prices else None})

photos = json.load(open("/home/user/workspace/v22_imgmap.json"))
pkeys = {}
for n, f in photos.items():
    pkeys.setdefault(key(n), f)
for a in additions:
    a["img"] = pkeys.get(a["srckey"]) or pkeys.get(key(a["name"]))

# collapse duplicates created by name normalisation (golden bone / bonee, waroc / warocqueanum)
merged = {}
SPELLDUP = {"bonee": "bone"}
for a in additions:
    kk = key(" ".join(SPELLDUP.get(w, w) for w in a["name"].split()))
    if kk in merged:
        m = merged[kk]
        lows = [v for v in (m["lo"], a["lo"]) if v]
        his = [v for v in (m["hi"], a["hi"]) if v]
        m["lo"] = min(lows) if lows else None
        m["hi"] = max(his) if his else None
        m["img"] = m["img"] or a["img"]
        if len(a["name"]) > len(m["name"]):
            m["name"] = a["name"]
        m["name"] = " ".join(SPELLDUP.get(w, w) for w in m["name"].split())
    else:
        merged[kk] = a
additions = list(merged.values())
for k, p in catkeys.items():
    for it in p:
        if not it.get("img") and k in pkeys:
            it["img"] = "/home/user/workspace/" + pkeys[k]
            it["photo_source"] = "v22"

additions.sort(key=lambda d: (d["genus"].lower(), d["name"].lower()))
json.dump(cat, open("/home/user/workspace/data_clean.json", "w"), ensure_ascii=False, indent=1)
json.dump([{k2: v for k2, v in a.items() if k2 != "srckey"} for a in additions], open("/home/user/workspace/additions_v22.json", "w"), ensure_ascii=False, indent=1)
print("photos attached:", sum(1 for a in additions if a["img"]))
print("prices filled:", filled, "| additions:", len(additions),
      "| with price:", sum(1 for a in additions if a["lo"]))
gen = collections.Counter(a["genus"] for a in additions)
print(gen.most_common(12))
