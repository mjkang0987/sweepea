// 앱(iOS·안드로이드)용 사진 파일 주소(177, 93 ②): Authorization: Bearer <Supabase 출입증>, { ids } → { urls: { <id>: { view, thumb, poster } } }.
// 그 출입증으로 사진을 읽어 볼 수 있는 것만(DB 권한), 못 보는·없는 id는 빠진다. 서명 비밀은 서버에만. 쿠키는 안 쓴다
import type { APIRoute } from 'astro';
import { getBackend } from '../../../lib/backend';
import { UUID, backendErrorResponse, bearerPass, json } from '../../../lib/media';
import { signedMediaUrl } from '../../../lib/signed';

export const POST: APIRoute = async ({ request, url }) => {
  const pass = bearerPass(request);
  if (!pass) return json(401, { error: 'login_required' });
  // id 100개는 4KB 남짓: 큰 본문은 읽기 전에 거절
  if (Number(request.headers.get('content-length') ?? 0) > 8192) return json(413, { error: 'too_large' });
  const body = (await request.json().catch(() => null)) as { ids?: unknown } | null;
  const ids = body?.ids;
  if (!Array.isArray(ids) || !ids.length || ids.length > 100 || !ids.every((x) => typeof x === 'string' && UUID.test(x))) {
    return json(400, { error: 'bad_request' });
  }
  try {
    const items = await getBackend().listMedia(pass, { ids: [...new Set(ids as string[])], limit: ids.length });
    const abs = async (key: string) => new URL(await signedMediaUrl(key), url).href;
    const urls = Object.fromEntries(
      await Promise.all(items.map(async (m) => [m.id, { view: await abs(m.view_key), thumb: await abs(m.thumb_key), poster: m.poster_key ? await abs(m.poster_key) : null }])),
    );
    return json(200, { urls });
  } catch (e) {
    return backendErrorResponse(e);
  }
};
