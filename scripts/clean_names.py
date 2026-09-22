"""Normalize plant names and genera in data.json -> data_clean.json"""
import json, re

rows = json.load(open("/home/user/workspace/data.json"))

# token-level fixes (whole words, case-insensitive)
WORD = {
    "aglonema": "Aglaonema", "phillo": "Philodendron", "philo": "Philodendron",
    "philo.": "Philodendron", "phillodendron": "Philodendron", "p.": "Philodendron",
    "sc.": "Scindapsus", "sygnioum": "Syngonium", "zamya": "Zamioculcas",
    "adansoni": "adansonii", "princes": "Princess", "beuty": "Beauty",
    "buttfly": "Butterfly", "wijard": "Wizard", "sulver": "Silver",
    "balck": "black", "volkadot": "Polka Dot", "mahrani": "Maharani",
    "chanterii": "chantrieri", "scalperum": "scalprum", "glorosium": "gloriosum",
    "gloriousum": "gloriosum", "tricollor": "tricolor", "colour": "Color",
    "betwing": "Bat Wing", "crame": "Creme", "brulee": "Brulee",
    "flobe": "'Florida Beauty'", "haderaceum": "hederaceum",
    "plaminggiana": "plumbea", "warszewiczii": "warscewiczii",
    "weple": "Whipple", "wiple": "Whipple", "poly": "poly",
}

# full-name overrides (lowercased, whitespace-collapsed key)
FULL = {
    "ؤ integrifolia": ("Tacca integrifolia", "Tacca"),
    "tetra sperma": ("Rhaphidophora tetrasperma", "Rhaphidophora"),
    "rhaphidophora": ("Rhaphidophora sp.", "Rhaphidophora"),
    "watermelon peperomia": ("Peperomia argyreia (Watermelon)", "Peperomia"),
    "pilea paperomia": ("Pilea / Peperomia sp.", "Pilea"),
    "begonian semua jenis": ("Begonia (mixed varieties)", "Begonia"),
    "begonia rex motherplan": ("Begonia rex (mother plant)", "Begonia"),
    "zamya balck": ("Zamioculcas zamiifolia (black)", "Zamioculcas"),
    "dragon scale aurea": ("Alocasia baginda 'Dragon Scale' aurea", "Alocasia"),
    "red tiger x zara michelle": ("Anthurium 'Red Tiger' x 'Zara Michelle'", "Anthurium"),
    "flobe x mayoy": ("Philodendron 'Florida Beauty' x mayoi", "Philodendron"),
    "glorosium dark foam": ("Philodendron gloriosum 'Dark Form'", "Philodendron"),
    "domesticum": ("Philodendron domesticum", "Philodendron"),
    "phillo domesticum": ("Philodendron domesticum", "Philodendron"),
    "phillodendron domesticum": ("Philodendron domesticum", "Philodendron"),
    "philo. rinf of fire": ("Philodendron 'Ring of Fire'", "Philodendron"),
    "philo pink princes galaxy": ("Philodendron 'Pink Princess' galaxy", "Philodendron"),
    "philo. pink princes marble": ("Philodendron 'Pink Princess' marble", "Philodendron"),
    "alocasia psuedo sanderian a pink variegated": ("Alocasia pseudosanderiana pink variegated", "Alocasia"),
    "alocasia ’helian‘": ("Alocasia 'Helian'", "Alocasia"),
    "dieffenbachia ’sublime‘": ("Dieffenbachia 'Sublime'", "Dieffenbachia"),
    "anthurium clarinerviumhybrid sulanjana": ("Anthurium clarinervium hybrid 'Sulanjana'", "Anthurium"),
    "haderasium": ("Hoya sp. (Haderasium)", "Hoya"),
    "jose buono": ("Jewel orchid 'Jose Buono'", "Jewel orchid"),
    "koreaseus": ("Jewel orchid 'Koreaseus'", "Jewel orchid"),
    "mega sperma": ("Jewel orchid 'Mega Sperma'", "Jewel orchid"),
    "jewel cystorchis": ("Jewel orchid Cystorchis", "Jewel orchid"),
    "jewel green orchid": ("Jewel orchid (green)", "Jewel orchid"),
    "jewel red orchid": ("Jewel orchid (red)", "Jewel orchid"),
    "prakensis": ("Philodendron sp. (Prakensis)", "Philodendron"),
    "purbesi sp jabar": ("Philodendron sp. (Purbesi, Jabar)", "Philodendron"),
    "philodendron ei choco red": ("Philodendron 'El Choco Red'", "Philodendron"),
    "hoya sigilatis splash": ("Hoya sigillatis splash", "Hoya"),
    "hoya bencai splash": ("Hoya bencalensis splash", "Hoya"),
    "hoya crassipeteolata variegata": ("Hoya crassipetiolata variegata", "Hoya"),
    "monstera delocasia": ("Monstera deliciosa", "Monstera"),
    "monstera peru karstenianum": ("Monstera karstenianum 'Peru'", "Monstera"),
    "cordyline giganteum 'blizzard'": ("Cordyline 'Giant Blizzard'", "Cordyline"),
    "alocasia yucatan pink": ("Alocasia 'Yucatan Princess' pink", "Alocasia"),
    "alocasia yucatan pink variegata": ("Alocasia 'Yucatan Princess' pink variegata", "Alocasia"),
    "alocasia heart ballon var": ("Alocasia 'Heart Balloon' variegata", "Alocasia"),
    "alocasia odora variegated batik": ("Alocasia odora 'Batik' variegated", "Alocasia"),
    "calathea picturata \"crimson\"": ("Calathea picturata 'Crimson'", "Calathea"),
    "dieffenbachia avocado": ("Dieffenbachia 'Avocado'", "Dieffenbachia"),
    "dieffenbachia white blizzard": ("Dieffenbachia 'White Blizzard'", "Dieffenbachia"),
    "anthurium bvit": ("Anthurium 'BVIT'", "Anthurium"),
    "anthurium doroyaki": ("Anthurium 'Dorayaki'", "Anthurium"),
    "anthurium modeanum": ("Anthurium moodeanum", "Anthurium"),
    "anthurium poldipolium": ("Anthurium podophyllum", "Anthurium"),
    "anthurium peitchi": ("Anthurium 'Peitchi'", "Anthurium"),
    "aglaonema a019": ("Aglaonema 'A019'", "Aglaonema"),
    "aglaonema a029": ("Aglaonema 'A029'", "Aglaonema"),
    "calathea c063": ("Calathea 'C063'", "Calathea"),
    "aglonema red vein": ("Aglaonema 'Red Vein'", "Aglaonema"),
}

