// 백엔드 계약. 결과 문자열은 supabase/migrations의 sp_entry_info·sp_enter·sp_me와 같다.

export interface Pass {
  /** Supabase 액세스 토큰(익명 사용자). mock에선 기기 id */
  access: string;
  refresh: string;
  /** 액세스 토큰 만료 시각(epoch 초) */
  expiresAt: number;
}

export interface EntryMember {
  id: string;
  name: string;
}

export interface EntryGroup {
  id: string;
  name: string;
  hint: string | null;
  members: EntryMember[];
}

/** 이 링크의 가족방에서 지금 기기 상태. 처음 온 기기면 null */
export interface EntryMe {
  device: 'active' | 'pending' | 'revoked';
  member: 'active' | 'pending' | 'expired' | 'rejected' | null;
  name: string | null;
}

export type EntryInfo =
  | { result: 'not_found' }
  | { result: 'closed' | 'expired'; me: EntryMe | null }
  | {
      result: 'ok';
      me: EntryMe | null;
      child_name: string | null;
      text_size_mode: TextSizeMode;
      new_entry_open: boolean;
      target_member_id: string | null;
      groups: EntryGroup[];
    };

export type EnterResult =
  | { result: 'ok' | 'pending'; member_id: string }
  | { result: 'wrong_password'; hint: string | null; attempts: number }
  | { result: 'locked'; retry_after: number }
  | {
      result: 'needs_approval' | 'expired' | 'not_found' | 'closed' | 'revoked' | 'name_taken' | 'bad_request';
    };

export interface EnterInput {
  code: string;
  password: string;
  memberId?: string;
  newName?: string;
  groupId?: string;
}

/** 지금 기기가 들어간 가족방 하나 */
export interface MeFamily extends EntryMe {
  family_id: string;
  closed: boolean;
  /** 부모가 '가족도 사진 저장하기'를 켰는지 */
  download_allowed?: boolean;
  child_name: string | null;
}

export interface Me {
  families: MeFamily[];
}

export type MediaKind = 'photo' | 'video';

export interface NewMedia {
  familyId: string;
  kind: MediaKind;
  takenAt: string;
  takenAtSource: 'exif' | 'file' | 'upload' | 'manual';
  width?: number;
  height?: number;
  durationSec?: number;
  /** 없으면 '기본 포함' 그룹 전부 */
  groupIds?: string[];
  childIds?: string[];
}

/** 파일을 넣어도 되는 사진(올리는 중 + 호출자가 올린 사람) */
export interface UploadTarget {
  family_id: string;
  kind: MediaKind;
}

export interface MediaKeys {
  view: string;
  thumb: string;
  poster: string | null;
}

/** 목록 커서: 찍은 날 + id(같은 시각이면 id로 순서) */
export interface MediaCursor {
  takenAt: string;
  id: string;
}
export interface MediaQuery {
  familyId?: string;
  childId?: string;
  limit?: number;
  before?: MediaCursor;
  after?: MediaCursor;
  id?: string;
  /** 찍은 날 범위 [takenFrom, takenBefore)(달별 개수) */
  takenFrom?: string;
  takenBefore?: string;
}

export interface MediaItem {
  id: string;
  family_id: string;
  kind: MediaKind;
  taken_at: string;
  width: number | null;
  height: number | null;
  duration_sec: number | null;
  view_key: string;
  thumb_key: string;
  poster_key: string | null;
  /** 올린 시각(가족 '새 사진' 레이어). 목록에서만 채운다 */
  created_at?: string;
}

/** 부모 최근 반응 한 줄 */
export interface ActivityItem {
  type: 'reaction' | 'comment';
  kind: ReactionKind | null;
  body: string | null;
  at: string;
  who: string;
  media_id: string;
  thumb_key: string | null;
}

/** 부모 사진 정보 화면 */
export interface MediaInfo {
  item: MediaItem;
  group_ids: string[];
  child_ids: string[];
}

export const REACTION_KINDS = ['heart', 'best', 'good', 'moved', 'sparkle'] as const;
export type ReactionKind = (typeof REACTION_KINDS)[number];

/** 사진 하나의 반응 요약. kind 'comment'는 한마디 수 */
export interface ReactionCount {
  media_id: string;
  kind: ReactionKind | 'comment';
  n: number;
  mine: boolean;
}

