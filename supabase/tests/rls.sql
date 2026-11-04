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
select pg_temp.ok(public.sp_parent_home() @> '{"role": "mom", "children": [{"name": "하린"}], "download_allowed": false, "photo_count": 0, "waiting": 0}', '부모 첫 화면 정보');
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
-- 보신 기록(20261029000001): 볼 수 있는 다 올라간 사진만, 같은 사진은 한 줄
select public.sp_note_views(array[:'m1', :'m2', :'m4', :'m1']::uuid[]);
select public.sp_note_views(array[:'m1']::uuid[]);
reset role;
-- 안 본 사진(20261101000002): 들어온 뒤 올라온 것만, 본 사진·못 보는 사진은 빠짐. m3를 외할머니가 들어온 뒤 올라온 것으로
update public.media set created_at = now() + interval '1 minute' where id = :'m3';
set role authenticated;
select pg_temp.ok(array(select public.sp_unseen_media(array[:'m1', :'m2', :'m3', :'m4']::uuid[])) = array[:'m3']::uuid[], '안 본 사진은 들어온 뒤 올라온 m3만(본 m1·친가 m2·올리는 중 m4 빠짐)');
select public.sp_note_views(array[:'m3']::uuid[]);
select pg_temp.ok(not exists (select 1 from public.sp_unseen_media(array[:'m3']::uuid[])), '보고 나면 안 본 사진에서 빠짐');
select public.sp_note_parent_views(array[:'m1']::uuid[]);
reset role;
select pg_temp.ok((select count(*) = 0 from public.parent_views), '가족 기기는 엄빠 본 기록을 못 남김');
delete from public.views where media_id = :'m3';

-- 권한 밖 동작은 에러가 나야 한다
\set ON_ERROR_STOP 0
set role authenticated;
\echo '아래 에러 4줄은 의도된 거부'
select public.sp_react(:'m2', 'heart', true);
select * from public.views;
select password_hash from public.groups;
update public.members set display_name = '왕할머니' where id = :'m_gm';
reset role;
\set ON_ERROR_STOP 1
select pg_temp.ok((select count(*) = 2 from public.reactions), '거부된 반응은 안 들어감');
select pg_temp.ok((select count(*) = 1 from public.views where media_id = :'m1' and member_id = :'m_gm') and (select count(*) = 1 from public.views), '본 기록은 볼 수 있는 사진 한 줄만');
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
select public.sp_note_views(array[:'m1']::uuid[]);
select pg_temp.ok((select count(*) = 1 from public.members), '승인 전엔 가족 명단 대신 자기 이름만');
select pg_temp.ok(not exists (select 1 from public.media where id = :'m5'), '공유 안 한 외가 사진은 안 보임');
\set ON_ERROR_STOP 0
\echo '아래 에러 1줄은 의도된 거부(승인 대기는 캐릭터 못 고름)'
select public.sp_set_member_avatar(:'fam', 3::smallint);
\set ON_ERROR_STOP 1
reset role;

select set_config('request.jwt.claims', json_build_object('sub', :'P', 'is_anonymous', false)::text, false);
set role authenticated;
update public.members set status = 'active', pending_until = null where display_name = '큰이모';
select pg_temp.ok(array(select name from public.sp_parent_media_viewers(:'m1')) = array['외할머니'], '엄빠는 본 사람 이름(승인 대기 때 본 건 안 남음)');
select public.sp_note_views(array[:'m1']::uuid[]);
reset role;
select pg_temp.ok((select count(*) = 1 from public.views), '엄빠가 본 건 안 셈');
-- 엄빠 안 본 사진(20261101000002): 내가 올린 사진은 빠짐, 본 기록은 엄빠 표에
set role authenticated;
select pg_temp.ok(not exists (select 1 from public.sp_unseen_media(array[:'m1', :'m3']::uuid[])), '엄빠가 올린 사진은 새 사진 아님');
select public.sp_note_parent_views(array[:'m1', :'m1']::uuid[]);
reset role;
select pg_temp.ok((select count(*) = 1 from public.parent_views where media_id = :'m1' and user_id = :'P'), '엄빠 본 기록 한 줄');
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
select pg_temp.ok((public.sp_parent_home() ->> 'waiting')::int = (select count(*) from public.devices where status = 'pending') + (select count(*) from public.members where status = 'pending' and pending_until > now()), '설정 탭 배지 수 = 승인 대기 휴대폰 + 기한 안 지난 신청');
select pg_temp.ok((public.sp_parent_home() ->> 'waiting')::int >= 1, '승인 대기 휴대폰이 배지에 셈');
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
-- 변경 기록(20261101000004): 가족 기기가 올리면 누가 = 그 구성원, 처음 그룹 그대로
select pg_temp.ok((select count(*) = 1 from public.media_changes where media_id = :'m6' and kind = 'create' and by_member = :'m_sp' and by_parent is null and group_ids = array[:'gpa']::uuid[]), '올리면 변경 기록 한 줄(가족 구성원)');
select pg_temp.ok(not has_table_privilege('authenticated', 'public.media_changes', 'select'), '변경 기록 표는 직접 못 읽음');
-- 엄빠 안 본 사진(20261101000002): 가족이 올린 사진은 엄빠에게 새 사진, 보고 나면 빠짐(잠깐 다 올라간 것으로)
update public.media set status = 'ready' where id = :'m6';
select set_config('request.jwt.claims', json_build_object('sub', :'P', 'is_anonymous', false)::text, false);
set role authenticated;
select pg_temp.ok(array(select public.sp_unseen_media(array[:'m6', :'m1']::uuid[])) = array[:'m6']::uuid[], '가족이 올린 사진은 엄빠에게 새 사진(엄빠가 올린 m1은 아님)');
select public.sp_note_parent_views(array[:'m6']::uuid[]);
select pg_temp.ok(not exists (select 1 from public.sp_unseen_media(array[:'m6']::uuid[])), '엄빠가 보고 나면 빠짐');
reset role;
delete from public.parent_views where media_id = :'m6';
update public.media set status = 'uploading' where id = :'m6';
select set_config('request.jwt.claims', json_build_object('sub', :'SP', 'is_anonymous', true)::text, false);
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

-- 한마디: 고치면 시각 남김, 지우기는 함수로(쓴 사람만, 2026-10-27부터 엄빠도 남의 것은 못 지움)
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
\set ON_ERROR_STOP 0
\echo '아래 에러 1줄은 의도된 거부(엄빠도 남의 한마디는 못 지움)'
select public.sp_delete_comment(:'c2');
\set ON_ERROR_STOP 1
reset role;
select pg_temp.ok((select deleted_at is null from public.comments where id = :'c2'), '엄빠는 가족 한마디를 못 지움');
select set_config('request.jwt.claims', json_build_object('sub', :'GM', 'is_anonymous', true)::text, false);
set role authenticated;
select public.sp_delete_comment(:'c2');
reset role;
select pg_temp.ok((select deleted_at is not null from public.comments where id = :'c2'), '쓴 사람은 지움');
-- 다른 가족(외할아버지)·다른 집 부모도 못 지움
select set_config('request.jwt.claims', json_build_object('sub', :'GM', 'is_anonymous', true)::text, false);
set role authenticated;
select public.sp_comment(:'m3', '외할머니 것') as c3 \gset
reset role;
\set ON_ERROR_STOP 0
\echo '아래 에러 2줄은 의도된 거부(남의 한마디)'
select set_config('request.jwt.claims', json_build_object('sub', :'GF', 'is_anonymous', true)::text, false);
set role authenticated;
select public.sp_delete_comment(:'c3');
reset role;
select set_config('request.jwt.claims', json_build_object('sub', :'P2', 'is_anonymous', false)::text, false);
set role authenticated;
select public.sp_delete_comment(:'c3');
select pg_temp.ok(not exists (select 1 from public.sp_parent_media_viewers(:'m1')), '다른 집 부모는 본 사람 못 봄');
select public.sp_note_views(array[:'m1']::uuid[]);
reset role;
\set ON_ERROR_STOP 1
select pg_temp.ok((select deleted_at is null from public.comments where id = :'c3'), '다른 가족·다른 집 부모는 못 지움');
select pg_temp.ok((select count(*) = 1 from public.views), '다른 집 부모는 본 기록을 못 남김');
delete from public.comments where id = :'c3';

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

-- ── 캐릭터(110): 각자 자기 것만. 가족 기기는 가족방마다 그 가족방의 자기 구성원(승인된 사람), 엄빠는 자기 행
select set_config('request.jwt.claims', json_build_object('sub', :'GM', 'is_anonymous', true)::text, false);
set role authenticated;
select public.sp_set_member_avatar(:'fam', 7::smallint);
select public.sp_set_member_avatar(:'fam2', 12::smallint);
select pg_temp.ok((select avatar = 7 from public.members where id = :'m_gm') and (select avatar = 12 from public.members where id = :'m_h2'), '가족방마다 내 구성원 캐릭터');
select pg_temp.ok((select avatar is null from public.members where id = :'m_gf'), '다른 구성원은 그대로');
select pg_temp.ok(public.sp_entry_info(:'code1') -> 'groups' -> 0 -> 'members' @> '[{"name": "외할머니", "avatar": 7}]', '누구세요 이름 목록에 캐릭터');
select pg_temp.ok(public.sp_me() -> 'families' @> '[{"name": "외할머니", "avatar": 7}, {"name": "할머니", "avatar": 12}]', 'sp_me 가족방마다 내 캐릭터');
select public.sp_set_member_avatar(:'fam', null);
select pg_temp.ok((select avatar is null from public.members where id = :'m_gm'), '고르지 않음으로 되돌림');
select public.sp_set_member_avatar(:'fam', 7::smallint);
reset role;
select set_config('request.jwt.claims', json_build_object('sub', :'P', 'is_anonymous', false)::text, false);
set role authenticated;
select public.sp_set_parent_avatar(5::smallint);
select pg_temp.ok((public.sp_parent_home() ->> 'avatar')::int = 5, '엄빠 내 캐릭터');
select pg_temp.ok((select avatar = 7 from public.members where id = :'m_gm'), '엄빠 설정 › 가족 목록에 가족 캐릭터');
reset role;
select pg_temp.ok((select avatar is null from public.parents where user_id = :'P2'), '다른 엄빠는 그대로');
\set ON_ERROR_STOP 0
\echo '아래 에러 9줄은 의도된 거부(캐릭터: 범위 밖 2, 남의 구성원 직접 고치기 2, 안 들어간 가족방, 엄빠가 가족 것, 가족이 엄빠 것, 엄빠 범위 밖, 기기 없는 사용자)'
select set_config('request.jwt.claims', json_build_object('sub', :'GM', 'is_anonymous', true)::text, false);
set role authenticated;
select public.sp_set_member_avatar(:'fam', 46::smallint);
select public.sp_set_member_avatar(:'fam', 0::smallint);
update public.members set avatar = 3 where id = :'m_gf';
reset role;
select set_config('request.jwt.claims', json_build_object('sub', :'P', 'is_anonymous', false)::text, false);
set role authenticated;
update public.members set avatar = 3 where id = :'m_gm';
reset role;
select set_config('request.jwt.claims', json_build_object('sub', :'GF', 'is_anonymous', true)::text, false);
set role authenticated;
select public.sp_set_member_avatar(:'fam2', 3::smallint);
reset role;
select set_config('request.jwt.claims', json_build_object('sub', :'P', 'is_anonymous', false)::text, false);
set role authenticated;
select public.sp_set_member_avatar(:'fam', 3::smallint);
reset role;
select set_config('request.jwt.claims', json_build_object('sub', :'GM', 'is_anonymous', true)::text, false);
set role authenticated;
select public.sp_set_parent_avatar(3::smallint);
reset role;
select set_config('request.jwt.claims', json_build_object('sub', :'P', 'is_anonymous', false)::text, false);
set role authenticated;
select public.sp_set_parent_avatar(46::smallint);
reset role;
select set_config('request.jwt.claims', json_build_object('sub', :'NEW', 'is_anonymous', true)::text, false);
set role authenticated;
select public.sp_set_member_avatar(:'fam', 3::smallint);
reset role;
\set ON_ERROR_STOP 1
select pg_temp.ok((select avatar = 7 from public.members where id = :'m_gm') and (select avatar is null from public.members where id = :'m_gf') and (select avatar = 5 from public.parents where user_id = :'P'), '거부된 캐릭터 바꾸기는 안 들어감');
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

