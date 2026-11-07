#!/usr/bin/env bash
# 엄빠 공동 관리 동시 처리 검사(100): 둘이 동시에 서로 내보내기·둘 다 나가기·나가기와 내보내기가 겹쳐도 엄빠가 한 명은 남는다(둘 다 나가면 마지막이 삭제 예정).
# 사용: LC_ALL=C PG_BIN=/opt/homebrew/bin bash supabase/tests/race.sh → 끝줄 '동시 처리 통과'
set -u
R="$(cd "$(dirname "$0")/../.." && pwd)"; B="${PG_BIN:-/usr/lib/postgresql/16/bin}"; W=$(mktemp -d); export LC_ALL=C
trap '$B/pg_ctl -D $W/data -m immediate stop >/dev/null 2>&1; rm -rf $W' EXIT
$B/initdb -D $W/data -U postgres --auth=trust -E UTF8 >/dev/null
$B/pg_ctl -D $W/data -o "-p 54339 -k $W -c listen_addresses=''" -l $W/log -w start >/dev/null || { cat $W/log; exit 1; }
P=($B/psql -h $W -p 54339 -U postgres -v ON_ERROR_STOP=1 -q -X)
"${P[@]}" -d postgres -c 'create database t'; "${P[@]}" -d t -f $R/supabase/tests/stub.sql >/dev/null
for f in $R/supabase/migrations/*.sql; do "${P[@]}" -d t -f $f >/dev/null || echo FAIL $f; done
A=11111111-1111-1111-1111-111111111111; D=22222222-2222-2222-2222-222222222222
setup(){ "${P[@]}" -d t >/dev/null <<EOF
delete from public.families; delete from public.parents; delete from auth.users;
insert into auth.users(id) values ('$A'),('$D');
select set_config('request.jwt.claims', '{"sub":"$A","is_anonymous":false}', false);
select public.sp_create_family('mom','엄마','하린','2025-09-17','0917') as fam \gset
select public.sp_create_parent_invite() as code \gset
select set_config('request.jwt.claims', '{"sub":"$D","is_anonymous":false}', false);
select public.sp_accept_parent_invite(:'code','dad');
EOF
}
run(){ "${P[@]}" -d t <<EOF
select set_config('request.jwt.claims', '{"sub":"$1","is_anonymous":false}', false);
set role authenticated;
begin; select $2; select pg_sleep(1); commit;
EOF
}
fail=0
show(){ r=$("${P[@]}" -d t -At -c "select (select count(*) from public.parents where removed_at is null)||' '||(select count(*) from public.families where delete_after is not null)"); echo "$1: 남은 엄빠·삭제 예정 = $r"; [ "$r" = "$2" ] || fail=1; }
setup; run $A "public.sp_remove_coparent('$D')" >/dev/null 2>&1 & run $D "public.sp_remove_coparent('$A')" >/dev/null 2>&1; wait; show 서로-내보내기 '1 0'
setup; run $A "public.sp_request_delete()" >/dev/null 2>&1 & run $D "public.sp_request_delete()" >/dev/null 2>&1; wait; show 둘-다-나가기 '1 1'
setup; run $A "public.sp_request_delete()" >/dev/null 2>&1 & run $D "public.sp_remove_coparent('$A')" >/dev/null 2>&1; wait; show 나가기-내보내기 '1 0'
[ $fail = 0 ] && echo '동시 처리 통과' || { echo '동시 처리 실패'; exit 1; }
