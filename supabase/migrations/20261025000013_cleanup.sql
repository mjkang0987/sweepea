-- 매일 예약 작업(service_role)이 부르는 정리 함수. 지운 사진·가족방의 R2 폴더는 r2_cleanup 대기열로 넘긴다

-- 하루 지나도 끝나지 않은 올리기: 행을 지우고 그 사진 폴더를 대기열에(완료 전이라 용량엔 안 잡혀 있다)
create function public.sp_cleanup_stale_uploads() returns int
language plpgsql security definer set search_path = ''
as $$
declare v_n int;
begin
  with gone as (
    delete from public.media where status = 'uploading' and created_at < now() - interval '1 day'
    returning family_id, id
  ), queued as (
    insert into public.r2_cleanup (prefix)
      select family_id::text || '/' || id::text || '/' from gone
      on conflict do nothing
  )
  select count(*) into v_n from gone;
  return v_n;
end $$;

-- 대기열에서 오래된 것부터 몇 개(지운 뒤 sp_r2_cleanup_done으로 뺀다. 실패하면 다음 날 다시)
create function public.sp_r2_cleanup_take(p_limit int) returns setof text
language sql stable security definer set search_path = ''
as $$ select prefix from public.r2_cleanup order by queued_at limit greatest(1, least(p_limit, 500)) $$;

create function public.sp_r2_cleanup_done(p_prefix text) returns void
language sql security definer set search_path = ''
as $$ delete from public.r2_cleanup where prefix = p_prefix $$;

revoke execute on function public.sp_cleanup_stale_uploads(), public.sp_r2_cleanup_take(int), public.sp_r2_cleanup_done(text)
  from public, anon, authenticated;
grant execute on function public.sp_cleanup_stale_uploads(), public.sp_r2_cleanup_take(int), public.sp_r2_cleanup_done(text) to service_role;
