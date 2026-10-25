-- 권한 시나리오 검사. run.sh가 stub.sql + 마이그레이션 뒤에 실행한다.
-- 사용자 바꾸기: request.jwt.claims 설정 + set role authenticated. 시간 조작·준비 데이터는 postgres로.
\set ON_ERROR_STOP 1
\set P   '00000000-0000-0000-0000-0000000000a1'
\set P2  '00000000-0000-0000-0000-0000000000a2'
\set GM  '00000000-0000-0000-0000-0000000000b1'
\set GF  '00000000-0000-0000-0000-0000000000b2'
\set AU  '00000000-0000-0000-0000-0000000000b3'
\set X   '00000000-0000-0000-0000-0000000000b4'
\set NEW '00000000-0000-0000-0000-0000000000b5'
\set SP  '00000000-0000-0000-0000-0000000000b6'

insert into auth.users (id, is_anonymous) values
  (:'P', false), (:'P2', false), (:'GM', true), (:'GF', true), (:'AU', true), (:'X', true), (:'NEW', true), (:'SP', true);

create function pg_temp.ok(cond boolean, msg text) returns void language plpgsql as $$
begin if cond is not true then raise exception '실패: %', msg; end if; end $$;

-- ── 부모: 가족방 만들기, 그룹, 가족 이름 등록, 사진
select set_config('request.jwt.claims', json_build_object('sub', :'P', 'is_anonymous', false)::text, false);
set role authenticated;
select public.sp_create_family('mom', '지우', '하린', '2025-09-17', '0917', '하린이 생일') as fam \gset
select public.sp_add_group('외가', '1234', '외가 비밀번호') as gma \gset
select public.sp_add_group('친가', '5678') as gpa \gset
select pg_temp.ok((select groups_enabled from public.families) , '그룹 추가하면 그룹 켜짐');
select pg_temp.ok(public.sp_parent_home() @> '{"role": "mom", "children": [{"name": "하린"}], "download_allowed": false, "photo_count": 0}', '부모 첫 화면 정보');
insert into public.members (family_id, group_id, display_name) values
  (:'fam', :'gma', '외할머니'), (:'fam', :'gma', '외할아버지'), (:'fam', :'gma', '하린 아빠'), (:'fam', :'gpa', '할머니');
select id as m_gm from public.members where display_name = '외할머니' \gset
select id as m_gf from public.members where display_name = '외할아버지' \gset
select id as m_sp from public.members where display_name = '하린 아빠' \gset
select public.sp_create_media(:'fam', 'photo', now(), 'exif', null, null, null, array[:'gma']::uuid[]) as m1 \gset
select public.sp_create_media(:'fam', 'photo', now(), 'exif', null, null, null, array[:'gpa']::uuid[]) as m2 \gset
select public.sp_create_media(:'fam', 'video', now(), 'file', null, null, null, array[:'gma', :'gpa']::uuid[]) as m3 \gset
select public.sp_create_media(:'fam', 'photo', now(), 'exif', null, null, null, array[:'gma']::uuid[]) as m4 \gset
select public.sp_create_media(:'fam', 'photo', now(), 'exif', null, null, null, array[:'gma']::uuid[]) as m5 \gset
reset role;
-- 처리 완료 표시는 서버(postgres)만. m4는 올리는 중으로 둔다
update public.media set status = 'ready' where id in (:'m1', :'m2', :'m3', :'m5');
set role authenticated;
select public.sp_create_share(array[:'gma']::uuid[], array[:'m1', :'m3']::uuid[]) as code1 \gset
select public.sp_create_share(array[:'gpa']::uuid[], array[:'m2']::uuid[]) as code_pa \gset
select pg_temp.ok((select count(*) = 5 from public.media), '부모는 자기 가족방 사진 5장 모두');
reset role;

-- ── 외할머니: 이름 고르기 + 비밀번호 3번 틀림 → 30초 쉬기
select set_config('request.jwt.claims', json_build_object('sub', :'GM', 'is_anonymous', true)::text, false);
set role authenticated;
select pg_temp.ok(public.sp_entry_info(:'code1') ->> 'result' = 'ok', '입장 정보');
select pg_temp.ok(jsonb_array_length(public.sp_entry_info(:'code1') -> 'groups' -> 0 -> 'members') = 3, '외가 이름 3개');
select pg_temp.ok(public.sp_enter(:'code1', '0000', :'m_gm') ->> 'result' = 'wrong_password', '1번 틀림');
select pg_temp.ok(public.sp_enter(:'code1', '0000', :'m_gm') ->> 'hint' = '외가 비밀번호', '틀리면 힌트');
select pg_temp.ok(public.sp_enter(:'code1', '0000', :'m_gm') ->> 'result' = 'wrong_password', '3번 틀림');
select pg_temp.ok(public.sp_enter(:'code1', '1234', :'m_gm') ->> 'result' = 'locked', '3번 틀리면 맞아도 쉬는 중');
reset role;
update public.entry_failures set at = at - interval '31 seconds' where auth_user_id = :'GM';
set role authenticated;
select pg_temp.ok(public.sp_enter(:'code1', '1234', :'m_gm') ->> 'result' = 'ok', '쉬고 나서 맞으면 입장');
reset role;
select pg_temp.ok((select count(*) = 0 from public.entry_failures where auth_user_id = :'GM'), '맞으면 이 그룹 틀린 기록 지움');
set role authenticated;
select pg_temp.ok((select count(*) = 3 from public.media), '외할머니는 외가 사진 3장(올리는 중 제외)');
select pg_temp.ok(not exists (select 1 from public.media where id = :'m2'), '친가 전용 사진은 안 보임');
select public.sp_react(:'m1', 'heart', true), public.sp_react(:'m1', 'sparkle', true);
select public.sp_comment(:'m1', '아이고 많이 컸네');
update public.members set text_size = 'large' where id = :'m_gm';
reset role;

