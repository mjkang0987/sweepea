// 앨범 화면 공통: 주소 쿼리(집 f, 보기 v, 칸 z) 읽기와 링크 만들기, 들어간 가족방·사진 목록
import type { AstroCookies } from 'astro';
import { BackendError, getBackend, REACTION_KINDS, type MediaCursor, type MediaItem, type MediaQuery, type MeFamily, type Pass, type ReactionCount, type ReactionKind } from './backend';
import { currentPass } from './pass';
import { isOpen } from './families';
import { callName } from './ko';
import { signedMediaUrl } from './signed';
import { UUID } from './media';

/** 사진 크기 단계(98a·98c): 1·2·3·5칸 = 사진 전부, 'm' = 월별, 'y' = 연별(대표 사진 카드). 크게 = 전부, 줄이면 대표(사진 앱처럼) */
export const ZOOMS = [1, 2, 3, 5, 'm', 'y'] as const;
export type Zoom = (typeof ZOOMS)[number];
const toZoom = (v: string | null | undefined): Zoom | undefined => ZOOMS.find((z) => String(z) === v);
const chosen = (url: URL) => (url.pathname === '/home' || url.pathname === '/album') && !url.searchParams.has('before') && !url.searchParams.has('to') && !url.searchParams.has('at');
const KEEP = { path: '/', httpOnly: true, sameSite: 'lax' as const, secure: import.meta.env.PROD, maxAge: 365 * 24 * 3600 };

export interface AlbumQuery {
  f?: string;
  v: 'swipe' | 'list';
  z: Zoom;
}

/** 칸 단계: 주소 ?z=가 있으면 그것, 없으면 기억한 단계, 그것도 없으면 2(사용자 2026-10-29 "보기 형식은 기억하도록").
 *  기억은 목록 화면에서 −/+·탭으로 고른 것만: 달 카드로 들어간 쪽·이어지는 쪽(?before=), 크게 보기에서 닫고 돌아온 쪽(?to=), 크게 보기 화면은 빼고 */
export function pickZoom(url: URL, cookies: AstroCookies, name: string): Zoom {
  const z = toZoom(url.searchParams.get('z'));
  if (z !== undefined) {
    if (chosen(url)) cookies.set(name, String(z), KEEP);
    return z;
  }
  const saved = toZoom(cookies.get(name)?.value) ?? 2;
  // 크게 보기·사진 정보 수정에서 돌아온 쪽(?to=)은 기억한 단계가 월별·연별이어도 칸으로(보던 사진 자리로, 리뷰 2026-10-29)
  return (saved === 'm' || saved === 'y') && url.searchParams.has('to') ? 3 : saved;
}

/** 가족 앨범 주소 읽기. 보기(넘겨/모아)와 칸 단계는 주소에 없으면 그 기기에 기억한 것(sp_av·sp_az) */
export function readQuery(url: URL, cookies: AstroCookies, familyIds: string[]): AlbumQuery {
  const f = url.searchParams.get('f') ?? undefined;
  const vp = url.searchParams.get('v');
  if ((vp === 'list' || vp === 'swipe') && chosen(url)) cookies.set('sp_av', vp, KEEP);
  const v = vp === 'list' || vp === 'swipe' ? vp : cookies.get('sp_av')?.value === 'list' ? 'list' : 'swipe';
  return { f: f && familyIds.includes(f) ? f : undefined, v, z: pickZoom(url, cookies, 'sp_az') };
}

/** 보기·칸은 늘 주소에 적는다(기억한 값보다 링크가 먼저라, 빼면 기억한 값으로 바뀌어 버림) */
export function albumHref(q: AlbumQuery, path = '/album'): string {
  const p = new URLSearchParams();
  if (q.f) p.set('f', q.f);
  p.set('v', q.v);
  p.set('z', String(q.z));
  return `${path}?${p}`;
}

