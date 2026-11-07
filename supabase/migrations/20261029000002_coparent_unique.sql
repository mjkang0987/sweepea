-- 공동 관리자(100): 가족방당 엄빠 둘까지. 가족방 하나에 엄빠 한 명이던 unique를 푼다(둘까지는 함수에서 확인).
-- drop이 들어 있어 운영 적용 도구가 막으므로 이 파일은 Supabase SQL 편집기에서 직접 실행한다(다시 실행해도 같은 결과)
alter table public.parents drop constraint if exists parents_family_id_key;
create index if not exists parents_family on public.parents (family_id);
-- 나간 엄빠의 행을 새 가족방으로 옮긴 뒤 그 가족방이 지워져도, 예전 가족방에 남긴 반응·한마디(parents를 cascade로 참조)가 같이 지워지지 않게
-- 가족방이 지워지면 엄빠 행의 family_id만 비운다(기록 없는 행은 sp_purge_family가 먼저 지움)
alter table public.parents alter column family_id drop not null;
alter table public.parents drop constraint if exists parents_family_id_fkey;
alter table public.parents add constraint parents_family_id_fkey foreign key (family_id) references public.families (id) on delete set null;
