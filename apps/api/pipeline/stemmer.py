import re
import pyarabic.araby as araby
from tashaphyne.stemming import ArabicLightStemmer

# Pre-compiled classical Arabic stopword particles
CLASSICAL_STOPWORDS = {
    "من", "الى", "إلى", "عن", "على", "في", "فى", "حتى", "خلا", "حاشا", "عدا",
    "مذ", "منذ", "رب", "ليس", "كان", "كانت", "يكون", "تكون", "ان", "إن", "أن",
    "انما", "إنما", "ما", "لا", "لم", "لن", "لو", "لولا", "لوما", "اما", "أما",
    "هو", "هي", "هما", "هم", "هن", "انت", "أنت", "انتم", "أنتم", "نحن", "انا", "أنا",
    "هذا", "هذه", "هذان", "هاتان", "هؤلاء", "ذلك", "ذاك", "تلك", "اولئك", "أولئك",
    "الذي", "التي", "اللذان", "اللتان", "الذين", "اللاتي", "اللواتي", "الائي", "اللائي",
    "اذا", "إذا", "اذ", "إذ", "ثم", "او", "أو", "ام", "أم", "بل", "لكن", "لكنما",
    "غير", "سوى", "بيد", "كل", "بعض", "مع", "عند", "لدى", "بين", "فوق", "تحت",
    "قبل", "بعد", "حيث", "اي", "أي", "كيف", "اين", "أين", "متى", "كم", "مهما"
}

_STEMMER = ArabicLightStemmer()

def normalize_arabic(text: str) -> str:
    """
    Performs deterministic classical Arabic orthographic normalization:
    1. Strips Tashkeel (vowels/harakat) and Tatweel/Kashida.
    2. Unifies Alef variants (أ, إ, آ, ٱ -> ا).
    3. Normalizes Taa Marbutah (ة -> ه) and Alif Maqsura (ى -> ي).
    4. Cleans non-Arabic characters, brackets, HTML tags, and extra spaces.
    """
    if not text:
        return ""
    
    # Strip HTML tags if present
    text = re.sub(r"<[^>]+>", " ", text)
    
    # Strip Tashkeel (harakat) and Tatweel using PyArabic
    text = araby.strip_tashkeel(text)
    text = araby.strip_tatweel(text)
    
    # Unify Alef forms
    text = araby.normalize_alef(text)
    text = araby.normalize_hamza(text)
    text = araby.normalize_teh(text)   # ة -> ه
    
    # Normalize Alif Maqsura: ى -> ي
    text = text.replace(araby.ALEF_MAKSURA, araby.YEH)
    
    # Keep only Arabic characters and basic alphanumeric tokens
    text = re.sub(r"[^\u0621-\u064A0-9\s]", " ", text)
    
    # Normalize whitespace
    text = re.sub(r"\s+", " ", text).strip()
    return text

def extract_composite_stems(text: str) -> str:
    """
    Extracts a space-delimited composite string of normalized Lemmas + Trilateral Roots.
    Combines:
    - Normalized surface word (de-voweled)
    - Light stem (from Tashaphyne)
    - Extracted root candidate (from Tashaphyne)
    Filters out short words (< 2 chars) and classical stop words.
    """
    norm_text = normalize_arabic(text)
    if not norm_text:
        return ""
    
    words = norm_text.split()
    tokens = []
    seen = set()
    
    for word in words:
        if len(word) < 2 or word in CLASSICAL_STOPWORDS:
            continue
            
        # 1. Surface lemma
        if word not in seen:
            seen.add(word)
            tokens.append(word)
            
        # 2. Light stem and root from Tashaphyne
        _STEMMER.light_stem(word)
        stem = _STEMMER.get_stem()
        root = _STEMMER.get_root()
        
        if stem and len(stem) >= 2 and stem not in seen and stem not in CLASSICAL_STOPWORDS:
            seen.add(stem)
            tokens.append(stem)
            
        if root and len(root) >= 2 and root not in seen and root not in CLASSICAL_STOPWORDS:
            seen.add(root)
            tokens.append(root)
            
    return " ".join(tokens)
