// 사진 행 만들기. 파일은 PUT /api/media/<id>/<부분>, 끝나면 POST /api/media/<id>/done
import type { APIRoute } from 'astro';
import { BackendError, getBackend, type NewMedia } from '../../../lib/backend';
import { currentPass } from '../../../lib/pass';
import { UUID, json } from '../../../lib/media';

const SOURCES = ['exif', 'file', 'upload', 'manual'];
const posInt = (v: unknown) => v === undefined || (Number.isInteger(v) && (v as number) > 0 && (v as number) < 100_000);
const uuids = (v: unknown) => v === undefined || (Array.isArray(v) && v.length <= 20 && v.every((x) => typeof x === 'string' && UUID.test(x)));

/** 클라이언트가 보낸 값을 그대로 믿지 않는다. 형식이 틀리면 null */
export function parseNewMedia(b: Record<string, unknown>): NewMedia | null {
  const takenAt = typeof b.takenAt === 'string' ? new Date(b.takenAt) : null;
  const ok =
    typeof b.familyId === 'string' && UUID.test(b.familyId) &&
    (b.kind === 'photo' || b.kind === 'video') &&
    takenAt !== null && !Number.isNaN(takenAt.getTime()) &&
    SOURCES.includes(b.takenAtSource as string) &&
    posInt(b.width) && posInt(b.height) &&
    (b.durationSec === undefined || (typeof b.durationSec === 'number' && b.durationSec >= 0 && b.durationSec < 100_000)) &&
    uuids(b.groupIds) && uuids(b.childIds);
  if (!ok) return null;
  return {
    familyId: b.familyId as string,
    kind: b.kind as NewMedia['kind'],
    takenAt: takenAt!.toISOString(),
    takenAtSource: b.takenAtSource as NewMedia['takenAtSource'],
    width: b.width as number | undefined,
    height: b.height as number | undefined,
    durationSec: b.durationSec as number | undefined,
    groupIds: b.groupIds as string[] | undefined,
    childIds: b.childIds as string[] | undefined,
  };
}

export const POST: APIRoute = async ({ request, cookies }) => {
  const pass = await currentPass(cookies);
  if (!pass) return json(401, { error: 'login_required' });
  const body = await request.json().catch(() => null);
  const input = body && typeof body === 'object' ? parseNewMedia(body as Record<string, unknown>) : null;
  if (!input) return json(400, { error: 'bad_request' });
  try {
    return json(201, { id: await getBackend().createMedia(pass, input) });
  } catch (e) {
    if (e instanceof BackendError && (e.status === 401 || e.status === 403)) return json(403, { error: 'not_allowed' });
    if (e instanceof BackendError && e.status === 400) return json(400, { error: 'bad_request' });
    throw e;
  }
};
