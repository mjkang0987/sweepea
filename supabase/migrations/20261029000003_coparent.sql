-- 공동 관리자(100, 사용자 2026-10-29 "권한은 공동으로"): 가족방마다 엄빠 계정 둘까지, 둘 다 같은 엄빠 화면.
-- 초대 링크(한 번, 3일) → 받은 사람이 로그인하면 엄빠로. 서로 내보낼 수 있고, 한 명 탈퇴는 나만 나가기(마지막 한 명일 때만 가족방 삭제).
-- 내보내거나 나간 엄빠가 반응·한마디를 남겼으면 그 기록이 지워지지 않게(반응·한마디가 parents를 cascade로 참조) 행을 지우지 않고 removed_at만 적는다
-- (가족 구성원 내보내기와 같은 방식). 알려진 한계: 그렇게 남은 계정은 같은 로그인으로 새 가족방을 만들거나 다른 초대를 받을 수 없다

alter table public.parents add column removed_at timestamptz;

-- 엄빠 판정은 나가지 않은 행만
create or replace function public.sp_parent_family() returns uuid
language sql stable security definer set search_path = ''
as $$ select p.family_id from public.parents p where p.user_id = auth.uid() and p.removed_at is null $$;

create or replace function public.sp_parent_home() returns jsonb
language sql stable security definer set search_path = ''
as $$
  select coalesce((
    select jsonb_build_object(
      'family_id', p.family_id,
      'role', p.role,
      -- 로그인 제공자(kakao·google 등). Supabase가 액세스 토큰 app_metadata에 넣는다
      'provider', auth.jwt() -> 'app_metadata' ->> 'provider',
      'text_size_mode', f.text_size_mode,
      'closing', f.delete_after is not null,
      'delete_after', f.delete_after,
      -- 스토어 구독이 끝나는 날(구독 중이면). 해지해도 이 날까지는 탈퇴를 막는다
      -- 마지막으로 최근 반응을 연 뒤 승인된 가족이 남긴 반응·한마디 수
      -- 목록(sp_parent_activity)과 같은 규칙: 최근 30일, 다 올라간 사진
      'new_activity', (select count(*) from public.reactions r join public.media x on x.id = r.media_id and x.status = 'ready'
                         join public.members m on m.id = r.member_id and m.status = 'active'
                         where x.family_id = f.id and r.created_at > greatest(p.activity_seen_at, now() - interval '30 days'))
                    + (select count(*) from public.comments c join public.media x on x.id = c.media_id and x.status = 'ready'
                         join public.members m on m.id = c.member_id and m.status = 'active'
                         where x.family_id = f.id and c.deleted_at is null and c.created_at > greatest(p.activity_seen_at, now() - interval '30 days')),
      -- 승인 기다리는 수(설정 탭 배지): 기한 안 지난 들어오기 신청 + 승인 기다리는 휴대폰
      'waiting', (select count(*) from public.members m where m.family_id = f.id and m.status = 'pending' and m.pending_until > now())
               + (select count(*) from public.devices d where d.family_id = f.id and d.status = 'pending'),
      'plan_until', (select max(e.expires_at) from public.entitlements e where e.family_id = f.id and e.expires_at > now()),
      'download_allowed', f.download_allowed,
      'storage_used_bytes', f.storage_used_bytes,
      'photo_count', (select count(*) from public.media x where x.family_id = f.id and x.status = 'ready' and x.kind = 'photo'),
      'video_count', (select count(*) from public.media x where x.family_id = f.id and x.status = 'ready' and x.kind = 'video'),
      'children', coalesce((
        select jsonb_agg(jsonb_build_object('id', c.id, 'name', c.name, 'birth_date', c.birth_date, 'show_health', c.show_health) order by c.sort_order, c.created_at)
        from public.children c where c.family_id = p.family_id
      ), '[]'::jsonb)
    )
    from public.parents p join public.families f on f.id = p.family_id
    -- 지울 날이 지난 가족방은 없는 것으로(처음 설정부터, sp_create_family가 먼저 지운다)
    where p.user_id = auth.uid() and p.removed_at is null and (f.delete_after is null or f.delete_after > now())
  ), jsonb_build_object('family_id', null))
$$;

