-- 가족 캐릭터(110, 사용자 2026-11-01 "캐릭터 선택할 수 있게", "각자만"): 가족 구성원·엄빠가 그림 45개(public/avatar/1~45.webp) 중 하나를 고른다. null = 안 고름(이름 첫 글자 그대로).
-- 고르기는 각자 자기 것만: 가족 기기는 그 가족방의 자기 구성원(승인된 사람만, sp_set_member_avatar), 엄빠는 자기 행(sp_set_parent_avatar).
-- 열 권한(members update는 열을 적어 둠)에는 넣지 않는다: 엄빠도 가족 캐릭터를 못 바꾸고, 가족 기기도 함수로만 바꾼다.
-- 읽기: 누구세요(sp_entry_info 구성원), 가족 기기 자기 것(sp_me), 엄빠 자기 것(sp_parent_home), 설정 › 가족(members 표, select는 열 제한 없음), 한마디 목록(sp_comment_list2).
-- 함수 모양이 바뀌는 한마디 목록은 이름을 바꾼 새 함수로(운영 적용 도구가 지우기 문을 막음). 옛 sp_comment_list는 배포 전 코드가 쓰므로 그대로 둔다

alter table public.members add column avatar smallint check (avatar between 1 and 45);
alter table public.parents add column avatar smallint check (avatar between 1 and 45);

-- 가족 기기: 그 가족방에서 내 캐릭터 고르기(null이면 고르지 않음). 승인된 구성원만(승인 대기·막힌 기기·닫힌 가족방은 거절)
create function public.sp_set_member_avatar(p_family_id uuid, p_avatar smallint) returns void
language plpgsql security definer set search_path = ''
as $$
declare v_member uuid := public.sp_device_member(p_family_id);
begin
  if v_member is null or not public.sp_device_active(p_family_id) then raise exception 'not_allowed' using errcode = '42501'; end if;
  update public.members set avatar = p_avatar where id = v_member;
end $$;

-- 엄빠: 내 캐릭터 고르기(나간 엄빠·가족 기기는 거절)
create function public.sp_set_parent_avatar(p_avatar smallint) returns void
language plpgsql security definer set search_path = ''
as $$
begin
  update public.parents set avatar = p_avatar where user_id = auth.uid() and removed_at is null and family_id is not null;
  if not found then raise exception 'parent_only' using errcode = '42501'; end if;
end $$;

revoke execute on function public.sp_set_member_avatar(uuid, smallint), public.sp_set_parent_avatar(smallint) from public, anon, authenticated;
grant execute on function public.sp_set_member_avatar(uuid, smallint), public.sp_set_parent_avatar(smallint) to authenticated;

-- 누구세요 이름 목록에 캐릭터(돌려주는 jsonb에 칸만 더함)
create or replace function public.sp_entry_info(p_code text) returns jsonb
language plpgsql stable security definer set search_path = ''
as $$
declare s public.shares; f public.families; v_child text; v_me jsonb;
begin
  select * into s from public.shares where code = p_code and revoked_at is null;
  if not found then return jsonb_build_object('result', 'not_found'); end if;
  select * into f from public.families where id = s.family_id;
  -- 이 가족방에서 지금 기기 상태(처음이면 null). 이미 들어온 기기는 바로 앨범으로 보낸다
  select jsonb_build_object(
      'device', d.status,
      'member', case when m.id is null then null
                     when m.status = 'pending' and m.pending_until <= now() then 'expired' else m.status end,
      'name', coalesce(m.display_name, d.requested_name))
    into v_me
    from public.devices d left join public.members m on m.id = d.member_id
    where d.auth_user_id = auth.uid() and d.family_id = s.family_id;
  if f.delete_after is not null then return jsonb_build_object('result', 'closed', 'me', v_me); end if;
  -- 한 사람용 문자 링크는 한 번, 72시간 안에만
  if s.target_member_id is not null and (s.used_at is not null or s.created_at + interval '72 hours' <= now()) then
    return jsonb_build_object('result', 'expired', 'me', v_me);
  end if;
  select c.name into v_child from public.children c where c.family_id = f.id order by c.sort_order, c.created_at limit 1;
  return jsonb_build_object(
    'result', 'ok',
    'me', v_me,
    'child_name', v_child,
    'text_size_mode', f.text_size_mode,
    'new_entry_open', s.created_at + interval '72 hours' > now() and s.used_at is null,
    'target_member_id', s.target_member_id,
    'groups', coalesce((
      select jsonb_agg(jsonb_build_object(
        'id', g.id, 'name', g.name, 'hint', g.password_hint,
        'members', coalesce((
          select jsonb_agg(jsonb_build_object('id', m.id, 'name', m.display_name, 'avatar', m.avatar) order by m.created_at)
          from public.members m where m.group_id = g.id and m.status = 'active'
        ), '[]'::jsonb)
      ) order by g.sort_order, g.created_at)
      from public.groups g
      join public.share_groups sg on sg.group_id = g.id and sg.share_id = s.id
    ), '[]'::jsonb)
  );
