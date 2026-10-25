-- 부모 최근 반응: 승인된 가족이 남긴 반응·한마디(최근 30일, 50개). 앱 알림 전까지 부모가 열어서 본다
create function public.sp_parent_activity() returns jsonb
language sql stable security definer set search_path = ''
as $$
  with p as (select family_id, activity_seen_at from public.parents where user_id = auth.uid()),
  items as (
    select 'reaction' as type, r.kind, null::text as body, r.created_at as at, m.display_name as who, x.id as media_id, x.thumb_key
      from public.reactions r join public.media x on x.id = r.media_id and x.status = 'ready'
      join public.members m on m.id = r.member_id and m.status = 'active'
      where x.family_id = (select family_id from p) and r.created_at > now() - interval '30 days'
    union all
    select 'comment', null, c.body, c.created_at, m.display_name, x.id, x.thumb_key
      from public.comments c join public.media x on x.id = c.media_id and x.status = 'ready'
      join public.members m on m.id = c.member_id and m.status = 'active'
      where x.family_id = (select family_id from p) and c.deleted_at is null and c.created_at > now() - interval '30 days'
    order by at desc
    limit 50
  )
  select jsonb_build_object(
    'seen_at', (select activity_seen_at from p),
    -- 이 목록을 읽은 시각. 읽음 표시는 이 시각까지만(그 사이 온 반응은 다음에 새 반응으로)
    'read_at', now(),
    'items', coalesce((select jsonb_agg(to_jsonb(i) order by i.at desc) from items i), '[]'::jsonb)
  )
  where exists (select 1 from p)
$$;

create function public.sp_mark_activity_seen(p_read_at timestamptz) returns void
language sql security definer set search_path = ''
as $$
  update public.parents set activity_seen_at = greatest(activity_seen_at, least(p_read_at, now()))
    where user_id = auth.uid()
$$;

-- 새 반응 수·목록은 시각으로 거른다(사진이 많아도 최근 것만 본다)
create index reactions_recent on public.reactions (created_at);
create index comments_recent on public.comments (created_at);

revoke execute on function public.sp_parent_activity(), public.sp_mark_activity_seen(timestamptz) from public, anon, authenticated;
grant execute on function public.sp_parent_activity(), public.sp_mark_activity_seen(timestamptz) to authenticated;
