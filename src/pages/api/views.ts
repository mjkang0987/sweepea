// 넘겨 보기 앨범에서 가운데에 머문 사진들을 남긴다(보신 기록, 95). { ids } → 204. 가족 출입증으로만(엄빠 계정은 안 셈)
import type { APIRoute } from 'astro';
import { getBackend } from '../../lib/backend';
import { UUID, backendErrorResponse, json } from '../../lib/media';
import { currentPass } from '../../lib/pass';

export const POST: APIRoute = async ({ request, cookies }) => {
  const body = (await request.json().catch(() => null)) as { ids?: unknown } | null;
  const ids = body?.ids;
  if (!Array.isArray(ids) || !ids.length || ids.length > 50 || !ids.every((x) => typeof x === 'string' && UUID.test(x))) {
    return json(400, { error: 'bad_request' });
  }
  try {
    const pass = await currentPass(cookies);
    if (!pass) return json(401, { error: 'login_required' });
    await getBackend().noteViews(pass, ids as string[]);
    return new Response(null, { status: 204 });
  } catch (e) {
    return backendErrorResponse(e);
  }
};
