#!/usr/bin/env python3
"""Post-process dist/sa -> dist-para/para/sa : serve everything under /para/ prefix."""
import os, re, shutil, sys

SRC = "dist/sa"
OUT = "dist-para"
shutil.rmtree(OUT, ignore_errors=True)
os.makedirs(OUT + "/para")
shutil.copytree(SRC, OUT + "/para/sa")


SUBS = [
    (re.compile(r'is an independent price comparison site for electronics \([^"<]*?(?:\.\.\.|updated daily\.)'), 'is an independent price comparison site for beauty and personal-care products in Saudi stores...'),
    (re.compile(r'لمقارنة أسعار الإلكترونيات \([^"<]*?(?:\.\.\.|ويُحدَّث يومياً\.)'), 'لمقارنة أسعار منتجات التجميل والعناية في المتاجر السعودية...'),
    (re.compile(r'(["\'(=])/sa/'), r'\1/para/sa/'),            # internal links
    (re.compile(r'(["\'(=])/tn/'), r'\1/para/tn/'),            # country switcher: Tunisian para
    (re.compile(r'https://kolasaar\.com/para/static/'), 'https://kolasaar.com/static/'),   # shared assets live on the main site
    (re.compile(r'url=/ar/'), 'url=/para/sa/ar/'),
    (re.compile(r'تُحدَّث الأسعار مرة يومياً، ويظهر'), 'يظهر'),
    (re.compile(r'، ويُحدَّث يومياً\.'), '.'),
    (re.compile(r'مع استمرار التتبع اليومي'), 'مع استمرار تتبع الأسعار'),
    (re.compile(r'وتُحدَّث يومياً'), 'مع عرض تاريخ آخر تحديث'),
    (re.compile(r'ونحدّثها يومياً'), 'مع عرض تاريخ آخر تحديث'),
    (re.compile(r'نحدّث الأسعار يومياً'), 'نعرض تاريخ آخر تحديث للأسعار'),
]

