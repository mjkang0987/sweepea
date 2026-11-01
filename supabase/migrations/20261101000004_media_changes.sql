-- 사진 변경 기록(123, 사용자 2026-11-01 "수정 기록이 남지 않는 게 이상한 거 아냐?" → "DB에는 넣어 두고 사진엔 비노출, 수정 진입 시 내역 보이도록").
-- 올릴 때(처음 그룹·아이·찍은 날)와 사진 정보를 고칠 때(전·후) 한 줄씩. 누가: 엄빠 계정 또는 가족 구성원. 표는 함수로만 읽고 쓴다.
-- sp_create_media(20261025000004)·sp_update_media(20261025000009)는 본문 그대로에 기록 한 줄만 더함(이름·받는 값·권한 같음). 지우는 문 없음

create table public.media_changes (
  id bigint generated always as identity primary key,
  media_id uuid not null references public.media (id) on delete cascade,
  family_id uuid not null references public.families (id) on delete cascade,
  kind text not null check (kind in ('create', 'update')),
  by_parent uuid references public.parents (user_id) on delete set null,
  by_member uuid references public.members (id) on delete set null,
  group_ids uuid[] not null,
  old_group_ids uuid[],
  child_ids uuid[] not null default '{}',
  old_child_ids uuid[],
  taken_at timestamptz not null,
  old_taken_at timestamptz,
  created_at timestamptz not null default now()
);
create index media_changes_media on public.media_changes (media_id, created_at desc);
create index media_changes_family on public.media_changes (family_id);
alter table public.media_changes enable row level security;
revoke all on public.media_changes from anon, authenticated;

create or replace function public.sp_create_media(
  p_family_id uuid, p_kind text, p_taken_at timestamptz, p_taken_at_source text,
  p_width int default null, p_height int default null, p_duration_sec numeric default null,
  p_group_ids uuid[] default null, p_child_ids uuid[] default '{}'
) returns uuid
language plpgsql security definer set search_path = ''
as $$
declare
  -- 익명 기기는 sp_parent_family()가 null이라 coalesce가 없으면 두 갈래 다 null이 된다
  v_parent boolean := coalesce(p_family_id = public.sp_parent_family(), false);
  v_member uuid := public.sp_device_member(p_family_id);
  v_groups uuid[];
  v_id uuid;
begin
  if not public.sp_can_upload(p_family_id) or (not v_parent and v_member is null)
     or exists (select 1 from public.families where id = p_family_id and delete_after is not null) then
    raise exception 'not_allowed' using errcode = '42501';
  end if;
  -- 무료 가족방은 저장 용량 5GB(5×1024³)가 차면 새로 올리기만 멈춘다. PT507 → HTTP 507
  if exists (select 1 from public.families where id = p_family_id and plan = 'free' and storage_used_bytes >= 5368709120) then
    raise exception 'storage_full' using errcode = 'PT507';
  end if;
  -- 끝내지 않은 올리기가 쌓이지 않게(완료 전 파일은 용량에 안 잡힌다). 올린 사람별·최근 하루만 세서
  -- 한 사람이 가족 전체를 막지 못하게 한다. 오래된 것 지우기는 이슈 13의 정리 작업. PT429 → PostgREST가 HTTP 429로
  if (select count(*) from public.media
      where family_id = p_family_id and status = 'uploading' and created_at > now() - interval '1 day'
        and (uploaded_by_parent = auth.uid() or uploaded_by_member = v_member)) >= 50 then
    raise exception 'too_many_uploads' using errcode = 'PT429';
  end if;
  v_groups := coalesce(p_group_ids,
    array(select g.id from public.groups g where g.family_id = p_family_id and g.include_by_default));
  if coalesce(array_length(v_groups, 1), 0) = 0
     or exists (select 1 from unnest(v_groups) x where x not in (select id from public.groups where family_id = p_family_id))
     or exists (select 1 from unnest(coalesce(p_child_ids, '{}')) x where x not in (select id from public.children where family_id = p_family_id))
  then
    raise exception 'bad_request' using errcode = '22023';
  end if;
  insert into public.media (family_id, uploaded_by_parent, uploaded_by_member, kind, taken_at, taken_at_source, width, height, duration_sec)
    values (p_family_id, case when v_parent then auth.uid() end, case when not v_parent then v_member end,
            p_kind, p_taken_at, p_taken_at_source, p_width, p_height, p_duration_sec)
    returning id into v_id;
  insert into public.media_groups (family_id, media_id, group_id) select p_family_id, v_id, x from unnest(v_groups) x;
  insert into public.media_children (family_id, media_id, child_id) select p_family_id, v_id, x from unnest(coalesce(p_child_ids, '{}')) x;
  -- 변경 기록: 처음 들어간 그룹·아이·찍은 날(20261101000004)
  insert into public.media_changes (media_id, family_id, kind, by_parent, by_member, group_ids, child_ids, taken_at)
    values (v_id, p_family_id, 'create', case when v_parent then auth.uid() end, case when not v_parent then v_member end,
            v_groups, coalesce(p_child_ids, '{}'), p_taken_at);
  return v_id;
end $$;

