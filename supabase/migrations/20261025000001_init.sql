-- 스위피 초기 스키마
-- 부모: Supabase Auth 사용자(소셜 로그인). 가족 기기: Supabase 익명 사용자(기기 하나 = 익명 사용자 하나).
-- 권한 판정은 이 파일의 RLS와 sp_* 함수에서만 한다.

create extension if not exists pgcrypto with schema extensions;

-- ───────────────────────── 테이블 ─────────────────────────

create table public.families (
  id uuid primary key default gen_random_uuid(),
  name text not null default '우리 가족' check (char_length(name) between 1 and 30),
  plan text not null default 'free' check (plan in ('free', 'family')),
  storage_used_bytes bigint not null default 0 check (storage_used_bytes >= 0),
  download_allowed boolean not null default false,
  groups_enabled boolean not null default false,
  -- 가족 화면 글자 크기 기본값. relation: 할머니·할아버지 호칭이면 크게, 나머지 기본
  text_size_mode text not null default 'relation' check (text_size_mode in ('relation', 'base', 'large', 'xlarge')),
  -- 탈퇴 유예: 값이 있으면 가족 화면은 바로 닫히고, 이 시각 뒤 삭제한다
  delete_after timestamptz,
  created_at timestamptz not null default now()
);

-- 가족방을 만든 부모 한 명. 배우자는 계정 없이 구성원 + 올리기 권한으로 들어온다
create table public.parents (
  user_id uuid primary key references auth.users (id) on delete cascade,
  family_id uuid not null unique references public.families (id) on delete cascade,
  role text not null check (role in ('mom', 'dad')),
  display_name text not null check (char_length(display_name) between 1 and 20),
  created_at timestamptz not null default now()
);

create table public.children (
  id uuid primary key default gen_random_uuid(),
  family_id uuid not null references public.families (id) on delete cascade,
  name text not null check (char_length(name) between 1 and 12),
  birth_date date not null,
  show_health boolean not null default true,
  sort_order int not null default 0,
  created_at timestamptz not null default now(),
  unique (family_id, id)
);

-- 그룹 기능이 꺼져 있어도 가족방마다 기본 그룹 하나("가족")가 있다
create table public.groups (
  id uuid primary key default gen_random_uuid(),
  family_id uuid not null references public.families (id) on delete cascade,
  name text not null check (char_length(name) between 1 and 12),
  include_by_default boolean not null default true,
  password_hash text not null,
  password_hint text check (char_length(password_hint) <= 30),
  sort_order int not null default 0,
  created_at timestamptz not null default now(),
  unique (family_id, name),
  unique (family_id, id)
);

create table public.shares (
  id uuid primary key default gen_random_uuid(),
  family_id uuid not null references public.families (id) on delete cascade,
  code text not null unique check (code ~ '^[A-Za-z0-9]{8}$'),
  -- 문자로 공유하기: 한 사람용 설치 링크. 값이 있으면 그 사람만, 한 번만 쓴다
  target_member_id uuid,
  used_at timestamptz,
  -- 카톡 카드 대표 사진(올리기 화면에서 고른 첫 장)
  cover_media_id uuid,
  created_at timestamptz not null default now(),
  unique (family_id, id)
);

create table public.members (
  id uuid primary key default gen_random_uuid(),
  family_id uuid not null references public.families (id) on delete cascade,
  group_id uuid not null,
  display_name text not null check (char_length(display_name) between 1 and 12),
  status text not null default 'active' check (status in ('active', 'pending', 'rejected')),
  -- 새 이름 승인 대기 마감(3일). 지나면 만료로 본다
  pending_until timestamptz,
  -- 승인 전에는 이 공유 묶음의 사진만 본다
  entry_share_id uuid references public.shares (id) on delete set null,
  text_size text check (text_size in ('base', 'large', 'xlarge')),
  created_at timestamptz not null default now(),
  unique (group_id, display_name),
  unique (family_id, id),
  -- 같은 가족방 그룹만(다른 가족방 id를 넣어도 FK가 막는다)
  foreign key (family_id, group_id) references public.groups (family_id, id) on delete cascade,
  check (status <> 'pending' or pending_until is not null)
);

alter table public.shares
  add constraint shares_target_member_fk foreign key (family_id, target_member_id) references public.members (family_id, id) on delete cascade;

create table public.share_groups (
  family_id uuid not null,
  share_id uuid not null,
  group_id uuid not null,
  primary key (share_id, group_id),
  foreign key (family_id, share_id) references public.shares (family_id, id) on delete cascade,
  foreign key (family_id, group_id) references public.groups (family_id, id) on delete cascade
);

create table public.devices (
  id uuid primary key default gen_random_uuid(),
  -- 기기(익명 사용자) 하나가 가족방마다 한 행. 할머니 폰 하나로 딸네·아들네 둘 다 들어간다
  auth_user_id uuid not null references auth.users (id) on delete cascade,
  family_id uuid not null references public.families (id) on delete cascade,
  member_id uuid,
  -- pending: 비밀번호 10번 틀려서 부모 승인 대기. revoked: 부모가 "내 가족 아님"
  status text not null default 'active' check (status in ('active', 'pending', 'revoked')),
  -- 올리기 권한은 승인된 기기에만 붙는다. 새 기기는 다시 승인
  can_upload boolean not null default false,
  -- 승인 대기 기기가 들어가려던 이름. 부모가 승인할 때 구성원을 붙이거나 만든다(틀린 시도로는 구성원을 만들지 않는다)
  requested_member_id uuid references public.members (id) on delete set null,
  requested_group_id uuid references public.groups (id) on delete set null,
  requested_name text check (char_length(requested_name) between 1 and 12),
  label text check (char_length(label) <= 30),
  last_seen_at timestamptz not null default now(),
  created_at timestamptz not null default now(),
  unique (auth_user_id, family_id),
  foreign key (family_id, member_id) references public.members (family_id, id) on delete set null (member_id)
);

