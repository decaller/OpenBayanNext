import React, { useState } from 'react';
import {
  Search,
  SlidersHorizontal,
  BookOpen,
  Layers,
  Sparkles,
  ExternalLink,
  Copy,
  Check,
  Languages,
  X,
  FileCode,
  CheckCircle2,
  Target,
  Cpu,
  CornerDownLeft,
  Compass,
  ArrowUpRight,
  Highlighter,
  ChevronUp,
  ChevronDown,
  Plus,
  Link2,
  Maximize2
} from 'lucide-react';

const MOCK_QUERY = {
  en: "What is the juristic and spiritual definition of the Heart (Al-Qalb)?",
  ar: "ما هو التعريف الفقهي والروحي للقلب وحقيقته؟"
};

const ACTIVE_ROOT_PATTERNS = {
  ar: [
    "القلب", "قلب", "قلبه", "للقلب", "القلوب",
    "اللطيفة", "لطيفة",
    "الروح", "روحانية", "روح",
    "العقل", "يعقلون", "عقل",
    "المدرك", "الإدراك", "إدراك",
    "اللحم", "الصنوبري"
  ],
  en: [
    "Heart", "heart", "hearts",
    "subtle", "entity", "spiritual",
    "intellect", "Intellect", "discernment",
    "cognition", "organ", "flesh", "perceives"
  ]
};

const MOCK_CLUSTERS = [
  {
    id: "cl-1",
    title_en: "1. Dual Meaning: Biological Organ vs. Spiritual Faculty",
    title_ar: "١. المعنى المزدوج: اللحم الصنوبري مقابل اللطيفة الربانية",
    doc_count: 8,
    dominant_roots: ["ق-ل-ب", "ل-ط-ف", "ر-و-ح", "ج-س-م"],
    sources: ["Iḥyāʾ ʿUlūm al-Dīn", "Al-Futūḥāt al-Makkiyyah"],
    summary_en: "Differentiates the anatomical muscle from the cognitive divine subtle entity (al-Laṭīfah al-Rabbāniyyah).",
    summary_ar: "التمييز بين العضو العضلي الصنوبري واللطيفة الروحانية الربانية التي هي مناط التكليف والإدراك."
  },
  {
    id: "cl-2",
    title_en: "2. Epistemic Locus: Brain (Dimāgh) vs. Heart (Qalb) in Legal Discernment",
    title_ar: "٢. مناط التكليف والإدراك: القلب أم الدماغ في الفقه والأصول",
    doc_count: 14,
    dominant_roots: ["ع-ق-ل", "د-ر-ك", "ف-ق-ه", "ص-د-ر"],
    sources: ["Al-Majmūʿ Sharḥ al-Muhadhdhab", "Al-Baḥr al-Muḥīṭ"],
    summary_en: "Examines the legal dispute on the seat of the intellect (Manāṭ al-Taklīf) between the four Sunni schools.",
    summary_ar: "تحقيق الخلاف الفقهي والأصولي بين الجمهور والحنفية والأطباء في محل استقرار العقل والإدراك."
  },
  {
    id: "cl-3",
    title_en: "3. Purification and Diseases of the Spiritual Heart",
    title_ar: "٣. آفات القلوب وأحكام تزكيتها ومفسدات الإخلاص",
    doc_count: 22,
    dominant_roots: ["م-ر-ض", "ط-ه-ر", "ش-ب-ه", "ن-ف-س"],
    sources: ["Jāmiʿ al-ʿUlūm wa-l-Ḥikam", "Madārij al-Sālikīn"],
    summary_en: "Outlines the causality between inner spiritual health and outer compliance in Hadith commentaries.",
    summary_ar: "بيان تلازم استقامة أعمال الجوارح الظاهرة مع طهارة النية وسلامة القلب الباطن في شروح الحديث."
  }
];

