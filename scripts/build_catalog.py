import json, os
from PIL import Image
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
import arabic_reshaper
from bidi.algorithm import get_display

pdfmetrics.registerFont(TTFont("AR", "/usr/share/fonts/truetype/noto/NotoSansArabic-Regular.ttf"))
pdfmetrics.registerFont(TTFont("ARB", "/usr/share/fonts/truetype/noto/NotoSansArabic-Bold.ttf"))
pdfmetrics.registerFont(TTFont("EN", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"))
pdfmetrics.registerFont(TTFont("ENB", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"))

def ar(t):
    return get_display(arabic_reshaper.reshape(t))

GREEN = colors.HexColor("#1F5135")
LIGHT = colors.HexColor("#F2F6F1")
ACCENT = colors.HexColor("#C9A227")
GREY = colors.HexColor("#5C6B60")

rows = json.load(open("/home/user/workspace/data.json"))
items = []
cur = None
for kind, payload, rn in rows:
    if kind == "HDR":
        cur = payload
    else:
        d = dict(payload)
        g = (d.get("genus") or cur or "Other")
        d["group"] = str(g).strip().title()
        items.append(d)

FIX = {"Aglonema": "Aglaonema", "Monstera": "Monstera", "Phillodendron": "Philodendron",
       "Sygnioum": "Syngonium", "Zamya": "Zamioculcas", "None": "Other"}
for d in items:
    d["group"] = FIX.get(d["group"], d["group"])

groups = {}
for d in items:
    groups.setdefault(d["group"], []).append(d)
for g in groups:
    groups[g].sort(key=lambda x: x["name"].lower())
order = sorted(groups)

# prepare thumbnails
os.makedirs("/home/user/workspace/thumbs", exist_ok=True)
def thumb(p):
    if not p or not os.path.exists(p):
        return None
    out = "/home/user/workspace/thumbs/" + os.path.splitext(os.path.basename(p))[0]+".jpg"
    if not os.path.exists(out):
        im = Image.open(p).convert("RGB")
        w, h = im.size
        ar_t = 55 / 33.0
        if w / h > ar_t:
            nw = int(h * ar_t); im = im.crop(((w - nw) // 2, 0, (w + nw) // 2, h))
        else:
            nh = int(w / ar_t); im = im.crop((0, max(0, (h - nh) // 2), w, max(0, (h - nh) // 2) + nh))
        im = im.resize((550, 330), Image.LANCZOS)
        im.save(out, quality=88)
    return out

W, H = A4
M = 15 * mm
c = canvas.Canvas("/home/user/workspace/Plant_Catalog_2026.pdf", pagesize=A4)
c.setTitle("Plant Catalog / كاتالوج النباتات")

total = len(items)
priced = [d for d in items if d.get("usd")]

# ---------- cover ----------
c.setFillColor(GREEN); c.rect(0, 0, W, H, fill=1, stroke=0)
c.setFillColor(ACCENT); c.rect(0, H - 8 * mm, W, 8 * mm, fill=1, stroke=0)
c.setFillColor(colors.white)
c.setFont("ENB", 44); c.drawCentredString(W / 2, H - 70 * mm, "PLANT CATALOG")
c.setFont("ARB", 30); c.drawCentredString(W / 2, H - 90 * mm, ar("كاتالوج النباتات"))
c.setStrokeColor(ACCENT); c.setLineWidth(1)
c.line(W / 2 - 40 * mm, H - 100 * mm, W / 2 + 40 * mm, H - 100 * mm)
c.setFont("EN", 13)
c.drawCentredString(W / 2, H - 115 * mm, "Tropical & Rare Houseplants  ·  Wholesale Price List")
c.setFont("AR", 12)
c.drawCentredString(W / 2, H - 126 * mm, ar("نباتات استوائية ونادرة - قائمة أسعار الجملة"))

bx, by, bw, bh = M + 15 * mm, 75 * mm, W - 2 * (M + 15 * mm), 45 * mm
c.setFillColor(colors.Color(1, 1, 1, 0.10)); c.roundRect(bx, by, bw, bh, 4 * mm, fill=1, stroke=0)
stats = [(str(total), "Varieties"), (str(len(order)), "Genera"), ("USD / EGP", "Currencies")]
for i, (v, l) in enumerate(stats):
    x = bx + bw * (i + 0.5) / 3
    c.setFillColor(colors.white); c.setFont("ENB", 20); c.drawCentredString(x, by + 25 * mm, v)
    c.setFillColor(ACCENT); c.setFont("EN", 10); c.drawCentredString(x, by + 15 * mm, l.upper())
c.setFillColor(colors.white); c.setFont("EN", 10)
c.drawCentredString(W / 2, 45 * mm, "Exchange rate applied: 1 USD = 52 EGP")
c.setFont("AR", 10); c.drawCentredString(W / 2, 36 * mm, ar("سعر التحويل المستخدم: 1 دولار = 52 جنيه"))
c.setFont("EN", 9); c.setFillColor(colors.Color(1, 1, 1, .7))
c.drawCentredString(W / 2, 22 * mm, "September 2026")
c.showPage()

# ---------- index ----------
c.setFillColor(GREEN); c.setFont("ENB", 22); c.drawString(M, H - M - 6 * mm, "Contents")
c.setFont("ARB", 15); c.drawRightString(W - M, H - M - 6 * mm, ar("المحتويات"))
c.setStrokeColor(ACCENT); c.line(M, H - M - 11 * mm, W - M, H - M - 11 * mm)
y = H - M - 24 * mm
col_x = [M, W / 2 + 3 * mm]
per = (len(order) + 1) // 2
for i, g in enumerate(order):
    x = col_x[i // per]
    yy = y - (i % per) * 8 * mm
    c.setFillColor(colors.HexColor("#22332A")); c.setFont("EN", 11); c.drawString(x + 2 * mm, yy, g)
    c.setFillColor(GREY); c.setFont("EN", 10)
    c.drawRightString(x + (W / 2 - M - 6 * mm), yy, f"{len(groups[g])} item" + ("s" if len(groups[g])>1 else ""))
    c.setStrokeColor(colors.HexColor("#E2E8E2")); c.setLineWidth(.5)
    c.line(x + 2 * mm, yy - 2.5 * mm, x + (W / 2 - M - 6 * mm), yy - 2.5 * mm)
c.setFont("EN", 8.5); c.setFillColor(GREY)
c.drawCentredString(W / 2, M, "Prices are per single plant unless a different package size is noted.")
c.showPage()

# ---------- cards ----------
COLS, ROWS = 3, 4
GAP = 6 * mm
CW = (W - 2 * M - (COLS - 1) * GAP) / COLS
CH = 58 * mm
page = 1

def header(gname, count):
    c.setFillColor(GREEN); c.rect(0, H - 22 * mm, W, 22 * mm, fill=1, stroke=0)
    c.setFillColor(colors.white); c.setFont("ENB", 16); c.drawString(M, H - 14 * mm, gname)
    c.setFillColor(ACCENT); c.setFont("EN", 9.5)
    c.drawRightString(W - M, H - 14 * mm, f"{count} VARIETIES")

def footer():
    c.setStrokeColor(colors.HexColor("#DDE4DD")); c.setLineWidth(.5)
    c.line(M, 14 * mm, W - M, 14 * mm)
    c.setFillColor(GREY); c.setFont("EN", 8)
    c.drawString(M, 9 * mm, "Plant Catalog 2026")
    c.drawRightString(W - M, 9 * mm, str(page))

def card(x, y, d):
    c.setFillColor(colors.white); c.setStrokeColor(colors.HexColor("#DFE6DF")); c.setLineWidth(.7)
    c.roundRect(x, y, CW, CH, 2.5 * mm, fill=1, stroke=1)
    ih = 32 * mm
    t = thumb(d.get("img"))
    if t:
        c.saveState()
        p = c.beginPath(); p.roundRect(x + .7, y + CH - ih, CW - 1.4, ih, 2.5 * mm)
        c.clipPath(p, stroke=0)
        c.drawImage(t, x + .7, y + CH - ih, CW - 1.4, ih)
        c.restoreState()
    else:
        c.setFillColor(LIGHT); c.rect(x + .7, y + CH - ih, CW - 1.4, ih, fill=1, stroke=0)
        c.setFillColor(GREY); c.setFont("EN", 8)
        c.drawCentredString(x + CW / 2, y + CH - ih / 2, "no photo")
    # name (wrap 2 lines)
    name = d["name"].replace("\n", " "); name = name[:1].upper() + name[1:]
    c.setFillColor(colors.HexColor("#22332A"))
    fs = 8.2
    c.setFont("ENB", fs)
    words = name.split()
    lines, line = [], ""
    for w in words:
        t2 = (line + " " + w).strip()
        if pdfmetrics.stringWidth(t2, "ENB", fs) > CW - 8 * mm and line:
            lines.append(line); line = w
        else:
            line = t2
    lines.append(line)
    if len(lines) > 2:
        lines = lines[:2]
        while pdfmetrics.stringWidth(lines[1] + "…", "ENB", fs) > CW - 8 * mm:
            lines[1] = lines[1][:-1]
        lines[1] += "…"
    ty = y + CH - ih - 6 * mm
    for ln in lines:
        c.drawString(x + 4 * mm, ty, ln); ty -= 4 * mm
    # price row
    usd, egp = d.get("usd"), d.get("egp")
    c.setFillColor(GREEN); c.setFont("ENB", 10)
    c.drawString(x + 4 * mm, y + 5.5 * mm, f"${usd:g}" if isinstance(usd, (int, float)) else "on request")
    if isinstance(egp, (int, float)):
        c.setFillColor(GREY); c.setFont("EN", 7.8)
        c.drawString(x + 4 * mm, y + 2 * mm, f"{egp:,.0f} EGP")
    pkg = d.get("pkg")
    if isinstance(pkg, (int, float)) and pkg and pkg != 1:
        c.setFillColor(ACCENT); c.setFont("ENB", 7.5)
        c.drawRightString(x + CW - 4 * mm, y + 5.5 * mm, f"pack of {pkg:g}")
    else:
        c.setFillColor(colors.HexColor("#9AA79D")); c.setFont("EN", 7.5)
        c.drawRightString(x + CW - 4 * mm, y + 5.5 * mm, "per plant")

for g in order:
    lst = groups[g]
    idx = 0
    while idx < len(lst):
        header(g, len(lst))
        top = H - 22 * mm - 8 * mm
        for r in range(ROWS):
            for col in range(COLS):
                if idx >= len(lst):
                    break
                x = M + col * (CW + GAP)
                y = top - (r + 1) * CH - r * GAP
                card(x, y, lst[idx]); idx += 1
        footer(); c.showPage(); page += 1

# ---------- price summary table ----------
def table_header():
    c.setFillColor(GREEN); c.rect(0, H - 22 * mm, W, 22 * mm, fill=1, stroke=0)
    c.setFillColor(colors.white); c.setFont("ENB", 15); c.drawString(M, H - 14 * mm, "Full Price List")
    c.setFont("ARB", 12); c.drawRightString(W - M, H - 14 * mm, ar("قائمة الأسعار الكاملة"))

cols = [M, M + 92 * mm, M + 130 * mm, M + 152 * mm]
def col_titles(y):
    c.setFillColor(LIGHT); c.rect(M, y - 2 * mm, W - 2 * M, 7 * mm, fill=1, stroke=0)
    c.setFillColor(GREEN); c.setFont("ENB", 8.5)
    for t, x in zip(["VARIETY", "GENUS", "PACK", "USD"], cols):
        c.drawString(x + 1.5 * mm, y, t)
    c.setFillColor(GREEN); c.setFont("ENB", 8.5); c.drawRightString(W - M - 1.5 * mm, y, "EGP")

y = 0
first = True
i = 0
flat = [(g, d) for g in order for d in groups[g]]
while i < len(flat):
    table_header()
    y = H - 34 * mm
    col_titles(y)
    y -= 8 * mm
    shade = False
    while i < len(flat) and y > 18 * mm:
        g, d = flat[i]
        if shade:
            c.setFillColor(colors.HexColor("#FAFBFA")); c.rect(M, y - 2 * mm, W - 2 * M, 6 * mm, fill=1, stroke=0)
        shade = not shade
        nm = d["name"].replace("\n", " "); nm = nm[:1].upper() + nm[1:]
        while pdfmetrics.stringWidth(nm, "EN", 8) > 88 * mm:
            nm = nm[:-2]
        c.setFillColor(colors.HexColor("#22332A")); c.setFont("EN", 8)
        c.drawString(cols[0] + 1.5 * mm, y, nm)
        c.setFillColor(GREY)
        c.drawString(cols[1] + 1.5 * mm, y, g[:16])
        pkg = d.get("pkg")
        c.drawString(cols[2] + 1.5 * mm, y, f"{pkg:g}" if isinstance(pkg, (int, float)) else "-")
        u, e = d.get("usd"), d.get("egp")
        c.setFillColor(colors.HexColor("#22332A"))
        c.drawString(cols[3] + 1.5 * mm, y, f"${u:g}" if isinstance(u, (int, float)) else "on request")
        c.drawRightString(W - M - 1.5 * mm, y, f"{e:,.0f}" if isinstance(e, (int, float)) else "-")
        y -= 6 * mm
        i += 1
    footer(); c.showPage(); page += 1

c.save()
print("pages", page)
