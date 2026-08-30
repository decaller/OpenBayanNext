import type { APIRoute } from 'astro';
import { getApiUrl } from '../../lib/api';

export const GET: APIRoute = async ({ params, site }) => {
  const part = parseInt(params.part || '1', 10);
  if (isNaN(part) || part < 1) {
    return new Response('Invalid partition number', { status: 400 });
  }

  const baseUrl = site?.toString().replace(/\/$/, '') || 'https://openbayan.mustaqbal.or.id';
  const today = new Date().toISOString().split('T')[0];

  let chunkIds: number[] = [];
  try {
    const apiUrl = getApiUrl(true);
    const res = await fetch(`${apiUrl}/sitemaps/chunks?part=${part}`);
    if (!res.ok) {
      return new Response('Failed to generate sitemap partition', { status: 502 });
    }
    chunkIds = await res.json();
  } catch (err: any) {
    return new Response(`Error fetching chunk IDs: ${err.message}`, { status: 500 });
  }

  const urls = chunkIds
    .map(
      (id) => `  <url>
    <loc>${baseUrl}/p/${id}</loc>
    <lastmod>${today}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.7</priority>
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