-- 권한 밖 동작은 에러가 나야 한다
\set ON_ERROR_STOP 0
set role authenticated;
\echo '아래 에러 3줄은 의도된 거부'
select public.sp_react(:'m2', 'heart', true);
select password_hash from public.groups;
update public.members set display_name = '왕할머니' where id = :'m_gm';
reset role;
\set ON_ERROR_STOP 1
select pg_temp.ok((select count(*) = 2 from public.reactions), '거부된 반응은 안 들어감');
select pg_temp.ok((select display_name = '외할머니' and text_size = 'large' from public.members where id = :'m_gm'), '글자 크기만 바뀜');

-- ── 큰이모: 새 이름 → 승인 대기, 받은 공유 묶음만
select set_config('request.jwt.claims', json_build_object('sub', :'AU', 'is_anonymous', true)::text, false);
set role authenticated;
select public.sp_enter(:'code1', '1234', null, '큰이모', :'gma') ->> 'result' as r \gset
select pg_temp.ok(:'r' = 'pending', '새 이름은 승인 대기');
select pg_temp.ok((select count(*) = 2 from public.media), '승인 전엔 공유 묶음 2장만');
\set ON_ERROR_STOP 0
\echo '아래 에러 1줄은 의도된 거부(승인 대기는 반응 못 함)'
select public.sp_react(:'m1', 'heart', true);
\set ON_ERROR_STOP 1
select pg_temp.ok((select count(*) = 1 from public.members), '승인 전엔 가족 명단 대신 자기 이름만');
select pg_temp.ok(not exists (select 1 from public.media where id = :'m5'), '공유 안 한 외가 사진은 안 보임');
reset role;

select set_config('request.jwt.claims', json_build_object('sub', :'P', 'is_anonymous', false)::text, false);
set role authenticated;
update public.members set status = 'active', pending_until = null where display_name = '큰이모';
reset role;
select set_config('request.jwt.claims', json_build_object('sub', :'AU', 'is_anonymous', true)::text, false);
set role authenticated;
select pg_temp.ok((select count(*) = 3 from public.media), '승인 뒤 외가 사진 전부');
reset role;

-- 승인 대기 3일이 지나면 아무것도 못 본다
update public.members set status = 'pending', pending_until = now() - interval '1 minute' where display_name = '큰이모';
set role authenticated;
select pg_temp.ok((select count(*) = 0 from public.media), '만료된 승인 대기는 0장');
reset role;

-- ── 모르는 사람: 새 이름으로 10번 틀리면 잠그지 않고 승인 대기
select set_config('request.jwt.claims', json_build_object('sub', :'X', 'is_anonymous', true)::text, false);
set role authenticated;
select pg_temp.ok(public.sp_enter(:'code1', '9999', null, '모르는사람', :'gma') ->> 'result' = 'wrong_password', '모르는 사람 1번 틀림');
reset role;
insert into public.entry_failures (family_id, group_id, auth_user_id, at) select :'fam', :'gma', :'X', now() from generate_series(1, 8);
-- 그룹 전체 1시간 한도와 30초 쉬기에 안 걸리게 두 시간 전 기록으로 돌린다
update public.entry_failures set at = now() - interval '2 hours' where auth_user_id = :'X';
set role authenticated;
select pg_temp.ok(public.sp_enter(:'code1', '9999', null, '모르는사람', :'gma') ->> 'result' = 'needs_approval', '10번 틀리면 승인 대기');
select pg_temp.ok(public.sp_enter(:'code1', '1234', null, '모르는사람', :'gma') ->> 'result' = 'needs_approval', '그 뒤엔 맞아도 승인 대기');
select pg_temp.ok((select count(*) = 0 from public.media), '승인 대기 기기는 0장');
reset role;
select set_config('request.jwt.claims', json_build_object('sub', :'P', 'is_anonymous', false)::text, false);
set role authenticated;
select pg_temp.ok((select status = 'pending' from public.devices where requested_name = '모르는사람'), '부모 화면에 승인 대기 기기와 들어가려던 이름이 보임');
select pg_temp.ok(not exists (select 1 from public.members where display_name = '모르는사람'), '틀린 시도로는 구성원이 생기지 않음(이름 선점 방지)');
update public.devices set status = 'revoked' where requested_name = '모르는사람';
reset role;
select set_config('request.jwt.claims', json_build_object('sub', :'X', 'is_anonymous', true)::text, false);
set role authenticated;
select pg_temp.ok(public.sp_enter(:'code1', '1234', :'m_gf') ->> 'result' = 'revoked', '내 가족 아님 처리된 기기는 못 들어옴');
reset role;