-- 비밀번호 틀린 기록. 기기·그룹별(3번 → 30초, 10번 → 승인 대기)과 그룹 전체(1시간 20번 → 새 기기는 승인 대기)로 센다.
-- 익명 사용자를 새로 만들어 횟수를 초기화하는 공격을 그룹 전체 한도로 막는다
create table public.entry_failures (
  id bigint generated always as identity primary key,
  family_id uuid not null references public.families (id) on delete cascade,
  group_id uuid not null references public.groups (id) on delete cascade,
  auth_user_id uuid not null,
  at timestamptz not null default now()
);

create table public.media (
  id uuid primary key default gen_random_uuid(),
  family_id uuid not null references public.families (id) on delete cascade,
  uploaded_by_parent uuid references public.parents (user_id) on delete set null,
  uploaded_by_member uuid,
  kind text not null check (kind in ('photo', 'video')),
  taken_at timestamptz not null,
  taken_at_source text not null check (taken_at_source in ('exif', 'file', 'upload', 'manual')),
  object_key text,
  view_key text,
  thumb_key text,
  poster_key text,
  bytes bigint not null default 0 check (bytes >= 0),
  width int,
  height int,
  duration_sec numeric(7, 2),
  status text not null default 'uploading' check (status in ('uploading', 'ready', 'deleted')),
  created_at timestamptz not null default now(),
  unique (family_id, id),
  foreign key (family_id, uploaded_by_member) references public.members (family_id, id) on delete set null (uploaded_by_member),
  check (num_nonnulls(uploaded_by_parent, uploaded_by_member) <= 1)
);
alter table public.shares add foreign key (cover_media_id) references public.media (id) on delete set null;

-- 연결 표는 family_id를 같이 들고 복합 FK로 같은 가족방끼리만 잇는다
create table public.media_groups (
  family_id uuid not null,
  media_id uuid not null,
  group_id uuid not null,
  primary key (media_id, group_id),
  foreign key (family_id, media_id) references public.media (family_id, id) on delete cascade,
  foreign key (family_id, group_id) references public.groups (family_id, id) on delete cascade
);

create table public.media_children (
  family_id uuid not null,
  media_id uuid not null,
  child_id uuid not null,
  primary key (media_id, child_id),
  foreign key (family_id, media_id) references public.media (family_id, id) on delete cascade,
  foreign key (family_id, child_id) references public.children (family_id, id) on delete cascade
);

create table public.share_media (
  family_id uuid not null,
  share_id uuid not null,
  media_id uuid not null,
  primary key (share_id, media_id),
  foreign key (family_id, share_id) references public.shares (family_id, id) on delete cascade,
  foreign key (family_id, media_id) references public.media (family_id, id) on delete cascade
);

create table public.reactions (
  media_id uuid not null references public.media (id) on delete cascade,
  member_id uuid not null references public.members (id) on delete cascade,
  kind text not null check (kind in ('heart', 'best', 'good', 'moved', 'sparkle')),
  created_at timestamptz not null default now(),
  primary key (media_id, member_id, kind)
);

create table public.comments (
  id uuid primary key default gen_random_uuid(),
  media_id uuid not null references public.media (id) on delete cascade,
  member_id uuid not null references public.members (id) on delete cascade,
  body text not null check (char_length(body) between 1 and 200),
  created_at timestamptz not null default now(),
  edited_at timestamptz,
  deleted_at timestamptz
);

-- 인앱결제(App Store·Google Play) 영수증 검증 결과. 쓰기는 서버(service_role)만
create table public.entitlements (
  id uuid primary key default gen_random_uuid(),
  family_id uuid not null references public.families (id) on delete cascade,
  platform text not null check (platform in ('ios', 'android')),
  product_id text not null,
  original_transaction_id text not null unique,
  expires_at timestamptz not null,
  created_at timestamptz not null default now()
);

create index on public.children (family_id);
create index on public.groups (family_id);
create index on public.members (family_id);
create index on public.members (group_id);
create index on public.devices (family_id);
create index on public.devices (member_id);
create index on public.shares (family_id);
create index on public.media (family_id, taken_at desc);
create index on public.media_groups (group_id);
create index on public.media_children (child_id);
create index on public.share_media (media_id);
create index on public.reactions (member_id);
create index on public.comments (media_id, created_at);
create index on public.entitlements (family_id);
create index on public.entry_failures (group_id, at);
create index on public.entry_failures (auth_user_id, group_id);

-- ───────────────────────── 권한 함수 ─────────────────────────
-- 모두 security definer + 빈 search_path. RLS 정책 안에서 다른 표를 읽을 때 재귀를 피한다.

create function public.sp_parent_family() returns uuid
language sql stable security definer set search_path = ''
as $$ select p.family_id from public.parents p where p.user_id = auth.uid() $$;

-- 지금 기기의 구성원들(가족방마다 하나, 열람 가능한 상태일 때만). 가족방이 탈퇴 유예 중이면 빠진다
create function public.sp_device_members() returns setof uuid
language sql stable security definer set search_path = ''
as $$
  select m.id
  from public.devices d
  join public.members m on m.id = d.member_id
  join public.families f on f.id = d.family_id
  where d.auth_user_id = auth.uid()
    and d.status = 'active'
    and f.delete_after is null
    and (m.status = 'active' or (m.status = 'pending' and m.pending_until > now()))
$$;

