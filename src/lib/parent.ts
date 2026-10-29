// 부모 로그인·첫 화면 공통
import type { AstroCookies } from 'astro';
import { PARENT_PROVIDERS, SWEEPEA_BACKEND } from 'astro:env/server';
import { getBackend, type Pass, type ParentHome } from './backend';
import { currentParent, PARENT } from './pass';

export const PROVIDERS = {
  kakao: { label: '카카오로 계속하기', cls: 'sp-p__login--kakao' },
  // 네이버는 Supabase 기본 제공자가 아니다: 따로 연결하기 전엔 PARENT_PROVIDERS에 넣지 않는다
  naver: { label: '네이버로 계속하기', cls: 'sp-p__login--naver' },
  google: { label: 'Google로 계속하기', cls: 'sp-p__login--google' },
  apple: { label: 'Apple로 계속하기', cls: 'sp-p__login--apple' },
} as const;
export type Provider = keyof typeof PROVIDERS;

/** 켠 제공자만(시안 순서). 개발 mock이면 가짜 로그인 'dev'도 */
export function enabledProviders(): string[] {
  const on = (PARENT_PROVIDERS ?? '').split(',').map((x) => x.trim());
  const list: string[] = (Object.keys(PROVIDERS) as Provider[]).filter((p) => on.includes(p));
  if (!import.meta.env.PROD && SWEEPEA_BACKEND === 'mock') list.push('dev');
  return list;
}

const b64url = (bytes: Uint8Array) => btoa(String.fromCharCode(...bytes)).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');

/** PKCE: 검증값(쿠키에 보관)과 그 SHA-256(제공자에 보냄) */
export async function pkce(): Promise<{ verifier: string; challenge: string }> {
  const verifier = b64url(crypto.getRandomValues(new Uint8Array(32)));
  const challenge = b64url(new Uint8Array(await crypto.subtle.digest('SHA-256', new TextEncoder().encode(verifier))));
  return { verifier, challenge };
}

export const PKCE_COOKIE = 'sp_pkce';

/** 서울 날짜 YYYY-MM-DD */
export const seoulDate = (at: string | number | Date) => new Intl.DateTimeFormat('en-CA', { timeZone: 'Asia/Seoul' }).format(new Date(at));
/** 서울 오늘(새벽에 오늘 태어난 아이가 '미래'로 막히지 않게) */
export const seoulToday = () => seoulDate(new Date());

/** 있는 날짜(2월 31일 같은 값 거절)이고 2010-01-01~오늘(서울)이면 true */
export function validBirth(birth: string): boolean {
  if (!/^\d{4}-\d{2}-\d{2}$/.test(birth)) return false;
  const d = new Date(`${birth}T00:00:00Z`);
  return !Number.isNaN(d.getTime()) && d.toISOString().slice(0, 10) === birth && birth >= '2010-01-01' && birth <= seoulToday();
}
/** 계정 화면에 쓰는 로그인 제공자 이름 */
export const PROVIDER_NAMES: Record<string, string> = { kakao: '카카오', naver: '네이버', google: 'Google', apple: 'Apple' };
export const INTRO_COOKIE = 'sp_intro';
/** 엄빠 함께 관리 초대: 로그인을 건너 콜백까지 가는 '코드:역할'(15분) */
export const JOIN_COOKIE = 'sp_join';
/** 초대 받기 실패 → 초대 화면 안내(?e=). DB raise 글로 가른다(23505를 family_exists·parents_full이 같이 써서) */
export const joinError = (e: { reason?: string; message: string }) =>
  ({ family_exists: 'other', role_taken: 'role', parents_full: 'full', is_device: 'device' } as Record<string, string>)[e.reason ?? e.message] ?? 'expired';

/** 부모 화면 들어오기: 로그인 안 했으면 소개(처음)·로그인, 설정 전이면 처음 설정으로 */
export async function loadParent(
  cookies: AstroCookies,
  opts: { needFamily: boolean; allowClosing?: boolean } = { needFamily: true },
): Promise<{ redirect: string } | { pass: Pass; home: ParentHome }> {
  const pass = await currentParent(cookies);
  if (!pass) return { redirect: cookies.has(INTRO_COOKIE) ? '/login' : '/start' };
  const home = await getBackend().parentHome(pass);
  if (opts.needFamily && !home.family_id) return { redirect: '/setup' };
  // 탈퇴 유예 중이면 되살리기 화면만
  if (home.closing && !opts.allowClosing) return { redirect: '/restore' };
  if (!opts.needFamily && home.family_id) return { redirect: '/home' };
  return { pass, home };
}

/** 부모 세션 끝내기: 갱신 토큰을 끊고(실패해도) 쿠키를 지운다. 가족 기기 출입증은 그대로 */
export async function logoutParent(cookies: AstroCookies) {
  const pass = await currentParent(cookies).catch(() => null);
  if (pass) await getBackend().parentLogout(pass);
  cookies.delete(PARENT, { path: '/' });
}

/** 작별 화면 주소: 지울 날(서울 날짜)을 들고 간다 */
export const goodbyeHref = (deleteAfter: string) =>
  `/goodbye?on=${seoulDate(deleteAfter)}`;

/** 그룹 비밀번호(숫자 4자리)·힌트 검사. 문제가 있으면 안내 문구 */
export function pinError(password: string, hint: string): string | null {
  if (!/^[0-9]{4}$/.test(password)) return '숫자 4자리를 써 주세요.';
  if (hint.includes(password)) return '힌트에 비밀번호를 그대로 쓰지 말아 주세요.';
  return null;
}
