-- 부모 첫 화면: 내 가족방·역할·아이들. 아직 처음 설정 전이면 family_id null
create function public.sp_parent_home() returns jsonb
language sql stable security definer set search_path = ''
as $$
  select coalesce((
    select jsonb_build_object(
      'family_id', p.family_id,
      'role', p.role,
      -- 로그인 제공자(kakao·google 등). Supabase가 액세스 토큰 app_metadata에 넣는다
      'provider', auth.jwt() -> 'app_metadata' ->> 'provider',
      'text_size_mode', f.text_size_mode,
      'closing', f.delete_after is not null,
      'delete_after', f.delete_after,
      -- 스토어 구독이 끝나는 날(구독 중이면). 해지해도 이 날까지는 탈퇴를 막는다
      -- 마지막으로 최근 반응을 연 뒤 승인된 가족이 남긴 반응·한마디 수
      -- 목록(sp_parent_activity)과 같은 규칙: 최근 30일, 다 올라간 사진
      'new_activity', (select count(*) from public.reactions r join public.media x on x.id = r.media_id and x.status = 'ready'
                         join public.members m on m.id = r.member_id and m.status = 'active'
                         where x.family_id = f.id and r.created_at > greatest(p.activity_seen_at, now() - interval '30 days'))
                    + (select count(*) from public.comments c join public.media x on x.id = c.media_id and x.status = 'ready'
                         join public.members m on m.id = c.member_id and m.status = 'active'
                         where x.family_id = f.id and c.deleted_at is null and c.created_at > greatest(p.activity_seen_at, now() - interval '30 days')),
      -- 승인 기다리는 수(설정 탭 배지): 기한 안 지난 들어오기 신청 + 승인 기다리는 휴대폰
      'waiting', (select count(*) from public.members m where m.family_id = f.id and m.status = 'pending' and m.pending_until > now())
               + (select count(*) from public.devices d where d.family_id = f.id and d.status = 'pending'),
      'plan_until', (select max(e.expires_at) from public.entitlements e where e.family_id = f.id and e.expires_at > now()),
      'download_allowed', f.download_allowed,
      'storage_used_bytes', f.storage_used_bytes,
      'photo_count', (select count(*) from public.media x where x.family_id = f.id and x.status = 'ready' and x.kind = 'photo'),
      'video_count', (select count(*) from public.media x where x.family_id = f.id and x.status = 'ready' and x.kind = 'video'),
      'children', coalesce((
        select jsonb_agg(jsonb_build_object('id', c.id, 'name', c.name, 'birth_date', c.birth_date, 'show_health', c.show_health) order by c.sort_order, c.created_at)
        from public.children c where c.family_id = p.family_id
      ), '[]'::jsonb)
    )
    from public.parents p join public.families f on f.id = p.family_id
    -- 지울 날이 지난 가족방은 없는 것으로(처음 설정부터, sp_create_family가 먼저 지운다)
    where p.user_id = auth.uid() and (f.delete_after is null or f.delete_after > now())
  ), jsonb_build_object('family_id', null))
$$;

revoke execute on function public.sp_parent_home() from public, anon, authenticated;
grant execute on function public.sp_parent_home() to authenticated;
