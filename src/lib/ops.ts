// 운영자 화면(164) 순수 함수: 기간 읽기, Cloudflare Access 도장 확인, 방문으로 셀 요청 고르기. 부수 효과 없이 단위 검사로 본다

export const PERIODS = { today: '오늘', '7d': '7일', '30d': '30일', '90d': '90일' } as const;
export type PeriodKey = keyof typeof PERIODS | 'custom';
export interface Period {
  key: PeriodKey;
  /** 서울 날짜 YYYY-MM-DD, 끝 포함 */
  from: string;
  to: string;
  days: number;
}
const DAYS: Record<keyof typeof PERIODS, number> = { today: 1, '7d': 7, '30d': 30, '90d': 90 };
/** DB 함수가 받는 최대 길이(sp_ops_*의 400일) */
export const MAX_DAYS = 400;

const DAY = 86400_000;
const t = (d: string) => Date.parse(`${d}T00:00:00Z`);
const iso = (ms: number) => new Date(ms).toISOString().slice(0, 10);
export const addDays = (d: string, n: number) => iso(t(d) + n * DAY);
const validDate = (d: string | null): d is string => !!d && /^\d{4}-\d{2}-\d{2}$/.test(d) && iso(t(d)) === d;

/** 주소의 ?p= 또는 ?from=&to=. 틀린 값·미래·너무 긴 기간은 기본 7일 */
export function parsePeriod(q: URLSearchParams, today: string): Period {
  const from = q.get('from'), to = q.get('to');
  if (validDate(from) && validDate(to) && from <= to && to <= today && (t(to) - t(from)) / DAY < MAX_DAYS) {
    return { key: 'custom', from, to, days: (t(to) - t(from)) / DAY + 1 };
  }
  const p = q.get('p');
  const key = p && p in DAYS ? (p as keyof typeof PERIODS) : '7d';
  return { key, from: addDays(today, 1 - DAYS[key]), to: today, days: DAYS[key] };
}

/** 링크에 달고 다닐 기간 주소 조각(기본 7일이면 빈 값) */
export function periodQuery(p: Period): string {
  if (p.key === 'custom') return `from=${p.from}&to=${p.to}`;
  return p.key === '7d' ? '' : `p=${p.key}`;
}
export const withPeriod = (path: string, p: Period, extra = '') => {
  const q = [periodQuery(p), extra].filter(Boolean).join('&');
  return q ? `${path}?${q}` : path;
};

const b64urlBytes = (s: string) => Uint8Array.from(atob(s.replace(/-/g, '+').replace(/_/g, '/') + '==='.slice((s.length + 3) % 4)), (c) => c.charCodeAt(0));
const b64urlJson = (s: string) => JSON.parse(new TextDecoder().decode(b64urlBytes(s)));

export interface AccessJwk {
  kid: string;
  kty: string;
  n: string;
  e: string;
  alg?: string;
}

/** Cloudflare Access가 붙여 보내는 도장(Cf-Access-Jwt-Assertion) 확인: RS256 서명, 발급처(팀 주소), 받는 쪽(aud), 기한.
 *  workers.dev 주소처럼 Access를 안 거친 요청은 도장이 없어서 여기서 막힌다 */
export async function verifyAccessJwt(token: string | null, o: { team: string; aud: string; keys: AccessJwk[]; nowSec?: number }): Promise<boolean> {
  if (!token) return false;
  const parts = token.split('.');
  if (parts.length !== 3) return false;
  try {
    const head = b64urlJson(parts[0]) as { alg?: string; kid?: string };
    const body = b64urlJson(parts[1]) as { iss?: string; aud?: string | string[]; exp?: number; nbf?: number };
    if (head.alg !== 'RS256') return false;
    const jwk = o.keys.find((k) => k.kid === head.kid);
    if (!jwk) return false;
    const key = await crypto.subtle.importKey('jwk', { kty: jwk.kty, n: jwk.n, e: jwk.e, alg: 'RS256', ext: true }, { name: 'RSASSA-PKCS1-v1_5', hash: 'SHA-256' }, false, ['verify']);
    const ok = await crypto.subtle.verify('RSASSA-PKCS1-v1_5', key, b64urlBytes(parts[2]), new TextEncoder().encode(`${parts[0]}.${parts[1]}`));
    if (!ok) return false;
    const now = o.nowSec ?? Date.now() / 1000;
    const auds = Array.isArray(body.aud) ? body.aud : [body.aud];
    return body.iss === `https://${o.team}` && auds.includes(o.aud) && typeof body.exp === 'number' && body.exp > now && (body.nbf === undefined || body.nbf <= now + 60);
  } catch {
    return false;
  }
}

/** 운영자 명단(쉼표로 적은 사용자 id) */
export const inList = (list: string | undefined, id: string | null) => !!id && (list ?? '').split(',').map((x) => x.trim()).filter(Boolean).includes(id);

// 카톡·검색·메신저 미리보기 봇은 방문으로 세지 않는다
const BOT = /bot|crawl|spider|scrap|preview|facebookexternalhit|slurp|kakaotalk-scrap|whatsapp|telegram|discord|slack|headless|lighthouse/i;
export const isBot = (ua: string | null) => !ua || BOT.test(ua);

/** 이 요청을 방문으로 셀까: 가족 링크면 그 단계, 앨범·엄빠 화면이면 'user', 아니면 null(운영·API·사진 전달·로그인 오가기 등) */
export function visitTarget(method: string, path: string): { kind: 'link'; code: string; step: 'link' | 'link_pw' } | { kind: 'user' } | null {
  if (method !== 'GET') return null;
  const m = path.match(/^\/i\/([A-Za-z0-9]{8})(\/password)?\/?$/);
  if (m) return { kind: 'link', code: m[1], step: m[2] ? 'link_pw' : 'link' };
  if (/^\/(ops|api|m|auth|login|logout|install|_)(\/|$)/.test(path) || path === '/' || /\.[a-z0-9]+$/i.test(path)) return null;
  return { kind: 'user' };
}

/** 숫자 1,234 */
export const nf = (n: number) => n.toLocaleString('ko-KR');
/** 가족방 번호 앞 8자리(이름 대신) */
export const shortId = (id: string) => id.slice(0, 8);
/** 서울 날짜 → '오늘'·'어제'·'11월 4일' */
export function dayLabel(day: string | null, today: string): string {
  if (!day) return '없음';
  if (day === today) return '오늘';
  if (day === addDays(today, -1)) return '어제';
  const [, m, d] = day.split('-').map(Number);
  return `${m}월 ${d}일`;
}