-- ── 엄빠 반응·한마디(부모 계정)
select set_config('request.jwt.claims', json_build_object('sub', :'P', 'is_anonymous', false)::text, false);
set role authenticated;
select (public.sp_parent_home() ->> 'new_activity')::int as na0 \gset
select pg_temp.ok(public.sp_parent_react(:'m3', 'heart', true), '부모 반응 켜기');
select public.sp_parent_react(:'m3', 'heart', true);
select pg_temp.ok((select n = 2 and mine from public.sp_reaction_counts(array[:'m3']::uuid[]) where kind = 'heart'), '부모 하트는 한 번 + 가족 하트 = 2, 내가 누름');
select public.sp_parent_comment(:'m3', '  우리 딸 최고  ');
select pg_temp.ok((select body = '우리 딸 최고' and member_id is null from public.comments where parent_user_id = :'P'), '부모 한마디(공백 정리), 부모가 읽음');
select pg_temp.ok((public.sp_parent_home() ->> 'new_activity')::int = :na0, '내 반응·한마디는 새 반응 수에 안 셈');
-- 월별 대표(98a): 반응 많은 사진이 그 달 대표 1번, 달 사진 수, 안 보이는 사진은 가족 쪽 수에서 빠짐
reset role;
select to_char(taken_at at time zone 'Asia/Seoul', 'YYYY-MM') as ym3 from public.media where id = :'m3' \gset
select count(*) as all3 from public.media where status = 'ready' and family_id = (select family_id from public.media where id = :'m3') and to_char(taken_at at time zone 'Asia/Seoul', 'YYYY-MM') = :'ym3' \gset
set role authenticated;
select pg_temp.ok((select reps -> 0 ->> 'id' = :'m3' and n = :all3 and jsonb_array_length(reps) <= 3 from public.sp_media_months() where ym = :'ym3'), '엄빠 월별: 반응 많은 사진이 대표 1번, 달 사진 수 전부');
select pg_temp.ok((select jsonb_array_length(reps) = 1 from public.sp_media_months(null, null, 1) where ym = :'ym3'), '대표 장 수 지정');
reset role;
select count(*) as gma3 from public.media x where status = 'ready' and exists (select 1 from public.media_groups g where g.media_id = x.id and g.group_id = :'gma') \gset
set role authenticated;
select pg_temp.ok((select coalesce(sum(n), 0) from public.sp_media_months_f(null, null, 3, null, :'gma')) = :gma3 and :gma3 > 0, '엄빠 그룹(외가)만 달 카드 수');
reset role;
select set_config('request.jwt.claims', json_build_object('sub', :'GM', 'is_anonymous', true)::text, false);
set role authenticated;
select pg_temp.ok(coalesce((select sum(n) from public.sp_media_months()), 0) = (select count(*) from public.media where status = 'ready'), '가족 월별 수 = 볼 수 있는 사진 수');
select pg_temp.ok(not exists (select 1 from public.sp_media_months(), jsonb_array_elements(reps) e where e ->> 'id' = :'m2'), '안 보이는 사진은 대표에 없음');
-- 거르기 달 카드(20261102000001): 조건 없으면 sp_media_months와 같고, 영상만·그룹만이면 그 사진만 셈
select pg_temp.ok((select coalesce(sum(n), 0) from public.sp_media_months_f()) = (select coalesce(sum(n), 0) from public.sp_media_months()), '거르기 없는 달 카드 = 기존 달 카드');
select pg_temp.ok((select coalesce(sum(n), 0) from public.sp_media_months_f(null, null, 3, 'video')) = (select count(*) from public.media where status = 'ready' and kind = 'video'), '영상만 달 카드 수');
reset role;
select set_config('request.jwt.claims', json_build_object('sub', :'P', 'is_anonymous', false)::text, false);
set role authenticated;
select pg_temp.ok(not exists (select 1 from jsonb_array_elements(public.sp_parent_activity() -> 'items') i where i ->> 'body' = '우리 딸 최고'), '최근 반응 목록에 내 것은 없음');
reset role;
select set_config('request.jwt.claims', json_build_object('sub', :'GM', 'is_anonymous', true)::text, false);
set role authenticated;
select pg_temp.ok((select n = 2 and mine from public.sp_reaction_counts(array[:'m3']::uuid[]) where kind = 'heart'), '가족 화면에 부모 하트도 셈(내 것은 내 것만)');
select pg_temp.ok(not exists (select 1 from public.comments where parent_user_id is not null), '가족은 부모 한마디 글을 못 읽음(수만)');
select pg_temp.ok((select count(*) = 1 from public.reactions where media_id = :'m3' and kind = 'heart' and member_id is null), '가족도 부모 반응 행은 보임(누군지는 모름)');
\set ON_ERROR_STOP 0
\echo '아래 에러 2줄은 의도된 거부(가족이 부모 반응 함수 부름, 부모 사용자 id 읽기)'
select public.sp_parent_react(:'m3', 'best', true);
select parent_user_id from public.reactions;
\set ON_ERROR_STOP 1
reset role;
select set_config('request.jwt.claims', json_build_object('sub', :'P2', 'is_anonymous', false)::text, false);
\set ON_ERROR_STOP 0
\echo '아래 에러 2줄은 의도된 거부(다른 집 부모가 반응·한마디)'
set role authenticated;
select public.sp_parent_react(:'m3', 'best', true);
select public.sp_parent_comment(:'m3', '남의 집');
reset role;
\set ON_ERROR_STOP 1
select set_config('request.jwt.claims', json_build_object('sub', :'P', 'is_anonymous', false)::text, false);
\set ON_ERROR_STOP 0
\echo '아래 에러 4줄은 의도된 거부(올리는 중 사진, 이상한 종류, 빈 한마디, 직접 넣기)'
set role authenticated;
select public.sp_parent_react(:'m4', 'heart', true);
select public.sp_parent_react(:'m3', 'angry', true);
select public.sp_parent_comment(:'m3', '   ');
insert into public.reactions (media_id, parent_user_id, kind) values (:'m3', :'P', 'best');
reset role;
\set ON_ERROR_STOP 1
set role authenticated;
select pg_temp.ok(not public.sp_parent_react(:'m3', 'heart', false), '부모 반응 끄기');
select pg_temp.ok((select n = 1 and not mine from public.sp_reaction_counts(array[:'m3']::uuid[]) where kind = 'heart'), '끄면 가족 하트만 남음');
select id as pc from public.comments where parent_user_id = :'P' \gset
select public.sp_delete_comment(:'pc');
select pg_temp.ok(not exists (select 1 from public.comments where parent_user_id = :'P'), '부모가 자기 한마디 지움');
reset role;
-- 하루 30개 한도(지운 것도 셈: 지운 1개 + 28개를 미리 넣고 30번째는 되고 31번째는 막힘)
insert into public.comments (media_id, parent_user_id, body) select :'m3', :'P', '하나' from generate_series(1, 28);
set role authenticated;
select public.sp_parent_comment(:'m3', '서른');
\set ON_ERROR_STOP 0
\echo '아래 에러 1줄은 의도된 거부(부모 한마디 하루 30개 넘음)'
select public.sp_parent_comment(:'m3', '서른하나');
\set ON_ERROR_STOP 1
reset role;
delete from public.comments where parent_user_id = :'P';
-- 탈퇴 유예 중엔 반응 못 함
update public.families set delete_after = now() + interval '3 days' where id = :'fam';
set role authenticated;
\set ON_ERROR_STOP 0
\echo '아래 에러 1줄은 의도된 거부(탈퇴 유예 중 부모 반응)'
select public.sp_parent_react(:'m3', 'heart', true);
\set ON_ERROR_STOP 1
reset role;
update public.families set delete_after = null where id = :'fam';

-- ── 한마디 목록(크게 보기): 볼 수 있는 사진이면 승인된 가족·엄빠 한마디를 본다
select set_config('request.jwt.claims', json_build_object('sub', :'P', 'is_anonymous', false)::text, false);
set role authenticated;
select public.sp_parent_comment(:'m3', '엄마 한마디');
reset role;
select set_config('request.jwt.claims', json_build_object('sub', :'GF', 'is_anonymous', true)::text, false);
set role authenticated;
select pg_temp.ok((select count(*) >= 2 from public.sp_comment_list(:'m3')), '가족도 한마디 목록을 봄(외할머니 + 엄마)');
select pg_temp.ok((select name = '지우' and not mine from public.sp_comment_list(:'m3') where body = '엄마 한마디'), '엄마 한마디는 엄마 이름, 내 것 아님');
select pg_temp.ok(not exists (select 1 from public.sp_comment_list(:'m2')), '안 보이는 사진 한마디는 없음');
reset role;
select set_config('request.jwt.claims', json_build_object('sub', :'P', 'is_anonymous', false)::text, false);
set role authenticated;
select pg_temp.ok((select mine from public.sp_comment_list(:'m3') where body = '엄마 한마디'), '엄마가 보면 내 것');
select pg_temp.ok((select bool_and(id is not null) from public.sp_comment_list(:'m3')), '목록에 지울 때 쓸 id');
select pg_temp.ok((select avatar = 5 from public.sp_comment_list2(:'m3') where body = '엄마 한마디'), '한마디 목록2: 엄빠 캐릭터');
select pg_temp.ok((select avatar = 7 from public.sp_comment_list2(:'m3') where name = '외할머니'), '한마디 목록2: 가족 캐릭터');
select pg_temp.ok((select count(*) from public.sp_comment_list2(:'m3')) = (select count(*) from public.sp_comment_list(:'m3')), '한마디 목록2는 옛 목록과 같은 줄');
reset role;
-- 승인 대기는 볼 수 있는 사진이어도 목록을 못 봄(가족 명단을 못 보는 것과 같게)
select m.status as km_status, coalesce(m.pending_until::text, '') as km_until, d.status as km_dev from public.members m join public.devices d on d.member_id = m.id and d.auth_user_id = :'AU' where m.display_name = '큰이모' \gset
update public.members set status = 'pending', pending_until = now() + interval '1 day' where display_name = '큰이모';
update public.devices set status = 'active' where auth_user_id = :'AU' and member_id = (select id from public.members where display_name = '큰이모');
select set_config('request.jwt.claims', json_build_object('sub', :'AU', 'is_anonymous', true)::text, false);
set role authenticated;
select id as km_media from public.media limit 1 \gset
reset role;
insert into public.comments (media_id, parent_user_id, body) values (:'km_media', :'P', '대기 중엔 안 보여야 함');
select set_config('request.jwt.claims', json_build_object('sub', :'AU', 'is_anonymous', true)::text, false);
set role authenticated;
select pg_temp.ok(public.sp_can_view_media(:'km_media') and not exists (select 1 from public.sp_comment_list(:'km_media')), '승인 대기는 사진은 봐도 한마디 목록은 못 봄');
select pg_temp.ok((select e -> 'children' = 'null'::jsonb from jsonb_array_elements(public.sp_me() -> 'families') e where e ->> 'member' = 'pending' limit 1), 'sp_me 승인 대기 구성원(기기 active)엔 아이 생일 없음');
reset role;
update public.members set status = :'km_status', pending_until = nullif(:'km_until', '')::timestamptz where display_name = '큰이모';
update public.devices set status = :'km_dev' where auth_user_id = :'AU' and member_id = (select id from public.members where display_name = '큰이모');
delete from public.comments where parent_user_id = :'P';

