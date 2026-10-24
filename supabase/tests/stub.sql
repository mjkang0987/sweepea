-- 로컬 검사용: Supabase가 미리 깔아 두는 것(auth 스키마, 역할, 기본 권한)을 흉내 낸다.
-- 실제 Supabase에는 적용하지 않는다.

create role anon nologin;
create role authenticated nologin;
create role service_role nologin bypassrls;

create schema auth;
create schema extensions;
grant usage on schema auth, extensions to anon, authenticated, service_role;

create table auth.users (id uuid primary key, is_anonymous boolean not null default false);

-- 검사에서는 request.jwt.claims(JSON)에 sub·is_anonymous를 넣어 사용자를 바꾼다
create function auth.jwt() returns jsonb language sql stable
as $$ select coalesce(nullif(current_setting('request.jwt.claims', true), ''), '{}')::jsonb $$;
create function auth.uid() returns uuid language sql stable
as $$ select nullif(auth.jwt() ->> 'sub', '')::uuid $$;
grant execute on function auth.jwt(), auth.uid() to anon, authenticated, service_role;

grant usage on schema public to anon, authenticated, service_role;
alter default privileges in schema public grant all on tables to anon, authenticated, service_role;
alter default privileges in schema public grant all on sequences to anon, authenticated, service_role;
alter default privileges in schema public grant execute on functions to anon, authenticated, service_role;