/** 목록 한 번에 그리는 장 수(사용자 2026-10-28 "60장씩, 끝까지") */
export const PAGE = 60;
/** 닫고 돌아올 때 한 번에 그리는 최대(Supabase 기본 max_rows 1000 아래, +1장으로 다음 쪽 확인) */
const TO_MAX = 900;
export interface MediaPage {
  items: MediaItem[];
  /** 다음 쪽 주소 값(?before=, 이 쪽 마지막 사진의 찍은 날~id). 끝이면 null */
  next: string | null;
  /** 앞 쪽에 이어지는 쪽이거나 여러 쪽을 그렸으면 true: 끝 줄 '모두 봤어요'를 보일지 */
  more: boolean;
  /** 이 쪽 앞에 있는 사진 수(넘겨 보기 'n / 전체'의 n) */
  offset: number;
}
const cursorParam = (m: MediaItem) => `${m.taken_at}~${m.id}`;
/** ?before= 값 → 커서. 기준 사진을 다시 찾지 않으므로 그사이 지워져도 그 자리부터 이어진다 */
// 찍은 날은 DB가 준 꼴 그대로(마이크로초까지, 다시 만들면 잘려 커서가 틀어짐) 엄격히 확인한다: DB 거르기 글에 그대로 들어가므로
const ISO = /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d{1,6})?(Z|[+-]\d{2}:\d{2})$/;
function readCursor(v: string | null): MediaCursor | undefined {
  const i = v?.lastIndexOf('~') ?? -1;
  if (!v || i < 0) return undefined;
  const takenAt = v.slice(0, i), id = v.slice(i + 1);
  return ISO.test(takenAt) && UUID.test(id) ? { takenAt, id } : undefined;
}
/** 주소에 맞는 한 쪽: ?before=<커서>면 그 다음 PAGE장, ?to=<id>면(크게 보기에서 닫고 돌아옴) 그 사진이 든 쪽까지 처음부터(아래로 30장은 더), 아니면 처음 PAGE장 */
export async function loadPage(pass: Pass, base: MediaQuery, url: URL): Promise<MediaPage> {
  const backend = getBackend();
  const page = (rows: MediaItem[], limit: number, more: boolean, offset: number): MediaPage => {
    const items = rows.slice(0, limit);
    return { items, next: rows.length > limit ? cursorParam(items[items.length - 1]) : null, more, offset };
  };
  const before = readCursor(url.searchParams.get('before'));
  if (before) {
    // 앞에 있는 수 = 전체 - 커서보다 옛것(기준 사진이 그사이 지워져도 맞게)
    const [rows, total, older] = await Promise.all([
      backend.listMedia(pass, { ...base, before, limit: PAGE + 1 }),
      backend.countMedia(pass, base),
      backend.countMedia(pass, { ...base, before }),
    ]);
    return page(rows, PAGE, true, total - older);
  }
  // ?at=YYYY-MM(달·해 카드): 처음부터 그 달까지 그려 위로 올리면 최근 달도 보이게(사용자 "월별에서 들어가면 이전 달이 안 보여"). 너무 아래면 그 달부터(?before= 방식)
  const at = url.searchParams.get('at');
  if (at && /^\d{4}-(0[1-9]|1[0-2])$/.test(at)) {
    const [cy, cm] = at.split('-').map(Number);
    const next = cm === 12 ? `${cy + 1}-01` : `${cy}-${String(cm + 1).padStart(2, '0')}`;
    const c = { takenAt: `${next}-01T00:00:00+09:00`, id: '00000000-0000-0000-0000-000000000000' };
    // 그 달보다 최근 사진 수(다음 달 1일 0시 이후) + 그 달 앞부분이 보이게 한 쪽 더
    const newer = await backend.countMedia(pass, { ...base, after: c });
    const want = Math.ceil((newer + PAGE) / PAGE) * PAGE;
    if (want <= TO_MAX) return page(await backend.listMedia(pass, { ...base, limit: want + 1 }), want, want > PAGE, 0);
    const [rows, total] = await Promise.all([backend.listMedia(pass, { ...base, before: c, limit: PAGE + 1 }), backend.countMedia(pass, base)]);
    return page(rows, PAGE, true, newer > total ? 0 : newer);
  }
  const toId = url.searchParams.get('to');
  const to = toId && UUID.test(toId) ? (await backend.listMedia(pass, { ...base, id: toId, limit: 1 }))[0] : undefined;
  if (to) {
    const c = { takenAt: to.taken_at, id: to.id };
    const newer = await backend.countMedia(pass, { ...base, after: c });
    // 그 사진 아래로도 30장은 있게(쪽 끝에 가까우면 아래가 짧아 같은 높이로 스크롤하지 못함)
    const want = Math.ceil((newer + 1 + 30) / PAGE) * PAGE;
    if (want <= TO_MAX) return page(await backend.listMedia(pass, { ...base, limit: want + 1 }), want, want > PAGE, 0);
    // shortcut: 아주 아래(900장 넘게) 사진은 그 위 30장부터 한 쪽만 그림(위로는 이어 붙이지 않음, 탭 '앨범'으로 처음부터), 필요하면 위쪽 이어 붙이기
    const [above, below] = await Promise.all([
      backend.listMedia(pass, { ...base, after: c, limit: 30 }),
      backend.listMedia(pass, { ...base, before: c, limit: PAGE - 30 }),
    ]);
    return page([...above, to, ...below], PAGE, true, newer - above.length);
  }
  return page(await backend.listMedia(pass, { ...base, limit: PAGE + 1 }), PAGE, false, 0);
}

