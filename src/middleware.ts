// 모든 화면 응답에 공통 보안 헤더. 이미 정한 헤더(사진 전달 /m의 sandbox CSP 등)는 덮지 않는다
import { defineMiddleware } from 'astro:middleware';

const HEADERS: [string, string][] = [
  ['x-content-type-options', 'nosniff'],
  // 가족 링크(/i/코드)·서명된 사진 주소가 다른 사이트로 새지 않게
  ['referrer-policy', 'no-referrer'],
  // 다른 사이트가 틀에 넣어 누르게 하는 공격 막기(오래된 브라우저는 x-frame-options)
  ['x-frame-options', 'DENY'],
  ['content-security-policy', "frame-ancestors 'none'; base-uri 'self'; object-src 'none'; form-action 'self'"],
  ['permissions-policy', 'camera=(), microphone=(), geolocation=(), payment=()'],
];
if (import.meta.env.PROD) HEADERS.push(['strict-transport-security', 'max-age=31536000']);

export const onRequest = defineMiddleware(async (_ctx, next) => {
  let res = await next();
  const add = () => { for (const [k, v] of HEADERS) if (!res.headers.has(k)) res.headers.set(k, v); };
  try {
    add();
  } catch {
    // Response.redirect 등은 헤더가 잠겨 있어 복사해서 쓴다
    res = new Response(res.body, res);
    add();
  }
  return res;
});
