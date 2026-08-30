import type { APIRoute } from 'astro';
import { getApiUrl } from '../lib/api';

export const GET: APIRoute = async () => {
  const rawUrl = getApiUrl(true);
  let baseUrl = 'http://127.0.0.1:8001';
  try {
    const u = new URL(rawUrl);
    baseUrl = `${u.protocol}//${u.host}`;
  } catch (e) {}

  try {
    let res = await fetch(`${baseUrl}/docs`);
    if (!res.ok && baseUrl !== 'http://127.0.0.1:8001') {
      res = await fetch('http://127.0.0.1:8001/docs');
    }
    const html = await res.text();
    return new Response(html, {
      status: 200,
      headers: {
        'Content-Type': 'text/html; charset=utf-8',
      },
    });
  } catch (e) {
    return new Response(`<h1>Swagger Docs Unavailable</h1><p>${e}</p>`, {
      status: 502,
      headers: { 'Content-Type': 'text/html; charset=utf-8' },
    });
  }
};