-- 그 가족방에서 지금 기기의 구성원
create function public.sp_device_member(p_family_id uuid) returns uuid
language sql stable security definer set search_path = ''
as $$ select m.id from public.members m where m.family_id = p_family_id and m.id in (select public.sp_device_members()) $$;

-- 그 가족방에서 지금 기기의 구성원이 승인된 상태인가(승인 대기는 가족 명단을 못 본다)
create function public.sp_device_active(p_family_id uuid) returns boolean
language sql stable security definer set search_path = ''
as $$ select exists (select 1 from public.members m where m.id = public.sp_device_member(p_family_id) and m.status = 'active') $$;

-- 그 가족방의 부모이거나 구성원인가
create function public.sp_in_family(p_family_id uuid) returns boolean
language sql stable security definer set search_path = ''
as $$ select coalesce(p_family_id = public.sp_parent_family(), false) or public.sp_device_member(p_family_id) is not null $$;

-- 사진이 속한 가족방에서 지금 기기의 구성원(반응·한마디를 다른 가족방 이름으로 달지 못하게)
create function public.sp_media_member(p_media_id uuid) returns uuid
language sql stable security definer set search_path = ''
as $$ select public.sp_device_member((select x.family_id from public.media x where x.id = p_media_id)) $$;

create function public.sp_can_view_media(p_media_id uuid) returns boolean
language sql stable security definer set search_path = ''
as $$
  with me as (
    select m.id, m.group_id, m.status, m.entry_share_id, m.family_id, d.can_upload
    from public.members m
    join public.devices d on d.member_id = m.id and d.auth_user_id = auth.uid()
    where m.id in (select public.sp_device_members())
  )
  select exists (
    select 1 from public.media x
    where x.id = p_media_id
      and (
        x.family_id = public.sp_parent_family()
        or (
          x.status = 'ready'
          and exists (
            select 1 from me
            where me.family_id = x.family_id
              and (
                -- 올리기 권한 가족은 모든 그룹 사진을 본다
                (me.status = 'active' and me.can_upload)
                or (me.status = 'active' and exists (
                  select 1 from public.media_groups g where g.media_id = x.id and g.group_id = me.group_id))
                -- 승인 대기는 들어온 공유 묶음만
                or (me.status = 'pending' and exists (
                  select 1 from public.share_media s where s.media_id = x.id and s.share_id = me.entry_share_id))
              )
          )
        )
      )
  )
$$;

create function public.sp_can_upload(p_family_id uuid) returns boolean
language sql stable security definer set search_path = ''
as $$
  select coalesce(p_family_id = public.sp_parent_family(), false)
    or exists (
      select 1 from public.devices d join public.members m on m.id = d.member_id
      where d.auth_user_id = auth.uid() and d.status = 'active' and d.can_upload
        and m.status = 'active' and m.family_id = p_family_id
        and m.id = public.sp_device_member(p_family_id)
    )
$$;

-- 사진의 공개 그룹·아이 태그를 바꿀 수 있는가: 부모 또는 그 사진을 올린 가족
create function public.sp_can_edit_media(p_media_id uuid) returns boolean
language sql stable security definer set search_path = ''
as $$
  select exists (
    select 1 from public.media x
    where x.id = p_media_id
      and (x.family_id = public.sp_parent_family()
           or (x.uploaded_by_member is not null and x.uploaded_by_member = public.sp_device_member(x.family_id)
               and public.sp_can_upload(x.family_id)))
  )
$$;

-- ───────────────────────── RLS ─────────────────────────

alter table public.families enable row level security;
alter table public.parents enable row level security;
alter table public.children enable row level security;
alter table public.groups enable row level security;
alter table public.shares enable row level security;
alter table public.members enable row level security;
alter table public.share_groups enable row level security;
alter table public.devices enable row level security;
alter table public.media enable row level security;
alter table public.media_groups enable row level security;
alter table public.media_children enable row level security;
alter table public.share_media enable row level security;
alter table public.reactions enable row level security;
alter table public.comments enable row level security;
alter table public.entitlements enable row level security;
-- 정책 없음: 입장 함수(definer)만 읽고 쓴다
alter table public.entry_failures enable row level security;

create policy families_read on public.families for select to authenticated
  using (public.sp_in_family(id));
create policy families_parent_update on public.families for update to authenticated
  using (id = public.sp_parent_family()) with check (id = public.sp_parent_family());

create policy parents_self on public.parents for select to authenticated
  using (user_id = auth.uid());

create policy children_read on public.children for select to authenticated
  using (public.sp_in_family(family_id));
create policy children_parent_write on public.children for all to authenticated
  using (family_id = public.sp_parent_family()) with check (family_id = public.sp_parent_family());

-- 비밀번호 해시는 열 권한으로 막는다(아래 grant). 바꾸기는 sp_set_group_password로만
create policy groups_parent on public.groups for select to authenticated
  using (family_id = public.sp_parent_family());
create policy groups_parent_update on public.groups for update to authenticated
  using (family_id = public.sp_parent_family()) with check (family_id = public.sp_parent_family());
create policy groups_parent_delete on public.groups for delete to authenticated
  using (family_id = public.sp_parent_family());
create policy groups_member_own on public.groups for select to authenticated
  using (id = (select m.group_id from public.members m where m.id = public.sp_device_member(groups.family_id)));

-- 공유 링크는 sp_create_share로만 만든다(코드·시각을 클라이언트가 못 정하게). 부모는 보고 지우기만
create policy shares_parent_read on public.shares for select to authenticated
  using (family_id = public.sp_parent_family());
create policy shares_parent_delete on public.shares for delete to authenticated
  using (family_id = public.sp_parent_family());