/** 크게 보기: 그 사진과 앞뒤 21장(창 ±20장 + 창 밖 한 장씩, slideWindow용), 몇 번째·전체. 볼 수 없는 사진이면 null */
export async function loadWindow(pass: Pass, base: MediaQuery, id: string): Promise<{ items: MediaItem[]; i: number; pos: number; total: number } | null> {
  const backend = getBackend();
  const m = (await backend.listMedia(pass, { ...base, id, limit: 1 }))[0];
  if (!m) return null;
  const c = { takenAt: m.taken_at, id: m.id };
  const [newer, older, ahead, total] = await Promise.all([
    backend.listMedia(pass, { ...base, after: c, limit: 21 }),
    backend.listMedia(pass, { ...base, before: c, limit: 21 }),
    backend.countMedia(pass, { ...base, after: c }),
    backend.countMedia(pass, base),
  ]);
  return { items: [...newer, m, ...older], i: newer.length, pos: ahead + 1, total };
}

export type AlbumLoad =
  | { redirect: string }
  | { pass: Pass; open: MeFamily[]; kids: Map<string, string>; q: AlbumQuery; base: MediaQuery; name: string | null };

/** 들어간 가족방이 없으면 이동할 곳. 있으면 고른 집과 사진 목록 조건(base: 쪽은 loadPage, 크게 보기는 loadWindow로) */
export async function loadAlbum(cookies: AstroCookies, url: URL): Promise<AlbumLoad> {
  const pass = await currentPass(cookies);
  if (!pass) return { redirect: '/' };
  const backend = getBackend();
  const { families } = await backend.me(pass);
  const open = families.filter(isOpen);
  if (open.length === 0) return { redirect: families.length ? '/wait' : '/' };
  const q = readQuery(url, cookies, open.map((f) => f.family_id));
  const kids = new Map(open.map((f) => [f.family_id, callName(f.child_name ?? '아이')]));
  return { pass, open, kids, q, base: { familyId: q.f }, name: (open.find((f) => f.family_id === q.f) ?? open[0]).name };
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
  // DB 함수는 한 번에 200장까지만 본다(닫고 돌아오면 900장까지 그림) → 200장씩 나눠 함께 묻는다
  const chunks = Array.from({ length: Math.ceil(mediaIds.length / 200) }, (_, i) => mediaIds.slice(i * 200, i * 200 + 200));
  const rows = (await Promise.all(chunks.map((ids) => getBackend().reactionCounts(pass, ids)))).flat() as ReactionCount[];
  for (const r of rows) {
    const x = out.get(r.media_id);
    if (!x) continue;
    x.counts[r.kind] = r.n;
    if (r.mine) x.mine.add(r.kind);
  }
  return out;
}