-- ── 탈퇴 유예: 가족 화면은 바로 닫힘
select set_config('request.jwt.claims', json_build_object('sub', :'P', 'is_anonymous', false)::text, false);
set role authenticated;
\set ON_ERROR_STOP 0
\echo '아래 에러 1줄은 의도된 거부(부모가 탈퇴 날짜를 직접 고침)'
update public.families set delete_after = now();
reset role;
insert into public.entitlements (family_id, platform, product_id, original_transaction_id, expires_at)
  values (:'fam', 'ios', 'family', 'tx-1', now() + interval '1 month');
set role authenticated;
\echo '아래 에러 1줄은 의도된 거부(구독 중 탈퇴)'
select public.sp_request_delete();
reset role;
delete from public.entitlements where family_id = :'fam';
select set_config('request.jwt.claims', json_build_object('sub', :'GM', 'is_anonymous', true)::text, false);
set role authenticated;
\echo '아래 에러 1줄은 의도된 거부(가족 기기가 탈퇴)'
select public.sp_request_delete();
\set ON_ERROR_STOP 1
reset role;
select pg_temp.ok((select delete_after is null from public.families where id = :'fam'), '거부된 탈퇴는 반영 안 됨');
select set_config('request.jwt.claims', json_build_object('sub', :'P', 'is_anonymous', false)::text, false);
set role authenticated;
select pg_temp.ok(public.sp_request_delete() between now() + interval '71 hours' and now() + interval '73 hours', '탈퇴하면 3일 뒤 지울 날');
select pg_temp.ok(public.sp_parent_home() @> '{"closing": true}' and public.sp_parent_home() ? 'delete_after', '부모 첫 화면에 탈퇴 유예');
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
select pg_temp.ok((select (e -> 'children' -> 0 ->> 'name') = '하린' and (e -> 'children' -> 0 ->> 'birth_date') is not null from jsonb_array_elements(public.sp_me() -> 'families') e where e ->> 'name' = '외할머니'), 'sp_me 승인된 가족에게 아이 이름·생일(기념일)');
select pg_temp.ok((select e -> 'children' = 'null'::jsonb from jsonb_array_elements(public.sp_me() -> 'families') e where e ->> 'device' = 'revoked' limit 1), 'sp_me 막힌 기기엔 아이 생일 없음');
reset role;
select set_config('request.jwt.claims', json_build_object('sub', :'X', 'is_anonymous', true)::text, false);
set role authenticated;
select pg_temp.ok(public.sp_me() -> 'families' @> '[{"device": "revoked", "name": "모르는사람"}]', 'sp_me 차단된 기기');
reset role;
select set_config('request.jwt.claims', json_build_object('sub', :'N1', 'is_anonymous', true)::text, false);
set role authenticated;
select pg_temp.ok(public.sp_me() = '{"families": []}', 'sp_me 처음 기기');
select pg_temp.ok(public.sp_parent_home() = '{"family_id": null, "agreed": []}', '설정 전·기기 사용자는 가족방 없음(동의도 없음)');
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
\set ON_ERROR_STOP 0
\echo '아래 에러 2줄은 의도된 거부(부모가 아이 지우기·순서 바꾸기는 아직 막음)'
delete from public.children where id = :'ch2';
update public.children set sort_order = -1 where id = :'ch2';
\echo '아래 에러 1줄은 의도된 거부(아이 10명 넘게)'
insert into public.children (family_id, name, birth_date) select :'fam', '아이' || g, '2026-01-01' from generate_series(1, 9) g;
\set ON_ERROR_STOP 1
select pg_temp.ok((select count(*) = 2 from public.children where family_id = :'fam'), '지우기·한도 초과는 반영 안 됨');
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

-- ── 되살리기·실제 삭제
select set_config('request.jwt.claims', json_build_object('sub', :'P', 'is_anonymous', false)::text, false);
set role authenticated;
select public.sp_restore_family();
reset role;
select set_config('request.jwt.claims', json_build_object('sub', :'GM', 'is_anonymous', true)::text, false);
set role authenticated;
select pg_temp.ok((select count(*) > 0 from public.media), '되살리면 가족 화면 다시 열림');
reset role;
-- 유예 중엔 부모도 공유 링크·올리기를 멈춘다
select set_config('request.jwt.claims', json_build_object('sub', :'P', 'is_anonymous', false)::text, false);
set role authenticated;
select public.sp_request_delete();
\set ON_ERROR_STOP 0
\echo '아래 에러 1줄은 의도된 거부(유예 중 부모가 공유 링크 만들기)'
select public.sp_create_share(array[:'gma']::uuid[]);
\set ON_ERROR_STOP 1
reset role;
update public.families set delete_after = now() - interval '1 minute' where id = :'fam';
set role authenticated;
\set ON_ERROR_STOP 0
\echo '아래 에러 2줄은 의도된 거부(기한 지난 뒤 되살리기, 부모가 지우기 함수 부름)'
select public.sp_restore_family();
select public.sp_purge_deleted_families();
\set ON_ERROR_STOP 1
select pg_temp.ok(public.sp_parent_home() ->> 'family_id' is null, '지울 날이 지나면 부모에겐 가족방 없음(처음 설정으로)');
-- 다른 부모의 기한 지난 가족방은 예약 작업이 지운다
reset role;
insert into public.families (delete_after) values (now() - interval '1 hour') returning id as fam_old \gset
set role service_role;
select pg_temp.ok((select array_agg(x) = array[:'fam', :'fam_old']::uuid[] or array_agg(x) = array[:'fam_old', :'fam']::uuid[] from public.sp_purge_deleted_families() x), '기한 지난 가족방만 지움');
reset role;
select pg_temp.ok(not exists (select 1 from public.families where id = :'fam') and not exists (select 1 from public.media where family_id = :'fam') and not exists (select 1 from public.parents where family_id = :'fam'), '사진·부모 연결까지 같이 지워짐');
select pg_temp.ok((select count(*) = 2 from public.r2_cleanup where prefix in (:'fam' || '/', :'fam_old' || '/')), '지운 가족방은 R2 정리 대기열에');
-- 지운 뒤 같은 부모는 새로 시작할 수 있다
select set_config('request.jwt.claims', json_build_object('sub', :'P', 'is_anonymous', false)::text, false);
set role authenticated;
select pg_temp.ok(public.sp_create_family('mom', '지우', '하린', '2025-09-17', '0917') is not null, '탈퇴 뒤 새 가족방');
reset role;
-- 예약 작업 전에 처음 설정하면 기한 지난 가족방을 먼저 지운다
select set_config('request.jwt.claims', json_build_object('sub', :'P', 'is_anonymous', false)::text, false);
set role authenticated;
select public.sp_request_delete() is not null;
select public.sp_parent_home() ->> 'family_id' as fam_new \gset
reset role;
update public.families set delete_after = now() - interval '1 minute' where id = :'fam_new';
set role authenticated;
select pg_temp.ok(public.sp_create_family('mom', '지우', '하린', '2025-09-17', '0917') <> :'fam_new', '기한 지난 가족방이 있어도 처음 설정이 됨');
reset role;
select pg_temp.ok((select count(*) = 1 from public.r2_cleanup where prefix = :'fam_new' || '/') and not exists (select 1 from public.families where id = :'fam_new'), '처음 설정 때 지운 가족방도 R2 정리 대기열에');

-- ── 그룹 관리: 10개 한도, 이름·기본 포함 바꾸기, 주소 다시 만들기
select set_config('request.jwt.claims', json_build_object('sub', :'P', 'is_anonymous', false)::text, false);
set role authenticated;
select id as g_home from public.groups where name = '가족' \gset
select public.sp_add_group('그룹' || g, '1111') from generate_series(1, 9) g;
\set ON_ERROR_STOP 0
\echo '아래 에러 1줄은 의도된 거부(그룹 11개)'
select public.sp_add_group('그룹10', '1111');
\set ON_ERROR_STOP 1
select pg_temp.ok((select count(*) = 10 from public.groups), '그룹은 10개까지');
update public.groups set name = '우리집', include_by_default = false where id = :'g_home';
select public.sp_parent_home() ->> 'family_id' as fam3 \gset
select public.sp_create_media(:'fam3', 'photo', now(), 'exif', null, null, null, array[:'g_home']::uuid[]) as mg \gset
reset role;
update public.media set status = 'ready' where id = :'mg';
set role authenticated;
select public.sp_create_share(array[:'g_home']::uuid[], array[:'mg']::uuid[]) as code_g \gset
-- 이 링크로 새 이름이 들어와 승인을 기다린다
\set N7 '00000000-0000-0000-0000-0000000000c7'
reset role;
insert into auth.users (id, is_anonymous) values (:'N7', true);
select set_config('request.jwt.claims', json_build_object('sub', :'N7', 'is_anonymous', true)::text, false);
set role authenticated;
select pg_temp.ok(public.sp_enter(:'code_g', '0917', null, '사촌', :'g_home') ->> 'result' = 'pending', '새 이름은 승인 대기');
reset role;
select set_config('request.jwt.claims', json_build_object('sub', :'P', 'is_anonymous', false)::text, false);
set role authenticated;
select pg_temp.ok(public.sp_reset_group_links(:'g_home') = 1, '주소 다시 만들기는 그 그룹 링크를 막음');
select pg_temp.ok(public.sp_entry_info(:'code_g') ->> 'result' = 'not_found', '예전 주소는 바로 막힘');
select pg_temp.ok(public.sp_reset_group_links(:'g_home') = 0, '이미 막힌 링크는 다시 세지 않음');
reset role;
select set_config('request.jwt.claims', json_build_object('sub', :'N7', 'is_anonymous', true)::text, false);
set role authenticated;
select pg_temp.ok((select count(*) = 1 from public.media), '주소를 다시 만들어도 승인 기다리는 사람은 링크 사진을 봄');
reset role;
select set_config('request.jwt.claims', json_build_object('sub', :'P', 'is_anonymous', false)::text, false);
set role authenticated;
reset role;
select pg_temp.ok((select name = '우리집' and not include_by_default from public.groups where id = :'g_home'), '이름·기본 포함 바꾸기');
select set_config('request.jwt.claims', json_build_object('sub', :'P2', 'is_anonymous', false)::text, false);
set role authenticated;
update public.groups set name = '남의집' where id = :'g_home';
\set ON_ERROR_STOP 0
\echo '아래 에러 2줄은 의도된 거부(다른 가족방 그룹 주소 다시 만들기·비밀번호 바꾸기)'
select public.sp_reset_group_links(:'g_home');
select public.sp_set_group_password(:'g_home', '0000', null);
\set ON_ERROR_STOP 1
reset role;
select pg_temp.ok((select name = '우리집' from public.groups where id = :'g_home'), '다른 가족방 부모는 그룹 이름 못 바꿈');

