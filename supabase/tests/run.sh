#!/usr/bin/env bash
# 로컬 Postgres 16에 임시 클러스터를 띄워 마이그레이션 + 권한 시나리오를 검사한다.
# 사용: npm run test:db  (PG_BIN으로 Postgres bin 경로 지정 가능)
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
PG_BIN="${PG_BIN:-/usr/lib/postgresql/16/bin}"
WORK="$(mktemp -d)"
PORT="${PG_PORT:-54329}"
AS=()
# initdb는 root로 못 돌리므로 root면 postgres 사용자로 실행
if [ "$(id -u)" = "0" ]; then AS=(runuser -u postgres --); chown postgres "$WORK"; fi

cleanup() { "${AS[@]}" "$PG_BIN/pg_ctl" -D "$WORK/data" -m immediate stop >/dev/null 2>&1 || true; rm -rf "$WORK"; }
trap cleanup EXIT

"${AS[@]}" "$PG_BIN/initdb" -D "$WORK/data" -U postgres --auth=trust -E UTF8 >/dev/null
"${AS[@]}" "$PG_BIN/pg_ctl" -D "$WORK/data" -o "-p $PORT -k $WORK -c listen_addresses=''" -l "$WORK/log" -w start >/dev/null

PSQL=("$PG_BIN/psql" -h "$WORK" -p "$PORT" -U postgres -v ON_ERROR_STOP=1 -q -X)
"${PSQL[@]}" -d postgres -c 'create database sweepea' >/dev/null
"${PSQL[@]}" -d sweepea -f "$ROOT/supabase/tests/stub.sql" >/dev/null
for f in "$ROOT"/supabase/migrations/*.sql; do "${PSQL[@]}" -d sweepea -f "$f" >/dev/null; done
if ! "${PSQL[@]}" -d sweepea -f "$ROOT/supabase/tests/rls.sql" >"$WORK/out" 2>&1; then cat "$WORK/out"; exit 1; fi
[ -n "${SHOW_OUT:-}" ] && grep -E "^psql.*ERROR|아래 에러" "$WORK/out"
n=$(grep -c '^psql.*ERROR' "$WORK/out" || true)
# rls.sql에 적은 의도된 거부(에러) 개수와 같아야 한다
if [ "$n" -ne 44 ]; then echo "의도된 거부가 44건이어야 하는데 ${n}건"; grep -E '^psql.*ERROR|아래 에러' "$WORK/out"; exit 1; fi
echo "의도된 거부 ${n}건 확인"
echo "DB 검사 통과"
