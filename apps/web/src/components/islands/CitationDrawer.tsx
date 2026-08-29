import React, { useEffect, useState, useRef } from 'react';
import { useStore } from '@nanostores/react';
import { 
  $isDrawerOpen, 
  $activeSection, 
  $fontSize, 
  closeChapterDrawer 
} from '../../stores/workspace';
import { PUBLIC_API_URL, type ChapterStreamResponse, type ChapterChunkItem } from '../../lib/api';

export const CitationDrawer: React.FC = () => {
  const isOpen = useStore($isDrawerOpen);
  const section = useStore($activeSection);
  const fontSize = useStore($fontSize);

  const [loading, setLoading] = useState(false);
  const [data, setData] = useState<ChapterStreamResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);
  const drawerRef = useRef<HTMLDivElement>(null);

  // Fetch chapter stream when drawer opens for a section
  useEffect(() => {
    if (!isOpen || !section) return;

    let isMounted = true;
    setLoading(true);
    setError(null);

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

        // Auto-scroll to target focus chunk after render
        if (section.focusChunkId) {
          setTimeout(() => {
            const targetEl = document.getElementById(`drawer-chunk-${section.focusChunkId}`);
            if (targetEl) {
              targetEl.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }
          }, 150);
        }
      })
      .catch((err) => {
        if (!isMounted) return;
        setError('تعذر تحميل نص الباب. تأكد من تشغيل خادم الواجهة البرمجية.');
        setLoading(false);
      });

    return () => {
      isMounted = false;
    };
  }, [isOpen, section]);

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
    setTimeout(() => setCopied(false), 2000);
  };

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
        <div className="p-4 border-b border-base-200 bg-base-100/90 backdrop-blur flex items-center justify-between gap-2">
          <div className="flex-1 overflow-hidden">
            <h3 className="font-bold text-base sm:text-lg text-emerald-800 dark:text-emerald-400 truncate">
              {section?.sectionTitle}
            </h3>
            <p className="text-xs text-base-content/60 truncate">
              {section?.breadcrumb}
            </p>
          </div>

          {/* Controls: Font Resizing, Copy, Close */}
          <div className="flex items-center gap-1.5 flex-shrink-0">
            {/* Font Size Toggle */}
            <div className="join bg-base-200/80 rounded-lg p-0.5">
              <button
                type="button"
                onClick={() => $fontSize.set('sm')}
                className={`join-item btn btn-xs ${fontSize === 'sm' ? 'btn-active bg-emerald-800 text-white' : 'btn-ghost'}`}
                title="خط أصغر"
              >
                A-
              </button>
              <button
                type="button"
                onClick={() => $fontSize.set('base')}
                className={`join-item btn btn-xs ${fontSize === 'base' ? 'btn-active bg-emerald-800 text-white' : 'btn-ghost'}`}
                title="خط عادي"
              >
                A
              </button>
              <button
                type="button"
                onClick={() => $fontSize.set('lg')}
                className={`join-item btn btn-xs ${fontSize === 'lg' ? 'btn-active bg-emerald-800 text-white' : 'btn-ghost'}`}
                title="خط كبير"
              >
                A+
              </button>
            </div>

            {/* Copy Citation Button */}
            <button
              type="button"
              onClick={handleCopyCitation}
              className="btn btn-ghost btn-circle btn-sm text-base-content/70"
              title="نسخ العزو"
            >
              {copied ? (
                <span className="text-xs text-success font-bold">✓</span>
              ) : (
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                </svg>
              )}
            </button>

            {/* Close Drawer Button */}
            <button
              type="button"
              onClick={closeChapterDrawer}
              className="btn btn-ghost btn-circle btn-sm text-base-content/70 hover:text-error"
              title="إغلاق (Esc)"
            >
              ✕
            </button>
          </div>
        </div>

        {/* Main Chapter Content Stream */}
        <div className="flex-1 overflow-y-auto p-5 sm:p-8 bg-[#fdfcf9] dark:bg-[#151719]">
          {loading && (
            <div className="flex flex-col items-center justify-center h-64 gap-3 text-base-content/60">
              <span className="loading loading-spinner loading-lg text-emerald-800"></span>
              <span className="text-sm">جاري تحميل الباب كاملاً...</span>
            </div>
          )}

          {error && (
            <div className="alert alert-error my-8 shadow-sm">
              <span>{error}</span>
            </div>
          )}

          {data && !loading && (
            <div className="max-w-2xl mx-auto space-y-6">
              {/* Section Title Banner */}
              <div className="text-center py-6 border-b-2 border-emerald-800/20 mb-8">
                <span className="badge badge-lg badge-neutral font-bold text-xs mb-2">مطالعة كاملة</span>
                <h1 className="text-2xl sm:text-3xl font-bold text-emerald-900 dark:text-emerald-300 font-sans">
                  {data.section_title}
                </h1>
                <p className="text-sm text-base-content/60 mt-1 font-sans">
                  {data.book_name} ({data.total_chunks} صفحة متصلة)
                </p>
              </div>

              {/* Continuous Stream of Pages */}
              {data.chunks.map((chunk) => {
                const isFocus = chunk.chunk_id === section?.focusChunkId;
                return (
                  <article
                    key={chunk.chunk_id}
                    id={`drawer-chunk-${chunk.chunk_id}`}
                    className={`relative p-5 rounded-2xl transition-all duration-300 ${
                      isFocus 
                        ? 'bg-emerald-50/80 dark:bg-emerald-950/30 border-2 border-emerald-700/40 shadow-sm' 
                        : 'bg-base-100 border border-base-200/70'
                    }`}
                  >
                    {/* Page Number Tag */}
                    <div className="flex items-center justify-between text-xs text-base-content/50 font-mono mb-2 pb-1 border-b border-base-200/40">
                      <span className="font-bold text-emerald-800 dark:text-emerald-400">
                        {chunk.volume_page}
                      </span>
                      {isFocus && (
                        <span className="badge badge-xs badge-success text-[10px]">
                          الموضع المطابق
                        </span>
                      )}
                    </div>

                    {/* Classical Text Body */}
                    <div className={`arabic-matn text-base-content/90 ${fontClass}`}>
                      {chunk.raw_text}
                    </div>

                    {/* Footnotes if present */}
                    {chunk.footnotes && (
                      <div className="mt-4 pt-3 border-t border-dashed border-base-200 text-xs font-sans text-base-content/60 bg-base-200/30 rounded-lg p-3 leading-relaxed">
                        <span className="font-bold text-base-content/80">الهوامش: </span>
                        <span>{chunk.footnotes}</span>
                      </div>
                    )}
                  </article>
                );
              })}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
