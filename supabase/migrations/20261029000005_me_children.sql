-- 가족 앨범 기념일(사용자 2026-10-29 "100일 이벤트, 200일 이벤트 이런 식으로", "1, 2, 3 셋 다"): 가족 기기에도 아이 이름·생일을 넘긴다.
-- 승인된 가족(기기 active·구성원 active)만. 대기·막힌 기기는 지금처럼 첫 아이 이름만
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
