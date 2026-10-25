-- 탈퇴: 가족 화면은 바로 닫히고(delete_after가 있으면 모든 가족 함수가 막는다) 3일 뒤 지운다.
-- 유예 중 다시 로그인한 부모는 되살릴 수 있다. delete_after는 이 함수들로만 바꾼다(열 권한에서 뺐다)

create function public.sp_request_delete() returns timestamptz
language plpgsql security definer set search_path = ''
as $$
declare v_family uuid := public.sp_parent_family(); v_at timestamptz;
begin
  if v_family is null then raise exception 'parent_only' using errcode = '42501'; end if;
  -- 스토어 구독은 탈퇴해도 결제가 멈추지 않으니 먼저 해지하게 한다(PT402 → HTTP 402)
  if exists (select 1 from public.entitlements where family_id = v_family and expires_at > now()) then
    raise exception 'subscribed' using errcode = 'PT402';
  end if;
  update public.families set delete_after = coalesce(delete_after, now() + interval '3 days')
    where id = v_family returning delete_after into v_at;
  return v_at;
end $$;

create function public.sp_restore_family() returns void
language plpgsql security definer set search_path = ''
as $$
declare v_family uuid := public.sp_parent_family();
begin
  if v_family is null then raise exception 'parent_only' using errcode = '42501'; end if;
  -- 기한이 지났으면(지우는 작업이 아직 안 돌았어도) 되살리지 않는다
  update public.families set delete_after = null where id = v_family and delete_after > now();
  if not found then raise exception 'not_closing' using errcode = '22023'; end if;
end $$;

-- 예약 작업(service_role)이 부른다. 지운 가족방은 r2_cleanup에 남아 그 R2 폴더를 지운다
create function public.sp_purge_deleted_families() returns setof uuid
language plpgsql security definer set search_path = ''
as $$
declare v_id uuid;
begin
  for v_id in select id from public.families where delete_after <= now() loop
    perform public.sp_purge_family(v_id);
    return next v_id;
  end loop;
end $$;

revoke execute on function public.sp_request_delete(), public.sp_restore_family(), public.sp_purge_deleted_families()
  from public, anon, authenticated;
grant execute on function public.sp_request_delete(), public.sp_restore_family() to authenticated;
grant execute on function public.sp_purge_deleted_families() to service_role;