-- ── 링크 72시간이 지나면: 새 이름은 막고, 등록된 이름은 비밀번호로 다시 들어온다
update public.shares set created_at = now() - interval '73 hours' where code = :'code1';
select set_config('request.jwt.claims', json_build_object('sub', :'NEW', 'is_anonymous', true)::text, false);
set role authenticated;
select pg_temp.ok((public.sp_entry_info(:'code1') ->> 'new_entry_open')::boolean = false, '새 입장 닫힘 표시');
select pg_temp.ok(public.sp_enter(:'code1', '1234', null, '사촌', :'gma') ->> 'result' = 'expired', '기간 지난 링크로 새 이름 불가');
reset role;
select set_config('request.jwt.claims', json_build_object('sub', :'GF', 'is_anonymous', true)::text, false);
set role authenticated;
select pg_temp.ok(public.sp_enter(:'code1', '1234', :'m_gf') ->> 'result' = 'ok', '등록된 이름은 기간 지나도 다시 들어옴');
reset role;
select set_config('request.jwt.claims', json_build_object('sub', :'GM', 'is_anonymous', true)::text, false);
set role authenticated;
select pg_temp.ok((select count(*) = 3 from public.media), '이미 들어온 기기는 계속 봄');
reset role;

-- ── 하린 아빠: 이름 고르기 → 외가만 → 올리기 권한 받으면 전부 보고 올림
select set_config('request.jwt.claims', json_build_object('sub', :'P', 'is_anonymous', false)::text, false);
set role authenticated;
select public.sp_create_share(array[:'gma']::uuid[], '{}'::uuid[], :'m_sp') as code_sms \gset
reset role;
select set_config('request.jwt.claims', json_build_object('sub', :'SP', 'is_anonymous', true)::text, false);
set role authenticated;
select pg_temp.ok(public.sp_enter(:'code_sms', '1234', :'m_sp') ->> 'result' = 'ok', '문자 링크로 입장');
select pg_temp.ok((select count(*) = 3 from public.media), '권한 전엔 외가 사진만');
reset role;
\set ON_ERROR_STOP 0
set role authenticated;
\echo '아래 에러 2줄은 의도된 거부'
insert into public.media (family_id, uploaded_by_member, kind, taken_at, taken_at_source) values (:'fam', :'m_sp', 'photo', now(), 'exif');
select public.sp_create_share(array[:'gma']::uuid[]);
reset role;
\set ON_ERROR_STOP 1
select set_config('request.jwt.claims', json_build_object('sub', :'NEW', 'is_anonymous', true)::text, false);
set role authenticated;
select pg_temp.ok(public.sp_enter(:'code_sms', '1234', :'m_sp') ->> 'result' = 'expired', '문자 링크는 한 번만');
select pg_temp.ok(public.sp_enter(:'code_sms', '1234', null, '누군가', :'gma') ->> 'result' = 'expired', '쓴 문자 링크로 새 이름 불가');
reset role;
select id as d_sp from public.devices where auth_user_id = :'SP' \gset
select set_config('request.jwt.claims', json_build_object('sub', :'P', 'is_anonymous', false)::text, false);
set role authenticated;
update public.devices set can_upload = true where id = :'d_sp';
reset role;
select set_config('request.jwt.claims', json_build_object('sub', :'SP', 'is_anonymous', true)::text, false);
set role authenticated;
select pg_temp.ok((select count(*) = 4 from public.media), '올리기 권한이면 모든 그룹 사진(올리는 중 제외)');
select public.sp_create_media(:'fam', 'photo', now(), 'exif', null, null, null, array[:'gpa']::uuid[]) as m6 \gset
reset role;
select pg_temp.ok((select uploaded_by_member = :'m_sp' and uploaded_by_parent is null from public.media where id = :'m6'), '가족 기기가 올리면 올린 사람은 그 구성원');
set role authenticated;
\set ON_ERROR_STOP 0
\echo '아래 에러 1줄은 의도된 거부(가족이 부모 사용자 id 열 읽기)'
select uploaded_by_parent from public.media;
\set ON_ERROR_STOP 1
select pg_temp.ok(public.sp_upload_target(:'m6') ->> 'kind' = 'photo', '가족 기기도 자기 사진에 파일을 넣을 수 있음');
select pg_temp.ok(length(public.sp_create_share(array[:'gpa']::uuid[], array[:'m6']::uuid[])) = 8, '올리기 권한 가족도 공유 링크 만듦');
reset role;
select id as d_gm from public.devices where auth_user_id = :'GM' \gset
\set ON_ERROR_STOP 0
set role authenticated;
-- 자기 기기 수정 정책이 없어서 에러 없이 0행으로 끝난다
update public.devices set can_upload = true, status = 'active' where id = :'d_gm';
reset role;
\set ON_ERROR_STOP 1
select pg_temp.ok((select not can_upload from public.devices where auth_user_id = :'GM'), '가족은 스스로 권한을 못 줌');

-- ── 검토에서 나온 구멍들
\set N1 '00000000-0000-0000-0000-0000000000c1'
\set N2 '00000000-0000-0000-0000-0000000000c2'
insert into auth.users (id, is_anonymous) values (:'N1', true), (:'N2', true);

