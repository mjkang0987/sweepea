// 큰 영상 나눠 올리기(Worker 요청 한도 100MB를 넘는 영상 원본): R2 multipart로 조각마다 PUT, 끝나면 합친다. 돌려준 키를 done에 보낸다.
// POST {action:'create', type, size} → {key, uploadId} / PUT ?key=&upload=&n= (조각) → {n, etag} / POST {action:'complete'|'abort', key, uploadId, parts?}
import type { APIRoute } from 'astro';
import { env } from 'cloudflare:workers';
import { getBackend } from '../../../../lib/backend';
import { BIG_VIDEO, PARTS, UUID, backendErrorResponse, isMediaKey, json, newMediaKey, withUploader } from '../../../../lib/media';

// 한 편 최대 크기를 넘는 조각 번호는 받지 않는다(2GB ÷ 50MB = 41)
const MAX_PARTS = Math.ceil(BIG_VIDEO.max / BIG_VIDEO.part);

/** 올린 사람의 올리는 중인 영상인지. 아니면 오류 응답 */
async function videoTarget(cookies: Parameters<APIRoute>[0]['cookies'], id: string) {
  if (!UUID.test(id)) return json(404, { error: 'not_found' });
  const r = await withUploader(cookies, (pass) => getBackend().uploadTarget(pass, id));
  if (r === 'login') return json(401, { error: 'login_required' });
  if (!r || r.value.kind !== 'video') return json(404, { error: 'not_found' });
  return r.value;
}

export const POST: APIRoute = async ({ params, request, cookies }) => {
  const id = params.id ?? '';
  const body = (await request.json().catch(() => null)) as Record<string, unknown> | null;
  try {
    const target = await videoTarget(cookies, id);
    if (target instanceof Response) return target;
    if (body?.action === 'create') {
      const type = String(body.type ?? '').toLowerCase();
      const size = Number(body.size);
      if (!PARTS.video.view.types.includes(type)) return json(415, { error: 'unsupported_type' });
      if (!Number.isInteger(size) || size <= 0) return json(400, { error: 'bad_request' });
      if (size > BIG_VIDEO.max) return json(413, { error: 'too_large' });
      const key = newMediaKey(target.family_id, id, 'view');
      const up = await env.MEDIA.createMultipartUpload(key, { httpMetadata: { contentType: type } });
      return json(201, { key, uploadId: up.uploadId, partSize: BIG_VIDEO.part });
    }
    const key = body?.key;
    const uploadId = typeof body?.uploadId === 'string' ? body.uploadId : '';
    if (!isMediaKey(key, target.family_id, id, 'view') || !uploadId) return json(400, { error: 'bad_request' });
    const up = env.MEDIA.resumeMultipartUpload(key as string, uploadId);
    if (body?.action === 'abort') {
      await up.abort().catch(() => undefined);
      return json(200, { ok: true });
    }
    if (body?.action !== 'complete' || !Array.isArray(body.parts) || body.parts.length < 1 || body.parts.length > MAX_PARTS) return json(400, { error: 'bad_request' });
    const parts = body.parts.map((p) => ({ partNumber: Number((p as Record<string, unknown>)?.partNumber), etag: String((p as Record<string, unknown>)?.etag ?? '') }));
    if (parts.some((p, i) => p.partNumber !== i + 1 || !p.etag)) return json(400, { error: 'bad_request' });
    let size: number;
    try {
      size = (await up.complete(parts)).size;
    } catch {
      // 조각이 빠졌거나 크기가 맞지 않으면 합치기가 실패한다
      return json(400, { error: 'incomplete_body' });
    }
    if (size > BIG_VIDEO.max) {
      await env.MEDIA.delete(key as string);
      return json(413, { error: 'too_large' });
    }
    return json(201, { key, size });
  } catch (e) {
    return backendErrorResponse(e);
  }
};

export const PUT: APIRoute = async ({ params, request, cookies, url }) => {
  const id = params.id ?? '';
  try {
    const target = await videoTarget(cookies, id);
    if (target instanceof Response) return target;
    const key = url.searchParams.get('key');
    const uploadId = url.searchParams.get('upload') ?? '';
    const n = Number(url.searchParams.get('n'));
    if (!isMediaKey(key, target.family_id, id, 'view') || !uploadId || !Number.isInteger(n) || n < 1 || n > MAX_PARTS) return json(400, { error: 'bad_request' });
    const length = Number(request.headers.get('content-length'));
    if (!Number.isInteger(length) || length <= 0) return json(411, { error: 'length_required' });
    if (length > BIG_VIDEO.part) return json(413, { error: 'too_large' });
    if (!request.body) return json(400, { error: 'bad_request' });
    try {
      const part = await env.MEDIA.resumeMultipartUpload(key as string, uploadId).uploadPart(n, request.body);
      return json(201, { n, etag: part.etag });
    } catch {
      // 연결이 끊겼거나 올리기 번호가 없어졌으면 실패한다(클라이언트가 그 조각만 다시 보낸다)
      return json(400, { error: 'incomplete_body' });
    }
  } catch (e) {
    return backendErrorResponse(e);
  }
};
