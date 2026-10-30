// 부모가 방금 올린 사진들로 공유 링크 만들기. { groupIds, mediaIds } → { code, url }
import type { APIRoute } from 'astro';
import { getBackend } from '../../lib/backend';
import { shareUrl } from '../../lib/familyAdmin';
import { UUID, backendErrorResponse, json } from '../../lib/media';
import { currentParent } from '../../lib/pass';

const ids = (v: unknown, max: number) => Array.isArray(v) && v.length <= max && v.every((x) => typeof x === 'string' && UUID.test(x));

export const POST: APIRoute = async ({ request, cookies, url }) => {
  const body = (await request.json().catch(() => null)) as { groupIds?: unknown; mediaIds?: unknown } | null;
  if (!body || !ids(body.groupIds, 20) || !(body.groupIds as string[]).length || !ids(body.mediaIds ?? [], 200)) {
    return json(400, { error: 'bad_request' });
  }
  try {
    const pass = await currentParent(cookies);
    if (!pass) return json(401, { error: 'login_required' });
    const code = await getBackend().createShare(pass, body.groupIds as string[], undefined, (body.mediaIds as string[]) ?? []);
    return json(201, { code, url: shareUrl(url.origin, code) });
  } catch (e) {
    return backendErrorResponse(e);
  }
};
