#!/usr/bin/env python3
"""Static site generator: reads data/*.json and writes dist/ (bilingual AR/EN, SEO + AI-ready)."""
import hashlib
COUNTRIES_ALL = ("ae", "eg", "tn", "kw")
import datetime as dt
import itertools
import os
import json
import re
import shutil
import sys
from collections import defaultdict
from pathlib import Path
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

if os.environ.get("COUNTRY", "").strip() and "_FR_DONE" not in globals():  # a country with its own French edition: re-run this file with the English slot rewritten to French
    import fr_patch
    if fr_patch.lang2_of(os.environ["COUNTRY"].strip()) in ("fr", "para"):
        fr_patch.run(__file__, os.environ["COUNTRY"].strip())
        sys.exit(0)

import content
GUIDES = {}  # electronics buying guides are not used by the para (beauty/care) sections
from jinja2 import Environment, FileSystemLoader, select_autoescape
from markupsafe import Markup

ROOT = Path(__file__).parent
COUNTRY = os.environ.get("COUNTRY", "").strip()  # "" = the whole site (Saudi under /sa/ + root files); "ae"/"eg" = that country only
IS_ROOT = not COUNTRY                             # root build: also writes the country chooser, redirects, robots, sitemap index, shared static
COUNTRY = COUNTRY or "sa"                         # every build is a country living in /<code>/
DROOT = ROOT / COUNTRY  # country data root (config.json + data/*.json): every country, Saudi included, lives in its own folder in this repo
OUT_ROOT = ROOT / "dist"
OUT = OUT_ROOT / COUNTRY
shutil.rmtree(OUT_ROOT if IS_ROOT else OUT, ignore_errors=True)  # never leave stale pages from earlier builds
LANGS = ("ar", "en")


def load(path):
    p = DROOT / path
    if not p.exists():
        sys.exit(f"Missing {path}. Run: python3 update_prices.py")
    return json.loads(p.read_text(encoding="utf-8"))


cfg = load("config.json")
catalog = load("data/products.json")
offers_data = load("data/offers.json")
history = load("data/history.json")

BASE = cfg["base_url"].rstrip("/")
if COUNTRY == "sa":
    BASE += "/sa"
SITE = BASE[: -len("/" + COUNTRY)]  # domain root (shared /static)
REPL = list(cfg.get("replace", []))
if COUNTRY == "sa":
    REPL += [('hreflang="ar"', 'hreflang="ar-SA"'), ('hreflang="en"', 'hreflang="en-SA"')]
CUR_AR, CUR_EN = cfg.get("currency_ar", "ر.س"), cfg.get("currency", "SAR")
UPDATED = offers_data["updated"]
UPDATED_DATE = UPDATED[:10]
VALID_UNTIL = (dt.date.fromisoformat(UPDATED_DATE) + dt.timedelta(days=1)).isoformat()
NAME = cfg["site_name"]

T = {
    "ar": {
        "home": "الرئيسية", "about": "من نحن", "methodology": "المنهجية", "privacy": "الخصوصية", "data": "البيانات المفتوحة",
        "updated": "آخر تحديث", "lowest": "أقل سعر", "at": "في", "stores_n": "متاجر", "products_n": "منتج",
        "pick_country": "الدولة", "pick_lang": "اللغة", "nav_label": "الأقسام",
        "categories": "الأقسام", "top_drops": "أكبر انخفاضات الأسعار هذا الأسبوع",
        "no_drops": "لا توجد انخفاضات مسجّلة هذا الأسبوع.", "all_products": "كل المنتجات",
        "go_store": "اذهب إلى المتجر", "in_stock": "متوفر", "out_stock": "غير متوفر", "store": "المتجر",
        "price": "السعر", "status": "الحالة", "history": "تاريخ السعر (آخر 30 يوماً)", "specs": "المواصفات",
        "faq": "أسئلة شائعة", "compare_with": "قارن مع منتجات أخرى", "related": "منتجات مشابهة",
        "disclosure": "الأسعار تُجمع من صفحات المتاجر وتُحدَّث يومياً وقد تتغير في المتجر. قد نحصل على عمولة عند الشراء عبر بعض الروابط، دون أي تأثير على الأسعار أو الترتيب.",
        "demo": "نسخة تجريبية قيد الاختبار: الأسعار حقيقية لكنها غير نهائية وقد تحتوي أخطاء. راجع سعر المتجر قبل الشراء.",
        "low30": "أدنى سعر خلال 30 يوماً", "high30": "أعلى سعر خلال 30 يوماً", "vs": "مقابل",
        "other_lang": "English", "other_lang_code": "en", "min_note": "نعرض المنتجات التي يزيد سعرها عن 100 ريال سعودي.",
        "feature": "الميزة", "best_price": "أفضل سعر", "cheapest_store": "أرخص متجر", "week_change": "تغيّر 7 أيام",
        "contact": "تواصل معنا", "featured": "منتجات مختارة", "compared_stores": "نقارن الأسعار من", "search_ph": "ابحث عن جوال أو تلفزيون أو ثلاجة أو مكيف", "no_match": "لا توجد نتائج مطابقة", "search": "بحث", "prev": "السابق", "next": "التالي", "page": "صفحة",
    },
    "en": {
        "home": "Home", "about": "About", "methodology": "Methodology", "privacy": "Privacy", "data": "Data (JSON)",
        "updated": "Last updated", "lowest": "Lowest price", "at": "at", "stores_n": "stores", "products_n": "products",
        "pick_country": "Country", "pick_lang": "Language", "nav_label": "Categories",
        "categories": "Categories", "top_drops": "Biggest price drops this week",
        "no_drops": "No price drops recorded this week.", "all_products": "All products",
        "go_store": "Go to store", "in_stock": "In stock", "out_stock": "Out of stock", "store": "Store",
        "price": "Price", "status": "Status", "history": "Price history (last 30 days)", "specs": "Specifications",
        "faq": "Frequently asked questions", "compare_with": "Compare with other products", "related": "Related products",
        "disclosure": "Prices are collected from the stores' pages, update daily and may change at the store. We may earn a commission on purchases made through some links, with no effect on prices or ranking.",
        "demo": "Test build: prices are real but not final and may contain errors. Check the store price before buying.",
        "low30": "30-day low", "high30": "30-day high", "vs": "vs",
        "other_lang": "العربية", "other_lang_code": "ar", "min_note": "We list products priced above SAR 100.",
        "feature": "Feature", "best_price": "Best price", "cheapest_store": "Cheapest store", "week_change": "7-day change",
        "contact": "Contact us", "featured": "Featured products", "compared_stores": "Prices compared across", "search_ph": "Search phones, TVs, fridges, ACs", "no_match": "No matching products", "search": "Search", "prev": "Previous", "next": "Next", "page": "Page",
    },
}


DEC = int(cfg.get("decimals", 0))


def money(v, lang):
    s = f"{v:,.{DEC}f}"
    return f"{s} ر.س" if lang == "ar" else f"SAR {s}"


def plain_money(v):
    return f"SAR {v:,.{DEC}f}"


def aff_url(o):
    url = o["url"]
    a = cfg.get("affiliate", {}).get(o["store"])
    if url and a and a.get("value"):
        u = urlparse(url)
        q = dict(parse_qsl(u.query))
        q[a["param"]] = a["value"]
        url = urlunparse(u._replace(query=urlencode(q)))
    return url


# ---------- data prep ----------
cats = {c["slug"]: c for c in cfg["categories"]}
by_pid = defaultdict(list)
for o in offers_data["offers"]:
    by_pid[o["product_id"]].append(o)


def series_for(pid):
    days = defaultdict(list)
    for d in history.get(pid, {}).values():
        for date, price in d.items():
            days[date].append(price)
    return sorted((d, min(v)) for d, v in days.items())


def sparkline(series, lang):
    if len(series) < 5:  # two or three days draw a meaningless straight line: say tracking has just started instead
        return ""
    w, h, pad = 600, 160, 26
    vals = [v for _, v in series]
    lo, hi = min(vals), max(vals)
    rng = (hi - lo) or 1
    pts = []
    for i, (_, v) in enumerate(series):
        x = pad + i * (w - 2 * pad) / (len(series) - 1)
        y = h - pad - (v - lo) / rng * (h - 2 * pad)
        pts.append(f"{x:.1f},{y:.1f}")
    label = (f"تغير أقل سعر من {money(series[0][1], lang)} إلى {money(series[-1][1], lang)}" if lang == "ar"
             else f"Lowest price moved from {plain_money(series[0][1])} to {plain_money(series[-1][1])}")
    return Markup(
        f'<svg viewBox="0 0 {w} {h}" role="img" aria-label="{label}" class="spark" direction="ltr">'
        f'<polyline points="{" ".join(pts)}" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linejoin="round"/>'
        f'<text x="{pad}" y="14" font-size="12" fill="currentColor">{plain_money(hi)}</text>'
        f'<text x="{pad}" y="{h - 6}" font-size="12" fill="currentColor">{plain_money(lo)}</text></svg>')


MIN_STORES = cfg.get("min_stores", 3)  # thin single-store pages add no comparison value
def short_slug(s, n=64):
    """Very long marketplace titles make URLs/paths too long (Windows 260-char limit) - cut at a word edge, keep it unique with a hash."""
    if len(s) <= n:
        return s
    import hashlib
    cut = s[:n].rsplit("-", 1)[0] or s[:n]
    return f"{cut}-{hashlib.md5(s.encode()).hexdigest()[:6]}"


NOUN_AR = {"phones": "جوال", "laptops": "لابتوب", "tvs": "تلفزيون", "fridges": "ثلاجة", "acs": "مكيف", "microwaves": "ميكروويف", "washers": "غسالة",
           "ovens": "فرن", "watches": "ساعة ذكية", "earbuds": "سماعات", "consoles": "جهاز", "printers": "طابعة", "consumables": "حبر", "networking": "جهاز شبكات", "storage": "وحدة تخزين", "components": "قطعة كمبيوتر", "desktops": "كمبيوتر مكتبي", "peripherals": "ملحق", "audio": "سماعة صوت", "cameras": "كاميرا", "vacuums": "مكنسة", "kitchen": "جهاز مطبخ", "home": "جهاز منزلي", "gaming": "مستلزم ألعاب", "power": "جهاز طاقة", "tools": "أداة", "smart-home": "جهاز ذكي", "other": "منتج"}
NOUN_HAS = {"phones": r"phone|iphone|galaxy|smartphone|جوال", "laptops": r"laptop|notebook|macbook|tablet|ipad|\bpad\b|\btab\b|لابتوب", "tvs": r"\btv\b|monitor|television|تلفزيون|شاشة",
            "fridges": r"refrigerator|fridge|freezer|ثلاجة", "acs": r"air ?condition|split|\bac\b|مكيف", "microwaves": r"microwave|ميكروويف", "washers": r"wash|غسالة",
            "ovens": r"oven|فرن", "watches": r"watch|ساعة", "earbuds": r"airpods|buds|headphone|earphone|سماعة|wh-|wf-|tune|soundcore|freebuds", "consoles": r"playstation|xbox|switch|steam deck|console", "printers": r"printer|imprimante|scanner|epson|canon", "consumables": r"toner|ink|cartouche|encre", "networking": r"router|routeur|switch|wifi|modem|tp-link|access point", "storage": r"ssd|hdd|disque|usb|memory|sd", "components": r"gpu|graphique|processeur|ryzen|rtx|ddr|carte mere|alimentation|boitier", "desktops": r"pc|desktop|imac|all in one|bureau", "peripherals": r"clavier|souris|webcam|keyboard|mouse|casque|manette", "audio": r"enceinte|speaker|barre de son|soundbar|parleur", "cameras": r"camera|drone|gopro|reflex|surveillance", "vacuums": r"aspirateur|vacuum|karcher|nettoyeur", "kitchen": r"friteuse|cafetiere|bouilloire|mixeur|blender|robot|grille|expresso", "home": r"chauffe|ventilateur|radiateur|fer a|seche|lisseur|rasoir|tondeuse", "gaming": r"gaming|gamer|jeu", "power": r"power|chargeur|onduleur|batterie|solaire", "tools": r"perceuse|visseuse|meuleuse|scie|compresseur", "smart-home": r"serrure|alarme|detecteur|gps|thermostat", "other": r"."}