-- 비밀번호 NULL·형식 틀림은 비교 없이 거절
select set_config('request.jwt.claims', json_build_object('sub', :'N1', 'is_anonymous', true)::text, false);
set role authenticated;
select pg_temp.ok(public.sp_enter(:'code1', null, :'m_gm') ->> 'result' = 'bad_request', 'NULL 비밀번호 거절');
select pg_temp.ok(public.sp_enter(:'code1', '', :'m_gm') ->> 'result' = 'bad_request', '빈 비밀번호 거절');
select pg_temp.ok(not exists (select 1 from public.devices), '거절된 시도로 기기가 생기지 않음');
reset role;

-- 다른 그룹 비밀번호를 번갈아 맞히며 횟수를 초기화하지 못한다
select set_config('request.jwt.claims', json_build_object('sub', :'GM', 'is_anonymous', true)::text, false);
select id as m_pgm from public.members where display_name = '할머니' \gset
set role authenticated;
select pg_temp.ok(public.sp_enter(:'code1', '0000', :'m_pgm') ->> 'result' = 'bad_request', '외가 링크로 친가 이름은 시도 불가');
select pg_temp.ok(public.sp_enter(:'code_pa', '0000', :'m_pgm') ->> 'result' = 'wrong_password', '친가 이름으로 틀림');
select pg_temp.ok(public.sp_enter(:'code_pa', '0001', :'m_pgm') ->> 'result' = 'wrong_password', '친가 이름으로 또 틀림');
select pg_temp.ok(public.sp_enter(:'code1', '1234', :'m_gm') ->> 'result' = 'ok', '자기 그룹은 맞음');
reset role;
select pg_temp.ok((select count(*) = 2 from public.entry_failures where auth_user_id = :'GM' and group_id = :'gpa'), '친가 틀린 기록은 그대로');

-- 그룹 전체가 1시간에 20번 틀리면, 비밀번호가 맞아도 새 기기는 승인 대기
insert into public.entry_failures (family_id, group_id, auth_user_id) select :'fam', :'gpa', gen_random_uuid() from generate_series(1, 18);
select set_config('request.jwt.claims', json_build_object('sub', :'N2', 'is_anonymous', true)::text, false);
set role authenticated;
select pg_temp.ok(public.sp_enter(:'code_pa', '5678', :'m_pgm') ->> 'result' = 'needs_approval', '익명 사용자 갈아타기 공격은 승인 대기로');
select pg_temp.ok((select count(*) = 0 from public.media), '승인 전엔 0장');
reset role;
select id as d_n2 from public.devices where auth_user_id = :'N2' \gset
select set_config('request.jwt.claims', json_build_object('sub', :'P', 'is_anonymous', false)::text, false);
set role authenticated;
update public.devices set status = 'active' where id = :'d_n2';
reset role;
select set_config('request.jwt.claims', json_build_object('sub', :'N2', 'is_anonymous', true)::text, false);
set role authenticated;
select pg_temp.ok((select count(*) = 2 from public.media), '부모가 승인하면 들어가려던 이름(할머니)으로 친가 사진');
select pg_temp.ok(public.sp_enter(:'code_pa', '0002', :'m_pgm') ->> 'result' = 'wrong_password', '경보 중에도 원래 기기의 오타는 그냥 틀림');
select pg_temp.ok((select status = 'active' from public.devices), '오타로 승인 대기로 떨어지지 않음');
reset role;

-- 한마디: 고치면 시각 남김, 지우기는 함수로(본인·부모)
select set_config('request.jwt.claims', json_build_object('sub', :'GM', 'is_anonymous', true)::text, false);
set role authenticated;
select id as c1 from public.comments limit 1 \gset
update public.comments set body = '아이고 많이 컸네!' where id = :'c1';
select pg_temp.ok((select edited_at is not null from public.comments where id = :'c1'), '고친 시각');
select public.sp_comment(:'m3', '영상 좋다') as c2 \gset
select public.sp_delete_comment(:'c1');
select pg_temp.ok(not exists (select 1 from public.comments where id = :'c1'), '본인이 지우면 안 보임');
reset role;
select set_config('request.jwt.claims', json_build_object('sub', :'P', 'is_anonymous', false)::text, false);
set role authenticated;
select public.sp_delete_comment(:'c2');
reset role;
select pg_temp.ok((select deleted_at is not null from public.comments where id = :'c2'), '부모가 지움');