/** 가족 화면 글자 크기 기본값. relation: 할머니·할아버지 호칭이면 크게, 나머지 기본 */
export type TextSizeMode = 'relation' | 'base' | 'large' | 'xlarge';

export interface ParentHome {
  family_id: string | null;
  role?: 'mom' | 'dad';
  /** 로그인 제공자(kakao·naver·google·apple). 모르면 null */
  provider?: string | null;
  text_size_mode?: TextSizeMode;
  closing?: boolean;
  /** 탈퇴 유예 중이면 지울 시각(ISO) */
  delete_after?: string | null;
  /** 최근 반응을 마지막으로 연 뒤 새로 온 반응·한마디 수 */
  new_activity?: number;
  /** 승인 기다리는 들어오기 신청 + 휴대폰 수(설정 탭 배지) */
  waiting?: number;
  /** 스토어 구독이 끝나는 시각(구독 중이면). 그때까지 탈퇴 불가 */
  plan_until?: string | null;
  download_allowed?: boolean;
  storage_used_bytes?: number;
  photo_count?: number;
  video_count?: number;
  children?: { id: string; name: string; birth_date: string; show_health: boolean }[];
}

export interface NewFamily {
  role: 'mom' | 'dad';
  childName: string;
  birthDate: string;
  password: string;
  hint?: string;
}

/** 설정 > 가족에서 부모가 보는 것 */
export interface AdminGroup {
  id: string;
  name: string;
  include_by_default: boolean;
  password_hint: string | null;
}
export interface NewGroup {
  name: string;
  password: string;
  hint: string | null;
  includeByDefault: boolean;
}
export interface AdminMember {
  id: string;
  group_id: string;
  display_name: string;
  status: 'active' | 'pending' | 'rejected';
  pending_until: string | null;
  /** 홈 화면에 두기를 부탁한 때 */
  install_help_at: string | null;
  created_at: string;
}
export interface AdminDevice {
  id: string;
  member_id: string | null;
  status: 'active' | 'pending' | 'revoked';
  requested_name: string | null;
  requested_group_id: string | null;
  requested_member_id: string | null;
  can_upload: boolean;
  last_seen_at: string;
  created_at: string;
}
export interface FamilyAdmin {
  groups: AdminGroup[];
  members: AdminMember[];
  devices: AdminDevice[];
}