end $$;

-- 가족 기기 자기 캐릭터(가족방마다, /me/avatar)
create or replace function public.sp_me() returns jsonb
language sql stable security definer set search_path = ''
as $$
  select jsonb_build_object('families', coalesce(jsonb_agg(jsonb_build_object(
      'family_id', f.id,
      'device', d.status,
      'member', case
        when m.id is null then null
        when m.status = 'pending' and m.pending_until <= now() then 'expired'
        else m.status end,
      'name', coalesce(m.display_name, d.requested_name),
      'closed', f.delete_after is not null,
      'download_allowed', f.download_allowed,
      'avatar', m.avatar,
      'child_name', (select c.name from public.children c where c.family_id = f.id order by c.sort_order, c.created_at limit 1),
      'children', case when d.status = 'active' and m.status = 'active' then
        (select coalesce(jsonb_agg(jsonb_build_object('name', c.name, 'birth_date', c.birth_date) order by c.sort_order, c.created_at), '[]'::jsonb)
           from public.children c where c.family_id = f.id) end
    ) order by d.last_seen_at), '[]'::jsonb))
  from public.devices d
  join public.families f on f.id = d.family_id
  left join public.members m on m.id = d.member_id
  where d.auth_user_id = auth.uid()
$$;

-- 엄빠 자기 캐릭터(설정 맨 위 내 이름 줄)
create or replace function public.sp_parent_home() returns jsonb
language sql stable security definer set search_path = ''
as $$
  select coalesce((
    select jsonb_build_object(
      'family_id', p.family_id,
      'role', p.role,
      'avatar', p.avatar,
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

-- 함께 관리하는 엄빠 목록에도 캐릭터(설정 › 가족, 리뷰 2026-11-01: 상대 엄빠 캐릭터가 안 보이던 것). 20261029000003 그대로에 avatar만
create or replace function public.sp_family_parents() returns jsonb
language sql stable security definer set search_path = ''
as $$
  select jsonb_build_object(
    'parents', coalesce((
      select jsonb_agg(jsonb_build_object('user_id', p.user_id, 'role', p.role, 'display_name', p.display_name, 'since', p.created_at, 'me', p.user_id = auth.uid(), 'avatar', p.avatar)
                       order by p.user_id <> auth.uid(), p.created_at)
      from public.parents p where p.family_id = public.sp_parent_family() and p.removed_at is null), '[]'::jsonb),
    'invite', (select jsonb_build_object('code', i.code, 'expires_at', i.expires_at) from public.parent_invites i
               where i.family_id = public.sp_parent_family() and i.used_at is null and i.expires_at > now()
               order by i.created_at desc limit 1))
  where public.sp_parent_family() is not null
$$;

-- 한마디 목록 + 쓴 사람 캐릭터(가족은 members, 엄빠는 parents)
create function public.sp_comment_list2(p_media_id uuid)
returns table (id uuid, name text, body text, created_at timestamptz, mine boolean, avatar smallint)
language sql stable security definer set search_path = ''
as $$
  select c.id, coalesce(m.display_name, p.display_name), c.body, c.created_at,
         coalesce(c.member_id in (select public.sp_device_members()) or c.parent_user_id = auth.uid(), false),
         coalesce(m.avatar, p.avatar)
  from public.comments c
  left join public.members m on m.id = c.member_id and m.status = 'active'
  left join public.parents p on p.user_id = c.parent_user_id
  where c.media_id = p_media_id and c.deleted_at is null
    and (m.id is not null or p.user_id is not null)
    and public.sp_can_view_media(p_media_id)
    and exists (select 1 from public.media x where x.id = p_media_id
                and (public.sp_device_active(x.family_id) or x.family_id = public.sp_parent_family()))
  order by c.created_at desc
  limit 100
$$;
revoke execute on function public.sp_comment_list2(uuid) from public, anon, authenticated;
grant execute on function public.sp_comment_list2(uuid) to authenticated;
