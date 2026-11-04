-- 운영자 화면 1단계(164): 방문 기록 + 운영 숫자 함수.
-- 방문: 30분 넘게 쉬었다 다시 연 것 한 번(서버가 30분 쿠키로 거름). 하루 한 줄(서울 날짜·가족방·누구·횟수), 주소·기기·IP는 안 남김.
-- 보관은 가족방이 있는 동안(사용자 2026-11-04), 가족방이 지워지면 같이 지워짐(cascade).
-- 운영 함수(sp_ops_*)는 서버(service_role)만. 숫자·날짜·번호만 돌려주고 이름·사진 키·한마디 내용은 꺼내지 않는다

create table public.visits (
  family_id uuid not null references public.families (id) on delete cascade,
  -- parent: 엄빠 user_id, device: devices.id, link·link_pw: shares.id(입장 전이라 사람을 모름)
  kind text not null check (kind in ('parent', 'device', 'link', 'link_pw')),
  visitor uuid not null,
  day date not null,
  count int not null default 1 check (count > 0),
  primary key (family_id, kind, visitor, day)
);
create index visits_day on public.visits (day);
alter table public.visits enable row level security;
revoke all on public.visits from anon, authenticated;

-- 서울 오늘
create function public.sp_seoul_today() returns date
language sql stable set search_path = ''
as $$ select (now() at time zone 'Asia/Seoul')::date $$;

-- 엄빠·가족 기기 본인이 부른다(자기 토큰). 엄빠면 자기 가족방에, 기기면 들어간(승인·대기) 가족방마다 한 번씩
create function public.sp_note_visit() returns void
language plpgsql security definer set search_path = ''
as $$
declare v_day date := public.sp_seoul_today();
begin
  insert into public.visits (family_id, kind, visitor, day)
    select p.family_id, 'parent', p.user_id, v_day from public.parents p
    where p.user_id = auth.uid() and p.family_id is not null and p.removed_at is null
  on conflict (family_id, kind, visitor, day) do update set count = public.visits.count + 1;
  -- 기기는 승인·기한 안 대기만(sp_ops_devices와 같은 뜻, 기한 지난 대기·내보냄은 안 셈)
  insert into public.visits (family_id, kind, visitor, day)
    select d.family_id, 'device', d.id, v_day from public.devices d left join public.members m on m.id = d.member_id
    where d.auth_user_id = auth.uid()
      and (d.status = 'pending' or (d.status = 'active' and (m.status = 'active' or (m.status = 'pending' and m.pending_until > now()))))
  on conflict (family_id, kind, visitor, day) do update set count = public.visits.count + 1;
end $$;
revoke all on function public.sp_note_visit() from public, anon;
grant execute on function public.sp_note_visit() to authenticated;

-- 가족 링크(/i/코드)를 연 것. 아직 사용자가 없어(익명 사용자는 비밀번호 낼 때 만듦) 서버가 부른다. p_step: link(누구세요)·link_pw(비밀번호)
create function public.sp_note_link_visit(p_code text, p_step text) returns void
language sql security definer set search_path = ''
as $$
  insert into public.visits (family_id, kind, visitor, day)
    select s.family_id, p_step, s.id, public.sp_seoul_today() from public.shares s
    where s.code = p_code and s.revoked_at is null
  on conflict (family_id, kind, visitor, day) do update set count = public.visits.count + 1
$$;
revoke all on function public.sp_note_link_visit(text, text) from public, anon, authenticated;
grant execute on function public.sp_note_link_visit(text, text) to service_role;

-- 무료 한도(sp_finish_upload와 같은 5GB)
create function public.sp_ops_quota(p_plan text) returns bigint
language sql immutable set search_path = ''
as $$ select case when p_plan = 'free' then 5368709120 else null end $$;

-- 가족 기기의 실제 상태. 새 이름으로 들어온 기기는 승인 전에도 devices.status가 active이고 구성원이 pending이라(sp_enter),
-- 승인 = 기기 active + 구성원 active, 대기 = 기기 pending(구성원 없이 기다림) 또는 구성원 pending이고 기한 전(엄빠 첫 화면 waiting과 같은 뜻).
-- 기한 지난 대기·내 가족 아님·내보냄은 null(어디에도 안 셈)
create function public.sp_ops_devices() returns table (id uuid, family_id uuid, created_at timestamptz, st text)
language sql stable security definer set search_path = ''
as $$
  select d.id, d.family_id, d.created_at,
    case
      when d.status = 'active' and m.status = 'active' then 'active'
      when d.status = 'pending' or (d.status = 'active' and m.status = 'pending' and m.pending_until > now()) then 'pending'
    end
  from public.devices d left join public.members m on m.id = d.member_id