create policy share_groups_parent_read on public.share_groups for select to authenticated
  using (family_id = public.sp_parent_family());
create policy share_media_parent_read on public.share_media for select to authenticated
  using (family_id = public.sp_parent_family());

-- 구성원 이름은 같은 가족방이면 보인다(댓글·반응 작성자 표시용)
create policy members_read on public.members for select to authenticated
  using (family_id = public.sp_parent_family()
         or id = public.sp_device_member(family_id)
         or public.sp_device_active(family_id));
-- 부모가 가족 이름을 미리 등록해 두면 가족은 "이름 고르기"로 바로 들어온다
create policy members_parent_insert on public.members for insert to authenticated
  with check (family_id = public.sp_parent_family()
              and exists (select 1 from public.groups g where g.id = members.group_id and g.family_id = members.family_id));
create policy members_parent_write on public.members for update to authenticated
  using (family_id = public.sp_parent_family()) with check (family_id = public.sp_parent_family());
create policy members_parent_delete on public.members for delete to authenticated
  using (family_id = public.sp_parent_family());
create policy members_self_update on public.members for update to authenticated
  using (id in (select public.sp_device_members())) with check (id in (select public.sp_device_members()));

create policy devices_parent on public.devices for select to authenticated
  using (family_id = public.sp_parent_family());
create policy devices_parent_update on public.devices for update to authenticated
  using (family_id = public.sp_parent_family()) with check (family_id = public.sp_parent_family());
create policy devices_self on public.devices for select to authenticated
  using (auth_user_id = auth.uid());

-- 부모·올린 사람은 행 값으로 바로 판정(방금 넣은 행도 보이게), 나머지는 sp_can_view_media
create policy media_parent_read on public.media for select to authenticated
  using (family_id = public.sp_parent_family());
create policy media_uploader_read on public.media for select to authenticated
  using (uploaded_by_member is not null and uploaded_by_member = public.sp_device_member(family_id) and status <> 'deleted');
create policy media_read on public.media for select to authenticated
  using (public.sp_can_view_media(id));
create policy media_parent_update on public.media for update to authenticated
  using (family_id = public.sp_parent_family()) with check (family_id = public.sp_parent_family());
create policy media_parent_delete on public.media for delete to authenticated
  using (family_id = public.sp_parent_family());

create policy media_groups_read on public.media_groups for select to authenticated
  using (public.sp_can_view_media(media_id));
create policy media_groups_write on public.media_groups for all to authenticated
  using (public.sp_can_edit_media(media_id))
  with check (public.sp_can_edit_media(media_id));

create policy media_children_read on public.media_children for select to authenticated
  using (public.sp_can_view_media(media_id));
create policy media_children_write on public.media_children for all to authenticated
  using (public.sp_can_edit_media(media_id))
  with check (public.sp_can_edit_media(media_id));

create policy reactions_read on public.reactions for select to authenticated
  using (public.sp_can_view_media(media_id));
create policy reactions_delete on public.reactions for delete to authenticated
  using (member_id in (select public.sp_device_members()));

-- 한마디 글은 그 가족방 부모와 쓴 사람만(가족 화면엔 수만 보인다, sp_reaction_counts)
create policy comments_read on public.comments for select to authenticated
  using (deleted_at is null
         and (member_id in (select public.sp_device_members())
              or exists (select 1 from public.media x where x.id = comments.media_id and x.family_id = public.sp_parent_family())));
create policy comments_self_update on public.comments for update to authenticated
  using (member_id in (select public.sp_device_members())) with check (member_id in (select public.sp_device_members()));
-- 지우기(본인·부모)는 sp_delete_comment로. 지운 행은 읽기 정책에서 빠져서 UPDATE로는 못 한다

create policy entitlements_parent on public.entitlements for select to authenticated
  using (family_id = public.sp_parent_family());

-- 열 권한: 비밀번호 해시는 어떤 클라이언트도 읽거나 직접 쓰지 못한다
revoke select, insert, update on public.groups from anon, authenticated;
grant select (id, family_id, name, include_by_default, password_hint, sort_order, created_at) on public.groups to authenticated;
grant update (name, include_by_default, password_hint, sort_order) on public.groups to authenticated;

-- 가족 기기가 스스로 바꿀 수 있는 열은 글자 크기뿐
revoke update on public.members from authenticated;
grant update (display_name, group_id, status, pending_until, text_size) on public.members to authenticated;
revoke update on public.devices from authenticated;
grant update (status, can_upload, label) on public.devices to authenticated;
-- 기기 사용자 id는 안 보여 준다: 가족방마다 같은 값이라 두 집 부모가 맞춰 보면 같은 사람인 걸 알 수 있다.
-- 그래서 select *·returning *는 거부된다. 부모 화면은 열을 꼭 적는다(select=id,status,...)
revoke select on public.devices from authenticated;
grant select (id, family_id, member_id, status, can_upload, requested_member_id, requested_group_id, requested_name, label, last_seen_at, created_at)
  on public.devices to authenticated;
-- 그룹은 켜면 끌 수 없으니 groups_enabled는 sp_add_group만 바꾼다
revoke update on public.families from authenticated;
grant update (name, download_allowed, text_size_mode, delete_after) on public.families to authenticated;
revoke insert on public.comments, public.reactions from authenticated;
-- 반응·한마디 넣기는 sp_react·sp_comment로만(하루 한도·공백 정리·구성원 확인)
revoke truncate, references, trigger on all tables in schema public from anon, authenticated;
revoke update on public.comments from authenticated;
grant update (body) on public.comments to authenticated;
-- 사진: 상태·저장 키·용량은 서버(service_role)만. 클라이언트는 기본 정보만 넣고 촬영일만 고친다
-- 사진 행은 sp_create_media로만 만든다(올린 사람·그룹·아이 태그를 함께 검사)
revoke insert, update on public.media from authenticated;
-- 읽기는 열을 정해서: 부모 사용자 id·원본 키·용량은 가족에게 안 보인다. select * 는 거부되니 열을 적는다
revoke select on public.media from authenticated;
grant select (id, family_id, uploaded_by_member, kind, taken_at, taken_at_source, width, height, duration_sec,
  status, view_key, thumb_key, poster_key, created_at) on public.media to authenticated;
