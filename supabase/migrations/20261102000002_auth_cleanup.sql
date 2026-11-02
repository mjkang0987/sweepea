-- 탈퇴·정리 때 로그인 계정도 지우기(138 개인정보 처리방침 준비): 예전엔 가족방·사진·가족은 지워도 Supabase 로그인 계정(auth.users:
-- 카카오 이메일·닉네임·프로필, 가족 기기 익명 계정)은 남았다.
-- sp_purge_family·sp_unlink_parent는 본문 그대로에 계정 지우기를 더함(이름·받는 값·권한 같음). 지우는 문(drop) 없음

-- 가족방 지우기: 그 가족방 엄빠(남길 기록이 없어 행을 지운 사람)와 가족 기기의 로그인 계정도 지운다.
-- 다른 가족방에 기록이 남아 행이 남은 엄빠, 다른 가족방에도 기기로 들어가 있는 계정, 지금 로그인한 본인(새 가족방을 만드는 중)은 남긴다
create or replace function public.sp_purge_family(p_family uuid) returns void
language plpgsql security definer set search_path = ''
as $$
declare
  v_users uuid[];
begin
  v_users := array(select d.auth_user_id from public.devices d where d.family_id = p_family);
  insert into public.r2_cleanup (prefix) values (p_family::text || '/') on conflict do nothing;
  -- 다른 가족방에 반응·한마디가 남은 엄빠 행은 남긴다(가족방을 지우면 family_id가 빔)
  with gone as (
    delete from public.parents p where p.family_id = p_family
      and not exists (select 1 from public.reactions r join public.media x on x.id = r.media_id where r.parent_user_id = p.user_id and x.family_id <> p_family)
      and not exists (select 1 from public.comments c join public.media x on x.id = c.media_id where c.parent_user_id = p.user_id and x.family_id <> p_family)
    returning p.user_id
  )
  select v_users || coalesce(array_agg(user_id), '{}') into v_users from gone;
  delete from public.families where id = p_family;
  delete from auth.users u where u.id = any (v_users)
    and u.id is distinct from auth.uid()
    and not exists (select 1 from public.parents p where p.user_id = u.id)
    and not exists (select 1 from public.devices d where d.auth_user_id = u.id);
end $$;

-- 엄빠 하나만 빠지기(나가기·내보내기): 남길 기록이 없어 행을 지우면 로그인 계정도 지운다(다른 가족방 기기로도 쓰는 계정은 남김)
create or replace function public.sp_unlink_parent(p_user uuid) returns void
language plpgsql security definer set search_path = ''
as $$
begin
  if exists (select 1 from public.reactions where parent_user_id = p_user) or exists (select 1 from public.comments where parent_user_id = p_user) then
    update public.parents set removed_at = now() where user_id = p_user;
  else
    delete from public.parents where user_id = p_user;
    delete from auth.users u where u.id = p_user and not exists (select 1 from public.devices d where d.auth_user_id = u.id);
  end if;
  delete from public.parent_invites where created_by = p_user and used_at is null;
end $$;

-- 매일 정리: 들어오지 못하고 남은 익명 계정(비밀번호만 내고 기기가 안 생김) 7일 뒤, 비밀번호 틀린 기록 7일 뒤 지운다. 지운 계정 수
create function public.sp_cleanup_auth() returns int
language plpgsql security definer set search_path = ''
as $$
declare v_n int;
begin
  delete from public.entry_failures where at < now() - interval '7 days';
  with gone as (
    delete from auth.users u
    where u.is_anonymous and u.created_at < now() - interval '7 days'
      and not exists (select 1 from public.devices d where d.auth_user_id = u.id)
      and not exists (select 1 from public.parents p where p.user_id = u.id)
    returning 1
  )
  select count(*) into v_n from gone;
  return v_n;
end $$;
revoke execute on function public.sp_cleanup_auth() from public, anon, authenticated;
grant execute on function public.sp_cleanup_auth() to service_role;
