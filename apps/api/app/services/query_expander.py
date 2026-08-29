import re
from typing import List, Tuple
from pipeline.stemmer import normalize_arabic, extract_composite_stems

ARABIC_STOPWORDS = {
    "انما", "في", "من", "عن", "على", "الى", "مع", "ما", "لا", "هو", "هي", "ان",
    "قد", "كان", "ثم", "او", "ام", "كل", "حتى", "اذا", "لو", "غير", "بين",
    "هذا", "هذه", "ذلك", "تلك", "هنا", "هناك", "الذي", "التي", "الذين", "اللاتي"
}

# Spurious 2-letter non-words caused by over-aggressive prefix stripping on 3-letter roots
SPURIOUS_STEMS = {"يع", "ني", "مر", "لم", "كم", "هم", "هن", "به", "له"}

def build_fts5_query(raw_query: str) -> str:
    """
    Constructs a hardened SQLite FTS5 query string using disjunctive lemma groupings
    with mandatory root intersections while filtering common classical particles
    and guarding against 2-letter root over-stripping.
    
    Example:
        Query: "شروط بيع السلم"
        Output: "salient_roots_text: (شروط OR شرط) AND (بيع) AND (السلم OR سلم)"
    """
    clean_query = normalize_arabic(raw_query)
    words = [w for w in clean_query.split() if len(w) >= 2 and w not in ARABIC_STOPWORDS]
    if not words:
        words = [w for w in clean_query.split() if len(w) >= 2]
        
    if not words:
        return ""

    grouped_expressions = []
    for word in words:
        variants = set()
        variants.add(word)
        
        # 1. Multi-letter prefix stripping: only if remaining stem is >= 3 chars
        for prefix in ("ال", "بال", "كال", "فال", "لل", "وال"):
            if word.startswith(prefix) and len(word) - len(prefix) >= 3:
                stripped = word[len(prefix):]
                if stripped not in ARABIC_STOPWORDS:
                    variants.add(stripped)
                
        # 2. Single-letter prefix stripping: guard against 3-letter root destruction (e.g. بيع -> يع)
        if word.startswith(('ب', 'ل', 'ك', 'ف', 'و')) and len(word) >= 4:
            stripped = word[1:]
            if len(stripped) >= 3 and stripped not in ARABIC_STOPWORDS and stripped not in SPURIOUS_STEMS:
                variants.add(stripped)

        # 3. Add composite stems and lemmas (filter spurious 2-letter tokens)
        stems = extract_composite_stems(word).split()
        for s in stems:
            if len(s) >= 3 and s not in ARABIC_STOPWORDS and s not in SPURIOUS_STEMS:
                variants.add(s)
            elif len(s) == 2 and s not in SPURIOUS_STEMS and len(word) == 2:
                variants.add(s)

        # Build disjunctive OR group
        disjunctive_group = " OR ".join(sorted(variants, key=lambda x: -len(x)))
        grouped_expressions.append(f"({disjunctive_group})")

    return f"salient_roots_text: {' AND '.join(grouped_expressions)}"
