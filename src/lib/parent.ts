// 부모 로그인·첫 화면 공통
import type { AstroCookies } from 'astro';
import { PARENT_PROVIDERS, SWEEPEA_BACKEND } from 'astro:env/server';
import { getBackend, type Pass, type ParentHome } from './backend';
import { currentParent } from './pass';

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

/** 서울 날짜 YYYY-MM-DD(새벽에 오늘 태어난 아이가 '미래'로 막히지 않게) */
export const seoulToday = () => new Intl.DateTimeFormat('en-CA', { timeZone: 'Asia/Seoul' }).format(new Date());

/** 있는 날짜(2월 31일 같은 값 거절)이고 2010-01-01~오늘(서울)이면 true */
export function validBirth(birth: string): boolean {
  if (!/^\d{4}-\d{2}-\d{2}$/.test(birth)) return false;
  const d = new Date(`${birth}T00:00:00Z`);
  return !Number.isNaN(d.getTime()) && d.toISOString().slice(0, 10) === birth && birth >= '2010-01-01' && birth <= seoulToday();
}
/** 계정 화면에 쓰는 로그인 제공자 이름 */
export const PROVIDER_NAMES: Record<string, string> = { kakao: '카카오', naver: '네이버', google: 'Google', apple: 'Apple' };
export const INTRO_COOKIE = 'sp_intro';

/** 부모 화면 들어오기: 로그인 안 했으면 소개(처음)·로그인, 설정 전이면 처음 설정으로 */
export async function loadParent(
  cookies: AstroCookies,
  opts: { needFamily: boolean } = { needFamily: true },
): Promise<{ redirect: string } | { pass: Pass; home: ParentHome }> {
  const pass = await currentParent(cookies);
  if (!pass) return { redirect: cookies.has(INTRO_COOKIE) ? '/login' : '/start' };
  const home = await getBackend().parentHome(pass);
  if (opts.needFamily && !home.family_id) return { redirect: '/setup' };
  if (!opts.needFamily && home.family_id) return { redirect: '/home' };
  return { pass, home };
}
