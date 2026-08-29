import re
from typing import Optional, Dict, Tuple, List, Any
from app.core.database import get_db_client

# Canonical dictionary mapping all 114 Surahs and historical aliases
SURAH_DICT: Dict[str, int] = {
    # 1 - 10
    "فاتحة": 1, "حمد": 1, "ام الكتاب": 1, "سبع مثاني": 1,
    "بقرة": 2, "سنام القران": 2,
    "ال عمران": 3, "عمران": 3,
    "نساء": 4,
    "مائدة": 5, "عقود": 5,
    "انعام": 6,
    "اعراف": 7, "ميثاق": 7,
    "انفال": 8, "بدر": 8,
    "توبة": 9, "براءة": 9, "فاضحة": 9,
    "يونس": 10,
    # 11 - 20
    "هود": 11,
    "يوسف": 12,
    "رعد": 13,
    "ابراهيم": 14,
    "حجر": 15,
    "نحل": 16, "نعم": 16,
    "اسراء": 17, "بني اسرائيل": 17, "سبحان": 17,
    "كهف": 18,
    "مريم": 19,
    "طه": 20,
    # 21 - 30
    "انبياء": 21,
    "حج": 22,
    "مؤمنون": 23,
    "نور": 24,
    "فرقان": 25,
    "شعراء": 26,
    "نمل": 27,
    "قصص": 28,
    "عنكبوت": 29,
    "روم": 30,
    # 31 - 40
    "لقمان": 31,
    "سجدة": 32, "مضاجع": 32,
    "احزاب": 33,
    "سبا": 34,
    "فاطر": 35, "ملائكة": 35,
    "يس": 36, "ياسين": 36,
    "صافات": 37,
    "ص": 38, "صاد": 38,
    "زمر": 39, "غرف": 39,
    "غافر": 40, "مؤمن": 40, "طول": 40,
    # 41 - 50
    "فصلت": 41, "مصابيح": 41,
    "شورى": 42,
    "زخرف": 43,
    "دخان": 44,
    "جاثية": 45,
    "احقاف": 46,
    "محمد": 47, "قتال": 47,
    "فتح": 48,
    "حجرات": 49,
    "ق": 50, "قاف": 50,
    # 51 - 60
    "ذاريات": 51,
    "طور": 52,
    "نجم": 53,
    "قمر": 54, "اقتربت": 54,
    "رحمن": 55,
    "واقعة": 56,
    "حديد": 57,
    "مجادلة": 58,
    "حشر": 59,
    "ممتحنة": 60,
    # 61 - 70
    "صف": 61,
    "جمعة": 62,
    "منافقون": 63,
    "تغابن": 64,
    "طلاق": 65,
    "تحريم": 66,
    "ملك": 67, "تبارك": 67, "مانعة": 67,
    "قلم": 68, "ن": 68, "نون": 68,
    "حاقة": 69,
    "معارج": 70,
    # 71 - 80
    "نوح": 71,
    "جن": 72,
    "مزمل": 73,
    "مدثر": 74,
    "قيامة": 75,
    "انسان": 76, "دهر": 76,
    "مرسلات": 77,
    "نبا": 78, "عم": 78,
    "نازعات": 79,
    "عبس": 80,
    # 81 - 90
    "تكوير": 81,
    "انفطار": 82,
    "مطففين": 83,
    "انشقاق": 84,
    "بروج": 85,
    "طارق": 86,
    "اعلى": 87,
    "غاشية": 88,
    "فجر": 89,
    "بلد": 90,
    # 91 - 100
    "شمس": 91,
    "ليل": 92,
    "ضحى": 93,
    "شرح": 94, "انشراح": 94,
    "تين": 95,
    "علق": 96, "اقرا": 96,
    "قدر": 97,
    "بينة": 98, "لم يكن": 98,
    "زلزلة": 99,
    "عاديات": 100,
    # 101 - 114
    "قارعة": 101,
    "تكاثر": 102,
    "عصر": 103,
    "همزة": 104,
    "فيل": 105,
    "قريش": 106,
    "ماعون": 107,
    "كوثر": 108,
    "كافرون": 109,
    "نصر": 110,
    "مسد": 111, "لهب": 111, "تبت": 111,
    "اخلاص": 112, "توحيد": 112, "قل هو الله احد": 112,
    "فلق": 113,
    "ناس": 114,
}

