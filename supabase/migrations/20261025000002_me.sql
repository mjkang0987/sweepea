-- 지금 기기(익명 사용자)가 들어간 가족방들(마지막으로 들어가려던 곳이 끝). 앨범·승인 기다림 화면이 무엇을 보여 줄지 정할 때 쓴다.
-- families[]: family_id, device(active | pending: 10번 틀림·경보 | revoked: 내 가족 아님),
--             member(null | active | pending: 새 이름 승인 대기 | expired: 승인 대기 3일 지남 | rejected), name, closed, child_name
create function public.sp_me() returns jsonb
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
      'child_name', (select c.name from public.children c where c.family_id = f.id order by c.sort_order, c.created_at limit 1)
    ) order by d.last_seen_at), '[]'::jsonb))
  from public.devices d
  join public.families f on f.id = d.family_id
  left join public.members m on m.id = d.member_id
  where d.auth_user_id = auth.uid()
$$;

revoke execute on function public.sp_me() from public, anon;
grant execute on function public.sp_me() to authenticated;