def tidy_en(name, limit=72):
    """Marketplace titles run to 200+ characters of keyword stuffing. Keep the leading, informative segments and drop the tail."""
    n = re.sub(r"\s+", " ", name).strip(" -,|")
    if len(n) <= limit:
        return n
    parts = re.split(r"\s+[-–|]\s+|,\s+|\s+\|\s+", n)
    out = parts[0]
    for seg in parts[1:]:
        if len(out) + 2 + len(seg) > limit:
            break
        out += ", " + seg
    if len(out) > limit + 10:
        out = out[:limit + 10].rsplit(" ", 1)[0]
    return out.strip(" -,|")


def tidy_ar(en, cat):
    return en if re.search(NOUN_HAS.get(cat, "$^"), en, re.I) or cat not in NOUN_AR else f"{NOUN_AR[cat]} {en}"


# neutral coloured letter badges (not the stores' trademarked logos): (letter, background, text colour)
STORE_BADGE = {"almanea": ("A", "#C8102E", "#fff"), "extra": ("e", "#FFD100", "#1a1a1a"), "noon": ("n", "#FEE600", "#1a1a1a"), "amazon-sa": ("a", "#FF9900", "#1a1a1a"),
               "jarir": ("J", "#E31E24", "#fff"), "blackbox": ("B", "#222222", "#fff"), "saeel": ("S", "#00A37A", "#fff"), "trendyol": ("T", "#F27A1A", "#fff"),
               "carrefour-ksa": ("C", "#004E9F", "#fff"), "sharafdg": ("S", "#E4002B", "#fff")}

def _keep_images():
    """File budget (Cloudflare Pages: 20k files): ship only the product images each country actually uses."""
    import csv as _csv
    keep = set()
    for cc in [""] + list(COUNTRIES_ALL):
        base = ROOT / cc if cc else ROOT
        try:
            cap = int(json.loads((base / "config.json").read_text(encoding="utf-8")).get("images_max", 0)) if cc else 0
            st = {}
            with (base / "feeds" / "inbox" / "scraped.csv").open(encoding="utf-8", newline="") as fh:
                for r in _csv.DictReader(fh):
                    st.setdefault(r["product_id"], set()).add(r["store"])
        except Exception:
            continue
        want = sorted(((len(v), pid) for pid, v in st.items() if len(v) >= 2), key=lambda x: (-x[0], x[1]))
        if cap:
            want = want[:cap]
        keep |= {hashlib.md5(pid.encode("utf-8")).hexdigest()[:12] for _, pid in want}
    return keep


KEEP_IMG = _keep_images()
try:
    IMG_CDN = (json.loads((ROOT / "config.json").read_text(encoding="utf-8")).get("img_cdn") or "").rstrip("/")
except Exception:
    IMG_CDN = ""


def _unpack_icons():
    """Store logos + brand logos ship as one JSON pack (scraper/icons_pack.json); unpack into static/img/{s,b}/ when missing."""
    pk = ROOT / "scraper" / "icons_pack.json"
    if not pk.exists():
        return
    import base64 as _b64
    for rel, data in json.loads(pk.read_text(encoding="utf-8")).items():
        dst = ROOT / "static" / "img" / rel
        if not dst.exists():
            dst.parent.mkdir(parents=True, exist_ok=True)
            dst.write_bytes(_b64.b64decode(data))


_unpack_icons()

_BADGE_COLORS = ["#0B6B5B", "#C8102E", "#1D4ED8", "#B45309", "#6D28D9", "#0E7490", "#BE185D", "#4D7C0F"]


def store_badge(store, name):
    """Store logo (favicon saved under static/img/s/) when we have one, else a coloured initial."""
    if (ROOT / "static" / "img" / "s" / f"{store}.png").exists():
        return ("img", f"{SITE}/static/img/s/{store}.png", "")
    c = _BADGE_COLORS[int(hashlib.md5(store.encode()).hexdigest(), 16) % len(_BADGE_COLORS)]
    return ((name or store)[:1].upper(), c, "#fff")


def brand_logo(name):
    """URL of the brand's monochrome logo (static/img/b/<slug>.svg) or None."""
    k = re.sub(r"[^a-z0-9]", "", (name or "").lower())
    return f"{SITE}/static/img/b/{k}.svg" if k and (ROOT / "static" / "img" / "b" / f"{k}.svg").exists() else None


def brand_initial(name):
    return ((name or "?").strip()[:1] or "?").upper()
items = []
for p in catalog:
    offs = by_pid.get(p["id"])
    if not offs or len({o["store"] for o in offs}) < MIN_STORES:
        continue
    offs = sorted(offs, key=lambda o: (not o["in_stock"], o["price"]))
    offs = [dict(o, store_name=cfg["stores"][o["store"]]["name"], link=aff_url(o), badge=store_badge(o["store"], cfg["stores"][o["store"]]["name"])) for o in offs]
    series = series_for(p["id"])
    last30 = [v for _, v in series[-30:]] or [offs[0]["price"]]
    change7 = None
    if len(series) >= 8 and series[-8][1]:
        change7 = (series[-1][1] - series[-8][1]) / series[-8][1] * 100
    _k = hashlib.md5(p["id"].encode("utf-8")).hexdigest()[:12]
    if IMG_CDN and (ROOT / "static" / "img" / f"{_k}.webp").exists():  # images live in the public kolasaar-img repo (jsDelivr): they no longer count toward the 20k-file host limit
        p = dict(p, image=f"{IMG_CDN}/{_k}.webp", thumb=f"{IMG_CDN}/{_k}.webp")
    elif (ROOT / "static" / "img" / f"{_k}.webp").exists() and (not KEEP_IMG or _k in KEEP_IMG):  # self-hosted copy (scraper/images.py); otherwise keep hot-linking the store image
        p = dict(p, image=f"{SITE}/static/img/{_k}.webp", thumb=f"{SITE}/static/img/{_k}.webp")
    full_en = p["name"]["en"]
    tidy = tidy_en(full_en)
    p = dict(p, slug=short_slug(p["slug"]), name_full=p["name"], name={"en": tidy, "ar": tidy_ar(tidy, p["category"])})
    _sn = sum(1 for v in (p.get("specs") or {}).values() if v not in ("-", "", None))
    _is_thin = len(offs) <= 2 and len(series) < 7 and _sn <= 1  # two stores, no history, hardly any specs: nothing a searcher cannot get from the store itself
    items.append(dict(
        p, offers=offs, best=offs[0], low30=min(last30), high30=max(last30), change7=change7, series=series,
        thin=_is_thin, nopage=bool(cfg.get("skip_thin")) and _is_thin, go=offs[0]["link"],
        href={l: f"/{l}/{p['category']}/{p['slug']}/" for l in LANGS}, compare=[]))

THIN = []
item_by_id = {i["id"]: i for i in items}
for c in cfg["categories"]:
    c["href"] = {l: f"/{l}/{c['slug']}/" for l in LANGS}
    c["name"] = {l: c[l] for l in LANGS}
    c["count"] = sum(1 for i in items if i["category"] == c["slug"])
cfg["categories"] = [c for c in cfg["categories"] if c["count"] >= (5 if c["slug"] not in ("phones","laptops","tvs","fridges","acs","microwaves","washers","ovens") else 1)]  # a new category needs a few products before it gets its own page
_live = {c["slug"] for c in cfg["categories"]}
items = [i for i in items if i["category"] in _live]
if IS_ROOT and IMG_CDN:  # Saudi (needs the freed file budget): pages Google may already have indexed must keep a real page (not a 404), even when thin
    try:
        import subprocess as _sp
        _legacy = set()
        _lf = ROOT / "data" / "legacy_slugs.json"  # committed copy: the host builds from a shallow clone with no old git history
        try:
            _o = _sp.run(["git", "show", "a75e679c:data/products.json"], capture_output=True, text=True, encoding="utf-8", cwd=str(ROOT)).stdout
            _g = {f'{q["category"]}/{q["slug"]}' for q in json.loads(_o)}
            if _g:
                _lf.write_text(json.dumps(sorted(_g)), encoding="utf-8")
        except Exception:
            pass
        try:
            _legacy |= set(json.loads(_lf.read_text(encoding="utf-8")))
        except Exception:
            pass
        try:
            _rg = json.loads((ROOT / "data" / "slug_registry.json").read_text(encoding="utf-8"))
            _legacy |= set((_rg.get("alias") or {}).values())
        except Exception:
            pass
        _n = 0
        for _i in items:
            if _i.get("nopage") and f'{_i["category"]}/{_i["slug"]}' in _legacy:
                _i["nopage"] = False
                _i["thin"] = False
                _n += 1
        print(f"legacy thin pages restored: {_n} (legacy slugs known: {len(_legacy)})")
    except Exception as _e:
        print("legacy restore skipped:", _e)

def _kind(i):
    n = i["name"]["en"].lower()
    if i["category"] == "tvs":
        return "monitor" if "monitor" in n else "tv"
    if i["category"] == "laptops":
        return "tablet" if re.search(r"\b(ipad|tablet|tab|pad|matepad)\b", n) else "laptop"
    return i["category"]


def _inch(i):
    m = re.search(r'(\d{2,3}(?:\.\d)?)\s?("|”|-inch|inch|inches)', i["name"]["en"].lower()) or re.search(r"\b(\d{2,3})\b", i["slug"])
    return float(m.group(1)) if m else None


def _family(i):  # same model in another storage size is not a "rival"
    return re.sub(r"-?\d+(gb|tb)$", "", i["slug"])


def _storage(i):
    m = re.search(r"(\d+)(gb|tb)$", i["slug"])
    return (int(m.group(1)) * (1024 if m.group(2) == "tb" else 1)) if m else None


def short_name(n):
    """Model name without spec tail, for compare-page titles: 'Apple iPhone 17 Pro Max, 5G, 6.9 inch 256GB' -> 'Apple iPhone 17 Pro Max'."""
    h = re.split(r",|\s[-–]\s|\sDual\s?SIM|\s\d+\s?GB|\s[45]G\b|\sSmartphone|\sTablet|\s\d+\s?TB|\s\d+[ -]?inch", n, maxsplit=1, flags=re.I)[0].strip()
    return h if len(h.split()) >= 2 else n


def comparable(a, b):
    """Only pair products a shopper would really weigh against each other: same kind, similar price, similar size, different model."""
    if _kind(a) != _kind(b) or _family(a) == _family(b):
        return False
    pa, pb = a["best"]["price"], b["best"]["price"]
    if max(pa, pb) > 1.2 * min(pa, pb):
        return False
    if _kind(a) in ("phones", "tablet", "laptop") and _storage(a) != _storage(b):
        return False  # compare like with like: same storage size
    if a["brand"] == b["brand"] and _kind(a) not in ("phone", "phones"):
        return False  # same-brand TVs/laptops are usually the same model in other sizes/configs
    if _kind(a) in ("tv", "monitor"):
        ia, ib = _inch(a), _inch(b)
        if not ia or not ib or max(ia, ib) > 1.2 * min(ia, ib):
            return False
    return True


compare_pages = []
MAX_PARTNERS = cfg.get("max_compare_partners", 2)
for slug in cats:
    if slug not in ("phones", "laptops", "tvs"):
        continue  # appliances are compared on their own category pages; head-to-head pages only for phones/laptops/TVs
    pool = [i for i in items if i["category"] == slug and len(i["offers"]) >= 3]  # both sides need real price data
    chosen = set()
    for a in pool:
        partners = sorted((b for b in pool if b is not a and comparable(a, b)),
                          key=lambda b: abs(b["best"]["price"] - a["best"]["price"]))[:MAX_PARTNERS]
        for b in partners:
            chosen.add(tuple(sorted((a["slug"], b["slug"]))))
    by_slug = {i["slug"]: i for i in pool}
    best_pair = {}  # the same two models in 256/512/1TB would be near-duplicate pages: keep the one with the most store data
    for sa, sb in chosen:
        k = tuple(sorted((_family(by_slug[sa]), _family(by_slug[sb]))))
        score = min(len(by_slug[sa]["offers"]), len(by_slug[sb]["offers"]))
        if k not in best_pair or (score, sa, sb) > best_pair[k][0]:
            best_pair[k] = ((score, sa, sb), (sa, sb))
    chosen = {v[1] for v in best_pair.values()}
    for sa, sb in sorted(chosen):
        a, b = by_slug[sa], by_slug[sb]
        s = f"{a['slug']}-vs-{b['slug']}"
        href = {l: f"/{l}/compare/{s}/" for l in LANGS}
        compare_pages.append((a, b, href))
        a["compare"].append((b, href))
        b["compare"].append((a, href))

