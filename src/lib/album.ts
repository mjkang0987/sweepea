// 앨범 화면 공통: 주소 쿼리(집 f, 보기 v, 칸 z) 읽기와 링크 만들기, 들어간 가족방·사진 목록
import type { AstroCookies } from 'astro';
import { BackendError, getBackend, REACTION_KINDS, type MediaItem, type MeFamily, type Pass, type ReactionCount, type ReactionKind } from './backend';
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
  | { pass: Pass; open: MeFamily[]; kids: Map<string, string>; q: AlbumQuery; items: MediaItem[]; name: string | null };

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
  return { pass, open, kids, q, items, name: (open.find((f) => f.family_id === q.f) ?? open[0]).name };
}

const dayFmt = new Intl.DateTimeFormat('ko-KR', { month: 'long', day: 'numeric', timeZone: 'Asia/Seoul' });
const yearDayFmt = new Intl.DateTimeFormat('ko-KR', { year: 'numeric', month: 'long', day: 'numeric', timeZone: 'Asia/Seoul' });
const yearFmt = new Intl.DateTimeFormat('ko-KR', { year: 'numeric', timeZone: 'Asia/Seoul' });
/** 올해면 '10월 21일', 다른 해면 '2025년 10월 21일'(서울 기준) */
export const dayLabel = (iso: string, now = new Date()) => {
  const d = new Date(iso);
  return (yearFmt.format(d) === yearFmt.format(now) ? dayFmt : yearDayFmt).format(d);
};

/** 사진별 반응 요약: 종류별 수·내가 눌렀는지, 한마디 수 */
export type Reacts = Map<string, { counts: Partial<Record<ReactionKind | 'comment', number>>; mine: Set<ReactionKind | 'comment'> }>;

export async function loadReacts(pass: Pass, mediaIds: string[]): Promise<Reacts> {
  const out: Reacts = new Map(mediaIds.map((id) => [id, { counts: {}, mine: new Set() }]));
  for (const r of await getBackend().reactionCounts(pass, mediaIds) as ReactionCount[]) {
    const x = out.get(r.media_id);
    if (!x) continue;
    x.counts[r.kind] = r.n;
    if (r.mine) x.mine.add(r.kind);
  }
  return out;
}

const BACK = /^\/album(\/[0-9a-f-]{36})?(\?[A-Za-z0-9=&%._-]*)?(#[A-Za-z0-9_-]+)?$/;

/** 반응·한마디 폼(POST /album/<id>) 처리. 돌아갈 곳은 앨범 안 주소만(열린 이동 방지) */
export async function handleReactPost(request: Request, mediaId: string, cookies: AstroCookies, fallback: string): Promise<string> {
  const form = await request.formData().catch(() => null);
  const back = String(form?.get('back') ?? '');
  const to = new URL(BACK.test(back) ? back : fallback, 'http://x');
  const pass = await currentPass(cookies);
  if (!pass || !form) return '/';
  try {
    const react = String(form.get('react') ?? '');
    const body = form.get('body');
    if (react) {
      const [kind, on] = react.split(':');
      if ((REACTION_KINDS as readonly string[]).includes(kind) && (on === 'on' || on === 'off')) {
        await getBackend().react(pass, mediaId, kind as ReactionKind, on === 'on');
      }
    } else if (body !== null) {
      const text = String(body).trim();
      if (!text) to.searchParams.set('say', 'empty');
      else {
        await getBackend().comment(pass, mediaId, text.slice(0, 200));
        to.searchParams.set('say', 'sent');
      }
      to.searchParams.set('sm', mediaId);
      // 넘겨 보기는 돌아올 카드(#p-<id>)가 이미 붙어 온다
      if (!to.hash) to.hash = 'say';
    }
  } catch (e) {
    if (!(e instanceof BackendError)) throw e;
    if (e.status === 401) return '/';
    // 반응 실패는 조용히, 한마디 실패는 알려 준다(429 하루 한도, 그 밖은 승인 대기·볼 수 없는 사진 등)
    if (form.get('body') !== null) {
      to.searchParams.set('say', e.status === 429 ? 'limit' : 'error');
      to.searchParams.set('sm', mediaId);
      if (!to.hash) to.hash = 'say';
    }
  }
  return to.pathname + to.search + to.hash;
}
