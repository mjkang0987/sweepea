-- 엄빠도 반응·한마디를 남긴다(가족방을 만든 부모 계정). 배우자는 원래 구성원으로 들어와 남긴다.
-- 한 행은 구성원 또는 부모 중 하나가 쓴다.

alter table public.reactions add column parent_user_id uuid references public.parents (user_id) on delete cascade;
alter table public.reactions drop constraint reactions_pkey;
alter table public.reactions alter column member_id drop not null;
alter table public.reactions add constraint reactions_one_author check (num_nonnulls(member_id, parent_user_id) = 1);
create unique index reactions_member_once on public.reactions (media_id, member_id, kind) where member_id is not null;
create unique index reactions_parent_once on public.reactions (media_id, parent_user_id, kind) where parent_user_id is not null;
-- 부모 계정을 지울 때(cascade) 찾기
create index reactions_parent on public.reactions (parent_user_id) where parent_user_id is not null;
-- 부모 사용자 id는 가족에게 안 보인다(사진의 올린 부모 id·기기 사용자 id와 같은 이유: 두 집을 맞춰 보면 같은 사람인 걸 앎)
revoke select on public.reactions from authenticated;
grant select (media_id, member_id, kind, created_at) on public.reactions to authenticated;

alter table public.comments add column parent_user_id uuid references public.parents (user_id) on delete cascade;
alter table public.comments alter column member_id drop not null;
alter table public.comments add constraint comments_one_author check (num_nonnulls(member_id, parent_user_id) = 1);
create index comments_parent_recent on public.comments (parent_user_id, created_at) where parent_user_id is not null;

-- 부모 자기 가족방의 다 올라간 사진인가. 탈퇴 유예 중이면 막는다(가족 화면도 닫혀 있다)
create function public.sp_parent_media(p_media_id uuid) returns boolean
language sql stable security definer set search_path = ''
as $$
  select exists (
    select 1 from public.media x join public.families f on f.id = x.family_id and f.delete_after is null
    where x.id = p_media_id and x.status = 'ready' and x.family_id = public.sp_parent_family())
$$;

create function public.sp_parent_react(p_media_id uuid, p_kind text, p_on boolean) returns boolean
language plpgsql security definer set search_path = ''
as $$
begin
  if not public.sp_parent_media(p_media_id) then
    raise exception 'not_allowed' using errcode = '42501';
  end if;
  if p_kind not in ('heart', 'best', 'good', 'moved', 'sparkle') then
    raise exception 'bad_request' using errcode = '22023';
  end if;
  if p_on then
    insert into public.reactions (media_id, parent_user_id, kind) values (p_media_id, auth.uid(), p_kind) on conflict do nothing;
  else
    delete from public.reactions where media_id = p_media_id and parent_user_id = auth.uid() and kind = p_kind;
  end if;
  return p_on;
end $$;

-- 한마디: 구성원과 같은 규칙(1~200자, 하루 30개)
create function public.sp_parent_comment(p_media_id uuid, p_body text) returns uuid
language plpgsql security definer set search_path = ''
as $$
declare
  v_body text := btrim(p_body);
  v_id uuid;
begin
  if not public.sp_parent_media(p_media_id) then
    raise exception 'not_allowed' using errcode = '42501';
  end if;
  if v_body is null or char_length(v_body) not between 1 and 200 then
    raise exception 'bad_request' using errcode = '22023';
  end if;
  perform pg_advisory_xact_lock(hashtext(auth.uid()::text));
  if (select count(*) from public.comments where parent_user_id = auth.uid() and created_at > now() - interval '1 day') >= 30 then
    raise exception 'too_many_comments' using errcode = 'PT429';
  end if;
  insert into public.comments (media_id, parent_user_id, body) values (p_media_id, auth.uid(), v_body) returning id into v_id;
  return v_id;
end $$;

-- 반응 수: 승인된 구성원 + 부모 것을 센다. '내가 눌렀는지'는 내 구성원 또는 내 부모 계정
create or replace function public.sp_reaction_counts(p_media_ids uuid[])
returns table (media_id uuid, kind text, n int, mine boolean)
language sql stable security definer set search_path = ''
as $$
  with ok as (select id from unnest(p_media_ids[1:200]) id where public.sp_can_view_media(id)),
  my as (select public.sp_device_members() id)
  select r.media_id, r.kind, count(*)::int,
         coalesce(bool_or(r.member_id in (select id from my) or r.parent_user_id = auth.uid()), false)
  from public.reactions r left join public.members m on m.id = r.member_id
  where r.media_id in (select id from ok) and (m.status = 'active' or r.parent_user_id is not null)
  group by r.media_id, r.kind
  union all
  select c.media_id, 'comment', count(*)::int,
         coalesce(bool_or(c.member_id in (select id from my) or c.parent_user_id = auth.uid()), false)
  from public.comments c left join public.members m on m.id = c.member_id
  where c.media_id in (select id from ok) and c.deleted_at is null and (m.status = 'active' or c.parent_user_id is not null)
  group by c.media_id
$$;

revoke execute on function public.sp_parent_media(uuid) from public, anon, authenticated;
revoke execute on function public.sp_parent_react(uuid, text, boolean), public.sp_parent_comment(uuid, text) from public, anon, authenticated;
grant execute on function public.sp_parent_react(uuid, text, boolean), public.sp_parent_comment(uuid, text) to authenticated;
