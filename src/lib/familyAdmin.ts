// 설정 > 가족 공통: 승인 대기 계산, 폼 동작 처리
import type { AstroCookies } from 'astro';
import { BackendError, getBackend, type FamilyAdmin } from './backend';
import { SITE_ORIGIN } from 'astro:env/server';
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

export const LINK_COOKIE = 'sp_link';

/** 용량 표시: 1GB 미만은 MB로 */
export const sizeLabel = (bytes: number) =>
  bytes < 1024 ** 3 ? `${Math.round(bytes / 1024 ** 2)}MB` : `${(bytes / 1024 ** 3).toFixed(1)}GB`;

/** 폼 동작: member:<id>:active|rejected, device:<id>:active|revoked, share:<그룹 id>, reset:<그룹 id>(주소 다시 만들기). 돌아갈 주소.
 *  거절·내 가족 아님은 되돌릴 수 없어서 한 번 더 묻는다(confirm=1이 없으면 확인 화면으로) */
export async function handleFamilyPost(request: Request, cookies: AstroCookies): Promise<string> {
  const pass = await currentParent(cookies);
  if (!pass) return '/login';
  const form = await request.formData().catch(() => null);
  const action = String(form?.get('do') ?? '');
  const [kind, id, status] = action.split(':');
  const b = getBackend();
  // 엄빠 함께 관리 초대 링크 만들기(링크는 화면이 sp_family_parents로 다시 읽어 보여 준다)
  if (action === 'pinvite') {
    try {
      await b.createParentInvite(pass);
      return '/settings/family?done=pinvite#parents';
    } catch (e) {
      if (!(e instanceof BackendError) || e.status >= 500) throw e;
      return `/settings/family?done=${e.code === '23505' ? 'parents-full' : 'error'}`;
    }
  }
  if (!ID.test(id ?? '')) return '/settings/family';
  const irreversible = (kind === 'member' && status === 'rejected') || (kind === 'device' && status === 'revoked') || kind === 'reset' || (kind === 'parent' && status === 'removed');
  if (irreversible && form?.get('confirm') !== '1') return `/settings/family?confirm=${encodeURIComponent(action)}#confirm`;
  try {
    // 켜기·끄기: 올리기 허용(구성원 상세), 가족도 사진 저장하기(설정)
    if (kind === 'upload' && (status === 'on' || status === 'off')) {
      await b.setUploadAllowed(pass, id, status === 'on');
      return `/settings/family/member/${id}?done=upload-${status}`;
    }
    if (kind === 'download' && (status === 'on' || status === 'off')) {
      await b.setDownloadAllowed(pass, id, status === 'on');
      return `/settings?done=download-${status}`;
    }
    if (kind === 'member' && (status === 'active' || status === 'rejected')) await b.setMemberStatus(pass, id, status);
    else if (kind === 'device' && (status === 'active' || status === 'revoked')) await b.setDeviceStatus(pass, id, status);
    // 함께 관리하는 상대 엄빠 내보내기
    else if (kind === 'parent' && status === 'removed') await b.removeCoparent(pass, id);
    else if (kind === 'share' || kind === 'reset') {
      // 주소 다시 만들기: 예전 링크를 막고 새 링크를 바로 만든다
      if (kind === 'reset') await b.resetGroupLinks(pass, id);
      // 만든 링크는 주소가 아니라 잠깐 쓰는 쿠키로 넘긴다(주소로 가짜 '링크를 만들었어요' 카드를 못 띄우게)
      cookies.set(LINK_COOKIE, `${await b.createShare(pass, [id])}:${id}`, { path: '/settings', httpOnly: true, sameSite: 'lax', secure: import.meta.env.PROD, maxAge: 300 });
      return '/settings/family#link';
    } else return '/settings/family';
    return `/settings/family?done=${kind}-${status}`;
  } catch (e) {
    if (!(e instanceof BackendError) || e.status >= 500) throw e;
    // 404: 이미 처리됐거나 기간 지남, 22023: 같은 이름 승인 대기 중·이름이 없어짐(DB 트리거)
    const where = kind === 'upload' ? `/settings/family/member/${id}` : kind === 'download' ? '/settings' : '/settings/family';
    return `${where}?done=${e.status === 404 ? 'gone' : e.code === '22023' || e.code === '23505' ? 'conflict' : 'error'}`;
  }
}

/** 공유 주소는 정해 둔 공개 주소로(미리보기·workers.dev 주소로 열어도 문자엔 진짜 주소). 없으면 지금 주소 */
export const shareUrl = (origin: string, code: string) => `${(SITE_ORIGIN || origin).replace(/\/$/, '')}/i/${code}`;

/** 엄빠 함께 관리 초대 주소 */
export const joinUrl = (origin: string, code: string) => `${(SITE_ORIGIN || origin).replace(/\/$/, '')}/join/${code}`;

/** 문자 앱을 미리 쓴 내용으로 연다(iOS·안드로이드 둘 다 열리는 형태) */
export const smsHref = (body: string) => `sms:?&body=${encodeURIComponent(body)}`;
