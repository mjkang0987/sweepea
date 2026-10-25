// Supabase Auth·PostgREST를 fetch로 직접 부른다. supabase-js는 서버에서만 쓸 일이지만
// Worker 번들 크기와 의존성을 줄이려고 필요한 호출 네 가지만 쓴다.
import type { Backend, EnterInput, EnterResult, EntryInfo, MediaItem, Me, ParentHome, Pass, ReactionCount, UploadTarget } from './types';

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


export function createSupabaseBackend(url: string, anonKey: string, serviceKey?: string): Backend {
  const base = url.replace(/\/$/, '');

  async function call<T>(path: string, init: RequestInit & { token?: string | null; apikey?: string }): Promise<T> {
    const headers = new Headers(init.headers);
    headers.set('apikey', init.apikey ?? anonKey);
    headers.set('content-type', 'application/json');
    headers.set('authorization', `Bearer ${init.token ?? anonKey}`);
    const res = await fetch(`${base}${path}`, { ...init, headers, signal: AbortSignal.timeout(8000) });
    if (!res.ok) {
      const body = (await res.json().catch(() => ({}))) as { error_code?: string; code?: string; error?: string };
      throw new BackendError(`${path} ${res.status}`, res.status, body.error_code ?? body.code ?? body.error);
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
        // 4xx(429 제외)는 토큰이 다시 살아날 일이 없다: 출입증을 버린다. 429·5xx·네트워크는 일시 오류라 그대로 던진다
        if (e instanceof BackendError && e.status >= 400 && e.status < 500 && e.status !== 429) return null;
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
    createMedia: (pass, m) =>
      rpc<string>(pass, 'sp_create_media', {
        p_family_id: m.familyId,
        p_kind: m.kind,
        p_taken_at: m.takenAt,
        p_taken_at_source: m.takenAtSource,
        p_width: m.width ?? null,
        p_height: m.height ?? null,
        p_duration_sec: m.durationSec ?? null,
        p_group_ids: m.groupIds ?? null,
        p_child_ids: m.childIds ?? [],
      }),
    uploadTarget: (pass, id) => rpc<UploadTarget | null>(pass, 'sp_upload_target', { p_media_id: id }),
    async finishUpload(id, keys, bytes) {
      if (!serviceKey) throw new Error('SUPABASE_SERVICE_ROLE_KEY가 없다');
      return call<boolean>('/rest/v1/rpc/sp_finish_upload', {
        method: 'POST',
        token: serviceKey,
        // 새 형식 비밀 키(sb_secret_)는 JWT가 아니라 apikey 자리에도 넣어야 한다
        apikey: serviceKey,
        body: JSON.stringify({ p_media_id: id, p_view_key: keys.view, p_thumb_key: keys.thumb, p_poster_key: keys.poster, p_bytes: bytes }),
      });
    },
    listMedia(pass, opts = {}) {
      const q = new URLSearchParams({
        select: 'id,family_id,kind,taken_at,width,height,duration_sec,view_key,thumb_key,poster_key',
        status: 'eq.ready',
        order: 'taken_at.desc,id.desc',
        limit: String(Math.min(opts.limit ?? 60, 200)),
      });
      if (opts.familyId) q.set('family_id', `eq.${opts.familyId}`);
      return call<MediaItem[]>(`/rest/v1/media?${q}`, { method: 'GET', token: pass.access });
    },
    async react(pass, id, kind, on) {
      await rpc(pass, 'sp_react', { p_media_id: id, p_kind: kind, p_on: on });
    },
    async comment(pass, id, body) {
      await rpc(pass, 'sp_comment', { p_media_id: id, p_body: body });
    },
    parentAuthorizeUrl(provider, redirectTo, codeChallenge) {
      const q = new URLSearchParams({ provider, redirect_to: redirectTo, code_challenge: codeChallenge, code_challenge_method: 's256' });
      return `${base}/auth/v1/authorize?${q}`;
    },
    async parentExchange(code, codeVerifier) {
      try {
        return toPass(
          await call<TokenResponse>('/auth/v1/token?grant_type=pkce', {
            method: 'POST',
            body: JSON.stringify({ auth_code: code, code_verifier: codeVerifier }),
          }),
        );
      } catch (e) {
        if (e instanceof BackendError && e.status >= 400 && e.status < 500) return null;
        throw e;
      }
    },
    parentHome: (pass) => rpc<ParentHome>(pass, 'sp_parent_home', {}),
    createFamily: (pass, f) =>
      rpc<string>(pass, 'sp_create_family', {
        p_role: f.role,
        p_display_name: f.role === 'mom' ? '엄마' : '아빠',
        p_child_name: f.childName,
        p_birth_date: f.birthDate,
        p_password: f.password,
        p_hint: f.hint ?? null,
      }),
    reactionCounts: (pass, ids) => (ids.length ? rpc<ReactionCount[]>(pass, 'sp_reaction_counts', { p_media_ids: ids }) : Promise.resolve([])),
  };
}
