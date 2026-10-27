// 올리기 끝: 본문 {view, thumb, poster?}는 PUT이 돌려준 키. 이 사진의 키인지, R2에 있는지 확인하고 잰 크기로 완료 처리(서버 전용 함수)
import type { APIRoute } from 'astro';
import { env } from 'cloudflare:workers';
import { BackendError, getBackend } from '../../../../lib/backend';
import { PARTS, UUID, backendErrorResponse, isMediaKey, json, withUploader } from '../../../../lib/media';

export const POST: APIRoute = async ({ params, request, cookies }) => {
  const id = params.id ?? '';
  if (!UUID.test(id)) return json(404, { error: 'not_found' });
  const body = (await request.json().catch(() => null)) as Record<string, unknown> | null;
  try {
    const backend = getBackend();
    const r = await withUploader(cookies, (pass) => backend.uploadTarget(pass, id));
    if (r === 'login') return json(401, { error: 'login_required' });
    if (!r) return json(404, { error: 'not_found' });
    const target = r.value;
    const parts = Object.keys(PARTS[target.kind]);
    const keys = parts.map((p) => (body && isMediaKey(body[p], target.family_id, id, p) ? (body[p] as string) : null));
    const heads = await Promise.all(keys.map((k) => (k ? env.MEDIA.head(k) : null)));
    const missing = parts.filter((_, i) => !heads[i]);
    if (missing.length) return json(409, { error: 'missing_parts', missing });
    const bytes = heads.reduce((n, h) => n + h!.size, 0);
    const k = (p: string) => keys[parts.indexOf(p)] as string;
    let ok: boolean;
    try {
      ok = await backend.finishUpload(id, { view: k('view'), thumb: k('thumb'), poster: target.kind === 'video' ? k('poster') : null }, bytes);
    } catch (e) {
      // 완료하면 5GB를 넘는다(507): 올린 파일은 바로 지운다(남겨 두면 정리 작업 전까지 요금)
      if (e instanceof BackendError && e.status === 507) await env.MEDIA.delete(keys.filter(Boolean) as string[]).catch(() => undefined);
      throw e;
    }
    if (!ok) return json(409, { error: 'already_done' });
    // 다시 올리느라 남은 예전 파일(PUT마다 새 키)은 바로 지운다. 실패해도 완료는 그대로(남은 건 용량에 안 잡힌다)
    const keep = new Set(keys.filter(Boolean) as string[]);
    const folder = await env.MEDIA.list({ prefix: `${target.family_id}/${id}/` }).catch(() => null);
    const stale = folder?.objects.map((o) => o.key).filter((k) => !keep.has(k)) ?? [];
    if (stale.length) await env.MEDIA.delete(stale).catch(() => undefined);
    return json(200, { id, bytes });
  } catch (e) {
    return backendErrorResponse(e);
  }
};
