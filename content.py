"""Per-product advice built from the product's real data: specs, store prices, stock and 30-day history.
Everything here is derived from facts we hold or from well-known properties of the product *type*. We do not invent test results
or reviews. Several phrasings per sentence are chosen by a stable hash of the product id so pages do not read as clones."""
import re
import zlib


def _pick(pid, salt, options):
    return options[zlib.crc32(f"{pid}:{salt}".encode()) % len(options)]


def _num(s):
    m = re.search(r"(\d+(?:\.\d+)?)", str(s or ""))
    return float(m.group(1)) if m else None


def _position(p):
    """0 = at the 30-day low, 1 = at the 30-day high; None when there is no range."""
    lo, hi, cur = p.get("low30"), p.get("high30"), p["best"]["price"]
    if lo is None or hi is None or hi - lo < max(1, cur * 0.01):
        return None
    return max(0.0, min(1.0, (cur - lo) / (hi - lo)))


# ----------------------------------------------------------------- spec rules: (strengths, watch-outs, good-for, not-for) per language
def spec_notes(p, lang):
    cat, sp = p["category"], p.get("specs") or {}
    ar = lang == "ar"
    pros, cons, good, notgood = [], [], [], []

    def add(lst, a, e):
        lst.append(a if ar else e)

    cap, typ = sp.get("capacity"), (sp.get("type") or "")
    capn = _num(cap)

    if cat == "acs":
        if capn:
            if capn <= 13000:
                add(good, "غرفة نوم أو مكتب حتى نحو 15 متراً مربعاً", "a bedroom or office up to about 15 m²")
                add(notgood, "صالة واسعة أو غرفة مكشوفة للشمس: السعة ستكون ضعيفة عليها", "a large living room or a sun-exposed room: this capacity will struggle")
            elif capn <= 20000:
                add(good, "غرفة أو مجلس بين 20 و28 متراً مربعاً تقريباً", "a room or majlis of roughly 20-28 m²")
                add(notgood, "صالة كبيرة تتجاوز 30 متراً مربعاً", "a big hall over 30 m²")
            else:
                add(good, "صالة أو مجلس كبير يتجاوز 30 متراً مربعاً", "a large hall or majlis over 30 m²")
                add(notgood, "غرفة صغيرة: السعة أكبر من اللازم وسترفع الاستهلاك دون فائدة", "a small room: the capacity is more than needed and wastes power")
        if sp.get("inverter"):
            add(pros, "ضاغط إنفرتر: يستهلك كهرباء أقل عادة ويعمل بهدوء أكبر", "Inverter compressor: usually lower power use and quieter running")
        else:
            add(cons, "لا يذكر العنوان تقنية الإنفرتر، فقد يستهلك كهرباء أكثر في التشغيل الطويل", "The listing does not mention inverter technology, so running costs may be higher over long use")
        if "Window" in typ:
            add(cons, "مكيف شباك: أعلى صوتاً من السبليت", "Window unit: louder than a split")
        elif "Portable" in typ:
            add(cons, "مكيف متنقل: أقل كفاءة من السبليت ويناسب الاستخدام المؤقت", "Portable unit: less efficient than a split, best for temporary use")
        elif "Split" in typ:
            add(pros, "سبليت: أهدأ وتوزيع هواء أفضل من الشباك", "Split type: quieter with better air distribution than a window unit")
            add(cons, "يحتاج تركيباً ومواسير، فاحسب تكلفتها", "Needs installation and piping, so factor in the cost")
    elif cat == "fridges":
        if capn:
            if capn < 300:
                add(good, "فرد أو فردان أو سكن صغير", "one or two people or a small flat")
                add(notgood, "أسرة من 4 أفراد فأكثر: السعة لن تكفي تسوّق الأسبوع", "a household of four or more: it will not hold a week's shopping")
            elif capn < 480:
                add(good, "أسرة من 3 إلى 4 أفراد", "a household of three to four")
                add(notgood, "أسرة كبيرة أو من يخزّن بكثرة", "a large family or heavy stockers")
            else:
                add(good, "أسرة كبيرة أو من يتسوق بكميات كبيرة", "a large family or bulk shoppers")
                add(notgood, "مطبخ صغير أو سكن لفردين: مساحة وتكلفة كهرباء أكبر من الحاجة", "a small kitchen or a couple: more space and power than needed")
        if "Side" in typ or "French" in typ or "Multi" in typ:
            add(pros, "تصميم واسع بأبواب متعددة وسعة تخزين كبيرة", "Wide multi-door layout with generous storage")
            add(cons, "يحتاج عرض مطبخ وباب دخول مناسباً، وسعره أعلى من الفريزر العلوي", "Needs kitchen width and a wide enough doorway, and costs more than a top-freezer")
        elif "Top" in typ:
            add(pros, "فريزر علوي: الأبسط والأرخص عادة", "Top freezer: usually the simplest and cheapest layout")
            add(cons, "الأرفف السفلية تتطلب الانحناء، والفريزر أصغر من الجنب إلى جنب", "Lower shelves need bending, and the freezer is smaller than a side-by-side")
        elif "Bottom" in typ:
            add(pros, "الثلاجة الأكثر استخداماً على مستوى العين", "The most-used fridge section sits at eye level")
        elif "Single" in typ:
            add(cons, "باب واحد: فريزر صغير أو بلا فريزر مستقل", "Single door: small or no separate freezer")
    elif cat == "washers":
        if capn:
            if capn <= 7.5:
                add(good, "فرد أو فردان أو أسرة صغيرة", "one or two people or a small household")
                add(notgood, "أسرة كبيرة: ستحتاج غسلات أكثر في الأسبوع", "a large family: you will need more loads each week")
            elif capn <= 9.5:
                add(good, "أسرة من 3 إلى 4 أفراد", "a household of three to four")
                add(notgood, "الأغطية الكبيرة واللحف بشكل متكرر", "frequent large duvets and bedding")
            else:
                add(good, "أسرة كبيرة أو من يغسل الأغطية الكبيرة", "a large family or anyone washing big bedding")
                add(notgood, "من يغسل كميات صغيرة غالباً: تشغيلها بحمولة ناقصة يهدر ماءً وكهرباء", "people who wash small loads: running it half-empty wastes water and power")
        if "Front" in typ:
            add(pros, "تحميل أمامي: أرفق بالملابس ويستهلك ماءً أقل", "Front load: gentler on clothes and uses less water")
            add(cons, "برنامج أطول وسعر أعلى من العلوي، ويحتاج ضغط ماء جيداً", "Longer cycles and a higher price than top load, and wants good water pressure")
        elif "Top" in typ:
            add(pros, "تحميل علوي: أسرع وأرخص ويمكن إضافة ملابس أثناء الغسيل", "Top load: faster and cheaper, and you can add clothes mid-cycle")
            add(cons, "يستهلك ماءً أكثر وأقل رفقاً بالأقمشة الحساسة", "Uses more water and is less gentle on delicate fabrics")
        if re.search(r"twin|tub", p.get("name_full", p["name"])["en"], re.I):
            add(cons, "توأم (حوضان): يحتاج نقل الغسيل يدوياً بين الحوضين", "Twin tub: you move washing between tubs by hand")
            add(pros, "الأرخص وبسيط الصيانة", "Cheapest and simple to maintain")
    elif cat == "microwaves":
        if "Grill" in typ:
            add(pros, "يضيف شواء لتحمير الوجه", "Adds a grill to brown the top")
        elif "Convection" in typ:
            add(pros, "يعمل كفرن صغير ويخبز", "Works as a small oven and can bake")
            add(cons, "أغلى من النوع العادي", "Costs more than a solo model")
        else:
            add(cons, "نوع عادي: للتسخين والتذويب فقط", "Solo type: reheating and defrosting only")
            add(good, "من يحتاج التسخين اليومي فقط", "people who just reheat food daily")
    elif cat == "ovens":
        if "Built" in typ:
            add(pros, "فرن مدمج: يعطي مظهراً متناسقاً في المطبخ", "Built-in: a neat integrated kitchen look")
            add(cons, "يحتاج فتحة تركيب مناسبة في خزانة المطبخ", "Needs a suitable cut-out in your kitchen units")
        if capn and capn >= 70:
            add(pros, "سعة كبيرة تتسع لأكثر من صينية", "Large capacity fits more than one tray")
    elif cat == "tvs":
        size, panel = _num(sp.get("size")), (sp.get("panel") or "").upper()
        if size:
            if size <= 43:
                add(good, "غرفة نوم أو مكتب أو مسافة مشاهدة تحت مترين", "a bedroom, office or viewing distance under 2 m")
                add(notgood, "صالة كبيرة", "a big living room")
            elif size <= 58:
                add(good, "غرفة معيشة متوسطة بمسافة مشاهدة نحو 2.5 متر", "a mid-size living room about 2.5 m from the sofa")
            else:
                add(good, "صالة كبيرة بمسافة مشاهدة 3 أمتار فأكثر", "a large living room with 3 m or more of viewing distance")
                add(notgood, "غرفة صغيرة: الشاشة ستكون أكبر من اللازم", "a small room: the screen will overwhelm it")
        if "OLED" in panel and "QLED" not in panel:
            add(pros, "أسود حقيقي وتباين ممتاز", "True blacks and excellent contrast")
            add(cons, "أقل سطوعاً في الغرف المشمسة وسعر أعلى", "Less bright in sunny rooms, and pricier")
        elif "QLED" in panel or "QNED" in panel or "NANOCELL" in panel.replace(" ", ""):
            add(pros, "ألوان وسطوع أعلى من LED العادي", "Richer colour and brightness than standard LED")
        elif panel == "LED":
            add(cons, "LED عادي: تباين أقل من QLED وOLED", "Standard LED: lower contrast than QLED or OLED")
            add(good, "الغرف المضيئة والميزانية المحدودة", "bright rooms and tight budgets")
    elif cat == "phones":
        stor, ram = _num(sp.get("storage")), _num(sp.get("ram"))
        if stor:
            if stor <= 64:
                add(cons, f"{int(stor)} جيجا تمتلئ بسرعة مع الصور والتطبيقات", f"{int(stor)} GB fills quickly with photos and apps")
            elif stor >= 256:
                add(pros, f"{int(stor)} جيجا مريحة للصور والفيديو لسنوات", f"{int(stor)} GB is comfortable for photos and video for years")
            else:
                add(pros, f"{int(stor)} جيجا كافية للاستخدام اليومي", f"{int(stor)} GB covers everyday use")
        if ram:
            if ram >= 12:
                add(good, "الألعاب الثقيلة وتعدد المهام", "heavy gaming and multitasking")
            elif ram <= 4:
                add(cons, f"ذاكرة {int(ram)} جيجا محدودة لتعدد المهام", f"{int(ram)} GB RAM is limited for multitasking")
                add(notgood, "الألعاب الثقيلة", "heavy gaming")
        if re.search(r"international|عالمي|دولي", p.get("name_full", p["name"])["en"] + p.get("name_full", p["name"])["ar"], re.I):
            add(cons, "نسخة دولية: تحقق من الضمان والوكيل المحلي", "International version: check the warranty and local service")
    elif cat == "laptops":
        ram, stor = _num(sp.get("ram")), _num(sp.get("storage"))
        if ram:
            if ram >= 16:
                add(pros, f"ذاكرة {int(ram)} جيجا مريحة للدراسة والعمل", f"{int(ram)} GB RAM is comfortable for study and work")
            elif ram <= 8:
                add(cons, f"ذاكرة {int(ram)} جيجا قد تضيق مع المتصفح وبرامج متعددة", f"{int(ram)} GB RAM can get tight with a browser and several apps")
                add(notgood, "المونتاج والتصميم والألعاب", "video editing, design and gaming")
        if stor:
            if stor >= 512:
                add(pros, f"تخزين {int(stor) if stor < 1000 else int(stor)} جيجا يكفي لأغلب المستخدمين", f"{int(stor)} GB storage suits most users")
            elif stor <= 256:
                add(cons, f"تخزين {int(stor)} جيجا محدود", f"{int(stor)} GB storage is limited")
    elif cat == "watches":
        name = p.get("name_full", p["name"])["en"]
        size = _num(sp.get("size"))
        conn = sp.get("connectivity") or ""
        if re.search(r"apple", name, re.I):
            add(cons, "تعمل مع آيفون فقط ولا تدعم هواتف أندرويد", "Works with iPhone only and does not support Android phones")
            add(notgood, "من يستخدم هاتف أندرويد", "anyone using an Android phone")
            add(good, "مستخدم آيفون يريد أفضل تكامل مع هاتفه", "an iPhone user who wants the tightest integration")
        elif re.search(r"samsung|galaxy", name, re.I):
            add(pros, "تكامل أفضل مع هواتف أندرويد وخصوصاً سامسونج", "Best integration with Android phones, Samsung in particular")
            add(cons, "لا تعمل مع آيفون", "Does not work with iPhone")
            add(notgood, "مستخدم آيفون", "iPhone users")
        elif re.search(r"garmin", name, re.I):
            add(pros, "ساعة موجهة للرياضة والتتبع الدقيق وبطارية تدوم طويلاً عادةً", "Built for sport and precise tracking, usually with long battery life")
            add(cons, "تطبيقاتها وردودها الذكية أقل من ساعات آبل وسامسونج", "Fewer apps and smart replies than Apple or Samsung watches")
            add(good, "الجري والدراجات والرياضات الخارجية", "running, cycling and outdoor sport")
        elif re.search(r"huawei", name, re.I):
            add(pros, "تعمل مع أندرويد وآيفون وبطارية أطول من أغلب الساعات الذكية", "Works with Android and iPhone, with longer battery than most smartwatches")
            add(cons, "متجر تطبيقات أصغر من آبل وسامسونج", "A smaller app store than Apple or Samsung")
        if size:
            if size <= 41:
                add(good, "معصم نحيف أو صغير", "a slim or small wrist")
                add(notgood, "من يريد شاشة أكبر وأسهل قراءة", "anyone who wants a bigger, easier-to-read screen")
            elif size >= 46:
                add(good, "معصم كبير ومن يفضّل شاشة واسعة", "a larger wrist and anyone who prefers a big screen")
                add(notgood, "معصم نحيف: قد تبدو كبيرة وثقيلة", "slim wrists: it may feel big and heavy")
        if "Cellular" in conn:
            add(pros, "تعمل بشريحة eSIM مستقلة دون الهاتف", "Works on its own eSIM without the phone")
            add(cons, "تحتاج باقة مدفوعة من شركة الاتصالات وتستهلك البطارية أكثر", "Needs a paid carrier plan and drains the battery faster")
        elif conn in ("GPS", "Bluetooth"):
            add(cons, "تعتمد على هاتفك القريب للمكالمات والرسائل", "Relies on your nearby phone for calls and messages")
    elif cat == "earbuds":
        name = p.get("name_full", p["name"])["en"]
        kind = (sp.get("type") or "")
        anc = (sp.get("anc") or "") == "Yes"
        if "Over-ear" in kind or "Headphones" in kind:
            add(pros, "سماعة رأس: راحة أطول وبطارية أكبر عادةً", "Over-ear: usually more comfortable for long use, with a bigger battery")
            add(cons, "أكبر حجماً وأقل ملاءمة للرياضة", "Bulkier and less suited to exercise")
            add(good, "العمل والسفر والاستماع الطويل", "work, travel and long listening sessions")
        else:
            add(pros, "حجم صغير وسهلة الحمل مع علبة شحن", "Small and easy to carry with a charging case")
            add(cons, "بطارية السماعة نفسها أقصر من سماعات الرأس وقد تضيع بسهولة", "Shorter battery than over-ear headphones, and easy to lose")
            add(good, "الرياضة والمواصلات", "exercise and commuting")
        if anc:
            add(pros, "عزل ضوضائي نشط يخفف ضجيج المواصلات والمكاتب", "Active noise cancelling reduces commute and office noise")
            add(cons, "بعض المستخدمين لا يرتاحون لإحساس الضغط في الأذن", "Some people dislike the pressure feeling in the ear")
        else:
            add(notgood, "من يحتاج عزلاً قوياً للضوضاء في المواصلات", "anyone who needs strong noise isolation on a commute")
        if re.search(r"airpods", name, re.I):
            add(good, "مستخدم آيفون: اقتران فوري وتكامل مع النظام", "iPhone users: instant pairing and system integration")
            add(cons, "مع أندرويد تعمل كبلوتوث عادي بميزات أقل", "On Android it works as plain Bluetooth with fewer features")
        elif re.search(r"galaxy buds", name, re.I):
            add(good, "مستخدم هاتف سامسونج", "Samsung phone owners")
            add(cons, "ميزاتها الكاملة تحتاج هاتف سامسونج", "Full features need a Samsung phone")
    elif cat == "consoles":
        name = p.get("name_full", p["name"])["en"]
        ed = (sp.get("edition") or "")
        stor = _num(sp.get("storage"))
        if re.search(r"digital", name + ed, re.I):
            add(pros, "أرخص من نسخة الأقراص", "Cheaper than the disc edition")
            add(cons, "لا تشغّل الأقراص: الألعاب من المتجر الإلكتروني فقط ولا يمكن إعادة بيعها", "No disc drive: games come from the online store only and cannot be resold")
            add(notgood, "من يشتري ألعاباً مستعملة أو يتبادلها", "anyone who buys used games or swaps them")
        elif re.search(r"disc", ed, re.I):
            add(pros, "تشغّل الأقراص ويمكن إعادة بيع الألعاب أو استعارتها", "Plays discs, so games can be resold or lent")
            add(cons, "أغلى من النسخة الرقمية", "Costs more than the digital edition")
        if stor:
            tb = stor / 1000 if "GB" in (sp.get("storage") or "").upper() else stor
            gb = stor if "GB" in (sp.get("storage") or "").upper() else stor * 1000
            if gb <= 520:
                add(cons, "مساحة محدودة: ألعاب كبيرة قليلة تملؤها", "Limited space: a few big games will fill it")
                add(notgood, "من يحمّل ألعاباً كثيرة", "people who install many games")
            elif gb >= 1000:
                add(pros, "مساحة كبيرة لعدد جيد من الألعاب", "Plenty of space for a good number of games")
        if re.search(r"pro\b", name, re.I):
            add(pros, "الأقوى أداءً في عائلة بلايستيشن 5", "The most powerful PlayStation 5")
            add(cons, "سعر أعلى بكثير وفارق أداء يلاحظه أصحاب شاشات 4K الحديثة غالباً", "Much pricier, and the gain is mostly noticed on modern 4K screens")
        if re.search(r"switch", name, re.I):
            add(pros, "تلعب في البيت أو متنقلاً وألعاب عائلية ممتازة", "Play at home or on the move, with excellent family games")
            add(cons, "رسومات أضعف من بلايستيشن وإكس بوكس", "Weaker graphics than PlayStation and Xbox")
        if re.search(r"series s", name, re.I):
            add(cons, "رقمي فقط وأقل قوة من Series X", "Digital only and less powerful than the Series X")
        if re.search(r"steam deck", name, re.I):
            add(pros, "مكتبة ألعاب الكمبيوتر في جهاز محمول", "A PC game library in a handheld")
            add(cons, "البطارية تنفد بسرعة في الألعاب الثقيلة وبعض الألعاب لا تعمل", "Battery drains quickly in demanding games and some games do not run")
    return pros, cons, good, notgood