# ---------- jinja ----------
env = Environment(loader=FileSystemLoader(ROOT / "templates"), autoescape=select_autoescape(["html"]))
# inline the small stylesheet (removes one render-blocking request)
env.globals["css"] = re.sub(r"\s*([{};:,])\s*", r"\1", re.sub(r"/\*.*?\*/", "", (ROOT / "static" / "style.css").read_text(encoding="utf-8"), flags=re.S)).strip()
env.filters["jsonld"] = lambda d: Markup(json.dumps(d, ensure_ascii=False).replace("</", "<\\/"))
env.globals["money"] = money
env.globals["dec"] = DEC
env.globals["brand_logo"] = brand_logo
env.globals["brand_initial"] = brand_initial
env.globals["fmt_price"] = lambda v: f"{v:,.{DEC}f}"
env.globals["href_of"] = lambda i, lang: (f"/{lang}/p/#{i['id']}" if cfg.get("thin_viewer") else i["go"]) if i.get("nopage") else i["href"][lang]
sitemap_entries = []

# ---------- header switchers (country + language) ----------
_CN = {"sa": ("السعودية", "Saudi Arabia", "Arabie saoudite"), "ae": ("الإمارات", "United Arab Emirates", "Émirats arabes unis"),
       "eg": ("مصر", "Egypt", "Égypte"), "tn": ("تونس", "Tunisia", "Tunisie"), "kw": ("الكويت", "Kuwait", "Koweït")}
_L2 = {"tn": "fr"}
_FR = cfg.get("lang2") == "fr"
_live = ["sa"] + [c for c in ("ae", "eg", "tn", "kw") if (ROOT / c / "LIVE").exists() and (ROOT / c / "data" / "products.json").exists()]
if COUNTRY not in _live:
    _live.append(COUNTRY)
env.globals["country_code"] = COUNTRY
env.globals["country_name"] = {"ar": _CN[COUNTRY][0], "en": _CN[COUNTRY][2 if _FR else 1]}
env.globals["country_list"] = [{"code": c, "ar": _CN[c][0], "en": _CN[c][2 if _FR else 1], "l2": _L2.get(c, "en")} for c in _live]
env.globals["lang_names"] = {"ar": "العربية", "en": "Français" if _FR else "English"}


def localize(content):
    for a, b in REPL:
        content = content.replace(a, b)
    content = re.sub(r'(["\'(=])/(ar|en|api)/', r'\1/' + COUNTRY + r'/\2/', content)
    content = re.sub(r'(["\'(=])/(llms\.txt|llms-full\.txt)', r'\1/' + COUNTRY + r'/\2', content)
    return content


def write_root(path, content):
    """Files that live at the domain root, shared by all countries (only the root build writes them)."""
    if IS_ROOT:
        t = OUT_ROOT / path.lstrip("/")
        t.parent.mkdir(parents=True, exist_ok=True)
        t.write_text(content, encoding="utf-8")


def write(path, content):
    if path in ("/_redirects", "/_headers", "/404.html", "/robots.txt") or path.endswith(".txt") and path.count("/") == 1 and not path.startswith("/llms"):
        return
    content = localize(content)
    target = OUT / path.strip("/") / "index.html" if path.endswith("/") else OUT / path.lstrip("/")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")


def render(tpl, paths, build_ctx, index=True):
    for lang in LANGS:
        ctx = build_ctx(lang)
        if ctx.get("description") and len(ctx["description"]) > 158:
            ctx["description"] = ctx["description"][:155].rsplit(" ", 1)[0].rstrip(" .,;:-") + "..."
        ctx.update(noindex=not index, lang=lang, t=T[lang], cfg=cfg, site=NAME[lang],
                   alternates={l: BASE + paths[l] for l in LANGS}, canonical=BASE + paths[lang], paths=paths,
                   updated=UPDATED_DATE, updated_iso=UPDATED, other_url=paths[T[lang]["other_lang_code"]],
                   og_image=(ctx.get("p") or {}).get("image") or SITE + "/static/og.png", footer_brands=footer_brands(lang))
        write(paths[lang], env.get_template(tpl).render(**ctx))
    if index:
        sitemap_entries.append(paths)


def breadcrumb(lang, crumbs):
    return {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": n, "item": BASE + u} for i, (n, u) in enumerate(crumbs)]}


def org_ld(lang):
    return {"@context": "https://schema.org", "@type": "Organization", "name": NAME[lang], "url": BASE + f"/{lang}/",
            "email": cfg["contact_email"], "areaServed": "SA", "logo": SITE + "/static/icon-192.png"}


def faq_ld(faq):
    return {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faq]}


def card_ld(lang, group, url):
    return {"@context": "https://schema.org", "@type": "ItemList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "url": (g["go"] if g.get("nopage") and not cfg.get("thin_viewer") else BASE + (f"/{lang}/p/#{g['id']}" if g.get("nopage") else g["href"][lang])), "name": g["name"][lang]}
        for i, g in enumerate(group)]}


# ---------- pages ----------
top_drops = sorted([i for i in items if i["change7"] is not None and i["change7"] < -0.5], key=lambda i: i["change7"])[:6]


from collections import Counter
BRAND_MIN = cfg.get("brand_hub_min", 4)
brand_hubs = {}
for _c in cfg["categories"]:
    _all = [i for i in items if i["category"] == _c["slug"]]
    _cnt = Counter(i["brand"] for i in _all if i["brand"] and i["brand"].lower() != "unknown")
    brand_hubs[_c["slug"]] = []
    for _brand, _n in sorted(_cnt.items(), key=lambda kv: (-kv[1], kv[0])):
        _slug = re.sub(r"[^a-z0-9]+", "-", _brand.lower()).strip("-")
        if _n >= BRAND_MIN and _slug and _n < 0.9 * len(_all):  # a brand that is (almost) the whole category would just duplicate the category page
            brand_hubs[_c["slug"]].append((_brand, _slug, _n))

SHORT = {"phones": ("الجوالات", "phones"), "laptops": ("اللابتوبات", "laptops"), "tvs": ("التلفزيونات", "TVs"), "fridges": ("الثلاجات", "refrigerators"),
         "acs": ("المكيفات", "air conditioners"), "microwaves": ("الميكروويف", "microwaves"), "washers": ("الغسالات", "washing machines"), "ovens": ("الأفران", "ovens"),
         "watches": ("الساعات الذكية", "smartwatches"), "earbuds": ("السماعات", "headphones"), "consoles": ("أجهزة الألعاب", "game consoles"), "printers": ("الطابعات", "printers"), "consumables": ("الأحبار والتونر", "ink & toner"), "networking": ("الشبكات", "networking"), "storage": ("التخزين", "storage"), "components": ("مكونات الكمبيوتر", "PC components"), "desktops": ("الكمبيوترات المكتبية", "desktop PCs"), "peripherals": ("ملحقات الكمبيوتر", "PC accessories"), "audio": ("الصوتيات", "speakers & audio"), "cameras": ("الكاميرات", "cameras"), "vacuums": ("المكانس", "vacuum cleaners"), "kitchen": ("أجهزة المطبخ", "kitchen appliances"), "home": ("الأجهزة المنزلية", "home appliances"), "gaming": ("مستلزمات الألعاب", "gaming gear"), "power": ("الطاقة والشحن", "power & charging"), "tools": ("العدد والأدوات", "tools"), "smart-home": ("المنزل الذكي", "smart home"), "other": ("منتجات أخرى", "other products")}
# category phrase used in brand-page titles ("أسعار جوالات سامسونج", "Samsung Smartphones prices")
BRAND_NOUN_AR = {"phones": "جوالات", "laptops": "لابتوبات وتابلت", "tvs": "تلفزيونات وشاشات", "fridges": "ثلاجات", "acs": "مكيفات", "microwaves": "أفران ميكروويف",
                 "washers": "غسالات", "ovens": "أفران", "watches": "ساعات", "earbuds": "سماعات", "consoles": "أجهزة", "printers": "طابعات", "consumables": "أحبار وتونر", "networking": "أجهزة شبكات", "storage": "وحدات تخزين", "components": "مكونات", "desktops": "كمبيوترات مكتبية", "peripherals": "ملحقات", "audio": "صوتيات", "cameras": "كاميرات", "vacuums": "مكانس", "kitchen": "أجهزة مطبخ", "home": "أجهزة منزلية", "gaming": "مستلزمات ألعاب", "power": "أجهزة طاقة", "tools": "أدوات", "smart-home": "أجهزة منزل ذكي", "other": "منتجات"}
SHORT.update({"visage": ("العناية بالبشرة", "face care"), "corps": ("العناية بالجسم", "body care"), "cheveux": ("العناية بالشعر", "hair care"), "solaire": ("الحماية من الشمس", "sun care"), "bebe": ("الأم والطفل", "mother & baby"), "complements": ("المكملات الغذائية", "supplements"), "hygiene": ("النظافة الشخصية", "personal hygiene"), "maquillage": ("المكياج", "makeup"), "parfum": ("العطور", "fragrances"), "minceur": ("التنحيف", "slimming"), "materiel": ("الأجهزة الصحية", "health devices")})
BRAND_NOUN_AR.update({"visage": "منتجات العناية بالبشرة", "corps": "منتجات العناية بالجسم", "cheveux": "منتجات العناية بالشعر", "solaire": "منتجات الحماية من الشمس", "bebe": "منتجات الأم والطفل", "complements": "مكملات", "hygiene": "منتجات النظافة", "maquillage": "منتجات مكياج", "parfum": "عطور", "minceur": "منتجات تنحيف", "materiel": "أجهزة صحية"})
BRAND_AR = {"Samsung": "سامسونج", "Apple": "آبل", "Xiaomi": "شاومي", "Huawei": "هواوي", "Honor": "هونر", "Oppo": "أوبو", "Vivo": "فيفو", "Realme": "ريلمي",
            "Infinix": "إنفنكس", "Tecno": "تكنو", "Nokia": "نوكيا", "Google": "جوجل", "LG": "إل جي", "Sony": "سوني", "TCL": "تي سي إل", "Hisense": "هايسنس",
            "Panasonic": "باناسونيك", "Hitachi": "هيتاشي", "Haier": "هاير", "Midea": "ميديا", "Toshiba": "توشيبا", "Bosch": "بوش", "Lenovo": "لينوفو",
            "Hp": "إتش بي", "HP": "إتش بي", "Dell": "ديل", "Asus": "أسوس", "Acer": "أيسر", "Super General": "سوبر جنرال", "Carrier": "كارير", "Nikai": "نيكاي",
            "General": "جنرال", "Mando": "ماندو", "Simfer": "سيمفر", "Class Pro": "كلاس برو", "Microsoft": "مايكروسوفت", "Philips": "فيليبس", "Oneplus": "ون بلس",
            "Msi": "إم إس آي", "Garmin": "غارمن", "JBL": "جي بي إل", "Anker Soundcore": "أنكر ساوندكور", "Nintendo": "نينتندو", "Valve": "فالف", "Benq": "بينكيو", "Aoc": "إيه أو سي", "Nothing": "ناثينج"}


def footer_brands(lang):
    out = []
    for c in cfg["categories"]:
        for bn, bs, n_ in brand_hubs.get(c["slug"], [])[:3]:
            label = (f"{BRAND_NOUN_AR.get(c['slug'], c['ar'])} {BRAND_AR.get(bn, bn)}" if lang == "ar" else f"{bn} {c['en']}")
            out.append((n_, label, f"/{lang}/{c['slug']}/brand/{bs}/"))
    res = [(l, u) for _, l, u in sorted(out, key=lambda x: -x[0])[:14]]
    if cfg.get("brand_page_max"):
        res.insert(0, ("كل الماركات" if lang == "ar" else "All brands", f"/{lang}/brands/"))
    return res