GENUS_FIX = {"Aglonema": "Aglaonema", "Phillodendron": "Philodendron",
             "Sygnioum": "Syngonium", "Zamya": "Zamioculcas", "None": "Other",
             "Jewel": "Jewel orchid", "Tetra": "Rhaphidophora",
             "Watermelon": "Peperomia", "Zebrina": "Tradescantia zebrina",
             "Domesticum": "Philodendron"}

ABBREV = {"var": "variegata", "var.": "variegata", "sp": "sp.", "spp": "spp."}


def fix_words(name):
    out = []
    for w in name.split():
        core = w.strip()
        low = core.lower().strip("'\u2019\u2018")
        if low in WORD:
            rep = WORD[low]
            # preserve original capitalisation style for species epithets
            out.append(rep)
        elif low in ABBREV:
            out.append(ABBREV[low])
        else:
            out.append(core)
    s = " ".join(out)
    s = re.sub(r"\s+", " ", s).replace(" ,", ",").strip()
    s = s.replace("’", "'").replace("‘", "'").replace("×", "x").replace("’", "'")
    s = re.sub(r"'\s+'", "' '", s)
    s = re.sub(r"'\s*([^']*?)\s*'", lambda m: "'" + m.group(1).strip() + "'", s)
    if s:
        s = s[0].upper() + s[1:]
    return s


cur = None
clean = []
review = []
for kind, payload, rn in rows:
    if kind == "HDR":
        cur = payload
        clean.append([kind, payload, rn])
        continue
    d = dict(payload)
    raw = " ".join(str(d["name"]).split())
    key = raw.lower()
    genus = str(d.get("genus") or cur or "Other").strip().title()
    genus = GENUS_FIX.get(genus, genus)
    if key in FULL:
        new, genus = FULL[key]
    else:
        new = fix_words(raw)
    # dedupe repeated genus word: "Philodendron Philodendron x"
    new = re.sub(r"\b(\w+)\s+\1\b", r"\1", new, flags=re.I)
    if new != raw:
        review.append((raw, new))
    d["name"] = new
    d["genus"] = genus
    clean.append([kind, d, rn])

json.dump(clean, open("/home/user/workspace/data_clean.json", "w"), ensure_ascii=False, indent=1)
with open("/home/user/workspace/name_changes.md", "w") as f:
    f.write("# Name normalization log / سجل تحسين الأسماء\n\n")
    f.write(f"Total entries renamed: {len(review)}\n\n| Original | Corrected |\n|---|---|\n")
    for a, b in sorted(review, key=lambda x: x[0].lower()):
        f.write(f"| {a} | {b} |\n")
print(len(review), "renamed")
for a, b in review[:20]:
    print(a, "->", b)
