# Nabta — كاتالوج النباتات / Plant Catalog

كاتالوج منسّق للنباتات الاستوائية والنادرة، مبني آليًا من ملف Excel الأصلي.

A formatted catalog of tropical and rare houseplants, generated automatically from the original Excel price list.

## المحتويات / Contents

| المسار | الوصف |
|---|---|
| `catalog/Plant_Catalog_2026.pdf` | الكاتالوج النهائي (52 صفحة، 289 صنفًا، 29 جنسًا) مع الصور والأسعار بالدولار والجنيه |
| `catalog/Plant_Catalog_2026.xlsx` | قائمة أسعار مرتبة أبجديًا بحسب الجنس، مع فلترة وتنسيق للعملتين |
| `source/Book1-version-1.xlsx` | الملف الأصلي كما تم تسليمه |
| `source/The-Plants-Price-22.pdf` | قائمة الأسعار الإضافية (إصدار 22) |
| `scripts/merge_v22.py` | دمج قائمة 22: تعبئة الأسعار الناقصة واستخراج الأصناف الجديدة |
| `scripts/additions_v22.json` | 167 صنفًا إضافيًا مع نطاق السعر وربط الصور |
| `photos/v22/` | 240 صورة مستخرجة من قائمة 22 بدقتها الأصلية |
| `scripts/v22_imgmap.json` | ربط كل صنف باسم ملف صورته |
| `scripts/pricelist.json` | الصفوف المستخرجة من ملف PDF لقائمة 22 |
| `scripts/build_catalog.py` | سكربت توليد الكاتالوج (reportlab + Pillow) |
| `scripts/data.json` | البيانات المستخرجة من الملف الأصلي |
| `scripts/data_clean.json` | البيانات بعد تحسين أسماء النباتات والأجناس |
| `scripts/clean_names.py` | سكربت تصحيح الأسماء (اختصارات، أخطاء إملائية، تنسيق الأصناف) |
| `docs/name_changes.md` | سجل كامل بكل اسم تم تصحيحه (قبل/بعد) |
| `scripts/imgmap.json` | خريطة الصور المضمّنة داخل الخلايا إلى صفوفها |

## التشغيل / Usage

```bash
pip install reportlab pillow openpyxl arabic_reshaper python-bidi
python scripts/clean_names.py   # تصحيح الأسماء
python scripts/merge_v22.py     # دمج قائمة الأسعار 22
python scripts/build_catalog.py  # توليد الكاتالوج
```

السكربت يقرأ `scripts/data.json` والصور المستخرجة، ويُنتج ملف PDF في مجلد العمل.

## ملاحظات / Notes

- سعر التحويل المستخدم: 1 دولار = 52 جنيه مصري.
- أُضيف قسم "New Varieties" المصوّر (159 صنفًا ببطاقات وصور) وقسم جدولي "Additional Varieties - Price List v22" يشمل 167 صنفًا من قائمة 22 غير موجودة في الكاتالوج المصوّر، والسعر يظهر كنطاق عند تعدد المقاسات.
- 286 صورة تم استخراجها من الصور المضمّنة داخل خلايا Excel (in-cell images).
- تمت مراجعة الأسماء الغامضة: صُنّفت أصناف الهجن (Michelle، Zara Michelle، Papi، Docblok، Dorayaki، Red Tiger) تحت Anthurium، و(Gigas، Paraiso Verde، Pink Princess، Burle Marx) تحت Philodendron، و(Silver Dragon، Golden Bone) تحت Alocasia، وبقيت 5 مدخلات فقط غير محددة.
- تم تصحيح 121 اسمًا: توحيد الأجناس (Philodendron، Scindapsus، Syngonium، Aglaonema)، تصحيح الأخطاء الإملائية، ووضع أسماء الأصناف بين علامتي تنصيص.
- الأصناف التي كانت أسعارها مرتبطة بملف خارجي غير متوفر تظهر باسم "on request".


## إضافة صورك الخاصة / Adding your own photos

1. سمِّ كل صورة باسم الصنف كما في الكاتالوج، مثل `Alocasia venom.jpg` أو `anthurium_carla_x_bvep.png`.
2. ضع الصور في `user_photos/` أو في مجلد على Google Drive.
3. شغّل:

```bash
python3 scripts/merge_v22.py
python3 scripts/add_user_photos.py user_photos/        # أو: --drive <folderId>
python3 scripts/build_catalog.py
```

- صورك تحل محل صور قائمة 22 والصور المرجعية من ويكيميديا.
- الأسماء العامة (`WhatsApp Image ...`، `photo_2026-...`، `IMG_1234`) تُتجاهل حتى لا تُربط صورة بصنف خاطئ.
- الملفات غير المطابقة أو التي تطابق أكثر من صنف تُسجَّل في `user_photos_log.json` ولا تُضاف.

الأصناف التي ما زالت بلا صورة: Alocasia venom، Philodendron 'Green Congo' variegata، Anthurium Carla x Bvep، Anthurium michelle x Zara michelle.
