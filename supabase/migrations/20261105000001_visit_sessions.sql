-- 자세한 방문 기록(179, 사용자 2026-11-05 "관리자에 방문기록 시간까지 좀 남겨줘 자세히" → 시각·머문 시간·본 화면, 90일 보관).
-- 방문 한 번(30분 넘게 쉬었다 다시 연 것, visits와 같은 뜻)마다 한 줄: 누가·처음 연 시각·마지막으로 화면을 연 시각·연 화면 이름 차례.
-- 화면 이름만(주소·사진 번호·기기·IP는 안 남김). 90일 지난 줄은 새 방문을 적을 때 지운다(따로 도는 작업 없음).
-- 엄빠가 나가면 그 사람 줄도 지움(visits와 같은 트리거에서), 가족방이 지워지면 같이 지워짐(cascade). 운영 함수는 서버(service_role)만

create table public.visit_sessions (
  id bigint generated always as identity primary key,
  -- 웹이 방문마다 만든 무작위 열쇠(30분 쿠키, HttpOnly). 기기가 여러 가족방에 들어가 있으면 같은 열쇠로 가족방마다 한 줄
  key uuid not null,
  family_id uuid not null references public.families (id) on delete cascade,
  -- visits.kind와 같음: parent 엄빠 user_id, device devices.id, link·link_pw shares.id
  kind text not null check (kind in ('parent', 'device', 'link', 'link_pw')),
  visitor uuid not null,
  started_at timestamptz not null default now(),
  last_at timestamptz not null default now(),
  -- 연 화면 이름 차례(같은 화면 연달아는 한 번, 100개까지)
  screens text[] not null default '{}'
);
create index visit_sessions_family on public.visit_sessions (family_id, started_at desc);
create index visit_sessions_started on public.visit_sessions (started_at);
create index visit_sessions_visitor on public.visit_sessions (kind, visitor);
create index visit_sessions_key on public.visit_sessions (key);
alter table public.visit_sessions enable row level security;
revoke all on public.visit_sessions from anon, authenticated;

-- 화면 이름 한 개: 글자만, 40자까지(웹이 정한 이름이지만 함수는 누구나 부르므로)
create function public.sp_visit_screen(p_screen text) returns text
language sql immutable set search_path = ''
as $$ select nullif(left(regexp_replace(coalesce(p_screen, ''), '[[:cntrl:]]', '', 'g'), 40), '') $$;

-- 방문 시작: 날짜별 횟수(sp_note_visit과 같음) + 자세한 줄. 엄빠면 자기 가족방, 기기면 들어간 가족방마다.
-- 열쇠는 웹이 만들어 30분 쿠키에 담는다(답을 기다리지 않고 화면을 바로 보내려고). 이미 있는 열쇠면 다시 만들지 않음
create function public.sp_visit_start(p_key uuid, p_screen text) returns void
language plpgsql security definer set search_path = ''
as $$
declare v_screen text := public.sp_visit_screen(p_screen);
begin
  -- 같은 열쇠로 내 줄이 이미 있으면 그대로(엄빠·가족 출입증이 한 브라우저에 같이 있으면 같은 열쇠를 각자 씀)
  if p_key is null or exists (select 1 from public.visit_sessions s where s.key = p_key
      and ((s.kind = 'parent' and s.visitor = auth.uid())
        or (s.kind = 'device' and exists (select 1 from public.devices d where d.id = s.visitor and d.auth_user_id = auth.uid())))) then
    return;
  end if;
  perform public.sp_note_visit();
  delete from public.visit_sessions where started_at < now() - interval '90 days';
  insert into public.visit_sessions (key, family_id, kind, visitor, screens)
  select p_key, w.family_id, w.kind, w.visitor, case when v_screen is null then '{}'::text[] else array[v_screen] end from (
    select p.family_id, 'parent'::text as kind, p.user_id as visitor from public.parents p
      where p.user_id = auth.uid() and p.family_id is not null and p.removed_at is null
    union all
    select d.family_id, 'device', d.id from public.devices d left join public.members m on m.id = d.member_id
      where d.auth_user_id = auth.uid()
        and (d.status = 'pending' or (d.status = 'active' and (m.status = 'active' or (m.status = 'pending' and m.pending_until > now()))))
  ) w;
end $$;
revoke all on function public.sp_visit_start(uuid, text) from public, anon;
grant execute on function public.sp_visit_start(uuid, text) to authenticated;