def fit(text, n=72):
    """Search titles over ~70 characters get cut: shorten a long product name at a word edge."""
    if len(text) <= n:
        return text
    out = text[:n].rsplit(" ", 1)[0].rstrip(" ,-–|")
    _dang = {"من", "في", "و", "مع", "لـ", "ل", "ب", "بـ", "على", "عن", "الى", "إلى", "for", "with", "and", "of", "the", "in", "by", "to", "&", "from", "a", "an", "-", "–", "|", ","}
    ws = out.split(" ")
    while len(ws) > 2 and ws[-1].strip(",-–|").lower() in _dang:
        ws.pop()
    return " ".join(ws).rstrip(" ,-–|")


def home_seo(lang):
    """Visible intro + FAQ for the home page (same text goes into FAQPage JSON-LD)."""
    n = len(items)
    st = sorted({o["store_name"] for i in items for o in i["offers"]})
    if COUNTRY == "sa":
        if lang == "ar":
            intro = (f"يقارن {NAME['ar']} أسعار {n} منتجاً من العناية بالبشرة والشعر والجسم والمكياج والعطور والحماية من الشمس ومستلزمات الأم والطفل والمكملات الغذائية في {len(st)} متجراً سعودياً للتجميل والعناية. "
                     "لكل منتج صفحة تعرض أقل سعر اليوم وسعر كل متجر وحالة التوفر وتاريخ تغيّر السعر، مع رابط مباشر إلى المتجر. "
                     "لا نضيف منتجاً إلا إذا كان متوفراً حالياً في متجرين على الأقل، لتكون المقارنة حقيقية.")
            faq = [("كيف أجد أرخص سعر لمنتج تجميل أو عناية في السعودية؟", "ابحث عن اسم المنتج أو الماركة أو افتح القسم المناسب، ثم افتح صفحة المنتج لترى أسعار كل المتاجر مرتبة من الأرخص، مع رابط مباشر إلى المتجر."),
                   ("كم متجراً ومنتجاً تقارنون؟", f"نقارن حالياً {n} منتجاً بين {len(st)} متجراً سعودياً، وكل منتج متوفر في متجرين على الأقل."),
                   ("هل تبيعون المنتجات؟", "لا، نحن موقع مقارنة مستقل. الشراء والدفع والتوصيل تتم عند المتجر الذي تختاره."),
                   ("هل الأسعار محدّثة؟", f"في كل صفحة أحدث الأسعار التي جمعناها مع تاريخ آخر تحديث ({UPDATED_DATE})، وقد يتغير السعر في المتجر بعد ذلك.")]
        else:
            intro = (f"{NAME['en']} compares prices of {n} beauty and personal-care products (skincare, haircare, bodycare, makeup, perfumes, sun protection, mother and baby care, supplements) across {len(st)} Saudi online stores. "
                     "Each product page shows today's lowest price, every store's price, availability and price history, with a direct link to the store. "
                     "We only list a product when at least two stores currently have it in stock, so the comparison is real.")
            faq = [("How do I find the cheapest price for a beauty or care product in Saudi Arabia?", "Search for the product or brand, or open the right category, then open the product page to see every store's price from cheapest, with a direct link to the store."),
                   ("How many stores and products do you compare?", f"We currently compare {n} products across {len(st)} Saudi online stores, and every product is available at at least two stores."),
                   ("Do you sell the products?", "No, we are an independent comparison site. You buy, pay and get delivery from the store you choose."),
                   ("Are the prices up to date?", f"Each page shows the latest prices we collected with the date of the last update ({UPDATED_DATE}); the price may have changed in the store since then.")]
        return intro, faq
    if lang == "ar":
        intro = (f"يقارن {NAME['ar']} أسعار {n} منتجاً من العناية بالبشرة والشعر والجسم والحماية من الشمس ومستلزمات الأم والطفل والمكملات الغذائية في {len(st)} متجراً تونسياً للبارافارماسي. "
                 "لكل منتج صفحة تعرض أقل سعر اليوم وسعر كل متجر وحالة التوفر وتاريخ تغيّر السعر، مع رابط مباشر إلى المتجر. "
                 "لا نضيف منتجاً إلا إذا كان متوفراً في متجرين على الأقل، لتكون المقارنة حقيقية.")
        faq = [("كيف أجد أرخص سعر لمنتج عناية في تونس؟", "ابحث عن اسم المنتج أو الماركة أو افتح القسم المناسب، ثم افتح صفحة المنتج لترى أسعار كل المتاجر مرتبة من الأرخص، مع رابط مباشر إلى المتجر."),
               ("كم متجراً ومنتجاً تقارنون؟", f"نقارن حالياً {n} منتجاً بين {len(st)} متجراً تونسياً للبارافارماسي، وكل منتج متوفر في متجرين على الأقل."),
               ("هل تبيعون المنتجات؟", "لا، نحن موقع مقارنة مستقل. الشراء والدفع والتوصيل تتم عند المتجر الذي تختاره."),
               ("هل الأسعار محدّثة؟", f"في كل صفحة أحدث الأسعار التي جمعناها مع تاريخ آخر تحديث ({UPDATED_DATE})، وقد يتغير السعر في المتجر بعد ذلك.")]
    else:
        intro = (f"{NAME['en']} compares prices of {n} products (skincare, haircare, bodycare, sun protection, mother and baby care, supplements) across {len(st)} Tunisian online parapharmacies. "
                 "Each product page shows today's lowest price, every store's price, availability and price history, with a direct link to the store. "
                 "We only list a product when at least two stores sell it, so the comparison is real.")
        faq = [("How do I find the cheapest price for a care product in Tunisia?", "Search for the product or brand, or open the right category, then open the product page to see every store's price from cheapest, with a direct link to the store."),
               ("How many stores and products do you compare?", f"We currently compare {n} products across {len(st)} Tunisian online parapharmacies, and every product is sold by at least two stores."),
               ("Do you sell the products?", "No, we are an independent comparison site. You buy, pay and get delivery from the store you choose."),
               ("Are the prices up to date?", f"Each page shows the latest prices we collected with the date of the last update ({UPDATED_DATE}); the price may have changed in the store since then.")]
    return intro, faq


def home_ctx(lang):
    names = [SHORT[c["slug"]][0 if lang == "ar" else 1] for c in cfg["categories"] if c["slug"] in SHORT]
    lead = names[:4] if len(names) > 4 else names
    sep = " و" if lang == "ar" else ", "
    if lang == "ar":
        phrase = "، ".join(lead[:-1]) + " و" + lead[-1] if len(lead) > 1 else "".join(lead)
        title, h1 = f"مقارنة أسعار {phrase} في السعودية | {NAME[lang]}", f"قارن أسعار {phrase} في السعودية"
    else:
        phrase = ", ".join(lead[:-1]) + " and " + lead[-1] if len(lead) > 1 else "".join(lead)
        title, h1 = f"Compare prices of {phrase} in Saudi Arabia | {NAME[lang]}", f"Compare prices of {phrase} in Saudi Arabia"
    stores = sorted({o["store_name"] for i in items for o in i["offers"]})
    allnames = "، ".join(names) if lang == "ar" else ", ".join(names)
    desc = (f"قارن أسعار {allnames} بين أبرز المتاجر السعودية. أقل سعر اليوم وتاريخ تغيّر السعر، وتُحدَّث يومياً."
            if lang == "ar" else
            f"Compare prices of {allnames} across the main Saudi stores. Today's lowest price and price history, updated daily.")
    cat_blocks = []
    for c in cfg["categories"]:
        top = sorted((i for i in items if i["category"] == c["slug"]), key=lambda i: (-len(i["offers"]), i["best"]["price"]))[:4]
        if top:
            cat_blocks.append((c, top))
    seo_intro, seo_faq = home_seo(lang)
    cat_ld = {"@context": "https://schema.org", "@type": "ItemList", "itemListElement": [{"@type": "ListItem", "position": k + 1, "url": BASE + c["href"][lang], "name": c[lang]} for k, c in enumerate(cfg["categories"])]}
    return dict(
        seo_intro=seo_intro, seo_faq=seo_faq,
        cat_blocks=cat_blocks,
        title=title, description=desc,
        h1=h1, categories=cfg["categories"], store_names=sorted({o["store_name"] for i in items for o in i["offers"]}), drops=top_drops, products=sorted(items, key=lambda i: (-len(i["offers"]), i["best"]["price"]))[:24],
        ld=[org_ld(lang), {"@context": "https://schema.org", "@type": "WebSite", "name": NAME[lang], "alternateName": [NAME["en"] if lang == "ar" else NAME["ar"], "kolasaar.com"], "url": BASE + f"/{lang}/", "inLanguage": lang}, cat_ld, faq_ld(seo_faq)])


render("home.html", {l: f"/{l}/" for l in LANGS}, home_ctx)

PAGE_SIZE = cfg.get("page_size", 48)
for c in cfg["categories"]:
    group_all = sorted((i for i in items if i["category"] == c["slug"]), key=lambda i: i["best"]["price"])
    if not group_all:
        continue
    chunks = [group_all[k:k + PAGE_SIZE] for k in range(0, len(group_all), PAGE_SIZE)]

    def page_paths(n, c=c):
        return {l: (c["href"][l] if n == 1 else f"/{l}/{c['slug']}/page/{n}/") for l in LANGS}

    for n, group in enumerate(chunks, 1):
        paths = page_paths(n)

        def ctx(lang, c=c, group=group, paths=paths, n=n, group_all=group_all, total=len(chunks), page_paths=page_paths):
            t = T[lang]
            cheapest = group_all[0]
            desc = (f"{c['intro'][lang]} " + (f"أقل سعر اليوم: {money(cheapest['best']['price'], lang)}." if lang == "ar"
                                               else f"Lowest today: {plain_money(cheapest['best']['price'])}."))
            title = (f"أسعار {c['ar']} في السعودية اليوم | {NAME['ar']}" if lang == "ar"
                     else f"{c['en']} Prices in Saudi Arabia Today | {NAME['en']}")
            if n > 1:
                title = f"{t['page']} {n} - {title}"
                desc = f"{t['page']} {n}/{total}: {desc}"
            faq = [(("ما أرخص منتج في قسم " + c["ar"] + " اليوم؟") if lang == "ar" else f"What is the cheapest product in {c['en']} today?",
                    (f"{cheapest['name']['ar']} بسعر {money(cheapest['best']['price'], 'ar')} في {cheapest['best']['store_name']}."
                     if lang == "ar" else f"{cheapest['name']['en']} at {plain_money(cheapest['best']['price'])} from {cheapest['best']['store_name']}."))]
            _pg = sorted({1, 2, total - 1, total} | set(range(n - 3, n + 4)) | set(range(5, total + 1, 5)))
            _pg = [k for k in _pg if 1 <= k <= total]
            nav = {"n": n, "total": total, "prev": page_paths(n - 1)[lang] if n > 1 else None,
                   "next": page_paths(n + 1)[lang] if n < total else None,
                   "pages": [(k, page_paths(k)[lang]) for k in _pg]}
            blinks = [(BRAND_AR.get(bn, bn) if lang == "ar" else bn, f"/{lang}/{c['slug']}/brand/{bs}/", n_) for bn, bs, n_ in brand_hubs[c["slug"]]]
            return dict(title=title, description=desc, cat=c, group=group, faq=faq, intro=c["intro"][lang], nav=nav, brand_links=blinks, h1_text=None,
                        guide=(GUIDES.get(c['slug'], {}).get(lang) if n == 1 else None),
                        ld=[breadcrumb(lang, [(t["home"], f"/{lang}/"), (c[lang], c["href"][lang])]), card_ld(lang, group, paths[lang]), faq_ld(faq)])

        render("category.html", paths, ctx)

    # ---- brand pages: "Samsung phones", "LG refrigerators" ... one real landing page per brand with enough products
    for brand, bslug, cnt in brand_hubs[c["slug"]]:
        bgroup = [i for i in group_all if i["brand"] == brand]
        bpaths = {l: f"/{l}/{c['slug']}/brand/{bslug}/" for l in LANGS}

        def bctx(lang, c=c, brand=brand, bgroup=bgroup, bpaths=bpaths):
            t = T[lang]
            lo, hi = bgroup[0], max(bgroup, key=lambda i: i["best"]["price"])
            stores = sorted({o["store_name"] for i in bgroup for o in i["offers"]})
            ar_b = BRAND_AR.get(brand, brand)
            if lang == "ar":
                h1 = f"أسعار {BRAND_NOUN_AR.get(c['slug'], c['ar'])} {ar_b} في السعودية"
                title = f"{h1} اليوم | {NAME['ar']}"
                intro = (f"نقارن {len(bgroup)} منتجاً من {ar_b} ({brand}) في قسم {c['ar']} بين {len(stores)} متاجر سعودية: {'، '.join(stores)}. "
                         f"تبدأ الأسعار من {money(lo['best']['price'], 'ar')} وتصل إلى {money(hi['best']['price'], 'ar')} (أقل سعر لكل منتج)، ونحدّثها يومياً.")
                faq = [(f"ما أرخص منتج من {ar_b} في قسم {c['ar']}؟", f"{lo['name']['ar']} بسعر {money(lo['best']['price'], 'ar')} في {lo['best']['store_name']}."),
                       (f"كم منتج من {ar_b} نقارن أسعاره؟", f"نقارن حالياً {len(bgroup)} منتجاً من {ar_b} في قسم {c['ar']} بين {len(stores)} متاجر، وآخر تحديث {UPDATED_DATE}.")]
            else:
                h1 = f"{brand} {c['en']} prices in Saudi Arabia"
                title = f"{h1} today | {NAME['en']}"
                intro = (f"We compare {len(bgroup)} {brand} products in {c['en']} across {len(stores)} Saudi stores: {', '.join(stores)}. "
                         f"Lowest prices run from {plain_money(lo['best']['price'])} to {plain_money(hi['best']['price'])} per product and are updated daily.")
                faq = [(f"What is the cheapest {brand} product in {c['en']}?", f"{lo['name']['en']} at {plain_money(lo['best']['price'])} from {lo['best']['store_name']}."),
                       (f"How many {brand} products do you compare?", f"{len(bgroup)} products in {c['en']} across {len(stores)} stores, last updated {UPDATED_DATE}.")]
            desc = intro[:300]
            return dict(title=title, description=desc, cat=c, group=bgroup, faq=faq, intro=intro, nav={"n": 1, "total": 1, "prev": None, "next": None},
                        h1_text=h1, brand_links=[],
                        ld=[breadcrumb(lang, [(t["home"], f"/{lang}/"), (c[lang], c["href"][lang]), (h1, bpaths[lang])]), card_ld(lang, bgroup, bpaths[lang]), faq_ld(faq)])

        render("category.html", bpaths, bctx)


