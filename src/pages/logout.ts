// 부모 로그아웃: Supabase 세션(갱신 토큰)을 끊고 쿠키를 지운다. 가족 기기 출입증은 그대로
import type { APIRoute } from 'astro';
import { getBackend } from '../lib/backend';
import { currentParent, PARENT } from '../lib/pass';

export const POST: APIRoute = async ({ cookies, redirect }) => {
  const pass = await currentParent(cookies).catch(() => null);
  if (pass) await getBackend().parentLogout(pass);
  cookies.delete(PARENT, { path: '/' });
  return redirect('/login', 303);
};