-- ── 사진 정보: 찍은 날·아이·그룹 고치기, 지우기
select set_config('request.jwt.claims', json_build_object('sub', :'P', 'is_anonymous', false)::text, false);
set role authenticated;
select id as g_other from public.groups where name = '그룹1' \gset
select (public.sp_parent_home() -> 'children' -> 0 ->> 'id') as kid1 \gset
select public.sp_update_media(:'mg', '2026-01-02T03:04:05+09', array[:'kid1']::uuid[], array[:'g_other']::uuid[]);
select pg_temp.ok((select taken_at = '2026-01-02T03:04:05+09' and taken_at_source = 'manual' from public.media where id = :'mg'), '찍은 날 고치기');
select pg_temp.ok((select array_agg(group_id) = array[:'g_other']::uuid[] from public.media_groups where media_id = :'mg'), '보여줄 그룹 바꾸기');
select pg_temp.ok((select array_agg(child_id) = array[:'kid1']::uuid[] from public.media_children where media_id = :'mg'), '아이 태그');
-- 변경 기록: 고친 한 줄(전·후) + 올린 한 줄, 최근 것부터. 안 바뀐 저장은 안 남김
select public.sp_update_media(:'mg', '2026-01-02T03:04:05+09', array[:'kid1']::uuid[], array[:'g_other', :'g_other']::uuid[]);
select pg_temp.ok((select array_agg(kind order by at desc) = array['update', 'create'] from public.sp_media_changes(:'mg')), '변경 기록 2줄(고침·올림), 같은 값 저장은 안 남김');
select pg_temp.ok((select who = '엄마' and groups = array['그룹1'] and old_groups = array['우리집'] and cardinality(children) = 1 and old_children = '{}'
  and taken_at = '2026-01-02T03:04:05+09' and old_taken_at is not null from public.sp_media_changes(:'mg') where kind = 'update'), '고친 기록: 누가·그룹·아이·찍은 날 전후');
select pg_temp.ok((select who = '엄마' and groups = array['우리집'] and old_groups is null from public.sp_media_changes(:'mg') where kind = 'create'), '올린 기록: 처음 그룹');
\set ON_ERROR_STOP 0
\echo '아래 에러 2줄은 의도된 거부(그룹 없이 저장, 남의 가족방 그룹)'
select public.sp_update_media(:'mg', now(), '{}', '{}');
select public.sp_update_media(:'mg', now(), '{}', array[:'gma']::uuid[]);
\set ON_ERROR_STOP 1
reset role;
select set_config('request.jwt.claims', json_build_object('sub', :'P2', 'is_anonymous', false)::text, false);
set role authenticated;
\set ON_ERROR_STOP 0
\echo '아래 에러 2줄은 의도된 거부(남의 사진 고치기·지우기)'
select public.sp_update_media(:'mg', now(), '{}', array[:'g_other']::uuid[]);
select public.sp_delete_media(:'mg');
\set ON_ERROR_STOP 1
select pg_temp.ok(not exists (select 1 from public.sp_media_changes(:'mg')), '다른 가족방 엄빠는 변경 기록 못 봄');
reset role;
-- 탈퇴 유예 중엔 부모도 고치기·지우기 못 함
update public.families set delete_after = now() + interval '3 days' where id = :'fam3';
select set_config('request.jwt.claims', json_build_object('sub', :'P', 'is_anonymous', false)::text, false);
set role authenticated;
\set ON_ERROR_STOP 0
\echo '아래 에러 2줄은 의도된 거부(탈퇴 유예 중 사진 고치기·지우기)'
select public.sp_update_media(:'mg', now(), '{}', array[:'g_other']::uuid[]);
select public.sp_delete_media(:'mg');
\set ON_ERROR_STOP 1
reset role;
update public.families set delete_after = null where id = :'fam3';
update public.media set bytes = 1000 where id = :'mg';
update public.families set storage_used_bytes = 5000 where id = :'fam3';
select set_config('request.jwt.claims', json_build_object('sub', :'P', 'is_anonymous', false)::text, false);
set role authenticated;
select public.sp_delete_media(:'mg');
select pg_temp.ok(not exists (select 1 from public.media where id = :'mg'), '사진 지우기');
reset role;
select pg_temp.ok((select storage_used_bytes = 4000 from public.families where id = :'fam3'), '지우면 저장 용량에서 빠짐');
select pg_temp.ok(exists (select 1 from public.r2_cleanup where prefix = :'fam3' || '/' || :'mg' || '/'), '지운 사진 폴더는 R2 정리 대기열에');

-- ── 부모 최근 반응
insert into public.media (family_id, kind, taken_at, taken_at_source, status, thumb_key) values (:'fam3', 'photo', now(), 'exif', 'ready', 'k') returning id as ma \gset
insert into public.members (family_id, group_id, display_name) values (:'fam3', :'g_home', '외할머니') returning id as mem_a \gset
insert into public.members (family_id, group_id, display_name, status) values (:'fam3', :'g_home', '모르는이', 'rejected') returning id as mem_r \gset
insert into public.reactions (media_id, member_id, kind) values (:'ma', :'mem_a', 'heart'), (:'ma', :'mem_r', 'best');
insert into public.comments (media_id, member_id, body) values (:'ma', :'mem_a', '아이고 많이 컸네');
update public.parents set activity_seen_at = now() - interval '1 hour' where family_id = :'fam3';
select set_config('request.jwt.claims', json_build_object('sub', :'P', 'is_anonymous', false)::text, false);
set role authenticated;
select pg_temp.ok((public.sp_parent_home() ->> 'new_activity')::int = 2, '새 반응 수(내보낸 사람 빼고)');
select pg_temp.ok(jsonb_array_length(public.sp_parent_activity() -> 'items') = 2, '최근 반응 목록');
select pg_temp.ok(public.sp_parent_activity() -> 'items' @> '[{"type": "comment", "who": "외할머니", "body": "아이고 많이 컸네"}, {"type": "reaction", "kind": "heart"}]', '반응·한마디 내용');
select public.sp_mark_activity_seen((public.sp_parent_activity() ->> 'read_at')::timestamptz);
select pg_temp.ok((public.sp_parent_home() ->> 'new_activity')::int = 0, '열면 새 반응 0');
reset role;
select set_config('request.jwt.claims', json_build_object('sub', :'P2', 'is_anonymous', false)::text, false);
set role authenticated;
select pg_temp.ok(not (coalesce(public.sp_parent_activity() -> 'items', '[]') @> '[{"body": "아이고 많이 컸네"}]'), '다른 가족방 부모는 못 봄');
reset role;
select set_config('request.jwt.claims', json_build_object('sub', :'GM', 'is_anonymous', true)::text, false);
set role authenticated;
select pg_temp.ok(public.sp_parent_activity() is null, '가족 기기는 못 봄');
reset role;

-- ── 접종·검진 완료 기록: 부모만
select set_config('request.jwt.claims', json_build_object('sub', :'P', 'is_anonymous', false)::text, false);
set role authenticated;
insert into public.health_done (family_id, child_id, item_key, done_on) values (:'fam3', :'kid1', 'mmr-1', '2026-10-02');
update public.children set show_health = false where id = :'kid1';
select pg_temp.ok((select count(*) = 1 from public.health_done), '부모는 완료 기록');
select pg_temp.ok((select not show_health from public.children where id = :'kid1'), '일정 보기 끄기');
reset role;
select set_config('request.jwt.claims', json_build_object('sub', :'P2', 'is_anonymous', false)::text, false);
set role authenticated;
select pg_temp.ok((select count(*) = 0 from public.health_done where child_id = :'kid1'), '다른 가족방 부모는 못 읽음');
\set ON_ERROR_STOP 0
\echo '아래 에러 1줄은 의도된 거부(다른 가족방 아이에 완료 기록)'
insert into public.health_done (family_id, child_id, item_key, done_on) values (:'fam3', :'kid1', 'var', '2026-10-02');
\set ON_ERROR_STOP 1
reset role;
select set_config('request.jwt.claims', json_build_object('sub', :'GM', 'is_anonymous', true)::text, false);
set role authenticated;
select pg_temp.ok((select count(*) = 0 from public.health_done), '가족 기기는 못 읽음');
reset role;

-- ── 홈 화면에 두기 부탁: 가족 기기 본인만
insert into public.devices (auth_user_id, family_id, member_id) values (:'N6', :'fam3', :'mem_a');
select set_config('request.jwt.claims', json_build_object('sub', :'N6', 'is_anonymous', true)::text, false);
set role authenticated;
select public.sp_request_install_help(:'fam3');
\set ON_ERROR_STOP 0
\echo '아래 에러 1줄은 의도된 거부(들어가지 않은 가족방에 부탁)'
select public.sp_request_install_help(:'fam');
\set ON_ERROR_STOP 1
reset role;
select pg_temp.ok((select install_help_at is not null from public.members where id = :'mem_a'), '부탁하면 그 사람에게 기록');

-- ── 정리 작업(service_role)·5GB 상한
insert into public.media (family_id, kind, taken_at, taken_at_source, status, created_at) values
  (:'fam3', 'photo', now(), 'exif', 'uploading', now() - interval '2 days'),
  (:'fam3', 'photo', now(), 'exif', 'uploading', now() - interval '1 hour');
