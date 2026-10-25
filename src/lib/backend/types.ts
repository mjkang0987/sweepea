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
  download_allowed?: boolean;
  storage_used_bytes?: number;
  photo_count?: number;
  video_count?: number;
  children?: { id: string; name: string; birth_date: string }[];
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
}
export interface AdminMember {
  id: string;
  group_id: string;
  display_name: string;
  status: 'active' | 'pending' | 'rejected';
  pending_until: string | null;
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
  /** 볼 수 있는 사진만(RLS). 최근 찍은 순 */
  // shortcut: 다음 쪽 넘기기 없음(최근 limit장만). 뷰어 이슈에서 (taken_at, id) 기준 커서로
  listMedia(pass: Pass, opts?: { familyId?: string; limit?: number }): Promise<MediaItem[]>;
  /** 반응 켜기·끄기. 볼 수 없는 사진이면 BackendError 403 */
  react(pass: Pass, mediaId: string, kind: ReactionKind, on: boolean): Promise<void>;
  /** 한마디(1~200자). 하루 30개 넘으면 BackendError 429 */
  comment(pass: Pass, mediaId: string, body: string): Promise<void>;
  reactionCounts(pass: Pass, mediaIds: string[]): Promise<ReactionCount[]>;
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
  /** 탈퇴 신청: 가족 화면을 바로 닫고 3일 뒤 지울 시각(ISO). 구독 중이면 BackendError 402 */
  requestDelete(pass: Pass): Promise<string>;
  /** 유예 중 되살리기. 유예가 아니거나 기한이 지났으면 400 */
  restoreFamily(pass: Pass): Promise<void>;
  /** 가족 화면 처음 글자 크기 */
  setTextSizeMode(pass: Pass, familyId: string, mode: TextSizeMode): Promise<void>;
  addChild(pass: Pass, familyId: string, name: string, birthDate: string): Promise<void>;
  /** 자기 가족방 아이가 아니면 404 */
  updateChild(pass: Pass, childId: string, name: string, birthDate: string): Promise<void>;
  createShare(pass: Pass, groupIds: string[], targetMemberId?: string, mediaIds?: string[]): Promise<string>;
}
