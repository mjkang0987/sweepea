// Supabase Auth·PostgREST를 fetch로 직접 부른다. supabase-js는 서버에서만 쓸 일이지만
// Worker 번들 크기와 의존성을 줄이려고 필요한 호출 네 가지만 쓴다.
import type { Backend, EnterInput, EnterResult, EntryInfo, Me, Pass } from './types';

interface TokenResponse {
  access_token: string;
  refresh_token: string;
  expires_at?: number;
  expires_in: number;
}

export class BackendError extends Error {
  constructor(
    message: string,
    readonly status: number,
    readonly code?: string,
  ) {
    super(message);
  }
}

// 이 코드들만 '토큰이 영영 무효'로 보고 출입증을 버린다(이미 쓴 토큰은 10초 재사용 창이 지난 경우). 429·5xx·네트워크는 일시 오류
const DEAD_REFRESH = new Set(['refresh_token_not_found', 'refresh_token_already_used', 'invalid_grant', 'user_not_found', 'session_not_found']);

export function createSupabaseBackend(url: string, anonKey: string): Backend {
  const base = url.replace(/\/$/, '');

  async function call<T>(path: string, init: RequestInit & { token?: string | null }): Promise<T> {
    const headers = new Headers(init.headers);
    headers.set('apikey', anonKey);
    headers.set('content-type', 'application/json');
    headers.set('authorization', `Bearer ${init.token ?? anonKey}`);
    const res = await fetch(`${base}${path}`, { ...init, headers, signal: AbortSignal.timeout(8000) });
    if (!res.ok) {
      const body = (await res.json().catch(() => ({}))) as { error_code?: string; code?: string };
      throw new BackendError(`${path} ${res.status}`, res.status, body.error_code ?? body.code);
    }
    return (await res.json()) as T;
  }

  function toPass(t: TokenResponse): Pass {
    return {
      access: t.access_token,
      refresh: t.refresh_token,
      expiresAt: t.expires_at ?? Math.floor(Date.now() / 1000) + t.expires_in,
    };
  }

  const rpc = <T>(pass: Pass | null, fn: string, args: Record<string, unknown>) =>
    call<T>(`/rest/v1/rpc/${fn}`, { method: 'POST', body: JSON.stringify(args), token: pass?.access });

  return {
    async signInAnonymously() {
      // 빈 본문 signup = 익명 로그인(대시보드에서 Anonymous sign-ins를 켜야 함)
      return toPass(await call<TokenResponse>('/auth/v1/signup', { method: 'POST', body: '{}' }));
    },
    async refresh(pass) {
      try {
        return toPass(
          await call<TokenResponse>('/auth/v1/token?grant_type=refresh_token', {
            method: 'POST',
            body: JSON.stringify({ refresh_token: pass.refresh }),
          }),
        );
      } catch (e) {
        if (e instanceof BackendError && e.code && DEAD_REFRESH.has(e.code)) return null;
        throw e;
      }
    },
    entryInfo: (pass, code) => rpc<EntryInfo>(pass, 'sp_entry_info', { p_code: code }),
    enter: (pass, i: EnterInput) =>
      rpc<EnterResult>(pass, 'sp_enter', {
        p_code: i.code,
        p_password: i.password,
        p_member_id: i.memberId ?? null,
        p_new_name: i.newName ?? null,
        p_group_id: i.groupId ?? null,
      }),
    me: (pass) => rpc<Me>(pass, 'sp_me', {}),
  };
}
