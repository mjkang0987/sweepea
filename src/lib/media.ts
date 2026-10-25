// 사진 파일 규칙: 종류별로 넣을 수 있는 파일(부분)과 형식·크기. 기기에서 압축해서 올린다(기획서)
import type { MediaKind } from './backend';

const MB = 1024 * 1024;
const IMAGE = { types: ['image/jpeg', 'image/webp', 'image/png'], max: 15 * MB };
// shortcut: Workers 요청 한도 100MB라 영상도 100MB까지. 앱에서 큰 원본을 올릴 때 R2 서명 URL로 바꾼다
const VIDEO = { types: ['video/mp4', 'video/quicktime'], max: 100 * MB };

export const PARTS: Record<MediaKind, Record<string, { types: string[]; max: number }>> = {
  photo: { view: IMAGE, thumb: IMAGE },
  video: { view: VIDEO, thumb: IMAGE, poster: IMAGE },
};

export const mediaKey = (familyId: string, mediaId: string, part: string) => `${familyId}/${mediaId}/${part}`;

export const UUID = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;

export const json = (status: number, body: unknown) =>
  new Response(JSON.stringify(body), { status, headers: { 'content-type': 'application/json', 'cache-control': 'no-store' } });