grant update (taken_at, taken_at_source) on public.media to authenticated;
-- 연결 표는 넣고 지우기만
revoke update on public.media_groups, public.media_children, public.share_groups, public.share_media from authenticated;
revoke insert on public.shares, public.share_groups, public.share_media from authenticated;
revoke update on public.shares from authenticated;

-- 구성원 자기 행 수정은 글자 크기만 허용(다른 열은 부모만)
-- 트리거는 호출자 권한으로 돈다: 클라이언트(authenticated)만 막고 서버(postgres·service_role)는 통과
create function public.sp_members_guard() returns trigger
language plpgsql set search_path = ''
as $$
begin
  if current_user = 'authenticated' and public.sp_parent_family() is distinct from new.family_id then
    if new.display_name is distinct from old.display_name
       or new.group_id is distinct from old.group_id
       or new.status is distinct from old.status
       or new.pending_until is distinct from old.pending_until then
      raise exception 'only_text_size' using errcode = '42501';
    end if;
  end if;
  return new;
end $$;
create trigger members_guard before update on public.members
  for each row execute function public.sp_members_guard();

-- 한마디 고치면 고친 시각을 남긴다
create function public.sp_comments_touch() returns trigger
language plpgsql set search_path = ''
as $$
begin
  if new.body is distinct from old.body then new.edited_at := now(); end if;
  return new;
end $$;
create trigger comments_touch before update on public.comments
  for each row execute function public.sp_comments_touch();

-- 반응·한마디를 남긴 적 있는 구성원인가(내보낸 사람의 기록은 같은 이름 재사용으로 지우지 않는다)
create function public.sp_member_has_history(p_member uuid) returns boolean
language sql stable security definer set search_path = ''
as $$
  select exists (select 1 from public.reactions where member_id = p_member)
      or exists (select 1 from public.comments where member_id = p_member)
$$;
revoke all on function public.sp_member_has_history(uuid) from public, anon, authenticated;

-- 부모가 승인 대기 기기를 승인하면: 틀린 기록을 지우고, 들어가려던 이름을 붙인다(새 이름이면 구성원을 만든다)
create function public.sp_devices_approve() returns trigger
language plpgsql security definer set search_path = ''
as $$
declare v_member uuid;
begin
  if old.status = 'pending' and new.status = 'active' then
    delete from public.entry_failures where auth_user_id = new.auth_user_id and family_id = new.family_id;
    if new.requested_member_id is not null then
      -- 들어가려던 이름이 그새 거절·삭제됐으면 승인하지 않는다(승인해도 볼 수 없는 기기가 된다)
      if not exists (select 1 from public.members where id = new.requested_member_id and status = 'active') then
        raise exception 'member_gone' using errcode = '22023';
      end if;
      new.member_id := new.requested_member_id;
    elsif new.requested_name is not null and new.requested_group_id is not null then
      delete from public.members
        where group_id = new.requested_group_id and display_name = new.requested_name
          and ((status = 'rejected' and not public.sp_member_has_history(id)) or (status = 'pending' and pending_until <= now()));
      -- 그 사이 같은 이름이 생겼으면: 승인된 이름이면 그 사람으로 붙이고, 아직 승인 대기면 막는다
      select id into v_member from public.members
        where group_id = new.requested_group_id and display_name = new.requested_name and status = 'active';
      if v_member is null then
        if exists (select 1 from public.members where group_id = new.requested_group_id and display_name = new.requested_name) then
          raise exception 'name_taken' using errcode = '22023';
        end if;
        insert into public.members (family_id, group_id, display_name)
          values (new.family_id, new.requested_group_id, new.requested_name)
          returning id into v_member;
      end if;
      new.member_id := v_member;
    elsif new.member_id is null then
      -- 들어가려던 이름이 지워져 요청이 비었다: 붙일 사람이 없으니 승인하지 않는다
      raise exception 'member_gone' using errcode = '22023';
    end if;
    new.requested_member_id := null; new.requested_group_id := null; new.requested_name := null;
  end if;
  return new;
end $$;
create trigger devices_approve before update of status on public.devices
  for each row execute function public.sp_devices_approve();

-- 부모가 이름을 거절하면 그 이름으로 들어온 기기도 막는다(같은 기기가 같은 이름으로 다시 못 들어오게)
create function public.sp_members_rejected() returns trigger
language plpgsql security definer set search_path = ''
as $$
begin
  if new.status = 'rejected' and old.status is distinct from 'rejected' then
    update public.devices set status = 'revoked', can_upload = false
      where member_id = new.id or (requested_member_id = new.id and status = 'pending');
  end if;
  return new;
end $$;
create trigger members_rejected after update of status on public.members
  for each row execute function public.sp_members_rejected();

-- ───────────────────────── RPC ─────────────────────────

create function public.sp_is_anonymous() returns boolean
language sql stable set search_path = ''
as $$ select coalesce((auth.jwt() ->> 'is_anonymous')::boolean, false) $$;