# ---- one page per brand (all categories) + a brands index, per country (cfg brand_page_max > 0)
BRAND_PAGE_MAX = int(cfg.get("brand_page_max", 0))
BRAND_PAGE_MIN = int(cfg.get("brand_page_min", 3))
all_brands = []
if BRAND_PAGE_MAX:
    _bc = Counter(i["brand"] for i in items if i["brand"] and i["brand"].lower() not in ("unknown", "*", "other") and len(i["brand"]) > 1)
    for _b, _n in sorted(_bc.items(), key=lambda kv: (-kv[1], kv[0])):
        _s = re.sub(r"[^a-z0-9]+", "-", _b.lower()).strip("-")
        if _n >= BRAND_PAGE_MIN and _s and len(all_brands) < BRAND_PAGE_MAX:
            all_brands.append((_b, _s, _n))
brand_page_slugs = {b: s for b, s, n in all_brands}
_CATN = {c["slug"]: c for c in cfg["categories"]}


def _brand_label(b, lang):
    return BRAND_AR.get(b, b) if lang == "ar" else b


for brand, bslug, cnt in all_brands:
    ball = sorted((i for i in items if i["brand"] == brand), key=lambda i: (-len(i["offers"]), i["best"]["price"]))
    bshow = ball[:96]
    bp = {l: f"/{l}/brand/{bslug}/" for l in LANGS}

    def bgctx(lang, brand=brand, bslug=bslug, ball=ball, bshow=bshow, bp=bp):
        t = T[lang]
        lb = _brand_label(brand, lang)
        stores = sorted({o["store_name"] for i in ball for o in i["offers"]})
        cats = Counter(i["category"] for i in ball)
        lo = min(ball, key=lambda i: i["best"]["price"])
        cat_txt = (["، ".join(f"{SHORT.get(k, (k, k))[0]} ({v})" for k, v in cats.most_common(6))] if lang == "ar" else [", ".join(f"{SHORT.get(k, (k, k))[1]} ({v})" for k, v in cats.most_common(6))])[0]
        if lang == "ar":
            h1 = f"أسعار منتجات {lb} في السعودية"
            intro = (f"نقارن {len(ball)} منتجاً من {lb} بين {len(stores)} متاجر: {'، '.join(stores)}. الأقسام: {cat_txt}. "
                     f"أرخص منتج حالياً: {lo['name']['ar']} بسعر {money(lo['best']['price'], 'ar')} في {lo['best']['store_name']}. نحدّث الأسعار يومياً.")
            faq = [(f"كم منتج من {lb} نقارن أسعاره؟", f"نقارن حالياً {len(ball)} منتجاً من {lb} بين {len(stores)} متاجر، وآخر تحديث {UPDATED_DATE}."),
                   (f"ما أرخص منتج من {lb}؟", f"{lo['name']['ar']} بسعر {money(lo['best']['price'], 'ar')} في {lo['best']['store_name']}.")]
        else:
            h1 = f"{lb} prices in Saudi Arabia"
            intro = (f"We compare {len(ball)} {lb} products across {len(stores)} stores: {', '.join(stores)}. Categories: {cat_txt}. "
                     f"Cheapest right now: {lo['name']['en']} at {plain_money(lo['best']['price'])} from {lo['best']['store_name']}. Prices are updated daily.")
            faq = [(f"How many {lb} products do you compare?", f"{len(ball)} products across {len(stores)} stores, last updated {UPDATED_DATE}."),
                   (f"What is the cheapest {lb} product?", f"{lo['name']['en']} at {plain_money(lo['best']['price'])} from {lo['best']['store_name']}.")]
        pc = {"slug": "other", "name": {"ar": "الماركات", "en": "Brands"}, "href": {l: f"/{l}/brands/" for l in LANGS}, "ar": "الماركات", "en": "Brands"}
        blinks = []
        for k, v in cats.most_common():
            hub = next((x for x in brand_hubs.get(k, []) if x[0] == brand), None)
            if hub and k in _CATN:
                blinks.append((f"{_CATN[k][lang] if lang in _CATN[k] else k} {lb}", f"/{lang}/{k}/brand/{hub[1]}/", hub[2]))
        return dict(title=f"{h1} | {NAME[lang]}", description=intro[:300], cat=pc, group=bshow, faq=faq, intro=intro, nav={"n": 1, "total": 1, "prev": None, "next": None},
                    h1_text=h1, brand_links=blinks,
                    ld=[breadcrumb(lang, [(t["home"], f"/{lang}/"), (pc["name"][lang], pc["href"][lang]), (h1, bp[lang])]), card_ld(lang, bshow, bp[lang]), faq_ld(faq)])

    render("category.html", bp, bgctx)

if all_brands:
    ip = {l: f"/{l}/brands/" for l in LANGS}

    def bictx(lang):
        t = T[lang]
        h1 = "كل الماركات" if lang == "ar" else "All brands"
        intro = (f"تصفح {len(all_brands)} ماركة نقارن أسعار منتجاتها بين المتاجر في السعودية، من الأكثر منتجات إلى الأقل." if lang == "ar"
                 else f"Browse {len(all_brands)} brands whose products we compare across stores in Saudi Arabia, from the most products to the fewest.")
        pc = {"slug": "other", "name": {"ar": "الماركات", "en": "Brands"}, "href": ip, "ar": "الماركات", "en": "Brands"}
        faq = [("كم ماركة نقارن؟" if lang == "ar" else "How many brands do you compare?", (f"{len(all_brands)} ماركة." if lang == "ar" else f"{len(all_brands)} brands."))]
        return dict(title=f"{h1} | {NAME[lang]}", description=intro[:300], cat=pc, group=[], faq=faq, intro=intro, nav={"n": 1, "total": 1, "prev": None, "next": None},
                    h1_text=h1, brand_links=[(_brand_label(b, lang), f"/{lang}/brand/{s}/", n) for b, s, n in all_brands],
                    ld=[breadcrumb(lang, [(t["home"], f"/{lang}/"), (pc["name"][lang], ip[lang])]), faq_ld(faq)])

    render("category.html", ip, bictx)


def _sv(k, v, lang):
    """Spec value in the page language (values may be {'en','ar'} dicts; sizes carry a neutral unit)."""
    if isinstance(v, dict):
        return v[lang]
    if lang == "ar" and k == "size":
        return re.sub(r"\b(ml|fl oz|oz|kg|g|L)$", lambda m: {"ml": "مل", "g": "غ", "kg": "كغ", "L": "لتر", "oz": "أونصة", "fl oz": "أونصة سائلة"}[m.group(1)], str(v))
    return v


def product_faq(p, lang):
    b, offs = p["best"], p["offers"]
    n = p["name"][lang]
    ar = lang == "ar"
    sep = "، " if ar else ", "
    stores = sep.join(o["store_name"] for o in offs)
    days = len(p["series"])
    labels = cfg["spec_labels"].get(p["category"], {})
    spec_txt = sep.join(f"{labels[k][lang]}: {_sv(k, v, lang)}" for k, v in (p.get("specs") or {}).items() if k in labels and v not in ("-", "", None))
    stock = [o["store_name"] for o in offs if o["in_stock"]]
    out = []
    if ar:
        out.append((f"كم أقل سعر لـ {n} في السعودية اليوم؟", f"أقل سعر هو {money(b['price'], 'ar')} في {b['store_name']} (تحديث {UPDATED_DATE})."))
        out.append((f"أين أشتري {n}؟", f"يُعرض في المتاجر التالية: {stores}."))
        out.append((f"هل {n} متوفر الآن؟", (f"نعم، متوفر حالياً في {sep.join(stock)}." if stock else "غير متوفر حالياً في أي متجر نتتبعه، وقد يعود قريباً.")
                    + (f" والباقي ({len(offs) - len(stock)}) غير متوفر." if stock and len(stock) < len(offs) else "")))
        if spec_txt:
            out.append((f"ما أبرز مواصفات {n}؟", f"{spec_txt}. المواصفات مأخوذة من عنوان المنتج في المتاجر، فتحقق منها في صفحة المتجر قبل الشراء."))
        if days >= 7:
            out.append((f"هل تغيّر سعر {n} مؤخراً؟", f"خلال آخر {min(days, 30)} يوماً تراوح أقل سعر بين {money(p['low30'], 'ar')} و{money(p['high30'], 'ar')}."))
        else:
            out.append((f"هل تغيّر سعر {n} مؤخراً؟", (f"بدأنا تتبع سعره حديثاً ({days} يوم حتى الآن)، فلا نملك بعد تاريخاً كافياً للحكم على اتجاه السعر." if days > 1 else "بدأنا تتبع سعره اليوم، فلا نملك بعد تاريخاً كافياً للحكم على اتجاه السعر.")))
    else:
        out.append((f"What is the lowest price of {n} in Saudi Arabia today?", f"The lowest price is {plain_money(b['price'])} at {b['store_name']} (updated {UPDATED_DATE})."))
        out.append((f"Where can I buy {n}?", f"Listed at: {stores}."))
        out.append((f"Is {n} in stock?", (f"Yes, it is in stock at {sep.join(stock)}." if stock else "It is not in stock at any store we track right now; it may return soon.")
                    + (f" It is out of stock at the other {len(offs) - len(stock)}." if stock and len(stock) < len(offs) else "")))
        if spec_txt:
            out.append((f"What are the main specifications of {n}?", f"{spec_txt}. Specs are read from the store listings, so confirm them on the store page before buying."))
        if days >= 7:
            out.append((f"Has the price of {n} changed recently?", f"Over the last {min(days, 30)} days the lowest price ranged from {plain_money(p['low30'])} to {plain_money(p['high30'])}."))
        else:
            out.append((f"Has the price of {n} changed recently?", (f"We only started tracking it recently ({days} days so far), so there is not enough history yet to judge the trend." if days > 1 else "We started tracking it today, so there is not enough history yet to judge the trend.")))
    return out


