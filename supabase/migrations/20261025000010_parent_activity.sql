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
    'items', coalesce((select jsonb_agg(to_jsonb(i) order by i.at desc) from items i), '[]'::jsonb)
  )
  where exists (select 1 from p)
$$;

create function public.sp_mark_activity_seen() returns void
language sql security definer set search_path = ''
as $$ update public.parents set activity_seen_at = now() where user_id = auth.uid() $$;

revoke execute on function public.sp_parent_activity(), public.sp_mark_activity_seen() from public, anon, authenticated;
grant execute on function public.sp_parent_activity(), public.sp_mark_activity_seen() to authenticated;