set role service_role;
select pg_temp.ok(public.sp_cleanup_stale_uploads() = 1, '하루 지난 올리는 중 사진만 지움');
select pg_temp.ok((select count(*) >= 1 from public.sp_r2_cleanup_take(500) p where p like :'fam3' || '/%/'), '그 사진 폴더는 대기열에');
select public.sp_r2_cleanup_done(p) from public.sp_r2_cleanup_take(500) p;
select pg_temp.ok((select count(*) = 0 from public.r2_cleanup), '지운 폴더는 대기열에서 빠짐');
reset role;
select set_config('request.jwt.claims', json_build_object('sub', :'P', 'is_anonymous', false)::text, false);
set role authenticated;
\set ON_ERROR_STOP 0
\echo '아래 에러 1줄은 의도된 거부(부모가 정리 함수 부름)'
select public.sp_cleanup_stale_uploads();
\set ON_ERROR_STOP 1
reset role;
update public.families set storage_used_bytes = 5368709120 where id = :'fam3';
set role authenticated;
\set ON_ERROR_STOP 0
\echo '아래 에러 1줄은 의도된 거부(5GB 다 참)'
select public.sp_create_media(:'fam3', 'photo', now(), 'exif');
\set ON_ERROR_STOP 1
reset role;
update public.families set storage_used_bytes = 0 where id = :'fam3';
-- 완료 때도 5GB 한도(큰 영상 나눠 올리기, 20261027000004): 시작은 됐어도 완료하면 넘으면 거절
update public.families set storage_used_bytes = 5368709120 - 500 where id = :'fam3';
set role authenticated;
select public.sp_create_media(:'fam3', 'video', now(), 'file') as q1 \gset
reset role;
set role service_role;
\set ON_ERROR_STOP 0
\echo '아래 에러 1줄은 의도된 거부(완료하면 5GB를 넘음)'
select public.sp_finish_upload(:'q1', 'x/v', 'x/t', 'x/p', 1000);
\set ON_ERROR_STOP 1
select pg_temp.ok(public.sp_finish_upload(:'q1', 'x/v', 'x/t', 'x/p', 400), '완료해도 5GB 안이면 완료');
reset role;
select pg_temp.ok((select storage_used_bytes = 5368709120 - 100 from public.families where id = :'fam3'), '완료한 크기만 더함');
select pg_temp.ok((select status = 'ready' from public.media where id = :'q1'), '거절된 완료는 되돌려지고 다시 완료하면 ready');
update public.families set storage_used_bytes = 0 where id = :'fam3';

-- ── 공동 관리자(20261029000003): 엄빠 둘까지, 초대 링크 한 번·3일, 서로 내보내기, 한 명 탈퇴는 나만 나가기
\set Q1 '00000000-0000-0000-0000-0000000000e1'
\set Q2 '00000000-0000-0000-0000-0000000000e2'
\set Q3 '00000000-0000-0000-0000-0000000000e3'
insert into auth.users (id, is_anonymous) values (:'Q1', false), (:'Q2', false), (:'Q3', false);
select set_config('request.jwt.claims', json_build_object('sub', :'Q1', 'is_anonymous', false)::text, false);
set role authenticated;
select public.sp_create_family('mom', '지우', '서아', '2025-09-17', '1111') as qfam \gset
select public.sp_create_media(:'qfam', 'photo', now(), 'exif') as qm \gset
select public.sp_create_parent_invite() as inv1 \gset
select pg_temp.ok(public.sp_parent_invite_info(:'inv1') @> '{"result": "ok", "child_name": "서아", "inviter_role": "mom"}', '초대 정보(아이 이름·초대한 역할)');
select pg_temp.ok(public.sp_create_parent_invite() <> :'inv1', '다시 만들면 새 링크');
select pg_temp.ok(public.sp_parent_invite_info(:'inv1') ->> 'result' = 'not_found', '예전 링크는 사라짐');
select public.sp_create_parent_invite() as inv1 \gset
select pg_temp.ok(jsonb_array_length(public.sp_family_parents() -> 'parents') = 1 and public.sp_family_parents() -> 'invite' ->> 'code' = :'inv1', '엄빠 목록·살아 있는 링크');
reset role;
update public.media set status = 'ready' where id = :'qm';
-- 가족 기기(익명)는 초대를 못 받는다
select set_config('request.jwt.claims', json_build_object('sub', :'GM', 'is_anonymous', true)::text, false);
set role authenticated;
\set ON_ERROR_STOP 0
\echo '아래 에러 1줄은 의도된 거부(익명 기기는 엄빠 초대를 못 받음)'
select public.sp_accept_parent_invite(:'inv1', 'dad');
\set ON_ERROR_STOP 1
-- 이미 다른 가족방 엄빠(P2)도 못 받는다
select set_config('request.jwt.claims', json_build_object('sub', :'P2', 'is_anonymous', false)::text, false);
\set ON_ERROR_STOP 0
\echo '아래 에러 1줄은 의도된 거부(이미 다른 가족방 엄빠)'
select public.sp_accept_parent_invite(:'inv1', 'dad');
\set ON_ERROR_STOP 1
-- Q2가 아빠로 받음 → 같은 가족방 엄빠 화면
select set_config('request.jwt.claims', json_build_object('sub', :'Q2', 'is_anonymous', false)::text, false);
select pg_temp.ok(public.sp_accept_parent_invite(:'inv1', 'dad') = :'qfam', '초대 받으면 같은 가족방');
select pg_temp.ok(public.sp_parent_family() = :'qfam' and public.sp_parent_home() @> '{"role": "dad"}', '받은 엄빠도 엄빠 화면(아빠)');
select pg_temp.ok((select count(*) = 1 from public.media where id = :'qm'), '받은 엄빠도 사진을 봄');
select pg_temp.ok(public.sp_parent_invite_info(:'inv1') ->> 'result' = 'expired', '쓴 링크는 지남');
\set ON_ERROR_STOP 0
\echo '아래 에러 3줄은 의도된 거부(엄빠 둘이면 초대 못 만듦, 나 자신은 못 내보냄, 다른 가족방 엄빠는 못 내보냄)'
select public.sp_create_parent_invite();
select public.sp_remove_coparent(:'Q2');
select public.sp_remove_coparent(:'P');
\set ON_ERROR_STOP 1
select pg_temp.ok(jsonb_array_length(public.sp_family_parents() -> 'parents') = 2 and (public.sp_family_parents() -> 'parents' -> 0 ->> 'me')::boolean, '엄빠 둘, 나 먼저');
-- 아빠가 하트를 남긴 뒤 엄마가 내보내면 기록은 남고(removed_at) 아빠는 엄빠 화면을 잃음
select public.sp_parent_react(:'qm', 'heart', true);
select set_config('request.jwt.claims', json_build_object('sub', :'Q1', 'is_anonymous', false)::text, false);
select public.sp_remove_coparent(:'Q2');
select pg_temp.ok(jsonb_array_length(public.sp_family_parents() -> 'parents') = 1, '내보내면 엄빠 하나');
reset role;
select pg_temp.ok((select removed_at is not null from public.parents where user_id = :'Q2'), '기록이 있으면 행은 남기고 나감 표시');
select pg_temp.ok((select count(*) = 1 from public.reactions where parent_user_id = :'Q2'), '내보낸 엄빠의 하트는 그대로');
set role authenticated;
select set_config('request.jwt.claims', json_build_object('sub', :'Q2', 'is_anonymous', false)::text, false);
select pg_temp.ok(public.sp_parent_family() is null and public.sp_parent_home() ->> 'family_id' is null, '내보낸 엄빠는 엄빠 화면 없음');
select pg_temp.ok((select count(*) = 0 from public.media where id = :'qm'), '내보낸 엄빠는 사진 못 봄');
select pg_temp.ok(public.sp_parent_activity() is null, '내보낸 엄빠는 예전 가족방 최근 반응 못 읽음');
-- 다시 초대받으면 남아 있던 행이 되살아남(막다른 길 없음), 같은 역할(엄마)은 거절
select set_config('request.jwt.claims', json_build_object('sub', :'Q1', 'is_anonymous', false)::text, false);
select public.sp_create_parent_invite() as invr \gset
select pg_temp.ok(public.sp_parent_invite_info(:'invr') @> '{"result": "ok", "taken_roles": ["mom"], "mine": true}', '초대 정보: 이미 있는 역할·내 가족방 초대');
select set_config('request.jwt.claims', json_build_object('sub', :'Q2', 'is_anonymous', false)::text, false);
select pg_temp.ok(public.sp_parent_invite_info(:'invr') ->> 'mine' = 'false', '다른 사람이 열면 mine 아님');
\set ON_ERROR_STOP 0
\echo '아래 에러 1줄은 의도된 거부(엄마가 이미 있으면 엄마로 못 받음)'
select public.sp_accept_parent_invite(:'invr', 'mom');
\set ON_ERROR_STOP 1
select pg_temp.ok(public.sp_accept_parent_invite(:'invr', 'dad') = :'qfam', '나갔던 엄빠도 다시 초대받음');
select pg_temp.ok(public.sp_parent_family() = :'qfam', '되살아나 엄빠 화면');
select set_config('request.jwt.claims', json_build_object('sub', :'Q1', 'is_anonymous', false)::text, false);
select public.sp_remove_coparent(:'Q2');
select pg_temp.ok(public.sp_parent_invite_info(:'invr') - 'mine' = '{"result": "expired"}', '지난 초대는 이름을 안 줌');
-- 나간 엄빠는 같은 로그인으로 새 가족방을 만들 수 있음(행을 옮김), 예전 하트는 그대로
select set_config('request.jwt.claims', json_build_object('sub', :'Q2', 'is_anonymous', false)::text, false);
select public.sp_create_family('dad', '민수', '도윤', '2026-01-02', '2222') as qfam2 \gset
select pg_temp.ok(public.sp_parent_family() = :'qfam2', '나간 엄빠가 새 가족방 만듦');
reset role;
select pg_temp.ok((select count(*) = 1 from public.reactions where parent_user_id = :'Q2' and media_id = :'qm'), '예전 가족방 하트는 그대로');
-- 옮겨 간 새 가족방이 지워져도 예전 가족방 하트는 남고, 그 로그인으로 다시 시작할 수 있음
select public.sp_purge_family(:'qfam2');
select pg_temp.ok((select count(*) = 1 from public.reactions where parent_user_id = :'Q2' and media_id = :'qm'), '새 가족방을 지워도 예전 하트는 그대로');
select pg_temp.ok((select family_id is null from public.parents where user_id = :'Q2'), '기록 있는 엄빠 행은 가족방만 비고 남음');
set role authenticated;
select set_config('request.jwt.claims', json_build_object('sub', :'Q2', 'is_anonymous', false)::text, false);
select pg_temp.ok(public.sp_parent_home() ->> 'family_id' is null, '가족방이 지워지면 처음 설정부터');
select public.sp_create_family('dad', '민수', '도윤', '2026-01-02', '2222') as qfam3 \gset
select pg_temp.ok(public.sp_parent_family() = :'qfam3', '다시 새 가족방을 만들 수 있음');
set role authenticated;
-- 새 초대로 Q3(아빠) → Q3 탈퇴는 나만 나가기(기록 없으면 행 삭제), 가족방은 그대로
select set_config('request.jwt.claims', json_build_object('sub', :'Q1', 'is_anonymous', false)::text, false);
select public.sp_create_parent_invite() as inv2 \gset
select set_config('request.jwt.claims', json_build_object('sub', :'Q3', 'is_anonymous', false)::text, false);
select public.sp_accept_parent_invite(:'inv2', 'dad');
select pg_temp.ok(public.sp_request_delete() is null, '함께 관리 중 탈퇴는 나만 나가기(null)');
select pg_temp.ok(public.sp_parent_family() is null, '나가면 엄빠 화면 없음');
select set_config('request.jwt.claims', json_build_object('sub', :'Q1', 'is_anonymous', false)::text, false);
select pg_temp.ok(public.sp_parent_home() ->> 'closing' = 'false', '남은 엄빠의 가족방은 그대로');
reset role;
select pg_temp.ok(not exists (select 1 from public.parents where user_id = :'Q3'), '기록 없이 나간 엄빠는 행 삭제');
select pg_temp.ok(not exists (select 1 from auth.users where id = :'Q3'), '기록 없이 나간 엄빠는 로그인 계정도 삭제(20261102000002)');
select pg_temp.ok(exists (select 1 from auth.users where id = :'Q2'), '기록이 남아 행이 남은 엄빠는 로그인 계정도 남김');
-- 3일 지난 초대는 지남
set role authenticated;
select public.sp_create_parent_invite() as inv3 \gset
reset role;
update public.parent_invites set expires_at = now() - interval '1 minute' where code = :'inv3';
set role authenticated;
select pg_temp.ok(public.sp_parent_invite_info(:'inv3') ->> 'result' = 'expired', '3일 지난 초대는 지남');
-- 마지막 한 명 탈퇴는 지금처럼 3일 뒤 삭제
select pg_temp.ok(public.sp_request_delete() is not null, '마지막 엄빠 탈퇴는 삭제 예정');
select public.sp_restore_family();
reset role;

