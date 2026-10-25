-- 주소 다시 만들기: 이 그룹이 들어간 공유 링크를 모두 지워 예전 주소를 바로 막는다.
-- 이미 들어온 기기는 그대로(출입증은 링크와 상관없다). 새 링크는 sp_create_share로 따로 만든다
create function public.sp_reset_group_links(p_group_id uuid) returns int
language plpgsql security definer set search_path = ''
as $$
declare v_n int;
begin
  if not exists (select 1 from public.groups where id = p_group_id and family_id = public.sp_parent_family()) then
    raise exception 'not_allowed' using errcode = '42501';
  end if;
  delete from public.shares s
    where s.id in (select sg.share_id from public.share_groups sg where sg.group_id = p_group_id);
  get diagnostics v_n = row_count;
  return v_n;
end $$;

revoke execute on function public.sp_reset_group_links(uuid) from public, anon, authenticated;
grant execute on function public.sp_reset_group_links(uuid) to authenticated;