-- 거절하면 그 기기도 막힌다
select set_config('request.jwt.claims', json_build_object('sub', :'P', 'is_anonymous', false)::text, false);
-- 내보내기 전 큰이모가 올리기 허용·반응 기록을 가졌다고 둔다
update public.devices set can_upload = true where auth_user_id = :'AU' and family_id = :'fam';
insert into public.reactions (media_id, member_id, kind) select :'m1', id, 'heart' from public.members where display_name = '큰이모';
set role authenticated;
update public.members set status = 'rejected' where display_name = '큰이모';
reset role;
select pg_temp.ok((select status = 'revoked' and not can_upload from public.devices where auth_user_id = :'AU' and family_id = :'fam'), '내보내면 기기 막힘·올리기 허용 꺼짐');
select set_config('request.jwt.claims', json_build_object('sub', :'AU', 'is_anonymous', true)::text, false);
set role authenticated;
select pg_temp.ok(public.sp_enter(:'code1', '1234', null, '큰이모', :'gma') ->> 'result' = 'revoked', '거절된 기기는 같은 이름으로 다시 못 들어옴');
reset role;
-- 다른 휴대폰으로 같은 이름을 다시 써도 내보낸 사람의 기록은 지우지 않는다
\set N6 '00000000-0000-0000-0000-0000000000c6'
insert into auth.users (id, is_anonymous) values (:'N6', true);
select set_config('request.jwt.claims', json_build_object('sub', :'P', 'is_anonymous', false)::text, false);
set role authenticated;
select public.sp_create_share(array[:'gma']::uuid[], '{}'::uuid[]) as code_k \gset
reset role;
select set_config('request.jwt.claims', json_build_object('sub', :'N6', 'is_anonymous', true)::text, false);
set role authenticated;
select pg_temp.ok(public.sp_enter(:'code_k', '1234', null, '큰이모', :'gma') ->> 'result' = 'name_taken', '기록 있는 내보낸 이름은 다시 못 씀');
reset role;
select pg_temp.ok((select count(*) = 1 from public.reactions r join public.members m on m.id = r.member_id where m.display_name = '큰이모'), '내보낸 사람의 반응 기록은 남음');
-- 부모 계정은 기기로 들어오지 못한다
select set_config('request.jwt.claims', json_build_object('sub', :'P2', 'is_anonymous', false)::text, false);
set role authenticated;
select pg_temp.ok(public.sp_enter(:'code1', '1234', :'m_gm') ->> 'result' = 'bad_request', '익명이 아닌 사용자는 입장 함수 불가');
reset role;

-- 권한 밖 동작
select set_config('request.jwt.claims', json_build_object('sub', :'P2', 'is_anonymous', false)::text, false);
set role authenticated;
select public.sp_create_family('dad', '다른집', '아이', '2025-01-01', '1111') as fam2 \gset
select public.sp_create_media(:'fam2', 'photo', now(), 'exif') as mx \gset
reset role;
select set_config('request.jwt.claims', json_build_object('sub', :'P', 'is_anonymous', false)::text, false);
set role authenticated;
update public.devices set can_upload = false where id = :'d_sp';
reset role;
\set ON_ERROR_STOP 0
\echo '아래 에러 8줄은 의도된 거부'
select set_config('request.jwt.claims', json_build_object('sub', :'GF', 'is_anonymous', true)::text, false);
set role authenticated;
select public.sp_delete_comment(:'c2');
reset role;
select set_config('request.jwt.claims', json_build_object('sub', :'SP', 'is_anonymous', true)::text, false);
set role authenticated;
insert into public.media (family_id, uploaded_by_member, kind, taken_at, taken_at_source, status) values (:'fam', :'m_sp', 'photo', now(), 'exif', 'ready');
insert into public.media_groups (family_id, media_id, group_id) values (:'fam', :'m6', :'gma');
reset role;
select set_config('request.jwt.claims', json_build_object('sub', :'P', 'is_anonymous', false)::text, false);
set role authenticated;
insert into public.shares (family_id, code, created_at) values (:'fam', 'AAAAAAAA', now() + interval '10 years');
update public.families set groups_enabled = false;
reset role;
select set_config('request.jwt.claims', json_build_object('sub', :'P2', 'is_anonymous', false)::text, false);
set role authenticated;
insert into public.media_groups (family_id, media_id, group_id) values (:'fam2', :'mx', :'gma');
reset role;
set role anon;
select public.sp_enter(:'code1', '1234', :'m_gm');
reset role;
set role anon;
select pg_temp.ok(public.sp_entry_info(:'code1') ->> 'result' = 'ok', 'anon(출입증 없는 첫 방문)도 입장 정보는 봄');
reset role;
select set_config('request.jwt.claims', json_build_object('sub', :'GM', 'is_anonymous', true)::text, false);
set role authenticated;
insert into public.comments (media_id, member_id, body, created_at) values (:'m1', :'m_gm', '옛날 글', now() - interval '1 year');
reset role;
\set ON_ERROR_STOP 1

-- ── 다른 가족방 부모는 아무것도 못 본다. 익명 기기는 가족방을 못 만든다
select set_config('request.jwt.claims', json_build_object('sub', :'P2', 'is_anonymous', false)::text, false);
set role authenticated;
select pg_temp.ok((select count(*) = 1 from public.media) and (select count(*) = 0 from public.members), '다른 가족방 사진은 안 보이고 자기 것 1장만');
reset role;
\set ON_ERROR_STOP 0
select set_config('request.jwt.claims', json_build_object('sub', :'NEW', 'is_anonymous', true)::text, false);
set role authenticated;
\echo '아래 에러 1줄은 의도된 거부'
select public.sp_create_family('dad', '익명', '아이', '2025-01-01', '1111');
reset role;
\set ON_ERROR_STOP 1
select pg_temp.ok((select count(*) = 2 from public.families), '가족방은 부모 둘이 만든 2개뿐');