-- ── 로그인 계정 정리(20261102000002): 가족방이 지워지면 엄빠·가족 기기 로그인 계정도 지움, 남은 익명 계정·틀린 기록은 7일 뒤
select gen_random_uuid() as ax \gset
select gen_random_uuid() as ad \gset
select gen_random_uuid() as ao \gset
select gen_random_uuid() as an \gset
insert into auth.users (id, is_anonymous) values (:'ax', false), (:'ad', true);
insert into auth.users (id, is_anonymous, created_at) values (:'ao', true, now() - interval '8 days'), (:'an', true, now() - interval '1 day');
select set_config('request.jwt.claims', json_build_object('sub', :'ax', 'is_anonymous', false)::text, false);
set role authenticated;
select public.sp_create_family('mom', '테스트', '아이', '2025-01-01', '1111') as afam \gset
reset role;
select id as agrp from public.groups where family_id = :'afam' \gset
insert into public.members (family_id, group_id, display_name) values (:'afam', :'agrp', '할머니') returning id as amem \gset
insert into public.devices (auth_user_id, family_id, member_id, status) values (:'ad', :'afam', :'amem', 'active');
insert into public.entry_failures (family_id, group_id, auth_user_id, at) values (:'afam', :'agrp', :'an', now() - interval '8 days'), (:'afam', :'agrp', :'an', now());
select set_config('request.jwt.claims', '', false);
set role service_role;
select pg_temp.ok(public.sp_cleanup_auth() = 1, '정리: 기기 없이 7일 넘은 익명 계정 1개만');
reset role;
select pg_temp.ok(not exists (select 1 from auth.users where id = :'ao') and exists (select 1 from auth.users where id = :'an'), '7일 안 된 익명 계정은 남김');
select pg_temp.ok((select count(*) = 1 from public.entry_failures where auth_user_id = :'an'), '7일 넘은 틀린 기록만 지움');
select public.sp_purge_family(:'afam');
select pg_temp.ok(not exists (select 1 from auth.users where id in (:'ax', :'ad')), '가족방을 지우면 엄빠·가족 기기 로그인 계정도 지움');

-- ── 동의 기록(20261103000001): 본인 것만, sp_agree로만 쓰기, 첫 화면 묶음에 agreed
select gen_random_uuid() as cu \gset
select gen_random_uuid() as cv \gset
insert into auth.users (id, is_anonymous) values (:'cu', false), (:'cv', false);
select set_config('request.jwt.claims', json_build_object('sub', :'cu', 'is_anonymous', false)::text, false);
set role authenticated;
select pg_temp.ok(public.sp_parent_home() -> 'agreed' = '[]'::jsonb and public.sp_parent_home() ->> 'family_id' is null, '동의 전: 가족방 없어도 agreed 빈 목록');
select public.sp_agree('terms', '2026-11-02');
select public.sp_agree('terms', '2026-11-02');
select pg_temp.ok(public.sp_parent_home() -> 'agreed' = '["terms:2026-11-02"]'::jsonb, '동의하면 agreed에(두 번 해도 하나)');
select public.sp_create_family('dad', '테스트', '아이', '2025-01-01', '2222') as cfam \gset
select public.sp_agree('health', '2026-11-02');
select pg_temp.ok(public.sp_parent_home() @> '{"agreed": ["terms:2026-11-02", "health:2026-11-02"], "role": "dad"}', '가족방이 있어도 agreed가 붙음');
do $$ begin perform public.sp_agree('other', '2026-11-02'); raise exception '모르는 종류가 들어감'; exception when check_violation then null; end $$;
do $$ begin perform public.sp_agree('terms', 'v1'); raise exception '날짜가 아닌 버전이 들어감'; exception when check_violation then null; end $$;
do $$ begin insert into public.consents (user_id, kind, version) values (auth.uid(), 'terms', '2027-01-01'); raise exception '직접 넣기가 됨'; exception when insufficient_privilege then null; end $$;
select set_config('request.jwt.claims', json_build_object('sub', :'cv', 'is_anonymous', false)::text, false);
select pg_temp.ok((select count(*) = 0 from public.consents), '다른 사람 동의 기록은 안 보임');
reset role;
set role anon;
do $$ begin perform public.sp_agree('terms', '2026-11-02'); raise exception '로그인 없이 동의 기록이 됨'; exception when insufficient_privilege then null; end $$;
reset role;
select public.sp_purge_family(:'cfam');
select pg_temp.ok(not exists (select 1 from public.consents where user_id = :'cu'), '가족방·계정을 지우면 동의 기록도 지움');

