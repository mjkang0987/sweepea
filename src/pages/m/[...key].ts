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
  let obj: R2Object | R2ObjectBody | null;
  try {
    obj = await env.MEDIA.get(key, { range: request.headers, onlyIf: request.headers });
  } catch {
    // 못 주는 범위·여러 범위(또는 R2 일시 오류): 범위·조건을 무시하고 파일 전체(200)를 한 번 더 시도
    obj = await env.MEDIA.get(key);
    request = new Request(request, { headers: new Headers() });
  }
  if (!obj) return notFound();
  const headers = new Headers();
  obj.writeHttpMetadata(headers);
  headers.set('etag', obj.httpEtag);
  headers.set('accept-ranges', 'bytes');
  headers.set('cache-control', `private, max-age=${left}`);
  // 올린 형식(이미지·영상)으로만 보이게: 다른 형식으로 해석하거나 스크립트로 쓰지 못하게
  headers.set('x-content-type-options', 'nosniff');
  headers.set('content-security-policy', "default-src 'none'; sandbox");
  if (!('body' in obj)) {
    // If-Match·If-Unmodified-Since가 먼저(RFC 9110)
    const pre = request.headers.has('if-match') || request.headers.has('if-unmodified-since');
    return new Response(null, { status: pre ? 412 : 304, headers });
  }
  const r = obj.range as { offset?: number; length?: number; suffix?: number } | undefined;
  if (r && request.headers.has('range')) {
    // 파일 크기 안으로 자른다(끝을 넘는 요청·큰 suffix)
    const start = r.suffix !== undefined ? Math.max(0, obj.size - r.suffix) : (r.offset ?? 0);
    const end = Math.min(obj.size, r.length !== undefined ? start + r.length : obj.size) - 1;
    if (start >= obj.size) {
      await obj.body.cancel();
      return new Response(null, { status: 416, headers: { 'content-range': `bytes */${obj.size}`, 'cache-control': 'no-store' } });
    }
    headers.set('content-range', `bytes ${start}-${end}/${obj.size}`);
    headers.set('content-length', String(end - start + 1));
    return new Response(obj.body, { status: 206, headers });
  }
  headers.set('content-length', String(obj.size));
  return new Response(obj.body, { headers });
};
