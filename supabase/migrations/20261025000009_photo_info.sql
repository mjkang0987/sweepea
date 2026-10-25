-- 부모 사진 정보: 찍은 날·아이·보여줄 그룹을 한 번에 고치기, 사진 지우기

-- 부모 또는 올린 가족(sp_can_edit_media). 아이·그룹은 같은 가족방 것만, 그룹은 하나 이상(아무도 못 보는 사진 방지)
create function public.sp_update_media(p_media_id uuid, p_taken_at timestamptz, p_child_ids uuid[], p_group_ids uuid[])
returns void
language plpgsql security definer set search_path = ''
as $$
declare v_family uuid;
begin
  select family_id into v_family from public.media where id = p_media_id and status = 'ready';
  if v_family is null or not public.sp_can_edit_media(p_media_id) then
    raise exception 'not_allowed' using errcode = '42501';
  end if;
  if coalesce(array_length(p_group_ids, 1), 0) = 0
     or exists (select 1 from unnest(p_group_ids) x where x not in (select id from public.groups where family_id = v_family))
     or exists (select 1 from unnest(coalesce(p_child_ids, '{}')) x where x not in (select id from public.children where family_id = v_family))
  then
    raise exception 'bad_request' using errcode = '22023';
  end if;
  update public.media
    set taken_at = p_taken_at,
        taken_at_source = case when taken_at = p_taken_at then taken_at_source else 'manual' end
    where id = p_media_id;
  delete from public.media_groups where media_id = p_media_id and group_id <> all (p_group_ids);
  insert into public.media_groups (family_id, media_id, group_id)
    select v_family, p_media_id, g from unnest(p_group_ids) g on conflict do nothing;
  delete from public.media_children where media_id = p_media_id and child_id <> all (coalesce(p_child_ids, '{}'));
  insert into public.media_children (family_id, media_id, child_id)
    select v_family, p_media_id, c from unnest(coalesce(p_child_ids, '{}')) c on conflict do nothing;
end $$;

-- 부모만. 저장 용량에서 빼고, R2 사진 폴더는 정리 대기열에 넣고 행을 지운다(반응·한마디·연결도 같이)
create function public.sp_delete_media(p_media_id uuid) returns void
language plpgsql security definer set search_path = ''
as $$
declare m public.media;
begin
  select * into m from public.media where id = p_media_id and family_id = public.sp_parent_family() for update;
  if not found then raise exception 'not_allowed' using errcode = '42501'; end if;
  insert into public.r2_cleanup (prefix) values (m.family_id::text || '/' || m.id::text || '/') on conflict do nothing;
  if m.status = 'ready' then
    update public.families set storage_used_bytes = greatest(0, storage_used_bytes - m.bytes) where id = m.family_id;
  end if;
  delete from public.media where id = p_media_id;
end $$;

revoke execute on function public.sp_update_media(uuid, timestamptz, uuid[], uuid[]), public.sp_delete_media(uuid)
  from public, anon, authenticated;
grant execute on function public.sp_update_media(uuid, timestamptz, uuid[], uuid[]), public.sp_delete_media(uuid) to authenticated;