-- 부모 처음 설정: 가족방 + 부모 + 기본 그룹("가족") + 첫 아이
create function public.sp_create_family(
  p_role text, p_display_name text, p_child_name text, p_birth_date date,
  p_password text, p_hint text default null
) returns uuid
language plpgsql security definer set search_path = ''
as $$
declare v_family uuid;
begin
  if auth.uid() is null or public.sp_is_anonymous() then
    raise exception 'parent_login_required' using errcode = '42501';
  end if;
  if exists (select 1 from public.parents where user_id = auth.uid()) then
    raise exception 'family_exists' using errcode = '23505';
  end if;
  -- 한 사용자가 부모이면서 다른 가족방 기기일 수 없다
  if exists (select 1 from public.devices where auth_user_id = auth.uid()) then
    raise exception 'is_device' using errcode = '42501';
  end if;
  if p_password !~ '^[0-9]{4}$' then
    raise exception 'password_4_digits' using errcode = '22023';
  end if;
  insert into public.families default values returning id into v_family;
  insert into public.parents (user_id, family_id, role, display_name)
    values (auth.uid(), v_family, p_role, p_display_name);
  insert into public.groups (family_id, name, password_hash, password_hint)
    values (v_family, '가족', extensions.crypt(p_password, extensions.gen_salt('bf')), p_hint);
  insert into public.children (family_id, name, birth_date) values (v_family, p_child_name, p_birth_date);
  return v_family;
end $$;

create function public.sp_set_group_password(p_group_id uuid, p_password text, p_hint text) returns void
language plpgsql security definer set search_path = ''
as $$
begin
  if p_password !~ '^[0-9]{4}$' then
    raise exception 'password_4_digits' using errcode = '22023';
  end if;
  update public.groups
    set password_hash = extensions.crypt(p_password, extensions.gen_salt('bf')), password_hint = p_hint
    where id = p_group_id and family_id = public.sp_parent_family();
  if not found then raise exception 'not_allowed' using errcode = '42501'; end if;
end $$;

create function public.sp_add_group(p_name text, p_password text, p_hint text default null, p_include_by_default boolean default true)
returns uuid
language plpgsql security definer set search_path = ''
as $$
declare v_family uuid := public.sp_parent_family(); v_id uuid;
begin
  if v_family is null then raise exception 'not_allowed' using errcode = '42501'; end if;
  if p_password !~ '^[0-9]{4}$' then raise exception 'password_4_digits' using errcode = '22023'; end if;
  insert into public.groups (family_id, name, password_hash, password_hint, include_by_default)
    values (v_family, p_name, extensions.crypt(p_password, extensions.gen_salt('bf')), p_hint, p_include_by_default)
    returning id into v_id;
  -- 그룹은 켜면 끌 수 없다
  update public.families set groups_enabled = true where id = v_family;
  return v_id;
end $$;

-- 입장 전 화면(누구세요?)에 필요한 정보. 링크를 받은 사람이면 누구나(익명 기기 포함)
create function public.sp_entry_info(p_code text) returns jsonb
language plpgsql stable security definer set search_path = ''
as $$
declare s public.shares; f public.families; v_child text; v_me jsonb;
begin
  select * into s from public.shares where code = p_code;
  if not found then return jsonb_build_object('result', 'not_found'); end if;
  select * into f from public.families where id = s.family_id;
  -- 이 가족방에서 지금 기기 상태(처음이면 null). 이미 들어온 기기는 바로 앨범으로 보낸다
  select jsonb_build_object(
      'device', d.status,
      'member', case when m.id is null then null
                     when m.status = 'pending' and m.pending_until <= now() then 'expired' else m.status end,
      'name', coalesce(m.display_name, d.requested_name))
    into v_me
    from public.devices d left join public.members m on m.id = d.member_id
    where d.auth_user_id = auth.uid() and d.family_id = s.family_id;
  if f.delete_after is not null then return jsonb_build_object('result', 'closed', 'me', v_me); end if;
  -- 한 사람용 문자 링크는 한 번, 72시간 안에만
  if s.target_member_id is not null and (s.used_at is not null or s.created_at + interval '72 hours' <= now()) then
    return jsonb_build_object('result', 'expired', 'me', v_me);
  end if;
  select c.name into v_child from public.children c where c.family_id = f.id order by c.sort_order, c.created_at limit 1;
  return jsonb_build_object(
    'result', 'ok',
    'me', v_me,
    'child_name', v_child,
    'new_entry_open', s.created_at + interval '72 hours' > now() and s.used_at is null,
    'target_member_id', s.target_member_id,
    'groups', coalesce((
      select jsonb_agg(jsonb_build_object(
        'id', g.id, 'name', g.name, 'hint', g.password_hint,
        'members', coalesce((
          select jsonb_agg(jsonb_build_object('id', m.id, 'name', m.display_name) order by m.created_at)
          from public.members m where m.group_id = g.id and m.status = 'active'
        ), '[]'::jsonb)
      ) order by g.sort_order, g.created_at)
      from public.groups g
      join public.share_groups sg on sg.group_id = g.id and sg.share_id = s.id
    ), '[]'::jsonb)
  );
end $$;

-- 입장: 이름 고르기(p_member_id) 또는 새 이름(p_new_name + p_group_id) + 그룹 비밀번호
-- 결과: ok | pending(새 이름, 승인 대기) | wrong_password | locked | needs_approval(10번 틀림·그룹 경보) |
--       expired(새 입장 72시간 지남, 쓴 문자 링크) | not_found | closed | revoked | name_taken | bad_request
create function public.sp_enter(
  p_code text, p_password text,
  p_member_id uuid default null, p_new_name text default null, p_group_id uuid default null
) returns jsonb
language plpgsql security definer set search_path = ''
as $$
declare
  s public.shares; d public.devices; g public.groups; m public.members;
  v_uid uuid := auth.uid();
  v_group uuid; v_new_open boolean; v_ok boolean;
  v_dev_fail int; v_last timestamptz; v_group_fail int; v_group_day int; v_alarm boolean; v_known boolean;
  v_name text := btrim(p_new_name);
