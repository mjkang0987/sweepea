-- 새 사진 '확인'을 사람마다(117d, 사용자 2026-11-01 "1, 2는 진행"): 지금은 기기 쿠키라 폰·태블릿이 따로 셈.
-- 가족은 이미 있는 보신 기록(views, 넘겨 보기에서 가운데 머문 사진·크게 본 사진)으로, 엄빠는 새 표 parent_views로 '본 사진'을 사람마다 남기고
-- '아직 안 본 사진'을 사람마다 알려 준다(엄빠 앨범에도 새 사진 맨 위 — 117e).

-- 엄빠가 본 사진(크게 보기·넘겨 보기). 한 사람 한 사진 한 줄. 표는 함수로만
create table public.parent_views (
  media_id uuid not null references public.media (id) on delete cascade,
  user_id uuid not null references public.parents (user_id) on delete cascade,
  created_at timestamptz not null default now(),
  primary key (media_id, user_id)
);
create index parent_views_user on public.parent_views (user_id);
alter table public.parent_views enable row level security;
revoke all on public.parent_views from anon, authenticated;

-- 엄빠: 본 사진 남기기. 내 가족방 사진만, 한 번에 50장
create function public.sp_note_parent_views(p_media_ids uuid[]) returns void
language sql security definer set search_path = ''
as $$
  insert into public.parent_views (media_id, user_id)
  select t.mid, auth.uid()
  from unnest(p_media_ids[1:50]) t (mid)
  where public.sp_parent_media(t.mid)
  on conflict do nothing
$$;

-- 이 사람이 아직 안 본 사진(받은 목록 중, 한 번에 300장): 볼 수 있고 다 올라간 사진 중
-- 그 사람이 들어온 뒤 올라왔고(처음 들어온 사람에게 옛 사진이 전부 '새 사진'이 되지 않게), 내가 올리지 않았고, 본 기록이 없는 것.
-- 가족 기기는 그 가족방의 내 구성원(승인된 사람만), 엄빠는 내 가족방
create function public.sp_unseen_media(p_media_ids uuid[]) returns setof uuid
language sql stable security definer set search_path = ''
as $$
  select x.id
  from unnest(p_media_ids[1:300]) t (mid)
  join public.media x on x.id = t.mid and x.status = 'ready'
  left join public.members m on m.id = public.sp_device_member(x.family_id) and m.status = 'active'
  left join public.parents p on p.user_id = auth.uid() and p.family_id = x.family_id and p.removed_at is null
  where (m.id is not null and public.sp_can_view_media(x.id)
         and x.created_at > m.created_at
         and x.uploaded_by_member is distinct from m.id
         and not exists (select 1 from public.views v where v.media_id = x.id and v.member_id = m.id))
     or (m.id is null and p.user_id is not null
         and x.created_at > p.created_at
         and x.uploaded_by_parent is distinct from p.user_id
         and not exists (select 1 from public.parent_views pv where pv.media_id = x.id and pv.user_id = p.user_id))
$$;

revoke execute on function public.sp_note_parent_views(uuid[]), public.sp_unseen_media(uuid[]) from public, anon, authenticated;
grant execute on function public.sp_note_parent_views(uuid[]), public.sp_unseen_media(uuid[]) to authenticated;
