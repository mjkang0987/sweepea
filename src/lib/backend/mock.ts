// 개발·검사용 메모리 백엔드. 서버 프로세스가 살아 있는 동안만 기억한다.
// 실제 규칙(그룹 경보, 승인 대기 3일 등)은 DB가 강제하고, 여기선 화면 흐름 확인에 필요한 만큼만 흉내 낸다.
// 운영에서는 index.ts가 이 구현을 쓰지 못하게 막는다.
import type { ActivityItem, Backend, EnterResult, EntryInfo, EntryMe, MediaItem, MediaQuery, Me, MeFamily, ParentHome, ParentInviteInfo, Pass, ReactionCount, ReactionKind, TextSizeMode } from './types';
import { BackendError } from './supabase';
import { SWEEPEA_MOCK_USED_BYTES } from 'astro:env/server';

// 개발 확인용: 저장 공간 레이어를 보려고 사용량을 미리 더한다
const MOCK_USED = SWEEPEA_MOCK_USED_BYTES ?? 0;

interface Group { id: string; familyId: string; name: string; hint: string; password: string; exclude?: boolean }
interface Member { id: string; groupId: string; name: string; status: 'active' | 'pending' | 'rejected'; uploader?: boolean; helpAt?: number; entryShare?: string }
interface Share { code: string; groupIds: string[]; createdAt: number; targetMemberId?: string; usedAt?: number; closed?: boolean; revoked?: boolean; mediaIds?: string[] }
interface Device { id: string; familyId: string; status: 'active' | 'pending' | 'revoked'; memberId?: string; requestedName?: string; failures: Map<string, number[]>; canUpload?: boolean }

const HOUR = 3600_000;
// 하린이네(외가·친가)와 도윤이네(외할머니의 다른 손주). 외할머니 한 기기로 두 가족방에 들어가는 흐름을 본다
// 가족방 id는 실제처럼 uuid(API가 형식을 검사한다)
const HARIN = '00000000-0000-4000-8000-00000000f001';
const DOYUN = '00000000-0000-4000-8000-00000000f002';
// Workers는 모듈 맨 위에서 난수를 못 만든다(crypto.randomUUID 금지) — 고정 id
const kids = [
  { id: '00000000-0000-4000-8000-00000000c001', familyId: HARIN, name: '하린', birth_date: '2025-09-17', show_health: true },
  { id: '00000000-0000-4000-8000-00000000c002', familyId: DOYUN, name: '도윤', birth_date: '2026-08-30', show_health: true },
];
// 접종·검진 완료: 아이 id → 항목 → 날짜
const healthDone = new Map<string, Map<string, string>>();
const firstChild = (familyId: string) => kids.find((k) => k.familyId === familyId)?.name ?? null;
const sizeModes: Record<string, TextSizeMode> = {};
// 탈퇴 유예: 가족방 → 지울 시각(ms). 있으면 가족 화면은 닫힌다
const closingAt: Record<string, number> = {};
const isClosing = (familyId: string) => closingAt[familyId] !== undefined;
const groups: Group[] = [
  { id: 'g-mat', familyId: HARIN, name: '외가', hint: '외가 비밀번호', password: '1234' },
  { id: 'g-pat', familyId: HARIN, name: '친가', hint: '할아버지 생신', password: '5678' },
  { id: 'g-dy', familyId: DOYUN, name: '가족', hint: '도윤이 생일', password: '9999' },
];
// shortcut: 만든 시각을 따로 안 들고 있어 처음 목록에 나온 때를 만든 때로 친다(목 전용)
const born = new WeakMap<object, string>();
const bornAt = (o: object) => born.get(o) ?? (born.set(o, new Date().toISOString()), born.get(o)!);
const members: Member[] = [
  { id: 'm-gm', groupId: 'g-mat', name: '외할머니', status: 'active' },
  { id: 'm-gf', groupId: 'g-mat', name: '외할아버지', status: 'active' },
  { id: 'm-aunt', groupId: 'g-mat', name: '이모', status: 'active' },
  // 올리기 권한 가족(배우자). 실제로는 부모가 기기에 권한을 준다
  { id: 'm-dad', groupId: 'g-mat', name: '하린 아빠', status: 'active', uploader: true },
  { id: 'm-pgm', groupId: 'g-pat', name: '할머니', status: 'active' },
  { id: 'm-dgm', groupId: 'g-dy', name: '할머니', status: 'active' },
  { id: 'm-dmom', groupId: 'g-dy', name: '도윤 엄마', status: 'active', uploader: true },
];
const shares: Share[] = [
  { code: 'Harin001', groupIds: ['g-mat'], createdAt: Date.now() },
  { code: 'Harin002', groupIds: ['g-mat'], createdAt: Date.now() - 73 * HOUR },
  { code: 'Harin003', groupIds: ['g-pat'], createdAt: Date.now() },
  { code: 'Sms00001', groupIds: ['g-mat'], createdAt: Date.now(), targetMemberId: 'm-gm' },
  { code: 'Closed01', groupIds: ['g-mat'], createdAt: Date.now(), closed: true },
  { code: 'Doyun001', groupIds: ['g-dy'], createdAt: Date.now() },
];
// 기기(출입증) × 가족방마다 하나
const devices = new Map<string, Device>();
// 그룹별 공개·승인 대기의 공유 묶음은 목록(listMedia)만 흉내 낸다(나머지 규칙은 DB 검사 rls.sql이 맡는다)
const media: (MediaItem & { status: 'uploading' | 'ready'; uploader: string; groupIds: string[]; childIds: string[]; bytes: number })[] = [];
const deviceOf = (pass: Pass, familyId: string) => devices.get(key(pass, familyId));
const canUpload = (d: Device | undefined) => !!d && d.status === 'active' && !!d.canUpload;
// 반응: `${사진}|${구성원}|${종류}`, 한마디: 사진·구성원·시각
const reactions = new Set<string>();
// 반응 키 → 남긴 시각(최근 반응 목록용)
const reactedAt = new Map<string, number>();
// 부모 → 최근 반응을 마지막으로 연 때
const seenAt = new Map<string, number>();
// 부모: 세션(access) → 가족방·역할
const parents = new Map<string, { familyId: string; role: 'mom' | 'dad'; since?: number; id?: string }>();
// 엄빠 초대 링크(공동 관리자): 코드 → 가족방·만든 사람·만든 때·쓴 때
const parentInvites: { code: string; familyId: string; by: string; at: number; usedAt?: number }[] = [];
const familyParentsOf = (fam: string) => [...parents].filter(([, p]) => p.familyId === fam);
// 가족도 사진 저장하기(가족방별)
const downloads: Record<string, boolean> = {};
const used: Record<string, number> = {};
// 지운 한마디는 deleted로 남김(DB처럼 하루 30개 한도엔 셈)
const comments: { id: string; mediaId: string; memberId: string; at: number; body: string; deleted?: boolean }[] = [];
// 보신 기록: `사진|구성원` (넣은 순서 = 처음 본 순)
const views = new Set<string>();
const familyOf = (s: Share) => groups.find((g) => g.id === s.groupIds[0])!.familyId;
const key = (pass: Pass, familyId: string) => `${pass.access}|${familyId}`;
function meOf(d: Device | undefined): EntryMe | null {
  if (!d) return null;
  const m = members.find((x) => x.id === d.memberId);
  return { device: d.status, member: m?.status ?? null, name: m?.name ?? d.requestedName ?? null };
}