begin
  if v_uid is null then raise exception 'login_required' using errcode = '42501'; end if;
  -- 가족 기기는 익명 사용자만(부모 계정이 기기로 겸하지 못하게)
  if public.sp_parent_family() is not null or not public.sp_is_anonymous() then
    return jsonb_build_object('result', 'bad_request');
  end if;
  -- 비밀번호는 숫자 4자리만. NULL·빈 값은 비교 전에 돌려보낸다(crypt(NULL)은 NULL)
  if p_password is null or p_password !~ '^[0-9]{4}$' then return jsonb_build_object('result', 'bad_request'); end if;
  if (p_member_id is null) = (p_new_name is null) then return jsonb_build_object('result', 'bad_request'); end if;

  select * into s from public.shares where code = p_code;
  if not found then return jsonb_build_object('result', 'not_found'); end if;
  -- 한 사람용 문자 링크만 잠근다(동시 사용 방지). 일반 링크는 잠그지 않아 여러 가족이 동시에 들어온다
  if s.target_member_id is not null then
    select * into s from public.shares where id = s.id for update;
  end if;
  if exists (select 1 from public.families where id = s.family_id and delete_after is not null) then
    return jsonb_build_object('result', 'closed');
  end if;
  v_new_open := s.created_at + interval '72 hours' > now() and s.used_at is null;

  -- 기기는 비밀번호가 맞거나 승인 대기로 넘어갈 때만 만든다(틀린 링크로 가족방에 묶이지 않게)
  select * into d from public.devices where auth_user_id = v_uid and family_id = s.family_id for update;
  if found then
    -- 승인 대기 화면이 '마지막으로 들어가려던 가족방'을 보여 주게
    update public.devices set last_seen_at = now() where id = d.id;
    if d.status = 'revoked' then return jsonb_build_object('result', 'revoked'); end if;
    if d.status = 'pending' then return jsonb_build_object('result', 'needs_approval'); end if;
  end if;

  if p_member_id is not null then
    select * into m from public.members
      where id = p_member_id and family_id = s.family_id and status = 'active';
    if not found then return jsonb_build_object('result', 'bad_request'); end if;
    if s.target_member_id is not null and s.target_member_id <> m.id then
      return jsonb_build_object('result', 'bad_request');
    end if;
    if s.target_member_id is not null and (s.used_at is not null or s.created_at + interval '72 hours' <= now()) then
      return jsonb_build_object('result', 'expired');
    end if;
    -- 링크를 보낸 그룹의 이름만(외가 링크로 친가 비밀번호를 시도하지 못하게)
    if not exists (select 1 from public.share_groups where share_id = s.id and group_id = m.group_id) then
      return jsonb_build_object('result', 'bad_request');
    end if;
    v_group := m.group_id;
  else
    if not v_new_open or s.target_member_id is not null then return jsonb_build_object('result', 'expired'); end if;
    if not exists (select 1 from public.share_groups where share_id = s.id and group_id = p_group_id) then
      return jsonb_build_object('result', 'bad_request');
    end if;
    if char_length(v_name) not between 1 and 12 then return jsonb_build_object('result', 'bad_request'); end if;
    v_group := p_group_id;
  end if;

  select count(*), max(at) into v_dev_fail, v_last
    from public.entry_failures where auth_user_id = v_uid and group_id = v_group;
  if v_dev_fail > 0 and v_dev_fail % 3 = 0 and v_last > now() - interval '30 seconds' then
    return jsonb_build_object('result', 'locked',
      'retry_after', ceil(extract(epoch from v_last + interval '30 seconds' - now())));
  end if;
  select count(*) filter (where at > now() - interval '1 hour'), count(*)
    into v_group_fail, v_group_day
    from public.entry_failures where group_id = v_group and at > now() - interval '24 hours';
  -- 이미 이 이름으로 들어와 있던 기기인가(경보 중에도 이 기기는 막지 않는다)
  v_known := d.id is not null and p_member_id is not null and d.member_id = p_member_id;

  select * into g from public.groups where id = v_group;
  v_ok := extensions.crypt(p_password, g.password_hash) = g.password_hash;

  if not v_ok then
    insert into public.entry_failures (family_id, group_id, auth_user_id) values (s.family_id, v_group, v_uid);
    v_dev_fail := v_dev_fail + 1; v_group_fail := v_group_fail + 1; v_group_day := v_group_day + 1;
  end if;
  -- 그룹 경보: 1시간 20번 또는 하루 30번. 링크 유출 의심이라 새 기기·다른 이름은 맞아도 승인 대기
  v_alarm := v_group_fail >= 20 or v_group_day >= 30;

  if not v_ok and v_dev_fail < 10 and not (v_alarm and not v_known) then
    return jsonb_build_object('result', 'wrong_password', 'hint', g.password_hint, 'attempts', v_dev_fail);
  end if;

  if (not v_ok) or (v_alarm and not v_known) then
    -- 잠그지 않고 부모 승인 대기로. 구성원은 만들지 않고 기기에 들어가려던 이름만 적는다.
    -- 이미 있던 기기의 원래 구성원은 그대로 둔다
    if d.id is null then
      insert into public.devices (auth_user_id, family_id, status, requested_member_id, requested_group_id, requested_name)
        values (v_uid, s.family_id, 'pending', p_member_id, case when p_member_id is null then v_group end,
                case when p_member_id is null then v_name end);
    else
      update public.devices
        set status = 'pending', can_upload = false, last_seen_at = now(),
            requested_member_id = p_member_id,
            requested_group_id = case when p_member_id is null then v_group end,
            requested_name = case when p_member_id is null then v_name end
        where id = d.id;
    end if;
    return jsonb_build_object('result', 'needs_approval');
  end if;

  if p_member_id is null then
    -- 만료된 승인 대기·거절된 같은 이름은 비우고 다시 받는다(내보낸 사람의 반응·한마디 기록이 있으면 남기고 이름을 막는다)
    delete from public.members
      where group_id = v_group and display_name = v_name
        and ((status = 'rejected' and not public.sp_member_has_history(id)) or (status = 'pending' and pending_until <= now()));
    if exists (select 1 from public.members where group_id = v_group and display_name = v_name) then
      return jsonb_build_object('result', 'name_taken');
    end if;
    insert into public.members (family_id, group_id, display_name, status, pending_until, entry_share_id)
      values (s.family_id, v_group, v_name, 'pending', now() + interval '3 days', s.id)
      returning * into m;
  end if;

  -- 맞으면 이 그룹에서 틀린 기록만 지운다(다른 그룹 기록은 남겨서 번갈아 맞히며 초기화하는 걸 막는다)
  delete from public.entry_failures where auth_user_id = v_uid and group_id = v_group;
  if d.id is null then
    insert into public.devices (auth_user_id, family_id, member_id) values (v_uid, s.family_id, m.id);
  else
    update public.devices
      set member_id = m.id, last_seen_at = now(),
          -- 다른 구성원으로 바꿔 들어오면 올리기 권한은 다시 승인
          can_upload = case when member_id = m.id then can_upload else false end
      where id = d.id;
  end if;
  if s.target_member_id is not null then update public.shares set used_at = now() where id = s.id; end if;

  return jsonb_build_object('result', case when m.status = 'pending' then 'pending' else 'ok' end, 'member_id', m.id);
