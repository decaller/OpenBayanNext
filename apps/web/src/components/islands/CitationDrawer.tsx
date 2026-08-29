import React, { useEffect, useState, useRef } from 'react';
import { useStore } from '@nanostores/react';
import { 
  $isDrawerOpen, 
  $activeSection, 
  $fontSize, 
  $currentLang,
  closeChapterDrawer,
  showToast
} from '../../stores/workspace';
import { PUBLIC_API_URL, type ChapterStreamResponse, type ChapterChunkItem } from '../../lib/api';
import { translations, formatAIPassagePrompt } from '../../lib/i18n';

export const CitationDrawer: React.FC = () => {
  const isOpen = useStore($isDrawerOpen);
  const section = useStore($activeSection);
  const fontSize = useStore($fontSize);
  const currentLang = useStore($currentLang);
  const t = translations[currentLang] || translations.ar;

  const [loading, setLoading] = useState(false);
  const [data, setData] = useState<ChapterStreamResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);

  // Dynamic pagination states for earlier/later expansion
  const [loadingEarlier, setLoadingEarlier] = useState(false);
  const [loadingLater, setLoadingLater] = useState(false);
  const [noMoreEarlier, setNoMoreEarlier] = useState(false);
  const [noMoreLater, setNoMoreLater] = useState(false);

  const drawerRef = useRef<HTMLDivElement>(null);

  // Fetch initial chapter stream when drawer opens for a section
  useEffect(() => {
    if (!isOpen || !section) return;

    let isMounted = true;
    setLoading(true);
    setError(null);
    setNoMoreEarlier(false);
    setNoMoreLater(false);

    const url = `${PUBLIC_API_URL}/books/${section.bookId}/sections/${encodeURIComponent(section.sectionId)}/chunks`;
    fetch(url)
      .then((res) => {
        if (!res.ok) throw new Error(`HTTP Error: ${res.status}`);
        return res.json();
      })
      .then((json: ChapterStreamResponse) => {
        if (!isMounted) return;
        setData(json);
        setLoading(false);

        // Auto-scroll to target focus chunk after initial render
        if (section.focusChunkId) {
          setTimeout(() => {
            const targetEl = document.getElementById(`drawer-chunk-${section.focusChunkId}`);
            if (targetEl) {
              targetEl.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }
          }, 200);
        }
      })
      .catch(() => {
        if (!isMounted) return;
        setError(currentLang === 'en' 
          ? 'Failed to load chapter text. Please check backend API server.'
          : currentLang === 'id'
          ? 'Gagal memuat teks bab. Pastikan server API backend aktif.'
          : 'تعذر تحميل نص الباب. تأكد من تشغيل خادم الواجهة البرمجية.');
        setLoading(false);
      });

    return () => {
      isMounted = false;
    };
  }, [isOpen, section, currentLang]);

  if (!isOpen) return null;

  const fontClass = {
    sm: 'text-base leading-relaxed',
    base: 'text-lg leading-loose',
    lg: 'text-xl leading-loose',
    xl: 'text-2xl leading-loose',
  }[fontSize];

  const handleCopyCitation = () => {
    if (!section) return;
    const citation = `${section.sectionTitle} - [${section.breadcrumb}]`;
    navigator.clipboard.writeText(citation);
    setCopied(true);
    showToast(t.copied);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleCopyPassageForAI = (chunk: { chunk_id: number; volume_page: string; raw_text: string; footnotes?: string | null }) => {
    if (!section) return;
    const prompt = formatAIPassagePrompt({
      chunk_id: chunk.chunk_id,
      book_name: section.sectionTitle,
      volume_page: chunk.volume_page,
      breadcrumb: section.breadcrumb,
      raw_text: chunk.raw_text,
      footnotes: chunk.footnotes,
    }, currentLang);

    navigator.clipboard.writeText(prompt);
    showToast(t.copied);
  };

  // Load earlier chunks before the first rendered chunk
  const handleLoadEarlier = async () => {
    if (!data || data.chunks.length === 0 || loadingEarlier) return;
    const firstChunk = data.chunks[0];
    setLoadingEarlier(true);

    try {
      const res = await fetch(`${PUBLIC_API_URL}/chunks/${firstChunk.chunk_id}/expand?direction=before&limit=5`);
      if (!res.ok) throw new Error('Failed to fetch earlier chunks');
      const earlierChunks: ChapterChunkItem[] = await res.json();

      if (earlierChunks.length === 0) {
        setNoMoreEarlier(true);
      } else {
        setData({
          ...data,
          chunks: [...earlierChunks, ...data.chunks],
          total_chunks: data.total_chunks + earlierChunks.length,
        });
      }
    } catch {
      showToast(currentLang === 'en' ? 'No earlier chunks found' : currentLang === 'id' ? 'Tidak ada kutipan sebelumnya' : 'لا توجد مواضع سابقة');
    } finally {
      setLoadingEarlier(false);
    }
  };

  // Load subsequent chunks after the last rendered chunk
  const handleLoadLater = async () => {
    if (!data || data.chunks.length === 0 || loadingLater) return;
    const lastChunk = data.chunks[data.chunks.length - 1];
    setLoadingLater(true);

    try {
      const res = await fetch(`${PUBLIC_API_URL}/chunks/${lastChunk.chunk_id}/expand?direction=after&limit=5`);
      if (!res.ok) throw new Error('Failed to fetch later chunks');
      const laterChunks: ChapterChunkItem[] = await res.json();

      if (laterChunks.length === 0) {
        setNoMoreLater(true);
      } else {
        setData({
          ...data,
          chunks: [...data.chunks, ...laterChunks],
          total_chunks: data.total_chunks + laterChunks.length,
        });
      }
    } catch {
      showToast(currentLang === 'en' ? 'No subsequent chunks found' : currentLang === 'id' ? 'Tidak ada kutipan selanjutnya' : 'لا توجد مواضع لاحقة');
    } finally {
      setLoadingLater(false);
    }
  };

  const turathBookUrl = section ? `https://turath.io/book/${section.bookId}` : '#';
  const shamelaBookUrl = section ? `https://shamela.ws/book/${section.bookId}` : '#';

  return (
    <div className="fixed inset-0 z-50 overflow-hidden flex justify-end font-sans">
      {/* Backdrop overlay */}
      <div 
        className="fixed inset-0 bg-black/50 backdrop-blur-xs transition-opacity"
        onClick={closeChapterDrawer}
      />

      {/* Slide-Out Drawer Panel */}
      <div 
        ref={drawerRef}
        className="relative w-full max-w-3xl bg-base-100 h-full shadow-2xl z-10 flex flex-col border-l border-base-300"
      >
        {/* Header Bar */}
        <div className="p-4 sm:p-5 border-b border-base-200 bg-base-100/95 backdrop-blur flex items-start justify-between gap-4">
          <div className="flex-1 overflow-hidden space-y-1">
            <div className="flex items-center gap-2 text-xs font-mono font-bold text-emerald-700 dark:text-emerald-400">
              <span>{t.canonicalNode} #{section?.focusChunkId || section?.sectionId}</span>
              <span>•</span>
              <span>{data?.total_chunks || 0} {t.connectedPages}</span>
            </div>
            <h2 className="font-bold text-lg sm:text-xl text-base-content tracking-tight truncate">
              {section?.sectionTitle}
            </h2>
          </div>

          {/* Close Drawer Button */}
          <button
            type="button"
            onClick={closeChapterDrawer}
            className="btn btn-ghost btn-circle btn-sm text-base-content/70 hover:text-error"
            title={t.closeDrawer}
          >
            ✕
          </button>
        </div>

        {/* Main Chapter Content Stream */}
        <div className="flex-1 overflow-y-auto p-4 sm:p-6 bg-base-100 space-y-5">
          
          {/* Section Taxonomy & Chapter Box */}
          <div className="bg-base-200/60 border border-base-300/80 rounded-2xl p-4 sm:p-5 space-y-3 font-sans text-xs">
            <div className="font-bold text-base-content/70 uppercase tracking-wider text-[11px]">
              {t.sectionTaxonomy}
            </div>
            <div className="font-mono text-emerald-800 dark:text-emerald-300 text-xs bg-base-100 p-2.5 rounded-lg border border-base-300/50">
              {section?.breadcrumb}
            </div>
            <div className="flex flex-wrap items-center justify-between gap-2 pt-1">
              <div className="text-base-content/60">
                <span>Book ID: {section?.bookId}</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-base-content/50">{t.primaryEditions}</span>
                <a
                  href={turathBookUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="badge badge-sm badge-outline hover:badge-primary text-[11px] gap-1 transition-colors"
                >
                  {t.turathLink}
                </a>
                <a
                  href={shamelaBookUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="badge badge-sm badge-outline hover:badge-primary text-[11px] gap-1 transition-colors"
                >
                  {t.shamelaLink}
                </a>
              </div>
            </div>
          </div>

          {/* Top Button: Load Earlier Chunks (N-3, N-4...) */}
          {data && data.chunks.length > 0 && (
            <div className="pt-2">
              {noMoreEarlier ? (
                <div className="text-center py-2 text-xs text-base-content/50 border border-dashed border-base-300 rounded-xl">
                  {t.noEarlierChunks}
                </div>
              ) : (
                <button
                  type="button"
                  onClick={handleLoadEarlier}
                  disabled={loadingEarlier}
                  className="w-full btn btn-sm btn-outline border-dashed border-base-300 hover:border-emerald-600 text-base-content/70 hover:text-emerald-800 text-xs font-sans rounded-xl py-2 flex items-center justify-center gap-2 transition-all"
                >
                  {loadingEarlier ? (
                    <span className="loading loading-spinner loading-xs text-emerald-700"></span>
                  ) : (
                    <>
                      <span className="text-base font-bold">⌃</span>
                      <span>{t.loadEarlierChunks}</span>
                    </>
                  )}
                </button>
              )}
            </div>
          )}

          {loading && (
            <div className="flex flex-col items-center justify-center h-64 gap-3 text-base-content/60">
              <span className="loading loading-spinner loading-lg text-emerald-800"></span>
              <span className="text-sm">{t.loadingChapter}</span>
            </div>
          )}

          {error && (
            <div className="alert alert-error my-8 shadow-sm">
              <span>{error}</span>
            </div>
          )}

          {/* Passages List */}
          {data && !loading && (
            <div className="space-y-6">
              {data.chunks.map((chunk) => {
                const isFocus = chunk.chunk_id === section?.focusChunkId;
                const isPreceding = section?.focusChunkId && chunk.chunk_id < section.focusChunkId;

                return (
                  <div key={chunk.chunk_id} className="space-y-1.5">
                    {/* Position Label Tag */}
                    <div className="text-[11px] font-mono font-bold flex items-center justify-between px-1">
                      {isFocus ? (
                        <span className="text-emerald-700 dark:text-emerald-400 flex items-center gap-1 font-sans">
                          {t.focusChunkLabel} (#{chunk.chunk_id})
                        </span>
                      ) : isPreceding ? (
                        <span className="text-base-content/50 font-sans">
                          {t.precedingChunk} (#{chunk.chunk_id})
                        </span>
                      ) : (
                        <span className="text-base-content/50 font-sans">
                          {t.succeedingChunk} (#{chunk.chunk_id})
                        </span>
                      )}

                      <span className="font-mono text-base-content/60">{chunk.volume_page}</span>
                    </div>

                    {/* Chunk Card */}
                    <article
                      id={`drawer-chunk-${chunk.chunk_id}`}
                      className={`p-5 rounded-2xl transition-all duration-300 ${
                        isFocus 
                          ? 'bg-emerald-50/70 dark:bg-emerald-950/20 border-2 border-emerald-600 shadow-sm' 
                          : 'bg-base-100 border border-base-200/80 shadow-2xs'
                      }`}
                    >
                      {/* Top bar inside chunk */}
                      <div className="flex items-center justify-between pb-2 mb-2 border-b border-base-200/50 text-xs">
                        <span className="font-mono font-bold text-emerald-800 dark:text-emerald-400">
                          {chunk.volume_page}
                        </span>
                        <button
                          type="button"
                          onClick={() => handleCopyPassageForAI(chunk)}
                          className="btn btn-ghost btn-xs text-base-content/60 hover:text-emerald-800 gap-1 font-sans"
                        >
                          <svg className="w-3 h-3 text-emerald-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                          </svg>
                          <span>{t.copyForAI}</span>
                        </button>
                      </div>

                      {/* Classical Text Body (Amiri Font) */}
                      <div className={`arabic-matn text-base-content/90 ${fontClass}`} dir="rtl">
                        {chunk.raw_text}
                      </div>

                      {/* Footnotes if present */}
                      {chunk.footnotes && (
                        <div className="mt-4 pt-3 border-t border-dashed border-base-200 text-xs font-sans text-base-content/60 bg-base-200/30 rounded-lg p-3 leading-relaxed" dir="rtl">
                          <span className="font-bold text-base-content/80">{t.footnotesTitle} </span>
                          <span>{chunk.footnotes}</span>
                        </div>
                      )}
                    </article>
                  </div>
                );
              })}
            </div>
          )}

          {/* Bottom Button: Load Subsequent Chunks (N+3, N+4...) */}
          {data && data.chunks.length > 0 && (
            <div className="pt-3 pb-6">
              {noMoreLater ? (
                <div className="text-center py-2 text-xs text-base-content/50 border border-dashed border-base-300 rounded-xl">
                  {t.noLaterChunks}
                </div>
              ) : (
                <button
                  type="button"
                  onClick={handleLoadLater}
                  disabled={loadingLater}
                  className="w-full btn btn-sm btn-outline border-dashed border-base-300 hover:border-emerald-600 text-base-content/70 hover:text-emerald-800 text-xs font-sans rounded-xl py-2 flex items-center justify-center gap-2 transition-all"
                >
                  {loadingLater ? (
                    <span className="loading loading-spinner loading-xs text-emerald-700"></span>
                  ) : (
                    <>
                      <span className="text-base font-bold">⌄</span>
                      <span>{t.loadLaterChunks}</span>
                    </>
                  )}
                </button>
              )}
            </div>
          )}

        </div>

        {/* Sticky Bottom Action Bar */}
        <div className="p-4 border-t border-base-200 bg-base-100 flex items-center justify-between gap-3 font-sans">
          <button
            type="button"
            onClick={closeChapterDrawer}
            className="btn btn-sm btn-ghost text-base-content/70 hover:text-base-content"
          >
            {t.closeDrawer}
          </button>

          <button
            type="button"
            onClick={handleCopyCitation}
            className="btn btn-sm bg-emerald-800 hover:bg-emerald-900 text-white font-bold gap-1.5 shadow-sm border-0"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
            </svg>
            <span>{copied ? t.copied : t.copyCitation}</span>
          </button>
        </div>
      </div>
    </div>
  );
};