def product_summary(p, lang):
    """Data-driven paragraph unique to each product (spread, stock, trend) - avoids thin templated pages."""
    offs, n = p["offers"], p["name"][lang]
    hi = max(offs, key=lambda o: o["price"])
    lo = p["best"]
    spread = hi["price"] - lo["price"]
    pct = spread / hi["price"] * 100 if hi["price"] else 0
    instock = sum(1 for o in offs if o["in_stock"])
    ch = p.get("change7")
    _sp = p.get("specs") or {}
    _pre = ""
    if _sp.get("type") or _sp.get("size"):
        if lang == "ar":
            _bits = [f"{n} " + (f"من فئة {_sv('type', _sp['type'], 'ar')}" if _sp.get("type") else "منتج للعناية")]
            if _sp.get("size"): _bits.append(f"بحجم {_sv('size', _sp['size'], 'ar')}")
            if _sp.get("spf"): _bits.append(f"بعامل حماية {_sp['spf']}")
            if _sp.get("audience"): _bits.append(f"موجّه لفئة {_sv('audience', _sp['audience'], 'ar')}")
            if _sp.get("feature"): _bits.append(f"ومن أبرز ما يميّزه: {_sv('feature', _sp['feature'], 'ar')}")
            _pre = " ".join(_bits) + ". هذه التفاصيل مستخرجة من عنوان المنتج في المتاجر. "
        else:
            _bits = [f"{n} is " + (f"a {_sv('type', _sp['type'], 'en').lower()}" if _sp.get("type") else "a care product")]
            if _sp.get("size"): _bits.append(f"sold in a {_sp['size']} size")
            if _sp.get("spf"): _bits.append(f"rated {_sp['spf']}")
            if _sp.get("audience"): _bits.append(f"aimed at {_sv('audience', _sp['audience'], 'en').lower()}")
            if _sp.get("feature"): _bits.append(f"with {_sv('feature', _sp['feature'], 'en').lower()} as a key feature")
            _pre = ", ".join(_bits) + ". These details are read from the product title at the stores. "
    if lang == "ar":
        s = (f"يتوفر {n} لدى {len(offs)} متاجر في السعودية، {instock} منها متوفر حالياً. أقل سعر {money(lo['price'], 'ar')} في {lo['store_name']}، "
             f"وأعلى سعر {money(hi['price'], 'ar')} في {hi['store_name']}، " + (f"أي فارق {money(spread, 'ar')} ({pct:.0f}٪) بين أرخص متجر وأغلاه." if spread > 0 else "والسعر متطابق بين المتاجر."))
        if ch is not None and abs(ch) >= 0.5:
            s += f" تغيّر أقل سعر خلال 7 أيام بنسبة {ch:+.1f}٪."
    else:
        s = (f"{n} is listed at {len(offs)} Saudi stores, {instock} in stock right now. The lowest price is {plain_money(lo['price'])} at {lo['store_name']} "
             f"and the highest {plain_money(hi['price'])} at {hi['store_name']}" + (f": a gap of {plain_money(spread)} ({pct:.0f}%) between cheapest and priciest." if spread > 0 else ". The price is identical across stores."))
        if ch is not None and abs(ch) >= 0.5:
            s += f" The lowest price moved {ch:+.1f}% over the past 7 days."
    return _pre + s


from collections import Counter as _Ctr
_TC = {l: _Ctr(fit(i["name"][l], 36) for i in items) for l in LANGS}
_TC3 = {l: _Ctr(fit(i["name"][l], 160) for i in items) for l in LANGS}
_TC2 = {l: _Ctr(fit(i["name"][l], 66) for i in items) for l in LANGS}


for p in items:
    def ctx(lang, p=p):
        t, c, b, n = T[lang], cats[p["category"]], p["best"], p["name"][lang]
        faq = product_faq(p, lang)
        if lang == "ar":
            title = f"سعر {fit(n, 36 if _TC[lang][fit(n, 36)] == 1 else (66 if _TC2[lang][fit(n, 66)] == 1 else 160))} في السعودية"
            desc = f"أقل سعر لـ {fit(n, 60)}: {money(b['price'], 'ar')} من {b['store_name']}. قارن {len(p['offers'])} متاجر سعودية وتابع تاريخ السعر. تحديث {UPDATED_DATE}."
        else:
            title = f"{fit(n, 36 if _TC[lang][fit(n, 36)] == 1 else (66 if _TC2[lang][fit(n, 66)] == 1 else 160))} Price in Saudi Arabia"
            desc = f"Lowest price for {fit(n, 60)}: {plain_money(b['price'])} at {b['store_name']}. Compare {len(p['offers'])} Saudi stores and track the price. Updated {UPDATED_DATE}."
        if p.get("gtin") and _TC3[lang][fit(n, 160)] > 1:  # two listings with the same name but different barcodes: keep titles unique
            title += f" (EAN …{str(p['gtin'])[-4:]})"
        prices = [o["price"] for o in p["offers"]]
        product_ld = {
            "@context": "https://schema.org", "@type": "Product", "name": n, "sku": p["id"], "category": c[lang],
            "brand": {"@type": "Brand", "name": p["brand"]}, "url": BASE + p["href"][lang], "description": desc,
            "offers": {"@type": "AggregateOffer", "priceCurrency": "SAR", "lowPrice": min(prices), "highPrice": max(prices),
                       "offerCount": len(prices), "offers": [{
                           "@type": "Offer", "price": o["price"], "priceCurrency": "SAR",
                           "availability": "https://schema.org/InStock" if o["in_stock"] else "https://schema.org/OutOfStock",
                           "url": o["link"], "seller": {"@type": "Organization", "name": o["store_name"]}} for o in p["offers"]]}}
        if p.get("image"):
            product_ld["image"] = p["image"]
        _g = re.sub(r"\D", "", str(p.get("gtin") or ""))
        if len(_g) in (8, 12, 13, 14) and sum(int(ch) * (3 if k % 2 == len(_g) % 2 else 1) for k, ch in enumerate(_g)) % 10 == 0:
            product_ld[f"gtin{len(_g)}"] = _g
        labels = cfg["spec_labels"][p["category"]]
        specs = [(labels[k][lang], _sv(k, v, lang)) for k, v in p["specs"].items() if k in labels and v not in ("-", "", None)]
        related = sorted((i for i in items if i["category"] == p["category"] and i["id"] != p["id"]),
                         key=lambda i: (i["brand"] != p["brand"], abs(i["best"]["price"] - p["best"]["price"])))[:6]
        hub = next(((bs, n_) for bn, bs, n_ in brand_hubs.get(p["category"], []) if bn == p["brand"]), None)
        more_links = ([(f"{'كل منتجات' if lang == 'ar' else 'All'} {BRAND_AR.get(p['brand'], p['brand']) if lang == 'ar' else p['brand']} {('في قسم ' + c['ar']) if lang == 'ar' else c['en']}",
                        f"/{lang}/{c['slug']}/brand/{hub[0]}/")] if hub else []) + [(("كل " + c["ar"]) if lang == "ar" else ("All " + c["en"]), c["href"][lang])]
        if p["brand"] in brand_page_slugs:
            more_links.append((f"كل منتجات {BRAND_AR.get(p['brand'], p['brand'])}" if lang == "ar" else f"All {p['brand']} products", f"/{lang}/brand/{brand_page_slugs[p['brand']]}/"))
        summary = product_summary(p, lang)
        adv = content.advice(p, items, lang, money, plain_money)
        guide = GUIDES.get(p['category'], {}).get(lang)
        return dict(title=title, description=desc, p=p, cat=c, faq=faq, specs=specs, related=related, summary=summary, more_links=more_links, adv=adv, guide=guide,
                    spark=sparkline(p["series"][-30:], lang),
                    ld=[product_ld, breadcrumb(lang, [(t["home"], f"/{lang}/"), (c[lang], f"/{lang}/{c['slug']}/"), (n, p["href"][lang])]), faq_ld(faq)])

    _thin = p["thin"]
    THIN.append(_thin)
    if p["nopage"]:  # file budget (host limit 20k files): thin pages are noindex anyway, so they get no page; cards link straight to the cheapest store
        continue
    render("product.html", p["href"], ctx, index=not _thin)

if cfg.get("thin_viewer"):
    _tv = {}
    for i in items:
        if i.get("nopage"):
            _tv[i["id"]] = {"n": i["name"], "b": i["brand"], "c": i["category"], "cn": {l: cats[i["category"]][l] for l in LANGS}, "i": i.get("thumb") or i.get("image"),
                            "o": [[o["store_name"], o["price"], 1 if o["in_stock"] else 0, o["link"]] for o in i["offers"]]}
    write("/api/thin.json", json.dumps(_tv, ensure_ascii=False, separators=(",", ":")))
    render("thin.html", {l: f"/{l}/p/" for l in LANGS}, lambda lang: dict(title=("مقارنة سعر المنتج" if lang == "ar" else "Product price comparison") + f" | {NAME[lang]}", description="", faq=[]), index=False)

for a, b, href in compare_pages:
    def ctx(lang, a=a, b=b, href=href):
        t, c = T[lang], cats[a["category"]]
        na, nb = a["name"][lang], b["name"][lang]
        labels = cfg["spec_labels"][a["category"]]
        rows = [(labels[k][lang], a["specs"].get(k, "-"), b["specs"].get(k, "-")) for k in labels]
        cheaper = a if a["best"]["price"] <= b["best"]["price"] else b
        diff = abs(a["best"]["price"] - b["best"]["price"])
        if lang == "ar":
            title = f"مقارنة {fit(na, 24)} مع {fit(nb, 24)}"
            desc = f"{fit(cheaper['name']['ar'], 50)} أرخص بفارق {money(diff, 'ar')} اليوم. قارن المواصفات وأسعار المتاجر في السعودية. آخر تحديث {UPDATED_DATE}."
        else:
            sa, sb = short_name(na), short_name(nb)
            stg = a["specs"].get("storage")
            title = f"{sa} vs {sb}" + (f" ({stg})" if stg and a["category"] == "phones" else "") + ": Specs & Price"
            desc = f"{fit(cheaper['name']['en'], 50)} is cheaper by {plain_money(diff)} today. Compare specs and Saudi store prices. Updated {UPDATED_DATE}."
        return dict(title=title, description=desc, a=a, b=b, rows=rows, cheaper=cheaper, diff=diff, cat=c,
                    ld=[breadcrumb(lang, [(t["home"], f"/{lang}/"), (c[lang], f"/{lang}/{c['slug']}/"), (f"{na} {t['vs']} {nb}", href[lang])]),
                        card_ld(lang, [a, b], href[lang])])

    # index only comparisons backed by real multi-store data on both sides; others stay reachable but noindex
    strong = min(len(a["offers"]), len(b["offers"])) >= 3 and len({a["best"]["store"], b["best"]["store"]}) >= 1
    render("compare.html", href, ctx, index=(strong and cfg.get("index_compare", False)) or bool(cfg.get("demo_mode")))

