// 로그인 시작: PKCE 검증값을 쿠키에 두고 Supabase 인증으로 보낸다
import type { APIRoute } from 'astro';
import { getBackend } from '../../lib/backend';
import { enabledProviders, PKCE_COOKIE, pkce } from '../../lib/parent';

export const GET: APIRoute = async ({ params, url, cookies, redirect }) => {
  const provider = params.provider ?? '';
  if (!enabledProviders().includes(provider)) return redirect('/login', 302);
  const { verifier, challenge } = await pkce();
  cookies.set(PKCE_COOKIE, verifier, { path: '/auth', httpOnly: true, secure: import.meta.env.PROD, sameSite: 'lax', maxAge: 600 });
  return redirect(getBackend().parentAuthorizeUrl(provider, `${url.origin}/auth/callback`, challenge), 302);
};