export interface Backend {
  /** 처음 오는 기기에 익명 출입증을 만든다 */
  signInAnonymously(): Promise<Pass>;
  /** 만료된 출입증을 갱신한다. 토큰이 확실히 무효일 때만 null, 일시 오류는 예외 */
  refresh(pass: Pass): Promise<Pass | null>;
  /** 출입증 없이도(처음 온 기기) 부를 수 있다 */
  entryInfo(pass: Pass | null, code: string): Promise<EntryInfo>;
  enter(pass: Pass, input: EnterInput): Promise<EnterResult>;
  me(pass: Pass): Promise<Me>;
  /** 사진 행 만들기(올리기 권한 확인). 권한 없으면 BackendError 403 */
  createMedia(pass: Pass, input: NewMedia): Promise<string>;
  uploadTarget(pass: Pass, mediaId: string): Promise<UploadTarget | null>;
  /** 서버 전용(service_role). 이미 완료됐거나 없으면 false */
  finishUpload(mediaId: string, keys: MediaKeys, bytes: number): Promise<boolean>;
  /** 볼 수 있는 사진(찍은 날·id 내림차순). before는 그 사진보다 옛것, after는 그보다 최근 것(가까운 순서로 limit개를 골라 내림차순으로 돌려줌), id는 한 장만 */
  listMedia(pass: Pass, opts?: MediaQuery): Promise<MediaItem[]>;
  /** listMedia와 같은 조건의 개수(limit 없음) */
  countMedia(pass: Pass, opts?: Omit<MediaQuery, 'limit' | 'id'>): Promise<number>;
  /** 반응 켜기·끄기. 볼 수 없는 사진이면 BackendError 403 */
  react(pass: Pass, mediaId: string, kind: ReactionKind, on: boolean): Promise<void>;
  /** 한마디(1~200자). 하루 30개 넘으면 BackendError 429 */
  comment(pass: Pass, mediaId: string, body: string): Promise<void>;
  /** 부모 계정이 반응 켜기·끄기(자기 가족방 사진만, 아니면 BackendError 403) */
  parentReact(pass: Pass, mediaId: string, kind: ReactionKind, on: boolean): Promise<void>;
  /** 부모 계정 한마디(1~200자, 하루 30개) */
  parentComment(pass: Pass, mediaId: string, body: string): Promise<void>;
  reactionCounts(pass: Pass, mediaIds: string[]): Promise<ReactionCount[]>;
  /** 크게 보기 한마디 목록(최근 것부터, 볼 수 있는 사진만, 승인된 가족·엄빠 것) */
  mediaComments(pass: Pass, mediaId: string): Promise<MediaComment[]>;
  /** 가족 기기가 본 사진 남기기(볼 수 있는 사진만, 승인된 구성원만, 한 번에 50장). 엄빠 계정은 아무것도 안 남음 */
  noteViews(pass: Pass, mediaIds: string[]): Promise<void>;
  /** 엄빠 크게 보기: 그 사진을 본 가족 이름(처음 본 순). 횟수·시간은 내보내지 않는다 */
  mediaViewers(pass: Pass, mediaId: string): Promise<string[]>;
  /** 한마디 지우기(쓴 사람만) */
  deleteComment(pass: Pass, commentId: string): Promise<void>;
  /** 부모 로그인 시작 주소(Supabase OAuth, PKCE) */
  parentAuthorizeUrl(provider: string, redirectTo: string, codeChallenge: string): string;
  /** 로그인 뒤 돌아온 코드를 세션으로 바꾼다. 실패하면 null */
  parentExchange(code: string, codeVerifier: string): Promise<Pass | null>;
  parentHome(pass: Pass): Promise<ParentHome>;
  /** 처음 설정: 가족방 + 기본 그룹(가족) + 첫 아이. 가족방 id */
  createFamily(pass: Pass, input: NewFamily): Promise<string>;
  /** 로그아웃: 이 세션의 갱신 토큰을 무효로(실패해도 쿠키는 지운다) */
  parentLogout(pass: Pass): Promise<void>;
  familyAdmin(pass: Pass): Promise<FamilyAdmin>;
  /** 새 이름 승인(active, 승인 대기만)·거절(rejected, 승인 대기·승인된 사람 모두 = 내보내기). 거절하면 그 사람 기기도 막힌다(DB 트리거) */
  setMemberStatus(pass: Pass, memberId: string, status: 'active' | 'rejected'): Promise<void>;
  /** 승인 대기 기기 승인(active, 들어가려던 이름을 붙임)·내 가족 아님(revoked) */
  setDeviceStatus(pass: Pass, deviceId: string, status: 'active' | 'revoked'): Promise<void>;
  /** 공유 링크 코드(8자). targetMemberId를 주면 그 사람 전용 한 번 쓰는 링크 */
  /** 그 사람의 승인된 기기들에 사진 올리기 허용·해제 */
  setUploadAllowed(pass: Pass, memberId: string, on: boolean): Promise<void>;
  /** 가족도 사진 저장하기 */
  setDownloadAllowed(pass: Pass, familyId: string, on: boolean): Promise<void>;
  /** 정리 예약 작업(service_role): 탈퇴 기한 지난 가족방 지우기. 지운 가족방 id */
  purgeDeletedFamilies(): Promise<string[]>;
  /** 하루 지난 '올리는 중' 사진 지우기. 지운 개수 */
  cleanupStaleUploads(): Promise<number>;
  /** R2 정리 대기열(폴더 접두사) 오래된 것부터 */
  r2CleanupTake(limit: number): Promise<string[]>;
  r2CleanupDone(prefix: string): Promise<void>;
  /** 홈 화면에 두기를 엄마아빠에게 부탁(가족 기기 본인) */
  requestInstallHelp(pass: Pass, familyId: string): Promise<void>;
  /** 접종·검진 완료 기록(부모만) */
  healthDone(pass: Pass, childId: string): Promise<{ item_key: string; done_on: string }[]>;
  /** 완료 기록 맞추기: add는 오늘 날짜로 넣고(이미 있으면 그대로), remove는 지운다 */
  setHealthDone(pass: Pass, familyId: string, childId: string, add: string[], remove: string[], today: string): Promise<void>;
  /** 앨범에 접종·검진 일정 보기(아이 모두) */
  setShowHealth(pass: Pass, childIds: string[], on: boolean): Promise<void>;
  /** 부모 최근 반응(최근 30일, 50개). 부모가 아니면 null */
  parentActivity(pass: Pass): Promise<{ seen_at: string; read_at: string; items: ActivityItem[] } | null>;
  /** 읽음 표시(목록을 읽은 시각까지만) */
  markActivitySeen(pass: Pass, readAt: string): Promise<void>;
  /** 부모 사진 정보. 내 가족방 사진이 아니거나 없으면 null */
  mediaInfo(pass: Pass, mediaId: string): Promise<MediaInfo | null>;
  /** 찍은 날·아이·보여줄 그룹(하나 이상)을 한 번에 */
  updateMedia(pass: Pass, mediaId: string, u: { takenAt: string; childIds: string[]; groupIds: string[] }): Promise<void>;
  /** 사진 지우기(부모만): 용량에서 빼고 R2 정리 대기열에 */
  deleteMedia(pass: Pass, mediaId: string): Promise<void>;
  /** 탈퇴 신청: 가족 화면을 바로 닫고 3일 뒤 지울 시각(ISO). 함께 관리하는 엄빠가 있으면 나만 빠지고 null. 구독 중이면 BackendError 402 */
  requestDelete(pass: Pass): Promise<string | null>;
  /** 함께 관리하는 엄빠(나 먼저)와 살아 있는 초대 링크 */
  familyParents(pass: Pass): Promise<FamilyParents>;
  /** 엄빠 초대 링크 코드(예전 안 쓴 링크는 지움). 엄빠가 둘이면 409 */
  createParentInvite(pass: Pass): Promise<string>;
  /** 초대 받은 화면 정보(로그인 전에도) */
  parentInviteInfo(pass: Pass | null, code: string): Promise<ParentInviteInfo>;
  /** 초대 받기(로그인한 엄빠 계정): 가족방 id. 이미 엄빠 계정이면 409 family_exists, 지났으면 400 expired, 둘이 차면 409 parents_full */
  acceptParentInvite(pass: Pass, code: string, role: 'mom' | 'dad'): Promise<string>;
  /** 함께 관리하는 상대 엄빠 내보내기 */
  removeCoparent(pass: Pass, userId: string): Promise<void>;
  /** 유예 중 되살리기. 유예가 아니거나 기한이 지났으면 400 */
  restoreFamily(pass: Pass): Promise<void>;
  /** 그룹 추가(10개까지, 넘으면 409). 그룹 id */
  addGroup(pass: Pass, g: NewGroup): Promise<string>;
  /** 이름·새 사진 기본 포함. 같은 이름이 있으면 409(23505), 남의 그룹이면 404 */
  updateGroup(pass: Pass, groupId: string, patch: { name?: string; include_by_default?: boolean }): Promise<void>;
  setGroupPassword(pass: Pass, groupId: string, password: string, hint: string | null): Promise<void>;
  /** 그 그룹이 들어간 공유 링크를 모두 지운다(예전 주소 막기) */
  resetGroupLinks(pass: Pass, groupId: string): Promise<void>;
  /** 가족 화면 처음 글자 크기 */
  setTextSizeMode(pass: Pass, familyId: string, mode: TextSizeMode): Promise<void>;
  /** showHealth: 다른 아이들과 같은 '접종·검진 일정 보기' */
  addChild(pass: Pass, familyId: string, name: string, birthDate: string, showHealth: boolean): Promise<void>;
  /** 자기 가족방 아이가 아니면 404 */
  updateChild(pass: Pass, childId: string, name: string, birthDate: string): Promise<void>;
  createShare(pass: Pass, groupIds: string[], targetMemberId?: string, mediaIds?: string[]): Promise<string>;
}

export interface MediaComment {
  id: string;
  name: string;
  body: string;
  created_at: string;
  mine: boolean;
}

/** 함께 관리하는 엄빠(설정 › 가족 맨 위) */
export interface FamilyParents {
  parents: { user_id: string; role: 'mom' | 'dad'; display_name: string; since: string; me: boolean }[];
  invite: { code: string; expires_at: string } | null;
}
/** 엄빠 초대 받은 화면(/join) */
export interface ParentInviteInfo {
  result: 'ok' | 'expired' | 'full' | 'closed' | 'not_found';
  child_name?: string;
  inviter_role?: 'mom' | 'dad';
}
