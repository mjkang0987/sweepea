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

export const onRequest = defineMiddleware(async (ctx, next) => {
  // www로 들어오면 같은 경로로 대표 주소에(가족 링크·로그인 쿠키가 주소에 묶이므로 하나로). 308: 폼 POST도 그대로 간다
  if (ctx.url.hostname.startsWith('www.')) {
    const to = new URL(ctx.url);
    to.hostname = to.hostname.slice(4);
    return new Response(null, { status: 308, headers: { location: to.href } });
  }
  let res = await next();
  // 검색에는 대표 첫 화면만: 가족 링크·앨범·사진·설정은 색인하지 않게(robots.txt로 막으면 카톡 미리보기도 막힐 수 있어 머리로)
  const robots: [string, string][] = ctx.url.pathname === '/' ? [] : [['x-robots-tag', 'noindex, nofollow']];
  const add = () => { for (const [k, v] of [...HEADERS, ...robots]) if (!res.headers.has(k)) res.headers.set(k, v); };
  try {
    add();
  } catch {
    // Response.redirect 등은 헤더가 잠겨 있어 복사해서 쓴다
    res = new Response(res.body, res);
    add();
  }
  return res;
});
