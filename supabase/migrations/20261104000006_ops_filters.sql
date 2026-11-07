-- 운영 목록 거르기(174, 사용자 2026-11-04 "리스트 나오면 필터좀 — 다 넣어 주고, 페이징 공통 디자인"):
-- 세 목록 함수에 p_filter jsonb를 받는 판을 더한다(같은 이름, 받는 값 하나 더 — 옛 판은 남지만 웹은 새 판만 부른다. DROP 없음).
-- 값은 웹이 아는 것만 넘긴다(가족방·계정의 모르는 값은 안 거름, 사진 종류·상태는 같은 값만). 서버(service_role)만
--   가족방: plan = free|paid(요금제 free가 아닌 것), state = pending(승인 대기 있음)|full(용량 80% 넘음)|closing(탈퇴 예정)
--   계정: provider = kakao|custom:naver|google|apple|email, fam = yes|no(지금 가족방 있음/없음)
--   사진: kind = photo|video, status = ready|uploading, by = parent|device(엄빠가 아닌 것 — 올린 사람이 지워진 것 포함)

create function public.sp_ops_families(p_from date, p_to date, p_sort text, p_offset int, p_filter jsonb) returns jsonb
language sql stable security definer set search_path = ''
as $$
  with dc as (select family_id, count(*) filter (where st = 'active') as active, count(*) filter (where st = 'pending') as pending
      from public.sp_ops_devices() group by family_id),
    pc as (select family_id, count(*) as n from public.parents where family_id is not null and removed_at is null group by family_id),
    mc as (select family_id, count(*) as n, max(created_at) as last from public.media where status = 'ready' group by family_id),
    vc as (select family_id, coalesce(sum(count) filter (where day between p_from and p_to), 0) as n, max(day) as last
      from public.visits where kind in ('parent', 'device') group by family_id),
  f as (
    select f.id, f.created_at, f.storage_used_bytes as bytes, f.delete_after, f.plan,
      coalesce(pc.n, 0) as parents, coalesce(dc.active, 0) as active, coalesce(dc.pending, 0) as pending,
      coalesce(mc.n, 0) as media, coalesce(vc.n, 0) as visits, mc.last as last_upload, vc.last as last_visit
    from public.families f
      left join dc on dc.family_id = f.id left join pc on pc.family_id = f.id
      left join mc on mc.family_id = f.id left join vc on vc.family_id = f.id
    where p_from <= p_to and p_to - p_from < 400
      and case p_filter ->> 'plan' when 'free' then f.plan = 'free' when 'paid' then f.plan <> 'free' else true end
      and case p_filter ->> 'state'
        when 'pending' then coalesce(dc.pending, 0) > 0
        when 'full' then f.storage_used_bytes >= 0.8 * public.sp_ops_quota(f.plan)
        when 'closing' then f.delete_after is not null
        else true end
  )
  , o as (
    select *, row_number() over (order by
      case p_sort when 'media' then media when 'bytes' then bytes when 'visits' then visits else null end desc nulls last,
      case p_sort when 'last_visit' then last_visit else null end desc nulls last,
      created_at desc, id) as rn
    from f
  )
  select jsonb_build_object('total', (select count(*) from f), 'rows', coalesce((
    select jsonb_agg(to_jsonb(o) - 'plan' - 'rn' || jsonb_build_object('quota', public.sp_ops_quota(o.plan)) order by o.rn)
    from o where o.rn > greatest(p_offset, 0) and o.rn <= greatest(p_offset, 0) + 50), '[]'))
$$;

create function public.sp_ops_accounts(p_from date, p_to date, p_sort text, p_offset int, p_filter jsonb) returns jsonb
language sql stable security definer set search_path = ''
as $$
  with vc as (select visitor, coalesce(sum(count) filter (where day between p_from and p_to), 0) as n, max(day) as last
      from public.visits where kind = 'parent' group by visitor),
  a as (
    select u.id, coalesce(u.raw_app_meta_data ->> 'provider', 'email') as provider, u.created_at, u.last_sign_in_at as last_sign_in,
      case when p.removed_at is null then p.family_id end as family_id, case when p.removed_at is null then p.role end as role,
      coalesce(vc.n, 0) as visits, vc.last as last_visit
    from auth.users u
      left join public.parents p on p.user_id = u.id
      left join vc on vc.visitor = u.id
    where not u.is_anonymous and u.deleted_at is null and p_from <= p_to and p_to - p_from < 400
  ),
  af as (
    select * from a
    where (p_filter ->> 'provider' is null or provider = p_filter ->> 'provider')
      and case p_filter ->> 'fam' when 'yes' then family_id is not null when 'no' then family_id is null else true end
  ),
  g as (
    select *, coalesce(family_id, id) as gk,
      max(created_at) over w as g_created, max(last_sign_in) over w as g_sign_in,
      sum(visits) over w as g_visits, max(last_visit) over w as g_last_visit
    from af window w as (partition by coalesce(family_id, id))
  ),
  o as (
    select *, dense_rank() over (order by
      family_id is null,
      case p_sort when 'visits' then g_visits else null end desc nulls last,
      case p_sort when 'last_sign_in' then g_sign_in else null end desc nulls last,
      case p_sort when 'last_visit' then g_last_visit else null end desc nulls last,
      g_created desc, gk) as grn
    from g
  )
  select jsonb_build_object('total', (select count(*) from af), 'groups', (select count(distinct gk) from g), 'rows', coalesce((
    select jsonb_agg(to_jsonb(o) - 'gk' - 'grn' - 'g_created' - 'g_sign_in' - 'g_visits' - 'g_last_visit'
        order by o.grn, case o.role when 'mom' then 0 when 'dad' then 1 else 2 end, o.created_at, o.id) from o
    where o.grn > greatest(p_offset, 0) and o.grn <= greatest(p_offset, 0) + 50), '[]'))
$$;

create function public.sp_ops_media(p_from date, p_to date, p_family uuid, p_offset int, p_filter jsonb) returns jsonb
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
      and (p_filter ->> 'kind' is null or x.kind = p_filter ->> 'kind')
      and (p_filter ->> 'status' is null or x.status = p_filter ->> 'status')
      -- 올린 사람이 지워져(엄빠 나감·구성원 지움) 둘 다 비면 가족 기기 쪽에 넣는다 → 엄빠 + 가족 기기 = 전체
      and case p_filter ->> 'by' when 'parent' then x.uploaded_by_parent is not null when 'device' then x.uploaded_by_parent is null else true end
  )
  select jsonb_build_object(
    'total', (select count(*) from m),
    'ready', (select count(*) from m where status = 'ready'),
    'bytes', (select coalesce(sum(bytes), 0) from m where status = 'ready'),
    'rows', coalesce((select jsonb_agg(to_jsonb(r) order by r.created_at desc, r.id) from (
      select * from m order by created_at desc, id offset greatest(p_offset, 0) limit 50) r), '[]'))
$$;

revoke all on function public.sp_ops_families(date, date, text, int, jsonb), public.sp_ops_accounts(date, date, text, int, jsonb),
  public.sp_ops_media(date, date, uuid, int, jsonb) from public, anon, authenticated;
grant execute on function public.sp_ops_families(date, date, text, int, jsonb), public.sp_ops_accounts(date, date, text, int, jsonb),
  public.sp_ops_media(date, date, uuid, int, jsonb) to service_role;
