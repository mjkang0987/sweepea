-- 주소 다시 만들기: 이 그룹이 들어간 공유 링크를 모두 막아 예전 주소로는 새로 못 들어오게 한다.
-- 지우지 않는다: 그 링크로 들어와 승인 기다리는 사람은 링크 사진(entry_share_id)을 계속 봐야 한다.
-- 이미 들어온 기기는 그대로(출입증은 링크와 상관없다). 새 링크는 sp_create_share로 따로 만든다
create function public.sp_reset_group_links(p_group_id uuid) returns int
language plpgsql security definer set search_path = ''
as $$
declare v_family uuid; v_n int;
begin
  select family_id into v_family from public.groups where id = p_group_id and family_id = public.sp_parent_family();
  -- 탈퇴 유예 중이면 새 링크를 못 만드니 막기만 하고 끝나지 않게 처음부터 거절(sp_can_upload)
  if v_family is null or not public.sp_can_upload(v_family) then
    raise exception 'not_allowed' using errcode = '42501';
  end if;
  update public.shares s set revoked_at = now()
    where s.revoked_at is null and s.id in (select sg.share_id from public.share_groups sg where sg.group_id = p_group_id);
  get diagnostics v_n = row_count;
  return v_n;
end $$;

revoke execute on function public.sp_reset_group_links(uuid) from public, anon, authenticated;
grant execute on function public.sp_reset_group_links(uuid) to authenticated;
