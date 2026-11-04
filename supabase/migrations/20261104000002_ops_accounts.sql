-- 운영자 화면(167, 사용자 2026-11-04): 계정 목록 + 가족방 상세에 지금 설정된 정보.
-- 목록은 여전히 번호만(가족방·계정 앞 8자리), 상세에 들어가면 그 가족방 설정(엄빠·아이·그룹·구성원 이름과 설정값)을 보여 준다.
-- 그룹 비밀번호(해시)·힌트, 사진·한마디 내용은 여전히 꺼내지 않는다. 서버(service_role)만

-- 엄빠 계정 목록: 익명(가족 기기) 계정은 빼고, 가족방이 없는(처음 설정 전·나간) 계정도 넣는다.
-- p_sort: created·last_sign_in·visits·last_visit(모두 최근/많은 순), 50개씩
create function public.sp_ops_accounts(p_from date, p_to date, p_sort text, p_offset int) returns jsonb
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
  o as (
    select *, row_number() over (order by
      case p_sort when 'visits' then visits else null end desc nulls last,
      case p_sort when 'last_sign_in' then last_sign_in else null end desc nulls last,
      case p_sort when 'last_visit' then last_visit else null end desc nulls last,
      created_at desc, id) as rn
    from a
  )
  select jsonb_build_object('total', (select count(*) from a), 'rows', coalesce((
    select jsonb_agg(to_jsonb(o) - 'rn' order by o.rn) from o
    where o.rn > greatest(p_offset, 0) and o.rn <= greatest(p_offset, 0) + 50), '[]'))
$$;
revoke all on function public.sp_ops_accounts(date, date, text, int) from public, anon, authenticated;
grant execute on function public.sp_ops_accounts(date, date, text, int) to service_role;

-- 가족방 상세(20261104000001 본문 + 설정 정보). 반환 모양만 넓어지고 이름·권한은 그대로(DROP 없음)
create or replace function public.sp_ops_family(p_id uuid, p_from date, p_to date) returns jsonb
language sql stable security definer set search_path = ''
as $$
  with g as (select id, name, include_by_default, row_number() over (order by sort_order, created_at) as no from public.groups where family_id = p_id),
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
    'plan', f.plan, 'download_allowed', f.download_allowed, 'groups_enabled', f.groups_enabled, 'text_size_mode', f.text_size_mode,
    'children', (select coalesce(jsonb_agg(jsonb_build_object('name', c.name, 'birth_date', c.birth_date, 'show_health', c.show_health)
        order by c.sort_order, c.created_at), '[]') from public.children c where c.family_id = f.id),
    'photos', (select count(*) from public.media m where m.family_id = f.id and m.status = 'ready' and m.kind = 'photo'),
    'videos', (select count(*) from public.media m where m.family_id = f.id and m.status = 'ready' and m.kind = 'video'),
    'last_upload', (select max(m.created_at) from public.media m where m.family_id = f.id and m.status = 'ready'),
    'shares', (select count(*) from public.shares s where s.family_id = f.id and s.revoked_at is null),
    'groups', (select coalesce(jsonb_agg(jsonb_build_object('no', g.no, 'name', g.name, 'include_by_default', g.include_by_default, 'members',
          (select count(*) from public.members m where m.group_id = g.id and (m.status = 'active' or (m.status = 'pending' and m.pending_until > now()))))
        order by g.no), '[]') from g),
    'parents', (select coalesce(jsonb_agg(jsonb_build_object('no', p.no, 'id', p.user_id, 'role', p.role, 'name', p.display_name,
          'provider', coalesce(u.raw_app_meta_data ->> 'provider', 'email'), 'since', p.created_at, 'visits', coalesce(pv.n, 0), 'last', pv.last) order by p.no), '[]')
        from (select user_id, role, display_name, created_at, row_number() over (order by created_at) as no from public.parents where family_id = f.id and removed_at is null) p
        join auth.users u on u.id = p.user_id
        left join pv on pv.kind = 'parent' and pv.visitor = p.user_id),
    'devices', (select coalesce(jsonb_agg(jsonb_build_object('no', d.no, 'status', d.st, 'group', g.no, 'group_name', g.name, 'name', d.name, 'can_upload', d.can_upload,
          'visits', coalesce(pv.n, 0), 'last', pv.last) order by d.no), '[]')
        from (select dv.id, dv.st, row_number() over (order by dv.created_at) as no, coalesce(m.group_id, dd.requested_group_id) as gid,
              coalesce(m.display_name, dd.requested_name) as name, dd.can_upload
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
