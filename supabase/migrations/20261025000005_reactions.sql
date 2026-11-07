-- 반응·한마디: 가족 화면은 이 함수로만(구성원 id를 클라이언트가 몰라도 되게, 사진의 가족방 이름으로)

-- 반응 켜기·끄기. 볼 수 있는 사진에만
create function public.sp_react(p_media_id uuid, p_kind text, p_on boolean) returns boolean
language plpgsql security definer set search_path = ''
as $$
declare v_member uuid := public.sp_media_member(p_media_id);
begin
  -- 승인된 구성원만(승인 대기는 보기만)
  if v_member is null or not public.sp_can_view_media(p_media_id)
     or not exists (select 1 from public.members where id = v_member and status = 'active') then
    raise exception 'not_allowed' using errcode = '42501';
  end if;
  if p_kind not in ('heart', 'best', 'good', 'moved', 'sparkle') then
    raise exception 'bad_request' using errcode = '22023';
  end if;
  if p_on then
    insert into public.reactions (media_id, member_id, kind) values (p_media_id, v_member, p_kind) on conflict do nothing;
  else
    delete from public.reactions where media_id = p_media_id and member_id = v_member and kind = p_kind;
  end if;
  return p_on;
end $$;

-- 한마디 보내기. 구성원별 하루 30개(PT429 → HTTP 429)
create function public.sp_comment(p_media_id uuid, p_body text) returns uuid
language plpgsql security definer set search_path = ''
as $$
declare
  v_member uuid := public.sp_media_member(p_media_id);
  v_body text := btrim(p_body);
  v_id uuid;
begin
  if v_member is null or not public.sp_can_view_media(p_media_id)
     or not exists (select 1 from public.members where id = v_member and status = 'active') then
    raise exception 'not_allowed' using errcode = '42501';
  end if;
  if v_body is null or char_length(v_body) not between 1 and 200 then
    raise exception 'bad_request' using errcode = '22023';
  end if;
  -- 같은 사람 동시 전송이 한도를 넘지 않게
  perform pg_advisory_xact_lock(hashtext(v_member::text));
  if (select count(*) from public.comments where member_id = v_member and created_at > now() - interval '1 day') >= 30 then
    raise exception 'too_many_comments' using errcode = 'PT429';
  end if;
  insert into public.comments (media_id, member_id, body) values (p_media_id, v_member, v_body) returning id into v_id;
  return v_id;
end $$;

-- 사진별 반응 수(종류별)·내가 눌렀는지·한마디 수. 볼 수 있는 사진만(사진마다 한 번 확인), 승인된 구성원 것만 센다
create function public.sp_reaction_counts(p_media_ids uuid[])
returns table (media_id uuid, kind text, n int, mine boolean)
language sql stable security definer set search_path = ''
as $$
  with ok as (select id from unnest(p_media_ids[1:200]) id where public.sp_can_view_media(id)),
  my as (select public.sp_device_members() id)
  select r.media_id, r.kind, count(*)::int, bool_or(r.member_id in (select id from my))
  from public.reactions r join public.members m on m.id = r.member_id and m.status = 'active'
  where r.media_id in (select id from ok)
  group by r.media_id, r.kind
  union all
  select c.media_id, 'comment', count(*)::int, bool_or(c.member_id in (select id from my))
  from public.comments c join public.members m on m.id = c.member_id and m.status = 'active'
  where c.media_id in (select id from ok) and c.deleted_at is null
  group by c.media_id
$$;

create index comments_member_recent on public.comments (member_id, created_at);

revoke execute on function public.sp_react(uuid, text, boolean), public.sp_comment(uuid, text),
  public.sp_reaction_counts(uuid[]) from public, anon, authenticated;
grant execute on function public.sp_react(uuid, text, boolean), public.sp_comment(uuid, text),
  public.sp_reaction_counts(uuid[]) to authenticated;
