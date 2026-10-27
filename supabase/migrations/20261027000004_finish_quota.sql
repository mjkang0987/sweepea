-- 큰 영상(최대 2GB) 나눠 올리기가 생겨, 올리기 시작 때만 보던 무료 5GB 한도를 완료 때도 본다.
-- 이미 쓴 용량 + 이번 크기가 5GB를 넘으면 완료하지 않는다(PT507 → HTTP 507). 같은 함수를 고쳐 쓴다(DROP 없음, 권한 그대로)
create or replace function public.sp_finish_upload(p_media_id uuid, p_view_key text, p_thumb_key text, p_poster_key text, p_bytes bigint)
returns boolean
language plpgsql security definer set search_path = ''
as $$
declare v_family uuid;
begin
  if exists (
    select 1 from public.media m join public.families f on f.id = m.family_id
    where m.id = p_media_id and m.status = 'uploading' and f.plan = 'free' and f.storage_used_bytes + greatest(p_bytes, 0) > 5368709120
  ) then
    raise exception 'storage_full' using errcode = 'PT507';
  end if;
  update public.media
    set status = 'ready', view_key = p_view_key, thumb_key = p_thumb_key, poster_key = p_poster_key, bytes = p_bytes
    where id = p_media_id and status = 'uploading' and p_bytes >= 0
    returning family_id into v_family;
  if v_family is null then return false; end if;
  update public.families set storage_used_bytes = storage_used_bytes + p_bytes where id = v_family;
  return true;
end $$;
