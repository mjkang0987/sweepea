-- 지금 기기(익명 사용자)의 상태. 가족 화면이 어디로 보낼지 정할 때 쓴다.
-- device: null(처음) | active | pending(비밀번호 10번 틀림·경보) | revoked(내 가족 아님)
-- member: null | active | pending(새 이름 승인 대기) | expired(승인 대기 3일 지남) | rejected
create function public.sp_me() returns jsonb
language sql stable security definer set search_path = ''
as $$
  select coalesce((
    select jsonb_build_object(
      'device', d.status,
      'member', case
        when m.id is null then null
        when m.status = 'pending' and m.pending_until <= now() then 'expired'
        else m.status end,
      'name', coalesce(m.display_name, d.requested_name),
      'closed', f.delete_after is not null,
      'child_name', (select c.name from public.children c where c.family_id = f.id order by c.sort_order, c.created_at limit 1)
    )
    from public.devices d
    join public.families f on f.id = d.family_id
    left join public.members m on m.id = d.member_id
    where d.auth_user_id = auth.uid()
  ), jsonb_build_object('device', null))
$$;

revoke execute on function public.sp_me() from public, anon;
grant execute on function public.sp_me() to authenticated;
