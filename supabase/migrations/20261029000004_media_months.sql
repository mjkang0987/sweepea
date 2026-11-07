-- 사진 크기 '월별'(98a, 사용자 2026-10-29 "줄여 보는 건 대표 사진 몇 장"): 달마다 사진 수와 대표 사진.
-- 볼 수 있는 사진만(sp_can_view_media, 엄빠·가족 같은 판정), 다 올라간 것만, 서울 달. 가족방·아이로 거를 수 있다.
-- 대표: 반응(하트 등)·한마디가 많은 순 → 같으면 최근. 반응·한마디는 sp_reaction_counts와 같은 규칙(활동 중인 가족·엄빠, 지운 한마디 빼고)
-- shortcut: 사진마다 점수를 세므로 아주 큰 가족방이면 느려질 수 있음 → 그때 점수를 미리 모아 두는 칸으로

create function public.sp_media_months(p_family uuid default null, p_child uuid default null, p_reps int default 3)
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
           filter (where r.rn <= least(greatest(p_reps, 1), 4))
  from r
  group by r.ym
  order by r.ym desc
$$;

revoke execute on function public.sp_media_months(uuid, uuid, int) from public, anon;
grant execute on function public.sp_media_months(uuid, uuid, int) to authenticated;
