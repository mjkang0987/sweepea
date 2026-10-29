-- 공동 관리자(100): 가족방당 엄빠 둘까지. 가족방 하나에 엄빠 한 명이던 unique를 푼다(둘까지는 함수에서 확인).
-- drop이 들어 있어 운영 적용 도구가 막으므로 이 파일은 Supabase SQL 편집기에서 직접 실행한다
alter table public.parents drop constraint parents_family_id_key;
create index parents_family on public.parents (family_id);
