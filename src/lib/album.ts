// 앨범 화면 공통: 주소 쿼리(집 f, 보기 v, 칸 z) 읽기와 링크 만들기, 들어간 가족방·사진 목록
import type { AstroCookies } from 'astro';
import { getBackend, type MediaItem, type MeFamily } from './backend';
import { currentPass } from './pass';
import { isOpen } from './families';
import { callName } from './ko';

export const ZOOMS = [1, 2, 3, 5] as const;
export type Zoom = (typeof ZOOMS)[number];

export interface AlbumQuery {
  f?: string;
  v: 'swipe' | 'list';
  z: Zoom;
}

export function readQuery(url: URL, familyIds: string[]): AlbumQuery {
  const f = url.searchParams.get('f') ?? undefined;
  const z = Number(url.searchParams.get('z'));
  return {
    f: f && familyIds.includes(f) ? f : undefined,
    v: url.searchParams.get('v') === 'list' ? 'list' : 'swipe',
    z: (ZOOMS as readonly number[]).includes(z) ? (z as Zoom) : 2,
  };
}

/** 기본값은 주소에서 뺀다(짧은 주소) */
export function albumHref(q: AlbumQuery, path = '/album'): string {
  const p = new URLSearchParams();
  if (q.f) p.set('f', q.f);
  if (q.v === 'list') p.set('v', 'list');
  if (q.z !== 2) p.set('z', String(q.z));
  const s = p.toString();
  return s ? `${path}?${s}` : path;
}

export type AlbumLoad =
  | { redirect: string }
  | { open: MeFamily[]; kids: Map<string, string>; q: AlbumQuery; items: MediaItem[]; name: string | null };

/** 들어간 가족방이 없으면 이동할 곳. 있으면 고른 집의 최근 사진(최대 200장) */
export async function loadAlbum(cookies: AstroCookies, url: URL): Promise<AlbumLoad> {
  const pass = await currentPass(cookies);
  if (!pass) return { redirect: '/' };
  const backend = getBackend();
  const { families } = await backend.me(pass);
  const open = families.filter(isOpen);
  if (open.length === 0) return { redirect: families.length ? '/wait' : '/' };
  const q = readQuery(url, open.map((f) => f.family_id));
  // shortcut: 최근 200장까지만. 더 오래된 사진은 다음 쪽 넘기기((taken_at, id) 커서)를 만들 때
  const items = await backend.listMedia(pass, { familyId: q.f, limit: 200 });
  const kids = new Map(open.map((f) => [f.family_id, callName(f.child_name ?? '아이')]));
  return { open, kids, q, items, name: (open.find((f) => f.family_id === q.f) ?? open[0]).name };
}

const dayFmt = new Intl.DateTimeFormat('ko-KR', { month: 'long', day: 'numeric', timeZone: 'Asia/Seoul' });
export const dayLabel = (iso: string) => dayFmt.format(new Date(iso));
