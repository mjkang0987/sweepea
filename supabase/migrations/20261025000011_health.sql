-- 접종·검진 완료 기록. 부모만 보고 쓴다(가족 화면엔 안 보임). 일정 자체는 앱(src/lib/health.ts)이 가진다
create table public.health_done (
  family_id uuid not null,
  child_id uuid not null,
  item_key text not null check (item_key ~ '^[a-z0-9-]{2,20}$'),
  done_on date not null,
  primary key (child_id, item_key),
  foreign key (family_id, child_id) references public.children (family_id, id) on delete cascade
);
alter table public.health_done enable row level security;
create policy health_done_parent on public.health_done for all to authenticated
  using (family_id = public.sp_parent_family()) with check (family_id = public.sp_parent_family());
revoke all on public.health_done from anon;
revoke update, truncate, references, trigger on public.health_done from authenticated;
grant select, insert, delete on public.health_done to authenticated;
