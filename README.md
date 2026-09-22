# Nabta — كاتالوج النباتات / Plant Catalog

كاتالوج منسّق للنباتات الاستوائية والنادرة، مبني آليًا من ملف Excel الأصلي.

A formatted catalog of tropical and rare houseplants, generated automatically from the original Excel price list.

## المحتويات / Contents

| المسار | الوصف |
|---|---|
| `catalog/Plant_Catalog_2026.pdf` | الكاتالوج النهائي (52 صفحة، 289 صنفًا، 29 جنسًا) مع الصور والأسعار بالدولار والجنيه |
| `catalog/Plant_Catalog_2026.xlsx` | قائمة أسعار مرتبة أبجديًا بحسب الجنس، مع فلترة وتنسيق للعملتين |
| `source/Book1-version-1.xlsx` | الملف الأصلي كما تم تسليمه |
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
python scripts/build_catalog.py  # توليد الكاتالوج
```

السكربت يقرأ `scripts/data.json` والصور المستخرجة، ويُنتج ملف PDF في مجلد العمل.

## ملاحظات / Notes

- سعر التحويل المستخدم: 1 دولار = 52 جنيه مصري.
- 286 صورة تم استخراجها من الصور المضمّنة داخل خلايا Excel (in-cell images).
- تم تصحيح 121 اسمًا: توحيد الأجناس (Philodendron، Scindapsus، Syngonium، Aglaonema)، تصحيح الأخطاء الإملائية، ووضع أسماء الأصناف بين علامتي تنصيص.
- الأصناف التي كانت أسعارها مرتبطة بملف خارجي غير متوفر تظهر باسم "on request".