-- ── 여러 가족방: 외할머니 기기 하나로 다른 가족방(P2네)에도 들어간다
select set_config('request.jwt.claims', json_build_object('sub', :'P2', 'is_anonymous', false)::text, false);
set role authenticated;
select id as g2 from public.groups where family_id = :'fam2' \gset
insert into public.members (family_id, group_id, display_name) values (:'fam2', :'g2', '할머니') returning id as m_h2 \gset
select public.sp_create_share(array[:'g2']::uuid[]) as code2 \gset
reset role;
update public.media set status = 'ready' where id = :'mx';
select set_config('request.jwt.claims', json_build_object('sub', :'GM', 'is_anonymous', true)::text, false);
set role authenticated;
select pg_temp.ok(public.sp_entry_info(:'code2') -> 'me' = 'null'::jsonb, '다른 가족방에선 처음 기기');
select pg_temp.ok(public.sp_entry_info(:'code1') -> 'me' @> '{"device": "active", "member": "active", "name": "외할머니"}', '들어간 가족방에선 내 상태가 보임');
select pg_temp.ok(public.sp_enter(:'code2', '1111', :'m_h2') ->> 'result' = 'ok', '같은 기기로 다른 가족방 입장');
select pg_temp.ok((select count(*) = 4 from public.media), '두 가족방 사진을 같이 봄(3 + 1)');
select pg_temp.ok(jsonb_array_length(public.sp_me() -> 'families') = 2, 'sp_me 가족방 2개');
select public.sp_react(:'mx', 'heart', true);
reset role;
select pg_temp.ok((select member_id = :'m_h2' from public.reactions where media_id = :'mx'), '다른 가족방 사진엔 그 가족방 이름(할머니)으로 반응');
select set_config('request.jwt.claims', json_build_object('sub', :'P2', 'is_anonymous', false)::text, false);
set role authenticated;
select pg_temp.ok((select count(*) = 1 from public.devices) and (select count(*) = 1 from public.members), 'P2는 자기 가족방 기기·이름만(외할머니의 다른 가족방은 모름)');
reset role;
\set ON_ERROR_STOP 0
set role authenticated;
\echo '아래 에러 1줄은 의도된 거부(부모가 기기 사용자 id를 읽어 다른 가족방과 맞춰 보기)'
select auth_user_id from public.devices;
reset role;
\set ON_ERROR_STOP 1
set role authenticated;
update public.devices set status = 'revoked' where family_id = :'fam2';
reset role;
select set_config('request.jwt.claims', json_build_object('sub', :'GM', 'is_anonymous', true)::text, false);
set role authenticated;
select pg_temp.ok((select count(*) = 3 from public.media), '한 가족방에서 막혀도 다른 가족방은 그대로');
select pg_temp.ok(public.sp_entry_info(:'code2') -> 'me' ->> 'device' = 'revoked', '막힌 가족방 링크에선 차단 상태');
reset role;

-- ── 사진 올리기: 행 만들기(부모) → 완료(서버) → 가족에게 보임
select set_config('request.jwt.claims', json_build_object('sub', :'P', 'is_anonymous', false)::text, false);
set role authenticated;
select public.sp_create_media(:'fam', 'photo', now(), 'exif', 4032, 3024) as u1 \gset
select pg_temp.ok(public.sp_upload_target(:'u1') ->> 'family_id' = :'fam', '올린 부모는 파일을 넣을 수 있음');
select pg_temp.ok((select count(*) = 3 from public.media_groups where media_id = :'u1'), '그룹을 안 고르면 기본 포함 그룹 전부');
reset role;
select set_config('request.jwt.claims', json_build_object('sub', :'GM', 'is_anonymous', true)::text, false);
set role authenticated;
select pg_temp.ok(public.sp_upload_target(:'u1') is null, '올린 사람이 아니면 파일을 못 넣음');
select pg_temp.ok(not exists (select 1 from public.media where id = :'u1'), '올리는 중인 사진은 가족에게 안 보임');
reset role;
set role service_role;
select pg_temp.ok(public.sp_finish_upload(:'u1', 'f/u1/view', 'f/u1/thumb', null, 1000), '서버가 완료 처리');
select pg_temp.ok(not public.sp_finish_upload(:'u1', 'f/u1/view', 'f/u1/thumb', null, 1000), '완료는 한 번만');
reset role;
select pg_temp.ok((select storage_used_bytes = 1000 from public.families where id = :'fam'), '가족방 사용량에 더함');
set role authenticated;
select pg_temp.ok(exists (select 1 from public.media where id = :'u1'), '완료되면 외할머니에게 보임');
select pg_temp.ok(public.sp_upload_target(:'u1') is null, '완료된 사진엔 파일을 더 못 넣음');
reset role;
\set ON_ERROR_STOP 0
\echo '아래 에러 3줄은 의도된 거부(권한 없는 올리기, 클라이언트 완료 처리, 다른 가족방 그룹)'
set role authenticated;
select public.sp_create_media(:'fam', 'photo', now(), 'exif');
select public.sp_finish_upload(:'u1', 'x', 'x', null, 0);
reset role;
select set_config('request.jwt.claims', json_build_object('sub', :'P', 'is_anonymous', false)::text, false);
set role authenticated;
select public.sp_create_media(:'fam', 'photo', now(), 'exif', null, null, null, array[:'g2']::uuid[]);
reset role;
\set ON_ERROR_STOP 1

-- ── 승인 대기 기기를 승인할 때 같은 이름이 이미 있으면 그 사람으로 붙인다
\set N3 '00000000-0000-0000-0000-0000000000c3'
insert into auth.users (id, is_anonymous) values (:'N3', true);
insert into public.devices (auth_user_id, family_id, status, requested_group_id, requested_name)
  values (:'N3', :'fam', 'pending', :'gma', '외할아버지') returning id as d_n3 \gset
