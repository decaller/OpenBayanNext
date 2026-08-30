import type { APIRoute } from 'astro';
import { getApiUrl, type ChunkDetailResponse } from '../../lib/api';
import { sanitizeSnippetText } from '../../lib/highlighter';

export const GET: APIRoute = async ({ params }) => {
  const chunkId = parseInt(params.id || '0', 10);
  if (!chunkId || chunkId < 1) {
    return new Response('Invalid Chunk ID', { status: 400 });
  }

  try {
    const apiUrl = getApiUrl(true);
    const res = await fetch(`${apiUrl}/chunks/${chunkId}`);
    if (!res.ok) {
      return new Response('Passage Not Found', { status: 404 });
    }

    const chunk: ChunkDetailResponse = await res.json();
    const cleanText = sanitizeSnippetText(chunk.raw_text);
    const cleanFootnotes = chunk.footnotes ? sanitizeSnippetText(chunk.footnotes) : null;

    const markdown = `---
title: "${chunk.book_name} - ${chunk.section_title}"
book: "${chunk.book_name}"
author: "${chunk.author_name}"
author_death_hijri: ${chunk.author_death_hijri ?? 'null'}
category: "${chunk.category_name}"
volume_page: "${chunk.volume_page}"
breadcrumb: "${chunk.breadcrumb}"
permalink: "https://openbayan.mustaqbal.or.id/p/${chunk.chunk_id}"
---

# ${chunk.section_title}
**الكتاب:** ${chunk.book_name} | **المؤلف:** ${chunk.author_name} (ت ${chunk.author_death_hijri} هـ) | **الموضع:** ${chunk.volume_page}
**المسار:** ${chunk.breadcrumb}

## النص
${cleanText}

${cleanFootnotes ? `## الحواشي والتعليقات\n${cleanFootnotes}\n` : ''}
`;

    return new Response(markdown, {
      headers: {
        'Content-Type': 'text/markdown; charset=utf-8',
        'Cache-Control': 'public, max-age=604800, s-maxage=31536000, stale-while-revalidate=86400'
      }
    });
  } catch (err: any) {
    return new Response(`Error fetching passage: ${err.message}`, { status: 500 });
  }
};