PAIRS = [
    (" أما أدلة الشراء في صفحات الأقسام فكتبناها يدوياً من معلومات عامة موثوقة (مثل سعة التبريد المناسبة لمساحة الغرفة). نحن لا نختبر الأجهزة بأنفسنا ولا ننشر مراجعات مختلقة", " نحن لا نختبر المنتجات بأنفسنا ولا ننشر مراجعات مختلقة"),
    (" The buying guides on category pages are written by hand from reliable general knowledge (for example, the cooling capacity that suits a given room size). We do not test devices ourselves and never publish invented reviews", " We do not test products ourselves and never publish invented reviews"),
    ("بإذن منها وبوتيرة هادئة", "وبوتيرة هادئة"),
    (", with their permission and at a gentle pace", ", at a gentle pace"),
    ("نعدّ منتجين متطابقين فقط إذا اتفقا في الماركة والموديل وسعة التخزين، وفي الفئة (مثل Pro أو Plus) والشبكة (4G أو 5G) والرام حين تُذكر. الألوان تُدمج في منتج واحد. إذا لم نتأكد لا ندمج.", "نعدّ عرضين لمنتج واحد أولاً إذا اتفق الباركود (EAN/GTIN) الصالح، وإلا فإذا تطابق الاسم والماركة والحجم أو العدد (مثل 200 مل أو 30 كبسولة) بدرجة عالية. لا ندمج أبداً منتجين لهما باركودان مختلفان، وإذا لم نتأكد لا ندمج. ولا ننشر منتجاً إلا إذا كان متوفراً حالياً في متجرين على الأقل."),
    ("Two listings count as the same product only if they agree on brand, model and storage size, and on the variant (Pro, Plus...), network (4G/5G) and RAM when those are stated. Colours are merged into one product. If we are not sure, we do not merge.", "Two offers are linked to the same product first if the valid barcode (EAN/GTIN) matches; otherwise only if name, brand and size or unit count (for example 200 ml or 30 capsules) are very close. We never merge two products with different barcodes, and when unsure we do not merge. A product is published only if it is currently in stock at two or more stores."),
    ("على /api/products.json", "على /para/sa/api/products.json"),
    ("at /api/products.json", "at /para/sa/api/products.json"),
    ("وبوتيرة هادئة", "وبوتيرة هادئة"),
    ("ابحث عن جوال أو تلفزيون أو ثلاجة أو مكيف", "ابحث عن منتج أو ماركة"),
    ("Search phones, TVs, fridges, ACs", "Search products or brands"),
    ("نعرض المنتجات التي يزيد سعرها عن 100 ريال سعودي.", "نعرض فقط المنتجات المتوفرة في متجرين على الأقل."),
    ("We list products priced above SAR 100.", "We list only products available at two or more stores."),
    ("قارن أسعار الجوالات والأجهزة الإلكترونية بين المتاجر في بلدك. Compare electronics prices across stores in your country.", "قارن أسعار منتجات التجميل والعناية بين المتاجر السعودية. Compare beauty and personal-care prices across Saudi stores."),
    ("موقع مستقل لمقارنة أسعار الإلكترونيات (الهواتف واللابتوبات والتابلت والتلفزيونات والشاشات والثلاجات والمكيفات وأفران الميكروويف والغسالات والأفران) التي يزيد سعرها عن 100 ريال سعودي في المتاجر السعودية، ويُحدَّث يومياً.", "موقع مستقل لمقارنة أسعار منتجات التجميل والعناية (البشرة والشعر والجسم والمكياج والعطور والحماية من الشمس والأم والطفل والمكملات) في المتاجر السعودية، مع عرض تاريخ آخر تحديث لكل سعر."),
    ("is an independent price comparison site for electronics (phones, laptops and tablets, TVs and monitors, refrigerators, air conditioners, microwaves, washing machines and ovens) priced above SAR 100 in Saudi stores, updated daily.", "is an independent price comparison site for beauty and personal-care products (skin, hair, body, makeup, fragrance, sun care, mother and baby, supplements) in Saudi stores; every price shows its last-update date."),
    ("نقارن حالياً بين: جرير، المنعم، إكسترا، نون، أمازون السعودية، ترينديول، سعيد. نضيف متاجر جديدة بعد الحصول على إذن منها.", "نقارن حالياً بين متاجر سعودية للتجميل والعناية والصيدليات الإلكترونية، وتظهر أسماؤها في كل صفحة منتج."),
    ("We currently compare: Jarir, Almanea, eXtra, Noon, Amazon.sa, Trendyol and Saeel. New stores are added only after we have their permission.", "We currently compare Saudi beauty, personal-care and online-pharmacy stores; the stores are named on every product page."),
    ("اختلاف النسخ", "الحجم والعروض"),
    ("قد تختلف الأسعار بين نسخة الشرق الأوسط والنسخة الدولية أو العالمية (Global/International) لأن الضمان والمواصفات قد تختلف. تحقق من نسخة المنتج في صفحة المتجر قبل الشراء.", "قد تختلف الأسعار بحسب الحجم والعرض الترويجي ومصاريف التوصيل، ولذلك نطابق الحجم أو العدد قبل أن نقارن. تحقق من التفاصيل في صفحة المتجر قبل الشراء."),
    ("Regional versions", "Size and offers"),
    ("Prices can differ between the Middle East version and international/global versions because warranty and specifications may differ. Check the version on the store page before buying.", "Prices can vary with size, current promotion and delivery fees, which is why we match size or unit count before comparing. Check the details on the store page before buying."),
    ("تُحدَّث الأسعار مرة يومياً، ويظهر وقت آخر تحديث في كل صفحة وفي البيانات المفتوحة.", "يظهر تاريخ آخر تحديث للأسعار في كل صفحة وفي البيانات المفتوحة."),
    ("Prices update once a day; the last-update time is shown on every page and in the open data.", "The last-update date is shown on every page and in the open data."),
    ("نستبعد الأسعار غير الصالحة والأقل من 100 ريال، وإذا اختلف سعرا متجرين بأكثر من 40% لا ننشر أياً منهما لأننا لا نعرف الصحيح، ونستبعد السعر الذي يبتعد كثيراً عن وسيط الأسعار.", "نستبعد الأسعار غير الصالحة (الصفر أو السالبة)، ونستبعد السعر الذي ينخفض عن وسيط أسعار المنتج بأكثر من 30٪ أو يرتفع عنه بأكثر من 45٪. وإذا بقي متجران فقط وتجاوز الفارق بين سعريهما 50٪ لا ننشر المنتج لأننا لا نعرف السعر الصحيح."),
    ("We drop invalid prices and prices below SAR 100. If two stores disagree by more than 40% we publish neither, because we cannot tell which is right, and we drop prices far from the median.", "We drop invalid (zero or negative) prices and prices more than 30% below or 45% above the product's median. If only two stores remain and their prices differ by more than 50%, we do not publish the product because we cannot tell which is right."),
    ("قد تختلف الأسعار بحسب النسخة (محلية أو دولية) والضمان وما يتضمنه العرض؛ راجع تفاصيل المنتج في صفحة المتجر قبل الشراء.", "قد تختلف الأسعار بحسب الحجم والعرض الترويجي ومصاريف التوصيل؛ راجع تفاصيل المنتج في صفحة المتجر قبل الشراء."),
    ("Prices can differ by version (local or international), warranty and what the offer includes; check the product details on the store page before buying.", "Prices can vary with size, promotion and delivery fees; check the product details on the store page before buying."),
    ("نعرض فقط المنتجات المتوفرة في متجرين على الأقل. Prices", "Prices"),
    ("Independent price comparison for electronics priced above SAR 100 in Saudi Arabia. Prices in SAR from official retailer feeds, refreshed daily. Last updated:", "Independent price comparison for beauty and personal-care products in Saudi Arabia. Prices in SAR collected from the stores' public pages; every page shows the date of the last update. Last updated:"),
    ('"cheapest price for a phone in Saudi Arabia", "compare laptop prices across Saudi stores"', '"cheapest price for a sunscreen in Saudi Arabia", "compare perfume prices across Saudi stores"'),
    ("cheapest price for a phone in Saudi Arabia", "cheapest price for a sunscreen in Saudi Arabia"),
    ("compare laptop prices across Saudi stores", "compare perfume prices across Saudi stores"),
    ("Prices are collected from the stores' pages, update daily and may change at the store.", "Prices are collected from the stores' pages, with the last-update date shown, and may change at the store."),
    ("الأسعار تُجمع من صفحات المتاجر وتُحدَّث يومياً وقد تتغير في المتجر.", "الأسعار تُجمع من صفحات المتاجر مع عرض تاريخ آخر تحديث، وقد تتغير في المتجر."),
    ("ونحدّثها يومياً", "مع عرض تاريخ آخر تحديث"),
    ("and are updated daily", "with the last-update date shown"),
    ("وتُحدَّث يومياً", "مع عرض تاريخ آخر تحديث"),
    ("، ويُحدَّث يومياً", ""),
    ("updated daily", "with last-update date"),
    ("نحدّث الأسعار يومياً", "نعرض تاريخ آخر تحديث للأسعار"),
    ("Prices are updated daily", "Each price shows its last-update date"),
]
LIT = []
for a, b in PAIRS:
    LIT.append((a, b))
    LIT.append((a.replace("'", "&#39;"), b.replace("'", "&#39;")))