create or replace function public.sp_update_media(p_media_id uuid, p_taken_at timestamptz, p_child_ids uuid[], p_group_ids uuid[])
returns void
language plpgsql security definer set search_path = ''
as $$
declare
  v_family uuid;
  v_old_taken timestamptz;
  v_old_groups uuid[];
  v_old_children uuid[];
  v_parent boolean;
begin
  select family_id into v_family from public.media where id = p_media_id and status = 'ready';
  -- 탈퇴 유예 중엔 부모도 고치지 못한다(sp_can_upload)
  if v_family is null or not public.sp_can_edit_media(p_media_id) or not public.sp_can_upload(v_family) then
    raise exception 'not_allowed' using errcode = '42501';
  end if;
  if coalesce(array_length(p_group_ids, 1), 0) = 0
     or exists (select 1 from unnest(p_group_ids) x where x not in (select id from public.groups where family_id = v_family))
     or exists (select 1 from unnest(coalesce(p_child_ids, '{}')) x where x not in (select id from public.children where family_id = v_family))
  then
    raise exception 'bad_request' using errcode = '22023';
  end if;
  -- 변경 기록용 바꾸기 전 값(20261101000004)
  select taken_at into v_old_taken from public.media where id = p_media_id;
  v_old_groups := array(select group_id from public.media_groups where media_id = p_media_id order by group_id);
  v_old_children := array(select child_id from public.media_children where media_id = p_media_id order by child_id);
  update public.media
    set taken_at = p_taken_at,
        taken_at_source = case when taken_at = p_taken_at then taken_at_source else 'manual' end
    where id = p_media_id;
  delete from public.media_groups where media_id = p_media_id and group_id <> all (p_group_ids);
  insert into public.media_groups (family_id, media_id, group_id)
    select v_family, p_media_id, g from unnest(p_group_ids) g on conflict do nothing;
  delete from public.media_children where media_id = p_media_id and child_id <> all (coalesce(p_child_ids, '{}'));
  insert into public.media_children (family_id, media_id, child_id)
    select v_family, p_media_id, c from unnest(coalesce(p_child_ids, '{}')) c on conflict do nothing;
  -- 변경 기록: 무엇이든 바뀌었을 때만 한 줄(누가: 엄빠 계정 또는 그 가족방의 내 구성원)
  if v_old_taken is distinct from p_taken_at
     or v_old_groups is distinct from array(select distinct g from unnest(p_group_ids) g order by g)
     or v_old_children is distinct from array(select distinct c from unnest(coalesce(p_child_ids, '{}')) c order by c) then
    v_parent := coalesce(v_family = public.sp_parent_family(), false);
    insert into public.media_changes (media_id, family_id, kind, by_parent, by_member, group_ids, old_group_ids, child_ids, old_child_ids, taken_at, old_taken_at)
      values (p_media_id, v_family, 'update', case when v_parent then auth.uid() end,
              case when not v_parent then public.sp_device_member(v_family) end,
              array(select distinct g from unnest(p_group_ids) g order by g), v_old_groups,
              array(select distinct c from unnest(coalesce(p_child_ids, '{}')) c order by c), v_old_children,
              p_taken_at, v_old_taken);
  end if;
end $$;

-- 엄빠: 이 사진의 변경 기록(최근 것부터 50줄). 그룹·아이는 지금 이름으로(지운 것은 '지운 그룹'·'지운 아이'), 누가 = 엄마/아빠/가족 이름
create function public.sp_media_changes(p_media_id uuid)
returns table (at timestamptz, kind text, who text, groups text[], old_groups text[], children text[], old_children text[], taken_at timestamptz, old_taken_at timestamptz)
language sql stable security definer set search_path = ''
as $$
  select c.created_at, c.kind,
         coalesce(case p.role when 'mom' then '엄마' when 'dad' then '아빠' end, m.display_name, '알 수 없음'),
         array(select coalesce(g.name, '지운 그룹') from unnest(c.group_ids) with ordinality u (id, o) left join public.groups g on g.id = u.id order by g.sort_order nulls last, u.o),
         case when c.old_group_ids is null then null else
           array(select coalesce(g.name, '지운 그룹') from unnest(c.old_group_ids) with ordinality u (id, o) left join public.groups g on g.id = u.id order by g.sort_order nulls last, u.o) end,
         array(select coalesce(k.name, '지운 아이') from unnest(c.child_ids) with ordinality u (id, o) left join public.children k on k.id = u.id order by k.sort_order nulls last, u.o),
         case when c.old_child_ids is null then null else
           array(select coalesce(k.name, '지운 아이') from unnest(c.old_child_ids) with ordinality u (id, o) left join public.children k on k.id = u.id order by k.sort_order nulls last, u.o) end,
         c.taken_at, c.old_taken_at
  from public.media_changes c
  left join public.parents p on p.user_id = c.by_parent
  left join public.members m on m.id = c.by_member
  where c.media_id = p_media_id and public.sp_parent_media(p_media_id)
  order by c.created_at desc, c.id desc
  limit 50
$$;
revoke execute on function public.sp_media_changes(uuid) from public, anon, authenticated;
grant execute on function public.sp_media_changes(uuid) to authenticated;