$$;

-- 현황: 지금 전체 + 고른 기간(서울 날짜, 끝 포함) + 바로 앞 같은 길이 기간.
-- 가족방·날짜마다 따로 세면 가족방 수천 곳에서 수십 초가 걸려(리뷰 2회차 실측) 표마다 한 번씩 묶어 센 뒤 붙인다
create function public.sp_ops_summary(p_from date, p_to date) returns jsonb
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
      'bytes', (select coalesce(sum(storage_used_bytes), 0) from public.families)) from dv),
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
      'pending', (select coalesce(jsonb_agg(jsonb_build_object('family_id', family_id, 'n', n, 'since', since) order by since), '[]') from (
          select family_id, count(*) as n, min(created_at) as since from dv
          where st = 'pending' and created_at < now() - interval '2 days' group by family_id order by since limit 50) t),
      'full', (select coalesce(jsonb_agg(jsonb_build_object('family_id', id, 'bytes', bytes, 'quota', quota) order by bytes desc), '[]') from (
          select id, storage_used_bytes as bytes, public.sp_ops_quota(plan) as quota from public.families
          where storage_used_bytes >= 0.8 * public.sp_ops_quota(plan) order by storage_used_bytes desc limit 50) t),
      'quiet', (select coalesce(jsonb_agg(jsonb_build_object('family_id', id, 'last', last) order by last nulls first, id), '[]') from (
          select f.id, lastv.last from public.families f left join lastv on lastv.family_id = f.id
          where f.delete_after is null and f.created_at < now() - interval '7 days'
            and f.id in (select family_id from dv where st = 'active')
            and (lastv.last is null or lastv.last <= public.sp_seoul_today() - 7)
          order by lastv.last nulls first, f.id limit 50) t),
      'closing', (select coalesce(jsonb_agg(jsonb_build_object('family_id', id, 'at', delete_after) order by delete_after), '[]') from (
          select id, delete_after from public.families where delete_after is not null order by delete_after limit 50) t)
    )
  ) into v;
  return v;
end $$;

-- 가족방 목록: 50곳씩. p_sort: created·media·bytes·visits·last_visit(모두 많은/최근 순). 표마다 가족방별로 한 번씩 묶어 센다
create function public.sp_ops_families(p_from date, p_to date, p_sort text, p_offset int) returns jsonb
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

