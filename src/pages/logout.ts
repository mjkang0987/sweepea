// 부모 로그아웃: 세션 쿠키만 지운다(가족 기기 출입증은 그대로). Supabase 세션 무효화는 실제 연결 때
import type { APIRoute } from 'astro';
import { PARENT } from '../lib/pass';

export const POST: APIRoute = ({ cookies, redirect }) => {
  cookies.delete(PARENT, { path: '/' });
  return redirect('/login', 303);
};
