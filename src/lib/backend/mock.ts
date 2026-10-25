// 개발·검사용 메모리 백엔드. 서버 프로세스가 살아 있는 동안만 기억한다.
// 실제 규칙(그룹 경보, 승인 대기 3일 등)은 DB가 강제하고, 여기선 화면 흐름 확인에 필요한 만큼만 흉내 낸다.
// 운영에서는 index.ts가 이 구현을 쓰지 못하게 막는다.
import type { Backend, EnterResult, EntryInfo, EntryMe, MediaItem, Me, MeFamily, Pass } from './types';
import { BackendError } from './supabase';

interface Group { id: string; familyId: string; name: string; hint: string; password: string }
interface Member { id: string; groupId: string; name: string; status: 'active' | 'pending' | 'rejected'; uploader?: boolean }
interface Share { code: string; groupIds: string[]; createdAt: number; targetMemberId?: string; usedAt?: number; closed?: boolean }
interface Device { familyId: string; status: 'active' | 'pending' | 'revoked'; memberId?: string; requestedName?: string; failures: Map<string, number[]>; canUpload?: boolean }

const HOUR = 3600_000;
// 하린이네(외가·친가)와 도윤이네(외할머니의 다른 손주). 외할머니 한 기기로 두 가족방에 들어가는 흐름을 본다
// 가족방 id는 실제처럼 uuid(API가 형식을 검사한다)
const HARIN = '00000000-0000-4000-8000-00000000f001';
const DOYUN = '00000000-0000-4000-8000-00000000f002';
const children: Record<string, string> = { [HARIN]: '하린', [DOYUN]: '도윤' };
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
// shortcut: 그룹별 공개 범위는 흉내 내지 않고 가족방 단위로만 보여 준다. 실제 규칙은 DB 검사(rls.sql)가 맡는다
const media: (MediaItem & { status: 'uploading' | 'ready'; uploader: string })[] = [];
const deviceOf = (pass: Pass, familyId: string) => devices.get(key(pass, familyId));
const canUpload = (d: Device | undefined) => !!d && d.status === 'active' && !!d.canUpload;
const familyOf = (s: Share) => groups.find((g) => g.id === s.groupIds[0])!.familyId;
const key = (pass: Pass, familyId: string) => `${pass.access}|${familyId}`;
function meOf(d: Device | undefined): EntryMe | null {
  if (!d) return null;
  const m = members.find((x) => x.id === d.memberId);
  return { device: d.status, member: m?.status ?? null, name: m?.name ?? d.requestedName ?? null };
}

const newOpen = (s: Share) => s.createdAt + 72 * HOUR > Date.now() && !s.usedAt;

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
      const s = shares.find((x) => x.code === code);
      if (!s) return { result: 'not_found' };
      const me = pass ? meOf(devices.get(key(pass, familyOf(s)))) : null;
      if (s.closed) return { result: 'closed', me };
      if (s.targetMemberId && s.usedAt) return { result: 'expired', me };
      return {
        result: 'ok',
        me,
        child_name: children[familyOf(s)],
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
      const s = shares.find((x) => x.code === i.code);
      if (!s) return { result: 'not_found' };
      if (s.closed) return { result: 'closed' };
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
        if (s.targetMemberId && (s.targetMemberId !== m.id || s.usedAt)) return { result: s.usedAt ? 'expired' : 'bad_request' };
        groupId = m.groupId;
      } else {
        if (!newOpen(s) || s.targetMemberId) return { result: 'expired' };
        if (!i.groupId || !s.groupIds.includes(i.groupId)) return { result: 'bad_request' };
        groupId = i.groupId;
      }
      const dev: Device = d ?? { familyId: familyOf(s), status: 'active', failures: new Map() };
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
          families.push({ ...meOf(d)!, family_id: d.familyId, closed: false, child_name: children[d.familyId] });
        }
      }
      return { families };
    },
    async createMedia(pass, m) {
      if (!canUpload(deviceOf(pass, m.familyId))) throw new BackendError('not_allowed', 403, '42501');
      const id = crypto.randomUUID();
      media.push({
        id, family_id: m.familyId, kind: m.kind, taken_at: m.takenAt, width: m.width ?? null, height: m.height ?? null,
        duration_sec: m.durationSec ?? null, status: 'uploading', uploader: pass.access,
      });
      return id;
    },
    async uploadTarget(pass, id) {
      const x = media.find((y) => y.id === id && y.status === 'uploading' && y.uploader === pass.access);
      return x && canUpload(deviceOf(pass, x.family_id)) ? { family_id: x.family_id, kind: x.kind } : null;
    },
    async finishUpload(id) {
      const x = media.find((y) => y.id === id && y.status === 'uploading');
      if (!x) return false;
      x.status = 'ready';
      return true;
    },
    async listMedia(pass, opts = {}) {
      return media
        .filter((x) => x.status === 'ready' && (!opts.familyId || x.family_id === opts.familyId))
        .filter((x) => {
          const d = deviceOf(pass, x.family_id);
          return d?.status === 'active' && members.find((m) => m.id === d.memberId)?.status === 'active';
        })
        .filter((x) => !opts.before || x.taken_at < opts.before)
        .sort((a, b) => (a.taken_at < b.taken_at ? 1 : -1))
        .slice(0, opts.limit ?? 60)
        .map(({ status: _s, uploader: _u, ...rest }) => rest);
    },
  };
}
