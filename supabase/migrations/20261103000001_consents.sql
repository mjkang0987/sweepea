-- 동의 기록(152, 사용자 2026-11-03 "SNS 로그인할 때 동의 받고 있나?" → 1~3 진행)
-- terms: 이용약관 + 개인정보 처리방침 확인 + 만 14세 이상, health: 예방접종·검진 완료 기록(민감정보) 수집·이용. version은 시행일
-- 본인 것만 읽고, 쓰기는 sp_agree로만. 계정이 지워지면(sp_purge_family 등) 같이 지워짐
create table public.consents (
  user_id uuid not null references auth.users (id) on delete cascade,
  kind text not null check (kind in ('terms', 'health')),
  version text not null check (version ~ '^[0-9]{4}-[0-9]{2}-[0-9]{2}$'),
  agreed_at timestamptz not null default now(),
  primary key (user_id, kind, version)
);
alter table public.consents enable row level security;
create policy consents_select_own on public.consents for select to authenticated using (user_id = (select auth.uid()));
revoke all on public.consents from anon, authenticated;
grant select on public.consents to authenticated;

create function public.sp_agree(p_kind text, p_version text) returns void
language sql security definer set search_path = ''
as $$
  -- auth.uid()가 없으면(로그인 안 함) not null에 걸려 실패. 같은 버전 두 번은 처음 시각 그대로
  insert into public.consents (user_id, kind, version) values (auth.uid(), p_kind, p_version)
  on conflict do nothing
$$;
revoke all on function public.sp_agree(text, text) from public, anon;
grant execute on function public.sp_agree(text, text) to authenticated;

-- 엄빠 첫 화면 묶음에 동의 기록을 붙임(모양·권한은 그대로, 20261101000001_avatar 본문 + 'agreed')
create or replace function public.sp_parent_home() returns jsonb
language sql stable security definer set search_path = ''
as $$
  select coalesce((
    select jsonb_build_object(
      'family_id', p.family_id,
      'role', p.role,
      'avatar', p.avatar,
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
    where p.user_id = auth.uid() and p.removed_at is null and (f.delete_after is null or f.delete_after > now())
  ), jsonb_build_object('family_id', null))
  -- 동의한 것('kind:version', 152). 가족방이 없어도(처음 설정 전) 붙인다
  || jsonb_build_object('agreed', coalesce((select jsonb_agg(c.kind || ':' || c.version) from public.consents c where c.user_id = auth.uid()), '[]'::jsonb))
$$;
