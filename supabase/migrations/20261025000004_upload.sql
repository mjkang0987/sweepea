-- 사진 올리기: 행 만들기(사용자) → 파일은 Worker가 R2에 넣음 → 완료 처리(서버 전용)

-- 사진 행 + 공개 그룹·아이 태그를 한 번에. 올린 사람은 호출자로 정한다(부모 또는 올리기 권한 가족)
-- p_group_ids가 null이면 '기본 포함' 그룹 전부
create function public.sp_create_media(
  p_family_id uuid, p_kind text, p_taken_at timestamptz, p_taken_at_source text,
  p_width int default null, p_height int default null, p_duration_sec numeric default null,
  p_group_ids uuid[] default null, p_child_ids uuid[] default '{}'
) returns uuid
language plpgsql security definer set search_path = ''
as $$
declare
  v_parent boolean := p_family_id = public.sp_parent_family();
  v_member uuid := public.sp_device_member(p_family_id);
  v_groups uuid[];
  v_id uuid;
begin
  if not public.sp_can_upload(p_family_id) then raise exception 'not_allowed' using errcode = '42501'; end if;
  v_groups := coalesce(p_group_ids,
    array(select g.id from public.groups g where g.family_id = p_family_id and g.include_by_default));
  if coalesce(array_length(v_groups, 1), 0) = 0
     or exists (select 1 from unnest(v_groups) x where x not in (select id from public.groups where family_id = p_family_id))
     or exists (select 1 from unnest(coalesce(p_child_ids, '{}')) x where x not in (select id from public.children where family_id = p_family_id))
  then
    raise exception 'bad_request' using errcode = '22023';
  end if;
  insert into public.media (family_id, uploaded_by_parent, uploaded_by_member, kind, taken_at, taken_at_source, width, height, duration_sec)
    values (p_family_id, case when v_parent then auth.uid() end, case when not v_parent then v_member end,
            p_kind, p_taken_at, p_taken_at_source, p_width, p_height, p_duration_sec)
    returning id into v_id;
  insert into public.media_groups (family_id, media_id, group_id) select p_family_id, v_id, x from unnest(v_groups) x;
  insert into public.media_children (family_id, media_id, child_id) select p_family_id, v_id, x from unnest(coalesce(p_child_ids, '{}')) x;
  return v_id;
end $$;

-- 파일을 넣어도 되는 사진인가: 올리는 중이고, 호출자가 올린 사람(올리기 권한이 아직 있음)일 때 가족방 id. 아니면 null
create function public.sp_upload_target(p_media_id uuid) returns jsonb
language sql stable security definer set search_path = ''
as $$
  select jsonb_build_object('family_id', x.family_id, 'kind', x.kind)
  from public.media x
  where x.id = p_media_id and x.status = 'uploading'
    and public.sp_can_upload(x.family_id)
    and (x.uploaded_by_parent = auth.uid() or x.uploaded_by_member = public.sp_device_member(x.family_id))
$$;

-- 완료 처리: 서버(service_role)만. 키·용량은 Worker가 R2에서 직접 잰 값
create function public.sp_finish_upload(p_media_id uuid, p_view_key text, p_thumb_key text, p_poster_key text, p_bytes bigint)
returns boolean
language plpgsql security definer set search_path = ''
as $$
declare v_family uuid;
begin
  update public.media
    set status = 'ready', view_key = p_view_key, thumb_key = p_thumb_key, poster_key = p_poster_key, bytes = p_bytes
    where id = p_media_id and status = 'uploading' and p_bytes >= 0
    returning family_id into v_family;
  if v_family is null then return false; end if;
  update public.families set storage_used_bytes = storage_used_bytes + p_bytes where id = v_family;
  return true;
end $$;

revoke execute on function public.sp_create_media(uuid, text, timestamptz, text, int, int, numeric, uuid[], uuid[]),
  public.sp_upload_target(uuid), public.sp_finish_upload(uuid, text, text, text, bigint) from public, anon, authenticated;
grant execute on function public.sp_create_media(uuid, text, timestamptz, text, int, int, numeric, uuid[], uuid[]),
  public.sp_upload_target(uuid) to authenticated;
grant execute on function public.sp_finish_upload(uuid, text, text, text, bigint) to service_role;
