// Supabase Auth·PostgREST를 fetch로 직접 부른다. supabase-js는 서버에서만 쓸 일이지만
// Worker 번들 크기와 의존성을 줄이려고 필요한 호출 네 가지만 쓴다.
import type { ActivityItem, AdminDevice, AdminGroup, AdminMember, Backend, EnterInput, EnterResult, EntryInfo, FamilyParents, MediaComment, MediaItem, MediaQuery, Me, ParentHome, ParentInviteInfo, Pass, ReactionCount, UploadTarget } from './types';

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


const MEDIA_COLS = 'id,family_id,kind,taken_at,width,height,duration_sec,view_key,thumb_key,poster_key,created_at';
// 한 번에 받는 최대(닫고 돌아올 때 그리는 901장 포함, Supabase 기본 max_rows 1000 아래)
const MEDIA_MAX = 1000;

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
    // return=minimal은 본문이 없다(PATCH 204, POST 201)
    const text = await res.text();
    return (text ? JSON.parse(text) : undefined) as T;
  }

  /** listMedia·countMedia 공통 거르기: 올린 것만, 가족방·아이, 커서(찍은 날·id), 한 장 */
  function mediaQuery(opts: MediaQuery) {
    const q = new URLSearchParams({ status: 'eq.ready' });
    if (opts.familyId) q.set('family_id', `eq.${opts.familyId}`);
    if (opts.childId) q.set('media_children.child_id', `eq.${opts.childId}`);
    if (opts.id) q.set('id', `eq.${opts.id}`);
    if (opts.takenFrom) q.append('taken_at', `gte.${opts.takenFrom}`);
    if (opts.takenBefore) q.append('taken_at', `lt.${opts.takenBefore}`);
    // 시각에 ':'·'+'가 있어 or 안에서는 따옴표로 감싼다
    const c = opts.before ?? opts.after;
    if (c) {
      const op = opts.before ? 'lt' : 'gt';
      q.set('or', `(taken_at.${op}."${c.takenAt}",and(taken_at.eq."${c.takenAt}",id.${op}.${c.id}))`);
    }
    return q;
  }

  /** 서버 전용 함수(service_role 키) */
  function serviceRpc<T>(fn: string, body: object): Promise<T> {
    if (!serviceKey) throw new Error('SUPABASE_SERVICE_ROLE_KEY가 없다');
    // 새 형식 비밀 키(sb_secret_)는 JWT가 아니라 apikey 자리에도 넣어야 한다
    return call<T>(`/rest/v1/rpc/${fn}`, { method: 'POST', token: serviceKey, apikey: serviceKey, body: JSON.stringify(body) });
  }

  /** 한 행 PATCH. RLS로 남의 가족방 행이면 0행이라 404로 */
  async function patchOne(pass: Pass, table: string, id: string, body: object) {
    const q = new URLSearchParams({ id: `eq.${id}`, select: 'id' });
    const rows = await call<{ id: string }[]>(`/rest/v1/${table}?${q}`, {
      method: 'PATCH',
      token: pass.access,
      headers: { prefer: 'return=representation' },
      body: JSON.stringify(body),
    });
    if (!rows.length) throw new BackendError('not_found', 404);
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
    finishUpload: (id, keys, bytes) =>
      serviceRpc<boolean>('sp_finish_upload', { p_media_id: id, p_view_key: keys.view, p_thumb_key: keys.thumb, p_poster_key: keys.poster, p_bytes: bytes }),
    purgeDeletedFamilies: () => serviceRpc<string[]>('sp_purge_deleted_families', {}),
    cleanupStaleUploads: () => serviceRpc<number>('sp_cleanup_stale_uploads', {}),
    r2CleanupTake: (limit) => serviceRpc<string[]>('sp_r2_cleanup_take', { p_limit: limit }),
    r2CleanupDone: (prefix) => serviceRpc<void>('sp_r2_cleanup_done', { p_prefix: prefix }),
    async listMedia(pass, opts = {}) {
      const q = mediaQuery(opts);
      q.set('select', `${MEDIA_COLS}${opts.childId ? ',media_children!inner(child_id)' : ''}`);
      // after는 가까운 것부터 골라야 해서 오름차순으로 받고 뒤집는다
      q.set('order', opts.after ? 'taken_at.asc,id.asc' : 'taken_at.desc,id.desc');
      q.set('limit', String(Math.min(opts.limit ?? 60, MEDIA_MAX)));
      const rows = await call<(MediaItem & { media_children?: unknown })[]>(`/rest/v1/media?${q}`, { method: 'GET', token: pass.access });
      // 한 아이만 고른 경우 연결 칸은 돌려주지 않는다
      const items = rows.map(({ media_children: _c, ...m }) => m);
      return opts.after ? items.reverse() : items;
    },
    async countMedia(pass, opts = {}) {
      const q = mediaQuery(opts);
      q.set('select', opts.childId ? 'id,media_children!inner(child_id)' : 'id');
      q.set('limit', '1');
      const res = await fetch(`${base}/rest/v1/media?${q}`, {
        method: 'HEAD',
        headers: { apikey: anonKey, authorization: `Bearer ${pass.access}`, prefer: 'count=exact' },
        signal: AbortSignal.timeout(8000),
      });
      if (!res.ok) throw new BackendError(`/rest/v1/media count ${res.status}`, res.status);
      // Content-Range: 0-0/123 또는 */0
      const n = Number(res.headers.get('content-range')?.split('/')[1]);
      if (!Number.isFinite(n)) throw new BackendError('/rest/v1/media count range', 502);
      return n;
    },
    async react(pass, id, kind, on) {
      await rpc(pass, 'sp_react', { p_media_id: id, p_kind: kind, p_on: on });
    },
    async comment(pass, id, body) {
      await rpc(pass, 'sp_comment', { p_media_id: id, p_body: body });
    },
    async parentReact(pass, id, kind, on) {
      await rpc(pass, 'sp_parent_react', { p_media_id: id, p_kind: kind, p_on: on });
    },
    async parentComment(pass, id, body) {
      await rpc(pass, 'sp_parent_comment', { p_media_id: id, p_body: body });
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
    async parentLogout(pass) {
      await fetch(`${base}/auth/v1/logout?scope=local`, {
        method: 'POST',
        headers: { apikey: anonKey, authorization: `Bearer ${pass.access}` },
        signal: AbortSignal.timeout(8000),
      }).catch(() => undefined);
    },
    async familyAdmin(pass) {
      const get = <T>(path: string) => call<T>(path, { method: 'GET', token: pass.access });
      // 부모 RLS로 자기 가족방 것만. devices는 열 권한이라 열을 적는다
      const [groups, members, devices] = await Promise.all([
        get<AdminGroup[]>('/rest/v1/groups?select=id,name,include_by_default,password_hint&order=sort_order,created_at'),
        get<AdminMember[]>('/rest/v1/members?select=id,group_id,display_name,status,pending_until,install_help_at,created_at&order=created_at'),
        get<AdminDevice[]>('/rest/v1/devices?select=id,member_id,status,requested_name,requested_group_id,requested_member_id,can_upload,last_seen_at,created_at&order=created_at.desc'),
      ]);
      return { groups, members, devices };
    },
    // 승인 대기인 것만 바꾼다(기간 지남·이미 처리됨·다른 가족방이면 0행 → 404). 열을 적어야 devices 열 권한에 걸리지 않는다
    async setMemberStatus(pass, id, status) {
      // 승인은 승인 대기만, 거절은 승인 대기·승인된 사람(내보내기)
      const q = new URLSearchParams({ id: `eq.${id}`, status: status === 'active' ? 'eq.pending' : 'in.(pending,active)', select: 'id' });
      if (status === 'active') q.set('pending_until', `gt.${new Date().toISOString()}`);
      const rows = await call<{ id: string }[]>(`/rest/v1/members?${q}`, {
        method: 'PATCH',
        token: pass.access,
        headers: { prefer: 'return=representation' },
        body: JSON.stringify(status === 'active' ? { status, pending_until: null } : { status }),
      });
      if (!rows.length) throw new BackendError('not_found', 404);
    },
    async setDeviceStatus(pass, id, status) {
      const q = new URLSearchParams({ id: `eq.${id}`, status: 'eq.pending', select: 'id' });
      const rows = await call<{ id: string }[]>(`/rest/v1/devices?${q}`, {
        method: 'PATCH',
        token: pass.access,
        headers: { prefer: 'return=representation' },
        body: JSON.stringify(status === 'revoked' ? { status, can_upload: false } : { status }),
      });
      if (!rows.length) throw new BackendError('not_found', 404);
    },
    async setUploadAllowed(pass, memberId, on) {
      const q = new URLSearchParams({ member_id: `eq.${memberId}`, status: 'eq.active', select: 'id' });
      const rows = await call<{ id: string }[]>(`/rest/v1/devices?${q}`, {
        method: 'PATCH',
        token: pass.access,
        headers: { prefer: 'return=representation' },
        body: JSON.stringify({ can_upload: on }),
      });
      if (!rows.length) throw new BackendError('not_found', 404);
    },
    addGroup: (pass, g) =>
      rpc<string>(pass, 'sp_add_group', { p_name: g.name, p_password: g.password, p_hint: g.hint, p_include_by_default: g.includeByDefault }),
    updateGroup: (pass, groupId, patch) => patchOne(pass, 'groups', groupId, patch),
    setGroupPassword: (pass, groupId, password, hint) => rpc<void>(pass, 'sp_set_group_password', { p_group_id: groupId, p_password: password, p_hint: hint }),
    resetGroupLinks: async (pass, groupId) => {
      await rpc<number>(pass, 'sp_reset_group_links', { p_group_id: groupId });
    },
    requestInstallHelp: (pass, familyId) => rpc<void>(pass, 'sp_request_install_help', { p_family_id: familyId }),
    healthDone: (pass, childId) =>
      call<{ item_key: string; done_on: string }[]>(`/rest/v1/health_done?${new URLSearchParams({ child_id: `eq.${childId}`, select: 'item_key,done_on' })}`, { method: 'GET', token: pass.access }),
    async setHealthDone(pass, familyId, childId, add, remove, today) {
      if (add.length)
        await call(`/rest/v1/health_done?on_conflict=child_id,item_key`, {
          method: 'POST',
          token: pass.access,
          headers: { prefer: 'resolution=ignore-duplicates,return=minimal' },
          body: JSON.stringify(add.map((k) => ({ family_id: familyId, child_id: childId, item_key: k, done_on: today }))),
        });
      if (remove.length)
        await call(`/rest/v1/health_done?${new URLSearchParams({ child_id: `eq.${childId}`, item_key: `in.(${remove.join(',')})` })}`, { method: 'DELETE', token: pass.access });
    },
    async setShowHealth(pass, childIds, on) {
      for (const id of childIds) await patchOne(pass, 'children', id, { show_health: on });
    },
    parentActivity: (pass) => rpc<{ seen_at: string; read_at: string; items: ActivityItem[] } | null>(pass, 'sp_parent_activity', {}),
    markActivitySeen: (pass, readAt) => rpc<void>(pass, 'sp_mark_activity_seen', { p_read_at: readAt }),
    async mediaInfo(pass, id) {
      const cols = 'id,family_id,kind,taken_at,width,height,duration_sec,view_key,thumb_key,poster_key';
      const q = new URLSearchParams({ id: `eq.${id}`, status: 'eq.ready', select: `${cols},media_groups(group_id),media_children(child_id)` });
      const rows = await call<(MediaItem & { media_groups: { group_id: string }[]; media_children: { child_id: string }[] })[]>(`/rest/v1/media?${q}`, { method: 'GET', token: pass.access });
      const r = rows[0];
      if (!r) return null;
      const { media_groups, media_children, ...item } = r;
      return {
        item,
        group_ids: media_groups.map((g) => g.group_id),
        child_ids: media_children.map((k) => k.child_id),
      };
    },
    updateMedia: (pass, id, u) =>
      rpc<void>(pass, 'sp_update_media', { p_media_id: id, p_taken_at: u.takenAt, p_child_ids: u.childIds, p_group_ids: u.groupIds }),
    deleteMedia: (pass, id) => rpc<void>(pass, 'sp_delete_media', { p_media_id: id }),
    requestDelete: (pass) => rpc<string | null>(pass, 'sp_request_delete', {}),
    familyParents: async (pass) => (await rpc<FamilyParents | null>(pass, 'sp_family_parents', {})) ?? { parents: [], invite: null },
    createParentInvite: (pass) => rpc<string>(pass, 'sp_create_parent_invite', {}),
    parentInviteInfo: (pass, code) => rpc<ParentInviteInfo>(pass, 'sp_parent_invite_info', { p_code: code }),
    acceptParentInvite: (pass, code, role) => rpc<string>(pass, 'sp_accept_parent_invite', { p_code: code, p_role: role }),
    removeCoparent: (pass, userId) => rpc<void>(pass, 'sp_remove_coparent', { p_user: userId }),
    restoreFamily: (pass) => rpc<void>(pass, 'sp_restore_family', {}),
    setDownloadAllowed: (pass, familyId, on) => patchOne(pass, 'families', familyId, { download_allowed: on }),
    setTextSizeMode: (pass, familyId, mode) => patchOne(pass, 'families', familyId, { text_size_mode: mode }),
    updateChild: (pass, childId, name, birthDate) => patchOne(pass, 'children', childId, { name, birth_date: birthDate }),
    async addChild(pass, familyId, name, birthDate, showHealth) {
      await call(`/rest/v1/children`, {
        method: 'POST',
        token: pass.access,
        headers: { prefer: 'return=minimal' },
        body: JSON.stringify({ family_id: familyId, name, birth_date: birthDate, show_health: showHealth }),
      });
    },
    createShare: (pass, groupIds, target, mediaIds) =>
      rpc<string>(pass, 'sp_create_share', { p_group_ids: groupIds, p_media_ids: mediaIds ?? [], p_target_member: target ?? null }),
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
    mediaComments: (pass, id) => rpc<MediaComment[]>(pass, 'sp_comment_list', { p_media_id: id }),
    noteViews: (pass, ids) => (ids.length ? rpc<void>(pass, 'sp_note_views', { p_media_ids: ids }) : Promise.resolve()),
    mediaViewers: async (pass, id) => (await rpc<{ name: string }[]>(pass, 'sp_parent_media_viewers', { p_media_id: id })).map((x) => x.name),
    deleteComment: (pass, id) => rpc<void>(pass, 'sp_delete_comment', { p_comment_id: id }),
    reactionCounts: (pass, ids) => (ids.length ? rpc<ReactionCount[]>(pass, 'sp_reaction_counts', { p_media_ids: ids }) : Promise.resolve([])),
  };
}
