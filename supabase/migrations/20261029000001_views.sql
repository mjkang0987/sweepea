-- 보신 기록(95, 사용자 2026-10-29 "이름만"): 가족이 사진을 본 걸 엄마아빠 크게 보기에 "외할머니가 봤어요"로.
-- 한 사람 한 사진 한 줄(처음 본 때만). 횟수·시간은 엄마아빠에게 안 보인다. 승인된 구성원만 남고, 엄마아빠 계정은 안 센다
create table public.views (
  media_id uuid not null references public.media (id) on delete cascade,
  member_id uuid not null references public.members (id) on delete cascade,
  created_at timestamptz not null default now(),
  primary key (media_id, member_id)
);
-- 구성원을 지울 때(cascade) 찾기
create index views_member on public.views (member_id);
alter table public.views enable row level security;
revoke all on public.views from anon, authenticated;

-- 가족 기기: 본 사진들을 남긴다. 볼 수 있는 사진만(사진마다 그 가족방의 내 구성원), 한 번에 50장
create function public.sp_note_views(p_media_ids uuid[]) returns void
language sql security definer set search_path = ''
as $$
  insert into public.views (media_id, member_id)
  select x.id, m.id
  from unnest(p_media_ids[1:50]) t (mid)
  join public.media x on x.id = t.mid
  join public.members m on m.id = public.sp_device_member(x.family_id) and m.status = 'active'
  where public.sp_can_view_media(x.id)
  on conflict do nothing
$$;

-- 엄마아빠: 그 사진을 본 가족 이름(처음 본 순). 자기 가족방 사진만, 지금 승인된 구성원만
create function public.sp_parent_media_viewers(p_media_id uuid) returns table (name text)
language sql stable security definer set search_path = ''
as $$
  select m.display_name
  from public.views v join public.members m on m.id = v.member_id and m.status = 'active'
  where v.media_id = p_media_id and public.sp_parent_media(p_media_id)
  order by v.created_at
  limit 100
$$;

revoke execute on function public.sp_note_views(uuid[]), public.sp_parent_media_viewers(uuid) from public, anon, authenticated;
grant execute on function public.sp_note_views(uuid[]), public.sp_parent_media_viewers(uuid) to authenticated;
