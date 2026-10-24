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

export type EntryInfo =
  | { result: 'not_found' | 'closed' | 'expired' }
  | {
      result: 'ok';
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

export interface Me {
  device: 'active' | 'pending' | 'revoked' | null;
  member?: 'active' | 'pending' | 'expired' | 'rejected' | null;
  name?: string | null;
  closed?: boolean;
  child_name?: string | null;
}

export interface Backend {
  /** 처음 오는 기기에 익명 출입증을 만든다 */
  signInAnonymously(): Promise<Pass>;
  /** 만료된 출입증을 갱신한다. 실패하면 null(새로 만들어야 함) */
  refresh(pass: Pass): Promise<Pass | null>;
  entryInfo(pass: Pass, code: string): Promise<EntryInfo>;
  enter(pass: Pass, input: EnterInput): Promise<EnterResult>;
  me(pass: Pass): Promise<Me>;
}
