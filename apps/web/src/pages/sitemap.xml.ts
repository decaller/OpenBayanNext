import type { APIRoute } from 'astro';
import { getApiUrl } from '../lib/api';

export const GET: APIRoute = async ({ site }) => {
  const baseUrl = site?.toString().replace(/\/$/, '') || 'https://openbayan.mustaqbal.or.id';
  
  let numPartitions = 2;
  try {
    const apiUrl = getApiUrl(true);
    const res = await fetch(`${apiUrl}/sitemaps/info`);
    if (res.ok) {
      const info = await res.json();
      numPartitions = info.num_chunk_partitions || 2;
    }
  } catch {
    // Default fallback to 2 partitions
  }

  const chunkSitemaps = Array.from({ length: numPartitions }, (_, i) => i + 1)
    .map(
      (p) => `  <sitemap>
    <loc>${baseUrl}/sitemaps/chunks-${p}.xml</loc>
    <lastmod>${new Date().toISOString().split('T')[0]}</lastmod>
  </sitemap>`
    )
    .join('\n');

  const xml = `<?xml version="1.0" encoding="UTF-8"?>
<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <sitemap>
    <loc>${baseUrl}/sitemaps/core.xml</loc>
    <lastmod>${new Date().toISOString().split('T')[0]}</lastmod>
  </sitemap>
  <sitemap>
    <loc>${baseUrl}/sitemaps/books.xml</loc>
    <lastmod>${new Date().toISOString().split('T')[0]}</lastmod>
  </sitemap>
${chunkSitemaps}
</sitemapindex>`;

  return new Response(xml, {
    headers: {
      'Content-Type': 'application/xml; charset=utf-8',
      'Cache-Control': 'public, max-age=86400, s-maxage=86400'
    }
  });
};
