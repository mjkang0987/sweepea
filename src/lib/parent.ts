// 부모 로그인·첫 화면 공통
import type { AstroCookies } from 'astro';
import { PARENT_PROVIDERS, SWEEPEA_BACKEND } from 'astro:env/server';
import { getBackend, type Pass, type ParentHome } from './backend';
import { currentParent } from './pass';

export const PROVIDERS = {
  kakao: { label: '카카오로 계속하기', cls: 'sp-p__login--kakao' },
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
