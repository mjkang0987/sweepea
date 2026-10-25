// 올리기 끝: 필요한 파일이 다 있는지 R2에서 확인하고, 잰 크기로 완료 처리(서버 전용 함수)
import type { APIRoute } from 'astro';
import { env } from 'cloudflare:workers';
import { getBackend } from '../../../../lib/backend';
import { currentPass } from '../../../../lib/pass';
import { PARTS, UUID, json, mediaKey } from '../../../../lib/media';

export const POST: APIRoute = async ({ params, cookies }) => {
  const id = params.id ?? '';
  if (!UUID.test(id)) return json(404, { error: 'not_found' });
  const pass = await currentPass(cookies);
  if (!pass) return json(401, { error: 'login_required' });
  const backend = getBackend();
  const target = await backend.uploadTarget(pass, id);
  if (!target) return json(404, { error: 'not_found' });
  const parts = Object.keys(PARTS[target.kind]);
  const heads = await Promise.all(parts.map((p) => env.MEDIA.head(mediaKey(target.family_id, id, p))));
  const missing = parts.filter((_, i) => !heads[i]);
  if (missing.length) return json(409, { error: 'missing_parts', missing });
  const bytes = heads.reduce((n, h) => n + h!.size, 0);
  const key = (p: string) => mediaKey(target.family_id, id, p);
  const ok = await backend.finishUpload(id, { view: key('view'), thumb: key('thumb'), poster: target.kind === 'video' ? key('poster') : null }, bytes);
  return ok ? json(200, { id, bytes }) : json(409, { error: 'already_done' });
};
