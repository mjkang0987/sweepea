// 올리기 끝: 본문 {view, thumb, poster?}는 PUT이 돌려준 키. 이 사진의 키인지, R2에 있는지 확인하고 잰 크기로 완료 처리(서버 전용 함수)
import type { APIRoute } from 'astro';
import { env } from 'cloudflare:workers';
import { getBackend } from '../../../../lib/backend';
import { currentPass } from '../../../../lib/pass';
import { PARTS, UUID, backendErrorResponse, isMediaKey, json } from '../../../../lib/media';

export const POST: APIRoute = async ({ params, request, cookies }) => {
  const id = params.id ?? '';
  if (!UUID.test(id)) return json(404, { error: 'not_found' });
  const body = (await request.json().catch(() => null)) as Record<string, unknown> | null;
  try {
    const pass = await currentPass(cookies);
    if (!pass) return json(401, { error: 'login_required' });
    const backend = getBackend();
    const target = await backend.uploadTarget(pass, id);
    if (!target) return json(404, { error: 'not_found' });
    const parts = Object.keys(PARTS[target.kind]);
    const keys = parts.map((p) => (body && isMediaKey(body[p], target.family_id, id, p) ? (body[p] as string) : null));
    const heads = await Promise.all(keys.map((k) => (k ? env.MEDIA.head(k) : null)));
    const missing = parts.filter((_, i) => !heads[i]);
    if (missing.length) return json(409, { error: 'missing_parts', missing });
    const bytes = heads.reduce((n, h) => n + h!.size, 0);
    const k = (p: string) => keys[parts.indexOf(p)] as string;
    const ok = await backend.finishUpload(id, { view: k('view'), thumb: k('thumb'), poster: target.kind === 'video' ? k('poster') : null }, bytes);
    return ok ? json(200, { id, bytes }) : json(409, { error: 'already_done' });
  } catch (e) {
    return backendErrorResponse(e);
  }
};
