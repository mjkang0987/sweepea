// 로그인에서 돌아옴: 코드 + 쿠키의 PKCE 검증값으로 세션을 받아 sp_parent에 담는다
import type { APIRoute } from 'astro';
import { getBackend } from '../../lib/backend';
import { PKCE_COOKIE } from '../../lib/parent';
import { PARENT, writePass } from '../../lib/pass';

export const GET: APIRoute = async ({ url, cookies, redirect }) => {
  const code = url.searchParams.get('code');
  const verifier = cookies.get(PKCE_COOKIE)?.value;
  cookies.delete(PKCE_COOKIE, { path: '/auth' });
  if (!code || !verifier) return redirect('/login?e=1', 302);
  const pass = await getBackend().parentExchange(code, verifier);
  if (!pass) return redirect('/login?e=1', 302);
  writePass(cookies, pass, PARENT);
  return redirect('/home', 302);
};