const MOCK_PASSAGES = [
  {
    chunk_id: 849201,
    book_id: 112,
    book_name_en: "Iḥyāʾ ʿUlūm al-Dīn (Revival of Religious Sciences)",
    book_name_ar: "إحياء علوم الدين",
    author_en: "Abū Ḥāmid al-Ghazālī (d. 505 AH)",
    author_ar: "أبو حامد الغزالي (ت 505 هـ)",
    vol_page: "Vol 3, p. 3",
    category_en: "Theology & Purification (Tazkiyah)",
    category_ar: "العقيدة والتزكية",
    breadcrumb: "Kitāb Sharḥ ʿAjāʾib al-Qalb > Bayān Maʿnā al-Nafs wa-l-Rūḥ wa-l-Qalb",
    discourse_flag: "Definition / Istilāḥ",
    continuity_score: 0.88,
    shamela_url: "https://shamela.ws/book/1887/1002",
    turath_url: "https://turath.io/book/1887?page=1002",
    raw_text_en: "The term 'Heart' (al-Qalb) is used for two distinct meanings: First, the physical pinecone-shaped flesh situated on the left side of the chest, hollow within, containing dark blood which is the reservoir and source of animal spirit. Second, it signifies a divine, subtle spiritual entity (Laṭīfah Rabbāniyyah Rūḥāniyyah) that possesses an intimate connection to this physical body. That subtle entity is the true essence of human reality; it is the entity within man that perceives, knows, is addressed with divine commands, held accountable, and rewarded.",
    raw_text_ar: "اللفظ الأول: القلب؛ ويطلق لمعنيين: أحدهما اللحم الصنوبري الشكل المودع في الجانب الأيسر من الصدر، وهو لحم مخصوص في باطنه تجويف، وفي ذلك التجويف دم أسود هو منبع الروح ومعدنه... والمعنى الثاني: هو لطيفة ربانية روحانية، لها بهذا القلب الجسماني تعلق، وتلك اللطيفة هي حقيقة الإنسان، وهو المدرك العالم العارف من الإنسان، وهو المخاطب والمطالب والمعاقب.",
    preceding_context_en: "...Know that the terms Heart, Spirit, Soul, and Intellect have different meanings across disciplines, leading many scholars to confuse theoretical rulings with physiological organs...",
    preceding_context_ar: "...اعلم أن هذه الأسماء الأربعة تستعمل في هذه الأبواب، وقلما يتفق للعلماء المحققين استيفاء الفرق بين هذه الأسامي واختلاف مقاصدها، فعرض من ذلك خلط عظيم...",
    succeeding_context_en: "Whenever we mention 'the Heart' in this book, we intend this spiritual reality, not the physical organ shared with beasts...",
    succeeding_context_ar: "وحيثما أطلقنا لفظ القلب في هذا الكتاب فإنا نعني به هذه اللطيفة المدركة، ولا نعني به اللحم الصنوبري المشترك بين الإنسان وسائر البهائم...",
    cluster_id: "cl-1",
    order: 412
  },
  {
    chunk_id: 849202,
    book_id: 112,
    book_name_en: "Iḥyāʾ ʿUlūm al-Dīn (Revival of Religious Sciences)",
    book_name_ar: "إحياء علوم الدين",
    author_en: "Abū Ḥāmid al-Ghazālī (d. 505 AH)",
    author_ar: "أبو حامد الغزالي (ت 505 هـ)",
    vol_page: "Vol 3, p. 5",
    category_en: "Theology & Purification (Tazkiyah)",
    category_ar: "العقيدة والتزكية",
    breadcrumb: "Kitāb Sharḥ ʿAjāʾib al-Qalb > Faṣl fī Junūd al-Qalb",
    discourse_flag: "Sub-division / Taqsīm",
    continuity_score: 0.81,
    shamela_url: "https://shamela.ws/book/1887/1004",
    turath_url: "https://turath.io/book/1887?page=1004",
    raw_text_en: "Know that the soldiers of the heart are divided into three classifications: One class consists of craving (shahwah) and anger (ghaḍab) which attract benefit and repel harm; the second consists of motor faculties; and the third consists of the cognitive senses that perceive realities.",
    raw_text_ar: "اعلم أن جنود القلب تنقسم إلى ثلاثة أقسام: قسم يبعث ويستحث وهو الشهوة والغضب اللذان بهما جلب المنافع ودفع المضار، وقسم يحرك الأعضاء، وقسم يدرك ويتعرف وهو الحواس الباطنة والظاهرة.",
    preceding_context_en: "...Explanation of how the spiritual heart commands the physical bodily limbs as a king commands his subjects...",
    preceding_context_ar: "...بيان تمثيل القلب بالملك وسائر الأعضاء والشهوات بالرعايا والجنود...",
    succeeding_context_en: "And whenever these internal armies transgress the boundary of equilibrium, spiritual corruption occurs...",
    succeeding_context_ar: "ومتى خرجت هذه القوى عن حد الاعتدال والانقياد لحكم العقل والشرع، هلك العبد وفسدت مملكته...",
    cluster_id: "cl-1",
    order: 414
  },
  {
    chunk_id: 602319,
    book_id: 84,
    book_name_en: "Al-Majmūʿ Sharḥ al-Muhadhdhab",
    book_name_ar: "المجموع شرح المهذب",
    author_en: "Yaḥyā ibn Sharaf al-Nawawī (d. 676 AH)",
    author_ar: "الإمام النووي (ت 676 هـ)",
    vol_page: "Vol 1, p. 44",
    category_en: "Comparative Jurisprudence (Fiqh)",
    category_ar: "الفقه المقارن وأصوله",
    breadcrumb: "Kitāb al-Ṭahārah > Mas'alat al-ʿAql wa Mahalluhu",
    discourse_flag: "Dialectical Refutation (Qulnā)",
    continuity_score: 0.74,
    shamela_url: "https://shamela.ws/book/21812/44",
    turath_url: "https://turath.io/book/21812?page=44",
    raw_text_en: "Regarding the locus of the Intellect (al-ʿAql): Our Shāfiʿī scholars, as well as the majority of jurists and theologians, held that its seat is the Heart (al-Qalb), from which light ascends to the brain. Abu Ḥanīfah and a faction of physicians stated its seat is the Brain. The proof of the majority is the explicit Quranic text: 'Have they not traveled through the land and have they hearts wherewith to understand' [Al-Ḥajj: 46], explicitly attributing discernment to the heart.",
    raw_text_ar: "فرعٌ في محل العقل: مذهبنا ومذهب جماهير الفقهاء والمتكلمين أنه في القلب، وله اتصال بالدماغ، وقال أبو حنيفة وطائفة من الأطباء: هو في الدماغ. وحجة الجمهور قوله تعالى: {أَفَلَمْ يَسِيرُوا فِي الْأَرْضِ فَتَكُونَ لَهُمْ قُلُوبٌ يَعْقِلُونَ بِهَا}، فأضاف العقل إلى القلب نصاً صريحاً.",
    preceding_context_en: "...Section discussing legal discernment and the conditions of religious obligation (Taklīf)...",
    preceding_context_ar: "...فصل في شروط التكليف وحقيقة الإدراك الذي يتعلق به الخطاب الشرعي...",
    succeeding_context_en: "If it is objected that brain damage impairs cognition, we respond: The brain is the cognitive sensorium, while the heart is the core grounding faculty...",
    succeeding_context_ar: "فإن قيل: إذا زال الدماغ زال الإدراك فكيف يكون مقره القلب؟ قلنا: الدماغ آلة للإدراك ومحل لاتصاله، والقلب هو أصل الإرادة ومستقر المعرفة...",
    cluster_id: "cl-2",
    order: 89
  },
  {
    chunk_id: 911405,
    book_id: 204,
    book_name_en: "Jāmiʿ al-ʿUlūm wa-l-Ḥikam",
    book_name_ar: "جامع العلوم والحكم",
    author_en: "Ibn Rajab al-Ḥanbalī (d. 795 AH)",
    author_ar: "ابن رجب الحنبلي (ت 795 هـ)",
    vol_page: "Vol 1, p. 145",
    category_en: "Hadith Commentary & Ethics",
    category_ar: "شروح الحديث والرقائق",
    breadcrumb: "Sharḥ Ḥadīth: 'Al-Ḥalālu Bayyin' > Faṣl fī Ṣalāḥ al-Qalb",
    discourse_flag: "Hadith Sharḥ / Condition",
    continuity_score: 0.62,
    shamela_url: "https://shamela.ws/book/11993/145",
    turath_url: "https://turath.io/book/11993?page=145",
    raw_text_en: "On the Prophet's ﷺ statement: 'Verily in the body there is a piece of flesh: if it is sound, the whole body is sound.' This indicates that the rectitude of a servant's physical actions, his restraint from prohibitions, and his engagement in lawful matters are all contingent upon the rectitude of the heart's movement and intentions. If the heart is populated with reverent awe of Allah, no limb moves toward disobedience.",
    raw_text_ar: "قوله صلى الله عليه وسلم: (ألا وإن في الجسد مضغة إذا صلحت صلح الجسد كله وإذا فسدت فسد الجسد كله ألا وهي القلب). فيه تصريح بأن صلاح حركات الجوارح واجتنابها للمحرمات واتقاءها للشبهات بحسب صلاح حركة القلب؛ فإن كان قلبه سليماً ليس فيه إلا محبة الله وما يحبه الله، صلحت حركات الجوارح كلها.",
    preceding_context_en: "...Explanation of doubtful matters (Al-Shubuhāt) and how they corrupt the inner conscience...",
    preceding_context_ar: "...بيان درجات الورع وكيفية توقي الشبهات التي تتردد بين الحل والحرمة...",
    succeeding_context_en: "And whenever the heart is diseased with lusts or persistent doubts, outer limbs inevitably falter in worship...",
    succeeding_context_ar: "ومتى كان القلب فاسداً قد استولى عليه اتباع الهوى وطلب الشهوات، فسدت حركات الجوارح كلها وانبعثت في المعاصي...",
    cluster_id: "cl-3",
    order: 302
  }
];