const newOpen = (s: Share) => s.createdAt + 72 * HOUR > Date.now() && !s.usedAt;

/** 볼 수 있는 사진이면 그 가족방의 내 구성원 id, 아니면 403 */
/** 가족방의 반응·한마디(승인된 가족만, 최근 것부터) */
function activityOf(familyId: string): ActivityItem[] {
  const name = (id: string) => members.find((m) => m.id === id && m.status === 'active')?.name;
  const thumb = (id: string) => media.find((x) => x.id === id && x.family_id === familyId && x.status === 'ready')?.thumb_key;
  const out: ActivityItem[] = [];
  for (const k of reactions) {
    const [mediaId, memberId, kind] = k.split('|');
    const who = name(memberId), t = thumb(mediaId);
    if (who && t !== undefined) out.push({ type: 'reaction', kind: kind as ReactionKind, body: null, at: new Date(reactedAt.get(k) ?? 0).toISOString(), who, media_id: mediaId, thumb_key: t });
  }
  for (const c of comments) {
    if (c.deleted) continue;
    const who = name(c.memberId), t = thumb(c.mediaId);
    if (who && t !== undefined) out.push({ type: 'comment', kind: null, body: c.body, at: new Date(c.at).toISOString(), who, media_id: c.mediaId, thumb_key: t });
  }
  return out.sort((a, b) => (a.at < b.at ? 1 : -1));
}

function viewer(pass: Pass, mediaId: string): string {
  const x = media.find((y) => y.id === mediaId && y.status === 'ready');
  const d = x && deviceOf(pass, x.family_id);
  const active = members.find((m) => m.id === d?.memberId)?.status === 'active';
  if (!x || !d || d.status !== 'active' || !d.memberId || !active) throw new BackendError('not_allowed', 403, '42501');
  return d.memberId;
}

/** 부모 계정 반응·한마디는 구성원 자리에 'p:<계정>'으로 둔다(DB의 parent_user_id 흉내) */
const parentKey = (pass: Pass) => `p:${pass.access}`;
// 한마디 쓴 사람 이름: 부모 키면 엄마·아빠, 아니면 승인된 구성원 이름(내보낸 사람은 null)
function authorName(id: string): string | null {
  if (id.startsWith('p:')) return parents.get(id.slice(2))?.role === 'dad' ? '아빠' : '엄마';
  return members.find((m) => m.id === id && m.status === 'active')?.name ?? null;
}
// 내가 쓴 한마디로 칠 작성자(DB sp_device_members처럼 활성 기기·승인된 구성원, 그리고 내 부모 계정)
function myAuthors(pass: Pass): Set<string> {
  const out = new Set<string>([parentKey(pass)]);
  for (const [k, d] of devices) {
    if (k.startsWith(`${pass.access}|`) && d.status === 'active' && d.memberId && members.find((m) => m.id === d.memberId)?.status === 'active') out.add(d.memberId);
  }
  return out;
}
function parentMedia(pass: Pass, mediaId: string): void {
  const fam = parents.get(pass.access)?.familyId;
  if (!fam || !media.some((y) => y.id === mediaId && y.status === 'ready' && y.family_id === fam)) throw new BackendError('not_allowed', 403, '42501');
}