-- 가족방 상세. 사람은 이름 없이 들어온 순서 번호, 그룹도 순서 번호. 그룹 인원은 승인 + 기한 안 대기(기기 수와 같은 뜻)
create function public.sp_ops_family(p_id uuid, p_from date, p_to date) returns jsonb
language sql stable security definer set search_path = ''
as $$
  with g as (select id, row_number() over (order by sort_order, created_at) as no from public.groups where family_id = p_id),
    days as (select x::date as d from generate_series(p_from::timestamp, p_to::timestamp, interval '1 day') x),
    v as (select kind, visitor, day, count from public.visits where family_id = p_id),
    pv as (select kind, visitor, coalesce(sum(count) filter (where day between p_from and p_to), 0) as n, max(day) as last from v group by kind, visitor),
    vday as (select day, sum(count) filter (where kind = 'parent') as parent, sum(count) filter (where kind = 'device') as device
      from v where day between p_from and p_to group by day),
    uday as (select (created_at at time zone 'Asia/Seoul')::date as day, count(*) as n from public.media
      where family_id = p_id and status = 'ready'
        and created_at >= p_from::timestamp at time zone 'Asia/Seoul' and created_at < (p_to + 1)::timestamp at time zone 'Asia/Seoul' group by 1)
  select jsonb_build_object(
    'id', f.id, 'created_at', f.created_at, 'delete_after', f.delete_after,
    'bytes', f.storage_used_bytes, 'quota', public.sp_ops_quota(f.plan),
    'children', (select count(*) from public.children c where c.family_id = f.id),
    'photos', (select count(*) from public.media m where m.family_id = f.id and m.status = 'ready' and m.kind = 'photo'),
    'videos', (select count(*) from public.media m where m.family_id = f.id and m.status = 'ready' and m.kind = 'video'),
    'last_upload', (select max(m.created_at) from public.media m where m.family_id = f.id and m.status = 'ready'),
    'shares', (select count(*) from public.shares s where s.family_id = f.id and s.revoked_at is null),
    'groups', (select coalesce(jsonb_agg(jsonb_build_object('no', g.no, 'members',
          (select count(*) from public.members m where m.group_id = g.id and (m.status = 'active' or (m.status = 'pending' and m.pending_until > now()))))
        order by g.no), '[]') from g),
    'parents', (select coalesce(jsonb_agg(jsonb_build_object('no', p.no, 'since', p.created_at, 'visits', coalesce(pv.n, 0), 'last', pv.last) order by p.no), '[]')
        from (select user_id, created_at, row_number() over (order by created_at) as no from public.parents where family_id = f.id and removed_at is null) p
        left join pv on pv.kind = 'parent' and pv.visitor = p.user_id),
    'devices', (select coalesce(jsonb_agg(jsonb_build_object('no', d.no, 'status', d.st, 'group', g.no, 'visits', coalesce(pv.n, 0), 'last', pv.last) order by d.no), '[]')
        from (select dv.id, dv.st, row_number() over (order by dv.created_at) as no, coalesce(m.group_id, dd.requested_group_id) as gid
            from public.sp_ops_devices() dv join public.devices dd on dd.id = dv.id left join public.members m on m.id = dd.member_id
            where dv.family_id = f.id and dv.st is not null) d
        left join g on g.id = d.gid left join pv on pv.kind = 'device' and pv.visitor = d.id),
    'uploads', (select jsonb_agg(jsonb_build_object('day', days.d, 'n', coalesce(uday.n, 0)) order by days.d) from days left join uday on uday.day = days.d),
    'visits', (select jsonb_agg(jsonb_build_object('day', days.d, 'parent', coalesce(vday.parent, 0), 'device', coalesce(vday.device, 0)) order by days.d)
        from days left join vday on vday.day = days.d),
    'entry', jsonb_build_object(
      'link', (select coalesce(sum(count), 0) from v where kind = 'link' and day between p_from and p_to),
      'failures', (select count(*) from public.entry_failures e where e.family_id = f.id
        and e.at >= p_from::timestamp at time zone 'Asia/Seoul' and e.at < (p_to + 1)::timestamp at time zone 'Asia/Seoul'))
  )
  from public.families f where f.id = p_id and p_from <= p_to and p_to - p_from < 400
$$;

revoke all on function public.sp_seoul_today(), public.sp_ops_quota(text) from public, anon, authenticated;
grant execute on function public.sp_seoul_today(), public.sp_ops_quota(text) to authenticated, service_role;
revoke all on function public.sp_ops_devices() from public, anon, authenticated;
grant execute on function public.sp_ops_devices() to service_role;
revoke all on function public.sp_ops_summary(date, date), public.sp_ops_families(date, date, text, int), public.sp_ops_family(uuid, date, date) from public, anon, authenticated;
grant execute on function public.sp_ops_summary(date, date), public.sp_ops_families(date, date, text, int), public.sp_ops_family(uuid, date, date) to service_role;

-- 엄빠가 나가거나(removed_at) 다른 가족방으로 옮기거나 지워지면, 예전 가족방에 남은 그 엄빠 방문 기록을 지운다(처리방침 3항)
create function public.sp_visits_parent_gone() returns trigger
language plpgsql security definer set search_path = ''
as $$
begin
  if tg_op = 'DELETE' then
    -- 다른 가족방 기록은 떠날 때(update) 이미 지웠다: 가족방을 붙여 표 전체를 훑지 않게
    delete from public.visits where kind = 'parent' and visitor = old.user_id and family_id = old.family_id;
    return old;
  end if;
  if old.family_id is not null and (new.removed_at is not null or new.family_id is distinct from old.family_id) then
    delete from public.visits where kind = 'parent' and visitor = old.user_id and family_id = old.family_id;
  end if;
  return new;
end $$;
revoke all on function public.sp_visits_parent_gone() from public, anon, authenticated;
create trigger parents_visits_gone after update of removed_at, family_id or delete on public.parents
  for each row execute function public.sp_visits_parent_gone();