# ------------------------------------------------------------------------------------------------- verdict
def verdict(p, lang, money, plain_money):
    """3-5 sentences: where to buy it, how the price sits against the last 30 days, stock, and the one thing to check."""
    ar = lang == "ar"
    n, offs, b = p["name"][lang], p["offers"], p["best"]
    pid = p["id"]
    ins = [o for o in offs if o["in_stock"]]
    cheapest_in = min(ins, key=lambda o: o["price"]) if ins else None
    pos = _position(p)
    s = []
    if cheapest_in and cheapest_in is not b and b["price"] < cheapest_in["price"]:
        s.append((f"أرخص سعر هو {money(b['price'], 'ar')} في {b['store_name']} لكنه غير متوفر حالياً؛ أرخص متجر متوفر هو {cheapest_in['store_name']} بسعر {money(cheapest_in['price'], 'ar')}."
                  if ar else f"The lowest price is {plain_money(b['price'])} at {b['store_name']} but it is out of stock; the cheapest store with stock is {cheapest_in['store_name']} at {plain_money(cheapest_in['price'])}."))
    elif cheapest_in:
        s.append(_pick(pid, "buy", [
            f"أفضل مكان للشراء حالياً هو {cheapest_in['store_name']} بسعر {money(cheapest_in['price'], 'ar')}، وهو متوفر.",
            f"إن كنت تريد أقل سعر فالخيار الأرخص المتوفر الآن هو {cheapest_in['store_name']} عند {money(cheapest_in['price'], 'ar')}.",
            f"{cheapest_in['store_name']} يعرض أقل سعر متوفر اليوم: {money(cheapest_in['price'], 'ar')}."]) if ar else _pick(pid, "buy", [
            f"The best place to buy right now is {cheapest_in['store_name']} at {plain_money(cheapest_in['price'])}, in stock.",
            f"For the lowest in-stock price, {cheapest_in['store_name']} is cheapest today at {plain_money(cheapest_in['price'])}.",
            f"{cheapest_in['store_name']} lists the lowest in-stock price today: {plain_money(cheapest_in['price'])}."]))
    else:
        s.append("لا يوجد متجر يعرض هذا المنتج متوفراً حالياً، لذا تابع السعر وارجع لاحقاً." if ar else "No store lists this in stock right now, so keep an eye on the price and come back.")
    if pos is not None:
        lo, hi = p["low30"], p["high30"]
        if pos <= 0.2:
            s.append((f"السعر قريب من أدنى مستوى له خلال 30 يوماً ({money(lo, 'ar')})، فالتوقيت جيد نسبياً." if ar
                      else f"The price is near its 30-day low ({plain_money(lo)}), so the timing is relatively good."))
        elif pos >= 0.8:
            s.append((f"السعر قريب من أعلى مستوى خلال 30 يوماً ({money(hi, 'ar')}) بينما نزل إلى {money(lo, 'ar')}؛ إن لم تكن مستعجلاً فتابع تغيّره." if ar
                      else f"The price is near its 30-day high ({plain_money(hi)}) after dipping to {plain_money(lo)}; if you are not in a hurry, watch it for a while."))
        else:
            s.append((f"تراوح السعر بين {money(lo, 'ar')} و{money(hi, 'ar')} خلال 30 يوماً، والسعر الحالي في منتصف هذا النطاق." if ar
                      else f"The price ranged between {plain_money(lo)} and {plain_money(hi)} over 30 days, and today sits mid-range."))
    elif len(p.get("series") or []) < 3:
        s.append(_pick(pid, "hist", ["بدأنا تتبع سعر هذا المنتج حديثاً، فلا يتوفر بعد نطاق 30 يوماً للمقارنة؛ سنعرضه هنا حين يكتمل.",
                                     "تاريخ سعر هذا المنتج قصير حتى الآن، وسيظهر نطاق 30 يوماً هنا مع استمرار التتبع اليومي."]) if ar else
                 _pick(pid, "hist", ["We only started tracking this product recently, so there is no 30-day range yet; it will appear here as tracking continues.",
                                     "This product's price history is still short, and the 30-day range will show here as daily tracking continues."]))
    if len(offs) >= 2:
        hi_o = max(offs, key=lambda o: o["price"])
        gap = hi_o["price"] - b["price"]
        if gap >= max(50, b["price"] * 0.05):
            s.append((f"الفارق بين أرخص وأغلى متجر {money(gap, 'ar')}، وهو مبلغ يستحق مقارنة المتاجر قبل الشراء." if ar
                      else f"The gap between cheapest and priciest store is {plain_money(gap)}, which is worth comparing before you buy."))
    return " ".join(s)


