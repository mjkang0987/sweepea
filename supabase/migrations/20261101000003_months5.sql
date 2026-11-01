-- 월별 카드 대표 사진 5장(사용자 2026-11-01 "월별 보기 레이아웃 3장 말고 5장으로"): 한 달 대표 상한 4 → 5.
-- 20261029000004 그대로에 상한 숫자만(이름·받는 값·돌려주는 모양·권한 같음, 지우는 문 없음)

create or replace function public.sp_media_months(p_family uuid default null, p_child uuid default null, p_reps int default 3)
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

