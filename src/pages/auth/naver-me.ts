// 네이버 로그인 사용자 정보 중계(158). 네이버는 {resultcode, response:{id,…}}로 감싸 오는데
// Supabase 직접 설정 제공자(custom:naver)는 맨 위 sub만 읽어서, 받은 토큰으로 네이버에 묻고 id만 sub로 편다.
// 이메일 등은 앱이 안 써서 넘기지 않는다(Supabase에서 '이메일 없이 허용' 켬)
import type { APIRoute } from 'astro';

export const GET: APIRoute = async ({ request }) => {
  const auth = request.headers.get('authorization') ?? '';
  if (!/^Bearer \S+$/i.test(auth)) return new Response(null, { status: 401 });
  const res = await fetch('https://openapi.naver.com/v1/nid/me', { headers: { authorization: auth } }).catch(() => null);
  if (!res) return new Response(null, { status: 502 });
  const body = (await res.json().catch(() => null)) as { resultcode?: string; response?: { id?: unknown } } | null;
  const id = body?.resultcode === '00' ? body.response?.id : undefined;
  if (!res.ok || typeof id !== 'string' || !id) return new Response(null, { status: 401 });
  return Response.json({ sub: id }, { headers: { 'cache-control': 'no-store' } });
};
