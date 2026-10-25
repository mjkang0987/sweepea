// 사진 파일 규칙: 종류별로 넣을 수 있는 파일(부분)과 형식·크기. 기기에서 압축해서 올린다(기획서)
import type { AstroCookies } from 'astro';
import { BackendError, type MediaKind, type Pass } from './backend';
import { currentParent, currentPass } from './pass';

/** 올릴 수 있는 출입증들: 부모 세션, 가족 기기 출입증 순. 한쪽 갱신이 일시적으로 실패해도 다른 쪽은 쓴다 */
async function uploaderPasses(cookies: AstroCookies): Promise<Pass[]> {
  const out: Pass[] = [];
  let failed: unknown = null;
  for (const get of [currentParent, currentPass]) {
    try {
      const p = await get(cookies);
      if (p) out.push(p);
    } catch (e) {
      failed = e;
    }
  }
  // 둘 다 일시 오류면 '로그인 끝남'(401)이 아니라 오류로(다시 누르면 이어 올리게)
  if (!out.length && failed) throw failed;
  return out;
}

/** 출입증마다 시도해서 처음 되는 것(403·null이면 다음 출입증). 하나도 없으면 null */
export async function withUploader<T>(cookies: AstroCookies, fn: (pass: Pass) => Promise<T | null>): Promise<{ pass: Pass; value: T } | null | 'login'> {
  const passes = await uploaderPasses(cookies);
  if (!passes.length) return 'login';
  let lastError: unknown = null;
  for (const pass of passes) {
    try {
      const value = await fn(pass);
      if (value !== null) return { pass, value };
    } catch (e) {
      if (!(e instanceof BackendError) || e.status !== 403) throw e;
      lastError = e;
    }
  }
  if (lastError) throw lastError;
  return null;
}

const MB = 1024 * 1024;
const IMAGE = { types: ['image/jpeg', 'image/webp', 'image/png'], max: 15 * MB };
// shortcut: Workers 요청 한도 100MB라 영상도 100MB까지. 앱에서 큰 원본을 올릴 때 R2 서명 URL로 바꾼다
const VIDEO = { types: ['video/mp4', 'video/quicktime'], max: 100 * MB };

export const PARTS: Record<MediaKind, Record<string, { types: string[]; max: number }>> = {
  photo: { view: IMAGE, thumb: IMAGE },
  video: { view: VIDEO, thumb: IMAGE, poster: IMAGE },
};

// 넣을 때마다 새 키: 완료 뒤에 늦게 끝난 PUT이 기록된 파일을 덮어쓰지 못하게
export const newMediaKey = (familyId: string, mediaId: string, part: string) => `${familyId}/${mediaId}/${part}-${crypto.randomUUID()}`;
export const isMediaKey = (key: unknown, familyId: string, mediaId: string, part: string) =>
  typeof key === 'string' && key.startsWith(`${familyId}/${mediaId}/${part}-`) && UUID.test(key.slice(`${familyId}/${mediaId}/${part}-`.length));

export const UUID = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;

/** 백엔드 인증 오류(만료·차단된 출입증)를 500 대신 401·403으로 */
export function backendErrorResponse(e: unknown): Response {
  if (e instanceof BackendError && e.status === 401) return json(401, { error: 'login_required' });
  if (e instanceof BackendError && e.status === 403) return json(403, { error: 'not_allowed' });
  if (e instanceof BackendError && e.status === 400) return json(400, { error: 'bad_request' });
  if (e instanceof BackendError && e.status === 429) return json(429, { error: 'too_many_uploads' });
  throw e;
}

export const json = (status: number, body: unknown) =>
  new Response(JSON.stringify(body), { status, headers: { 'content-type': 'application/json', 'cache-control': 'no-store' } });
