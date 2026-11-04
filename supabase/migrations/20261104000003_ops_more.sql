-- 운영 현황에 더 볼 것(169, 사용자 2026-11-04 "실제 확인 필요한 데이터 추가"): 유료 가족방 수, 가입하고 멈춘 곳(기간 안 가입 계정이
-- 처음 설정·첫 사진·가족 들어옴까지 왔나 + 지금 가족방 없는 계정), 예약 정리 작업 밀림, 살펴볼 것에 올리다 멈춘 사진.
-- sp_ops_summary 본문(20261104000001)에 더함. 이름·받는 값·권한 같음(DROP 없음)

create or replace function public.sp_ops_summary(p_from date, p_to date) returns jsonb
language plpgsql stable security definer set search_path = ''
as $$
declare
  v_len int := p_to - p_from + 1;
  v_pf date := p_from - (p_to - p_from + 1);
  lo timestamptz := p_from::timestamp at time zone 'Asia/Seoul';
  hi timestamptz := (p_to + 1)::timestamp at time zone 'Asia/Seoul';
  plo timestamptz := (p_from - (p_to - p_from + 1))::timestamp at time zone 'Asia/Seoul';
  v jsonb;
begin
  if p_from > p_to or v_len > 400 then raise exception 'bad_range' using errcode = '22023'; end if;
  with dv as materialized (select * from public.sp_ops_devices()),
  vis as materialized (select day, kind, visitor, count, day >= p_from as cur from public.visits where day between v_pf and p_to),
  vday as (select day, sum(count) filter (where kind = 'parent') as parent, sum(count) filter (where kind = 'device') as device from vis where cur group by day),
  lastv as (select family_id, max(day) as last from public.visits where kind = 'device' group by family_id)
  select jsonb_build_object(
    'now', (select jsonb_build_object(
      'families', (select count(*) from public.families),
      'parents', (select count(*) from public.parents where family_id is not null and removed_at is null),
      'devices', count(*) filter (where st is not null),
      'devices_active', count(*) filter (where st = 'active'),
      'devices_pending', count(*) filter (where st = 'pending'),
      'media', (select count(*) from public.media where status = 'ready'),
      'bytes', (select coalesce(sum(storage_used_bytes), 0) from public.families),
      -- 유료 = 스토어 구독이 살아 있는 가족방(앱의 plan_until과 같은 기준, families.plan 값과는 따로)
      'paid', (select count(distinct family_id) from public.entitlements where expires_at > now())) from dv),
    -- 가입하고 멈춘 곳: 이 기간에 가입한 엄빠 계정(익명 기기·지운 계정 제외)이 지금 어디까지 왔나
    'signup', (select jsonb_build_object(
      'accounts', count(*),
      'setup', count(*) filter (where fam is not null),
      'uploaded', count(*) filter (where fam is not null and exists (select 1 from public.media m where m.family_id = fam and m.status = 'ready')),
      -- 단계가 차례로 줄게 가족이 들어옴은 첫 사진까지 온 것 중에서만
      'joined', count(*) filter (where fam is not null and exists (select 1 from public.media m where m.family_id = fam and m.status = 'ready')
        and exists (select 1 from dv where dv.family_id = fam and dv.st = 'active')),
      'no_family', (select count(*) from auth.users u where not u.is_anonymous and u.deleted_at is null
        and not exists (select 1 from public.parents p where p.user_id = u.id and p.family_id is not null and p.removed_at is null)))
      from (select u.id, (select p.family_id from public.parents p where p.user_id = u.id and p.removed_at is null limit 1) as fam
        from auth.users u where not u.is_anonymous and u.deleted_at is null and u.created_at >= lo and u.created_at < hi) su),
    -- 예약 정리 작업(하루 한 번, 03:17)이 밀렸는지: 이틀 넘게 남은 것
    'jobs', jsonb_build_object(
      'purge_late', (select count(*) from public.families where delete_after < now() - interval '2 days'),
      'r2_late', (select count(*) from public.r2_cleanup where queued_at < now() - interval '2 days'),
      -- 하루 넘은 것만 지우고 하루 한 번 돌아서 정상이어도 이틀 가까이 남는다 → 사흘
      'uploads_late', (select count(*) from public.media where status = 'uploading' and created_at < now() - interval '3 days')
    ),
    'visits', (select jsonb_build_object(
      'people', count(distinct visitor) filter (where cur and kind in ('parent', 'device')),
      'people_parent', count(distinct visitor) filter (where cur and kind = 'parent'),
      'people_device', count(distinct visitor) filter (where cur and kind = 'device'),
      'count', coalesce(sum(count) filter (where cur and kind in ('parent', 'device')), 0),
      'prev_people', count(distinct visitor) filter (where not cur and kind in ('parent', 'device')),
      'prev_count', coalesce(sum(count) filter (where not cur and kind in ('parent', 'device')), 0),
      'days', (select jsonb_agg(jsonb_build_object('day', g.d, 'parent', coalesce(vday.parent, 0), 'device', coalesce(vday.device, 0)) order by g.d)
        from (select x::date as d from generate_series(p_from::timestamp, p_to::timestamp, interval '1 day') x) g left join vday on vday.day = g.d)) from vis),
    'new', jsonb_build_object(
      'families', (select count(*) from public.families where created_at >= lo and created_at < hi),
      'prev_families', (select count(*) from public.families where created_at >= plo and created_at < lo),
      'devices', (select count(*) from dv where st = 'active' and created_at >= lo and created_at < hi),
      'prev_devices', (select count(*) from dv where st = 'active' and created_at >= plo and created_at < lo),
      'media', (select count(*) from public.media where status = 'ready' and created_at >= lo and created_at < hi),
      'prev_media', (select count(*) from public.media where status = 'ready' and created_at >= plo and created_at < lo)
    ),
    'seen', jsonb_build_object(
      'active', (select count(*) from dv where st = 'active'),
      'visited', (select count(*) from dv where st = 'active' and dv.id in (select visitor from vis where cur and kind = 'device')),
      'reactions', (select count(*) from public.reactions where created_at >= lo and created_at < hi),
      'prev_reactions', (select count(*) from public.reactions where created_at >= plo and created_at < lo),
      'comments', (select count(*) from public.comments where deleted_at is null and created_at >= lo and created_at < hi),
      'prev_comments', (select count(*) from public.comments where deleted_at is null and created_at >= plo and created_at < lo)
    ),
    'entry', jsonb_build_object(
      'link', (select coalesce(sum(count), 0) from vis where cur and kind = 'link'),
      'link_pw', (select coalesce(sum(count), 0) from vis where cur and kind = 'link_pw'),
      'requested', (select count(*) from public.devices where created_at >= lo and created_at < hi),
      'approved', (select count(*) from dv where st = 'active' and created_at >= lo and created_at < hi),
      'failures', (select count(*) from public.entry_failures where at >= lo and at < hi),
      'expired', (select count(*) from public.members where status = 'pending' and pending_until >= lo and pending_until < least(hi, now()))
    ),
    'install_help', (select count(*) from public.members where install_help_at >= lo and install_help_at < hi),
    'providers', (select coalesce(jsonb_object_agg(pr, n), '{}') from (
        select coalesce(u.raw_app_meta_data ->> 'provider', 'email') as pr, count(*) as n
        from public.parents p join auth.users u on u.id = p.user_id
        where p.family_id is not null and p.removed_at is null group by 1) t),
    -- 살펴볼 것(지금 기준): 가족방 번호와 짧은 사유 숫자만. 종류마다 50곳까지(나머지는 목록에서 정렬해 찾음)
    'checks', jsonb_build_object(
      -- 대기는 현황의 대기 수와 같은 뜻(구성원 대기 + 기기만 대기), 2일 넘은 것
      'pending', (select coalesce(jsonb_agg(jsonb_build_object('family_id', family_id, 'n', n, 'since', since) order by since, family_id), '[]') from (
          select family_id, count(*) as n, min(created_at) as since from dv
          where st = 'pending' and created_at < now() - interval '2 days' group by family_id order by since, family_id limit 50) t),
      'full', (select coalesce(jsonb_agg(jsonb_build_object('family_id', id, 'bytes', bytes, 'quota', quota) order by bytes desc, id), '[]') from (
          select id, storage_used_bytes as bytes, public.sp_ops_quota(plan) as quota from public.families
          where storage_used_bytes >= 0.8 * public.sp_ops_quota(plan) order by storage_used_bytes desc, id limit 50) t),
      'quiet', (select coalesce(jsonb_agg(jsonb_build_object('family_id', id, 'last', last) order by last nulls first, id), '[]') from (
          select f.id, lastv.last from public.families f left join lastv on lastv.family_id = f.id
          where f.delete_after is null and f.created_at < now() - interval '7 days'
            and f.id in (select family_id from dv where st = 'active')
            and (lastv.last is null or lastv.last <= public.sp_seoul_today() - 7)
          order by lastv.last nulls first, f.id limit 50) t),
      -- 올리다 멈춘 사진(1시간 넘게 uploading): 올리기 실패 신호. 하루 지나면 정리 작업이 지운다
      'stuck', (select coalesce(jsonb_agg(jsonb_build_object('family_id', family_id, 'n', n, 'since', since) order by since, family_id), '[]') from (
          select family_id, count(*) as n, min(created_at) as since from public.media
          where status = 'uploading' and created_at < now() - interval '1 hour' group by family_id order by since, family_id limit 50) t),
      'closing', (select coalesce(jsonb_agg(jsonb_build_object('family_id', id, 'at', delete_after) order by delete_after, id), '[]') from (
          select id, delete_after from public.families where delete_after is not null order by delete_after, id limit 50) t)
    )
  ) into v;
  return v;
end $$;
