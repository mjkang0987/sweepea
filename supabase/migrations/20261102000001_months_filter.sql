-- 달·해 카드도 앨범 거르기를 따름(132, 코드리뷰 "월별 카드가 그룹 거르기를 무시"): 사진/영상(p_kind)·그룹(p_group) 조건을 받는 sp_media_months_f.
-- 본문은 sp_media_months(20261101000003) 그대로에 조건 두 줄. 이름이 달라 기존 함수는 그대로 두고(받는 값이 늘어 같은 이름이면 PostgREST가 고르지 못함), 지우는 문 없음

create function public.sp_media_months_f(p_family uuid default null, p_child uuid default null, p_reps int default 3, p_kind text default null, p_group uuid default null)
returns table (ym text, n int, reps jsonb)
language sql stable security definer set search_path = ''
as $$
  with v as (
    select x.id, x.kind, x.thumb_key, x.width, x.height, x.taken_at,
           to_char(x.taken_at at time zone 'Asia/Seoul', 'YYYY-MM') as ym
    from public.media x
    where x.status = 'ready'
      -- 먼저 내 가족방(엄빠)·들어간 가족방(가족 기기)으로 좁힌다: 서비스 전체 사진마다 판정 함수를 부르지 않게(리뷰 2026-10-29)
      and x.family_id in (select public.sp_parent_family()
                          union select m.family_id from public.members m where m.id in (select public.sp_device_members()))
      and (p_family is null or x.family_id = p_family)
      and (p_child is null or exists (select 1 from public.media_children c where c.media_id = x.id and c.child_id = p_child))
      and (p_kind is null or x.kind = p_kind)
      and (p_group is null or exists (select 1 from public.media_groups g where g.media_id = x.id and g.group_id = p_group))
      and public.sp_can_view_media(x.id)
  ),
  s as (
    select v.*,
      (select count(*) from public.reactions r left join public.members m on m.id = r.member_id
        where r.media_id = v.id and (m.status = 'active' or r.parent_user_id is not null))
      + (select count(*) from public.comments c left join public.members m on m.id = c.member_id
        where c.media_id = v.id and c.deleted_at is null and (m.status = 'active' or c.parent_user_id is not null)) as score
    from v
  ),
  r as (
    select s.*, row_number() over (partition by s.ym order by s.score desc, s.taken_at desc, s.id desc) as rn,
           count(*) over (partition by s.ym) as cnt
    from s
  )
  select r.ym, max(r.cnt)::int,
         jsonb_agg(jsonb_build_object('id', r.id, 'kind', r.kind, 'thumb_key', r.thumb_key, 'width', r.width, 'height', r.height) order by r.rn)
           filter (where r.rn <= least(greatest(p_reps, 1), 5))
  from r
  group by r.ym
  order by r.ym desc
$$;

revoke execute on function public.sp_media_months_f(uuid, uuid, int, text, uuid) from public, anon;
grant execute on function public.sp_media_months_f(uuid, uuid, int, text, uuid) to authenticated;