create table public.parent_invites (
  id uuid primary key default gen_random_uuid(),
  family_id uuid not null references public.families (id) on delete cascade,
  code text not null unique check (code ~ '^[A-Za-z0-9]{8}$'),
  created_by uuid not null references public.parents (user_id) on delete cascade,
  created_at timestamptz not null default now(),
  expires_at timestamptz not null default now() + interval '3 days',
  used_at timestamptz,
  used_by uuid
);
create index on public.parent_invites (family_id);
alter table public.parent_invites enable row level security;
-- 표는 함수로만 다룬다
revoke all on public.parent_invites from public, anon, authenticated;

-- 함께 관리하는 엄빠(설정 › 가족 맨 위): 나 먼저, 그다음 들어온 순. 살아 있는 초대 링크가 있으면 같이
create function public.sp_family_parents() returns jsonb
language sql stable security definer set search_path = ''
as $$
  select jsonb_build_object(
    'parents', coalesce((
      select jsonb_agg(jsonb_build_object('user_id', p.user_id, 'role', p.role, 'display_name', p.display_name, 'since', p.created_at, 'me', p.user_id = auth.uid())
                       order by p.user_id <> auth.uid(), p.created_at)
      from public.parents p where p.family_id = public.sp_parent_family() and p.removed_at is null), '[]'::jsonb),
    'invite', (select jsonb_build_object('code', i.code, 'expires_at', i.expires_at) from public.parent_invites i
               where i.family_id = public.sp_parent_family() and i.used_at is null and i.expires_at > now()
               order by i.created_at desc limit 1))
  where public.sp_parent_family() is not null
$$;

-- 초대 링크 만들기: 엄빠가 둘이면 거절. 예전 안 쓴 링크는 지우고 새로(링크는 하나만 살아 있다)
create function public.sp_create_parent_invite() returns text
language plpgsql security definer set search_path = ''
as $$
declare
  v_family uuid := public.sp_parent_family();
  v_alpha constant text := 'ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz23456789';
  v_code text; b bytea;
begin
  if v_family is null or exists (select 1 from public.families where id = v_family and delete_after is not null) then
    raise exception 'not_allowed' using errcode = '42501';
  end if;
  if (select count(*) from public.parents where family_id = v_family and removed_at is null) >= 2 then
    raise exception 'parents_full' using errcode = '23505';
  end if;
  delete from public.parent_invites where family_id = v_family and used_at is null;
  loop
    b := extensions.gen_random_bytes(8);
    select string_agg(substr(v_alpha, (get_byte(b, i) % length(v_alpha)) + 1, 1), '') into v_code from generate_series(0, 7) i;
    exit when not exists (select 1 from public.parent_invites where code = v_code);
  end loop;
  insert into public.parent_invites (family_id, code, created_by) values (v_family, v_code, auth.uid());
  return v_code;
end $$;

-- 초대 받은 화면(/join, 로그인 전에도): 아이 이름·초대한 사람 역할·상태. 상태: ok, expired(썼거나 3일 지남), full, closed, not_found
create function public.sp_parent_invite_info(p_code text) returns jsonb
language sql stable security definer set search_path = ''
as $$
  select coalesce((
    select jsonb_build_object(
      'result', case
        when f.delete_after is not null then 'closed'
        when i.used_at is not null or i.expires_at <= now() then 'expired'
        when (select count(*) from public.parents p where p.family_id = i.family_id and p.removed_at is null) >= 2 then 'full'
        else 'ok' end,
      'child_name', (select c.name from public.children c where c.family_id = i.family_id order by c.sort_order, c.created_at limit 1),
      'inviter_role', (select p.role from public.parents p where p.user_id = i.created_by))
    from public.parent_invites i join public.families f on f.id = i.family_id
    where i.code = p_code), jsonb_build_object('result', 'not_found'))
$$;

