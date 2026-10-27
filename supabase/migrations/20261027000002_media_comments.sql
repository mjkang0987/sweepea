-- 크게 보기 한마디 목록(사용자 2026-10-27 "엄빠·가족 모두 보기"): 그 사진을 볼 수 있는 사람이면 승인된 가족과 엄빠가 쓴 한마디를 본다.
-- 표(comments)의 읽기 정책은 그대로(쓴 사람·엄빠만) 두고 이 함수로만 연다. 쓴 사람 id는 내보내지 않는다
create function public.sp_media_comments(p_media_id uuid)
returns table (name text, body text, created_at timestamptz, mine boolean)
language sql stable security definer set search_path = ''
as $$
  select coalesce(m.display_name, p.display_name), c.body, c.created_at,
         coalesce(c.member_id in (select public.sp_device_members()) or c.parent_user_id = auth.uid(), false)
  from public.comments c
  left join public.members m on m.id = c.member_id and m.status = 'active'
  left join public.parents p on p.user_id = c.parent_user_id
  where c.media_id = p_media_id and c.deleted_at is null
    and (m.id is not null or p.user_id is not null)
    and public.sp_can_view_media(p_media_id)
  order by c.created_at desc
  limit 100
$$;

revoke execute on function public.sp_media_comments(uuid) from public, anon, authenticated;
grant execute on function public.sp_media_comments(uuid) to authenticated;
