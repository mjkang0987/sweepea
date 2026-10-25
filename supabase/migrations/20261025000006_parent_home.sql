-- 부모 첫 화면: 내 가족방·역할·아이들. 아직 처음 설정 전이면 family_id null
create function public.sp_parent_home() returns jsonb
language sql stable security definer set search_path = ''
as $$
  select coalesce((
    select jsonb_build_object(
      'family_id', p.family_id,
      'role', p.role,
      'closing', f.delete_after is not null,
      'children', coalesce((
        select jsonb_agg(jsonb_build_object('id', c.id, 'name', c.name, 'birth_date', c.birth_date) order by c.sort_order, c.created_at)
        from public.children c where c.family_id = p.family_id
      ), '[]'::jsonb)
    )
    from public.parents p join public.families f on f.id = p.family_id
    where p.user_id = auth.uid()
  ), jsonb_build_object('family_id', null))
$$;

revoke execute on function public.sp_parent_home() from public, anon, authenticated;
grant execute on function public.sp_parent_home() to authenticated;