-- 같은 방문 안에서 화면을 또 엶: 내 줄이고 30분 안일 때만 마지막 시각을 새로, 화면이 바뀌었으면 이름을 덧붙임
create function public.sp_visit_touch(p_key uuid, p_screen text) returns void
language sql security definer set search_path = ''
as $$
  update public.visit_sessions s set last_at = now(),
    screens = case when public.sp_visit_screen(p_screen) is null or s.screens[cardinality(s.screens)] = public.sp_visit_screen(p_screen)
        or cardinality(s.screens) >= 100 then s.screens
      else s.screens || public.sp_visit_screen(p_screen) end
  where s.key = p_key and s.last_at > now() - interval '30 minutes'
    and ((s.kind = 'parent' and s.visitor = auth.uid())
      or (s.kind = 'device' and exists (select 1 from public.devices d where d.id = s.visitor and d.auth_user_id = auth.uid())))
$$;
revoke all on function public.sp_visit_touch(uuid, text) from public, anon;
grant execute on function public.sp_visit_touch(uuid, text) to authenticated;

-- 가족 링크 단계(누구세요·비밀번호)를 연 것: 날짜별 횟수 + 자세한 줄(입장 전이라 사람 대신 링크). 서버만
create or replace function public.sp_note_link_visit(p_code text, p_step text) returns void
language sql security definer set search_path = ''
as $$
  insert into public.visits (family_id, kind, visitor, day)
    select s.family_id, p_step, s.id, public.sp_seoul_today() from public.shares s
    where s.code = p_code and s.revoked_at is null
  on conflict (family_id, kind, visitor, day) do update set count = public.visits.count + 1;
  insert into public.visit_sessions (key, family_id, kind, visitor, screens)
    select gen_random_uuid(), s.family_id, p_step, s.id, array[case when p_step = 'link_pw' then '가족 링크 비밀번호' else '가족 링크 누구세요' end] from public.shares s
    where s.code = p_code and s.revoked_at is null
$$;

-- 엄빠가 나가거나 옮기거나 지워지면 예전 가족방의 그 엄빠 자세한 줄도 지운다(처리방침 3항, visits와 같은 트리거)
create or replace function public.sp_visits_parent_gone() returns trigger
language plpgsql security definer set search_path = ''
as $$
begin
  if tg_op = 'DELETE' then
    delete from public.visits where kind = 'parent' and visitor = old.user_id and family_id = old.family_id;
    delete from public.visit_sessions where kind = 'parent' and visitor = old.user_id and family_id = old.family_id;
    return old;
  end if;
  if old.family_id is not null and (new.removed_at is not null or new.family_id is distinct from old.family_id) then
    delete from public.visits where kind = 'parent' and visitor = old.user_id and family_id = old.family_id;
    delete from public.visit_sessions where kind = 'parent' and visitor = old.user_id and family_id = old.family_id;
  end if;
  return new;
end $$;

-- 운영 가족방 상세 '방문 기록': 고른 기간(서울 날짜)에 시작한 방문, 최근 것부터 200줄. 누구는 이름(운영자가 이미 보는 엄빠·가족 이름)
create function public.sp_ops_visit_log(p_id uuid, p_from date, p_to date) returns jsonb
language sql stable security definer set search_path = ''
as $$
  select coalesce(jsonb_agg(jsonb_build_object('at', x.started_at, 'last', x.last_at, 'kind', x.kind, 'who', x.who, 'screens', x.screens)
      order by x.started_at desc), '[]')
  from (
    select s.started_at, s.last_at, s.kind, s.screens,
      case s.kind
        when 'parent' then (select p.display_name from public.parents p where p.user_id = s.visitor)
        -- 들어오지 못했거나 내보낸 기기는 이름 없이(처리방침 3항: 이름 없는 기기 번호와 기록만)
        when 'device' then (select coalesce(m.display_name, d.requested_name) from public.devices d left join public.members m on m.id = d.member_id where d.id = s.visitor
          and (d.status = 'pending' or (d.status = 'active' and (m.status = 'active' or (m.status = 'pending' and m.pending_until > now())))))
        else null end as who
    from public.visit_sessions s
    where s.family_id = p_id and p_from <= p_to and p_to - p_from < 400
      and s.started_at >= p_from::timestamp at time zone 'Asia/Seoul' and s.started_at < (p_to + 1)::timestamp at time zone 'Asia/Seoul'
    order by s.started_at desc
    limit 200
  ) x
$$;
revoke all on function public.sp_ops_visit_log(uuid, date, date) from public, anon, authenticated;
grant execute on function public.sp_ops_visit_log(uuid, date, date) to service_role;