SURAH_NAMES_AR = {
    1: "الفاتحة", 2: "البقرة", 3: "آل عمران", 4: "النساء", 5: "المائدة",
    6: "الأنعام", 7: "الأعراف", 8: "الأنفال", 9: "التوبة", 10: "يونس",
    11: "هود", 12: "يوسف", 13: "الرعد", 14: "إبراهيم", 15: "الحجر",
    16: "النحل", 17: "الإسراء", 18: "الكهف", 19: "مريم", 20: "طه",
    21: "الأنبياء", 22: "الحج", 23: "المؤمنون", 24: "النور", 25: "الفرقان",
    26: "الشعراء", 27: "النمل", 28: "القصص", 29: "العنكبوت", 30: "الروم",
    31: "لقمان", 32: "السجدة", 33: "الأحزاب", 34: "سبأ", 35: "فاطر",
    36: "يس", 37: "الصافات", 38: "ص", 39: "الزمر", 40: "غافر",
    41: "فصلت", 42: "الشورى", 43: "الزخرف", 44: "الدخان", 45: "الجاثية",
    46: "الأحقاف", 47: "محمد", 48: "الفتح", 49: "الحجرات", 50: "ق",
    51: "الذاريات", 52: "الطور", 53: "النجم", 54: "القمر", 55: "الرحمن",
    56: "الواقعة", 57: "الحديد", 58: "المجادلة", 59: "الحشر", 60: "الممتحنة",
    61: "الصف", 62: "الجمعة", 63: "المنافقون", 64: "التغابن", 65: "الطلاق",
    66: "التحريم", 67: "الملك", 68: "القلم", 69: "الحاقة", 70: "المعارج",
    71: "نوح", 72: "الجن", 73: "المزمل", 74: "المدثر", 75: "القيامة",
    76: "الإنسان", 77: "المرسلات", 78: "النبأ", 79: "النازعات", 80: "عبس",
    81: "التكوير", 82: "الانفطار", 83: "المطففين", 84: "الانشقاق", 85: "البروج",
    86: "الطارق", 87: "الأعلى", 88: "الغاشية", 89: "الفجر", 90: "البلد",
    91: "الشمس", 92: "الليل", 93: "الضحى", 94: "الشرح", 95: "التين",
    96: "العلق", 97: "القدر", 98: "البينة", 99: "الزلزلة", 100: "العاديات",
    101: "القارعة", 102: "التكاثر", 103: "العصر", 104: "الهمزة", 105: "الفيل",
    106: "قريش", 107: "الماعون", 108: "الكوثر", 109: "الكافرون", 110: "النصر",
    111: "المسد", 112: "الإخلاص", 113: "الفلق", 114: "الناس"
}

def normalize_arabic(text: str) -> str:
    """Normalizes Hamzahs, Alefs, and strips Tashkeel."""
    text = re.sub(r'[\u064B-\u065F\u0670]', '', text)
    text = re.sub(r'[إأآا]', 'ا', text)
    text = re.sub(r'[ة]', 'ه', text)
    text = re.sub(r'[ى]', 'ي', text)
    text = re.sub(r'^(سورة|سوره)\s+', '', text.strip())
    text = re.sub(r'^(ال)', '', text.strip())
    return text.strip()

# Pre-normalized lookup table
SURAH_NORMALIZED_DICT = {normalize_arabic(k): v for k, v in SURAH_DICT.items()}

