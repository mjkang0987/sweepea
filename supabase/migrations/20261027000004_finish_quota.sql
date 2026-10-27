-- 큰 영상(최대 2GB) 나눠 올리기가 생겨, 올리기 시작 때만 보던 무료 5GB 한도를 완료 때도 본다.
-- 이미 쓴 용량 + 이번 크기가 5GB를 넘으면 완료하지 않는다(PT507 → HTTP 507). 확인과 더하기를 한 문장으로(동시에 끝나도 행 잠금으로 넘지 않게),
-- 넘으면 예외로 위의 media 바꾸기도 함께 되돌린다. 같은 함수를 고쳐 쓴다(DROP 없음, 권한 그대로)
create or replace function public.sp_finish_upload(p_media_id uuid, p_view_key text, p_thumb_key text, p_poster_key text, p_bytes bigint)
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
  update public.families set storage_used_bytes = storage_used_bytes + p_bytes
    where id = v_family and (plan <> 'free' or storage_used_bytes + p_bytes <= 5368709120);
  if not found then
    raise exception 'storage_full' using errcode = 'PT507';
  end if;
  return true;
end $$;
