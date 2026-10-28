// 홈 화면에 두기 안내 답: 알겠어요(1년 숨김)·다음에 할게요(7일)·엄마아빠에게 부탁하기(들어가 있는 가족방마다)
// 스크립트가 그 자리에서 보내면(x-sp-inplace) 이동 없이 204(다 됨)·409(부탁할 곳 없음·실패), 안내 판은 스크립트가 치운다
import type { APIRoute } from 'astro';
import { BackendError, getBackend } from '../lib/backend';
import { isOpen } from '../lib/families';
import { INSTALL_AGES, INSTALL_COOKIE } from '../lib/install';
import { currentPass } from '../lib/pass';

export const POST: APIRoute = async ({ request, cookies, redirect }) => {
  const form = await request.formData().catch(() => null);
  const back = String(form?.get('back') ?? '');
  // 앨범으로만 돌아간다(다른 주소로 보내는 데 쓰이지 않게)
  const to = /^\/album(\/[0-9a-f-]{36})?(\?[\w=&%.-]*)?$/.test(back) ? back : '/album';
  const action = String(form?.get('do') ?? '');
  const inplace = request.headers.get('x-sp-inplace') === '1';
  const done = (status = 204) => (inplace ? new Response(null, { status }) : redirect(to, 303));
  const set = (v: string, maxAge: number) => cookies.set(INSTALL_COOKIE, v, { path: '/', sameSite: 'lax', secure: import.meta.env.PROD, maxAge });
  if (action === 'ok') set('ok', INSTALL_AGES.ok);
  else if (action === 'later') set('later', INSTALL_AGES.later);
  else if (action === 'ask') {
    const pass = await currentPass(cookies);
    if (!pass) return inplace ? new Response(null, { status: 401 }) : redirect('/', 303);
    const b = getBackend();
    try {
      const open = (await b.me(pass)).families.filter(isOpen);
      // 들어가 있는 가족방이 없으면 부탁할 곳이 없다(알림도 띄우지 않는다)
      if (!open.length) return done(409);
      await Promise.all(open.map((f) => b.requestInstallHelp(pass, f.family_id)));
    } catch (e) {
      if (!(e instanceof BackendError)) throw e;
      return done(409);
    }
    set('asked', INSTALL_AGES.later);
    if (inplace) return done();
    cookies.set(`${INSTALL_COOKIE}_msg`, '1', { path: '/', sameSite: 'lax', secure: import.meta.env.PROD, maxAge: 60 });
  }
  return done();
};