PAGES = {
    "about": {
        "ar": ("من نحن", [
            ("ما هو الموقع؟", f"{NAME['ar']} موقع مستقل لمقارنة أسعار الإلكترونيات (الهواتف واللابتوبات والتابلت والتلفزيونات والشاشات والثلاجات والمكيفات وأفران الميكروويف والغسالات والأفران) التي يزيد سعرها عن 100 ريال سعودي في المتاجر السعودية، ويُحدَّث يومياً."),
            ("ماذا نفعل؟", "نقرأ أسعار المنتجات من صفحات المتاجر العامة، ونطابق المنتج نفسه بين المتاجر، ونعرض لك أرخص سعر اليوم مع سجل الأسعار. لا نبيع المنتجات ولا نشحنها؛ تشتري مباشرة من المتجر الذي تختاره."),
            ("المتاجر", "نقارن حالياً بين: جرير، المنعم، إكسترا، نون، أمازون السعودية، ترينديول، سعيد. نضيف متاجر جديدة بعد الحصول على إذن منها."),
            ("كيف نكتب التحليلات؟", "الخلاصة وقائمة المميزات وما يجب الانتباه إليه في كل صفحة منتج يولّدها نظامنا آلياً من بيانات حقيقية: المواصفات المنشورة وأسعار المتاجر اليوم ونطاق السعر خلال 30 يوماً. أما أدلة الشراء في صفحات الأقسام فكتبناها يدوياً من معلومات عامة موثوقة (مثل سعة التبريد المناسبة لمساحة الغرفة). نحن لا نختبر الأجهزة بأنفسنا ولا ننشر مراجعات مختلقة، وإذا لم تتوفر معلومة لا نخترعها."),
            ("استقلالية الموقع", "لا تدفع المتاجر لتحسين ترتيبها، ويُرتَّب العرض دائماً بحسب السعر الفعلي والتوفر."),
            ("التواصل", f"للتصحيحات والاقتراحات: {cfg['contact_email']}")]),
        "en": ("About us", [
            ("What is this site?", f"{NAME['en']} is an independent price comparison site for electronics (phones, laptops and tablets, TVs and monitors, refrigerators, air conditioners, microwaves, washing machines and ovens) priced above SAR 100 in Saudi stores, updated daily."),
            ("What we do", "We read product prices from the stores' public pages, match the same product across stores, and show today's lowest price with its price history. We do not sell or ship anything; you buy directly from the store you choose."),
            ("Stores", "We currently compare: Jarir, Almanea, eXtra, Noon, Amazon.sa, Trendyol and Saeel. New stores are added only after we have their permission."),
            ("How we write the analysis", "The verdict, pros list and 'things to check' on each product page are generated automatically from real data: published specifications, today's store prices and the 30-day price range. The buying guides on category pages are written by hand from reliable general knowledge (for example, the cooling capacity that suits a given room size). We do not test devices ourselves and never publish invented reviews; when a fact is unavailable we leave it out."),
            ("Independence", "Stores cannot pay for a better position. Listings are always ordered by actual price and availability."),
            ("Contact", f"Corrections and suggestions: {cfg['contact_email']}")]),
    },
    "methodology": {
        "ar": ("المنهجية", [
            ("مصادر الأسعار", "نجمع الأسعار من صفحات قوائم المنتجات العامة في المتاجر المذكورة، بإذن منها وبوتيرة هادئة، ولا نقدّر أي سعر أو نخمّنه."),
            ("مطابقة المنتجات", "نعدّ منتجين متطابقين فقط إذا اتفقا في الماركة والموديل وسعة التخزين، وفي الفئة (مثل Pro أو Plus) والشبكة (4G أو 5G) والرام حين تُذكر. الألوان تُدمج في منتج واحد. إذا لم نتأكد لا ندمج."),
            ("اختلاف النسخ", "قد تختلف الأسعار بين نسخة الشرق الأوسط والنسخة الدولية أو العالمية (Global/International) لأن الضمان والمواصفات قد تختلف. تحقق من نسخة المنتج في صفحة المتجر قبل الشراء."),
            ("التحديث", "تُحدَّث الأسعار مرة يومياً، ويظهر وقت آخر تحديث في كل صفحة وفي البيانات المفتوحة. قد يتغير السعر في المتجر بعد آخر تحديث."),
            ("الفحص", "نستبعد الأسعار غير الصالحة والأقل من 100 ريال، وإذا اختلف سعرا متجرين بأكثر من 40% لا ننشر أياً منهما لأننا لا نعرف الصحيح، ونستبعد السعر الذي يبتعد كثيراً عن وسيط الأسعار."),
            ("الترتيب والعمولة", "قد نحصل على عمولة عند الشراء عبر بعض الروابط مستقبلاً، لكنها لا تؤثر على ترتيب المتاجر أو الأسعار المعروضة، وسنذكر ذلك بوضوح."),
            ("البيانات المفتوحة", "نوفّر كل الأسعار بصيغة JSON على /api/products.json للاستخدام والاقتباس مع ذكر المصدر.")]),
        "en": ("Methodology", [
            ("Price sources", "Prices are collected from the public product-listing pages of the stores named on this site, with their permission and at a gentle pace. We never estimate or guess a price."),
            ("Product matching", "Two listings count as the same product only if they agree on brand, model and storage size, and on the variant (Pro, Plus...), network (4G/5G) and RAM when those are stated. Colours are merged into one product. If we are not sure, we do not merge."),
            ("Regional versions", "Prices can differ between the Middle East version and international/global versions because warranty and specifications may differ. Check the version on the store page before buying."),
            ("Update schedule", "Prices update once a day; the last-update time is shown on every page and in the open data. A store's price may change after our last update."),
            ("Validation", "We drop invalid prices and prices below SAR 100. If two stores disagree by more than 40% we publish neither, because we cannot tell which is right, and we drop prices far from the median."),
            ("Ranking & commissions", "We may earn commissions through some links in the future; they never affect store ranking or displayed prices, and we will say so clearly."),
            ("Open data", "All prices are available as JSON at /api/products.json for use and citation with attribution.")]),
    },
    "privacy": {
        "ar": ("سياسة الخصوصية", [
            ("ما الذي نجمعه؟", "لا نطلب منك إنشاء حساب ولا نجمع اسمك أو بريدك أو بيانات الدفع. قد نستخدم إحصاءات زيارات مجمّعة لا تحدد هويتك لفهم الصفحات الأكثر استخداماً."),
            ("ملفات تعريف الارتباط والإعلانات", "قد نعرض إعلانات من جهات خارجية مثل Google AdSense. تستخدم هذه الجهات ملفات تعريف الارتباط لعرض إعلانات بناءً على زياراتك السابقة لهذا الموقع ومواقع أخرى. يمكنك إيقاف الإعلانات المخصصة من إعدادات الإعلانات في حسابك على Google (adssettings.google.com) أو من إعدادات متصفحك."),
            ("روابط المتاجر", "عند الضغط على رابط متجر تنتقل إلى موقعه، وتخضع بياناتك هناك لسياسة خصوصية ذلك المتجر. قد نحصل على عمولة من بعض الروابط دون أن يزيد السعر عليك."),
            ("التواصل", f"لأي استفسار عن الخصوصية: {cfg['contact_email']}")]),
        "en": ("Privacy policy", [
            ("What we collect", "We do not ask you to create an account and we do not collect your name, email or payment details. We may use aggregated, non-identifying traffic statistics to see which pages are most used."),
            ("Cookies and advertising", "We may show ads from third parties such as Google AdSense. These vendors use cookies to serve ads based on your previous visits to this and other sites. You can opt out of personalised ads in your Google Ads settings (adssettings.google.com) or in your browser settings."),
            ("Store links", "When you click a store link you leave this site, and your data there is governed by that store's privacy policy. We may earn a commission from some links at no extra cost to you."),
            ("Contact", f"Privacy questions: {cfg['contact_email']}")]),
    },
}
for key, per_lang in PAGES.items():
    paths = {l: f"/{l}/{key}/" for l in LANGS}

    def ctx(lang, key=key, paths=paths):
        title, sections = PAGES[key][lang]
        return dict(title=f"{title} | {NAME[lang]}", description=sections[0][1], h1=title, sections=sections,
                    ld=[org_ld(lang), breadcrumb(lang, [(T[lang]["home"], f"/{lang}/"), (title, paths[lang])])])

    render("page.html", paths, ctx)

# ---------- root, static, machine-readable files ----------
write("/", f'<!doctype html><html lang="ar"><head><meta charset="utf-8"><title>{NAME["ar"]} | {NAME["en"]}</title>'
           f'<meta http-equiv="refresh" content="0; url=/ar/"><link rel="canonical" href="{BASE}/ar/">'
           f'<link rel="alternate" hreflang="ar" href="{BASE}/ar/"><link rel="alternate" hreflang="en" href="{BASE}/en/">'
           f'<link rel="alternate" hreflang="x-default" href="{BASE}/ar/"></head>'
           f'<body><a href="/ar/">العربية</a> · <a href="/en/">English</a></body></html>')


def make_og_png(path, text="kolasaar.com"):
    """1200x630 share image drawn with the standard library only (no Pillow needed): brand colour, yellow bar, pixel-font site name."""
    import struct
    import zlib
    G = {"k": ["X...X", "X..X.", "X.X..", "XX...", "X.X..", "X..X.", "X...X"], "o": [".....", ".....", ".XXX.", "X...X", "X...X", "X...X", ".XXX."],
         "l": ["XX...", ".X...", ".X...", ".X...", ".X...", ".X...", ".XXX."], "a": [".....", ".....", ".XXX.", "....X", ".XXXX", "X...X", ".XXXX"],
         "s": [".....", ".....", ".XXXX", "X....", ".XXX.", "....X", "XXXX."], "r": [".....", ".....", "X.XX.", "XX..X", "X....", "X....", "X...."],
         ".": [".....", ".....", ".....", ".....", ".....", ".XX..", ".XX.."], "c": [".....", ".....", ".XXXX", "X....", "X....", "X....", ".XXXX"],
         "m": [".....", ".....", "XX.X.", "X.X.X", "X.X.X", "X.X.X", "X.X.X"]}
    W, H, S = 1200, 630, 13
    bg, bar, fg = (11, 107, 91), (255, 194, 26), (255, 255, 255)
    px = [[bg] * W for _ in range(H)]
    for y in range(H - 16, H):
        px[y] = [bar] * W
    x0 = (W - len(text) * 6 * S + S) // 2
    y0 = (H - 7 * S) // 2 - 20
    for i, ch in enumerate(text):
        for ry, row in enumerate(G.get(ch, [])):
            for rx, c in enumerate(row):
                if c == "X":
                    for yy in range(S):
                        for xx in range(S):
                            px[y0 + ry * S + yy][x0 + (i * 6 + rx) * S + xx] = fg
    raw = b"".join(b"\x00" + bytes(v for p in row for v in p) for row in px)
    def chunk(t, d):
        return struct.pack(">I", len(d)) + t + d + struct.pack(">I", zlib.crc32(t + d) & 0xFFFFFFFF)
    png = b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)) + chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b"")
    Path(path).write_bytes(png)