-- 초대 받기(로그인 뒤): 이미 엄빠 계정이거나 가족 기기 계정이면 거절, 둘이 차 있으면 거절. 한 번 쓰면 끝
create function public.sp_accept_parent_invite(p_code text, p_role text) returns uuid
language plpgsql security definer set search_path = ''
as $$
declare v_inv public.parent_invites;
begin
  if auth.uid() is null or public.sp_is_anonymous() then
    raise exception 'parent_login_required' using errcode = '42501';
  end if;
  if p_role not in ('mom', 'dad') then
    raise exception 'bad_request' using errcode = '22023';
  end if;
  select * into v_inv from public.parent_invites where code = p_code for update;
  if not found then raise exception 'not_found' using errcode = 'P0002'; end if;
  if v_inv.used_at is not null or v_inv.expires_at <= now()
     or exists (select 1 from public.families where id = v_inv.family_id and delete_after is not null) then
    raise exception 'expired' using errcode = '22023';
  end if;
  -- 지울 날이 지난 내 가족방은 먼저 지운다(sp_create_family와 같게)
  perform public.sp_purge_family(p.family_id) from public.parents p join public.families f on f.id = p.family_id
    where p.user_id = auth.uid() and f.delete_after <= now();
  if exists (select 1 from public.parents where user_id = auth.uid()) then
    raise exception 'family_exists' using errcode = '23505';
  end if;
  if exists (select 1 from public.devices where auth_user_id = auth.uid()) then
    raise exception 'is_device' using errcode = '42501';
  end if;
  if (select count(*) from public.parents where family_id = v_inv.family_id and removed_at is null) >= 2 then
    raise exception 'parents_full' using errcode = '23505';
  end if;
  insert into public.parents (user_id, family_id, role, display_name)
    values (auth.uid(), v_inv.family_id, p_role, case p_role when 'mom' then '엄마' else '아빠' end);
  update public.parent_invites set used_at = now(), used_by = auth.uid() where id = v_inv.id;
  return v_inv.family_id;
end $$;

-- 엄빠 한 명 빼기(내보내기·나만 나가기 공통). 반응·한마디가 있으면 행은 남기고 removed_at만
create function public.sp_drop_parent(p_user uuid) returns void
language plpgsql security definer set search_path = ''
as $$
begin
  if exists (select 1 from public.reactions where parent_user_id = p_user) or exists (select 1 from public.comments where parent_user_id = p_user) then
    update public.parents set removed_at = now() where user_id = p_user;
  else
    delete from public.parents where user_id = p_user;
  end if;
  delete from public.parent_invites where created_by = p_user and used_at is null;
end $$;
revoke execute on function public.sp_drop_parent(uuid) from public, anon, authenticated;

-- 함께 관리하는 상대 엄빠 내보내기(나는 못 내보냄 → 나가기는 탈퇴)
create function public.sp_remove_coparent(p_user uuid) returns void
language plpgsql security definer set search_path = ''
as $$
declare v_family uuid := public.sp_parent_family();
begin
  if v_family is null or p_user = auth.uid()
     or not exists (select 1 from public.parents where user_id = p_user and family_id = v_family and removed_at is null) then
    raise exception 'not_allowed' using errcode = '42501';
  end if;
  perform public.sp_drop_parent(p_user);
end $$;

-- 탈퇴: 함께 관리하는 엄빠가 있으면 나만 나가고(null), 마지막 한 명이면 지금처럼 3일 뒤 삭제 예정 시각
create or replace function public.sp_request_delete() returns timestamptz
language plpgsql security definer set search_path = ''
as $$
declare v_family uuid := public.sp_parent_family(); v_at timestamptz;
begin
  if v_family is null then raise exception 'parent_only' using errcode = '42501'; end if;
  if exists (select 1 from public.parents where family_id = v_family and removed_at is null and user_id <> auth.uid()) then
    perform public.sp_drop_parent(auth.uid());
    return null;
  end if;
  -- 스토어 구독은 탈퇴해도 결제가 멈추지 않으니 먼저 해지하게 한다(PT402 → HTTP 402)
  if exists (select 1 from public.entitlements where family_id = v_family and expires_at > now()) then
    raise exception 'subscribed' using errcode = 'PT402';
  end if;
  update public.families set delete_after = coalesce(delete_after, now() + interval '3 days')
    where id = v_family returning delete_after into v_at;
  return v_at;
end $$;

revoke execute on function public.sp_family_parents(), public.sp_create_parent_invite(), public.sp_accept_parent_invite(text, text), public.sp_remove_coparent(uuid) from public, anon;
grant execute on function public.sp_family_parents(), public.sp_create_parent_invite(), public.sp_accept_parent_invite(text, text), public.sp_remove_coparent(uuid) to authenticated;
revoke execute on function public.sp_parent_invite_info(text) from public;
grant execute on function public.sp_parent_invite_info(text) to anon, authenticated;
