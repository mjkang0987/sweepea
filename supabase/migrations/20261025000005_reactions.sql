-- 반응·한마디: 가족 화면은 이 함수로만(구성원 id를 클라이언트가 몰라도 되게, 사진의 가족방 이름으로)

-- 반응 켜기·끄기. 볼 수 있는 사진에만
create function public.sp_react(p_media_id uuid, p_kind text, p_on boolean) returns boolean
language plpgsql security definer set search_path = ''
as $$
declare v_member uuid := public.sp_media_member(p_media_id);
begin
  if v_member is null or not public.sp_can_view_media(p_media_id) then
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
  if v_member is null or not public.sp_can_view_media(p_media_id) then
    raise exception 'not_allowed' using errcode = '42501';
  end if;
  if v_body is null or char_length(v_body) not between 1 and 200 then
    raise exception 'bad_request' using errcode = '22023';
  end if;
  if (select count(*) from public.comments where member_id = v_member and created_at > now() - interval '1 day') >= 30 then
    raise exception 'too_many_comments' using errcode = 'PT429';
  end if;
  insert into public.comments (media_id, member_id, body) values (p_media_id, v_member, v_body) returning id into v_id;
  return v_id;
end $$;

-- 사진별 반응 수(종류별)·내가 눌렀는지·한마디 수. 호출자 권한이라 RLS로 볼 수 있는 것만 센다
create function public.sp_reaction_counts(p_media_ids uuid[])
returns table (media_id uuid, kind text, n int, mine boolean)
language sql stable set search_path = ''
as $$
  select r.media_id, r.kind, count(*)::int, bool_or(r.member_id in (select public.sp_device_members()))
  from public.reactions r
  where r.media_id = any (p_media_ids[1:200])
  group by r.media_id, r.kind
  union all
  select c.media_id, 'comment', count(*)::int, bool_or(c.member_id in (select public.sp_device_members()))
  from public.comments c
  where c.media_id = any (p_media_ids[1:200]) and c.deleted_at is null
  group by c.media_id
$$;

revoke execute on function public.sp_react(uuid, text, boolean), public.sp_comment(uuid, text),
  public.sp_reaction_counts(uuid[]) from public, anon, authenticated;
grant execute on function public.sp_react(uuid, text, boolean), public.sp_comment(uuid, text),
  public.sp_reaction_counts(uuid[]) to authenticated;