/** listMedia·countMedia 공통: 볼 수 있는 올린 사진, 가족방·아이·한 장·커서로 거른 뒤 찍은 날·id 내림차순 */
function visibleMedia(pass: Pass, opts: MediaQuery) {
  const parent = parents.get(pass.access);
  const c = opts.before ?? opts.after;
  return media
    .filter((x) => x.status === 'ready' && (!opts.familyId || x.family_id === opts.familyId) && (!opts.childId || x.childIds.includes(opts.childId)) && (!opts.id || x.id === opts.id) && (!opts.takenFrom || Date.parse(x.taken_at) >= Date.parse(opts.takenFrom)) && (!opts.takenBefore || Date.parse(x.taken_at) < Date.parse(opts.takenBefore)))
    .filter((x) => !c || (opts.before ? newerFirst(x, { taken_at: c.takenAt, id: c.id }) > 0 : newerFirst(x, { taken_at: c.takenAt, id: c.id }) < 0))
    .filter((x) => {
      if (parent) return x.family_id === parent.familyId;
      if (isClosing(x.family_id)) return false;
      const d = deviceOf(pass, x.family_id);
      const mem = members.find((m) => m.id === d?.memberId);
      if (d?.status !== 'active') return false;
      // 승인 대기는 들어온 링크의 사진 묶음만(DB sp_can_view_media와 같게)
      if (mem?.status === 'pending') return !!shares.find((s) => s.code === mem.entryShare)?.mediaIds?.includes(x.id);
      // 올리기 권한 가족은 모든 그룹 사진을 본다
      return mem?.status === 'active' && (canUpload(d) || x.groupIds.includes(mem.groupId));
    })
    .sort(newerFirst);
}
/** 찍은 날·id 내림차순 비교(앞이 더 최근이면 음수) */
// 시각은 글자가 아니라 시각으로(달 카드 커서는 +09:00, 사진은 Z라 글자로 비교하면 서울 1일 0~9시가 틀림)
const newerFirst = (a: { taken_at: string; id: string }, b: { taken_at: string; id: string }) => {
  const ta = Date.parse(a.taken_at), tb = Date.parse(b.taken_at);
  return ta === tb ? (a.id < b.id ? 1 : a.id > b.id ? -1 : 0) : ta < tb ? 1 : -1;
};