select set_config('request.jwt.claims', json_build_object('sub', :'P', 'is_anonymous', false)::text, false);
set role authenticated;
update public.devices set status = 'active' where id = :'d_n3';
reset role;
select pg_temp.ok((select member_id = :'m_gf' from public.devices where id = :'d_n3'), '같은 이름이 있으면 그 구성원으로 승인(이름 중복 오류 없음)');
-- 같은 이름이 아직 승인 대기면 승인을 막고, 그 이름을 거절하면 요청한 대기 기기도 막힌다
\set N4 '00000000-0000-0000-0000-0000000000c4'
\set N5 '00000000-0000-0000-0000-0000000000c5'
insert into auth.users (id, is_anonymous) values (:'N4', true), (:'N5', true);
insert into public.members (family_id, group_id, display_name, status, pending_until) values (:'fam', :'gma', '작은이모', 'pending', now() + interval '1 day') returning id as m_small \gset
insert into public.devices (auth_user_id, family_id, status, requested_group_id, requested_name)
  values (:'N4', :'fam', 'pending', :'gma', '작은이모') returning id as d_n4 \gset
insert into public.devices (auth_user_id, family_id, status, requested_member_id)
  values (:'N5', :'fam', 'pending', :'m_gf') returning id as d_n5 \gset
select set_config('request.jwt.claims', json_build_object('sub', :'P', 'is_anonymous', false)::text, false);
set role authenticated;
\set ON_ERROR_STOP 0
\echo '아래 에러 1줄은 의도된 거부(같은 이름이 승인 대기 중인데 기기 승인)'
update public.devices set status = 'active' where id = :'d_n4';
\set ON_ERROR_STOP 1
update public.members set status = 'rejected' where id = :'m_gf';
reset role;
select pg_temp.ok((select status = 'revoked' from public.devices where id = :'d_n5'), '거절하면 그 이름을 요청한 대기 기기도 막힘');
select pg_temp.ok((select status = 'pending' from public.devices where id = :'d_n4'), '막힌 승인은 그대로 대기');
-- 거절한 외할아버지를 원래대로(뒤 검사용)
update public.members set status = 'active' where id = :'m_gf';
update public.devices set status = 'active' where member_id = :'m_gf';
-- 한 사람용 문자 링크는 72시간이 지나면 못 쓴다
set role authenticated;
select public.sp_create_share(array[:'gma']::uuid[], '{}'::uuid[], :'m_gf') as code_old \gset
reset role;
update public.shares set created_at = now() - interval '73 hours' where code = :'code_old';
select set_config('request.jwt.claims', json_build_object('sub', :'N1', 'is_anonymous', true)::text, false);
set role authenticated;
select pg_temp.ok(public.sp_enter(:'code_old', '1234', :'m_gf') ->> 'result' = 'expired', '오래된 문자 링크는 기간 지남');
reset role;

-- ── 반응·한마디(함수)
select set_config('request.jwt.claims', json_build_object('sub', :'GM', 'is_anonymous', true)::text, false);
set role authenticated;
select pg_temp.ok(public.sp_react(:'m3', 'best', true), '반응 켜기');
select pg_temp.ok(not public.sp_react(:'m3', 'best', false), '반응 끄기');
select public.sp_react(:'m3', 'heart', true);
select public.sp_react(:'m3', 'heart', true);
select pg_temp.ok((select n = 1 and mine from public.sp_reaction_counts(array[:'m3']::uuid[]) where kind = 'heart'), '같은 반응 두 번은 한 번');
select public.sp_comment(:'m3', '  예쁘다  ');
select pg_temp.ok((select body = '예쁘다' from public.comments where media_id = :'m3' order by created_at desc limit 1), '한마디 앞뒤 공백 정리');
select pg_temp.ok((select n >= 1 from public.sp_reaction_counts(array[:'m3']::uuid[]) where kind = 'comment'), '한마디 수');
select pg_temp.ok(not exists (select 1 from public.sp_reaction_counts(array[:'m2']::uuid[])), '안 보이는 사진 반응 수는 안 셈');
reset role;
select set_config('request.jwt.claims', json_build_object('sub', :'GF', 'is_anonymous', true)::text, false);
set role authenticated;
select pg_temp.ok(not exists (select 1 from public.comments where media_id = :'m3'), '다른 가족의 한마디 글은 안 보임');
select pg_temp.ok((select n >= 1 from public.sp_reaction_counts(array[:'m3']::uuid[]) where kind = 'comment'), '한마디 수는 보임');
reset role;
select set_config('request.jwt.claims', json_build_object('sub', :'GM', 'is_anonymous', true)::text, false);
\set ON_ERROR_STOP 0
\echo '아래 에러 3줄은 의도된 거부(안 보이는 사진 반응, 이상한 종류, 빈 한마디)'
set role authenticated;
select public.sp_react(:'m2', 'heart', true);
select public.sp_react(:'m3', 'angry', true);
select public.sp_comment(:'m3', '   ');
reset role;
\set ON_ERROR_STOP 1

