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
    let res = await fetch(`${baseUrl}/openapi.json`);
    if (!res.ok && baseUrl !== 'http://127.0.0.1:8001') {
      res = await fetch('http://127.0.0.1:8001/openapi.json');
    }
    const data = await res.text();
    return new Response(data, {
      status: 200,
      headers: {
        'Content-Type': 'application/json; charset=utf-8',
        'Access-Control-Allow-Origin': '*',
      },
    });
  } catch (e) {
    return new Response(JSON.stringify({ error: 'OpenAPI Schema Unavailable' }), {
      status: 502,
      headers: { 'Content-Type': 'application/json' },
    });
  }
};