const BACK = /^\/album(\/[0-9a-f-]{36})?(\?[A-Za-z0-9=&%._-]*)?(#[A-Za-z0-9_-]+)?$/;

/** 반응·한마디 보내기(가족은 구성원으로, 엄빠는 부모 계정으로) */
export interface ReactOps {
  react(mediaId: string, kind: ReactionKind, on: boolean): Promise<void>;
  comment(mediaId: string, body: string): Promise<void>;
  /** 한마디 지우기(쓴 사람만, DB가 막음) */
  deleteComment(commentId: string): Promise<void>;
}

/** 반응·한마디 폼 처리 공통. back은 back 정규식에 맞는 주소만(열린 이동 방지), 아니면 fallback */
export async function applyReactPost(request: Request, mediaId: string, ops: ReactOps, back: RegExp, fallback: string): Promise<string> {
  const form = await request.formData().catch(() => null);
  const asked = String(form?.get('back') ?? '');
  const to = new URL(back.test(asked) ? asked : fallback, 'http://x');
  if (!form) return fallback;
  try {
    const react = String(form.get('react') ?? '');
    const body = form.get('body');
    const del = String(form.get('del') ?? '');
    if (del) {
      // 지운 뒤엔 시트를 열어 둔 채로 돌아온다(say=deleted면 서버가 시트를 열어서 그림, #talk는 쓰지 않음)
      to.hash = '';
      to.searchParams.set('say', 'delerror');
      if (UUID.test(del)) {
        await ops.deleteComment(del);
        to.searchParams.set('say', 'deleted');
      }
    } else if (react) {
      const [kind, on] = react.split(':');
      if ((REACTION_KINDS as readonly string[]).includes(kind) && (on === 'on' || on === 'off')) {
        await ops.react(mediaId, kind as ReactionKind, on === 'on');
      }
    } else if (body !== null) {
      const text = String(body).trim();
      if (!text) to.searchParams.set('say', 'empty');
      else {
        await ops.comment(mediaId, text.slice(0, 200));
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
    // 지우기 실패(이미 지움·권한 없음 등)는 say=delerror 그대로 시트에서 알림
    if (form.get('body') !== null) {
      to.searchParams.set('say', e.status === 429 ? 'limit' : 'error');
      to.searchParams.set('sm', mediaId);
      if (!to.hash) to.hash = 'say';
    }
  }
  return to.pathname + to.search + to.hash;
}

/** 가족 반응·한마디 폼(POST /album/<id>) 처리. 돌아갈 곳은 앨범 안 주소만 */
export async function handleReactPost(request: Request, mediaId: string, cookies: AstroCookies, fallback: string): Promise<string> {
  const pass = await currentPass(cookies);
  if (!pass) return '/';
  const b = getBackend();
  return applyReactPost(request, mediaId, { react: (id, k, on) => b.react(pass, id, k, on), comment: (id, t) => b.comment(pass, id, t), deleteComment: (id) => b.deleteComment(pass, id) }, BACK, fallback);
}

/** 크게 보기 스와이퍼에 넘길 앞뒤 사진(주소는 미리 서명: 한 시간 동안 같은 주소라 브라우저 캐시를 탄다) */
export interface Slide {
  id: string;
  href: string;
  src: string;
  poster?: string;
  video: boolean;
  label: string;
}
// shortcut: 앞뒤 20장까지만 손가락으로 넘김, 그 밖은 끝에서 ‹ › 링크로 페이지를 새로 연다
export interface SlideWindow {
  slides: Slide[];
  /** 창 바로 밖 앞뒤 사진 주소(창 끝에서 ‹ ›가 이 페이지를 연다) */
  before?: string;
  after?: string;
}
export async function slideWindow(items: MediaItem[], i: number, href: (m: MediaItem) => string, label: (m: MediaItem) => string): Promise<SlideWindow> {
  const from = Math.max(0, i - 20);
  const slides = await Promise.all(
    items.slice(from, i + 21).map(async (m) => ({
      id: m.id,
      href: href(m),
      src: await signedMediaUrl(m.view_key),
      poster: m.poster_key ? await signedMediaUrl(m.poster_key) : undefined,
      video: m.kind === 'video',
      label: label(m),
    })),
  );
  const b = items[from - 1];
  const a = items[i + 21];
  return { slides, before: b && href(b), after: a && href(a) };
}