n = 0
for root, _, files in os.walk(OUT + "/para/sa"):
    for f in files:
        if not f.endswith((".html", ".xml", ".txt", ".json")):
            continue
        p = os.path.join(root, f)
        s = open(p, encoding="utf-8").read()
        o = s
        for rx, rep in SUBS:
            s = rx.sub(rep, s)
        for a_, b_ in LIT:
            s = s.replace(a_, b_)
        if s != o:
            open(p, "w", encoding="utf-8").write(s)
            n += 1
print("rewrote", n)

# entry redirects (Cloudflare Pages)
open(OUT + "/_redirects", "w").write(
    "/para/sa /para/sa/ar/ 301\n/para/sa/ /para/sa/ar/ 301\n")
open(OUT + "/robots.txt", "w").write(
    "User-agent: *\nAllow: /\n\nSitemap: https://kolasaar.com/para/sa/sitemap.xml\n")


# --- staged opening: sa/INDEX_OK lists the sections that are open for indexing (one slug per line; "all" opens everything).
# Sections not listed stay noindex and are left out of the sitemap until they are added to the file.
if os.path.exists("sa/INDEX_OK"):
    ALLC = ["visage", "corps", "hygiene", "maquillage", "cheveux", "parfum", "bebe", "solaire", "brand"]
    OPEN = {l.strip() for l in open("sa/INDEX_OK", encoding="utf-8") if l.strip() and not l.startswith("#")}
    CLOSED = [] if "all" in OPEN else [c for c in ALLC if c not in OPEN]
    if CLOSED:
        pat = re.compile(r"/para/sa/(?:ar|en)/(?:%s)(?:/|$)" % "|".join(CLOSED))
        nclosed = 0
        for root, _, files in os.walk(OUT + "/para/sa"):
            for f in files:
                if f.endswith(".html"):
                    p = os.path.join(root, f)
                    rel = "/" + os.path.relpath(p, OUT).replace(os.sep, "/")
                    if pat.search(rel):
                        s = open(p, encoding="utf-8").read()
                        s2 = re.sub(r'<meta name="robots"[^>]*>', '<meta name="robots" content="noindex,follow">', s)
                        if s2 != s:
                            open(p, "w", encoding="utf-8").write(s2)
                        nclosed += 1
        sp = OUT + "/para/sa/sitemap.xml"
        sm = open(sp, encoding="utf-8").read()
        kept = [l for l in sm.split("\n") if not (l.strip().startswith("<url>") and pat.search(re.search(r"<loc>([^<]*)</loc>", l).group(1).replace("https://kolasaar.com", "")))]
        open(sp, "w", encoding="utf-8").write("\n".join(kept))
        print("staged opening: closed", CLOSED, "pages", nclosed, "sitemap urls", len([l for l in kept if "<url>" in l]))
    else:
        print("indexing fully open")
# --- launch gate: pages stay noindex until the owner verifies the data and creates sa/INDEX_OK
if not os.path.exists("sa/INDEX_OK"):
    import re as _re
    for root, _, files in os.walk(OUT + "/para/sa"):
        for f in files:
            if f.endswith(".html"):
                p = os.path.join(root, f)
                s = open(p, encoding="utf-8").read()
                s2 = _re.sub(r'<meta name="robots"[^>]*>', '<meta name="robots" content="noindex,nofollow">', s)
                if s2 != s:
                    open(p, "w", encoding="utf-8").write(s2)
    open(OUT + "/_headers", "w").write("/para/sa/*\n  X-Robots-Tag: noindex, nofollow\n")
    open(OUT + "/robots.txt", "w").write("User-agent: *\nDisallow: /\n")
    print("noindex gate ON")
