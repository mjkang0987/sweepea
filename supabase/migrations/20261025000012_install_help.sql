-- 홈 화면에 두기 부탁: 가족 기기가 자기 이름으로만. 카톡 안에서는 홈 화면에 둘 수 없어 엄마아빠가 문자 링크로 도와준다
create function public.sp_request_install_help(p_family_id uuid) returns void
language plpgsql security definer set search_path = ''
as $$
declare v_member uuid := public.sp_device_member(p_family_id);
begin
  -- 승인된 가족만(부모 최근 반응에도 승인된 사람만 보인다)
  if v_member is null or not public.sp_device_active(p_family_id) then raise exception 'not_allowed' using errcode = '42501'; end if;
  update public.members set install_help_at = now() where id = v_member;
end $$;

revoke execute on function public.sp_request_install_help(uuid) from public, anon, authenticated;
grant execute on function public.sp_request_install_help(uuid) to authenticated;
