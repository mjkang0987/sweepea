// 개발·검사용 메모리 백엔드. 서버 프로세스가 살아 있는 동안만 기억한다.
// 실제 규칙(그룹 경보, 승인 대기 3일 등)은 DB가 강제하고, 여기선 화면 흐름 확인에 필요한 만큼만 흉내 낸다.
// 운영에서는 index.ts가 이 구현을 쓰지 못하게 막는다.
import type { ActivityItem, Backend, EnterResult, EntryInfo, EntryMe, MediaItem, Me, MeFamily, ParentHome, Pass, ReactionCount, ReactionKind, TextSizeMode } from './types';
import { BackendError } from './supabase';

interface Group { id: string; familyId: string; name: string; hint: string; password: string; exclude?: boolean }
interface Member { id: string; groupId: string; name: string; status: 'active' | 'pending' | 'rejected'; uploader?: boolean }
interface Share { code: string; groupIds: string[]; createdAt: number; targetMemberId?: string; usedAt?: number; closed?: boolean; revoked?: boolean }
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
// 그룹별 공개는 목록(listMedia)만 흉내 낸다(승인 대기·공유 묶음 규칙은 DB 검사 rls.sql이 맡는다)
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
const parents = new Map<string, { familyId: string; role: 'mom' | 'dad' }>();
// 가족도 사진 저장하기(가족방별)
const downloads: Record<string, boolean> = {};
const used: Record<string, number> = {};
const comments: { mediaId: string; memberId: string; at: number; body: string }[] = [];
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
        member = { id: crypto.randomUUID(), groupId, name, status: 'pending' };
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
          families.push({ ...meOf(d)!, family_id: d.familyId, closed: isClosing(d.familyId), child_name: firstChild(d.familyId), download_allowed: !!downloads[d.familyId] });
        }
      }
      return { families };
    },
    async createMedia(pass, m) {
      const parentOwns = parents.get(pass.access)?.familyId === m.familyId;
      if (isClosing(m.familyId) || (!parentOwns && !canUpload(deviceOf(pass, m.familyId)))) throw new BackendError('not_allowed', 403, '42501');
      const id = crypto.randomUUID();
      media.push({
        id, family_id: m.familyId, kind: m.kind, taken_at: m.takenAt, width: m.width ?? null, height: m.height ?? null,
        duration_sec: m.durationSec ?? null, status: 'uploading', uploader: pass.access, view_key: '', thumb_key: '', poster_key: null,
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
      comments.push({ mediaId: id, memberId: m, at: Date.now(), body: text });
    },
    async reactionCounts(pass, ids) {
      // 볼 수 있는 사진만(DB의 sp_can_view_media 흉내)
      ids = ids.filter((id) => {
        try {
          viewer(pass, id);
          return true;
        } catch {
          return false;
        }
      });
      const out = new Map<string, ReactionCount>();
      const mineIds = new Set([...devices].filter(([k]) => k.startsWith(`${pass.access}|`)).map(([, d]) => d.memberId));
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
      for (const c of comments) if (ids.includes(c.mediaId)) add(c.mediaId, 'comment', c.memberId);
      return [...out.values()];
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
          .map((m) => ({ id: m.id, group_id: m.groupId, display_name: m.name, status: m.status, pending_until: m.status === 'pending' ? new Date(Date.now() + 3 * 86_400_000).toISOString() : null, created_at: now })),
        devices: [...devices.values()]
          .filter((d) => d.familyId === fam)
          .map((d) => ({ id: d.id, member_id: d.memberId ?? null, status: d.status, requested_name: d.requestedName ?? null, requested_group_id: null, requested_member_id: null, can_upload: !!d.canUpload, last_seen_at: now, created_at: now })),
      };
    },
    async setMemberStatus(pass, id, status) {
      const fam = parents.get(pass.access)?.familyId;
      const m = members.find((x) => x.id === id && (x.status === 'pending' || (status === 'rejected' && x.status === 'active')) && groups.find((g) => g.id === x.groupId)?.familyId === fam);
      if (!m) throw new BackendError('not_found', 404);
      m.status = status;
      if (status === 'rejected') for (const d of devices.values()) if (d.memberId === id) d.status = 'revoked';
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
      closingAt[fam] ??= Date.now() + 72 * HOUR;
      return new Date(closingAt[fam]).toISOString();
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
    async addChild(pass, familyId, name, birthDate) {
      if (parents.get(pass.access)?.familyId !== familyId) throw new BackendError('forbidden', 403, '42501');
      if (kids.filter((k) => k.familyId === familyId).length >= 10) throw new BackendError('children_limit', 400, '22023');
      kids.push({ id: crypto.randomUUID(), familyId, name, birth_date: birthDate, show_health: kids.find((k) => k.familyId === familyId)?.show_health ?? true });
    },
    async updateChild(pass, childId, name, birthDate) {
      const k = kids.find((x) => x.id === childId && x.familyId === parents.get(pass.access)?.familyId);
      if (!k) throw new BackendError('not_found', 404);
      Object.assign(k, { name, birth_date: birthDate });
    },
    async createShare(pass, groupIds, target) {
      const fam = parents.get(pass.access)?.familyId;
      if (!fam || isClosing(fam) || !groupIds.length || groupIds.some((id) => groups.find((g) => g.id === id)?.familyId !== fam)) {
        throw new BackendError('bad_request', 400, '22023');
      }
      const abc = 'ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz23456789';
      const code = [...crypto.getRandomValues(new Uint8Array(8))].map((b) => abc[b % abc.length]).join('');
      shares.push({ code, groupIds, createdAt: Date.now(), targetMemberId: target });
      return code;
    },
    async parentHome(pass): Promise<ParentHome> {
      const p = parents.get(pass.access);
      if (!p) return { family_id: null };
      const ready = media.filter((x) => x.family_id === p.familyId && x.status === 'ready');
      return {
        family_id: p.familyId, role: p.role, closing: isClosing(p.familyId), new_activity: activityOf(p.familyId).filter((x) => Date.parse(x.at) > (seenAt.get(pass.access) ?? 0)).length, delete_after: isClosing(p.familyId) ? new Date(closingAt[p.familyId]).toISOString() : null, download_allowed: !!downloads[p.familyId],
        storage_used_bytes: used[p.familyId] ?? 0, photo_count: ready.filter((x) => x.kind === 'photo').length, video_count: ready.filter((x) => x.kind === 'video').length,
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
      parents.set(pass.access, { familyId: id, role: f.role });
      return id;
    },
    async listMedia(pass, opts = {}) {
      const parent = parents.get(pass.access);
      return media
        .filter((x) => x.status === 'ready' && (!opts.familyId || x.family_id === opts.familyId))
        .filter((x) => {
          if (parent) return x.family_id === parent.familyId;
          if (isClosing(x.family_id)) return false;
          const d = deviceOf(pass, x.family_id);
          const mem = members.find((m) => m.id === d?.memberId);
          // 올리기 권한 가족은 모든 그룹 사진을 본다(DB sp_can_view_media와 같게)
          return d?.status === 'active' && mem?.status === 'active' && (canUpload(d) || x.groupIds.includes(mem.groupId));
        })
        .sort((a, b) => (a.taken_at === b.taken_at ? (a.id < b.id ? 1 : -1) : a.taken_at < b.taken_at ? 1 : -1))
        .slice(0, opts.limit ?? 60)
        .map(({ status: _s, uploader: _u, groupIds: _g, childIds: _c, bytes: _b, ...rest }) => rest);
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
      const last = comments.filter((c) => c.mediaId === id).at(-1);
      return { item, group_ids: [...groupIds], child_ids: [...childIds], latest: last ? { name: members.find((m) => m.id === last.memberId)?.name ?? '가족', body: last.body } : null };
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
    },
  };
}
