// 설정 > 가족 공통: 승인 대기 계산, 폼 동작 처리
import type { AstroCookies } from 'astro';
import { BackendError, getBackend, type FamilyAdmin } from './backend';
import { currentParent } from './pass';

const ID = /^[0-9a-f-]{36}$/;

export function summarize(a: FamilyAdmin) {
  const now = Date.now();
  const pendingMembers = a.members.filter((m) => m.status === 'pending' && (!m.pending_until || Date.parse(m.pending_until) > now));
  const pendingDevices = a.devices.filter((d) => d.status === 'pending');
  return {
    pendingMembers,
    pendingDevices,
    waiting: pendingMembers.length + pendingDevices.length,
    activeDevices: a.devices.filter((d) => d.status === 'active').length,
    groupName: (id: string | null) => a.groups.find((g) => g.id === id)?.name ?? '가족',
    memberName: (id: string | null) => a.members.find((m) => m.id === id)?.display_name ?? null,
  };
}

/** 폼 동작: member:<id>:active|rejected, device:<id>:active|revoked, share:<그룹 id>. 돌아갈 주소 */
export async function handleFamilyPost(request: Request, cookies: AstroCookies): Promise<string> {
  const pass = await currentParent(cookies);
  if (!pass) return '/login';
  const form = await request.formData().catch(() => null);
  const [kind, id, status] = String(form?.get('do') ?? '').split(':');
  if (!ID.test(id ?? '')) return '/settings/family';
  const b = getBackend();
  try {
    if (kind === 'member' && (status === 'active' || status === 'rejected')) await b.setMemberStatus(pass, id, status);
    else if (kind === 'device' && (status === 'active' || status === 'revoked')) await b.setDeviceStatus(pass, id, status);
    else if (kind === 'share') return `/settings/family?link=${await b.createShare(pass, [id])}&g=${id}#link`;
    return `/settings/family?done=${kind}-${status}`;
  } catch (e) {
    if (e instanceof BackendError && e.status < 500) return '/settings/family?done=error';
    throw e;
  }
}

export const shareUrl = (origin: string, code: string) => `${origin}/i/${code}`;

/** 문자 앱을 미리 쓴 내용으로 연다(iOS·안드로이드 둘 다 열리는 형태) */
export const smsHref = (body: string) => `sms:?&body=${encodeURIComponent(body)}`;
