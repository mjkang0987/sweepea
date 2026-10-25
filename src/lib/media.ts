// 사진 파일 규칙: 종류별로 넣을 수 있는 파일(부분)과 형식·크기. 기기에서 압축해서 올린다(기획서)
import { BackendError, type MediaKind } from './backend';

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
  throw e;
}

export const json = (status: number, body: unknown) =>
  new Response(JSON.stringify(body), { status, headers: { 'content-type': 'application/json', 'cache-control': 'no-store' } });