end $$;

-- 공유 묶음 + 짧은 링크 코드(8자). 부모 또는 올리기 권한 가족
create function public.sp_create_share(p_group_ids uuid[], p_media_ids uuid[] default '{}', p_target_member uuid default null)
returns text
language plpgsql security definer set search_path = ''
as $$
declare
  -- 가족방은 첫 그룹으로 정한다(기기가 여러 가족방에 있을 수 있어서). 나머지 그룹도 같은 가족방이어야 한다
  v_family uuid := (select g.family_id from public.groups g where g.id = p_group_ids[1]);
  v_alpha constant text := 'ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz23456789';
  v_code text; v_id uuid; b bytea;
begin
  if v_family is null or not public.sp_can_upload(v_family) then
    raise exception 'not_allowed' using errcode = '42501';
  end if;
  if coalesce(array_length(p_group_ids, 1), 0) = 0
     or exists (select 1 from unnest(p_group_ids) x where x not in (select id from public.groups where family_id = v_family))
     or exists (select 1 from unnest(p_media_ids) x where x not in (select id from public.media where family_id = v_family))
     or (p_target_member is not null and not exists (
           select 1 from public.members where id = p_target_member and family_id = v_family and group_id = any (p_group_ids)))
  then
    raise exception 'bad_request' using errcode = '22023';
  end if;
  loop
    b := extensions.gen_random_bytes(8);
    select string_agg(substr(v_alpha, (get_byte(b, i) % length(v_alpha)) + 1, 1), '') into v_code
      from generate_series(0, 7) i;
    exit when not exists (select 1 from public.shares where code = v_code);
  end loop;
  insert into public.shares (family_id, code, target_member_id, cover_media_id) values (v_family, v_code, p_target_member, p_media_ids[1])
    returning id into v_id;
  insert into public.share_groups (family_id, share_id, group_id) select v_family, v_id, x from unnest(p_group_ids) x;
  insert into public.share_media (family_id, share_id, media_id) select v_family, v_id, x from unnest(p_media_ids) x;
  return v_code;
end $$;

-- 한마디 지우기: 쓴 사람 또는 그 가족방 부모
create function public.sp_delete_comment(p_comment_id uuid) returns void
language plpgsql security definer set search_path = ''
as $$
begin
  update public.comments c set deleted_at = now()
    where c.id = p_comment_id and c.deleted_at is null
      and (c.member_id in (select public.sp_device_members())
           or exists (select 1 from public.media x where x.id = c.media_id and x.family_id = public.sp_parent_family()));
  if not found then raise exception 'not_allowed' using errcode = '42501'; end if;
end $$;

-- 함수 실행 권한: 기본(public) 회수 후 로그인 사용자(익명 포함)에게만
revoke execute on all functions in schema public from public, anon, authenticated;
grant execute on function public.sp_parent_family(), public.sp_device_members(), public.sp_device_member(uuid),
  public.sp_device_active(uuid), public.sp_in_family(uuid), public.sp_media_member(uuid),
  public.sp_can_view_media(uuid), public.sp_can_upload(uuid), public.sp_is_anonymous(),
  public.sp_can_edit_media(uuid),
  public.sp_create_family(text, text, text, date, text, text), public.sp_set_group_password(uuid, text, text),
  public.sp_add_group(text, text, text, boolean), public.sp_entry_info(text),
  public.sp_enter(text, text, uuid, text, uuid), public.sp_create_share(uuid[], uuid[], uuid),
  public.sp_delete_comment(uuid)
  to authenticated;
-- 앞으로 만드는 함수도 anon에 열리지 않게(Supabase 기본 권한은 anon에도 실행을 준다)
alter default privileges in schema public revoke execute on functions from public, anon, authenticated;