def make_icons(out):
    """Favicon set drawn with the standard library only: teal tile, yellow disc, dark 'price drop' arrow. Google needs a real favicon for the search-result icon."""
    import struct
    import zlib
    teal, yellow = (11, 107, 91), (255, 194, 26)

    def shade(u, v):
        """colour (r,g,b,a) at unit coords, or None when transparent"""
        r = 0.22  # corner radius
        cx, cy = min(max(u, r), 1 - r), min(max(v, r), 1 - r)
        if (u - cx) ** 2 + (v - cy) ** 2 > r * r:
            return None
        if (u - .5) ** 2 + (v - .5) ** 2 <= .33 ** 2:
            shaft = .44 <= u <= .56 and .27 <= v <= .52
            head = .50 <= v <= .73 and abs(u - .5) <= (.73 - v) / .23 * .20
            return teal if (shaft or head) else yellow
        return teal

    def png(size, n=3):
        rows = []
        for y in range(size):
            row = bytearray(b"\x00")
            for x in range(size):
                acc = [0, 0, 0]
                a = 0
                for sy in range(n):
                    for sx in range(n):
                        c = shade((x + (sx + .5) / n) / size, (y + (sy + .5) / n) / size)
                        if c:
                            a += 1
                            acc[0] += c[0]; acc[1] += c[1]; acc[2] += c[2]
                row += bytes((acc[0] // a, acc[1] // a, acc[2] // a, 255 * a // (n * n)) if a else (0, 0, 0, 0))
            rows.append(bytes(row))
        def chunk(t, d):
            return struct.pack(">I", len(d)) + t + d + struct.pack(">I", zlib.crc32(t + d) & 0xFFFFFFFF)
        return b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", size, size, 8, 6, 0, 0, 0)) + chunk(b"IDAT", zlib.compress(b"".join(rows), 9)) + chunk(b"IEND", b"")

    p48, p180, p192 = png(48), png(180), png(192)
    (out / "static" / "icon-192.png").write_bytes(p192)
    (out / "static" / "apple-touch-icon.png").write_bytes(p180)
    # .ico containing the 48px PNG (browsers and Google read it from /favicon.ico)
    (out / "favicon.ico").write_bytes(struct.pack("<HHH", 0, 1, 1) + struct.pack("<BBBBHHII", 48, 48, 0, 0, 1, 32, len(p48), 22) + p48)
    (out / "static" / "icon.svg").write_text(
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><rect width="100" height="100" rx="22" fill="#0B6B5B"/>'
        '<circle cx="50" cy="50" r="33" fill="#FFC21A"/><path d="M44 27h12v25h14L50 73 30 52h14z" fill="#0B6B5B"/></svg>', encoding="utf-8")


if IS_ROOT:
    _skip_imgs = (lambda d, names: [n for n in names if n.endswith(".webp")]) if IMG_CDN else (lambda d, names: [n for n in names if n.endswith(".webp") and n[:-5] not in KEEP_IMG] if KEEP_IMG else [])
    shutil.copytree(ROOT / "static", OUT_ROOT / "static", dirs_exist_ok=True, ignore=_skip_imgs)
    make_icons(OUT_ROOT)
    make_og_png(OUT_ROOT / "static" / "og.png")
_old_red = ""
try:  # 301 from old/alias Saudi slugs (already indexed) to the live page, only when the old page is gone and the target exists
    _built = {(i_["category"], i_["slug"]) for i_ in items if not i_.get("nopage")}  # thin items have no page file, so never redirect to them
    _seen = set()
    for _fn in ("slug_redirects.txt", "sa_redirects.txt"):
        _rf = ROOT / "data" / _fn
        if not _rf.exists():
            continue
        for _ln in _rf.read_text(encoding="utf-8").splitlines():
            _p = _ln.split()
            if len(_p) != 2 or _p[0] == _p[1] or _p[0] in _seen:
                continue
            _oc, _os = _p[0].split("/", 1); _nc, _ns = _p[1].split("/", 1)
            if (_oc, _os) in _built or (_nc, _ns) not in _built:
                continue
            if len(_seen) >= 950:  # Cloudflare Pages: ~2000 static redirect rules
                break
            _seen.add(_p[0])
            for _l in ("ar", "en"):
                _old_red += "/sa/%s/%s/ /sa/%s/%s/ 301\n" % (_l, _p[0], _l, _p[1])
except Exception as _e:
    print("redirects skipped:", _e)
write_root("/_redirects", _old_red + "/ar/* /sa/ar/:splat 301\n/en/* /sa/en/:splat 301\n/api/* /sa/api/:splat 301\n/tn/en/* /tn/fr/:splat 301\n/llms-full.txt /sa/llms-full.txt 301\n")  # Cloudflare Pages: a real redirect for the root (the HTML file below stays as a fallback)
write_root("/_headers", "/*\n  X-Content-Type-Options: nosniff\n  Referrer-Policy: strict-origin-when-cross-origin\n\n/sa/api/*\n  Access-Control-Allow-Origin: *\n  Cache-Control: public, max-age=3600\n\n/ae/api/*\n  Access-Control-Allow-Origin: *\n  Cache-Control: public, max-age=3600\n\n/eg/api/*\n  Access-Control-Allow-Origin: *\n  Cache-Control: public, max-age=3600\n\n/tn/api/*\n  Access-Control-Allow-Origin: *\n  Cache-Control: public, max-age=3600\n\n/kw/api/*\n  Access-Control-Allow-Origin: *\n  Cache-Control: public, max-age=3600\n\n/static/*\n  Cache-Control: public, max-age=604800\n")
write_root("/404.html", f'<!doctype html><html lang="ar" dir="rtl"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
                   f'<title>الصفحة غير موجودة | Page not found</title><meta name="robots" content="noindex"></head>'
                   f'<body style="font-family:system-ui,sans-serif;max-width:640px;margin:15vh auto;padding:0 16px;line-height:1.8">'
                   f'<h1>الصفحة غير موجودة</h1><p>تأكد من الرابط أو ابدأ من <a href="/">الصفحة الرئيسية</a>.</p>'
                   f'<h2 dir="ltr" style="text-align:left">Page not found</h2><p dir="ltr">Start from the <a href="/">home page</a>.</p>'
                   # a product page that was merged or removed (old Google result): send the visitor to its category listing instead of a dead end
                   f'<script>(function(){{try{{var m=location.pathname.match(/^\\/(sa|eg|tn|kw|ae)\\/(ar|en|fr)\\/([a-z0-9-]+)\\/([^\\/]+)\\/?$/);if(!m||sessionStorage.getItem("nf"))return;sessionStorage.setItem("nf","1");var u="/"+m[1]+"/"+m[2]+"/"+m[3]+"/";fetch("/"+m[1]+"/api/thin.json").then(function(r){{return r.ok?r.json():{{}}}}).catch(function(){{return{{}}}}).then(function(j){{if(j[m[4]]){{location.replace("/"+m[1]+"/"+m[2]+"/p/#"+m[4]);return}}fetch(u,{{method:"HEAD"}}).then(function(r){{if(r.ok)location.replace(u)}})}})}}catch(e){{}}}})()</script></body></html>')
_ik = cfg.get("indexnow_key")
if _ik:
    write_root(f"/{_ik}.txt", _ik)
OUT.mkdir(parents=True, exist_ok=True)
(OUT / ".nojekyll").write_text("")

urls = []
_seen_sm = set()
for paths in sitemap_entries:
    for lang in LANGS:
        if (paths[lang]) in _seen_sm:
            continue
        _seen_sm.add(paths[lang])
        alts = "".join(f'<xhtml:link rel="alternate" hreflang="{l}" href="{BASE}{paths[l]}"/>' for l in LANGS)
        alts += f'<xhtml:link rel="alternate" hreflang="x-default" href="{BASE}{paths["ar"]}"/>'
        urls.append(f"  <url><loc>{BASE}{paths[lang]}</loc><lastmod>{UPDATED_DATE}</lastmod>{alts}</url>")
write("/sitemap.xml", '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
                      'xmlns:xhtml="http://www.w3.org/1999/xhtml">\n' + "\n".join(urls) + "\n</urlset>\n")

robots = ["User-agent: *", "Disallow: /" if cfg["demo_mode"] else "Allow: /", ""]
if not cfg["demo_mode"]:
    for bot in cfg["ai_crawlers"]:
        robots += [f"User-agent: {bot}", "Allow: /", ""]
robots.append(f"Sitemap: {SITE}/sitemap.xml")
write_root("/robots.txt", "\n".join(robots) + "\n")

llms = [f"# {NAME['en']} ({NAME['ar']})", "",
        f"> {cfg['tagline']['en']}. Independent price comparison for electronics priced above SAR 100 in Saudi Arabia. "
        f"Prices in SAR from official retailer feeds, refreshed daily. Last updated: {UPDATED}.", "",
        "Cite as: " + NAME["en"] + " (" + BASE + "), with the page URL and the last-updated date.", "", "## Categories"]
for c in cfg["categories"]:
    llms.append(f"- [{c['en']}]({BASE}/en/{c['slug']}/): {c['intro']['en']}")
llms += ["", "## Data & trust", f"- [Open data (JSON)]({BASE}/api/products.json): all current best prices, offers and 30-day ranges",
         f"- [Full text for LLMs]({BASE}/llms-full.txt): every product with current prices as plain text",
         f"- [Methodology]({BASE}/en/methodology/): sources, update schedule, validation rules",
         f"- [About]({BASE}/en/about/)", "", "## Arabic", f"- [العربية]({BASE}/ar/)"]
write("/llms.txt", "\n".join(llms) + "\n")
write("/.well-known/ai-catalog.json", json.dumps({"specVersion": "1.0", "entries": [{
    "identifier": "urn:air:" + BASE.split("//")[-1] + ":catalog:products", "displayName": NAME["en"] + " - Saudi price comparison data",
    "type": "application/json", "url": BASE + "/api/products.json",
    "representativeQueries": ["cheapest price for a phone in Saudi Arabia", "compare laptop prices across Saudi stores"]}]}, indent=1) + "\n")

full = [f"# {NAME['en']} - full price list", f"Updated: {UPDATED}. Currency: SAR. Only products above SAR {cfg['min_price']}.", ""]
for i in sorted(items, key=lambda x: (x["category"], x["best"]["price"])):
    full.append(f"## {i['name']['en']} / {i['name']['ar']}")
    full.append(f"URL: {BASE}{i['href']['en']}")
    full.append(f"Lowest price: {plain_money(i['best']['price'])} at {i['best']['store_name']}; 30-day range {plain_money(i['low30'])} - {plain_money(i['high30'])}")
    full.append("Offers: " + "; ".join(f"{o['store_name']} {plain_money(o['price'])}" + ("" if o["in_stock"] else " (out of stock)") for o in i["offers"]))
    full.append("")
write("/llms-full.txt", "\n".join(full))

api = {"name": NAME["en"], "currency": "SAR", "updated": UPDATED, "min_price": cfg["min_price"], "attribution": f"Source: {NAME['en']} ({BASE})",
       "products": [{"id": i["id"], "image": i.get("image"), "brand": i["brand"], "category": i["category"], "name": i["name"],
                     "url": {l: (i["go"] if i.get("nopage") else BASE + i["href"][l]) for l in LANGS},
                     "best": {"price": i["best"]["price"], "store": i["best"]["store_name"], "in_stock": i["best"]["in_stock"]},
                     "low30": i["low30"], "high30": i["high30"],
                     "offers": [{"store": o["store_name"], "price": o["price"], "in_stock": o["in_stock"]} for o in i["offers"]]} for i in items]}
write("/api/products.json", json.dumps(api, ensure_ascii=False, indent=1))
print(f"Thin product pages kept out of the index: {sum(THIN)}")
print(f"Built {len(items)} products, {len(compare_pages)} comparisons -> {OUT}")


# ---------- root build: country chooser, sitemap index, shared machine-readable files ----------
def _live_countries():
    return [c for c in ("ae", "eg", "tn", "kw") if (ROOT / c / "LIVE").exists() and (ROOT / c / "data" / "products.json").exists()]


def _root_pages(live):
    names = {"sa": ("السعودية", "Saudi Arabia"), "ae": ("الإمارات", "United Arab Emirates"), "eg": ("مصر", "Egypt"), "tn": ("تونس", "Tunisia"), "kw": ("الكويت", "Kuwait")}
    codes = ["sa"] + live
    sm = ['<?xml version="1.0" encoding="UTF-8"?>', '<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    sm += [f"  <sitemap><loc>{SITE}/{c}/sitemap.xml</loc><lastmod>{UPDATED_DATE}</lastmod></sitemap>" for c in codes]
    write_root("/sitemap.xml", "\n".join(sm + ["</sitemapindex>", ""]))
    cards = "".join(f'<div class="c"><b>{names[c][0]} · {names[c][1]}</b><p><a href="/{c}/ar/">العربية</a> &nbsp;|&nbsp; <a href="/{c}/{"fr" if c == "tn" else "en"}/">{"Français" if c == "tn" else "English"}</a></p></div>' for c in codes)
    write_root("/index.html", f'<!doctype html><html lang="ar" dir="rtl"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
               f'<title>{NAME["ar"]} | {NAME["en"]} - اختر دولتك | Choose your country</title>'
               f'<meta name="description" content="قارن أسعار الجوالات والأجهزة الإلكترونية بين المتاجر في بلدك. Compare electronics prices across stores in your country.">'
               f'<link rel="canonical" href="{SITE}/"><link rel="icon" href="/favicon.ico">'
               f'<style>body{{font-family:system-ui,sans-serif;max-width:640px;margin:10vh auto;padding:0 16px;line-height:1.9;text-align:center}}'
               f'.c{{border:1px solid #cfd8d5;border-radius:12px;padding:12px 16px;margin:12px 0}}a{{color:#0B6B5B;font-weight:600}}</style></head>'
               f'<body><h1>{NAME["ar"]} <small dir="ltr">· {NAME["en"]}</small></h1><p>اختر دولتك · Choose your country</p>{cards}</body></html>')
    for f in ("llms.txt", ".well-known/ai-catalog.json"):
        src = OUT / f
        if src.exists():
            write_root("/" + f, src.read_text(encoding="utf-8"))


if IS_ROOT:
    _root_pages(_live_countries())

# On the host's build (Cloudflare sets CF_PAGES) dist/ is not committed, so rebuild every live country here too.
if IS_ROOT and os.environ.get("CF_PAGES"):
    import subprocess
    for _c in _live_countries():
        subprocess.run([sys.executable, str(Path(__file__).resolve())], env={**os.environ, "COUNTRY": _c}, check=False)
