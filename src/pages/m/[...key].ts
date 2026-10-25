// 사진·영상 파일 전달: 서명된 주소만. 영상 이어 보기용 Range(206) 지원
import type { APIRoute } from 'astro';
import { env } from 'cloudflare:workers';
import { verifyMediaUrl } from '../../lib/signed';

const U = '[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}';
const KEY = new RegExp(`^${U}/${U}/(view|thumb|poster)-${U}$`);
const notFound = () => new Response('Not found', { status: 404, headers: { 'cache-control': 'no-store' } });

export const GET: APIRoute = async ({ params, url, request }) => {
  const key = params.key ?? '';
  if (!KEY.test(key)) return notFound();
  const left = await verifyMediaUrl(key, url.searchParams.get('e'), url.searchParams.get('s'));
  if (!left) return notFound();
  const obj = await env.MEDIA.get(key, { range: request.headers, onlyIf: request.headers });
  if (!obj) return notFound();
  const headers = new Headers();
  obj.writeHttpMetadata(headers);
  headers.set('etag', obj.httpEtag);
  headers.set('accept-ranges', 'bytes');
  headers.set('cache-control', `private, max-age=${left}`);
  // 올린 형식(이미지·영상)으로만 보이게: 다른 형식으로 해석하거나 스크립트로 쓰지 못하게
  headers.set('x-content-type-options', 'nosniff');
  headers.set('content-security-policy', "default-src 'none'; sandbox");
  if (!('body' in obj)) return new Response(null, { status: 304, headers });
  const r = obj.range as { offset?: number; length?: number; suffix?: number } | undefined;
  if (r && request.headers.has('range')) {
    const offset = r.suffix !== undefined ? obj.size - r.suffix : (r.offset ?? 0);
    const length = r.suffix !== undefined ? r.suffix : (r.length ?? obj.size - offset);
    headers.set('content-range', `bytes ${offset}-${offset + length - 1}/${obj.size}`);
    headers.set('content-length', String(length));
    return new Response(obj.body, { status: 206, headers });
  }
  headers.set('content-length', String(obj.size));
  return new Response(obj.body, { headers });
};
