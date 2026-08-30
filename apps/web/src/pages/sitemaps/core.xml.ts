import type { APIRoute } from 'astro';

export const GET: APIRoute = async ({ site }) => {
  const baseUrl = site?.toString().replace(/\/$/, '') || 'https://openbayan.mustaqbal.or.id';
  const today = new Date().toISOString().split('T')[0];

  const coreRoutes = [
    { path: '/', priority: '1.0', changefreq: 'daily' },
    { path: '/search', priority: '0.9', changefreq: 'daily' },
    { path: '/about', priority: '0.7', changefreq: 'monthly' },
  ];

  const urls = coreRoutes
    .map(
      (r) => `  <url>
    <loc>${baseUrl}${r.path}</loc>
    <lastmod>${today}</lastmod>
    <changefreq>${r.changefreq}</changefreq>
    <priority>${r.priority}</priority>
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