def alternatives(p, items, lang, limit=3):
    """Cheaper options in the same category with a similar size/capacity, and one step up. Returns [(item, reason)]."""
    cat = p["category"]
    key = "capacity" if cat in ("acs", "fridges", "washers", "microwaves", "ovens") else ("size" if cat == "tvs" else ("storage" if cat in ("phones", "laptops") else "none"))
    base = _num((p.get("specs") or {}).get(key))
    price = p["best"]["price"]
    ar = lang == "ar"

    def close(i):
        v = _num((i.get("specs") or {}).get(key))
        if base is None or v is None:
            return True
        return abs(v - base) <= 0.25 * base

    pool = [i for i in items if i["category"] == cat and i["id"] != p["id"] and i["best"]["price"] > 0]
    cheaper = sorted((i for i in pool if i["best"]["price"] <= price * 0.9 and close(i)),
                     key=lambda i: ((i.get("specs") or {}).get("type") != (p.get("specs") or {}).get("type"), i["brand"] != p["brand"], -i["best"]["price"]))[:limit]
    out = []
    for i in cheaper:
        d = price - i["best"]["price"]
        out.append((i, (f"أرخص بنحو {int(round(d))} ر.س" if ar else f"about SAR {int(round(d))} cheaper")))
    up = sorted((i for i in pool if price * 1.1 <= i["best"]["price"] <= price * 1.6 and i["brand"] == p["brand"] and close(i)),
                key=lambda i: i["best"]["price"])[:1]
    for i in up:
        out.append((i, ("خيار أعلى من نفس الماركة" if ar else "a step up from the same brand")))
    return out


def advice(p, items, lang, money, plain_money):
    pros, cons, good, notgood = spec_notes(p, lang)
    return dict(verdict=verdict(p, lang, money, plain_money), pros=pros, cons=cons, good=good, notgood=notgood,
                alts=alternatives(p, items, lang))
