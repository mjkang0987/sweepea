-- 운영 올린 사진·영상 목록(173, 사용자 2026-11-04 "사진 업로드된 거 리스트 뿌려줘" → '정보만' 고름).
-- 사진·영상 자체(파일 주소 object/view/thumb/poster key)는 내보내지 않는다 — 처리방침 '운영자는 사진을 보지 않는다' 그대로.
-- 한 줄: 올린 때·가족방·종류·크기·가로세로·영상 길이·상태(올림/올리다 멈춤)·올린 사람(엄마/아빠 역할, 가족 기기는 구성원 이름).
-- 고른 기간(서울 날짜, 끝 포함)에 올린 것, 지운 것 빼고, 최근 순 50개씩. p_family가 있으면 그 가족방만. 서버(service_role)만
create function public.sp_ops_media(p_from date, p_to date, p_family uuid, p_offset int) returns jsonb
language sql stable security definer set search_path = ''
as $$
  with m as (
    select x.id, x.family_id, x.kind, x.bytes, x.width, x.height, x.duration_sec, x.status, x.created_at,
      p.role as by_role, mb.display_name as by_name
    from public.media x
      left join public.parents p on p.user_id = x.uploaded_by_parent
      left join public.members mb on mb.id = x.uploaded_by_member
    where x.status in ('ready', 'uploading') and (p_family is null or x.family_id = p_family)
      and x.created_at >= p_from::timestamp at time zone 'Asia/Seoul' and x.created_at < (p_to + 1)::timestamp at time zone 'Asia/Seoul'
      and p_from <= p_to and p_to - p_from < 400
  )
  select jsonb_build_object(
    'total', (select count(*) from m),
    'ready', (select count(*) from m where status = 'ready'),
    'bytes', (select coalesce(sum(bytes), 0) from m where status = 'ready'),
    'rows', coalesce((select jsonb_agg(to_jsonb(r) order by r.created_at desc, r.id) from (
      select * from m order by created_at desc, id offset greatest(p_offset, 0) limit 50) r), '[]'))
$$;
revoke all on function public.sp_ops_media(date, date, uuid, int) from public, anon, authenticated;
grant execute on function public.sp_ops_media(date, date, uuid, int) to service_role;
