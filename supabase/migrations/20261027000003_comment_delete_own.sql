-- 한마디 지우기는 쓴 사람만(사용자 2026-10-27). 엄빠도 가족이 쓴 한마디는 못 지운다(전엔 가족방 사진의 한마디를 다 지울 수 있었음)
create or replace function public.sp_delete_comment(p_comment_id uuid) returns void
language plpgsql security definer set search_path = ''
as $$
begin
  update public.comments c set deleted_at = now()
    where c.id = p_comment_id and c.deleted_at is null
      and (c.member_id in (select public.sp_device_members()) or c.parent_user_id = auth.uid());
  if not found then raise exception 'not_allowed' using errcode = '42501'; end if;
end $$;

-- 한마디 목록에 지울 때 쓸 id를 더한다(돌려주는 열이 바뀌어 지우고 다시 만듦. 조건은 20261027000002와 같음)
drop function public.sp_media_comments(uuid);
create function public.sp_media_comments(p_media_id uuid)
returns table (id uuid, name text, body text, created_at timestamptz, mine boolean)
language sql stable security definer set search_path = ''
as $$
  select c.id, coalesce(m.display_name, p.display_name), c.body, c.created_at,
         coalesce(c.member_id in (select public.sp_device_members()) or c.parent_user_id = auth.uid(), false)
  from public.comments c
  left join public.members m on m.id = c.member_id and m.status = 'active'
  left join public.parents p on p.user_id = c.parent_user_id
  where c.media_id = p_media_id and c.deleted_at is null
    and (m.id is not null or p.user_id is not null)
    and public.sp_can_view_media(p_media_id)
    and exists (select 1 from public.media x where x.id = p_media_id
                and (public.sp_device_active(x.family_id) or x.family_id = public.sp_parent_family()))
  order by c.created_at desc
  limit 100
$$;
revoke execute on function public.sp_media_comments(uuid) from public, anon, authenticated;
grant execute on function public.sp_media_comments(uuid) to authenticated;
