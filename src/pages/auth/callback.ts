// 로그인에서 돌아옴: 코드 + 쿠키의 PKCE 검증값으로 세션을 받아 sp_parent에 담는다
import type { APIRoute } from 'astro';
import { getBackend } from '../../lib/backend';
import { BackendError } from '../../lib/backend';
import { JOIN_COOKIE, joinError, PKCE_COOKIE } from '../../lib/parent';
import { PARENT, writePass } from '../../lib/pass';

export const GET: APIRoute = async ({ url, cookies, redirect }) => {
  const code = url.searchParams.get('code');
  const verifier = cookies.get(PKCE_COOKIE)?.value;
  cookies.delete(PKCE_COOKIE, { path: '/auth' });
  if (!code || !verifier) return redirect('/login?e=1', 302);
  const pass = await getBackend().parentExchange(code, verifier);
  if (!pass) return redirect('/login?e=1', 302);
  writePass(cookies, pass, PARENT);
  // 엄빠 함께 관리 초대를 받으러 온 로그인이면 바로 받는다(실패하면 초대 화면에서 이유)
  const [joinCode, joinRole] = (cookies.get(JOIN_COOKIE)?.value ?? '').split(':');
  cookies.delete(JOIN_COOKIE, { path: '/' });
  if (/^[A-Za-z0-9]{8}$/.test(joinCode ?? '') && (joinRole === 'mom' || joinRole === 'dad')) {
    try {
      await getBackend().acceptParentInvite(pass, joinCode, joinRole);
      return redirect('/home?joined=1', 302);
    } catch (e) {
      if (!(e instanceof BackendError) || e.status >= 500) throw e;
      return redirect(`/join/${joinCode}?e=${joinError(e)}`, 302);
    }
  }
  return redirect('/home', 302);
};
