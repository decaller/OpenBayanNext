import type { APIRoute } from 'astro';
import { getApiUrl } from '../../lib/api';

export const GET: APIRoute = async ({ site }) => {
  const baseUrl = site?.toString().replace(/\/$/, '') || 'https://openbayan.mustaqbal.or.id';
  const today = new Date().toISOString().split('T')[0];

  let books: any[] = [];
  try {
    const apiUrl = getApiUrl(true);
    const res = await fetch(`${apiUrl}/sitemaps/books`);
    if (res.ok) {
      books = await res.json();
    }
  } catch {
    // Fallback if API is unreachable
  }

  const urls = books
    .map(
      (b) => `  <url>
    <loc>${baseUrl}/search?q=${encodeURIComponent(b.title_ar)}</loc>
    <lastmod>${today}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.8</priority>
  </url>`
    )
    .join('\n');

  const xml = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
${urls}
</urlset>`;

  return new Response(xml, {
    headers: {
      'Content-Type': 'application/xml; charset=utf-8',
      'Cache-Control': 'public, max-age=86400, s-maxage=86400'
    }
  });
};
