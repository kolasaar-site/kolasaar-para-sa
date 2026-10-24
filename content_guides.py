"""Hand-written buying guides, one per category and language. Plain facts, no invented test results.
Shown on the first page of each category and linked from every product page (the 'how to choose' part of a buying guide)."""

GUIDES = {
    "acs": {
        "ar": {
            "title": "دليل شراء المكيف: كيف تختار السعة والنوع المناسبين؟",
            "sections": [
                ("كم BTU تحتاج غرفتك؟",
                 "السعة تُقاس بالوحدة الحرارية BTU. كقاعدة تقريبية: 12,000 BTU (طن واحد) لغرفة حتى نحو 15 متراً مربعاً، و18,000 BTU لغرفة بين 20 و28 متراً، و24,000 BTU لصالة بين 30 و40 متراً، وما فوق ذلك لمساحات أكبر. في صيف السعودية يُفضَّل أن تختار السعة الأعلى عند التردد بين حجمين، "
                 "خاصة إذا كانت الغرفة تتعرض للشمس أو تحتها سطح مكشوف، لأن المكيف الأصغر من اللازم سيعمل بلا توقف ويستهلك أكثر."),
                ("إنفرتر أم عادي؟",
                 "مكيف الإنفرتر يغيّر سرعة الضاغط بدل التشغيل والإيقاف الكامل، فيستهلك كهرباء أقل عادة ويحافظ على حرارة أكثر ثباتاً وصوتاً أهدأ. سعره الابتدائي أعلى، لكن مع التشغيل الطويل في الصيف يعوّض الفرق غالباً خلال موسمين أو ثلاثة. "
                 "إن كان استخدامك قليلاً (غرفة ضيوف مثلاً) فالمكيف العادي خيار اقتصادي معقول."),
                ("بارد فقط أم بارد وحار؟",
                 "الموديلات بارد فقط أرخص وتكفي معظم مناطق المملكة. اختر بارد وحار إذا كنت في منطقة تنخفض فيها الحرارة شتاءً (الشمال والمرتفعات) وتريد تدفئة اقتصادية بدل المدفأة الكهربائية."),
                ("سبليت أم شباك؟",
                 "السبليت أهدأ وأكفأ ويوزّع الهواء بشكل أفضل، لكنه يحتاج تركيباً ومواسير نحاسية. مكيف الشباك أرخص وأسهل تركيباً لكنه أعلى صوتاً. المكيف المتنقل حل مؤقت للمستأجر ولا يُنصح به كمصدر تبريد رئيسي."),
                ("لا تنسَ تكلفة التركيب والضمان",
                 "اسأل عن تكلفة التركيب والمواسير الإضافية قبل المقارنة، فقد تتجاوز فارق السعر بين متجرين. وتحقق من مدة ضمان الضاغط تحديداً لأنه أغلى قطعة في المكيف."),
            ],
        },
        "en": {
            "title": "Air conditioner buying guide: how to pick the right size and type",
            "sections": [
                ("How many BTU does your room need?",
                 "Capacity is measured in BTU. As a rough guide: 12,000 BTU (1 ton) for a room up to about 15 m², 18,000 BTU for 20-28 m², 24,000 BTU for a 30-40 m² living room, and more for larger spaces. In a Saudi summer, go one size up when in doubt, "
                 "especially for sun-facing rooms or rooms under an uninsulated roof: an undersized unit runs non-stop and costs more to run."),
                ("Inverter or non-inverter?",
                 "An inverter compressor changes speed instead of switching fully on and off, so it usually uses less electricity, holds a steadier temperature and is quieter. It costs more up front, but with long summer use the difference is often recovered within two or three seasons. "
                 "For occasional use (a guest room) a standard unit is a fair budget choice."),
                ("Cold-only or hot & cold?",
                 "Cold-only models are cheaper and enough for most of the Kingdom. Pick hot & cold if winters get cold where you live (the north, the highlands) and you want efficient heating instead of electric heaters."),
                ("Split or window?",
                 "A split unit is quieter, more efficient and spreads air better, but needs installation and copper piping. A window unit is cheaper and simpler to fit but louder. A portable unit is a stop-gap for renters, not a main cooling source."),
                ("Installation and warranty",
                 "Ask about installation and extra piping before comparing prices: it can exceed the price gap between two stores. Check the compressor warranty in particular, since it is the most expensive part."),
            ],
        },
    },
    "fridges": {
        "ar": {
            "title": "دليل شراء الثلاجة: السعة والنوع وما يناسب أسرتك",
            "sections": [
                ("ما السعة المناسبة؟",
                 "للفرد أو الفردين تكفي ثلاجة بين 200 و300 لتر. للأسرة من 3 إلى 4 أفراد اختر بين 350 و450 لتراً. وللأسر الأكبر أو من يتسوق أسبوعياً بكميات كبيرة، 500 لتر فأكثر. الأرقام المكتوبة بالقدم المكعب: كل قدم مكعب يساوي نحو 28 لتراً."),
                ("أي نوع تختار؟",
                 "الفريزر العلوي هو الأرخص والأبسط. الفريزر السفلي يضع الأكثر استخداماً (الثلاجة) على مستوى العين. الجنب إلى جنب (Side by Side) وأبواب الفرنسية أوسع وأغلى وتحتاج مساحة مطبخ وعرض باب مناسباً، فقس مدخل المطبخ قبل الشراء."),
                ("نو فروست وكفاءة الطاقة",
                 "النظام No Frost يمنع تكوّن الثلج فلا تحتاج لإزالته يدوياً، وهو أنسب للاستخدام اليومي. ضاغط الإنفرتر أهدأ وأقل استهلاكاً. ابحث عن تصنيف مناخي T المخصص للأجواء الحارة، لأنه مصمم للعمل في حرارة محيط مرتفعة كما في الصيف عندنا."),
                ("الفريزر المنفصل",
                 "إن كنت تخزّن لحوماً بكميات كبيرة فالفريزر الصندوقي أو العمودي المنفصل أوفر من شراء ثلاجة ضخمة، ويُبقي ثلاجتك الرئيسية أصغر وأقل استهلاكاً."),
            ],
        },
        "en": {
            "title": "Refrigerator buying guide: capacity, type and what suits your household",
            "sections": [
                ("What capacity do you need?",
                 "One or two people: 200-300 litres. A household of 3-4: 350-450 litres. Larger families, or anyone who does big weekly shops: 500 litres or more. When capacity is given in cubic feet, one cubic foot is about 28 litres."),
                ("Which type?",
                 "Top freezer is the cheapest and simplest. Bottom freezer puts the part you use most at eye level. Side-by-side and French-door models are roomier and pricier and need kitchen space and a wide enough doorway, so measure your kitchen entrance first."),
                ("No Frost and energy use",
                 "No Frost prevents ice build-up so you never defrost by hand, which suits daily use. An inverter compressor is quieter and uses less power. Look for climate class T, built for hot ambient temperatures like a Saudi summer."),
                ("A separate freezer",
                 "If you store a lot of meat, a separate chest or upright freezer is cheaper than buying a huge fridge, and keeps your main fridge smaller and cheaper to run."),
            ],
        },
    },
    "washers": {
        "ar": {
            "title": "دليل شراء الغسالة: السعة وأنواع التحميل",
            "sections": [
                ("كم كيلوجرام تحتاج؟",
                 "للفرد أو الفردين 5 إلى 7 كجم، لأسرة من 3 إلى 4 أفراد 8 إلى 9 كجم، ولأسرة كبيرة (5 فأكثر) 10 كجم فأكثر. الغسالة الأكبر قليلاً من حاجتك أفضل لأن ملء الأسطوانة بالكامل يضر بالغسيل ويُجهد المحرك."),
                ("تحميل أمامي أم علوي؟",
                 "الأمامي أرفق بالملابس ويستهلك ماءً وكهرباءً أقل ويعصر بقوة أكبر، لكنه أغلى وبرنامجه أطول ويحتاج ضغط ماء جيداً. العلوي أرخص وأسرع ويمكن إضافة الملابس أثناء الغسيل، لكنه يستهلك ماءً أكثر. التوأم (Twin Tub) الأرخص على الإطلاق لكنه يحتاج تدخلاً يدوياً بنقل الغسيل بين الحوضين."),
                ("سرعة العصر والمحرك",
                 "سرعة العصر 1000 إلى 1400 لفة في الدقيقة تكفي لمعظم الاستخدامات، فالأعلى يجفف الغسيل أكثر لكنه يزيد الاهتزاز. المحرك الإنفرتر (الدفع المباشر) أهدأ وأطول عمراً وأقل استهلاكاً."),
                ("غسالة بتجفيف",
                 "الغسالة المدمجة بمجفف توفر المساحة لكنها تجفف كمية أقل مما تغسل. في السعودية حيث الجفاف طبيعي معظم السنة، قد لا تحتاج هذه الميزة."),
            ],
        },
        "en": {
            "title": "Washing machine buying guide: capacity and load types",
            "sections": [
                ("How many kilograms?",
                 "1-2 people: 5-7 kg. A household of 3-4: 8-9 kg. A large family (5+): 10 kg or more. Buy slightly above your need: packing the drum to the limit is hard on both clothes and motor."),
                ("Front load or top load?",
                 "Front load is gentler on clothes, uses less water and power and spins harder, but costs more, runs longer cycles and needs good water pressure. Top load is cheaper and faster and lets you add clothes mid-cycle, but uses more water. Twin tub is the cheapest of all but needs you to move washing between tubs by hand."),
                ("Spin speed and motor",
                 "1,000-1,400 rpm is enough for most households; higher dries clothes more but adds vibration. An inverter direct-drive motor is quieter, lasts longer and uses less power."),
                ("Washer-dryer combos",
                 "A combo saves space but dries a smaller load than it washes. Where air-drying works most of the year, as in much of Saudi Arabia, you may not need it."),
            ],
        },
    },
    "microwaves": {
        "ar": {
            "title": "دليل شراء الميكروويف",
            "sections": [
                ("السعة والقدرة",
                 "20 لتراً تكفي فرداً أو فردين، و25 إلى 30 لتراً تناسب الأسرة، وما فوق 30 لتراً لمن يطبخ أطباقاً كبيرة. القدرة بين 700 و1000 واط؛ الأعلى يسخّن أسرع."),
                ("عادي أم شواء أم حراري؟",
                 "النوع العادي (Solo) للتسخين والتذويب فقط وهو الأرخص. نوع الشواء يضيف مقلاة علوية لتحمير الوجه. الحراري (Convection) يعمل كفرن صغير ويخبز، وهو الأغلى. إن كنت تحتاج التسخين فقط فلا تدفع ثمن ما لا تستخدمه."),
                ("أمان واستخدام",
                 "تجنّب وضع الأواني المعدنية في النوع العادي، واختر أطباقاً مخصصة للميكروويف. تحقق من قفل الأطفال إن كان في المنزل صغار."),
            ],
        },
        "en": {
            "title": "Microwave buying guide",
            "sections": [
                ("Capacity and power",
                 "20 litres suits one or two people, 25-30 litres a family, and over 30 litres anyone cooking larger dishes. Power runs 700-1,000 W; higher heats faster."),
                ("Solo, grill or convection?",
                 "Solo only reheats and defrosts and is cheapest. Grill adds a top element to brown food. Convection works as a small oven and can bake, at the highest price. If you only reheat, do not pay for features you will not use."),
                ("Safety and use",
                 "Do not put metal in a solo microwave and use microwave-safe dishes. Check for a child lock if you have young children."),
            ],
        },
    },
    "ovens": {
        "ar": {
            "title": "دليل شراء الفرن",
            "sections": [
                ("مدمج أم قائم بذاته؟",
                 "الفرن المدمج (Built-in) يُركَّب داخل خزانة المطبخ بأبعاد قياسية عرضها نحو 60 سم، ويعطي شكلاً متناسقاً لكنه يحتاج فتحة مناسبة في التصميم. القائم بذاته (Cooker) أسهل ويُركَّب بلا تجهيز، وغالباً يضم الموقد."),
                ("غاز أم كهرباء؟",
                 "الغاز أسرع تسخيناً وأرخص تشغيلاً حيث يتوفر، والكهربائي أدق في ثبات الحرارة ويناسب الخبز والحلويات. تأكد أن مطبخك مجهز بتمديد كهرباء قوي إن اخترت الكهربائي."),
                ("المروحة والسعة",
                 "فرن بمروحة يوزّع الحرارة بالتساوي فيخبز أكثر من صينية في وقت واحد. السعة من 60 إلى 80 لتراً تكفي معظم الأسر."),
            ],
        },
        "en": {
            "title": "Oven buying guide",
            "sections": [
                ("Built-in or freestanding?",
                 "A built-in oven fits into a kitchen cabinet at a standard width of about 60 cm for a neat look, but needs a suitable cut-out. A freestanding cooker needs no prep and usually includes the hob."),
                ("Gas or electric?",
                 "Gas heats quicker and is cheaper to run where available; electric holds temperature more steadily and suits baking. Make sure your kitchen has a strong enough electrical supply if you choose electric."),
                ("Fan and capacity",
                 "A fan oven spreads heat evenly so you can bake several trays at once. 60-80 litres is enough for most households."),
            ],
        },
    },
    "tvs": {
        "ar": {
            "title": "دليل شراء التلفزيون: الحجم والشاشة والنظام",
            "sections": [
                ("ما الحجم المناسب لغرفتك؟",
                 "قاعدة مفيدة: المسافة المثالية للمشاهدة بدقة 4K تساوي تقريباً من مرة ونصف إلى مرتين ونصف قطر الشاشة. فعلى مسافة 2.5 متر تناسبك شاشة 55 بوصة، وعلى 3 أمتار 65 بوصة، ولصالة كبيرة 75 بوصة فأكثر."),
                ("LED أم QLED أم OLED؟",
                 "LED العادي هو الأرخص وكافٍ لغرف الإضاءة القوية. QLED يعطي ألواناً وسطوعاً أعلى. OLED يعطي أسود حقيقياً وتبايناً ممتازاً لغرف الإضاءة الخافتة، لكنه أغلى وأقل سطوعاً في الغرف المشمسة."),
                ("معدل التحديث وأجهزة الألعاب",
                 "معدل 60 هرتز يكفي للمشاهدة. إن كنت تلعب على PS5 أو Xbox Series X فابحث عن 120 هرتز ومنفذ HDMI 2.1 لتستفيد من 4K بسلاسة."),
                ("النظام الذكي",
                 "تختلف الأنظمة: Google TV وTizen (سامسونج) وwebOS (إل جي). تأكد من توفر تطبيقاتك المفضلة، ومن أن الجهاز نسخة تدعم السوق السعودي وبضمان محلي."),
            ],
        },
        "en": {
            "title": "TV buying guide: size, panel and smart platform",
            "sections": [
                ("What size for your room?",
                 "A useful rule: the ideal 4K viewing distance is roughly 1.5 to 2.5 times the screen diagonal. At 2.5 m, a 55-inch suits; at 3 m, 65 inches; for a big living room, 75 inches and up."),
                ("LED, QLED or OLED?",
                 "Standard LED is cheapest and fine for bright rooms. QLED adds colour and brightness. OLED gives true blacks and excellent contrast for dim rooms, but costs more and is less bright in sunny rooms."),
                ("Refresh rate and gaming",
                 "60 Hz is enough for watching. If you game on a PS5 or Xbox Series X, look for 120 Hz and HDMI 2.1 to get 4K smoothly."),
                ("Smart platform",
                 "Platforms differ: Google TV, Tizen (Samsung), webOS (LG). Check your apps are available, and that the unit is the Saudi-market version with a local warranty."),
            ],
        },
    },
    "phones": {
        "ar": {
            "title": "دليل شراء الجوال: السعة والنسخة والضمان",
            "sections": [
                ("كم سعة التخزين؟",
                 "128 جيجا هو الحد الأدنى المعقول اليوم لمن يصوّر ويحمّل تطبيقات. 256 جيجا أفضل إن كنت تصوّر فيديو كثيراً. السعة لا تُوسَّع في أغلب الجوالات الحديثة، فاشترِ ما يكفيك لسنوات."),
                ("الذاكرة العشوائية والمعالج",
                 "8 جيجا ذاكرة مريحة للاستخدام اليومي ومتعدد المهام، و12 جيجا فأكثر للألعاب الثقيلة. المعالج يحدد السلاسة أكثر من أي رقم آخر، فقارن فئة المعالج وليس الذاكرة وحدها."),
                ("نسخة محلية أم دولية؟",
                 "كثير من المتاجر الإلكترونية تعرض نسخاً دولية بسعر أقل. الفرق أن الضمان قد يكون من البائع لا من الوكيل المحلي، وقد تختلف حزمة الشبكات أو الشاحن. اقرأ شروط الضمان واسأل عن الوكيل قبل الاختيار."),
                ("5G والبطارية",
                 "إن كنت ضمن تغطية 5G فاختر موديلاً يدعمه ليبقى مفيداً لسنوات. وانظر إلى سعة البطارية وسرعة الشحن، فهما أهم لليوم الفعلي من كثير من المواصفات اللامعة."),
            ],
        },
        "en": {
            "title": "Phone buying guide: storage, version and warranty",
            "sections": [
                ("How much storage?",
                 "128 GB is a sensible minimum today if you shoot photos and install apps. 256 GB is better if you film a lot of video. Most modern phones cannot expand storage, so buy enough for years."),
                ("RAM and chipset",
                 "8 GB RAM is comfortable for daily use and multitasking, 12 GB or more for heavy gaming. The chipset decides smoothness more than any single number, so compare chip tier, not RAM alone."),
                ("Local or international version?",
                 "Many online stores list international versions at a lower price. The catch: the warranty may come from the seller rather than the local distributor, and network bands or the charger can differ. Read the warranty terms and ask who services it."),
                ("5G and battery",
                 "If you are in 5G coverage, choose a model that supports it so it stays useful for years. And check battery size and charging speed, which matter more for your real day than many flashy specs."),
            ],
        },
    },
    "laptops": {
        "ar": {
            "title": "دليل شراء اللابتوب والتابلت",
            "sections": [
                ("حدّد استخدامك أولاً",
                 "للدراسة والمكتب يكفي معالج متوسط (Core i5 أو Ryzen 5) مع 16 جيجا ذاكرة. للتصميم والمونتاج والألعاب تحتاج بطاقة رسوميات مخصصة وذاكرة 16 إلى 32 جيجا. للتصفح والبريد فقط يكفي جهاز أخف وأرخص."),
                ("الذاكرة والتخزين",
                 "تجنّب 8 جيجا ذاكرة إن أمكن لأنها تضيق بسرعة مع المتصفح وبرامج متعددة. التخزين SSD إلزامي عملياً، و512 جيجا أفضل نقطة بين السعر والمساحة."),
                ("الشاشة والبطارية",
                 "ابحث عن شاشة بدقة Full HD على الأقل ونسبة سطوع جيدة. للتنقل الكثير اختر جهازاً بوزن أقل من 1.6 كجم وبطارية تكفي يوم عمل. والتابلت يناسب المحتوى والقراءة؛ إن احتجت كتابة طويلة فأضف لوحة مفاتيح."),
            ],
        },
        "en": {
            "title": "Laptop and tablet buying guide",
            "sections": [
                ("Decide how you will use it",
                 "For study and office work a mid-range chip (Core i5 or Ryzen 5) with 16 GB RAM is plenty. For design, editing and gaming you need a dedicated graphics card and 16-32 GB RAM. For browsing and email only, a lighter, cheaper machine will do."),
                ("RAM and storage",
                 "Avoid 8 GB RAM if you can: it fills quickly with a browser and several apps. An SSD is effectively mandatory, and 512 GB is the best balance of price and space."),
                ("Screen and battery",
                 "Look for at least Full HD and decent brightness. If you travel a lot, pick something under 1.6 kg with a battery that lasts a working day. A tablet suits media and reading; add a keyboard for long typing."),
            ],
        },
    },
}

