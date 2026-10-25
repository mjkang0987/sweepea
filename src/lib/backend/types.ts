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
  child_name: string | null;
}

export interface Me {
  families: MeFamily[];
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
}
