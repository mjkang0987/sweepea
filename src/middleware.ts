// 모든 화면 응답에 공통 보안 헤더. 이미 정한 헤더(사진 전달 /m의 sandbox CSP 등)는 덮지 않는다
import { defineMiddleware } from 'astro:middleware';
import { PARENT, PASS } from './lib/pass';
import { parsePass, passStale, REFRESH_EARLY } from './lib/passcheck';
import { getBackend } from './lib/backend';
import { isBot, screenName, visitTarget } from './lib/ops';

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

// 방문 세기(164): 30분 넘게 쉬었다 다시 연 것만 한 번. 쿠키가 있으면 안 세고, 셀 화면을 열 때마다 30분을 다시 채운다.
// 링크 단계(누구세요·비밀번호)와 앨범·엄빠 화면은 쿠키를 따로: 같이 쓰면 링크를 열고 30분 안에 들어간 다음 단계가 안 세진다.
// 자세한 기록(179): 앨범·엄빠 쿠키 값은 방문마다 만든 무작위 열쇠. 쿠키가 있으면 그 방문에 화면 이름을 덧붙인다(옛 값 '1'은 다음 방문부터)
const VISIT = { user: 'sp_v', link: 'sp_vl', link_pw: 'sp_vp' } as const;
const visitCookie = ([name, value]: [string, string]) => `${name}=${value}; Max-Age=1800; Path=/; HttpOnly; SameSite=Lax${import.meta.env.PROD ? '; Secure' : ''}`;
const VISIT_KEY = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/;

export const onRequest = defineMiddleware(async (ctx, next) => {
  // www로 들어오면 같은 경로로 대표 주소에(가족 링크·로그인 쿠키가 주소에 묶이므로 하나로). 308: 폼 POST도 그대로 간다
  if (ctx.url.hostname.startsWith('www.')) {
    const to = new URL(ctx.url);
    to.hostname = to.hostname.slice(4);
    return new Response(null, { status: 308, headers: { location: to.href } });
  }
  // 미리 받기(크게 보기, 131)는 로그인 표를 갱신하지 않는다(133): 갱신할 때가 된 출입증이면 미리 받기만 그만둔다.
  // 갱신은 쓴 갱신 토큰을 바꾸므로, 버려진 미리 받기 응답의 쿠키를 브라우저가 안 담으면 다음 요청이 옛 토큰으로 세션이 끊길 수 있어서
  // 그 화면이 실제로 쓰는 출입증만 본다(엄빠 크게 보기 /view = 엄빠, 가족 /album = 가족 기기). 안 쓰는 쪽이 오래돼 미리 받기가 늘 꺼지지 않게
  const uses = ctx.url.pathname.startsWith('/view/') ? [PARENT] : ctx.url.pathname.startsWith('/album') ? [PASS] : [PARENT, PASS];
  if (/prefetch/i.test(ctx.request.headers.get('sec-purpose') ?? '') && uses.some((n) => passStale(ctx.cookies.get(n)?.value))) {
    return new Response(null, { status: 503, headers: { 'cache-control': 'no-store' } });
  }
  let res = await next();
  // 방문 세기가 어떻게 실패해도 화면은 그대로
  let visit: [string, string] | null = null;
  try {
    visit = countVisit(ctx, res);
  } catch (e) {
    console.error('방문 세기 실패', e instanceof Error ? e.message : e);
  }
  // 검색에는 대표 첫 화면과 자주 묻는 질문(181)만: 가족 링크·앨범·사진·설정은 색인하지 않게(robots.txt로 막으면 카톡 미리보기도 막힐 수 있어 머리로)
  const robots: [string, string][] = ['/', '/guide'].includes(ctx.url.pathname) ? [] : [['x-robots-tag', 'noindex, nofollow']];
  const add = () => {
    for (const [k, v] of [...HEADERS, ...robots]) if (!res.headers.has(k)) res.headers.set(k, v);
    if (visit) res.headers.append('set-cookie', visitCookie(visit));
  };
  try {
    add();
  } catch {
    // Response.redirect 등은 헤더가 잠겨 있어 복사해서 쓴다
    res = new Response(res.body, res);
    add();
  }
  return res;
});

type Ctx = Parameters<Parameters<typeof defineMiddleware>[0]>[0];
/** 방문으로 셀 화면이면 기록을 응답 뒤로 맡기고(waitUntil) 새로 쓸 쿠키 [이름, 값]. 기록 실패는 화면에 영향 없음 */
function countVisit(ctx: Ctx, res: Response): [string, string] | null {
  const target = visitTarget(ctx.request.method, ctx.url.pathname);
  if (!target || res.status !== 200 || !res.headers.get('content-type')?.includes('text/html')) return null;
  if (isBot(ctx.request.headers.get('user-agent')) || /prefetch/i.test(ctx.request.headers.get('sec-purpose') ?? '')) return null;
  const cookie = VISIT[target.kind === 'link' ? target.step : 'user'];
  const had = ctx.cookies.get(cookie)?.value;
  if (target.kind === 'link' && had) return [cookie, had];
  let job: Promise<unknown>;
  let value = '1';
  if (target.kind === 'link') job = getBackend().noteLinkVisit(target.code, target.step);
  else {
    // 갱신할 때가 된 출입증은 이번엔 안 센다(쿠키도 안 써서 다음 화면에서 셈)
    const now = Date.now() / 1000;
    const passes = [PARENT, PASS].map((n) => parsePass(ctx.cookies.get(n)?.value)).filter((p) => p && p.expiresAt - REFRESH_EARLY > now);
    if (!passes.length) return had ? [cookie, had] : null;
    const screen = screenName(ctx.url.pathname);
    if (had && !VISIT_KEY.test(had)) return [cookie, had];
    value = had ?? crypto.randomUUID();
    job = Promise.all(passes.map((p) => (had ? getBackend().visitTouch(p!, value, screen) : getBackend().visitStart(p!, value, screen))));
  }
  const done = job.catch((e) => console.error('방문 기록 실패', e instanceof Error ? e.message : e));
  const cf = (ctx.locals as { cfContext?: { waitUntil(p: Promise<unknown>): void } }).cfContext;
  if (cf) cf.waitUntil(done);
  return [cookie, value];
}