GUIDES["watches"] = {
    "ar": {
        "title": "دليل شراء الساعة الذكية",
        "sections": [
            ("اختر حسب هاتفك أولاً",
             "ساعة آبل تعمل مع آيفون فقط، وساعات سامسونج تعطي أفضل تجربة مع هواتف أندرويد وخصوصاً سامسونج. أما هواوي وغارمن فتعملان مع أندرويد وآيفون لكن بعض الميزات تقل. اختيار ساعة لا تناسب هاتفك هو أشيع سبب لندم المشتري."),
            ("المقاس: 40 أم 44؟",
             "قِس معصمك قبل الشراء. المقاس الأصغر (نحو 40-42 ملم) أنسب للمعصم النحيف، والأكبر (45 ملم فأكثر) أسهل قراءة وبطاريته أكبر قليلاً. المقاس الواحد من الموديل نفسه يأتي بسعر مختلف، لذلك نعرض كل مقاس كمنتج مستقل."),
            ("GPS أم خلوي (Cellular)؟",
             "نسخة GPS أو البلوتوث تحتاج هاتفك قريباً لتلقي المكالمات والرسائل. النسخة الخلوية تعمل بشريحة eSIM مستقلة لكنها أغلى وتحتاج باقة مدفوعة من شركة الاتصالات. اختر الخلوية فقط إن كنت تريد الخروج للرياضة دون الهاتف."),
            ("البطارية",
             "أغلب الساعات الذكية تحتاج شحناً كل يوم إلى يومين، بينما تمتد ساعات الرياضة (مثل غارمن) وبعض ساعات هواوي إلى أيام طويلة. إن كان الشحن اليومي يزعجك فاختر ساعة بعمر بطارية أطول."),
        ],
    },
    "en": {
        "title": "Smartwatch buying guide",
        "sections": [
            ("Start with your phone",
             "An Apple Watch works only with an iPhone, and Samsung's watches give the best experience with Android phones, Samsung in particular. Huawei and Garmin work with both Android and iPhone, with some features reduced. Buying a watch that does not suit your phone is the most common reason for regret."),
            ("Case size: 40 or 44?",
             "Measure your wrist before buying. The smaller size (about 40-42 mm) suits slim wrists; the larger (45 mm and up) is easier to read and has a slightly bigger battery. The same model in a different size is priced differently, so we list each size as its own product."),
            ("GPS or cellular?",
             "GPS or Bluetooth versions need your phone nearby for calls and messages. Cellular versions use their own eSIM but cost more and need a paid plan from your carrier. Choose cellular only if you want to leave the phone at home when exercising."),
            ("Battery",
             "Most smartwatches need charging every one to two days, while sports watches (such as Garmin) and some Huawei models last many days. If daily charging annoys you, pick a longer-lasting watch."),
        ],
    },
}
GUIDES["earbuds"] = {
    "ar": {
        "title": "دليل شراء السماعات اللاسلكية",
        "sections": [
            ("داخل الأذن أم فوق الأذن؟",
             "سماعات الأذن الصغيرة (True Wireless) أخف وأسهل في الحمل وتناسب الرياضة والمواصلات. سماعات الرأس تعطي عادةً راحة أطول وبطارية أكبر وصوتاً أعمق للمستخدم الذي يجلس لساعات."),
            ("العزل الضوضائي النشط (ANC)",
             "يخفّف ضجيج المواصلات والمكيفات والمكاتب المفتوحة، وهو مفيد جداً لمن يسافر كثيراً. لكن بعض الناس لا يرتاحون لإحساس الضغط في الأذن، وهو يرفع السعر. إن كنت تستخدمها في البيت غالباً فقد لا تحتاجه."),
            ("التوافق مع هاتفك",
             "AirPods تعطيك أفضل تجربة مع آيفون، وGalaxy Buds مع هواتف سامسونج، وكلاهما يعمل كبلوتوث عادي مع غيره بميزات أقل. سوني وجي بي إل وأنكر تعمل جيداً مع أي هاتف عبر تطبيق الشركة."),
            ("المقاس والبطارية",
             "جرّب أطراف الأذن الصحيحة لأن الإحكام يغيّر جودة الصوت والعزل. وتحقق من عمر البطارية للسماعة نفسها ومع علبة الشحن، فهو يختلف كثيراً بين الموديلات."),
        ],
    },
    "en": {
        "title": "Wireless earbuds and headphones buying guide",
        "sections": [
            ("In-ear or over-ear?",
             "True wireless earbuds are lighter, easier to carry and suit exercise and commuting. Over-ear headphones are usually more comfortable for long sessions, with bigger batteries and deeper sound for people who sit for hours."),
            ("Active noise cancelling (ANC)",
             "It reduces commute, air-conditioner and open-office noise, which is very useful if you travel. Some people dislike the pressure feeling in the ear, and it raises the price. If you mostly listen at home you may not need it."),
            ("Compatibility with your phone",
             "AirPods give the best experience with iPhone and Galaxy Buds with Samsung phones; both work as plain Bluetooth with other phones, with fewer features. Sony, JBL and Anker work well with any phone through the maker's app."),
            ("Fit and battery",
             "Try the right ear tips, because a good seal changes sound quality and noise isolation. Check battery life for the earbuds alone and with the charging case, as it varies a lot between models."),
        ],
    },
}
GUIDES["consoles"] = {
    "ar": {
        "title": "دليل شراء جهاز الألعاب",
        "sections": [
            ("اختر المنصة حسب الألعاب التي تريدها",
             "ألعاب كل منصة حصرية في الغالب: بلايستيشن لألعاب سوني الفردية، وإكس بوكس لألعاب مايكروسوفت وخدمة Game Pass، ونينتندو سويتش لألعاب العائلة والتنقل. حدّد ألعابك المفضلة قبل مقارنة الأسعار."),
            ("نسخة الأقراص أم الرقمية؟",
             "النسخة الرقمية أرخص لكنها لا تشغّل الأقراص، فتشتري الألعاب من المتجر الإلكتروني فقط ولا يمكنك إعادة بيعها أو استعارتها. نسخة الأقراص أغلى وأكثر مرونة، خاصةً إن كنت تشتري ألعاباً مستعملة أو تتبادلها."),
            ("مساحة التخزين",
             "الألعاب الحديثة تتجاوز 50 جيجا وبعضها 100 جيجا، والمساحة المتاحة للمستخدم أقل من المكتوبة على العلبة. إن كنت تحمّل ألعاباً كثيرة فاختر السعة الأكبر أو خطّط لشراء وحدة تخزين إضافية."),
            ("انتبه للحزم والنسخ",
             "الأسعار تتغير كثيراً بين النسخة المجردة والحزمة التي تضم لعبة أو يدّ إضافية. نعرض هنا النسخ المجردة فقط حتى تكون المقارنة عادلة، فتحقق مما تتضمنه صفحة المتجر."),
        ],
    },
    "en": {
        "title": "Game console buying guide",
        "sections": [
            ("Pick the platform by the games you want",
             "Most platforms keep their best games to themselves: PlayStation for Sony's single-player titles, Xbox for Microsoft's games and Game Pass, and Nintendo Switch for family and portable play. Decide on your favourite games before comparing prices."),
            ("Disc or digital?",
             "Digital editions are cheaper but cannot play discs, so you buy games only from the online store and cannot resell or lend them. Disc editions cost more and are more flexible, especially if you buy used games or swap them."),
            ("Storage",
             "Modern games run past 50 GB and some reach 100 GB, and the space available to you is less than the number on the box. If you install many games, choose the larger capacity or plan to buy extra storage."),
            ("Watch for bundles",
             "Prices vary widely between a bare console and a bundle that includes a game or a second controller. We list bare consoles only so the comparison is fair; check what the store page includes."),
        ],
    },
}