-- ── 운영자 화면(20261104000001): 방문 기록은 본인 것만 세고, 운영 숫자는 서버(service_role)만
select gen_random_uuid() as op \gset
select gen_random_uuid() as od \gset
select gen_random_uuid() as oo \gset
insert into auth.users (id, is_anonymous, raw_app_meta_data) values (:'op', false, '{"provider": "kakao"}'), (:'od', true, null), (:'oo', true, null);
select set_config('request.jwt.claims', json_build_object('sub', :'op', 'is_anonymous', false)::text, false);
set role authenticated;
select public.sp_create_family('mom', '운영', '아이', '2025-01-01', '3333') as ofam \gset
reset role;
select id as ogrp from public.groups where family_id = :'ofam' \gset
update public.groups set password_hint = '운영힌트' where id = :'ogrp';
insert into public.members (family_id, group_id, display_name) values (:'ofam', :'ogrp', '할머니') returning id as omem \gset
insert into public.devices (auth_user_id, family_id, member_id, status) values (:'od', :'ofam', :'omem', 'active') returning id as odev \gset
insert into public.shares (family_id, code) values (:'ofam', 'OpsCode1');
-- 엄빠 두 번, 기기 한 번
select set_config('request.jwt.claims', json_build_object('sub', :'op', 'is_anonymous', false)::text, false);
set role authenticated;
select public.sp_note_visit();
select public.sp_note_visit();
do $$ begin perform 1 from public.visits; raise exception '방문 기록이 읽힘'; exception when insufficient_privilege then null; end $$;
do $$ begin insert into public.visits (family_id, kind, visitor, day) values (gen_random_uuid(), 'parent', auth.uid(), current_date); raise exception '방문 기록을 직접 씀'; exception when insufficient_privilege then null; end $$;
do $$ begin perform public.sp_ops_summary(current_date, current_date); raise exception '엄빠가 운영 현황을 봄'; exception when insufficient_privilege then null; end $$;
do $$ begin perform public.sp_ops_families(current_date, current_date, 'created', 0); raise exception '엄빠가 가족방 목록을 봄'; exception when insufficient_privilege then null; end $$;
do $$ begin perform public.sp_ops_family(gen_random_uuid(), current_date, current_date); raise exception '엄빠가 가족방 상세를 봄'; exception when insufficient_privilege then null; end $$;
do $$ begin perform public.sp_note_link_visit('OpsCode1', 'link'); raise exception '엄빠가 링크 방문을 씀'; exception when insufficient_privilege then null; end $$;
do $$ begin perform public.sp_ops_accounts(current_date, current_date, 'created', 0); raise exception '엄빠가 계정 목록을 봄'; exception when insufficient_privilege then null; end $$;
select set_config('request.jwt.claims', json_build_object('sub', :'od', 'is_anonymous', true)::text, false);
select public.sp_note_visit();
do $$ begin perform public.sp_ops_summary(current_date, current_date); raise exception '가족 기기가 운영 현황을 봄'; exception when insufficient_privilege then null; end $$;
-- 들어간 가족방이 없는 사용자는 아무것도 안 남김
select set_config('request.jwt.claims', json_build_object('sub', :'oo', 'is_anonymous', true)::text, false);
select public.sp_note_visit();
reset role;
set role anon;
do $$ begin perform public.sp_note_visit(); raise exception '로그인 없이 방문 기록'; exception when insufficient_privilege then null; end $$;
do $$ begin perform public.sp_ops_summary(current_date, current_date); raise exception '로그인 없이 운영 현황'; exception when insufficient_privilege then null; end $$;
reset role;
select set_config('request.jwt.claims', '', false);
set role service_role;
select public.sp_note_link_visit('OpsCode1', 'link');
select public.sp_note_link_visit('없는코드', 'link');
select public.sp_ops_summary(public.sp_seoul_today() - 6, public.sp_seoul_today()) as osum \gset
select public.sp_ops_families(public.sp_seoul_today() - 6, public.sp_seoul_today(), 'visits', 0) as olist \gset
select public.sp_ops_family(:'ofam', public.sp_seoul_today() - 6, public.sp_seoul_today()) as odet \gset
select public.sp_ops_accounts(public.sp_seoul_today() - 6, public.sp_seoul_today(), 'visits', 0) as oacc \gset
reset role;
select pg_temp.ok((select count from public.visits where family_id = :'ofam' and kind = 'parent') = 2, '엄빠 방문 두 번은 한 줄 2회');
select pg_temp.ok((select count from public.visits where family_id = :'ofam' and kind = 'device' and visitor = :'odev') = 1, '기기 방문은 기기 번호로');
select pg_temp.ok((select count(*) from public.visits where visitor = :'oo') = 0, '가족방 없는 사용자는 기록 없음');
select pg_temp.ok((select sum(count) from public.visits where family_id = :'ofam' and kind = 'link') = 1, '링크 방문은 있는 코드만');
select pg_temp.ok((:'osum'::jsonb -> 'visits' ->> 'count')::int >= 3 and jsonb_array_length(:'osum'::jsonb -> 'visits' -> 'days') = 7, '현황: 방문 수와 7일 막대');
select pg_temp.ok((:'osum'::jsonb -> 'providers' ->> 'kakao')::int >= 1, '현황: 로그인 방법');
select pg_temp.ok((:'osum'::jsonb -> 'visits' -> 'days' -> 6 ->> 'day') = public.sp_seoul_today()::text, '현황: 막대 마지막 날은 오늘(날짜만)');
select pg_temp.ok((:'olist'::jsonb -> 'rows' -> 0 ->> 'id') = :'ofam' and (:'olist'::jsonb -> 'rows' -> 0 ->> 'visits')::int = 3, '목록: 방문 많은 순 첫 줄');
select pg_temp.ok(not (:'olist'::jsonb::text ~ '할머니|운영|아이|OpsCode1'), '목록에 이름·코드 없음');
select pg_temp.ok(not (:'odet'::jsonb::text ~ 'OpsCode1|3333|password'), '상세에 공유 코드·그룹 비밀번호 없음');
select pg_temp.ok(not exists (select 1 from public.groups g where g.family_id = :'ofam' and g.password_hint is not null and position(g.password_hint in :'odet'::jsonb::text) > 0), '상세에 그룹 비밀번호 힌트 없음');
select pg_temp.ok(not (:'odet'::jsonb::text ~ '운영힌트'), '상세에 힌트 글자 없음');
select pg_temp.ok(:'odet'::jsonb -> 'children' -> 0 ->> 'name' = '아이' and :'odet'::jsonb -> 'devices' -> 0 ->> 'name' = '할머니' and :'odet'::jsonb -> 'parents' -> 0 ->> 'name' = '운영' and :'odet'::jsonb -> 'parents' -> 0 ->> 'provider' = 'kakao', '상세: 지금 설정된 아이·구성원·엄빠 이름(167)');
select pg_temp.ok(:'odet'::jsonb ->> 'text_size_mode' = 'relation' and :'odet'::jsonb -> 'groups' -> 0 ->> 'name' is not null, '상세: 설정값·그룹 이름');
select pg_temp.ok((:'odet'::jsonb -> 'devices' -> 0 ->> 'visits')::int = 1 and (:'odet'::jsonb -> 'parents' -> 0 ->> 'visits')::int = 2 and (:'odet'::jsonb -> 'entry' ->> 'link')::int = 1, '상세: 사람별 방문·링크 방문');
select pg_temp.ok((:'odet'::jsonb -> 'devices' -> 0 ->> 'group')::int = 1, '상세: 그룹은 순서 번호');
select pg_temp.ok((select count(*) = 1 from jsonb_array_elements(:'oacc'::jsonb -> 'rows') r where r ->> 'id' = :'op' and r ->> 'family_id' = :'ofam' and (r ->> 'visits')::int = 2 and r ->> 'provider' = 'kakao'), '계정 목록: 엄빠 계정·가족방·방문');
select pg_temp.ok(not exists (select 1 from jsonb_array_elements(:'oacc'::jsonb -> 'rows') r where r ->> 'id' in (:'od', :'oo')), '계정 목록에 익명(가족 기기) 계정 없음');
select pg_temp.ok(not (:'oacc'::jsonb::text ~ '운영|email\"\:'), '계정 목록에 이름·이메일 없음');
-- 173: 올린 사진·영상 목록 — 정보만(파일 주소 없음), 엄빠·가족 기기는 막힘, 가족방 거르기
select set_config('request.jwt.claims', json_build_object('sub', :'op', 'is_anonymous', false)::text, false);
set role authenticated;
do $$ begin perform public.sp_ops_media(current_date, current_date, null, 0); raise exception '엄빠가 운영 사진 목록을 봄'; exception when insufficient_privilege then null; end $$;
reset role;
set role anon;
do $$ begin perform public.sp_ops_media(current_date, current_date, null, 0); raise exception '로그인 없이 운영 사진 목록'; exception when insufficient_privilege then null; end $$;
reset role;
select set_config('request.jwt.claims', '', false);
insert into public.media (family_id, uploaded_by_parent, kind, taken_at, taken_at_source, status, bytes, object_key, view_key, thumb_key) values (:'ofam', :'op', 'photo', now(), 'exif', 'ready', 1234, 'k-obj-secret', 'k-view-secret', 'k-thumb-secret') returning id as omd \gset
insert into public.media (family_id, uploaded_by_member, kind, taken_at, taken_at_source, status, bytes) values (:'ofam', :'omem', 'video', now(), 'exif', 'ready', 99) returning id as omd2 \gset
insert into public.media (family_id, uploaded_by_parent, kind, taken_at, taken_at_source, status) values (:'ofam', :'op', 'photo', now(), 'exif', 'deleted') returning id as omd3 \gset
insert into public.media (family_id, kind, taken_at, taken_at_source, status, bytes) values (:'ofam', 'photo', now(), 'exif', 'ready', 5) returning id as omd4 \gset
set role service_role;
select public.sp_ops_media(public.sp_seoul_today() - 6, public.sp_seoul_today(), null, 0) as omed \gset
select public.sp_ops_media(public.sp_seoul_today() - 6, public.sp_seoul_today(), gen_random_uuid(), 0) as omed0 \gset
reset role;
select pg_temp.ok((select count(*) = 1 from jsonb_array_elements(:'omed'::jsonb -> 'rows') r where r ->> 'id' = :'omd' and r ->> 'by_role' = 'mom' and (r ->> 'bytes')::int = 1234 and r ->> 'kind' = 'photo'), '사진 목록: 올린 엄마·크기·종류');
select pg_temp.ok(not (:'omed'::jsonb::text ~ 'secret|_key'), '사진 목록에 파일 주소 없음');
select pg_temp.ok((select count(*) = 1 from jsonb_array_elements(:'omed'::jsonb -> 'rows') r where r ->> 'id' = :'omd2' and r ->> 'by_name' = '할머니' and r ->> 'by_role' is null), '사진 목록: 가족 기기가 올린 건 구성원 이름');
select pg_temp.ok(not exists (select 1 from jsonb_array_elements(:'omed'::jsonb -> 'rows') r where r ->> 'id' = :'omd3'), '사진 목록: 지운 사진은 빠짐');
select pg_temp.ok((:'omed0'::jsonb ->> 'total')::int = 0, '사진 목록: 다른 가족방으로 거르면 0');
-- 174: 거르기 판(p_filter)
set role service_role;
select public.sp_ops_media(public.sp_seoul_today() - 6, public.sp_seoul_today(), null, 0, '{"kind": "video"}') as omv \gset
select public.sp_ops_media(public.sp_seoul_today() - 6, public.sp_seoul_today(), null, 0, '{"by": "parent"}') as omp \gset
select public.sp_ops_media(public.sp_seoul_today() - 6, public.sp_seoul_today(), null, 0, '{"by": "device"}') as omdv \gset
select public.sp_ops_media(public.sp_seoul_today() - 6, public.sp_seoul_today(), null, 0, '{}') as omall \gset
select public.sp_ops_families(public.sp_seoul_today() - 6, public.sp_seoul_today(), 'created', 0, '{"plan": "paid"}') as ofp \gset
select public.sp_ops_families(public.sp_seoul_today() - 6, public.sp_seoul_today(), 'created', 0, '{"plan": "free", "state": "closing"}') as ofc \gset
select public.sp_ops_families(public.sp_seoul_today() - 6, public.sp_seoul_today(), 'created', 0, '{}') as ofa \gset
select public.sp_ops_accounts(public.sp_seoul_today() - 6, public.sp_seoul_today(), 'created', 0, '{"provider": "kakao", "fam": "yes"}') as oak \gset
select public.sp_ops_accounts(public.sp_seoul_today() - 6, public.sp_seoul_today(), 'created', 0, '{"provider": "email"}') as oae \gset
reset role;
select pg_temp.ok((select bool_and(r ->> 'kind' = 'video') and count(*) >= 1 from jsonb_array_elements(:'omv'::jsonb -> 'rows') r), '사진 거르기: 영상만');
select pg_temp.ok(not exists (select 1 from jsonb_array_elements(:'omp'::jsonb -> 'rows') r where r ->> 'id' = :'omd2') and exists (select 1 from jsonb_array_elements(:'omp'::jsonb -> 'rows') r where r ->> 'id' = :'omd'), '사진 거르기: 엄빠가 올린 것만');
select pg_temp.ok(not exists (select 1 from jsonb_array_elements(:'ofp'::jsonb -> 'rows') r where r ->> 'id' = :'ofam'), '가족방 거르기: 유료엔 무료 가족방 없음');
select pg_temp.ok(not exists (select 1 from jsonb_array_elements(:'ofc'::jsonb -> 'rows') r where r ->> 'delete_after' is null), '가족방 거르기: 탈퇴 예정만');
select pg_temp.ok((:'ofa'::jsonb ->> 'total')::int = (select count(*) from public.families), '가족방 거르기 없음 = 전체');
select pg_temp.ok(exists (select 1 from jsonb_array_elements(:'oak'::jsonb -> 'rows') r where r ->> 'id' = :'op') and not exists (select 1 from jsonb_array_elements(:'oak'::jsonb -> 'rows') r where r ->> 'family_id' is null), '계정 거르기: 카카오·가족방 있음');
select pg_temp.ok(not exists (select 1 from jsonb_array_elements(:'oae'::jsonb -> 'rows') r where r ->> 'provider' <> 'email'), '계정 거르기: 이메일만');
select pg_temp.ok((:'omp'::jsonb ->> 'total')::int + (:'omdv'::jsonb ->> 'total')::int = (:'omall'::jsonb ->> 'total')::int and exists (select 1 from jsonb_array_elements(:'omdv'::jsonb -> 'rows') r where r ->> 'id' = :'omd4'), '사진 거르기: 엄빠 + 가족 기기(올린 사람 지워진 것 포함) = 전체');
select pg_temp.ok(not has_function_privilege('authenticated', 'public.sp_ops_families(date,date,text,int,jsonb)', 'execute')
  and not has_function_privilege('anon', 'public.sp_ops_accounts(date,date,text,int,jsonb)', 'execute')
  and not has_function_privilege('authenticated', 'public.sp_ops_media(date,date,uuid,int,jsonb)', 'execute')
  and has_function_privilege('service_role', 'public.sp_ops_media(date,date,uuid,int,jsonb)', 'execute'), '거르기 판도 서버만');