-- ── 탈퇴 유예: 가족 화면은 바로 닫힘
select set_config('request.jwt.claims', json_build_object('sub', :'P', 'is_anonymous', false)::text, false);
set role authenticated;
update public.families set delete_after = now() + interval '3 days';
select pg_temp.ok((select count(*) = 7 from public.media), '부모는 유예 중에도 봄(되살리기)');
reset role;
select set_config('request.jwt.claims', json_build_object('sub', :'GM', 'is_anonymous', true)::text, false);
set role authenticated;
select pg_temp.ok((select count(*) = 0 from public.media), '가족은 바로 0장');
select pg_temp.ok(public.sp_entry_info(:'code1') ->> 'result' = 'closed', '앨범이 닫혔어요');
reset role;

-- ── sp_me: 가족 화면이 어디로 보낼지
select set_config('request.jwt.claims', json_build_object('sub', :'GM', 'is_anonymous', true)::text, false);
set role authenticated;
select pg_temp.ok(public.sp_me() -> 'families' @> '[{"device": "active", "member": "active", "name": "외할머니", "closed": true, "child_name": "하린"}]', 'sp_me 외할머니(앨범 닫힘)');
select pg_temp.ok(public.sp_me() -> 'families' @> '[{"device": "revoked", "name": "할머니", "closed": false}]', 'sp_me 다른 가족방은 따로');
reset role;
select set_config('request.jwt.claims', json_build_object('sub', :'X', 'is_anonymous', true)::text, false);
set role authenticated;
select pg_temp.ok(public.sp_me() -> 'families' @> '[{"device": "revoked", "name": "모르는사람"}]', 'sp_me 차단된 기기');
reset role;
select set_config('request.jwt.claims', json_build_object('sub', :'N1', 'is_anonymous', true)::text, false);
set role authenticated;
select pg_temp.ok(public.sp_me() = '{"families": []}', 'sp_me 처음 기기');
select pg_temp.ok(public.sp_parent_home() = '{"family_id": null}', '설정 전·기기 사용자는 가족방 없음');
reset role;

-- ── 사진 저장하기 켜기: 자기 가족방 부모만
select set_config('request.jwt.claims', json_build_object('sub', :'P2', 'is_anonymous', false)::text, false);
set role authenticated;
update public.families set download_allowed = true where id = :'fam';
reset role;
select pg_temp.ok((select not download_allowed from public.families where id = :'fam'), '다른 가족방 부모는 저장 허용을 못 바꿈');
select set_config('request.jwt.claims', json_build_object('sub', :'GM', 'is_anonymous', true)::text, false);
set role authenticated;
do $$ begin update public.families set download_allowed = true; exception when insufficient_privilege then null; end $$;
reset role;
select pg_temp.ok((select not download_allowed from public.families where id = :'fam'), '가족 기기는 저장 허용을 못 바꿈');
select set_config('request.jwt.claims', json_build_object('sub', :'P', 'is_anonymous', false)::text, false);
set role authenticated;
update public.families set download_allowed = true where id = :'fam';
select pg_temp.ok(public.sp_parent_home() @> '{"download_allowed": true}', '부모는 저장 허용을 켬');
reset role;

-- ── 아이·가족 화면 글자 크기·계정: 자기 가족방 부모만
select set_config('request.jwt.claims', json_build_object('sub', :'P', 'is_anonymous', false, 'app_metadata', json_build_object('provider', 'kakao'))::text, false);
set role authenticated;
insert into public.children (family_id, name, birth_date) values (:'fam', '도윤', '2026-08-30') returning id as ch2 \gset
update public.children set name = '도윤이' where id = :'ch2';
update public.families set text_size_mode = 'xlarge' where id = :'fam';
select pg_temp.ok(public.sp_parent_home() @> '{"provider": "kakao", "text_size_mode": "xlarge"}', '부모 계정 정보·글자 크기');
select pg_temp.ok(public.sp_parent_home() -> 'children' @> '[{"name": "도윤이"}]', '아이 추가·고치기');
reset role;
select set_config('request.jwt.claims', json_build_object('sub', :'P2', 'is_anonymous', false)::text, false);
set role authenticated;
update public.children set name = '남의아이' where id = :'ch2';
update public.families set text_size_mode = 'base' where id = :'fam';
\set ON_ERROR_STOP 0
\echo '아래 에러 1줄은 의도된 거부(다른 가족방에 아이 넣기)'
insert into public.children (family_id, name, birth_date) values (:'fam', '남의아이', '2026-01-01');
\set ON_ERROR_STOP 1
reset role;
select set_config('request.jwt.claims', json_build_object('sub', :'GM', 'is_anonymous', true)::text, false);
set role authenticated;
update public.children set name = '할머니가' where id = :'ch2';
\set ON_ERROR_STOP 0
\echo '아래 에러 1줄은 의도된 거부(가족 기기가 아이 넣기)'
insert into public.children (family_id, name, birth_date) values (:'fam', '할머니가', '2026-01-01');
\set ON_ERROR_STOP 1
reset role;
select pg_temp.ok((select name = '도윤이' from public.children where id = :'ch2'), '다른 가족방 부모·가족 기기는 아이를 못 바꿈');
select pg_temp.ok((select text_size_mode = 'xlarge' from public.families where id = :'fam'), '다른 가족방 부모는 글자 크기를 못 바꿈');
