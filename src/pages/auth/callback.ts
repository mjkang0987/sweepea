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
  // 제공자·Supabase가 거절하면 이유(error_description)를 주소에 남겨 원인을 볼 수 있게(158)
  const why = url.searchParams.get('error_description') ?? url.searchParams.get('error');
  if (why) return redirect(`/login?e=1&why=${encodeURIComponent(why.slice(0, 200))}`, 302);
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
      // 초대받아 들어온 엄빠는 약관 동의가 아직 없으니 /agree를 거쳐 '함께 관리해요' 안내로(152)
      return redirect('/agree?joined=1', 302);
    } catch (e) {
      if (!(e instanceof BackendError) || e.status >= 500) throw e;
      return redirect(`/join/${joinCode}?e=${joinError(e)}`, 302);
    }
  }
  return redirect('/home', 302);
};
