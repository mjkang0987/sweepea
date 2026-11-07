-- 운영 계정 목록을 가족방별로 묶기(171, 사용자 2026-11-04 "계정 앨범별로 묶어야 할 것 같은데.. 대시보드에서"):
-- 같은 가족방 엄빠가 붙어 나오게 묶음(가족방) 단위로 정렬·50묶음씩. 가족방 없는 계정은 한 개씩 한 묶음, 늘 맨 뒤.
-- 정렬 값은 묶음 안 가장 큰 값(가입·마지막 로그인·마지막 방문은 최근, 방문은 합). 받는 모양은 그대로 + groups(묶음 수).
-- sp_ops_accounts 본문(20261104000002)을 바꿈. 이름·받는 값·권한 같음(DROP 없음)
create or replace function public.sp_ops_accounts(p_from date, p_to date, p_sort text, p_offset int) returns jsonb
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
  g as (
    select *, coalesce(family_id, id) as gk,
      max(created_at) over w as g_created, max(last_sign_in) over w as g_sign_in,
      sum(visits) over w as g_visits, max(last_visit) over w as g_last_visit
    from a window w as (partition by coalesce(family_id, id))
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
  select jsonb_build_object('total', (select count(*) from a), 'groups', (select count(distinct gk) from g), 'rows', coalesce((
    select jsonb_agg(to_jsonb(o) - 'gk' - 'grn' - 'g_created' - 'g_sign_in' - 'g_visits' - 'g_last_visit'
        order by o.grn, case o.role when 'mom' then 0 when 'dad' then 1 else 2 end, o.created_at, o.id) from o
    where o.grn > greatest(p_offset, 0) and o.grn <= greatest(p_offset, 0) + 50), '[]'))
$$;