-- 176: 가족방별 사진 요약
set role service_role;
select public.sp_ops_media_families(public.sp_seoul_today() - 6, public.sp_seoul_today(), 0, '{}') as omf \gset
select public.sp_ops_media_families(public.sp_seoul_today() - 6, public.sp_seoul_today(), 0, '{"kind": "video"}') as omfv \gset
reset role;
select pg_temp.ok((select (r ->> 'photos')::int >= 2 and (r ->> 'videos')::int >= 1 and (r ->> 'bytes')::int >= 1234 + 99 from jsonb_array_elements(:'omf'::jsonb -> 'rows') r where r ->> 'family_id' = :'ofam'), '사진 요약: 가족방 한 줄에 사진·영상 수·크기');
select pg_temp.ok((select (r ->> 'photos')::int = 0 and (r ->> 'videos')::int >= 1 from jsonb_array_elements(:'omfv'::jsonb -> 'rows') r where r ->> 'family_id' = :'ofam'), '사진 요약 거르기: 영상만 세기');
select pg_temp.ok((:'omf'::jsonb ->> 'items')::int = (select sum((r ->> 'photos')::int + (r ->> 'videos')::int) from jsonb_array_elements(:'omf'::jsonb -> 'rows') r), '사진 요약: 줄 합 = 전체 수');
select pg_temp.ok(not has_function_privilege('authenticated', 'public.sp_ops_media_families(date,date,int,jsonb)', 'execute') and has_function_privilege('service_role', 'public.sp_ops_media_families(date,date,int,jsonb)', 'execute'), '사진 요약: 서버만');
delete from public.media where id in (:'omd', :'omd2', :'omd3', :'omd4');
-- 171: 가족방별 묶음 — 같은 가족방 엄빠(엄마 먼저)가 붙어 나오고, 가족방 없는 계정은 맨 뒤. 가족방 없는 계정이 가장 최근에 가입해도 뒤
select gen_random_uuid() as oq \gset
select gen_random_uuid() as on1 \gset
insert into auth.users (id, is_anonymous, raw_app_meta_data, created_at) values (:'oq', false, '{"provider": "kakao"}', now() - interval '1 day'), (:'on1', false, '{"provider": "kakao"}', now() + interval '1 minute');
insert into public.parents (user_id, family_id, role, display_name) values (:'oq', :'ofam', 'dad', '운영아빠');
set role service_role;
select public.sp_ops_accounts(public.sp_seoul_today() - 6, public.sp_seoul_today(), 'created', 0) as ogrp1 \gset
reset role;
select pg_temp.ok((select array_agg(r ->> 'id' order by n) from jsonb_array_elements(:'ogrp1'::jsonb -> 'rows') with ordinality t(r, n) where r ->> 'family_id' = :'ofam') = array[:'op', :'oq']::text[], '계정 묶음: 같은 가족방 엄마·아빠 순');
select pg_temp.ok((select max(n) filter (where r ->> 'family_id' is not null) < min(n) filter (where r ->> 'family_id' is null) from jsonb_array_elements(:'ogrp1'::jsonb -> 'rows') with ordinality t(r, n)), '계정 묶음: 가족방 없는 계정은 맨 뒤(가장 최근 가입이어도)');
select pg_temp.ok((select (n2 - n1) = 1 from (select min(n) filter (where r ->> 'id' = :'op') as n1, min(n) filter (where r ->> 'id' = :'oq') as n2 from jsonb_array_elements(:'ogrp1'::jsonb -> 'rows') with ordinality t(r, n)) x), '계정 묶음: 같은 가족방은 붙어 나옴');
select pg_temp.ok((:'ogrp1'::jsonb ->> 'groups')::int < (:'ogrp1'::jsonb ->> 'total')::int, '계정 묶음 수 < 계정 수(엄빠 둘인 가족방)');
delete from public.parents where user_id = :'oq';
delete from auth.users where id in (:'oq', :'on1');
-- 새 이름으로 들어와 기다리는 기기(기기 active + 구성원 pending)는 '대기', 기한 지난 대기는 어디에도 안 셈
select gen_random_uuid() as ow \gset
select gen_random_uuid() as ox \gset
insert into auth.users (id, is_anonymous) values (:'ow', true), (:'ox', true);
insert into public.members (family_id, group_id, display_name, status, pending_until, created_at) values (:'ofam', :'ogrp', '큰이모', 'pending', now() + interval '1 day', now() - interval '3 days') returning id as owm \gset
insert into public.members (family_id, group_id, display_name, status, pending_until, created_at) values (:'ofam', :'ogrp', '작은이모', 'pending', now() - interval '1 hour', now() - interval '4 days') returning id as oxm \gset
insert into public.devices (auth_user_id, family_id, member_id, status, created_at) values (:'ow', :'ofam', :'owm', 'active', now() - interval '3 days'), (:'ox', :'ofam', :'oxm', 'active', now() - interval '4 days');
set role service_role;
select public.sp_ops_families(public.sp_seoul_today() - 6, public.sp_seoul_today(), 'created', 0) as olist2 \gset
select public.sp_ops_family(:'ofam', public.sp_seoul_today() - 6, public.sp_seoul_today()) as odet2 \gset
select public.sp_ops_summary(public.sp_seoul_today() - 6, public.sp_seoul_today()) as osum2 \gset
reset role;
select pg_temp.ok((select (r ->> 'active')::int = 1 and (r ->> 'pending')::int = 1 from jsonb_array_elements(:'olist2'::jsonb -> 'rows') r where r ->> 'id' = :'ofam'), '목록: 승인 1(할머니)·대기 1(큰이모), 기한 지난 작은이모는 빠짐');
select pg_temp.ok(jsonb_array_length(:'odet2'::jsonb -> 'devices') = 2 and (select count(*) = 1 from jsonb_array_elements(:'odet2'::jsonb -> 'devices') d where d ->> 'status' = 'pending'), '상세: 큰이모 기기는 대기, 작은이모 기기는 없음');
select pg_temp.ok((select count(*) = 1 from jsonb_array_elements(:'osum2'::jsonb -> 'checks' -> 'pending') c where c ->> 'family_id' = :'ofam' and (c ->> 'n')::int = 1), '살펴볼 것: 기한 안 대기만(2일 넘은 큰이모)');
select pg_temp.ok((:'osum2'::jsonb -> 'entry' ->> 'requested')::int > (:'osum2'::jsonb -> 'entry' ->> 'approved')::int, '승인은 신청보다 적음(대기·기한 지남은 승인에 안 셈)');
-- 169: 가입하고 멈춘 곳·올리다 멈춘 사진·정리 작업 밀림
insert into public.media (family_id, uploaded_by_parent, kind, taken_at, taken_at_source, created_at) values (:'ofam', :'op', 'photo', now(), 'exif', now() - interval '2 hours');
insert into public.media (family_id, uploaded_by_parent, kind, taken_at, taken_at_source, created_at) values (:'ofam', :'op', 'photo', now(), 'exif', now() - interval '4 days');
insert into public.r2_cleanup (prefix, queued_at) values (gen_random_uuid()::text || '/', now() - interval '3 days') returning prefix as or2 \gset
set role service_role;
select public.sp_ops_summary(public.sp_seoul_today() - 6, public.sp_seoul_today()) as osum3 \gset
reset role;
select pg_temp.ok((:'osum3'::jsonb -> 'signup' ->> 'accounts')::int >= 1 and (:'osum3'::jsonb -> 'signup' ->> 'setup')::int >= 1
  and (:'osum3'::jsonb -> 'signup' ->> 'setup')::int <= (:'osum3'::jsonb -> 'signup' ->> 'accounts')::int
  and (:'osum3'::jsonb -> 'signup' ->> 'uploaded')::int <= (:'osum3'::jsonb -> 'signup' ->> 'setup')::int
  and (:'osum3'::jsonb -> 'signup' ->> 'joined')::int <= (:'osum3'::jsonb -> 'signup' ->> 'uploaded')::int, '현황: 가입하고 멈춘 곳(가입 ≥ 설정 ≥ 첫 사진 ≥ 가족 들어옴)');
select pg_temp.ok((:'osum3'::jsonb -> 'signup' ->> 'no_family')::int >= 1, '현황: 지금 가족방 없는 엄빠 계정(가족방 없는 사용자)');
select pg_temp.ok((:'osum3'::jsonb -> 'signup')::text !~ '[0-9a-f]{8}-[0-9a-f]{4}', '가입 흐름엔 숫자만(계정 번호 없음)');
select pg_temp.ok((select (c ->> 'n')::int = 2 from jsonb_array_elements(:'osum3'::jsonb -> 'checks' -> 'stuck') c where c ->> 'family_id' = :'ofam'), '살펴볼 것: 1시간 넘게 올리다 멈춘 사진 2장');
select pg_temp.ok((:'osum3'::jsonb -> 'jobs' ->> 'uploads_late')::int >= 1 and (:'osum3'::jsonb -> 'jobs' ->> 'r2_late')::int >= 1 and (:'osum3'::jsonb -> 'jobs' ->> 'purge_late')::int = 0, '정리 작업 밀림: 이틀 넘은 올리기·R2 대기');
select pg_temp.ok((:'osum3'::jsonb -> 'now' ->> 'paid')::int = 0, '현황: 유료 가족방 수');
delete from public.media where family_id = :'ofam' and status = 'uploading';
delete from public.r2_cleanup where prefix = :'or2';
select set_config('request.jwt.claims', json_build_object('sub', :'ox', 'is_anonymous', true)::text, false);
set role authenticated;
select public.sp_note_visit();
select set_config('request.jwt.claims', json_build_object('sub', :'ow', 'is_anonymous', true)::text, false);
select public.sp_note_visit();
reset role;
select pg_temp.ok(not exists (select 1 from public.visits v join public.devices d on d.id = v.visitor where d.auth_user_id = :'ox'), '기한 지난 대기 기기는 방문을 안 남김');
select pg_temp.ok(exists (select 1 from public.visits v join public.devices d on d.id = v.visitor where d.auth_user_id = :'ow'), '기한 안 대기 기기는 방문을 남김');
-- 엄빠가 나가면 그 가족방의 엄빠 방문 기록을 지운다
update public.parents set removed_at = now() where user_id = :'op';
select pg_temp.ok(not exists (select 1 from public.visits where kind = 'parent' and visitor = :'op'), '나간 엄빠의 방문 기록은 지움');
update auth.users set deleted_at = now() where id = :'ow';
update auth.users set is_anonymous = false where id = :'ow';
set role service_role;
select public.sp_ops_accounts(public.sp_seoul_today() - 6, public.sp_seoul_today(), 'created', 0) as oacc2 \gset
reset role;
select pg_temp.ok((select r ->> 'family_id' is null and r ->> 'role' is null from jsonb_array_elements(:'oacc2'::jsonb -> 'rows') r where r ->> 'id' = :'op'), '계정 목록: 나간 엄빠는 가족방·역할 없음');
select pg_temp.ok(not exists (select 1 from jsonb_array_elements(:'oacc2'::jsonb -> 'rows') r where r ->> 'id' = :'ow'), '계정 목록: 지운(deleted_at) 계정은 빠짐');
select pg_temp.ok(exists (select 1 from public.visits where kind = 'device' and family_id = :'ofam'), '가족 기기 방문 기록은 그대로');
select public.sp_purge_family(:'ofam');
select pg_temp.ok(not exists (select 1 from public.visits where family_id = :'ofam'), '가족방을 지우면 방문 기록도 지움');
