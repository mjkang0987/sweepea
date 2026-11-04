-- 운영 사진 목록을 가족방별 요약으로(176, 사용자 2026-11-04 "사진은 그냥 다 보이는 거여? 가족방별로 묶어 주면" → '가족방 요약 표 → 눌러서 사진' 고름).
-- 고른 기간에 올린 것을 가족방마다 한 줄: 사진 수·영상 수·크기(다 올라간 것)·마지막 올림·멈춤(1시간 넘게 올리는 중). 최근에 올린 가족방부터 50곳씩.
-- 거르기(p_filter: kind·status·by)는 sp_ops_media(000006)와 같은 뜻. 사진 자체·파일 주소는 없음. 서버(service_role)만
create function public.sp_ops_media_families(p_from date, p_to date, p_offset int, p_filter jsonb) returns jsonb
language sql stable security definer set search_path = ''
as $$
  with m as (
    select x.family_id, x.kind, x.bytes, x.status, x.created_at
    from public.media x
    where x.status in ('ready', 'uploading')
      and x.created_at >= p_from::timestamp at time zone 'Asia/Seoul' and x.created_at < (p_to + 1)::timestamp at time zone 'Asia/Seoul'
      and p_from <= p_to and p_to - p_from < 400
      and (p_filter ->> 'kind' is null or x.kind = p_filter ->> 'kind')
      and (p_filter ->> 'status' is null or x.status = p_filter ->> 'status')
      and case p_filter ->> 'by' when 'parent' then x.uploaded_by_parent is not null when 'device' then x.uploaded_by_parent is null else true end
  ),
  f as (
    select family_id,
      count(*) filter (where kind = 'photo') as photos, count(*) filter (where kind = 'video') as videos,
      coalesce(sum(bytes) filter (where status = 'ready'), 0) as bytes, max(created_at) as last,
      count(*) filter (where status = 'uploading' and created_at < now() - interval '1 hour') as stuck
    from m group by family_id
  )
  select jsonb_build_object(
    'total', (select count(*) from f),
    'items', (select count(*) from m),
    'bytes', (select coalesce(sum(bytes), 0) from f),
    'rows', coalesce((select jsonb_agg(to_jsonb(r) order by r.last desc, r.family_id) from (
      select * from f order by last desc, family_id offset greatest(p_offset, 0) limit 50) r), '[]'))
$$;
revoke all on function public.sp_ops_media_families(date, date, int, jsonb) from public, anon, authenticated;
grant execute on function public.sp_ops_media_families(date, date, int, jsonb) to service_role;
