// 파일 넣기: 올린 사람만, 올리는 중인 사진에만. 형식·크기를 확인하고 R2에 그대로 흘려 넣는다
import type { APIRoute } from 'astro';
import { env } from 'cloudflare:workers';
import { getBackend } from '../../../../lib/backend';
import { currentPass } from '../../../../lib/pass';
import { PARTS, UUID, json, mediaKey } from '../../../../lib/media';

export const PUT: APIRoute = async ({ params, request, cookies }) => {
  const id = params.id ?? '';
  const part = params.part ?? '';
  if (!UUID.test(id)) return json(404, { error: 'not_found' });
  const pass = await currentPass(cookies);
  if (!pass) return json(401, { error: 'login_required' });
  const target = await getBackend().uploadTarget(pass, id);
  const spec = target && Object.hasOwn(PARTS[target.kind], part) ? PARTS[target.kind][part] : null;
  if (!target || !spec) return json(404, { error: 'not_found' });
  const type = (request.headers.get('content-type') ?? '').split(';')[0].trim().toLowerCase();
  if (!spec.types.includes(type)) return json(415, { error: 'unsupported_type' });
  const length = Number(request.headers.get('content-length'));
  if (!Number.isInteger(length) || length <= 0) return json(411, { error: 'length_required' });
  if (length > spec.max) return json(413, { error: 'too_large' });
  if (!request.body) return json(400, { error: 'bad_request' });
  const key = mediaKey(target.family_id, id, part);
  const obj = await env.MEDIA.put(key, request.body, { httpMetadata: { contentType: type } });
  // 길이를 속여 보낸 경우 버린다
  if (!obj || obj.size !== length) {
    await env.MEDIA.delete(key);
    return json(400, { error: 'bad_request' });
  }
  return json(201, { size: obj.size });
};