export function createMockBackend(): Backend {
  return {
    async signInAnonymously(): Promise<Pass> {
      const id = crypto.randomUUID();
      return { access: id, refresh: id, expiresAt: Math.floor(Date.now() / 1000) + 365 * 24 * 3600 };
    },
    async refresh(pass) {
      return pass;
    },
    async entryInfo(pass, code): Promise<EntryInfo> {
      const s = shares.find((x) => x.code === code && !x.revoked);
      if (!s) return { result: 'not_found' };
      const me = pass ? meOf(devices.get(key(pass, familyOf(s)))) : null;
      if (s.closed || isClosing(familyOf(s))) return { result: 'closed', me };
      if (s.targetMemberId && (s.usedAt || s.createdAt + 72 * HOUR <= Date.now())) return { result: 'expired', me };
      return {
        result: 'ok',
        me,
        child_name: firstChild(familyOf(s)),
        text_size_mode: sizeModes[familyOf(s)] ?? 'relation',
        new_entry_open: newOpen(s),
        target_member_id: s.targetMemberId ?? null,
        groups: groups
          .filter((g) => s.groupIds.includes(g.id))
          .map((g) => ({
            id: g.id,
            name: g.name,
            hint: g.hint,
            members: members.filter((m) => m.groupId === g.id && m.status === 'active').map((m) => ({ id: m.id, name: m.name })),
          })),
      };
    },
    async enter(pass, i): Promise<EnterResult> {
      if (!/^[0-9]{4}$/.test(i.password) || !i.memberId === !i.newName) return { result: 'bad_request' };
      const s = shares.find((x) => x.code === i.code && !x.revoked);
      if (!s) return { result: 'not_found' };
      if (s.closed || isClosing(familyOf(s))) return { result: 'closed' };
      const k = key(pass, familyOf(s));
      const d = devices.get(k);
      // 마지막으로 들어가려던 가족방이 목록 끝에 오게(DB의 last_seen_at 순서와 같게)
      if (d) {
        devices.delete(k);
        devices.set(k, d);
      }
      if (d?.status === 'revoked') return { result: 'revoked' };
      if (d?.status === 'pending') return { result: 'needs_approval' };
      let groupId: string;
      if (i.memberId) {
        const m = members.find((x) => x.id === i.memberId && x.status === 'active');
        if (!m || !s.groupIds.includes(m.groupId)) return { result: 'bad_request' };
        const old = s.createdAt + 72 * HOUR <= Date.now();
        if (s.targetMemberId && (s.targetMemberId !== m.id || s.usedAt || old)) return { result: s.usedAt || old ? 'expired' : 'bad_request' };
        groupId = m.groupId;
      } else {
        if (!newOpen(s) || s.targetMemberId) return { result: 'expired' };
        if (!i.groupId || !s.groupIds.includes(i.groupId)) return { result: 'bad_request' };
        groupId = i.groupId;
      }
      const dev: Device = d ?? { id: crypto.randomUUID(), familyId: familyOf(s), status: 'active', failures: new Map() };
      const fails = dev.failures.get(groupId) ?? [];
      const last = fails.at(-1) ?? 0;
      if (fails.length > 0 && fails.length % 3 === 0 && last > Date.now() - 30_000) {
        return { result: 'locked', retry_after: Math.ceil((last + 30_000 - Date.now()) / 1000) };
      }
      const g = groups.find((x) => x.id === groupId)!;
      if (i.password !== g.password) {
        fails.push(Date.now());
        dev.failures.set(groupId, fails);
        if (fails.length >= 10) {
          dev.status = 'pending';
          dev.requestedName = i.newName ?? members.find((m) => m.id === i.memberId)?.name;
          devices.set(k, dev);
          return { result: 'needs_approval' };
        }
        devices.set(k, dev);
        return { result: 'wrong_password', hint: g.hint, attempts: fails.length };
      }
      dev.failures.delete(groupId);
      let member = members.find((m) => m.id === i.memberId);
      if (!member) {
        const name = (i.newName ?? '').trim();
        if (members.some((m) => m.groupId === groupId && m.name === name)) return { result: 'name_taken' };
        member = { id: crypto.randomUUID(), groupId, name, status: 'pending', entryShare: s.code };
        members.push(member);
      }
      dev.memberId = member.id;
      dev.canUpload = !!member.uploader;
      devices.set(k, dev);
      if (s.targetMemberId) s.usedAt = Date.now();
      return { result: member.status === 'pending' ? 'pending' : 'ok', member_id: member.id };
    },
    async me(pass): Promise<Me> {
      const families: MeFamily[] = [];
      for (const [k, d] of devices) {
        if (k.startsWith(`${pass.access}|`)) {
          families.push({ ...meOf(d)!, family_id: d.familyId, closed: isClosing(d.familyId), child_name: firstChild(d.familyId), download_allowed: !!downloads[d.familyId], children: d.status === 'active' && meOf(d)?.member === 'active' ? kids.filter((k) => k.familyId === d.familyId).map((k) => ({ name: k.name, birth_date: k.birth_date })) : null });
        }
      }
      return { families };
    },
    async createMedia(pass, m) {
      const parentOwns = parents.get(pass.access)?.familyId === m.familyId;
      if (isClosing(m.familyId) || (!parentOwns && !canUpload(deviceOf(pass, m.familyId)))) throw new BackendError('not_allowed', 403, '42501');
      if ((used[m.familyId] ?? 0) >= 5 * 1024 ** 3) throw new BackendError('storage_full', 507, 'PT507');
      const id = crypto.randomUUID();
      media.push({
        id, family_id: m.familyId, kind: m.kind, taken_at: m.takenAt, width: m.width ?? null, height: m.height ?? null,
        duration_sec: m.durationSec ?? null, status: 'uploading', uploader: pass.access, view_key: '', thumb_key: '', poster_key: null, created_at: new Date().toISOString(),
        groupIds: m.groupIds?.length ? m.groupIds : groups.filter((g) => g.familyId === m.familyId && !g.exclude).map((g) => g.id),
        childIds: m.childIds ?? [], bytes: 0,
      });
      return id;
    },
    async uploadTarget(pass, id) {
      const x = media.find((y) => y.id === id && y.status === 'uploading' && y.uploader === pass.access);
      const ok = x && (parents.get(pass.access)?.familyId === x.family_id || canUpload(deviceOf(pass, x.family_id)));
      return x && ok ? { family_id: x.family_id, kind: x.kind } : null;
    },
    async finishUpload(id, keys, bytes) {
      const x = media.find((y) => y.id === id && y.status === 'uploading');
      if (!x) return false;
      // 완료 때도 무료 5GB 한도(마이그레이션 20261027000004와 같게)
      if ((used[x.family_id] ?? 0) + bytes > 5 * 1024 ** 3) throw new BackendError('storage_full', 507, 'PT507');
      Object.assign(x, { status: 'ready', view_key: keys.view, thumb_key: keys.thumb, poster_key: keys.poster, bytes });
      used[x.family_id] = (used[x.family_id] ?? 0) + bytes;
      return true;
    },
    async react(pass, id, kind, on) {
      const m = viewer(pass, id);
      const k = `${id}|${m}|${kind}`;
      if (on) {
        if (!reactions.has(k)) reactedAt.set(k, Date.now());
        reactions.add(k);
      } else reactions.delete(k);
    },
    async comment(pass, id, body) {
      const m = viewer(pass, id);
      const text = body.trim();
      if (text.length < 1 || text.length > 200) throw new BackendError('bad_request', 400, '22023');
      if (comments.filter((c) => c.memberId === m && c.at > Date.now() - 86_400_000).length >= 30) {
        throw new BackendError('too_many_comments', 429, 'PT429');
      }
      comments.push({ id: crypto.randomUUID(), mediaId: id, memberId: m, at: Date.now(), body: text });
    },
    async parentReact(pass, id, kind, on) {
      parentMedia(pass, id);
      const k = `${id}|${parentKey(pass)}|${kind}`;
      if (on) {
        if (!reactions.has(k)) reactedAt.set(k, Date.now());
        reactions.add(k);
      } else reactions.delete(k);
    },
    async parentComment(pass, id, body) {
      parentMedia(pass, id);
      const text = body.trim();
      if (text.length < 1 || text.length > 200) throw new BackendError('bad_request', 400, '22023');
      if (comments.filter((c) => c.memberId === parentKey(pass) && c.at > Date.now() - 86_400_000).length >= 30) {
        throw new BackendError('too_many_comments', 429, 'PT429');
      }
      comments.push({ id: crypto.randomUUID(), mediaId: id, memberId: parentKey(pass), at: Date.now(), body: text });
    },
    async mediaMonths(pass, opts = {}) {
      // DB(sp_media_months)처럼: 볼 수 있는 사진, 서울 달, 반응·한마디 많은 순 → 최근
      const all = visibleMedia(pass, { familyId: opts.familyId, childId: opts.childId });
      const score = (id: string) => [...reactions].filter((r) => r.startsWith(`${id}|`) && authorName(r.split('|')[1])).length + comments.filter((c) => c.mediaId === id && !c.deleted && authorName(c.memberId)).length;
      const ym = (iso: string) => new Intl.DateTimeFormat('en-CA', { timeZone: 'Asia/Seoul', year: 'numeric', month: '2-digit' }).format(new Date(iso));
      const by = new Map<string, typeof all>();
      for (const x of all) by.set(ym(x.taken_at), [...(by.get(ym(x.taken_at)) ?? []), x]);
      const k = Math.min(4, Math.max(1, opts.reps ?? 3));
      return [...by]
        .sort(([a], [b]) => (a < b ? 1 : -1))
        .map(([m, xs]) => ({
          ym: m,
          n: xs.length,
          reps: [...xs].sort((a, b) => score(b.id) - score(a.id) || newerFirst(a, b)).slice(0, k).map(({ id, kind, thumb_key, width, height }) => ({ id, kind, thumb_key, width, height })),
        }));
    },
    async reactionCounts(pass, ids) {
      // DB(sp_reaction_counts)처럼 앞 200장만, 볼 수 있는 사진만(sp_can_view_media 흉내)
      ids = ids.slice(0, 200).filter((id) => {
        try {
          if (parents.has(pass.access)) parentMedia(pass, id);
          else viewer(pass, id);
          return true;
        } catch {
          return false;
        }
      });
      const out = new Map<string, ReactionCount>();
      const mineIds = new Set([...devices].filter(([k]) => k.startsWith(`${pass.access}|`)).map(([, d]) => d.memberId));
      mineIds.add(parentKey(pass));
      const add = (mediaId: string, kind: ReactionCount['kind'], member: string) => {
        const key = `${mediaId}|${kind}`;
        const c = out.get(key) ?? { media_id: mediaId, kind, n: 0, mine: false };
        c.n++;
        c.mine ||= mineIds.has(member);
        out.set(key, c);
      };
      for (const r of reactions) {
        const [mediaId, member, kind] = r.split('|');
        if (ids.includes(mediaId)) add(mediaId, kind as ReactionCount['kind'], member);
      }
      for (const c of comments) if (!c.deleted && ids.includes(c.mediaId) && authorName(c.memberId)) add(c.mediaId, 'comment', c.memberId);
      return [...out.values()];
    },
    async deleteComment(pass, commentId) {
      const mine = myAuthors(pass);
      const c = comments.find((x) => x.id === commentId && !x.deleted && mine.has(x.memberId));
      if (!c) throw new BackendError('not_allowed', 403, '42501');
      c.deleted = true;
    },
    async noteViews(pass, ids) {
      for (const id of ids.slice(0, 50)) {
        try {
          views.add(`${id}|${viewer(pass, id)}`);
        } catch {
          // 볼 수 없는 사진은 건너뜀(DB처럼 조용히)
        }
      }
    },
    async mediaViewers(pass, id) {
      // DB처럼 자기 가족방 사진이 아니면 빈 목록
      try {
        parentMedia(pass, id);
      } catch {
        return [];
      }
      return [...views].filter((k) => k.startsWith(`${id}|`)).map((k) => authorName(k.split('|')[1])).filter((x): x is string => !!x).slice(0, 100);
    },
    async mediaComments(pass, id) {
      try {
        if (parents.has(pass.access)) parentMedia(pass, id);
        else viewer(pass, id);
      } catch {
        return [];
      }
      const mine = myAuthors(pass);
      return comments
        .filter((c) => !c.deleted && c.mediaId === id && authorName(c.memberId))
        .map((c) => ({ id: c.id, name: authorName(c.memberId)!, body: c.body, created_at: new Date(c.at).toISOString(), mine: mine.has(c.memberId) }))
        .reverse()
        .slice(0, 100);
    },
    parentAuthorizeUrl(_provider, redirectTo) {
      // 개발용: 제공자 화면 없이 바로 돌아온다
      return `${redirectTo}?code=dev-${crypto.randomUUID()}`;
    },
    async parentExchange(code) {
      if (!code.startsWith('dev-')) return null;
      return { access: `parent-${code}`, refresh: `parent-${code}`, expiresAt: Math.floor(Date.now() / 1000) + 365 * 24 * 3600 };
    },
    async parentLogout() {},
    async familyAdmin(pass) {
      const fam = parents.get(pass.access)?.familyId;
      const gs = groups.filter((g) => g.familyId === fam);
      const now = new Date().toISOString();
      return {
        groups: gs.map((g) => ({ id: g.id, name: g.name, include_by_default: !g.exclude, password_hint: g.hint || null })),
        members: members
          .filter((m) => gs.some((g) => g.id === m.groupId))
          .map((m) => ({ id: m.id, group_id: m.groupId, display_name: m.name, status: m.status, pending_until: m.status === 'pending' ? new Date(Date.now() + 3 * 86_400_000).toISOString() : null, install_help_at: m.helpAt ? new Date(m.helpAt).toISOString() : null, created_at: bornAt(m) })),
        devices: [...devices.values()]
          .filter((d) => d.familyId === fam)
          .map((d) => ({ id: d.id, member_id: d.memberId ?? null, status: d.status, requested_name: d.requestedName ?? null, requested_group_id: null, requested_member_id: null, can_upload: !!d.canUpload, last_seen_at: now, created_at: bornAt(d) })),
      };
    },
    async setMemberStatus(pass, id, status) {
      const fam = parents.get(pass.access)?.familyId;
      const m = members.find((x) => x.id === id && (x.status === 'pending' || (status === 'rejected' && x.status === 'active')) && groups.find((g) => g.id === x.groupId)?.familyId === fam);
      if (!m) throw new BackendError('not_found', 404);
      m.status = status;
      if (status === 'rejected') for (const d of devices.values()) if (d.memberId === id) d.status = 'revoked';
    },
    async renameMember(pass, id, name) {
      // DB(members_parent_write + unique(group_id, display_name))처럼: 내 가족방 승인된 사람만, 같은 그룹 같은 이름이면 409
      const fam = parents.get(pass.access)?.familyId;
      const m = members.find((x) => x.id === id && x.status === 'active' && groups.find((g) => g.id === x.groupId)?.familyId === fam);
      if (!m) throw new BackendError('not_found', 404);
      if (members.some((x) => x.id !== id && x.groupId === m.groupId && x.name === name)) throw new BackendError('duplicate', 409, '23505');
      m.name = name;
    },
    async setDeviceStatus(pass, id, status) {
      const fam = parents.get(pass.access)?.familyId;
      const d = [...devices.values()].find((x) => x.id === id && x.familyId === fam && x.status === 'pending');
      if (!d) throw new BackendError('not_found', 404);
      d.status = status;
      if (status === 'active') d.failures.clear();
    },
    async setUploadAllowed(pass, memberId, on) {
      const fam = parents.get(pass.access)?.familyId;
      const ds = [...devices.values()].filter((d) => d.familyId === fam && d.memberId === memberId && d.status === 'active');
      if (!ds.length) throw new BackendError('not_found', 404);
      ds.forEach((d) => (d.canUpload = on));
    },
    async setDownloadAllowed(pass, familyId, on) {
      if (parents.get(pass.access)?.familyId !== familyId) throw new BackendError('not_found', 404);
      downloads[familyId] = on;
    },
    async addGroup(pass, g) {
      const fam = parents.get(pass.access)?.familyId;
      if (!fam) throw new BackendError('not_allowed', 403, '42501');
      if (!/^[0-9]{4}$/.test(g.password)) throw new BackendError('password_4_digits', 400, '22023');
      const mine = groups.filter((x) => x.familyId === fam);
      if (mine.length >= 10) throw new BackendError('group_limit', 409, 'PT409');
      if (mine.some((x) => x.name === g.name)) throw new BackendError('duplicate', 409, '23505');
      const id = crypto.randomUUID();
      groups.push({ id, familyId: fam, name: g.name, hint: g.hint ?? '', password: g.password, exclude: !g.includeByDefault });
      return id;
    },
    async updateGroup(pass, groupId, patch) {
      const fam = parents.get(pass.access)?.familyId;
      const g = groups.find((x) => x.id === groupId && x.familyId === fam);
      if (!g) throw new BackendError('not_found', 404);
      if (patch.name !== undefined && groups.some((x) => x.familyId === fam && x.id !== groupId && x.name === patch.name)) throw new BackendError('duplicate', 409, '23505');
      if (patch.name !== undefined) g.name = patch.name;
      if (patch.include_by_default !== undefined) g.exclude = !patch.include_by_default;
    },
    async setGroupPassword(pass, groupId, password, hint) {
      const g = groups.find((x) => x.id === groupId && x.familyId === parents.get(pass.access)?.familyId);
      if (!g) throw new BackendError('not_allowed', 403, '42501');
      if (!/^[0-9]{4}$/.test(password)) throw new BackendError('password_4_digits', 400, '22023');
      Object.assign(g, { password, hint: hint ?? '' });
    },
    async resetGroupLinks(pass, groupId) {
      const fam = parents.get(pass.access)?.familyId;
      if (!fam || isClosing(fam) || !groups.some((x) => x.id === groupId && x.familyId === fam)) throw new BackendError('not_allowed', 403, '42501');
      for (const s of shares) if (s.groupIds.includes(groupId)) s.revoked = true;
    },
    async requestDelete(pass) {
      const fam = parents.get(pass.access)?.familyId;
      if (!fam) throw new BackendError('parent_only', 403, '42501');
      // 함께 관리하는 엄빠가 있으면 나만 빠진다(DB sp_request_delete와 같게)
      if (familyParentsOf(fam).length > 1) {
        parents.delete(pass.access);
        return null;
      }
      closingAt[fam] ??= Date.now() + 72 * HOUR;
      return new Date(closingAt[fam]).toISOString();
    },
    async familyParents(pass) {
      const fam = parents.get(pass.access)?.familyId;
      if (!fam) return { parents: [], invite: null };
      const list = familyParentsOf(fam)
        .map(([access, p]) => ({ user_id: (p.id ??= crypto.randomUUID()), role: p.role, display_name: p.role === 'mom' ? '엄마' : '아빠', since: new Date(p.since ?? 0).toISOString(), me: access === pass.access }))
        .sort((a, b) => Number(b.me) - Number(a.me) || a.since.localeCompare(b.since));
      const inv = parentInvites.filter((i) => i.familyId === fam && !i.usedAt && i.at + 72 * HOUR > Date.now()).at(-1);
      return { parents: list, invite: inv ? { code: inv.code, expires_at: new Date(inv.at + 72 * HOUR).toISOString() } : null };
    },
    async createParentInvite(pass) {
      const fam = parents.get(pass.access)?.familyId;
      if (!fam || isClosing(fam)) throw new BackendError('not_allowed', 403, '42501');
      if (familyParentsOf(fam).length >= 2) throw new BackendError('parents_full', 409, '23505');
      for (let i = parentInvites.length - 1; i >= 0; i--) if (parentInvites[i].familyId === fam && !parentInvites[i].usedAt) parentInvites.splice(i, 1);
      const abc = 'ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz23456789';
      const code = [...crypto.getRandomValues(new Uint8Array(8))].map((b) => abc[b % abc.length]).join('');
      parentInvites.push({ code, familyId: fam, by: pass.access, at: Date.now() });
      return code;
    },
    async parentInviteInfo(_pass, code): Promise<ParentInviteInfo> {
      const i = parentInvites.find((x) => x.code === code);
      if (!i) return { result: 'not_found' };
      const result = isClosing(i.familyId) ? 'closed' : i.usedAt || i.at + 72 * HOUR <= Date.now() ? 'expired' : familyParentsOf(i.familyId).length >= 2 ? 'full' : 'ok';
      const mine = !!_pass && parents.get(_pass.access)?.familyId === i.familyId;
      if (result !== 'ok') return { result, mine };
      return { result, mine, child_name: kids.find((k) => k.familyId === i.familyId)?.name, inviter_role: parents.get(i.by)?.role, taken_roles: familyParentsOf(i.familyId).map(([, p]) => p.role) };
    },
    async acceptParentInvite(pass, code, role) {
      if (!pass.access.startsWith('parent-')) throw new BackendError('parent_login_required', 403, '42501');
      const i = parentInvites.find((x) => x.code === code);
      if (!i) throw new BackendError('not_found', 404, 'P0002');
      if (i.usedAt || i.at + 72 * HOUR <= Date.now() || isClosing(i.familyId)) throw new BackendError('expired', 400, '22023');
      if (parents.has(pass.access)) throw new BackendError('family_exists', 409, '23505');
      if (familyParentsOf(i.familyId).length >= 2) throw new BackendError('parents_full', 409, '23505');
      if (familyParentsOf(i.familyId).some(([, p]) => p.role === role)) throw new BackendError('role_taken', 400, '22023');
      parents.set(pass.access, { familyId: i.familyId, role, since: Date.now() });
      i.usedAt = Date.now();
      return i.familyId;
    },
    async removeCoparent(pass, userId) {
      const fam = parents.get(pass.access)?.familyId;
      // 화면에 내보낸 id(user_id)는 mock에선 출입증과 따로 붙인 uuid
      const target = familyParentsOf(fam ?? '').find(([access, p]) => p.id === userId && access !== pass.access);
      if (!fam || !target) throw new BackendError('not_allowed', 403, '42501');
      parents.delete(target[0]);
    },
    async restoreFamily(pass) {
      const fam = parents.get(pass.access)?.familyId;
      if (!fam || !(closingAt[fam] > Date.now())) throw new BackendError('not_closing', 400, '22023');
      delete closingAt[fam];
    },
    async setTextSizeMode(pass, familyId, mode) {
      if (parents.get(pass.access)?.familyId !== familyId) throw new BackendError('not_found', 404);
      sizeModes[familyId] = mode;
    },
    async addChild(pass, familyId, name, birthDate, showHealth) {
      if (parents.get(pass.access)?.familyId !== familyId) throw new BackendError('forbidden', 403, '42501');
      if (kids.filter((k) => k.familyId === familyId).length >= 10) throw new BackendError('children_limit', 400, '22023');
      kids.push({ id: crypto.randomUUID(), familyId, name, birth_date: birthDate, show_health: showHealth });
    },
    async updateChild(pass, childId, name, birthDate) {
      const k = kids.find((x) => x.id === childId && x.familyId === parents.get(pass.access)?.familyId);
      if (!k) throw new BackendError('not_found', 404);
      Object.assign(k, { name, birth_date: birthDate });
    },
    async createShare(pass, groupIds, target, mediaIds = []) {
      const fam = parents.get(pass.access)?.familyId;
      if (!fam || isClosing(fam) || !groupIds.length || groupIds.some((id) => groups.find((g) => g.id === id)?.familyId !== fam) || mediaIds.some((id) => media.find((x) => x.id === id)?.family_id !== fam)) {
        throw new BackendError('bad_request', 400, '22023');
      }
      const abc = 'ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz23456789';
      const code = [...crypto.getRandomValues(new Uint8Array(8))].map((b) => abc[b % abc.length]).join('');
      shares.push({ code, groupIds, createdAt: Date.now(), targetMemberId: target, mediaIds });
      return code;
    },
    async parentHome(pass): Promise<ParentHome> {
      const p = parents.get(pass.access);
      if (!p) return { family_id: null };
      const ready = media.filter((x) => x.family_id === p.familyId && x.status === 'ready');
      return {
        family_id: p.familyId, role: p.role, closing: isClosing(p.familyId), new_activity: activityOf(p.familyId).filter((x) => Date.parse(x.at) > (seenAt.get(pass.access) ?? 0)).length,
        waiting: members.filter((m) => m.status === 'pending' && groups.find((g) => g.id === m.groupId)?.familyId === p.familyId).length + [...devices.values()].filter((d) => d.familyId === p.familyId && d.status === 'pending').length, delete_after: isClosing(p.familyId) ? new Date(closingAt[p.familyId]).toISOString() : null, download_allowed: !!downloads[p.familyId],
        storage_used_bytes: (used[p.familyId] ?? 0) + MOCK_USED, photo_count: ready.filter((x) => x.kind === 'photo').length, video_count: ready.filter((x) => x.kind === 'video').length,
        provider: null, text_size_mode: sizeModes[p.familyId] ?? 'relation',
        children: kids.filter((k) => k.familyId === p.familyId).map(({ id, name, birth_date, show_health }) => ({ id, name, birth_date, show_health })),
      };
    },
    async createFamily(pass, f) {
      if (!pass.access.startsWith('parent-')) throw new BackendError('parent_login_required', 403, '42501');
      if (parents.has(pass.access)) throw new BackendError('family_exists', 409, '23505');
      if (!/^[0-9]{4}$/.test(f.password)) throw new BackendError('password_4_digits', 400, '22023');
      const id = crypto.randomUUID();
      kids.push({ id: crypto.randomUUID(), familyId: id, name: f.childName, birth_date: f.birthDate, show_health: true });
      groups.push({ id: crypto.randomUUID(), familyId: id, name: '가족', hint: f.hint ?? '', password: f.password });
      parents.set(pass.access, { familyId: id, role: f.role, since: Date.now() });
      return id;
    },
    async listMedia(pass, opts = {}) {
      const all = visibleMedia(pass, opts);
      // after: 그보다 최근 것 중 가까운 limit개(내림차순 유지)
      const picked = opts.after ? all.slice(Math.max(0, all.length - (opts.limit ?? 60))) : all.slice(0, opts.limit ?? 60);
      return picked.map(({ status: _s, uploader: _u, groupIds: _g, childIds: _c, bytes: _b, ...rest }) => rest);
    },
    async countMedia(pass, opts = {}) {
      return visibleMedia(pass, opts).length;
    },
    // 정리 작업은 mock에선 할 일이 없다(실제 규칙은 DB 검사와 cleanup 단위 검사가 맡는다)
    purgeDeletedFamilies: async () => [],
    cleanupStaleUploads: async () => 0,
    r2CleanupTake: async () => [],
    r2CleanupDone: async () => {},
    async requestInstallHelp(pass, familyId) {
      const d = deviceOf(pass, familyId);
      const m = members.find((x) => x.id === d?.memberId && x.status === 'active');
      if (!d || d.status !== 'active' || !m) throw new BackendError('not_allowed', 403, '42501');
      m.helpAt = Date.now();
    },
    async healthDone(pass, childId) {
      const k = kids.find((x) => x.id === childId && x.familyId === parents.get(pass.access)?.familyId);
      return k ? [...(healthDone.get(childId) ?? new Map())].map(([item_key, done_on]) => ({ item_key, done_on })) : [];
    },
    async setHealthDone(pass, familyId, childId, add, remove, today) {
      if (!kids.some((x) => x.id === childId && x.familyId === familyId && familyId === parents.get(pass.access)?.familyId)) throw new BackendError('not_allowed', 403, '42501');
      const m = healthDone.get(childId) ?? new Map<string, string>();
      for (const k of add) if (!m.has(k)) m.set(k, today);
      for (const k of remove) m.delete(k);
      healthDone.set(childId, m);
    },
    async setShowHealth(pass, childIds, on) {
      const fam = parents.get(pass.access)?.familyId;
      for (const k of kids) if (k.familyId === fam && childIds.includes(k.id)) k.show_health = on;
    },
    async parentActivity(pass) {
      const fam = parents.get(pass.access)?.familyId;
      if (!fam) return null;
      return { seen_at: new Date(seenAt.get(pass.access) ?? 0).toISOString(), read_at: new Date().toISOString(), items: activityOf(fam).slice(0, 50) };
    },
    async markActivitySeen(pass, readAt) {
      seenAt.set(pass.access, Math.max(seenAt.get(pass.access) ?? 0, Math.min(Date.parse(readAt), Date.now())));
    },
    async mediaInfo(pass, id) {
      const fam = parents.get(pass.access)?.familyId;
      const x = media.find((y) => y.id === id && y.status === 'ready' && y.family_id === fam);
      if (!x) return null;
      const { status: _s, uploader: _u, groupIds, childIds, bytes: _b, ...item } = x;
      return { item, group_ids: [...groupIds], child_ids: [...childIds] };
    },
    async updateMedia(pass, id, u) {
      const fam = parents.get(pass.access)?.familyId;
      const x = media.find((y) => y.id === id && y.status === 'ready' && y.family_id === fam);
      if (!x || isClosing(fam!)) throw new BackendError('not_allowed', 403, '42501');
      const okGroups = u.groupIds.length > 0 && u.groupIds.every((g) => groups.some((y) => y.id === g && y.familyId === fam));
      const okKids = u.childIds.every((c) => kids.some((k) => k.id === c && k.familyId === fam));
      if (!okGroups || !okKids) throw new BackendError('bad_request', 400, '22023');
      Object.assign(x, { taken_at: u.takenAt, groupIds: [...u.groupIds], childIds: [...u.childIds] });
    },
    async deleteMedia(pass, id) {
      const fam = parents.get(pass.access)?.familyId;
      const i = media.findIndex((y) => y.id === id && y.family_id === fam && y.status === 'ready');
      if (i < 0 || isClosing(fam!)) throw new BackendError('not_allowed', 403, '42501');
      used[fam!] = Math.max(0, (used[fam!] ?? 0) - media[i].bytes);
      media.splice(i, 1);
      for (let j = comments.length - 1; j >= 0; j--) if (comments[j].mediaId === id) comments.splice(j, 1);
      for (const k of [...reactions]) if (k.startsWith(`${id}|`)) reactions.delete(k);
      for (const k of [...views]) if (k.startsWith(`${id}|`)) views.delete(k);
    },
  };
}
