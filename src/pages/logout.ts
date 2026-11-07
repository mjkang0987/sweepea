// 부모 로그아웃: Supabase 세션(갱신 토큰)을 끊고 쿠키를 지운다. 가족 기기 출입증은 그대로
import type { APIRoute } from 'astro';
import { logoutParent } from '../lib/parent';

export const POST: APIRoute = async ({ cookies, redirect }) => {
  await logoutParent(cookies);
  return redirect('/login', 303);
};