function HighlightedText({ text, lang, isFocus = false }) {
  if (!text) return null;
  const patterns = lang === 'ar' ? ACTIVE_ROOT_PATTERNS.ar : ACTIVE_ROOT_PATTERNS.en;
  
  const escaped = patterns.map(p => p.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')).join('|');
  const regex = new RegExp(`(${escaped})`, 'gi');

  const parts = text.split(regex);

  return (
    <span>
      {parts.map((part, index) => {
        const isMatch = patterns.some(p => p.toLowerCase() === part.toLowerCase());
        if (isMatch) {
          return (
            <mark
              key={index}
              className={`rounded px-1 py-0.5 font-semibold transition-colors ${
                isFocus
                  ? 'bg-emerald-200/90 text-emerald-950 border-b-2 border-emerald-600'
                  : 'bg-amber-100 text-amber-950 border-b border-amber-400'
              }`}
            >
              {part}
            </mark>
          );
        }
        return <span key={index}>{part}</span>;
      })}
    </span>
  );
}

export default function App() {
  const [lang, setLang] = useState('en'); // 'en' | 'ar'
  const [searchMode, setSearchMode] = useState('semantic'); // 'semantic' | 'direct'
  const [globalDepth, setGlobalDepth] = useState(2); // 1: Atomic, 2: Discourse, 3: Reading
  const [cardDepths, setCardDepths] = useState({});
  const [toastMessage, setToastMessage] = useState(null);
  const [queryInput, setQueryInput] = useState(MOCK_QUERY.en);
  const [enableHighlight, setEnableHighlight] = useState(true);

  // Inspector Drawer State with Sibling Buffer
  const [drawerData, setDrawerData] = useState(null); 
  // drawerData structure: { focusPassage, loadedBefore: [...chunks], loadedAfter: [...] }

  const isRtl = lang === 'ar';

  const showToast = (msg) => {
    setToastMessage(msg);
    setTimeout(() => setToastMessage(null), 3500);
  };

  const handleLanguageToggle = () => {
    const nextLang = lang === 'en' ? 'ar' : 'en';
    setLang(nextLang);
    setQueryInput(nextLang === 'en' ? MOCK_QUERY.en : MOCK_QUERY.ar);
  };

  const getEffectiveDepth = (chunkId) => {
    return cardDepths[chunkId] || globalDepth;
  };

  // Open inspection drawer initialized with multiple preceding/succeeding chunks
  const openInspectorDrawer = (passage, focusDirection = 'center') => {
    // Generate initial dynamic sibling chunks (N-2, N-1, Focus N, N+1, N+2)
    const baseOrder = passage.order || 400;
    
    const initialBefore = [
      {
        chunk_id: passage.chunk_id - 2,
        order: baseOrder - 2,
        text_en: `[Chunk N-2 Context] Preliminary introduction establishing the disciplinary definitions in ${passage.book_name_en}...`,
        text_ar: `[مقتطف ن-٢] مقدمة تمهيدية تقرر الاصطلاحات المستعملة في هذا الفن من كتاب ${passage.book_name_ar}...`
      },
      {
        chunk_id: passage.chunk_id - 1,
        order: baseOrder - 1,
        text_en: passage.preceding_context_en,
        text_ar: passage.preceding_context_ar
      }
    ];

    const initialAfter = [
      {
        chunk_id: passage.chunk_id + 1,
        order: baseOrder + 1,
        text_en: passage.succeeding_context_en,
        text_ar: passage.succeeding_context_ar
      },
      {
        chunk_id: passage.chunk_id + 2,
        order: baseOrder + 2,
        text_en: `[Chunk N+2 Context] Concluding observations detailing exceptions and subsequent scholarly commentary in ${passage.book_name_en}...`,
        text_ar: `[مقتطف ن+٢] خاتمة وتعقيبات تذكر الاستثناءات والوجوه الشارحة للعبارات المتقدمة في ${passage.book_name_ar}...`
      }
    ];

    setDrawerData({
      focusPassage: passage,
      focusDirection,
      beforeChunks: initialBefore,
      afterChunks: initialAfter
    });
  };

  const handleLoadMoreBefore = () => {
    if (!drawerData) return;
    const oldest = drawerData.beforeChunks[0];
    const newOrder = oldest.order - 1;
    const newChunk = {
      chunk_id: oldest.chunk_id - 1,
      order: newOrder,
      text_en: `[Chunk N-${drawerData.beforeChunks.length + 2}] Earlier textual context expanding prior arguments and foundational premises...`,
      text_ar: `[مقتطف ن-${drawerData.beforeChunks.length + 2}] سياق نصي أقدم يستعرض مقدمات المسألة وأدلتها الأصلية...`
    };
    setDrawerData({
      ...drawerData,
      beforeChunks: [newChunk, ...drawerData.beforeChunks]
    });
    showToast(lang === 'en' ? 'Loaded earlier chunk (N-3)...' : 'تم تحميل المقتطف الأسبق (ن-٣)...');
  };

  const handleLoadMoreAfter = () => {
    if (!drawerData) return;
    const newest = drawerData.afterChunks[drawerData.afterChunks.length - 1];
    const newOrder = newest.order + 1;
    const newChunk = {
      chunk_id: newest.chunk_id + 1,
      order: newOrder,
      text_en: `[Chunk N+${drawerData.afterChunks.length + 2}] Subsequent chapter context elaborating secondary branches and legal implications...`,
      text_ar: `[مقتطف ن+${drawerData.afterChunks.length + 2}] سياق نصي لاحق يتناول الفروع الثانوية والآثار التكليفية...`
    };
    setDrawerData({
      ...drawerData,
      afterChunks: [...drawerData.afterChunks, newChunk]
    });
    showToast(lang === 'en' ? 'Loaded later chunk (N+3)...' : 'تم تحميل المقتطف اللاحق (ن+٣)...');
  };

  const setCardDepth = (chunkId, depth) => {
    setCardDepths(prev => ({ ...prev, [chunkId]: depth }));
    if (depth === 3) {
      const passage = MOCK_PASSAGES.find(p => p.chunk_id === chunkId);
      if (passage) openInspectorDrawer(passage, 'center');
    }
  };

  // Copy Single Passage for AI
  const handleCopyPassageForAI = (passage) => {
    const text = lang === 'en' ? passage.raw_text_en : passage.raw_text_ar;
    const book = lang === 'en' ? passage.book_name_en : passage.book_name_ar;
    const author = lang === 'en' ? passage.author_en : passage.author_ar;
    
    const prompt = `Please analyze this verified classical passage from ${book} (${author}), ${passage.vol_page}:

Canonical Link: https://corpus.ai/p/${passage.chunk_id}
Online Editions: Shamela (${passage.shamela_url}) | Turath (${passage.turath_url})
Taxonomy Breadcrumb: ${passage.breadcrumb}
Discourse Flag: ${passage.discourse_flag}

Text:
"${text}"

Task: Analyze its juristic implications, grammatical conditions, and how classical commentators frame this definition.`;

    copyText(prompt, lang === 'en' ? "Passage prompt copied for AI!" : "تم نسخ بطاقة الاستشهاد للذكاء الاصطناعي!");
  };

  const copyPageUrlForAI = () => {
    const currentUrl = `https://corpus.ai/search?q=${encodeURIComponent(queryInput)}&mode=${searchMode}&depth=${globalDepth}`;
    const aiPrompt = `Please analyze and synthesize the classical Islamic corpus search results available at this live URL:
${currentUrl}

Task: Explore the primary source passages on this page, evaluate the differences between juristic and spiritual definitions, and summarize the consensus across Sunni schools.`;

    copyText(aiPrompt, lang === 'en' ? "Page URL prompt copied for your AI!" : "تم نسخ رابط الصفحة الموثق لاستكشافه بالذكاء الاصطناعي!");
  };

  const copyText = (content, successMsg) => {
    try {
      const el = document.createElement('textarea');
      el.value = content;
      document.body.appendChild(el);
      el.select();
      document.execCommand('copy');
      document.body.removeChild(el);
      showToast(successMsg);
    } catch {
      showToast(lang === 'en' ? "Failed to copy" : "تعذر النسخ");
    }
  };

  const scrollToCluster = (clusterId) => {
    const el = document.getElementById(clusterId);
    if (el) {
      el.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  };

  return (
    <div className={`min-h-screen bg-stone-100 text-stone-900 font-sans antialiased flex flex-col ${isRtl ? 'rtl text-right' : 'ltr text-left'}`} dir={isRtl ? 'rtl' : 'ltr'}>
      
      {/* --- TOP NAVBAR --- */}
      <header className="sticky top-0 z-30 bg-white/95 backdrop-blur-sm border-b border-stone-200 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between gap-4">
          
          {/* Logo / Brand */}
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-lg bg-emerald-800 text-white flex items-center justify-center font-serif font-bold text-lg shadow-sm">
              ش
            </div>
            <div>
              <div className="text-sm font-bold tracking-tight text-stone-900">
                {lang === 'en' ? 'Turāth Semantic Corpus' : 'المكتبة الشاملة الدلالية'}
              </div>
              <div className="text-[10px] text-stone-500 font-mono">
                {lang === 'en' ? '5.91M Passages • Turso Tantivy BM25 + Jaccard' : '٥.٩١ مليون مقتطف • محرك بحث نصوص واسترجاع تركيبي'}
              </div>
            </div>
          </div>

          {/* Right Controls */}
          <div className="flex items-center gap-2.5">
            <div className="hidden sm:flex items-center gap-1.5 text-xs text-stone-500 font-mono bg-stone-50 px-2.5 py-1 rounded-md border border-stone-200">
              <Cpu className="w-3.5 h-3.5 text-emerald-700" />
              <span>Turso/libSQL: 0.84ms</span>
            </div>

            {/* Language Switcher */}
            <button
              onClick={handleLanguageToggle}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-stone-300 bg-white hover:bg-stone-50 text-xs font-semibold text-stone-700 transition-colors shadow-sm"
              title="Toggle Language (English / Arabic)"
            >
              <Languages className="w-3.5 h-3.5 text-emerald-700" />
              <span>{lang === 'en' ? 'العربية' : 'English'}</span>
            </button>
          </div>
        </div>
      </header>

      {/* --- SEARCH & CONTROL PANEL --- */}
      <div className="bg-white border-b border-stone-200 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-5 space-y-3.5">
          
          {/* Main Search Input with Inline Search Mode Switcher */}
          <div className="relative flex flex-col md:flex-row items-stretch gap-2 bg-stone-50 p-1.5 rounded-xl border border-stone-300 focus-within:border-emerald-700 focus-within:ring-1 focus-within:ring-emerald-700 transition-all">
            
            {/* Search Mode Toggle (Semantic vs Direct) */}
            <div className="flex items-center bg-stone-200/80 p-0.5 rounded-lg text-xs font-medium shrink-0">
              <button
                type="button"
                onClick={() => setSearchMode('semantic')}
                className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md transition-all text-xs ${
                  searchMode === 'semantic'
                    ? 'bg-white text-emerald-900 font-bold shadow-sm'
                    : 'text-stone-600 hover:text-stone-900'
                }`}
                title="Vector & Meaning Search (Multilingual Embeddings)"
              >
                <Sparkles className="w-3.5 h-3.5 text-emerald-700" />
                <span>{lang === 'en' ? 'Semantic / Meaning' : 'بحث دلالي / بالمعنى'}</span>
              </button>

              <button
                type="button"
                onClick={() => setSearchMode('direct')}
                className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md transition-all text-xs ${
                  searchMode === 'direct'
                    ? 'bg-white text-emerald-900 font-bold shadow-sm'
                    : 'text-stone-600 hover:text-stone-900'
                }`}
                title="Exact Root & BM25 Keyword Search"
              >
                <Target className="w-3.5 h-3.5 text-emerald-700" />
                <span>{lang === 'en' ? 'Direct / Exact Root' : 'بحث مطابق / بالجذر'}</span>
              </button>
            </div>

            {/* Input Box */}
            <div className="relative flex-1 flex items-center">
              <Search className={`w-4 h-4 text-stone-400 absolute ${isRtl ? 'right-3' : 'left-3'}`} />
              <input
                type="text"
                value={queryInput}
                onChange={(e) => setQueryInput(e.target.value)}
                placeholder={
                  searchMode === 'semantic'
                    ? (lang === 'en' ? "Type a conceptual inquiry in any language (e.g. 'invalidating wudu', 'heart cognition')..." : "اكتب مسألة أو سؤالاً بالمعنى بأي لغة...")
                    : (lang === 'en' ? "Search exact Arabic roots or terms (e.g. 'ق-ل-ب', 'بيع السلم', 'نية')..." : "ابحث بالجذر الصريح أو اللفظ المطابق (مثل: ق-ل-ب، بيع السلم)...")
                }
                className={`w-full bg-transparent text-sm py-2 px-9 text-stone-900 focus:outline-none font-medium placeholder:text-stone-400 placeholder:font-normal`}
              />
            </div>

            {/* Search Execution Button */}
            <button
              onClick={() => showToast(lang === 'en' ? `Re-indexed with ${searchMode.toUpperCase()} mode` : `تم التحديث بنمط ${searchMode}`)}
              className="bg-emerald-800 hover:bg-emerald-900 text-white text-xs font-bold px-4 py-2 rounded-lg flex items-center justify-center gap-1.5 transition-colors shadow-sm shrink-0"
            >
              <span>{lang === 'en' ? 'Search' : 'بحث'}</span>
              <CornerDownLeft className="w-3.5 h-3.5 opacity-80" />
            </button>
          </div>

          {/* SUB-SEARCH ACTION BAR: Depth Switcher + Root Highlights + Copy to AI */}
          <div className="flex flex-wrap items-center justify-between gap-3 pt-1 text-xs">
            
            {/* Left Actions: Depth Switcher & Highlight Toggle */}
            <div className="flex flex-wrap items-center gap-3">
              
              {/* Context Depth Switcher */}
              <div className="flex items-center bg-stone-100 p-0.5 rounded-lg border border-stone-200">
                <span className="text-[11px] font-semibold text-stone-500 px-2 flex items-center gap-1">
                  <SlidersHorizontal className="w-3 h-3 text-stone-600" />
                  {lang === 'en' ? 'Depth Level:' : 'مستوى العمق:'}
                </span>
                {[
                  { id: 1, label_en: 'Atomic (Snippet)', label_ar: 'مقتطف (لب)' },
                  { id: 2, label_en: 'Discourse (±1 Context)', label_ar: 'سياق (ن±١)' }
                ].map(d => (
                  <button
                    key={d.id}
                    onClick={() => {
                      setGlobalDepth(d.id);
                      setCardDepths({});
                    }}
                    className={`px-2.5 py-1 rounded-md transition-all text-xs ${
                      globalDepth === d.id
                        ? 'bg-white text-emerald-900 font-bold shadow-sm border border-stone-200/80'
                        : 'text-stone-600 hover:text-stone-900'
                    }`}
                  >
                    {lang === 'en' ? d.label_en : d.label_ar}
                  </button>
                ))}
              </div>

              {/* Root & Keyword Highlighting Toggle */}
              <button
                onClick={() => setEnableHighlight(!enableHighlight)}
                className={`flex items-center gap-1.5 px-2.5 py-1 rounded-lg border text-[11px] transition-all ${
                  enableHighlight
                    ? 'bg-emerald-50 text-emerald-900 border-emerald-300 font-semibold'
                    : 'bg-stone-100 text-stone-500 border-stone-200 hover:text-stone-700'
                }`}
                title="Toggle highlighting of roots and search terms"
              >
                <Highlighter className="w-3 h-3" />
                <span>{lang === 'en' ? 'Root Highlights' : 'تمييز الجذور والألفاظ'}</span>
              </button>

              {/* Quick Jump Anchors to Thematic Groups */}
              <div className="hidden xl:flex items-center gap-1.5 text-stone-600 text-[11px]">
                <Compass className="w-3.5 h-3.5 text-stone-400" />
                <span className="text-stone-400">{lang === 'en' ? 'Jump to:' : 'انتقال إلى:'}</span>
                {MOCK_CLUSTERS.map((cl, idx) => (
                  <button
                    key={cl.id}
                    onClick={() => scrollToCluster(cl.id)}
                    className="bg-stone-100 hover:bg-stone-200 text-stone-700 px-2 py-0.5 rounded text-[11px] transition-colors"
                  >
                    #{idx + 1}
                  </button>
                ))}
              </div>
            </div>

            {/* Right Actions: Copy Page URL for AI */}
            <div className="flex items-center gap-2">
              <button
                onClick={copyPageUrlForAI}
                className="flex items-center gap-1.5 px-3.5 py-1.5 bg-stone-900 hover:bg-stone-800 text-white rounded-lg text-xs font-semibold transition-all shadow-sm"
                title="Copy the live search page URL formatted as a prompt for ChatGPT/Claude"
              >
                <Copy className="w-3.5 h-3.5 text-emerald-400" />
                <span>{lang === 'en' ? 'Copy Page URL for AI' : 'نسخ رابط الصفحة للذكاء الاصطناعي'}</span>
              </button>
            </div>

          </div>
        </div>
      </div>

      {/* --- MAIN WORKSPACE CONTENT --- */}
      <main className="flex-1 max-w-7xl mx-auto w-full px-4 sm:px-6 lg:px-8 py-6 grid grid-cols-1 lg:grid-cols-12 gap-6">

        {/* MAIN COLUMN (8 cols): Structured Scrollable Thematic Sections */}
        <section className="lg:col-span-8 space-y-8">

          {/* Thematic Sections */}
          <div className="space-y-10">
            {MOCK_CLUSTERS.map((cluster, clusterIndex) => {
              const clusterPassages = MOCK_PASSAGES.filter(p => p.cluster_id === cluster.id);

              return (
                <section key={cluster.id} id={cluster.id} className="space-y-4 scroll-mt-24">
                  <div className="bg-stone-50 border-s-4 border-emerald-700 p-4 rounded-e-xl border border-stone-200/80 shadow-sm">
                    <div className="flex flex-wrap items-center justify-between gap-2 mb-1.5">
                      <div className="flex items-center gap-2">
                        <span className="text-xs font-mono font-bold bg-emerald-800 text-white px-2 py-0.5 rounded">
                          {clusterIndex + 1}
                        </span>
                        <h3 className="text-base font-bold text-stone-900 tracking-tight">
                          {lang === 'en' ? cluster.title_en : cluster.title_ar}
                        </h3>
                      </div>
                      <span className="text-xs bg-white text-stone-700 px-2.5 py-0.5 rounded-full border border-stone-200 font-mono font-medium">
                        {cluster.doc_count} {lang === 'en' ? 'passages' : 'مقتطف'}
                      </span>
                    </div>
                    <p className="text-xs text-stone-600 mb-3 font-sans">
                      {lang === 'en' ? cluster.summary_en : cluster.summary_ar}
                    </p>
                    <div className="flex flex-wrap items-center justify-between gap-2 pt-2 border-t border-stone-200/60 text-[11px] text-stone-500">
                      <div className="flex items-center gap-1.5">
                        <span className="font-semibold text-stone-600">
                          {lang === 'en' ? 'Roots:' : 'الجذور:'}
                        </span>
                        <div className="flex gap-1">
                          {cluster.dominant_roots.map(r => (
                            <span key={r} className="bg-white border border-stone-200 text-stone-800 font-semibold px-1.5 py-0.5 rounded font-mono text-[10px]">
                              {r}
                            </span>
                          ))}
                        </div>
                      </div>
                      <div className="flex items-center gap-1 text-stone-500">
                        <span className="font-semibold">{lang === 'en' ? 'Primary Sources:' : 'أهم المصادر:'}</span>
                        <span>{cluster.sources.join(' • ')}</span>
                      </div>
                    </div>
                  </div>

                  {/* Passages List within this Section */}
                  <div className="space-y-4">
                    {clusterPassages.map((passage) => {
                      const currentDepth = getEffectiveDepth(passage.chunk_id);
                      const text = lang === 'en' ? passage.raw_text_en : passage.raw_text_ar;
                      const preText = lang === 'en' ? passage.preceding_context_en : passage.preceding_context_ar;
                      const postText = lang === 'en' ? passage.succeeding_context_en : passage.succeeding_context_ar;

                      return (
                        <article
                          key={passage.chunk_id}
                          className="bg-white border border-stone-200 rounded-xl p-5 shadow-sm hover:border-stone-300 transition-all text-stone-900 space-y-4"
                        >
                          {/* 1. TOP SECTION: Text Snippet & Context Body (Appears First) */}
                          <div className="space-y-2">
                            {/* Level Switcher & ID Header */}
                            <div className="flex items-center justify-between pb-2 border-b border-stone-100">
                              <span className="text-[11px] font-mono text-stone-400">
                                CHUNK #{passage.chunk_id} • Jaccard {(passage.continuity_score * 100).toFixed(0)}%
                              </span>

                              {/* Per-Card Depth Stepper */}
                              <div className="flex items-center bg-stone-100 p-0.5 rounded-lg border border-stone-200 text-xs">
                                <button
                                  onClick={() => setCardDepth(passage.chunk_id, 1)}
                                  className={`px-2 py-0.5 rounded text-[11px] transition-all ${
                                    currentDepth === 1 ? 'bg-white font-bold text-stone-900 shadow-sm' : 'text-stone-500 hover:text-stone-800'
                                  }`}
                                >
                                  {lang === 'en' ? 'Snippet' : 'مقتطف'}
                                </button>
                                <button
                                  onClick={() => setCardDepth(passage.chunk_id, 2)}
                                  className={`px-2 py-0.5 rounded text-[11px] transition-all ${
                                    currentDepth === 2 ? 'bg-white font-bold text-emerald-900 shadow-sm' : 'text-stone-500 hover:text-stone-800'
                                  }`}
                                >
                                  {lang === 'en' ? 'Context (±1)' : 'سياق'}
                                </button>
                                <button
                                  onClick={() => setCardDepth(passage.chunk_id, 3)}
                                  className={`px-2 py-0.5 rounded text-[11px] transition-all flex items-center gap-1 ${
                                    currentDepth === 3 ? 'bg-white font-bold text-emerald-900 shadow-sm' : 'text-stone-500 hover:text-stone-800'
                                  }`}
                                >
                                  <span>{lang === 'en' ? 'Read' : 'مطالعة'}</span>
                                  <ExternalLink className="w-2.5 h-2.5" />
                                </button>
                              </div>
                            </div>

                            {/* Text Render with Root/Keyword Highlighting & Direct Sibling Exploration Triggers */}
                            <div className="font-serif leading-relaxed text-sm sm:text-base space-y-2.5 pt-1">
                              {currentDepth === 1 && (
                                <p className="text-stone-800">
                                  {enableHighlight ? (
                                    <HighlightedText text={text} lang={lang} isFocus={true} />
                                  ) : (
                                    text
                                  )}
                                </p>
                              )}

                              {currentDepth === 2 && (
                                <div className="space-y-2">
                                  {/* Preceding Block - Clicking opens Inspection Sidebar focused on N-1 */}
                                  {preText && (
                                    <div 
                                      onClick={() => openInspectorDrawer(passage, 'before')}
                                      className="text-xs text-stone-600 bg-stone-50 hover:bg-stone-100 p-2.5 rounded border-s-2 border-stone-300 cursor-pointer transition-colors group relative"
                                      title={lang === 'en' ? "Click to open Inspection Sidebar focused on preceding chunk" : "انقر لفتح الجانب الأسبق من المقتطف في شريط الفحص"}
                                    >
                                      <div className="flex items-center justify-between font-sans font-semibold text-[10px] text-stone-400 mb-0.5">
                                        <span>{lang === 'en' ? '◀ PRECEDING DISCOURSE (CHUNK N-1)' : '◀ السياق السابق (المقتطف السابق)'}</span>
                                        <span className="text-emerald-700 group-hover:underline flex items-center gap-0.5">
                                          {lang === 'en' ? 'Explore in Sidebar' : 'استكشاف في الجانب'}
                                          <Maximize2 className="w-2.5 h-2.5" />
                                        </span>
                                      </div>
                                      {enableHighlight ? (
                                        <HighlightedText text={preText} lang={lang} isFocus={false} />
                                      ) : (
                                        preText
                                      )}
                                    </div>
                                  )}

                                  {/* Active Focus Block */}
                                  <div className="bg-emerald-50/70 p-3.5 rounded-lg border-s-4 border-emerald-700 text-stone-900 font-medium shadow-sm">
                                    {enableHighlight ? (
                                      <HighlightedText text={text} lang={lang} isFocus={true} />
                                    ) : (
                                      text
                                    )}
                                  </div>

                                  {/* Succeeding Block - Clicking opens Inspection Sidebar focused on N+1 */}
                                  {postText && (
                                    <div 
                                      onClick={() => openInspectorDrawer(passage, 'after')}
                                      className="text-xs text-stone-600 bg-stone-50 hover:bg-stone-100 p-2.5 rounded border-s-2 border-stone-300 cursor-pointer transition-colors group relative"
                                      title={lang === 'en' ? "Click to open Inspection Sidebar focused on succeeding chunk" : "انقر لفتح الجانب اللاحق من المقتطف في شريط الفحص"}
                                    >
                                      <div className="flex items-center justify-between font-sans font-semibold text-[10px] text-stone-400 mb-0.5">
                                        <span>{lang === 'en' ? '▶ SUCCEEDING DISCOURSE (CHUNK N+1)' : '▶ السياق اللاحق (المقتطف اللاحق)'}</span>
                                        <span className="text-emerald-700 group-hover:underline flex items-center gap-0.5">
                                          {lang === 'en' ? 'Explore in Sidebar' : 'استكشاف في الجانب'}
                                          <Maximize2 className="w-2.5 h-2.5" />
                                        </span>
                                      </div>
                                      {enableHighlight ? (
                                        <HighlightedText text={postText} lang={lang} isFocus={false} />
                                      ) : (
                                        postText
                                      )}
                                    </div>
                                  )}
                                </div>
                              )}
                            </div>
                          </div>

                          {/* 2. BOTTOM SECTION: Book Metadata, Taxonomy & External Reader Links */}
                          <div className="pt-3 border-t border-stone-200 bg-stone-50/70 -mx-5 -mb-5 p-4 rounded-b-xl space-y-3">
                            
                            {/* Author, Book, and Path */}
                            <div className="flex flex-wrap items-center justify-between gap-2">
                              <div className="space-y-0.5">
                                <div className="flex items-center gap-2 flex-wrap">
                                  <span 
                                    onClick={() => openInspectorDrawer(passage, 'center')}
                                    className="text-xs font-bold text-stone-900 hover:text-emerald-800 cursor-pointer"
                                  >
                                    {lang === 'en' ? passage.book_name_en : passage.book_name_ar}
                                  </span>
                                  <span className="text-[11px] bg-white border border-stone-200 text-stone-700 px-2 py-0.5 rounded font-mono">
                                    {passage.vol_page}
                                  </span>
                                  <span className="text-[10px] bg-emerald-100 text-emerald-900 font-semibold px-2 py-0.5 rounded">
                                    {passage.discourse_flag}
                                  </span>
                                </div>
                                
                                <div className="text-[11px] text-stone-500 font-sans flex items-center gap-1.5 flex-wrap">
                                  <span>{lang === 'en' ? passage.author_en : passage.author_ar}</span>
                                  <span>•</span>
                                  <span className="text-stone-600 font-mono text-[10px]">{passage.breadcrumb}</span>
                                </div>
                              </div>
                            </div>

                            {/* Online Readers & Action Buttons */}
                            <div className="flex flex-wrap items-center justify-between pt-2 border-t border-stone-200/70 text-xs gap-2">
                              
                              {/* Direct Full Book Online Readers */}
                              <div className="flex items-center gap-1.5 flex-wrap">
                                <span className="text-[11px] font-semibold text-stone-500 me-1">
                                  {lang === 'en' ? 'Online Book:' : 'المصدر الكامل:'}
                                </span>

                                <a
                                  href={passage.turath_url}
                                  target="_blank"
                                  rel="noopener noreferrer"
                                  className="inline-flex items-center gap-1 px-2 py-1 rounded bg-teal-50 hover:bg-teal-100 text-teal-900 border border-teal-200 text-xs font-medium transition-colors"
                                  title="Open full book page on Turath.io"
                                >
                                  <BookOpen className="w-3 h-3 text-teal-700" />
                                  <span>Turath.io ↗</span>
                                </a>

                                <a
                                  href={passage.shamela_url}
                                  target="_blank"
                                  rel="noopener noreferrer"
                                  className="inline-flex items-center gap-1 px-2 py-1 rounded bg-amber-50 hover:bg-amber-100 text-amber-900 border border-amber-200 text-xs font-medium transition-colors"
                                  title="Open original edition on Al-Maktaba Al-Shamela"
                                >
                                  <ArrowUpRight className="w-3 h-3 text-amber-700" />
                                  <span>Shamela.ws ↗</span>
                                </a>
                              </div>

                              {/* Copy for AI & Full Node Inspection */}
                              <div className="flex items-center gap-2">
                                <button
                                  onClick={() => handleCopyPassageForAI(passage)}
                                  className="flex items-center gap-1 px-2.5 py-1 bg-stone-900 hover:bg-stone-800 text-white rounded text-xs font-sans transition-all shadow-sm"
                                  title="Copy structured citation card with online links for ChatGPT / Claude"
                                >
                                  <Copy className="w-3 h-3 text-emerald-400" />
                                  <span>{lang === 'en' ? 'Copy for AI' : 'نسخ للذكاء الاصطناعي'}</span>
                                </button>

                                <button
                                  onClick={() => openInspectorDrawer(passage, 'center')}
                                  className="px-2.5 py-1 bg-white hover:bg-stone-100 border border-stone-200 text-stone-700 rounded text-xs font-sans transition-colors flex items-center gap-1"
                                >
                                  <Maximize2 className="w-3 h-3 text-stone-500" />
                                  <span>{lang === 'en' ? 'Inspect Node' : 'فحص العقدة'}</span>
                                </button>
                              </div>
                            </div>

                          </div>
                        </article>
                      );
                    })}
                  </div>

                </section>
              );
            })}
          </div>

        </section>

        {/* SIDEBAR COLUMN (4 cols): Sticky Combined Navigation & AI Page URL Explorer */}
        <aside className="lg:col-span-4 space-y-6">

          <div className="sticky top-20 space-y-6">
            
            {/* Quick Table of Contents / Outline */}
            <div className="bg-white border border-stone-200 rounded-xl p-4 shadow-sm space-y-3">
              <div className="flex items-center justify-between pb-2 border-b border-stone-100">
                <h3 className="text-xs font-bold uppercase tracking-wider text-stone-500 flex items-center gap-1.5">
                  <Layers className="w-3.5 h-3.5 text-emerald-700" />
                  {lang === 'en' ? 'Thematic Structure' : 'الهيكل الموضوعي'}
                </h3>
                <span className="text-[10px] text-stone-400 font-mono">3 Sections</span>
              </div>

              <div className="space-y-2">
                {MOCK_CLUSTERS.map((cl, idx) => (
                  <button
                    key={cl.id}
                    onClick={() => scrollToCluster(cl.id)}
                    className="w-full text-start p-2.5 rounded-lg border border-stone-100 hover:border-emerald-300 hover:bg-emerald-50/40 transition-all text-xs group block"
                  >
                    <div className="flex items-center justify-between mb-1">
                      <span className="font-bold text-stone-800 group-hover:text-emerald-900">
                        {lang === 'en' ? `Section ${idx + 1}` : `المحور ${idx + 1}`}
                      </span>
                      <span className="text-[10px] text-stone-400 font-mono">
                        {cl.doc_count} passages
                      </span>
                    </div>
                    <div className="text-[11px] text-stone-600 truncate">
                      {lang === 'en' ? cl.title_en.split(':')[1] || cl.title_en : cl.title_ar.split(':')[1] || cl.title_ar}
                    </div>
                  </button>
                ))}
              </div>

              {/* Retrieval Telemetry Box */}
              <div className="pt-3 border-t border-stone-100 space-y-1.5 text-xs text-stone-600">
                <div className="flex justify-between">
                  <span className="text-stone-400">{lang === 'en' ? 'Retrieval Mode:' : 'نمط البحث:'}</span>
                  <span className="font-mono text-emerald-800 font-semibold">
                    {searchMode === 'semantic' ? 'Dense Vector (384-d)' : 'BM25 Sparse'}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-stone-400">{lang === 'en' ? 'Bitset SIMD Time:' : 'زمن الجاكارد:'}</span>
                  <span className="font-mono text-emerald-700 font-semibold">0.84 ms</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-stone-400">{lang === 'en' ? 'Engine Target:' : 'محرك البيانات:'}</span>
                  <span className="font-mono text-stone-800">Turso / libSQL</span>
                </div>
              </div>
            </div>

            {/* AI PAGE URL EXPLORER CARD (FOLLOWS SCROLL) */}
            <div className="bg-stone-900 text-stone-300 rounded-xl p-4 shadow-sm border border-stone-800 space-y-3 text-xs">
              <div className="flex items-center gap-2 text-white font-bold">
                <Sparkles className="w-4 h-4 text-emerald-400" />
                <span>{lang === 'en' ? 'Explore with Your Own AI' : 'استكشف بذكائك الاصطناعي الخاص'}</span>
              </div>
              
              <p className="text-stone-400 leading-relaxed text-[11px]">
                {lang === 'en'
                  ? 'Use your own AI model (ChatGPT, Claude, or Perplexity) to analyze and explore the primary source results on this page by copying the live URL:'
                  : 'استخدم نموذج الذكاء الاصطناعي الخاص بك (ChatGPT أو Claude أو Perplexity) لاستكشاف وتحليل نصوص هذه الصفحة عبر نسخ رابط الاستعلام المباشر:'}
              </p>

              {/* URL Box */}
              <div className="space-y-2 pt-1">
                <div className="relative flex items-center bg-black/60 border border-stone-800 rounded px-2.5 py-1.5">
                  <Link2 className="w-3.5 h-3.5 text-stone-500 me-2 shrink-0" />
                  <input
                    type="text"
                    readOnly
                    value={`https://corpus.ai/search?q=${encodeURIComponent(queryInput)}&mode=${searchMode}&depth=${globalDepth}`}
                    className="w-full bg-transparent font-mono text-[10px] text-emerald-300 focus:outline-none select-all truncate"
                  />
                </div>

                {/* Copy Page URL Button */}
                <button
                  onClick={copyPageUrlForAI}
                  className="w-full bg-emerald-700 hover:bg-emerald-800 text-white font-bold py-2 px-3 rounded-lg flex items-center justify-center gap-2 text-xs transition-colors shadow-sm"
                >
                  <Copy className="w-3.5 h-3.5" />
                  <span>{lang === 'en' ? 'Copy Page URL for AI' : 'نسخ رابط الصفحة للذكاء الاصطناعي'}</span>
                </button>
              </div>

              <div className="text-[10px] text-stone-500 pt-1 flex items-center justify-between border-t border-stone-800/80">
                <span>{lang === 'en' ? 'Format: SSR Markdown / JSON-LD' : 'التنسيق: Markdown نقي تلقائي'}</span>
                <span className="font-mono text-emerald-400">200 OK</span>
              </div>
            </div>

          </div>

        </aside>
      </main>

      {/* --- SITE FOOTER --- */}
      <footer className="mt-auto bg-white border-t border-stone-200 text-stone-600 text-xs font-sans">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 grid grid-cols-1 md:grid-cols-12 gap-8">

          {/* Brand & Platform Mission */}
          <div className="md:col-span-5 space-y-3">
            <div className="flex items-center gap-2.5">
              <div className="w-7 h-7 rounded bg-emerald-800 text-white flex items-center justify-center font-serif font-bold text-sm shadow-sm">
                ش
              </div>
              <span className="font-bold text-stone-900 text-sm">
                {lang === 'en' ? 'Turāth Semantic Corpus' : 'المكتبة الشاملة الدلالية'}
              </span>
            </div>
            <p className="text-stone-500 leading-relaxed text-xs max-w-sm">
              {lang === 'en'
                ? 'An open-access, high-performance semantic retrieval engine indexing 5.91M classical Islamic primary source passages across Jurisprudence, Theology, Hadith, and Tafsir.'
                : 'محرك بحث نصوص وتنقيب دلالي عالي الأداء يغطي ٥.٩١ مليون مقتطف تراثي في الفقه والعقيدة والحديث والتفسير.'}
            </p>
            <div className="flex items-center gap-3 pt-1 text-[11px] text-stone-400 font-mono">
              <span>Turso / libSQL</span>
              <span>•</span>
              <span>Tantivy BM25</span>
              <span>•</span>
              <span>Dense Vector SIMD</span>
            </div>
          </div>

          {/* Primary Source Digital Editions */}
          <div className="md:col-span-3 space-y-2.5">
            <h4 className="font-bold text-stone-900 text-xs uppercase tracking-wider">
              {lang === 'en' ? 'Digital Libraries' : 'المكتبات الرقمية'}
            </h4>
            <ul className="space-y-1.5 text-xs text-stone-600">
              <li>
                <a href="https://turath.io" target="_blank" rel="noopener noreferrer" className="hover:text-emerald-800 transition-colors inline-flex items-center gap-1">
                  <span>Turath.io (تراث)</span>
                  <ArrowUpRight className="w-3 h-3 text-stone-400" />
                </a>
              </li>
              <li>
                <a href="https://shamela.ws" target="_blank" rel="noopener noreferrer" className="hover:text-emerald-800 transition-colors inline-flex items-center gap-1">
                  <span>Al-Maktaba Al-Shamela (الشاملة)</span>
                  <ArrowUpRight className="w-3 h-3 text-stone-400" />
                </a>
              </li>
              <li>
                <a href="https://quran.ksu.edu.sa" target="_blank" rel="noopener noreferrer" className="hover:text-emerald-800 transition-colors inline-flex items-center gap-1">
                  <span>KSU Ayah & Tafsir Engine</span>
                  <ArrowUpRight className="w-3 h-3 text-stone-400" />
                </a>
              </li>
            </ul>
          </div>

          {/* Academic AI & API Specs */}
          <div className="md:col-span-4 space-y-2.5">
            <h4 className="font-bold text-stone-900 text-xs uppercase tracking-wider">
              {lang === 'en' ? 'Open API & AI Grounding' : 'بروتوكولات التوثيق والذكاء الاصطناعي'}
            </h4>
            <p className="text-stone-500 text-[11px] leading-relaxed">
              {lang === 'en'
                ? 'All passage permalinks support content negotiation (`Accept: text/markdown`) providing zero-JS raw source cards for direct LLM context injection.'
                : 'تدعم روابط المقتطعات التوافق المباشر مع روبوتات الذكاء الاصطناعي بتنسيق Markdown نقي مع التوثيق الكامل.'}
            </p>
            <div className="bg-stone-50 border border-stone-200 p-2 rounded text-[10px] font-mono text-emerald-800 flex items-center justify-between">
              <span>https://corpus.ai/p/:chunk_id</span>
              <span className="text-stone-400">200 OK</span>
            </div>
          </div>

        </div>

        {/* Bottom Bar */}
        <div className="bg-stone-50 border-t border-stone-200/80 py-4">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between gap-3 text-[11px] text-stone-500">
            <div className="flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
              <span>
                {lang === 'en'
                  ? '5.91M Passages Active • Read Replica Sync: 0.84ms'
                  : '٥.٩١ مليون مقتطف متاح • زمن الاستجابة: ٠.٨٤ ملـي ثانية'}
              </span>
            </div>
            <div>
              {lang === 'en'
                ? 'Designed for Classical Islamic Research & AI Grounding'
                : 'صُمم للبحث العلمي في التراث والتكاتف مع الذكاء الاصطناعي'}
            </div>
          </div>
        </div>
      </footer>

      {/* --- CITATION & MULTI-CHUNK SIBLING READING DRAWER (SLIDE-OVER) --- */}
      {drawerData && (
        <div className="fixed inset-0 z-50 overflow-hidden bg-stone-900/40 backdrop-blur-sm flex justify-end">
          <div className="w-full max-w-2xl bg-white h-full shadow-2xl flex flex-col animate-in slide-in-from-right duration-200">
            
            {/* Drawer Header */}
            <div className="p-4 border-b border-stone-200 flex items-center justify-between bg-stone-50">
              <div className="space-y-0.5">
                <div className="text-xs font-mono text-emerald-800 font-semibold flex items-center gap-2">
                  <span>CANONICAL NODE: #{drawerData.focusPassage.chunk_id}</span>
                  <span>•</span>
                  <span>Jaccard {(drawerData.focusPassage.continuity_score * 100).toFixed(0)}%</span>
                </div>
                <h3 className="text-sm font-bold text-stone-900">
                  {lang === 'en' ? drawerData.focusPassage.book_name_en : drawerData.focusPassage.book_name_ar}
                </h3>
              </div>
              <button
                onClick={() => setDrawerData(null)}
                className="p-1.5 rounded-lg hover:bg-stone-200 text-stone-600 transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Drawer Content: Full Sibling Window Context Stream */}
            <div className="flex-1 overflow-y-auto p-6 space-y-5 text-stone-800 font-serif leading-relaxed">
              
              {/* Metadata Breadcrumb & External Readers */}
              <div className="bg-stone-100 p-3.5 rounded-lg text-xs font-sans space-y-2">
                <div className="text-stone-500 font-semibold">
                  {lang === 'en' ? 'Section Taxonomy & Chapter:' : 'المسار البنائي والباب:'}
                </div>
                <div className="font-mono text-stone-800 text-[11px]">
                  {drawerData.focusPassage.breadcrumb}
                </div>
                <div className="text-[11px] text-stone-600">
                  {lang === 'en' ? drawerData.focusPassage.author_en : drawerData.focusPassage.author_ar} • {drawerData.focusPassage.vol_page}
                </div>

                {/* External Online Book Editions inside Drawer */}
                <div className="pt-2 border-t border-stone-200 flex items-center gap-2 flex-wrap">
                  <span className="text-[11px] font-semibold text-stone-600">
                    {lang === 'en' ? 'Primary Editions:' : 'المصادر الرقمية:'}
                  </span>
                  <a
                    href={drawerData.focusPassage.turath_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center gap-1 px-2.5 py-1 rounded bg-teal-50 hover:bg-teal-100 text-teal-900 border border-teal-200 text-xs font-medium transition-colors"
                  >
                    <BookOpen className="w-3 h-3 text-teal-700" />
                    <span>Turath.io ↗</span>
                  </a>
                  <a
                    href={drawerData.focusPassage.shamela_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center gap-1 px-2.5 py-1 rounded bg-amber-50 hover:bg-amber-100 text-amber-900 border border-amber-200 text-xs font-medium transition-colors"
                  >
                    <ArrowUpRight className="w-3 h-3 text-amber-700" />
                    <span>Shamela.ws ↗</span>
                  </a>
                </div>
              </div>

              {/* Top Action: "Load Earlier Chunks" */}
              <div className="text-center pt-2">
                <button
                  onClick={handleLoadMoreBefore}
                  className="inline-flex items-center gap-1.5 px-4 py-1.5 rounded-full bg-stone-100 hover:bg-stone-200 text-stone-700 text-xs font-sans font-semibold border border-stone-300 transition-all shadow-sm"
                >
                  <ChevronUp className="w-3.5 h-3.5 text-stone-500" />
                  <span>{lang === 'en' ? 'Load Earlier Chunks (N-3, N-4...)' : 'تحميل المقتطعات الأسبق (ن-٣، ن-٤...)'}</span>
                </button>
              </div>

              {/* PRECEDING CHUNKS STREAM */}
              <div className="space-y-3">
                {drawerData.beforeChunks.map((chunk) => (
                  <div key={chunk.chunk_id} className="space-y-1">
                    <span className="text-[10px] font-sans font-bold uppercase tracking-wider text-stone-400 block">
                      {lang === 'en' ? `Preceding Chunk (Order #${chunk.order})` : `مقتطف سياقي أسبق (ترتيب #${chunk.order})`}
                    </span>
                    <div className="p-4 bg-stone-50 rounded-lg text-sm text-stone-600 border border-stone-200 leading-relaxed">
                      {enableHighlight ? (
                        <HighlightedText 
                          text={lang === 'en' ? chunk.text_en : chunk.text_ar} 
                          lang={lang} 
                          isFocus={false} 
                        />
                      ) : (
                        lang === 'en' ? chunk.text_en : chunk.text_ar
                      )}
                    </div>
                  </div>
                ))}
              </div>

              {/* TARGET FOCUS CHUNK BLOCK */}
              <div className="space-y-1 my-4">
                <span className="text-[10px] font-sans font-bold uppercase tracking-wider text-emerald-800 flex items-center gap-1">
                  <CheckCircle2 className="w-3.5 h-3.5" />
                  {lang === 'en' ? `Target Focus Chunk (Order #${drawerData.focusPassage.order || 412})` : `المقتطف المستهدف محل البحث (ترتيب #${drawerData.focusPassage.order || 412})`}
                </span>
                <div className="p-5 bg-emerald-50 rounded-xl text-base text-stone-900 border-2 border-emerald-700 shadow-sm font-medium leading-relaxed">
                  {enableHighlight ? (
                    <HighlightedText 
                      text={lang === 'en' ? drawerData.focusPassage.raw_text_en : drawerData.focusPassage.raw_text_ar} 
                      lang={lang} 
                      isFocus={true} 
                    />
                  ) : (
                    lang === 'en' ? drawerData.focusPassage.raw_text_en : drawerData.focusPassage.raw_text_ar
                  )}
                </div>
              </div>

              {/* SUCCEEDING CHUNKS STREAM */}
              <div className="space-y-3">
                {drawerData.afterChunks.map((chunk) => (
                  <div key={chunk.chunk_id} className="space-y-1">
                    <span className="text-[10px] font-sans font-bold uppercase tracking-wider text-stone-400 block">
                      {lang === 'en' ? `Succeeding Chunk (Order #${chunk.order})` : `مقتطف سياقي لاحق (ترتيب #${chunk.order})`}
                    </span>
                    <div className="p-4 bg-stone-50 rounded-lg text-sm text-stone-600 border border-stone-200 leading-relaxed">
                      {enableHighlight ? (
                        <HighlightedText 
                          text={lang === 'en' ? chunk.text_en : chunk.text_ar} 
                          lang={lang} 
                          isFocus={false} 
                        />
                      ) : (
                        lang === 'en' ? chunk.text_en : chunk.text_ar
                      )}
                    </div>
                  </div>
                ))}
              </div>

              {/* Bottom Action: "Load Later Chunks" */}
              <div className="text-center pb-2">
                <button
                  onClick={handleLoadMoreAfter}
                  className="inline-flex items-center gap-1.5 px-4 py-1.5 rounded-full bg-stone-100 hover:bg-stone-200 text-stone-700 text-xs font-sans font-semibold border border-stone-300 transition-all shadow-sm"
                >
                  <ChevronDown className="w-3.5 h-3.5 text-stone-500" />
                  <span>{lang === 'en' ? 'Load Later Chunks (N+3, N+4...)' : 'تحميل المقتطعات اللاحقة (ن+٣، ن+٤...)'}</span>
                </button>
              </div>

              {/* Direct Permalink Box */}
              <div className="pt-2 border-t border-stone-200 space-y-2">
                <div className="text-xs font-sans font-bold text-stone-700">
                  {lang === 'en' ? 'Public Citation Permalink:' : 'رابط الاستشهاد الدائم الموثق:'}
                </div>
                <div className="flex items-center gap-2">
                  <input
                    type="text"
                    readOnly
                    value={`https://corpus.ai/p/${drawerData.focusPassage.chunk_id}`}
                    className="flex-1 bg-stone-100 border border-stone-300 rounded px-2.5 py-1.5 font-mono text-xs text-stone-700 select-all"
                  />
                  <button
                    onClick={() => handleCopyPassageForAI(drawerData.focusPassage)}
                    className="px-3 py-1.5 bg-stone-900 text-white rounded text-xs font-sans hover:bg-stone-800 transition-colors flex items-center gap-1.5"
                  >
                    <Copy className="w-3.5 h-3.5" />
                    <span>{lang === 'en' ? 'Copy' : 'نسخ'}</span>
                  </button>
                </div>
              </div>

            </div>

            {/* Drawer Footer */}
            <div className="p-4 border-t border-stone-200 bg-stone-50 flex items-center justify-between">
              <button
                onClick={() => setDrawerData(null)}
                className="px-4 py-2 border border-stone-300 bg-white hover:bg-stone-100 rounded-lg text-xs font-semibold text-stone-700 transition-colors"
              >
                {lang === 'en' ? 'Close Reader' : 'إغلاق نافذة القراءة'}
              </button>
              
              <button
                onClick={() => handleCopyPassageForAI(drawerData.focusPassage)}
                className="px-4 py-2 bg-emerald-800 hover:bg-emerald-900 text-white rounded-lg text-xs font-bold transition-colors flex items-center gap-2 shadow-sm"
              >
                <Sparkles className="w-3.5 h-3.5 text-emerald-300" />
                <span>{lang === 'en' ? 'Copy Citation Card' : 'نسخ بطاقة الاستشهاد'}</span>
              </button>
            </div>

          </div>
        </div>
      )}

      {/* --- TOAST NOTIFICATION --- */}
      {toastMessage && (
        <div className="fixed bottom-5 left-1/2 -translate-x-1/2 z-50 bg-stone-900 text-white text-xs font-medium px-4 py-2.5 rounded-lg shadow-lg flex items-center gap-2 animate-in fade-in slide-in-from-bottom-3 duration-200 border border-stone-700">
          <Check className="w-4 h-4 text-emerald-400" />
          <span>{toastMessage}</span>
        </div>
      )}

    </div>
  );
}