def parse_scripture_citation(query: str) -> Optional[Dict[str, Any]]:
    """
    Parses a scripture citation from query string (e.g. 'البقرة: 275', '2:275', 'صحيح البخاري: 1').
    Returns matched citation metadata or None.
    """
    q = query.strip()
    
    # 1. Pattern: Surah:Ayah (e.g. '2:275', 'البقرة: 275', 'سورة البقرة: 275')
    ayah_match = re.match(r'^(?:سورة\s+)?([\u0621-\u064A0-9\s]+)[:\s\-\,]+(\d+)$', q)
    if ayah_match:
        surah_ref = ayah_match.group(1).strip()
        ayah_num = int(ayah_match.group(2))
        
        surah_num = None
        if surah_ref.isdigit():
            s_int = int(surah_ref)
            if 1 <= s_int <= 114:
                surah_num = s_int
        else:
            norm_name = normalize_arabic(surah_ref)
            surah_num = SURAH_NORMALIZED_DICT.get(norm_name)
        
        if surah_num and 1 <= surah_num <= 114 and ayah_num >= 1:
            canonical_name = SURAH_NAMES_AR.get(surah_num, f"سورة {surah_num}")
            return {
                "type": "ayah",
                "surah_num": surah_num,
                "ayah_num": ayah_num,
                "surah_name": canonical_name,
                "display_title": f"سورة {canonical_name} - الآية {ayah_num}",
                "search_expr": f"{canonical_name} {ayah_num}"
            }

    # 2. Pattern: Hadith Citation (e.g. 'صحيح البخاري: 1', 'حديث 1')
    hadith_match = re.match(r'^(?:حديث|رقم|صحيح\s+البخاري|البخاري)?\s*[:\#]?\s*(\d+)$', q)
    if hadith_match and not q.isdigit():
        h_num = int(hadith_match.group(1))
        if 1 <= h_num <= 7563:
            return {
                "type": "hadith",
                "hadith_num": h_num,
                "book_name": "صحيح البخاري",
                "display_title": f"صحيح البخاري - حديث رقم {h_num}",
                "search_expr": f"صحيح البخاري {h_num}"
            }

    return None

async def resolve_pinned_citation(citation: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Executes a direct fast lookup for the canonical primary source passage for the citation.
    """
    try:
        client = await get_db_client()
    except Exception:
        return None
    
    if citation["type"] == "ayah":
        surah_name = citation["surah_name"]
        ayah_num = citation["ayah_num"]
        
        # Look for Tafsir passage matching this Ayah or Surah
        res = await client.execute("""
            SELECT p.chunk_id, p.book_id, b.title_ar, b.author_name, p.volume_page,
                   p.section_title, p.breadcrumb, p.raw_text, p.footnotes
            FROM prepared_chunks p
            JOIN books b ON p.book_id = b.book_id
            WHERE b.category_name = 'التفسير'
              AND (p.section_title LIKE ? OR p.breadcrumb LIKE ? OR p.raw_text LIKE ?)
            ORDER BY b.author_death_hijri ASC
            LIMIT 1
        """, [f"%{surah_name}%", f"%{surah_name}%", f"%{surah_name}%"])
        
        if res.rows:
            r = res.rows[0]
            return {
                "citation": citation,
                "chunk_id": r[0],
                "book_id": r[1],
                "book_name": r[2],
                "author_name": r[3],
                "volume_page": r[4],
                "section_title": r[5],
                "breadcrumb": r[6],
                "raw_text": r[7],
                "footnotes": r[8],
            }

    elif citation["type"] == "hadith":
        h_num = citation["hadith_num"]
        res = await client.execute("""
            SELECT p.chunk_id, p.book_id, b.title_ar, b.author_name, p.volume_page,
                   p.section_title, p.breadcrumb, p.raw_text, p.footnotes
            FROM prepared_chunks p
            JOIN books b ON p.book_id = b.book_id
            WHERE b.title_ar LIKE '%صحيح البخاري%'
              AND (p.section_title LIKE ? OR p.raw_text LIKE ?)
            LIMIT 1
        """, [f"%{h_num}%", f"%حديث%{h_num}%"])
        
        if res.rows:
            r = res.rows[0]
            return {
                "citation": citation,
                "chunk_id": r[0],
                "book_id": r[1],
                "book_name": r[2],
                "author_name": r[3],
                "volume_page": r[4],
                "section_title": r[5],
                "breadcrumb": r[6],
                "raw_text": r[7],
                "footnotes": r[8],
            }

    return None
